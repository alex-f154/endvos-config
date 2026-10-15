#!/usr/bin/env python3
"""Opt-in user-local Plasma profile installer; no changes without --apply."""

import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ASSETS = (
    "plasma/desktoptheme/Fluent-round-dark",
    "color-schemes/FluentDark.colors",
    "icons/Fluent-dark",
    "icons/Fluent-dark-cursors",
    "aurorae/themes/Fluent-round-dark",
    "plasma/plasmoids/menu.11.next",
)
CONFIGS = (
    "kdeglobals", "kwinrc", "plasmarc", "kcminputrc",
    "plasma-org.kde.plasma.desktop-appletsrc", "plasmashellrc",
    "kglobalshortcutsrc", "Kvantum/kvantum.kvconfig", "Kvantum/Fluent-roundDark",
)


def run(*args, interactive=False):
    result = subprocess.run(args, check=True, text=True,
                            stdout=None if interactive else subprocess.PIPE,
                            stderr=None if interactive else subprocess.PIPE,
                            timeout=None if interactive else 120)
    return result.stdout or ""


def xdg(variable, fallback):
    path = Path(os.environ.get(variable) or Path.home() / fallback)
    if not path.is_absolute():
        raise ValueError(f"{variable} must be an absolute path")
    return path


def roots():
    return {"data": xdg("XDG_DATA_HOME", ".local/share"),
            "config": xdg("XDG_CONFIG_HOME", ".config")}


def targets():
    return [("data", item) for item in ASSETS] + [("config", item) for item in CONFIGS]


def safe_path(base, relative):
    """Never traverse a symlink while replacing user configuration."""
    path = base / relative
    if not path.is_relative_to(base) or ".." in Path(relative).parts:
        raise ValueError("Path outside the profile")
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError(f"Refusing symlink destination: {parent}")
    return path


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination)


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def merge(source, destination):
    """Overlay a source tree in a private staging directory, preserving aliases."""
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_symlink():
            remove(target)
            target.symlink_to(os.readlink(child))
        elif child.is_dir():
            if target.is_symlink() or target.is_file():
                remove(target)
            merge(child, target)
        else:
            remove(target)
            shutil.copy2(child, target)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_archive(name, source, cache):
    path = cache / f"{name}-{source['revision']}.tar.gz"
    if not path.exists():
        url = f"https://codeload.github.com/{source['repository']}/tar.gz/{source['revision']}"
        print(f"Download: {name}", flush=True)
        # A failed download never becomes a cached, supposedly complete archive.
        with tempfile.NamedTemporaryFile(dir=cache, delete=True) as temporary:
            with urllib.request.urlopen(url, timeout=60) as response:
                shutil.copyfileobj(response, temporary)
            temporary.flush()
            if sha256(Path(temporary.name)) != source["sha256"]:
                raise ValueError(f"SHA-256 mismatch: {name}")
            shutil.copyfile(temporary.name, path)
    if sha256(path) != source["sha256"]:
        raise ValueError(f"SHA-256 mismatch in cache: {path}")
    return path


def extract(archive_path, destination):
    with tarfile.open(archive_path) as archive:
        members = archive.getmembers()
        top_levels = {Path(member.name).parts[0] for member in members}
        if len(top_levels) != 1 or any(Path(member.name).is_absolute() or
                                      ".." in Path(member.name).parts for member in members):
            raise ValueError("Unexpected archive paths")
        # 'data' rejects escaping links, special devices and path traversal.
        archive.extractall(destination, filter="data")
    return destination / top_levels.pop()


def patch_weather(menu):
    """Honor the disabled weather setting and supply the caller's missing method."""
    path = menu / "contents/ui/WeatherCard.qml"
    content = path.read_text()
    changes = {
        "running: true": "running: weatherCard.visible",
        "    function fetchWeatherFromAPI() {": (
            "    function updateWeather() {\n"
            "        fetchWeatherFromAPI();\n"
            "    }\n\n"
            "    function fetchWeatherFromAPI() {\n"
            "        if (!weatherCard.visible) { return; }"),
    }
    for before, after in changes.items():
        if content.count(before) != 1:
            raise ValueError("Pinned Menu 11 weather source differs from expected content")
        content = content.replace(before, after)
    path.write_text(content)


def build_assets(sources, stage):
    kde, icons, menu = (sources[key] for key in ("fluent-kde", "fluent-icons", "menu11"))
    data, config = stage / "data", stage / "config"
    style = data / ASSETS[0]
    copy(kde / "plasma/desktoptheme/Fluent-round", style)
    copy(kde / "color-schemes/FluentDark.colors", data / ASSETS[1])
    shutil.copy2(data / ASSETS[1], style / "colors")
    # Plasma 6 metadata with the installed ID; retain upstream effect settings.
    (style / "metadata.json").write_text(json.dumps({
        "KPlugin": {"Id": "Fluent-round-dark", "Name": "Fluent round dark (Endvos)",
                    "Description": "Fluent rounded Plasma style with dark colors",
                    "License": "LGPL", "Authors": [{"Name": "Vince Liuice"}]}
    }, indent=2) + "\n")

    icon_theme = data / ASSETS[2]
    icon_theme.mkdir(parents=True)
    for size in ("16", "22", "24", "32", "256", "scalable", "symbolic"):
        for tree in (icons / "src" / size, icons / "links" / size):
            if tree.is_dir():
                merge(tree, icon_theme / size)
    # Match upstream's standard dark variant without building other variants.
    dark_dirs = [f"{size}/{kind}" for size in ("16", "22", "24")
                 for kind in ("actions", "devices", "places")]
    dark_dirs += ["22/categories", "32/actions", "32/devices", "32/status", "symbolic"]
    for directory in dark_dirs:
        for svg in (icon_theme / directory).rglob("*.svg"):
            if not svg.is_symlink():
                svg.write_text(svg.read_text().replace("#363636", "#dedede"))
    (icon_theme / "index.theme").write_text(
        (icons / "src/index.theme").read_text().replace("%NAME%", "Fluent dark"))
    for scale in (2, 3):
        for size in ("16", "22", "24", "32", "256", "scalable"):
            (icon_theme / f"{size}@{scale}x").symlink_to(size)
    copy(icons / "COPYING", icon_theme / "COPYING")
    copy(icons / "cursors/dist-dark", data / ASSETS[3])
    copy(icons / "cursors/LICENSE", data / ASSETS[3] / "LICENSE")
    copy(kde / "aurorae/Fluent-round-dark", data / ASSETS[4])
    copy(menu, data / ASSETS[5])
    patch_weather(data / ASSETS[5])
    kvantum = config / "Kvantum/Fluent-roundDark"
    for suffix in ("kvconfig", "svg"):
        copy(kde / f"Kvantum/Fluent-round/Fluent-roundDark.{suffix}",
             kvantum / f"Fluent-roundDark.{suffix}")
    copy(kde / "LICENSE", style / "UPSTREAM-LICENSE")
    copy(kde / "LICENSE", kvantum / "UPSTREAM-LICENSE")
    # Some upstream icon aliases lack a target. Let hicolor handle those names.
    # Never install a symlink escaping the staged assets.
    pruned = 0
    for root in (data, config):
        for path in root.rglob("*"):
            if not path.is_symlink():
                continue
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError(f"Escaping asset link: {path}")
            if not path.exists():
                path.unlink()
                pruned += 1
    if pruned:
        print(f"Skipped {pruned} upstream aliases with missing targets.")
    return data, config


def snapshot(root_map, backup):
    entries = []
    # Check every target before copying or changing any of them.
    for root, relative in targets():
        safe_path(root_map[root], relative)
    backup.mkdir(mode=0o700)
    for index, (root, relative) in enumerate(targets()):
        path = safe_path(root_map[root], relative)
        entry = {"root": root, "relative": relative, "exists": path.exists()}
        if entry["exists"]:
            copy(path, backup / "files" / str(index))
        entries.append(entry)
    manifest = {"roots": {key: str(value) for key, value in root_map.items()},
                "entries": entries, "status": "prepared"}
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def restore(root_map, backup):
    manifest = json.loads((backup / "manifest.json").read_text())
    expected = targets()
    if manifest["roots"] != {key: str(value) for key, value in root_map.items()}:
        raise ValueError("Backup belongs to different XDG directories")
    if [(entry["root"], entry["relative"]) for entry in manifest["entries"]] != expected:
        raise ValueError("Unexpected backup targets")
    for index, entry in enumerate(manifest["entries"]):
        safe_path(root_map[entry["root"]], entry["relative"])
        if entry["exists"] and not (backup / "files" / str(index)).exists():
            raise ValueError("Incomplete backup; no files restored")
    for index, entry in enumerate(manifest["entries"]):
        target = safe_path(root_map[entry["root"]], entry["relative"])
        remove(target)
        if entry["exists"]:
            copy(backup / "files" / str(index), target)


def plasma_running():
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid == os.getuid() and (entry / "comm").read_text().strip() == "plasmashell":
                return True
        except (OSError, ProcessLookupError):
            continue
    return False


def qdbus_command():
    for candidate in ("qdbus6", "/usr/lib/qt6/bin/qdbus", "qdbus"):
        if shutil.which(candidate):
            return candidate
    raise ValueError("Qt6 qdbus is missing (package qt6-tools)")


def evaluate(qdbus, script, sentinel):
    output = run(qdbus, "org.kde.plasmashell", "/PlasmaShell",
                 "org.kde.PlasmaShell.evaluateScript", script)
    if sentinel not in output:
        raise ValueError(f"Plasma script did not finish: {output.strip()}")
    return output


def prerequisites(install_packages):
    if os.geteuid() == 0:
        raise ValueError("Run as your desktop user, not with sudo")
    os_info = Path("/etc/os-release").read_text()
    if not re.search(r'^ID=(?:"?)(?:endeavouros|arch)(?:"?)$', os_info, re.M):
        raise ValueError("This profile requires EndeavourOS or Arch Linux")
    if not shutil.which("pacman") or not shutil.which("plasmashell"):
        raise ValueError("Run inside the EndeavourOS Plasma VM")
    if not re.fullmatch(r"plasmashell\s+6\.7\.\d+", run("plasmashell", "--version").strip()):
        raise ValueError("This profile currently targets Plasma 6.7.x")
    if not plasma_running() or not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        raise ValueError("Run from Konsole inside your logged-in Plasma desktop")
    packages = [line for line in (REPO / "packages/profiles/windows11-dark.pacman.txt").read_text().splitlines()
                if line and not line.startswith("#")]
    missing = [package for package in packages if subprocess.run(
        ["pacman", "-Q", package], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, check=False).returncode]
    if missing:
        if not install_packages:
            raise ValueError("Missing packages: " + ", ".join(missing) +
                             ". Add --install-packages to allow installation.")
        # No database refresh, partial upgrade, blanket upgrade or AUR helper.
        run("sudo", "pacman", "-S", "--needed", "--", *missing, interactive=True)
    for tool in ("kwriteconfig6", "kreadconfig6", "kpackagetool6", "kbuildsycoca6",
                 "plasma-apply-colorscheme", "plasma-apply-desktoptheme", "plasma-apply-cursortheme"):
        if not shutil.which(tool):
            raise ValueError(f"Required Plasma command missing: {tool}")
    return qdbus_command()


def write_setting(config, filename, group, key, value):
    run("kwriteconfig6", "--file", str(config / filename), "--group", group,
        "--key", key, "--", value)


def activate(config, qdbus):
    settings = [
        ("kdeglobals", "Icons", "Theme", "Fluent-dark"),
        ("kdeglobals", "KDE", "widgetStyle", "kvantum-dark"),
        ("Kvantum/kvantum.kvconfig", "General", "theme", "Fluent-roundDark"),
        ("kwinrc", "org.kde.kdecoration2", "library", "org.kde.kwin.aurorae"),
        ("kwinrc", "org.kde.kdecoration2", "theme", "__aurorae__svg__Fluent-round-dark"),
        ("kwinrc", "org.kde.kdecoration2", "ButtonsOnLeft", ""),
        ("kwinrc", "org.kde.kdecoration2", "ButtonsOnRight", "IAX"),
        ("kwinrc", "Plugins", "blurEnabled", "true"),
    ]
    for filename, group, key, value in settings:
        write_setting(config, filename, group, key, value)
    run("plasma-apply-colorscheme", "FluentDark")
    run("plasma-apply-desktoptheme", "Fluent-round-dark")
    run("plasma-apply-cursortheme", "Fluent-dark-cursors")
    run(qdbus, "org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure")
    expected_settings = settings + [
        ("kdeglobals", "General", "ColorScheme", "FluentDark"),
        ("plasmarc", "Theme", "name", "Fluent-round-dark"),
        ("kcminputrc", "Mouse", "cursorTheme", "Fluent-dark-cursors"),
    ]
    for filename, group, key, value in expected_settings:
        actual = run("kreadconfig6", "--file", str(config / filename),
                     "--group", group, "--key", key).strip()
        if actual != value:
            raise ValueError(f"Setting verification failed: {filename}/{group}/{key}")


def apply_profile(args, state):
    if sys.version_info < (3, 11) or not hasattr(tarfile, "data_filter"):
        raise ValueError("Python 3.11+ with the tarfile data filter is required")
    qdbus = prerequisites(args.install_packages)
    # Prove the user session is reachable before downloads or configuration writes.
    evaluate(qdbus, 'print("ENDVOS_SESSION_OK");', "ENDVOS_SESSION_OK")
    source_lock = json.loads((HERE / "sources.json").read_text())
    cache = xdg("XDG_CACHE_HOME", ".cache") / "endvos/windows11-dark"
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="endvos-profile-") as temporary:
        work = Path(temporary)
        sources = {name: extract(source_archive(name, source, cache), work / name)
                   for name, source in source_lock.items()}
        data, staged_config = build_assets(sources, work / "stage")
        root_map = roots()
        identifier = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        backup = state / identifier
        manifest = snapshot(root_map, backup)
        print(f"Backup: {backup}", flush=True)
        try:
            live_layout = run(qdbus, "org.kde.plasmashell", "/PlasmaShell",
                              "org.kde.PlasmaShell.dumpCurrentLayoutJS")
            if not live_layout.strip():
                raise ValueError("Plasma did not export the existing live layout")
            (backup / "live-layout.js").write_text(live_layout)
            (backup / "sources.json").write_text(json.dumps(source_lock, indent=2) + "\n")
            for relative in ASSETS:
                destination = safe_path(root_map["data"], relative)
                if relative == "plasma/plasmoids/menu.11.next":
                    # KPackage notifies the running shell about the new widget.
                    mode = "--upgrade" if destination.exists() else "--install"
                    run("kpackagetool6", "--type", "Plasma/Applet", mode, str(data / relative))
                else:
                    remove(destination)
                    copy(data / relative, destination)
            destination = safe_path(root_map["config"], "Kvantum/Fluent-roundDark")
            remove(destination)
            copy(staged_config / "Kvantum/Fluent-roundDark", destination)
            run("kbuildsycoca6", "--noincremental")
            # Allow KPackage's discovery notification to reach the running shell.
            for attempt in range(10):
                try:
                    evaluate(qdbus, 'if (knownWidgetTypes.indexOf("menu.11.next") >= 0) '
                             '{ print("ENDVOS_WIDGET_READY"); }', "ENDVOS_WIDGET_READY")
                    break
                except ValueError:
                    if attempt == 9:
                        raise ValueError("Plasma has not discovered Menu 11. Log out and back in, then rerun the installer.")
                    time.sleep(0.5)
            activate(root_map["config"], qdbus)
            # Explicit --apply authorizes replacing bottom panels on this screen.
            script = "var endvosReplaceBottomPanels = true;\n" + (HERE / "layout.js").read_text()
            evaluate(qdbus, script, "ENDVOS_PANEL_OK")
            run("bash", str(HERE / "check.sh"))
            manifest["status"] = "applied"
        except BaseException:
            manifest["status"] = "failed"
            print(f"Application stopped. Backup retained: {identifier}\n"
                  "Log out of Plasma, then restore from a text console with:\n"
                  f"bash bootstrap.sh --profile windows11-dark --restore {identifier} --apply",
                  file=sys.stderr)
            raise
        finally:
            (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print("Profile applied. Log out and back in to reload application styles and icons.\n"
              f"Recovery backup: {identifier}\nVisual verification in the VM is still required.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="install assets and replace the bottom panel; existing settings are backed up")
    parser.add_argument("--install-packages", action="store_true", help="allow sudo pacman to install missing profile dependencies")
    parser.add_argument("--restore", metavar="BACKUP_ID", help="restore a backup while logged out of Plasma")
    args = parser.parse_args(argv)
    if args.restore and not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", args.restore):
        parser.error("Invalid backup ID")
    if args.restore and args.install_packages:
        parser.error("--restore cannot be combined with --install-packages")
    if not args.apply:
        print("PLAN ONLY: no files, packages or desktop settings will be changed.")
        if args.restore:
            print(f"Would restore backup {args.restore} while Plasma is stopped.")
        else:
            print("Would download SHA-256-verified, pinned Fluent and Menu 11 sources;\n"
                  "back up affected user configuration and theme directories;\n"
                  "install dark themes, icons, cursor and start menu locally;\n"
                  "activate the appearance and replace bottom panels on the selected screen.\n"
                  "Other panels, wallpaper, SDDM, networking and hardware are untouched.")
            if args.install_packages:
                print("Missing packages may be installed using sudo pacman only with --apply.")
        return 0
    if os.geteuid() == 0:
        raise ValueError("Run as your desktop user, not with sudo")
    os.umask(0o077)
    state = xdg("XDG_STATE_HOME", ".local/state") / "endvos/windows11-dark"
    safe_path(state, "lock")
    state.mkdir(parents=True, exist_ok=True)
    with (state / "lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("Another profile operation is running") from error
        if args.restore:
            if plasma_running():
                raise ValueError("Log out of Plasma first; restore from a text console as the same user")
            restore(roots(), safe_path(state, args.restore))
            print("Backup restored. Log in to Plasma. Installed system packages were retained.")
        else:
            apply_profile(args, state)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        print(f"ERROR: {detail.strip()}", file=sys.stderr)
        raise SystemExit(1)
