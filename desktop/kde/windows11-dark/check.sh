#!/usr/bin/env bash
# Read-only prerequisite inspection. No installation or desktop changes.
set -Eeuo pipefail

if (( $# != 0 )); then
  printf 'Usage: bash desktop/kde/windows11-dark/check.sh\n' >&2
  exit 2
fi

for tool in plasmashell python3; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'Missing command: %s. Run this check on the Plasma target computer.\n' "$tool" >&2
    exit 1
  fi
done

plasma_version=$(plasmashell --version)
printf '%s\n' "$plasma_version"
if [[ ! "$plasma_version" =~ ^plasmashell[[:space:]]6\.7\.[0-9]+$ ]]; then
  printf 'Expected Plasma 6.7.x; compatibility with other versions is not verified.\n' >&2
  exit 1
fi

python3 - <<'PY'
import json
import os
from pathlib import Path

user_data = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local/share")
system_data = os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"
roots = [Path(user_data)] + [Path(item) for item in system_data.split(":") if item]
if any(not root.is_absolute() for root in roots):
    raise SystemExit("XDG data directories must use absolute paths.")

requirements = [
    ("Fluent round dark Plasma style", "plasma/desktoptheme/Fluent-round-dark"),
    ("Fluent dark colors", "color-schemes/FluentDark.colors"),
    ("Fluent dark icons", "icons/Fluent-dark/index.theme"),
    ("Fluent dark cursor", "icons/Fluent-dark-cursors/index.theme"),
    ("Fluent round dark window decoration", "aurorae/themes/Fluent-round-dark"),
    ("Menu 11 Next", "plasma/plasmoids/menu.11.next/metadata.json"),
]
missing = False
for label, relative in requirements:
    matches = [root / relative for root in roots if (root / relative).exists()]
    if not matches:
        print(f"MISSING: {label}")
        missing = True
        continue
    path = matches[0]
    if relative.startswith("plasma/desktoptheme/"):
        if not any((path / name).is_file() for name in ("metadata.json", "metadata.desktop")):
            print(f"INVALID: {label}: theme metadata is missing")
            missing = True
            continue
    if path.name == "metadata.json":
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
            if metadata.get("KPlugin", {}).get("Id") != path.parent.name:
                raise ValueError("plugin ID differs from its directory")
        except (OSError, ValueError, AttributeError) as error:
            print(f"INVALID: {label}: {error}")
            missing = True
            continue
    print(f"FOUND: {label}")

print("Asset presence only: Kvantum, active settings and rendering need a desktop check.")
raise SystemExit(1 if missing else 0)
PY
