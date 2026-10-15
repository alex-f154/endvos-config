# Endvos Dark — stage 1

The user-approved design replaces the earlier Windows 11 clone target: a narrow
top bar, Windows-style app launcher, charcoal surfaces and one changeable KDE
accent color. KDE Plasma and EndeavourOS remain the foundation.

## Implemented scope

- A full-width, attached top panel, 36 logical pixels high.
- Menu 11 Next at the left: search, pinned apps and the All Apps list. Its popup
  follows the top panel instead of opening at the bottom of the screen.
- Icon-only tasks beside the launcher. Initial pins use only existing desktop
  files; later applications/pins are not installed or reset by this profile.
- A local `org.endvos.paneltitle` widget in the expanding middle area: the active
  window's title takes priority. With no active window it shows a playing track
  and artist; with neither it is empty. Paused music is not shown.
- The native Plasma tray and clock on the right, with date beside time.
- A complete color scheme derived from the installed Breeze Dark scheme, with
  charcoal neutral surfaces. Breeze widgets, icons and window decoration use
  KDE's native color system; this profile does not activate Kvantum or Fluent.

The title is centered in the space between tasks and the tray, not guaranteed
to be at the physical screen center when those areas have unequal widths.
The native Breeze panel/menu framing is used in this first stage. The mockup's
exact geometry, rounded status groups, custom control center and window-layout
picker are not implemented yet. Native KWin window behavior is retained.
Wallpaper, login screen, cursor, fonts, GTK styling, hardware and network
configuration are outside this stage. Applications with custom styling can
ignore the KDE accent.

## Status and prerequisites

Implementation has isolated Python and JavaScript behavior tests. It has not
been rendered, deployed or recovered in a real Plasma session here. The host
has no Qt/QML tools or Plasma; native QML validation and VM acceptance remain
pending. The reported target is Plasma 6.7.5; application requires Plasma 6.7.x,
Python 3.11+ with the safe tarfile data filter, and a logged-in normal-user
Plasma session with D-Bus. No GitHub account or Git checkout is required.

Menu 11 sources are pinned by commit and SHA-256 in `sources.json`. The local
title widget is included in this repository under MIT. Official packages are
listed separately in `packages/profiles/endvos-dark.pacman.txt`; their versions
come from the target's configured repositories. Upstream installers are not run.
The narrow weather fix from the earlier installer is retained and weather is
disabled. The upstream menu update checker may contact GitHub.

## Setup in the test VM

From Konsole in the directory containing `bootstrap.sh`, preview without writes,
downloads, package queries or session commands:

```bash
bash bootstrap.sh --profile endvos-dark
```

Explicitly apply and permit missing official packages:

```bash
bash bootstrap.sh --profile endvos-dark --apply --install-packages
```

Run as the normal desktop user; do not put `sudo` before the command. Only
missing official dependencies invoke interactive `sudo pacman -S --needed`.
There is no automatic upgrade, package database refresh, AUR or Flatpak install.
If packages are unavailable, the installer stops rather than changing mirrors
or forcing a partial upgrade.

An existing custom KDE accent is retained; otherwise the initial color is
`#9abca8`. To deliberately choose another during installation:

```bash
bash bootstrap.sh --profile endvos-dark --apply --install-packages --accent '#809fea'
```

Later change the accent centrally in **System Settings → Colors & Themes →
Colors** (labels vary with language). Rerunning the installer retains a stored
custom accent unless `--accent` is passed. It reapplies this profile's charcoal
scheme, layout and other owned appearance settings.

The installer backs up its configuration and asset targets, then replaces
existing **top and bottom panels on the runtime-selected monitor** after all
replacement widget instances have been created. This includes an earlier
Windows 11 bottom panel and its custom widgets/pins. Side panels and panels on
other monitors remain. Raw configuration backups and a live layout export are
saved first. Do not edit the desktop during application. A customized Endvos
top panel with unknown/duplicate widgets is refused rather than rearranged.
Creation/discovery checks do not prove that a widget's QML renders successfully.
Identical widget files are retained on repeat application; changed widget
directories are replaced from the pinned/local sources after backup, using
KPackage installation rather than an unreliable same-version upgrade.

Log out and back in after success. Run the read-only check:

```bash
bash bootstrap.sh --profile endvos-dark --check
```

It checks local assets, selected appearance settings and widget registration,
not visual rendering or a running media player's behavior.

## Recovery and migration

Private backups are under
`${XDG_STATE_HOME:-~/.local/state}/endvos/endvos-dark/<BACKUP_ID>/`.
They include all owned asset paths, `kdeglobals`, `kwinrc`, `plasmarc`,
`plasma-org.kde.plasma.desktop-appletsrc`, `plasmashellrc` and
`kglobalshortcutsrc`. Download caches use the corresponding XDG cache directory.
The manifest records original absence so newly created assets can be removed.
The raw snapshot represents the on-disk state; `live-layout.js` additionally
preserves unsaved panel state. KActivities' external usage/favorites database
is not restored. System packages are retained.

On failure a backup is retained and its ID printed. Log out of Plasma, open a
text console, log in as the same user and run from the repository directory:

```bash
bash bootstrap.sh --profile endvos-dark --restore BACKUP_ID --apply
```

Replace the placeholder with the actual printed ID. The command refuses to
restore while that user's plasmashell is running. Later changes in backed-up
files are also reverted. Backups and caches are retained. Log into Plasma again.

The old `windows11-dark` profile and its original backup contract remain
available. Restore an old backup with `--profile windows11-dark`; restore an
Endvos Dark backup with `--profile endvos-dark`. Never interchange backup IDs
or manifests. Both profiles share a lock so they cannot modify Plasma together.

## VM acceptance

1. Confirm a single new top panel and usable launcher, tray and clock.
2. Open search, launch an installed app and switch to the All Apps list.
3. Focus two different windows and change a window title: the bar must follow.
4. Play music, then minimize all windows/show the desktop: track and artist
   should appear. Stop/pause music: the otherwise unused title area becomes empty.
5. Change the KDE accent: native selections and menu highlights should follow.
6. Reapply: no duplicate panel; edited app pins and custom accent survive.
7. Log out/in, then verify persistence. Test offline recovery using its backup.

## Development checks

```bash
bash -n bootstrap.sh desktop/kde/windows11-dark/check.sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_panel.js
node tests/test_top_panel.js
```

JavaScript tests were run with an isolated V8 engine on the development host;
Node is a development convenience, not an installation dependency. Tests mock
the Plasma API and cover panel replacement scope, failure/resume, repeated
application, pin retention and window-title/music priority. Python tests use
temporary directories and cover no-write planning, staging, palette application,
installed-app selection, migration backups and recoverability after failure.

API references: [Plasma 6.7 task model](https://github.com/KDE/plasma-workspace/blob/Plasma/6.7/libtaskmanager/tasksmodel.h),
[Plasma 6.7 media controller](https://github.com/KDE/plasma-workspace/blob/Plasma/6.7/applets/mediacontroller/main.qml),
[KDE color application](https://github.com/KDE/plasma-workspace/blob/Plasma/6.7/kcms/colors/plasma-apply-colorscheme.cpp),
[task configuration](https://github.com/KDE/plasma-desktop/blob/Plasma/6.7/applets/taskmanager/main.xml),
[clock configuration](https://github.com/KDE/plasma-workspace/blob/Plasma/6.7/applets/digital-clock/main.xml).
