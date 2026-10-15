"""Non-destructive tests; all file mutations are confined to TemporaryDirectory."""

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "windows11_profile", REPO / "desktop/kde/windows11-dark/install.py")
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="endvos-unit-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.roots = {"config": self.base / "config", "data": self.base / "data"}
        for path in self.roots.values():
            path.mkdir()

    def test_plan_does_not_create_xdg_directories_or_call_system_tools(self):
        environment = {key: str(self.base / key) for key in
                       ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME")}
        with patch.dict(os.environ, environment), patch.object(profile, "run") as run:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(profile.main([]), 0)
                self.assertEqual(profile.main(["--install-packages"]), 0)
            run.assert_not_called()
        for path in environment.values():
            self.assertFalse(Path(path).exists())

    def test_snapshot_restores_original_files_directories_and_absence(self):
        original = self.roots["config"] / "kdeglobals"
        original.write_text("original colors\n")
        theme = self.roots["data"] / "icons/Fluent-dark"
        theme.mkdir(parents=True)
        (theme / "original.svg").write_text("original icon")
        (theme / "alias.svg").symlink_to("original.svg")
        backup = self.base / "backup"
        profile.snapshot(self.roots, backup)
        original.write_text("changed")
        (theme / "original.svg").write_text("changed icon")
        (theme / "new.svg").write_text("new icon")
        created = self.roots["config"] / "plasmarc"
        created.write_text("new setting")
        profile.restore(self.roots, backup)
        self.assertEqual(original.read_text(), "original colors\n")
        self.assertEqual((theme / "alias.svg").read_text(), "original icon")
        self.assertTrue((theme / "alias.svg").is_symlink())
        self.assertFalse((theme / "new.svg").exists())
        self.assertFalse(created.exists())
        # Recovery is repeatable and does not consume its backup.
        profile.restore(self.roots, backup)
        self.assertEqual(original.read_text(), "original colors\n")

    def test_symlinked_destination_is_rejected_before_snapshot(self):
        external = self.base / "external"
        external.mkdir()
        (external / "keep").write_text("untouched")
        (self.roots["data"] / "icons").symlink_to(external)
        with self.assertRaisesRegex(ValueError, "symlink"):
            profile.snapshot(self.roots, self.base / "backup")
        self.assertFalse((self.base / "backup").exists())
        self.assertEqual((external / "keep").read_text(), "untouched")

    def test_incomplete_or_tampered_backup_cannot_partially_restore(self):
        original = self.roots["config"] / "kdeglobals"
        original.write_text("original")
        backup = self.base / "backup"
        manifest = profile.snapshot(self.roots, backup)
        original.write_text("new")
        index = profile.targets().index(("config", "kdeglobals"))
        (backup / "files" / str(index)).unlink()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            profile.restore(self.roots, backup)
        self.assertEqual(original.read_text(), "new")
        manifest["entries"][0]["relative"] = "../../outside"
        (backup / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            profile.restore(self.roots, backup)
        self.assertEqual(original.read_text(), "new")

    def test_cached_archive_requires_matching_hash(self):
        content = b"archive"
        source = {"revision": "a" * 40, "repository": "example/repo",
                  "sha256": hashlib.sha256(content).hexdigest()}
        cached = self.base / f"test-{source['revision']}.tar.gz"
        cached.write_bytes(content)
        with patch.object(profile.urllib.request, "urlopen") as download:
            self.assertEqual(profile.source_archive("test", source, self.base), cached)
            download.assert_not_called()
            cached.write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                profile.source_archive("test", source, self.base)
            download.assert_not_called()

    def test_archive_rejects_path_traversal_and_escaping_symlinks(self):
        for name, link in (("root/../../outside", None), ("root/link", "../../outside")):
            archive = self.base / "archive.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                item = tarfile.TarInfo(name)
                if link:
                    item.type = tarfile.SYMTYPE
                    item.linkname = link
                stream.addfile(item)
            with self.assertRaises((ValueError, tarfile.TarError)):
                profile.extract(archive, self.base / "extracted")
            self.assertFalse((self.base / "outside").exists())

    def test_dbus_success_without_script_sentinel_is_failure(self):
        with patch.object(profile, "run", return_value="Error: missing widget"):
            with self.assertRaisesRegex(ValueError, "did not finish"):
                profile.evaluate("qdbus6", "script", "ENDVOS_PANEL_OK")

    def test_weather_source_mismatch_does_not_partially_patch_file(self):
        menu = self.base / "menu"
        source = menu / "contents/ui/WeatherCard.qml"
        source.parent.mkdir(parents=True)
        original = "running: true\nchanged upstream method\n"
        source.write_text(original)
        with self.assertRaisesRegex(ValueError, "differs"):
            profile.patch_weather(menu)
        self.assertEqual(source.read_text(), original)

    def test_failure_retains_recoverable_backup(self):
        original = self.roots["config"] / "kdeglobals"
        original.write_text("original")
        state = self.base / "state"
        state.mkdir()
        cache = self.base / "cache"
        staged = self.base / "stage"
        for relative in profile.ASSETS:
            path = staged / "data" / relative
            if relative.endswith(".colors"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("colors")
            else:
                path.mkdir(parents=True)
        (staged / "config/Kvantum/Fluent-roundDark").mkdir(parents=True)
        def command(*args, **kwargs):
            if args[-1] == "org.kde.PlasmaShell.dumpCurrentLayoutJS":
                return "// exported live layout"
            return ""
        def broken_activation(*args):
            original.write_text("partly applied")
            raise ValueError("simulated activation failure")
        with patch.object(profile, "prerequisites", return_value="qdbus6"), \
                patch.object(profile, "evaluate"), \
                patch.object(profile, "source_archive", return_value=self.base / "unused"), \
                patch.object(profile, "extract", return_value=self.base), \
                patch.object(profile, "build_assets", return_value=(staged / "data", staged / "config")), \
                patch.object(profile, "roots", return_value=self.roots), \
                patch.object(profile, "xdg", return_value=cache), \
                patch.object(profile, "activate", side_effect=broken_activation), \
                patch.object(profile, "run", side_effect=command):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaisesRegex(ValueError, "simulated"):
                    profile.apply_profile(argparse.Namespace(install_packages=False), state)
        backup = next(state.iterdir())
        self.assertEqual(json.loads((backup / "manifest.json").read_text())["status"], "failed")
        profile.restore(self.roots, backup)
        self.assertEqual(original.read_text(), "original")


if __name__ == "__main__":
    unittest.main()
