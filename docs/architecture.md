# Architecture

## Target design

This repository describes the desired state of a personal EndeavourOS system
with KDE Plasma. Package sources, user configuration, desktop settings,
services, and hardware profiles remain clearly separated.

The future bootstrap process will orchestrate these areas through understandable,
idempotent steps. Hardware profiles are optional and require explicit selection.
Destructive actions require prior confirmation.

## Current implementation status

The primary `endvos-dark` profile implements the first stage of the approved UI
redesign: a 36px top panel, Windows-style launcher, an expanding window-title/music
widget and charcoal native KDE colors. Breeze replaces fixed Qt/Plasma styling
for centralized accent support. An integrated control center and snap-layout
picker are later stages. These are not included in stage 1.

The bootstrap is non-mutating by default. The optional Windows 11 dark profile
provides automated asset installation, appearance activation and panel replacement
with private backups and offline restoration. Theme sources have fixed commits
and SHA-256 hashes; upstream installers are not executed. Only official packages
listed for this profile may be installed with an explicit additional flag.
General package lists remain empty. Isolated installer, restoration and panel
tests pass; deployment and visual output on the target remain unverified.
General state reconciliation, GNU Stow links, other desktop profiles, service
activation, hardware detection and complete system recovery remain unimplemented.
