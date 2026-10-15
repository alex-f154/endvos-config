# Recovery

## Planned workflow

Eventually, a fresh EndeavourOS installation should be recoverable from this
repository with only a few terminal commands. The planned workflow separates
packages, dotfiles, KDE Plasma, services, and an optionally selected hardware
profile.

## Current status

A complete system recovery workflow has not been implemented or tested.
`bootstrap.sh` is non-mutating by default; an explicitly selected and applied
desktop profile installs assets and changes user configuration.

## Optional desktop profile

The primary [Endvos Dark profile](../desktop/kde/endvos-dark/README.md) saves
its own private backups under
`${XDG_STATE_HOME:-~/.local/state}/endvos/endvos-dark/<BACKUP_ID>/`.
It includes owned color/widget assets, appearance settings, panel configuration,
global shortcuts and a live layout export. It records which targets were absent.
After logging out of Plasma, from a text console as the same user, restore with:

```bash
bash bootstrap.sh --profile endvos-dark --restore BACKUP_ID --apply
```

This also restores the earlier bottom-panel configuration when the backup was
created during migration. Installed system packages, caches and external
KActivities usage/favorites databases are retained. Changes made later within
the backed-up paths are reverted. Keep the backup. Log back into Plasma after
restoration. Isolated backup/failure tests pass; real-session recovery is pending.

Use the profile that created the backup. The old and new manifest target lists
are intentionally distinct. Both profiles share a lock to prevent simultaneous
configuration changes.

### Earlier Windows 11 profile

The [Windows 11 dark profile](../desktop/kde/windows11-dark/README.md) automatically
backs up affected configuration and theme/widget paths before replacing them.
Backups live in `${XDG_STATE_HOME:-~/.local/state}/endvos/windows11-dark/` and
include a manifest, live layout export and pinned source information.

To restore, log out of Plasma and use a text console as the same user. From the
repository directory, run:

```bash
bash bootstrap.sh --profile windows11-dark --restore BACKUP_ID --apply
```

Use the ID printed during installation. Restoration refuses to run while the
user's plasmashell is active. It restores backed-up paths, removes those newly
created by the profile and retains the backup. Later changes in those paths
are also reverted. System packages and download caches remain installed.

Raw configuration backups reflect the on-disk state at installation time; the
live layout export also records unsaved panel state for additional recovery.
Failure during application stops further work and prints recovery instructions.
Backup/restore round trips and failure handling have been tested only in isolated
temporary directories; desktop recovery and rendering in the VM remain unverified.
