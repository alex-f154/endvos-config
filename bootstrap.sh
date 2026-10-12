#!/usr/bin/env bash

set -Eeuo pipefail

readonly REPOSITORY_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

main() {
  printf 'endvos-config bootstrap (scaffold)\n'
  printf 'Repository: %s\n' "$REPOSITORY_ROOT"

  if [[ ! -r /etc/os-release ]]; then
    printf 'Notice: /etc/os-release is not readable; the target system cannot be checked.\n' >&2
  else
    # This file contains standardized metadata supplied by the distribution.
    # shellcheck disable=SC1091
    source /etc/os-release
    printf 'Detected system: %s\n' "${PRETTY_NAME:-unknown}"
  fi

  printf '\nNo packages will be installed and no system files will be changed.\n'
  printf 'Future steps: package lists, dotfiles, KDE, services, and a hardware profile.\n'
}

main "$@"
