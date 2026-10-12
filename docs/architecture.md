# Architecture

## Target design

This repository describes the desired state of a personal EndeavourOS system
with KDE Plasma. Package sources, user configuration, desktop settings,
services, and hardware profiles remain clearly separated.

The future bootstrap process will orchestrate these areas through understandable,
idempotent steps. Hardware profiles are optional and require explicit selection.
Destructive actions require prior confirmation.

## Current implementation status

The repository currently provides the directory structure, empty package lists,
and a non-installing bootstrap scaffold. Package installation, state
reconciliation, GNU Stow links, KDE import, service activation, and hardware
detection have not been implemented.
