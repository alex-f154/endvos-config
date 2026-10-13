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
foundation. The profile is opt-in and separate from the non-installing bootstrap.

The initial implementation provides a marked, repeatable bottom-panel layout
and documents Fluent round dark and Menu 11 Next as appearance components.
These components are candidates pending validation on the target. Dependency
installation, visual parity and recovery have not been verified. Existing
desktop configuration must be backed up before an approved application.
