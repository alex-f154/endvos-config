# Verbindliche Regeln für Codex-Aufgaben

Diese Regeln gelten für das gesamte Repository.

## Projektgrenzen

1. Bevorzuge Open-Source-Software und dokumentiere begründete Ausnahmen.
2. KDE Plasma und EndeavourOS/Arch Linux bleiben die technische Grundlage.
3. Erstelle keine eigene ISO und keine eigene Distribution.
4. Respektiere bereits bestätigte Architekturentscheidungen. Änderungen daran
   müssen als Entscheidung dokumentiert und vom Benutzer bestätigt werden.
5. Implementiere nur den ausdrücklich beauftragten Umfang.

## Sicherheit und Datenschutz

1. Versioniere niemals Passwörter, Tokens, SSH-Schlüssel, private Schlüssel,
   Zugangsdaten oder andere Secrets.
2. Prüfe neue und geänderte Dateien vor Abschluss einer Aufgabe auf mögliche
   Secrets.
3. Verlange vor destruktiven Aktionen eine ausdrückliche Bestätigung. Beschreibe
   dabei Ziel, Auswirkung und Wiederherstellbarkeit.
4. Führe keine produktiven Systemänderungen aus, wenn sie nicht ausdrücklich
   Bestandteil eines späteren, bestätigten Auftrags sind.
5. Nutze keine Befehle, die vorhandene Benutzerdateien ungefragt überschreiben.

## Konfiguration und Implementierung

1. Halte allgemeine Konfiguration frei von hardwareabhängigen Werten.
2. Lege gerätespezifische Anpassungen ausschließlich in
   `hardware/profiles/<profil>/` ab und aktiviere sie nur nach expliziter
   Auswahl.
3. Entwickle Installations- und Konfigurationsskripte idempotent: Wiederholte
   Ausführung muss denselben gewünschten Zustand ergeben.
4. Bevorzuge deklarative Konfiguration, kleine nachvollziehbare Schritte und
   prüfbare Vorbedingungen.
5. Halte Paketlisten nach Quelle getrennt. Vermische Pacman-, AUR- und
   Flatpak-Pakete nicht.
6. Trenne GNU-Stow-Pakete in `dotfiles/` so, dass sie gezielt aktiviert werden
   können.

## Dokumentation und Validierung

1. Beschreibe den tatsächlichen Implementierungsstand wahrheitsgemäß. Roadmap,
   Entwurf und geplante Funktionen dürfen nicht als umgesetzt erscheinen.
2. Dokumentiere neue Architekturentscheidungen in `docs/decisions.md`.
3. Aktualisiere die Wiederherstellungsdokumentation, sobald sich der getestete
   Ablauf ändert.
4. Validiere Shell-Skripte mindestens mit `bash -n` und führe passende,
   nicht-destruktive Prüfungen aus.
5. Prüfe vor Abschluss `git diff`, `git status` und die geänderten Inhalte auf
   versehentlich enthaltene Secrets.
6. Erstelle keine Commits und pushe keine Änderungen ohne ausdrückliche
   Freigabe des Benutzers.
