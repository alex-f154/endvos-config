#!/usr/bin/env bash

set -Eeuo pipefail

readonly REPOSITORY_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

main() {
  if (( $# )); then
    case "$1" in
      --help|-h)
        printf 'Usage: bash bootstrap.sh [--profile windows11-dark [--apply] [--install-packages] [--restore BACKUP_ID]]\n'
        printf 'Without --apply, the profile prints a plan and changes nothing.\n'
        return 0
        ;;
      --profile)
        if [[ "${2:-}" != windows11-dark ]]; then
          printf 'Supported profile: windows11-dark\n' >&2
          return 2
        fi
        shift 2
        if ! command -v python3 >/dev/null 2>&1; then
          printf 'Python 3.11 or newer is required for this profile.\n' >&2
          return 1
        fi
        exec python3 "$REPOSITORY_ROOT/desktop/kde/windows11-dark/install.py" "$@"
        ;;
      *)
        printf 'Unknown option: %s. Use --help.\n' "$1" >&2
        return 2
        ;;
    esac
  fi
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
