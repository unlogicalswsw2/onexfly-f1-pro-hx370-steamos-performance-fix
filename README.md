## OneXFly F1 Pro (HX370) SteamOS Performance Fix — Decky Loader Plugin

Decky Loader plugin with a **single ON/OFF toggle** to apply performance tweaks on **OneXFly F1 Pro** and make them **persist after reboot** via `systemd`.

### What it does
- **ON**
  - Disables `power-profiles-daemon`
  - Sets CPU governors to `performance`
  - Sets GPU performance mode (`manual` + profile `1`)
  - Installs/enables a oneshot `systemd` service to re-apply settings after reboot
- **OFF**
  - Re-enables `power-profiles-daemon`
  - Restores CPU governor to `schedutil`
  - Restores GPU mode to `auto` (profile `0`)
  - Disables/removes the `systemd` service and helper script

### Install (no build needed)
This repo includes the prebuilt frontend bundle in `onexfly-f1pro-performance-fix/dist/`.

On the device (SteamOS) run:

```bash
cd ~/homebrew/plugins
git clone https://github.com/unlogicalswsw2/onexfly-f1-pro-hx370-steamos-performance-fix.git
```

Then restart Decky Loader (or reboot), and enable the plugin:
- Decky → Plugins → **OneXFly F1 Pro Performance Fix**

### Development / rebuild frontend (optional)
If you want to rebuild the frontend yourself:

```bash
cd ~/homebrew/plugins/onexfly-f1-pro-hx370-steamos-performance-fix/onexfly-f1pro-performance-fix
npm install
npm run build
```

