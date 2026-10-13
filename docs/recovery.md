# Recovery

## Planned workflow

Eventually, a fresh EndeavourOS installation should be recoverable from this
repository with only a few terminal commands. The planned workflow separates
packages, dotfiles, KDE Plasma, services, and an optionally selected hardware
profile.

## Current status

A complete recovery workflow has not been implemented or tested. `bootstrap.sh`
currently performs no installation or production system changes. This file does
not yet document a complete executable recovery procedure.

## Optional desktop profile

The [Windows 11 dark profile](../desktop/kde/windows11-dark/README.md) documents
backup, preview and restoration steps for its panel and appearance components.
That desktop procedure has not been tested on the target and does not constitute
a complete system recovery workflow.
