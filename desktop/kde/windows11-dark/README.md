# Windows 11 dark desktop profile

## Scope and status

The requested visual target is Windows 11 in dark mode, using EndeavourOS and
KDE Plasma. The target reports Plasma 6.7.5. This repository provides an opt-in
panel script and a read-only asset check. Neither has been run in a real Plasma
6.7.5 session here. The profile is not installed or visually verified.

The panel is full-width, attached to the bottom edge and 48 logical pixels high.
Two flexible spacers place the launcher and icon-only tasks toward the center;
the system tray, clock and show-desktop button sit on the right. The tray makes
this approximate rather than pixel-exact screen centering. Existing panels and
their widgets are retained. Running the script again updates its marked panel
without creating duplicates; it refuses unrecognized customizations.

## Appearance components

| Component | Selected upstream component | Source |
| --- | --- | --- |
| Plasma style | Fluent round dark | [Fluent KDE](https://github.com/vinceliuice/Fluent-kde) |
| Colors | FluentDark | Fluent KDE |
| Window decoration | Fluent-round-dark, rounded variant | Fluent KDE |
| Qt application style | Kvantum with Fluent dark theme | Fluent KDE installation guidance |
| Icons | Fluent-dark | [Fluent icons](https://github.com/vinceliuice/Fluent-icon-theme) |
| Cursor | Fluent-dark-cursors | Fluent icons / Fluent KDE defaults |
| Start menu | Menu 11 Next (`menu.11.next`) | [Menu 11 Next](https://github.com/Eisteed/menu-11-next) |

Fluent KDE and Fluent icons declare GPL-3.0; Menu 11 Next declares GPL-2.0+ and
targets Plasma 6.5+. Their declared support is not a compatibility test on 6.7.5.
No upstream code or Microsoft assets are bundled. Dependency revisions have
not been pinned; fully reproducible dependency installation is still pending.

GTK applications and applications with their own decorations may look different.
This profile does not change the login screen, install fonts, select a wallpaper,
or implement Windows snap layouts. Wallpaper remains a separate visual choice.

## Read-only target inspection

From the repository root on the target computer:

```bash
bash desktop/kde/windows11-dark/check.sh
```

This checks Plasma's reported version and installed theme/widget asset paths.
Missing assets produce exit status 1. It does not install packages, download
code, apply settings or connect to a graphical session. A successful check does
not prove that the Qt style or effects work.

## Explicit setup on the target computer

These are manual deployment steps for a separately approved desktop change.
The bootstrap does not run them.

1. Record the current theme, colors, icons, cursor, decoration and Qt style in
   System Settings. Back up the existing `kdeglobals`, `kwinrc`, `plasmarc`,
   `kcminputrc`, `plasma-org.kde.plasma.desktop-appletsrc`, `plasmashellrc`,
   `kglobalshortcutsrc` and the `Kvantum/` configuration directory from your XDG
   configuration directory (normally `~/.config`) to a new private location
   outside Git. Only include paths that exist. For a consistent backup, copy
   them while logged out of Plasma, using a text console or another session.
2. Review the upstream components and install them only after approval. Use
   user-local destinations for themes and widgets. Fluent KDE's installer also
   copies wallpaper, widgets and layouts; inspect and limit installation to
   the listed desktop components. System package installation for Kvantum
   requires separate approval. Package lists remain unchanged until reviewed.
3. Run the read-only check. Fix missing assets before proceeding.
4. In System Settings, select the individual components above. Do not apply the
   upstream global-theme bundle: it declares additional download dependencies,
   including an SDDM theme and wallpaper, outside this profile's scope. Set the
   titlebar buttons to minimize/maximize/close on the right, and
   select Fluent dark in Kvantum Manager. Confirm blur/shadows visually.
5. Open Plasma's **desktop** scripting console (KRunner: `desktop console`).
   Open or paste `layout.js`, review it, and execute it once. Execution writes
   Plasma configuration and adds a panel. It does not install themes.
6. Inspect the new panel in edit mode. Two bottom panels may initially stack:
   keep the old one until you are happy with the replacement. Manually remove
   the old panel only after accepting the result. Existing pinned apps remain
   on the old panel; choose the desired pins on the new one.

## Acceptance and recovery

Check launcher opening, search, app launching, task switching, tray controls,
clock, show-desktop, display scaling and the intended monitor. Log out and back
in to verify persistence. Reapply the panel script to verify no duplicate panel
is created. Check Qt and GTK windows separately. Record the installed upstream
revisions and any differences before calling the profile verified.

To undo the preview, remove only the new Endvos panel in Plasma edit mode and
reselect the recorded appearance settings. If the old panel was retained, it
continues to provide its original launcher and pins. If configuration recovery
is necessary, log out of Plasma before restoring the private backup, then log
in again. Restoring replaces the backed-up configuration state and also reverts
later changes in those files; inspect it before overwriting anything.

The recovery procedure is documented but has not been tested on the target.

Implementation references: [Plasma scripting API](https://develop.kde.org/docs/plasma/scripting/api/),
[panel properties](https://github.com/KDE/plasma-workspace/blob/master/shell/scripting/panel.h),
[Fluent defaults](https://github.com/vinceliuice/Fluent-kde/blob/main/plasma/look-and-feel/com.github.vinceliuice.Fluent-round-dark/contents/defaults),
[menu metadata](https://github.com/Eisteed/menu-11-next/blob/main/metadata.json),
[menu configuration](https://github.com/Eisteed/menu-11-next/blob/main/contents/config/main.xml).
