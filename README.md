# endvos-config

A personal, reproducible configuration for EndeavourOS/Arch Linux with KDE
Plasma. The goal is to restore a freshly installed EndeavourOS system to a
documented, predominantly open-source working environment with only a few
terminal commands.

This repository is under development. It provides an initial structure and an
opt-in Windows 11 dark KDE profile. The bootstrap makes no changes by default.
Explicit profile application installs desktop assets and changes user settings;
an additional flag permits installation of missing official packages.

## Prerequisites

- A fresh or existing Arch-based EndeavourOS installation
- KDE Plasma as the desktop environment
- `git` and `bash`
- Python 3.11+ with the safe tarfile data filter for the desktop profile
- Internet access to GitHub downloads and the configured Arch package sources
- A user account with deliberately applied `sudo` privileges

Review package lists, the selected hardware profile, and every proposed system
change before applying a future configuration. Secrets such as passwords,
tokens, and SSH keys must never be stored in this repository.

## Structure

- `bootstrap.sh`: preview by default; explicit desktop profile application
- `packages/`: package lists for Pacman, AUR, and later Flatpak
- `dotfiles/`: user configuration managed with GNU Stow
- `desktop/kde/`: KDE Plasma configuration
- `services/`: declarative systemd configuration
- `hardware/profiles/`: explicitly selected, device-specific adjustments
- `scripts/`: small helper scripts
- `docs/`: architecture, decisions, and recovery documentation

## Current status

The optional [Windows 11 dark desktop profile](desktop/kde/windows11-dark/README.md)
downloads pinned, checksum-verified sources and installs themes, icons, cursor,
Kvantum settings, a start menu and a bottom panel. It supports backups and
restoration. Profile-specific Pacman dependencies are kept under
`packages/profiles/`; general package lists remain empty. Isolated tests pass;
deployment, visual output and recovery on the reported Plasma 6.7.5 VM remain
unverified. A complete system recovery workflow is still unimplemented.

## Roadmap

1. Establish the repository structure and safety rules.
2. Inventory open-source packages and curate package lists.
3. Organize dotfiles with GNU Stow.
4. Export and apply KDE settings reproducibly.
5. Declare optional systemd services.
6. Design hardware profiles that require explicit selection.
7. Implement an idempotent bootstrap and recovery workflow.
8. Test and document recovery on a fresh EndeavourOS installation.

## Usage

Default invocation performs no installation:

```bash
bash bootstrap.sh
```

Preview the desktop profile without changes:

```bash
bash bootstrap.sh --profile windows11-dark
```

Inside Konsole on the EndeavourOS test VM, explicitly apply it:

```bash
bash bootstrap.sh --profile windows11-dark --apply --install-packages
```

This backs up affected files, installs missing dependencies with Pacman when
needed, activates the appearance and replaces bottom panels on the selected
screen. Run as the normal desktop user. Log out and back in afterward. See the
profile documentation for recovery and the scope of changes.
