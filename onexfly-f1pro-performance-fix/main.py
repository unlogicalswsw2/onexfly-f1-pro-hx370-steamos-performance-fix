import asyncio
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.request import urlopen

import decky


SERVICE_NAME = "onexfly-performance-fix.service"
SERVICE_PATH = Path("/etc/systemd/system") / SERVICE_NAME
SCRIPT_PATH = Path("/usr/local/bin/onexfly-performance-fix.sh")

CPU_GOVERNOR_GLOB = "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
GPU_DPM_FORCE_LEVEL = Path("/sys/class/drm/card0/device/power_dpm_force_performance_level")
GPU_POWER_PROFILE_MODE = Path("/sys/class/drm/card0/device/pp_power_profile_mode")

# "Defaults" we revert to when toggling OFF.
DEFAULT_CPU_GOVERNOR = "schedutil"
DEFAULT_GPU_DPM_LEVEL = "auto"
DEFAULT_GPU_POWER_PROFILE_MODE = "0"

# Base URL for self-update (raw GitHub).
UPDATE_BASE_URL = (
    "https://raw.githubusercontent.com/"
    "unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix/"
    "main/onexfly-f1pro-performance-fix"
)


@dataclass
class PersistedState:
    enabled: bool = False
    readonly_was_enabled: Optional[bool] = None


class Plugin:
    async def _main(self):
        self.loop = asyncio.get_event_loop()
        self._state_path = Path(decky.DECKY_SETTINGS_DIR) / "onexfly-f1pro-performance-fix.json"
        decky.logger.info("OneXFly F1 Pro Performance Fix loaded")

    async def _unload(self):
        decky.logger.info("OneXFly F1 Pro Performance Fix unloading")

    async def _uninstall(self):
        decky.logger.info("OneXFly F1 Pro Performance Fix uninstall: disabling service and cleaning up")
        try:
            await self._set_enabled(False)
        except Exception:
            decky.logger.exception("Uninstall cleanup failed")

    # -------- Public API (called from frontend) --------
    async def get_status(self) -> Dict[str, Any]:
        """
        Returns:
          { enabled: bool }
        """
        persisted = self._load_state()

        return {
            "enabled": bool(persisted.enabled),
        }

    async def set_enabled(self, enabled: bool) -> Dict[str, Any]:
        """
        Toggle performance optimizations on/off.
        """
        await self._set_enabled(bool(enabled))
        return await self.get_status()

    async def update_plugin(self) -> Dict[str, Any]:
        """
        Download latest plugin files from GitHub into this plugin directory.
        Does not auto-restart Decky; user should restart Decky/Steam UI after update.
        """
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._do_update)
            msg = "Update downloaded. Please restart Decky Loader to apply changes."
            decky.logger.info(msg)
            return {"ok": True, "message": msg}
        except Exception as e:
            decky.logger.exception("Update failed")
            return {"ok": False, "message": str(e)}

    # -------- Core toggle logic --------
    async def _set_enabled(self, enabled: bool) -> None:
        if enabled:
            decky.logger.info("Enabling OneXFly performance mode")
            await self._enable()
        else:
            decky.logger.info("Disabling OneXFly performance mode (revert to defaults)")
            await self._disable()

    async def _enable(self) -> None:
        state = self._load_state()

        # We need /etc + /usr/local writes; ensure filesystem is writable where supported.
        if state.readonly_was_enabled is None:
            try:
                state.readonly_was_enabled = self._steamos_readonly_is_enabled()
                self._save_state(state)
            except RuntimeError:
                # steamos-readonly not present or unsupported; ignore and proceed.
                decky.logger.warning("steamos-readonly not available; assuming writable filesystem")
                state.readonly_was_enabled = None
                self._save_state(state)

        if state.readonly_was_enabled:
            try:
                self._run(["steamos-readonly", "disable"], check=True)
            except RuntimeError as e:
                decky.logger.warning(f"Failed to disable steamos-readonly: {e}")

        # Disable power-profiles-daemon (same as script).
        self._run(["systemctl", "stop", "power-profiles-daemon"], check=False)
        self._run(["systemctl", "disable", "power-profiles-daemon"], check=False)

        # Apply sysfs tweaks immediately.
        self._set_all_cpu_governors("performance")
        self._write_sysfs(GPU_DPM_FORCE_LEVEL, "manual")
        self._write_sysfs(GPU_POWER_PROFILE_MODE, "1")

        # Persist across reboots via oneshot systemd service.
        self._ensure_persistence_files()
        self._run(["systemctl", "daemon-reload"], check=True)
        self._run(["systemctl", "enable", SERVICE_NAME], check=True)
        self._run(["systemctl", "start", SERVICE_NAME], check=False)

        state.enabled = True
        self._save_state(state)

    async def _disable(self) -> None:
        state = self._load_state()

        # Revert sysfs to typical defaults.
        self._set_all_cpu_governors(DEFAULT_CPU_GOVERNOR)
        self._write_sysfs(GPU_DPM_FORCE_LEVEL, DEFAULT_GPU_DPM_LEVEL)
        self._write_sysfs(GPU_POWER_PROFILE_MODE, DEFAULT_GPU_POWER_PROFILE_MODE)

        # Re-enable power-profiles-daemon.
        self._run(["systemctl", "enable", "power-profiles-daemon"], check=False)
        self._run(["systemctl", "start", "power-profiles-daemon"], check=False)

        # Remove persistence.
        self._run(["systemctl", "disable", SERVICE_NAME], check=False)
        self._run(["systemctl", "stop", SERVICE_NAME], check=False)

        if SERVICE_PATH.exists():
            try:
                SERVICE_PATH.unlink()
            except Exception:
                decky.logger.exception("Failed to remove systemd unit")

        if SCRIPT_PATH.exists():
            try:
                SCRIPT_PATH.unlink()
            except Exception:
                decky.logger.exception("Failed to remove helper script")

        self._run(["systemctl", "daemon-reload"], check=False)

        # Restore SteamOS read-only mode if it was enabled before we touched it.
        if state.readonly_was_enabled:
            try:
                self._run(["steamos-readonly", "enable"], check=False)
            except RuntimeError as e:
                decky.logger.warning(f"Failed to re-enable steamos-readonly: {e}")

        state.enabled = False
        self._save_state(state)

    # -------- Helpers: persistence files --------
    def _ensure_persistence_files(self) -> None:
        SCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)

        script_body = "\n".join(
            [
                "#!/bin/bash",
                "",
                f"for g in {CPU_GOVERNOR_GLOB}",
                "do",
                "    echo performance > $g",
                "done",
                "",
                f"echo manual > {GPU_DPM_FORCE_LEVEL}",
                f"echo 1 > {GPU_POWER_PROFILE_MODE}",
                "",
            ]
        )

        self._atomic_write(SCRIPT_PATH, script_body + "\n", mode=0o755)

        unit_body = "\n".join(
            [
                "[Unit]",
                "Description=OneXFly Performance Fix",
                "",
                "[Service]",
                "Type=oneshot",
                f"ExecStart={SCRIPT_PATH}",
                "",
                "[Install]",
                "WantedBy=multi-user.target",
                "",
            ]
        )
        self._atomic_write(SERVICE_PATH, unit_body + "\n", mode=0o644)

    def _atomic_write(self, path: Path, content: str, mode: int) -> None:
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(content)
        os.chmod(tmp, mode)
        tmp.replace(path)

    # -------- Helpers: self-update --------
    def _do_update(self) -> None:
        plugin_dir = Path(__file__).resolve().parent
        files_to_update = [
            "main.py",
            "plugin.json",
            "package.json",
            "rollup.config.mjs",
            "tsconfig.json",
            "README.md",
            "src/index.tsx",
            "dist/index.js",
            "dist/index.js.map",
        ]

        for rel in files_to_update:
            url = f"{UPDATE_BASE_URL}/{rel}"
            target = plugin_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)

            decky.logger.info(f"Updating {rel} from {url}")
            with urlopen(url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Failed to download {rel}: HTTP {resp.status}")
                data = resp.read()

            # Binary-safe write.
            tmp = target.with_suffix(target.suffix + ".tmp")
            with open(tmp, "wb") as f:
                f.write(data)
            os.chmod(tmp, 0o644)
            tmp.replace(target)

    # -------- Helpers: sysfs writes --------
    def _set_all_cpu_governors(self, governor: str) -> None:
        import glob

        for gpath in glob.glob(CPU_GOVERNOR_GLOB):
            try:
                self._write_sysfs(Path(gpath), governor)
            except Exception:
                decky.logger.exception(f"Failed setting governor for {gpath}")

    def _write_sysfs(self, path: Path, value: str) -> None:
        if not path.exists():
            decky.logger.warning(f"sysfs path missing: {path}")
            return
        try:
            path.write_text(value.strip() + "\n")
        except PermissionError:
            raise RuntimeError(
                f"Permission denied writing {path}. Ensure plugin is installed with plugin.json flag '_root'."
            )

    def _is_sysfs_in_perf_mode(self) -> bool:
        # Governor: any cpu not "performance" => false
        import glob

        governor_ok = True
        for gpath in glob.glob(CPU_GOVERNOR_GLOB):
            try:
                cur = Path(gpath).read_text(errors="ignore").strip()
                if cur != "performance":
                    governor_ok = False
                    break
            except Exception:
                governor_ok = False
                break

        try:
            gpu_level = GPU_DPM_FORCE_LEVEL.read_text(errors="ignore").strip()
            gpu_profile = GPU_POWER_PROFILE_MODE.read_text(errors="ignore").strip()
            gpu_ok = (gpu_level == "manual") and (gpu_profile == "1")
        except Exception:
            gpu_ok = False

        return governor_ok and gpu_ok

    # -------- Helpers: SteamOS read-only state --------
    def _steamos_readonly_is_enabled(self) -> bool:
        # steamos-readonly is only present on SteamOS; treat missing command as "not enabled".
        try:
            res = self._run(["steamos-readonly", "status"], check=False)
        except RuntimeError:
            decky.logger.warning("steamos-readonly command not found; assuming read-only is disabled")
            return False

        out = (res[1] or "").lower()
        if "enabled" in out:
            return True
        if "disabled" in out:
            return False
        return False

    # -------- Helpers: systemd --------
    def _systemd_is_enabled(self, unit: str) -> bool:
        res = self._run(["systemctl", "is-enabled", unit], check=False)
        out = (res[1] or "").strip().lower()
        return out == "enabled"

    # -------- Helpers: state --------
    def _load_state(self) -> PersistedState:
        try:
            if self._state_path.exists():
                data = json.loads(self._state_path.read_text(errors="ignore"))
                return PersistedState(
                    enabled=bool(data.get("enabled", False)),
                    readonly_was_enabled=data.get("readonly_was_enabled", None),
                )
        except Exception:
            decky.logger.exception("Failed to load persisted state")
        return PersistedState()

    def _save_state(self, state: PersistedState) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(
                json.dumps(
                    {
                        "enabled": state.enabled,
                        "readonly_was_enabled": state.readonly_was_enabled,
                    },
                    indent=2,
                )
                + "\n"
            )
        except Exception:
            decky.logger.exception("Failed to save persisted state")

    # -------- Helpers: subprocess --------
    def _run(self, cmd: list, check: bool) -> Tuple[int, str, str]:
        decky.logger.debug(f"Running: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
            )
        except FileNotFoundError:
            raise RuntimeError(f"Required command not found: {cmd[0]}")

        if proc.stdout:
            decky.logger.debug(proc.stdout.strip())
        if proc.stderr:
            decky.logger.debug(proc.stderr.strip())

        if check and proc.returncode != 0:
            raise RuntimeError(
                f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
            )
        return proc.returncode, proc.stdout, proc.stderr
