# Architecture decisions

## Confirmed foundations

- EndeavourOS/Arch Linux is the operating system foundation.
- KDE Plasma is the desktop environment.
- Open-source software is preferred.
- The project will not create a custom ISO or distribution.
- Hardware-specific configuration remains isolated in explicit profiles.
- Automation should be idempotent.

Further decisions will be documented here with their context, decision, and
consequences after they are confirmed.

## Windows 11 dark visual target (2026-10-13)

The user selected a desktop appearance as close as possible to Windows 11 in
dark mode and reported Plasma 6.7.5. EndeavourOS and KDE Plasma remain the
foundation. The profile is inactive unless explicitly selected in the bootstrap.

The initial implementation provides a marked, repeatable bottom-panel layout
and documents Fluent round dark and Menu 11 Next as appearance components.
These components are candidates pending validation on the target. Dependency
installation, visual parity and recovery have not been verified. Existing
desktop configuration must be backed up before an approved application.

## Automatic desktop profile application (2026-10-15)

The user explicitly requires setup through configuration rather than manually
selecting themes and widgets. The bootstrap now delegates the selected profile
to a Python standard-library installer. Default execution prints a plan only;
`--apply` permits asset replacement and desktop changes, while
`--install-packages` separately permits missing official Pacman dependencies.

Sources are pinned by commit and SHA-256 digest. The installer assembles only
the selected assets without executing upstream installers or importing the
upstream global theme. KPackage installs the widget; KDE commands and the user
session D-Bus apply appearance and the panel. Existing bottom panels on the
runtime-selected monitor are replaced only after widget creation. Other panels,
SDDM, wallpaper and hardware configuration remain outside this change.

Affected configuration and asset paths are backed up privately before replacement.
Offline restoration avoids racing the running Plasma shell. System packages
are not removed during restoration. Tests cover staging, repeatable panel
application and recovery behavior in isolation; a real VM acceptance test is pending.
