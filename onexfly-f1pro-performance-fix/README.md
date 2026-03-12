## OneXFly F1 Pro Performance Fix (Decky Loader plugin)

Single-toggle Decky plugin that:
- **ON**: disables `power-profiles-daemon`, sets CPU governor to `performance`, sets GPU to performance mode
- **OFF**: re-enables `power-profiles-daemon`, reverts CPU governor to `schedutil`, reverts GPU to `auto`
- **Persistence**: installs a oneshot `systemd` service so the ON state is re-applied after reboot

### Files it touches (when ON)
- `/usr/local/bin/onexfly-performance-fix.sh`
- `/etc/systemd/system/onexfly-performance-fix.service`
- sysfs:
  - `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
  - `/sys/class/drm/card0/device/power_dpm_force_performance_level`
  - `/sys/class/drm/card0/device/pp_power_profile_mode`

### Privileges / safety
- This plugin sets `plugin.json` flag `"_root"` so the backend runs as **root** (no interactive `sudo`).
- It also checks the device via DMI strings and refuses to run unless it looks like **OneXFly F1 Pro**.

### Build (on your dev machine)
From the plugin folder:

```bash
pnpm install
pnpm build
```

### Install (on the device running Decky Loader)
Copy the whole folder `onexfly-f1pro-performance-fix` into:
- `~/homebrew/plugins/`

Final path should look like:
- `~/homebrew/plugins/onexfly-f1pro-performance-fix/plugin.json`

Then in Decky Loader:
- Open Decky → Plugins → enable **OneXFly F1 Pro Performance Fix**

### Usage
- Open the plugin in Decky and toggle **Performance Fix** ON/OFF.
- ON applies changes immediately and enables the systemd service for next reboot.
- OFF reverts immediately and disables/removes the systemd service and helper script.

