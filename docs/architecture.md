# Architektur

## Zielbild

Das Repository beschreibt den gewünschten Zustand eines persönlichen
EndeavourOS-Systems mit KDE Plasma. Paketquellen, Benutzerkonfiguration,
Desktop-Einstellungen, Dienste und Hardwareprofile bleiben klar getrennt.

Der spätere Bootstrap orchestriert diese Bereiche in nachvollziehbaren,
idempotenten Schritten. Hardwareprofile sind optional und explizit auszuwählen.
Destruktive Aktionen benötigen eine vorherige Bestätigung.

## Aktueller Implementierungsstand

Vorhanden sind die Verzeichnisstruktur, leere Paketlisten und ein
nicht-installierendes Bootstrap-Grundgerüst. Installation, Zustandsabgleich,
GNU-Stow-Verknüpfungen, KDE-Import, Dienstaktivierung und Hardwareerkennung sind
noch nicht implementiert.
