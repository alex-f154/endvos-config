# endvos-config

A personal, reproducible configuration for EndeavourOS/Arch Linux with KDE
Plasma. The goal is to restore a freshly installed EndeavourOS system to a
documented, predominantly open-source working environment with only a few
terminal commands.

This repository is under development. It provides an initial structure and an
opt-in KDE panel profile. The bootstrap does not install software or modify the
host system; manually executing the panel script changes desktop configuration.

## Prerequisites

- A fresh or existing Arch-based EndeavourOS installation
- KDE Plasma as the desktop environment
- `git` and `bash`
- Internet access to the package sources documented later
- A user account with deliberately applied `sudo` privileges

Review package lists, the selected hardware profile, and every proposed system
change before applying a future configuration. Secrets such as passwords,
tokens, and SSH keys must never be stored in this repository.

## Structure

- `bootstrap.sh`: safe entry point; currently installs nothing
- `packages/`: package lists for Pacman, AUR, and later Flatpak
- `dotfiles/`: user configuration managed with GNU Stow
- `desktop/kde/`: KDE Plasma configuration
- `services/`: declarative systemd configuration
- `hardware/profiles/`: explicitly selected, device-specific adjustments
- `scripts/`: small helper scripts
- `docs/`: architecture, decisions, and recovery documentation

## Current status

The bootstrap script checks basic prerequisites and describes the intended
future steps. Package lists remain empty. The optional
[Windows 11 dark desktop profile](desktop/kde/windows11-dark/README.md) includes
a panel script and read-only asset check for the reported Plasma 6.7.5 target.
It has not been deployed or visually verified; dependency installation and a
complete recovery workflow remain unimplemented.

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

The current bootstrap intentionally performs no installation:

```bash
./bootstrap.sh
```

Destructive or production system changes may only be added or run in a future
task after explicit confirmation.
