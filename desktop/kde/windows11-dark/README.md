# Windows 11 dark desktop profile

This earlier bottom-panel profile is retained for its existing installation and
backup recovery. New UI work uses [Endvos Dark](../endvos-dark/README.md), based
on the user's approved top-panel design with central KDE accent colors.

## Scope and status

The requested visual target is Windows 11 in dark mode, using EndeavourOS and
KDE Plasma. The target reports Plasma 6.7.5. The bootstrap now downloads,
installs and activates the profile automatically when explicitly requested.
It does not require a GitHub account or Git checkout: an extracted repository
ZIP works too. Python 3.11+ with the safe tarfile data filter is required.
The installer and recovery have isolated tests; application in a real Plasma
6.7.5 session and visual parity have not been verified here.

The panel is full-width, attached to the bottom edge and 48 logical pixels high.
Two flexible spacers place the launcher and icon-only tasks toward the center;
the system tray, clock and show-desktop button sit on the right. The tray makes
this approximate rather than pixel-exact screen centering. Applying the profile
replaces existing bottom panels on the runtime-selected screen after creating
the replacement widgets. This also replaces their custom widgets and pins;
the original configuration is backed up first. Other screens and panels are
retained. Reapplying updates its marked panel without duplicates. It refuses
unrecognized customizations of the Endvos panel. Direct execution of `layout.js`
without the installer's replacement flag remains a non-removing preview.

## Appearance components

| Component | Selected upstream component | Source |
| --- | --- | --- |
| Plasma style | Fluent round dark | [Fluent KDE](https://github.com/vinceliuice/Fluent-kde) |
| Colors | FluentDark | Fluent KDE |
| Window decoration | Fluent-round-dark, rounded variant | Fluent KDE |
| Qt application style | Kvantum with Fluent-roundDark | Fluent KDE installation guidance |
| Icons | Fluent-dark | [Fluent icons](https://github.com/vinceliuice/Fluent-icon-theme) |
| Cursor | Fluent-dark-cursors | Fluent icons / Fluent KDE defaults |
| Start menu | Menu 11 Next (`menu.11.next`) | [Menu 11 Next](https://github.com/Eisteed/menu-11-next) |

Fluent KDE and Fluent icons declare GPL-3.0; Menu 11 Next declares GPL-2.0+ and
targets Plasma 6.5+. Their declared support is not a compatibility test on 6.7.5.
No upstream assets are bundled in Git. Theme/widget commit IDs and archive
SHA-256 checksums are pinned in `sources.json`; mismatches stop installation.
Pacman packages use the target's configured repositories and are not version
pinned. Upstream installers are never executed. Only the selected desktop assets
are assembled, retaining license files. Ten dangling icon aliases in the pinned
upstream source are omitted so the icon fallback can handle those names.

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

## Automatic setup in the EndeavourOS VM

Open Konsole in the running Plasma session and change into the extracted
repository directory (the directory containing `bootstrap.sh`). Preview first:

```bash
bash bootstrap.sh --profile windows11-dark
```

Apply the profile and permit installation of its missing official packages:

```bash
bash bootstrap.sh --profile windows11-dark --apply --install-packages
```

Run as your ordinary desktop user. Only missing Pacman dependencies use `sudo`;
Pacman may ask for confirmation and a password. The dependency list is
`packages/profiles/windows11-dark.pacman.txt`. Without `--install-packages`,
missing dependencies are reported and installation stops. There is no automatic
system upgrade, database refresh or AUR installation.

The installer saves the affected configuration and existing asset directories
under `${XDG_STATE_HOME:-~/.local/state}/endvos/windows11-dark/<BACKUP_ID>/`.
The backup is private and includes a live Plasma layout export and the source
lock. The files restored automatically are listed in `manifest.json`.
The raw configuration snapshot represents its on-disk state; the live export
also retains panel changes not yet written by Plasma. Do not edit the desktop
while applying the profile. Downloads are cached under the XDG cache directory.

After download verification and asset staging, it installs the menu via
KPackage, applies colors/style/cursor, configures icons and Kvantum, selects the
rounded window decoration, enables blur, reconfigures KWin and applies the panel
via the user's session D-Bus. It checks written settings and required assets.
Log out and back in afterward to reload existing applications and icon caches.
Whether blur renders depends on the VM's compositor and graphics support.

The global-theme bundle is not applied; its unrelated SDDM/wallpaper downloads
are excluded. No external installer, shell restart, hardware change or network
configuration is performed. The menu's upstream update checker may contact
GitHub. A narrow local patch to the pinned menu makes its weather timer and
requests respect the disabled setting and supplies a missing method called by
the menu. No weather location is configured by Endvos.

## Acceptance and recovery

Check launcher opening, search, app launching, task switching, tray controls,
clock, show-desktop, display scaling and the intended monitor. Log out and back
in to verify persistence. Reapply the panel script to verify no duplicate panel
is created. Check Qt and GTK windows separately. Record the installed upstream
revisions and any differences before calling the profile verified.

The installer prints the backup ID on success and on failure after snapshot
creation. To restore, **log out of Plasma**, open a text console (for example
Ctrl+Alt+F3), log in as the same user and change to the repository directory:

```bash
bash bootstrap.sh --profile windows11-dark --restore BACKUP_ID --apply
```

Replace `BACKUP_ID` with the actual printed ID. Restoration refuses to run while
your plasmashell is active. It restores previous files/directories and removes
profile paths that were absent before installation. Changes made after that
backup in those paths are also reverted. It does not uninstall system packages
or clear caches. Then log back into Plasma. Backups are retained for reuse.

If activation fails, the installer stops and keeps the backup instead of
overwriting configuration files underneath the running shell. A successful
installation is never reported when a command or panel script fails.

## Development validation

```bash
bash -n bootstrap.sh desktop/kde/windows11-dark/check.sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_panel.js
```

Python tests cover no-write planning, archive traversal, checksums, backups,
restoration and failure handling in temporary directories. Panel tests use a
mock Plasma API, including replacement scope, repeat application and partial
failure. The panel tests were run in an isolated V8 engine here; Node is only
needed to run that development test command locally, not to install the profile.
Real upstream assets were staged successfully with aliases checked. These tests
do not establish real-session compatibility, graphics output or target recovery.

Implementation references: [Plasma scripting API](https://develop.kde.org/docs/plasma/scripting/api/),
[panel properties](https://github.com/KDE/plasma-workspace/blob/master/shell/scripting/panel.h),
[Fluent defaults](https://github.com/vinceliuice/Fluent-kde/blob/main/plasma/look-and-feel/com.github.vinceliuice.Fluent-round-dark/contents/defaults),
[menu metadata](https://github.com/Eisteed/menu-11-next/blob/main/metadata.json),
[menu configuration](https://github.com/Eisteed/menu-11-next/blob/main/contents/config/main.xml).
