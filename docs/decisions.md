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

## Confirmed Endvos UI redesign and stage 1 (2026-10-15)

The user replaced the Windows 11 clone target with an approved interactive
design based on supplied screenshots: a narrow top bar, apps at the left,
status and clock at the right, Windows-style search/pinned/All Apps launcher,
dark surfaces and a centrally adjustable accent. The active window title always
takes priority in the middle; playing music appears only with no active window.
An integrated right-side control center and Windows-style snap-layout selection
are confirmed later stages. Windows remain freely movable. KDE Plasma remains
the desktop; the reference screenshots' Hyprland stack is not adopted.

The user authorized stage 1 implementation. `endvos-dark` is the primary profile;
the legacy `windows11-dark` command is retained to preserve its backup contract.
Stage 1 uses native Breeze widgets/decoration and a derived Breeze Dark palette
so KDE's accent propagates, rather than activating fixed Fluent/Kvantum themes.
Menu 11 remains pinned, and a local MIT-licensed QML widget combines task focus
and MPRIS metadata. Only real installed applications seed new pins; repeat
application preserves those pins and existing custom accent colors.

On explicit application, top and bottom panels on the selected runtime monitor
are replaced after replacement widget instances exist. Other monitors and side
panels remain. Backups use a distinct profile directory and explicit target list;
both installers share a mutation lock. There is no automatic VM deployment.
Native QML compatibility, exact geometry and real-session recovery are pending
target testing; custom control center and snap picker are not implemented yet.
