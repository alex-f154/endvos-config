# Architecture

## Target design

This repository describes the desired state of a personal EndeavourOS system
with KDE Plasma. Package sources, user configuration, desktop settings,
services, and hardware profiles remain clearly separated.

The future bootstrap process will orchestrate these areas through understandable,
idempotent steps. Hardware profiles are optional and require explicit selection.
Destructive actions require prior confirmation.

## Current implementation status

The repository provides the directory structure, empty package lists and a
non-installing bootstrap scaffold. An optional Windows 11 dark KDE profile
provides a repeatable panel script, a read-only asset check and manual appearance
setup guidance. It has not been deployed or visually verified on the target.
Package installation, general state reconciliation, GNU Stow links, automatic
KDE appearance import, service activation and hardware detection remain
unimplemented.
