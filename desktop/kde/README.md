# KDE Plasma

The primary [Endvos Dark profile](endvos-dark/README.md) implements stage 1 of
the approved redesign: a top panel, Windows-style app launcher, active window
title/music fallback and native KDE accent colors. Its control center and
snap-layout picker are planned separately. Application and recovery have
isolated tests; native QML rendering and real VM verification remain pending.

The opt-in [Windows 11 dark profile](windows11-dark/README.md) targets the
reported Plasma 6.7.5 desktop. Select it through `bootstrap.sh` to preview or
explicitly install assets, activate appearance and replace the bottom panel.
It includes private backups, restoration and a read-only asset check. Isolated
tests pass; deployment, visual output and recovery in the VM remain unverified.
