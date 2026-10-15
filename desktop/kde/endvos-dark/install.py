#!/usr/bin/env python3
"""Endvos dark stage 1: top panel, Windows-style launcher and KDE accent color."""

import argparse
import configparser
import datetime
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
# Share archive/path/backup primitives without changing the legacy profile's
# target list. Old backup manifests remain restorable by their original CLI.
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("endvos_common", HERE.parent / "windows11-dark/install.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)

TITLE_ID = "org.endvos.paneltitle"
ASSETS = ("color-schemes/EndvosDark.colors", "plasma/plasmoids/menu.11.next",
          f"plasma/plasmoids/{TITLE_ID}")
CONFIGS = ("kdeglobals", "kwinrc", "plasmarc", "plasma-org.kde.plasma.desktop-appletsrc",
           "plasmashellrc", "kglobalshortcutsrc")
TARGETS = [("data", item) for item in ASSETS] + [("config", item) for item in CONFIGS]
DEFAULT_ACCENT = "#9abca8"
SETTINGS = [
    ("kdeglobals", "Icons", "Theme", "breeze-dark"),
    ("kdeglobals", "KDE", "widgetStyle", "Breeze"),
    ("kwinrc", "org.kde.kdecoration2", "library", "org.kde.breeze"),
    ("kwinrc", "org.kde.kdecoration2", "ButtonsOnLeft", ""),
    ("kwinrc", "org.kde.kdecoration2", "ButtonsOnRight", "IAX"),
    ("kwinrc", "Plugins", "blurEnabled", "true"),
]


def data_directories():
    directories = [common.roots()["data"]] + [Path(value) for value in
                  (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":") if value]
    if any(not directory.is_absolute() for directory in directories):
        raise ValueError("XDG data directories must be absolute")
    return directories


def available_launchers():
    # Seed only applications that actually exist. Subsequent runs keep pins.
    candidates = ("org.kde.dolphin.desktop", "firefox.desktop", "org.mozilla.firefox.desktop",
                  "org.kde.konsole.desktop", "systemsettings.desktop", "code.desktop")
    return [name for name in candidates if any(
        (root / "applications" / name).is_file() for root in data_directories())]


def stored_accent(config):
    existing = common.run("kreadconfig6", "--file", str(config / "kdeglobals"),
                          "--group", "General", "--key", "AccentColor").strip()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", existing):
        return existing
    if re.fullmatch(r"\d{1,3},\d{1,3},\d{1,3}", existing):
        channels = [int(value) for value in existing.split(",")]
        if all(value <= 255 for value in channels):
            return "#" + "".join(f"{value:02x}" for value in channels)
    return None


def current_accent(config):
    return stored_accent(config) or DEFAULT_ACCENT


def tree_signature(root):
    entries = []
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            entries.append((relative, "link", os.readlink(path)))
        elif path.is_file():
            entries.append((relative, "file", common.sha256(path)))
        elif path.is_dir():
            entries.append((relative, "dir", ""))
        else:
            raise ValueError(f"Unsupported widget asset: {path}")
    return entries


def install_widget(source, destination):
    # KPackage can reject same-version upgrades. Keep byte-identical assets;
    # otherwise replace the already-backed-up directory and notify via install.
    if destination.exists() and tree_signature(source) == tree_signature(destination):
        return
    common.remove(destination)
    common.run("kpackagetool6", "--type", "Plasma/Applet", "--install", str(source))


def build_assets(menu, stage):
    data = stage / "data"
    common.copy(menu, data / ASSETS[1])
    common.patch_weather(data / ASSETS[1])
    common.copy(HERE / "widgets" / TITLE_ID, data / ASSETS[2])
    # Start from the target's complete Breeze Dark scheme, preserving KDE's
    # color roles/effects. Change neutral surfaces to the approved charcoal.
    base = next((root / "color-schemes/BreezeDark.colors" for root in data_directories()
                 if (root / "color-schemes/BreezeDark.colors").is_file()), None)
    if base is None:
        raise ValueError("BreezeDark.colors is missing; install the official breeze package")
    colors = configparser.ConfigParser(interpolation=None)
    colors.optionxform = str
    colors.read(base)
    for group, background in (("Window", "28,38,41"), ("View", "20,29,32"),
                              ("Button", "40,52,56"), ("Tooltip", "28,38,41")):
        section = f"Colors:{group}"
        if section not in colors:
            raise ValueError(f"Incomplete Breeze Dark scheme: {section}")
        colors[section]["BackgroundNormal"] = background
        colors[section]["ForegroundNormal"] = "230,236,232"
    if "General" not in colors:
        colors["General"] = {}
    colors["General"]["Name"] = "Endvos Dark"
    target = data / ASSETS[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w") as stream:
        colors.write(stream, space_around_delimiters=False)
    return data


def verify_settings(config):
    expected = SETTINGS + [("kdeglobals", "General", "ColorScheme", "EndvosDark"),
                           ("plasmarc", "Theme", "name", "default")]
    for filename, group, key, value in expected:
        actual = common.run("kreadconfig6", "--file", str(config / filename),
                            "--group", group, "--key", key).strip()
        if actual != value:
            raise ValueError(f"Setting verification failed: {filename}/{group}/{key}")


def activate(config, qdbus, accent):
    for filename, group, key, value in SETTINGS:
        common.write_setting(config, filename, group, key, value)
    # Two separate calls: Plasma 6.7's --accent-color branch ignores the
    # positional scheme argument. The accent call also reapplies edited colors.
    common.run("plasma-apply-colorscheme", "EndvosDark")
    common.run("plasma-apply-colorscheme", "--accent-color", accent)
    common.run("plasma-apply-desktoptheme", "default")
    common.run(qdbus, "org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure")
    verify_settings(config)
    if (stored_accent(config) or "").lower() != accent.lower():
        raise ValueError("KDE accent color readback did not match the requested color")


def widget_ready(qdbus):
    common.evaluate(qdbus, 'if (["menu.11.next", "org.endvos.paneltitle"].every(function (id) '
                    '{ return knownWidgetTypes.indexOf(id) >= 0; })) '
                    '{ print("ENDVOS_WIDGETS_READY"); }', "ENDVOS_WIDGETS_READY")


def check_installed():
    root_map = common.roots()
    for relative in ASSETS:
        path = root_map["data"] / relative
        if relative.endswith(".colors"):
            if not path.is_file():
                raise ValueError(f"Missing colors: {path}")
        else:
            metadata = json.loads((path / "metadata.json").read_text())
            if metadata["KPlugin"]["Id"] != path.name or not (path / "contents/ui/main.qml").is_file():
                raise ValueError(f"Incomplete widget: {path}")
    verify_settings(root_map["config"])
    widget_ready(common.qdbus_command())
    print("Assets, appearance settings and widget registration checked.\n"
          "Now check panel rendering, search, focus/title changes and accent changes in Plasma.")


def apply_profile(args, state):
    if sys.version_info < (3, 11) or not hasattr(tarfile, "data_filter"):
        raise ValueError("Python 3.11+ with the tarfile data filter is required")
    qdbus = common.prerequisites(args.install_packages, REPO / "packages/profiles/endvos-dark.pacman.txt")
    common.evaluate(qdbus, 'print("ENDVOS_SESSION_OK");', "ENDVOS_SESSION_OK")
    root_map = common.roots()
    accent = args.accent or current_accent(root_map["config"])
    launchers = available_launchers()
    source_lock = json.loads((HERE / "sources.json").read_text())
    cache = common.xdg("XDG_CACHE_HOME", ".cache") / "endvos/endvos-dark"
    common.safe_path(cache, ".probe")
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="endvos-dark-") as temporary:
        work = Path(temporary)
        menu = common.extract(common.source_archive("menu11", source_lock["menu11"], cache), work / "source")
        staged = build_assets(menu, work / "stage")
        identifier = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        backup = state / identifier
        manifest = common.snapshot(root_map, backup, TARGETS)
        print(f"Backup: {backup}", flush=True)
        try:
            live = common.run(qdbus, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.dumpCurrentLayoutJS")
            if not live.strip():
                raise ValueError("Plasma did not export its live layout")
            (backup / "live-layout.js").write_text(live)
            (backup / "sources.json").write_text(json.dumps(source_lock, indent=2) + "\n")
            for relative in ASSETS:
                destination = common.safe_path(root_map["data"], relative)
                if relative.startswith("plasma/plasmoids/"):
                    install_widget(staged / relative, destination)
                else:
                    common.remove(destination)
                    common.copy(staged / relative, destination)
            common.run("kbuildsycoca6", "--noincremental")
            for attempt in range(10):
                try:
                    widget_ready(qdbus)
                    break
                except ValueError:
                    if attempt == 9:
                        raise ValueError("Plasma has not discovered the widgets. Log out and back in, then rerun.")
                    time.sleep(0.5)
            activate(root_map["config"], qdbus, accent)
            script = ("var endvosReplacePanels = true;\nvar endvosLaunchers = " +
                      json.dumps(launchers) + ";\n" + (HERE / "layout.js").read_text())
            common.evaluate(qdbus, script, "ENDVOS_TOP_PANEL_OK")
            check_installed()
            manifest["status"] = "applied"
        except BaseException:
            manifest["status"] = "failed"
            print(f"Application stopped. Backup retained: {identifier}\n"
                  "Log out, then restore from a text console as the same user:\n"
                  f"bash bootstrap.sh --profile endvos-dark --restore {identifier} --apply", file=sys.stderr)
            raise
        finally:
            (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Stage 1 applied. Backup: {identifier}\nLog out and back in, then check the desktop.\n"
              "Change the accent in KDE System Settings > Colors.\n"
              "The custom control center and snap-layout selection are later stages.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="back up and apply stage 1")
    mode.add_argument("--check", action="store_true", help="read-only installed asset/settings check in Plasma")
    parser.add_argument("--install-packages", action="store_true", help="allow missing official packages via Pacman")
    parser.add_argument("--accent", metavar="#RRGGBB", help="optional KDE accent; otherwise retain an existing custom color")
    parser.add_argument("--restore", metavar="BACKUP_ID", help="restore this profile's backup while logged out")
    args = parser.parse_args(argv)
    if args.accent and not re.fullmatch(r"#[0-9a-fA-F]{6}", args.accent):
        parser.error("--accent must be a quoted hex color such as '#9abca8'")
    if args.restore and not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", args.restore):
        parser.error("Invalid backup ID")
    if args.restore and (args.accent or args.install_packages or args.check):
        parser.error("--restore cannot be combined with --accent, --install-packages or --check")
    if args.check:
        if args.install_packages or args.accent:
            parser.error("--check cannot install packages or change the accent")
        check_installed()
        return 0
    if not args.apply:
        print("PLAN ONLY: no files, packages, downloads or desktop settings will change.")
        if args.restore:
            print(f"Would restore endvos-dark backup {args.restore} while Plasma is stopped.")
        else:
            print("Would install pinned Menu 11 and the local Endvos title widget;\n"
                  "derive charcoal colors from installed Breeze Dark;\n"
                  "back up appearance, shortcuts, widgets and panel settings;\n"
                  "replace top/bottom panels on the selected screen with one 36px top panel;\n"
                  "show apps left, window title/music in the middle, tray and clock right.\n"
                  "Side panels and other screens are retained. No control center or snap extension yet.")
            print(f"Accent: {args.accent or 'retain custom color, otherwise #9abca8'}.")
            if args.install_packages:
                print("Missing official packages may be installed only with --apply.")
        return 0
    if os.geteuid() == 0:
        raise ValueError("Run as your desktop user, not with sudo")
    os.umask(0o077)
    state = common.xdg("XDG_STATE_HOME", ".local/state") / "endvos/endvos-dark"
    common.safe_path(state, "lock")
    state.mkdir(parents=True, exist_ok=True)
    # Use the legacy lock too: both profiles touch the same Plasma config files.
    shared_state = common.xdg("XDG_STATE_HOME", ".local/state") / "endvos/windows11-dark"
    common.safe_path(shared_state, "lock")
    shared_state.mkdir(parents=True, exist_ok=True)
    with (shared_state / "lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("Another desktop profile operation is running") from error
        if args.restore:
            if common.plasma_running():
                raise ValueError("Log out of Plasma and restore from a text console as the same user")
            common.restore(common.roots(), common.safe_path(state, args.restore), TARGETS)
            print("Backup restored. Log back in. Packages and caches retained.")
        else:
            apply_profile(args, state)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, tarfile.TarError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        print(f"ERROR: {detail.strip()}", file=sys.stderr)
        raise SystemExit(1)
