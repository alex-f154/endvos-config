#!/usr/bin/env bash

set -Eeuo pipefail

readonly REPOSITORY_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

main() {
  printf 'endvos-config bootstrap (Grundgerüst)\n'
  printf 'Repository: %s\n' "$REPOSITORY_ROOT"

  if [[ ! -r /etc/os-release ]]; then
    printf 'Hinweis: /etc/os-release ist nicht lesbar; das Zielsystem kann nicht geprüft werden.\n' >&2
  else
    # Die Datei enthält standardisierte, distributionsseitig bereitgestellte Metadaten.
    # shellcheck disable=SC1091
    source /etc/os-release
    printf 'Erkanntes System: %s\n' "${PRETTY_NAME:-unbekannt}"
  fi

  printf '\nEs werden keine Pakete installiert und keine Systemdateien geändert.\n'
  printf 'Spätere Schritte: Paketlisten, Dotfiles, KDE, Dienste und Hardwareprofil.\n'
}

main "$@"
