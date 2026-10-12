# endvos-config

Persönliche, reproduzierbare Konfiguration für EndeavourOS/Arch Linux mit KDE
Plasma. Ziel ist, ein frisch installiertes EndeavourOS mit wenigen
Terminalbefehlen in einen dokumentierten, möglichst vollständig
Open-Source-basierten Arbeitszustand zu versetzen.

Dieses Repository befindet sich im Aufbau. Die vorhandenen Dateien bilden
zunächst nur die Struktur ab; sie führen noch keine Installation oder Änderung
am produktiven System aus.

## Voraussetzungen

- Eine frische oder bestehende EndeavourOS-Installation auf Arch-Linux-Basis
- KDE Plasma als Desktop-Umgebung
- `git` und `bash`
- Internetzugang zu den später dokumentierten Paketquellen
- Ein Benutzerkonto mit gezielt einsetzbaren `sudo`-Rechten

Vor einer späteren Anwendung müssen Paketlisten, Hardwareprofil und geplante
Systemänderungen geprüft werden. Secrets wie Passwörter, Tokens und SSH-Keys
gehören niemals in dieses Repository.

## Struktur

- `bootstrap.sh`: sicherer Einstiegspunkt; installiert derzeit nichts
- `packages/`: Paketlisten für Pacman, AUR und später Flatpak
- `dotfiles/`: mit GNU Stow verwaltbare Benutzerkonfigurationen
- `desktop/kde/`: KDE-Plasma-Konfigurationen
- `services/`: deklarative systemd-Konfigurationen
- `hardware/profiles/`: explizit auswählbare, gerätespezifische Anpassungen
- `scripts/`: kleine Hilfsskripte
- `docs/`: Architektur, Entscheidungen und Wiederherstellung

## Aktueller Stand

Aufgabe 001 stellt ausschließlich die Repository-Grundstruktur bereit. Das
Bootstrap-Skript validiert lediglich grundlegende Voraussetzungen und beschreibt
die vorgesehenen späteren Schritte. Leere Paketlisten und Platzhalter-
Dokumentationen sind keine implementierten Installationsfunktionen.

## Roadmap

1. Grundstruktur und Sicherheitsregeln festlegen.
2. Open-Source-Paketbestand erfassen und Paketlisten kuratieren.
3. Dotfiles mit GNU Stow strukturieren.
4. KDE-Einstellungen reproduzierbar exportieren und anwenden.
5. Optionale systemd-Dienste deklarieren.
6. Hardwareprofile entwerfen und ausdrücklich auswählbar machen.
7. Idempotenten Bootstrap- und Wiederherstellungsablauf implementieren.
8. Wiederherstellung auf einer frischen EndeavourOS-Installation testen und
   dokumentieren.

## Verwendung

Der aktuelle Bootstrap ist absichtlich nicht installierend:

```bash
./bootstrap.sh
```

Destruktive oder produktive Änderungen dürfen erst in späteren Aufgaben und nur
nach ausdrücklicher Bestätigung ergänzt oder ausgeführt werden.
