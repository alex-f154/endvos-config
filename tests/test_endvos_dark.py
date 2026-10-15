"""Stage-1 tests: temporary files only; no installed desktop is modified."""
import argparse
import configparser
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("endvos_dark", REPO / "desktop/kde/endvos-dark/install.py")
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


class EndvosDarkTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="endvos-top-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.roots = {name: self.base / name for name in ("config", "data")}
        for path in self.roots.values():
            path.mkdir()

    def test_preview_and_restore_preview_do_not_write_or_run_commands(self):
        environment = {name: str(self.base / name) for name in
                       ("XDG_STATE_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME")}
        with patch.dict(os.environ, environment), patch.object(profile.common, "run") as run:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(profile.main([]), 0)
                self.assertEqual(profile.main(["--install-packages", "--accent", "#abcdef"]), 0)
                self.assertEqual(profile.main(["--restore", "20261015T123456Z-01234567"]), 0)
            run.assert_not_called()
        for path in environment.values():
            self.assertFalse(Path(path).exists())

    def test_cli_rejects_conflicting_or_invalid_options_before_commands(self):
        combinations = (["--accent", "green"], ["--accent", "#fff"],
                        ["--apply", "--check"], ["--check", "--install-packages"],
                        ["--restore", "../../outside"],
                        ["--restore", "20261015T123456Z-01234567", "--accent", "#123456"])
        with patch.object(profile.common, "run") as run, contextlib.redirect_stderr(io.StringIO()):
            for arguments in combinations:
                with self.subTest(arguments=arguments), self.assertRaises(SystemExit):
                    profile.main(arguments)
            run.assert_not_called()

    def test_backup_restores_migration_and_does_not_change_legacy_manifest_contract(self):
        self.assertNotIn(("data", profile.ASSETS[2]), profile.common.targets())
        original = self.roots["config"] / "plasma-org.kde.plasma.desktop-appletsrc"
        original.write_text("old bottom panel and shortcuts")
        backup = self.base / "backup"
        profile.common.snapshot(self.roots, backup, profile.TARGETS)
        original.write_text("new top panel")
        title = self.roots["data"] / profile.ASSETS[2]
        title.mkdir(parents=True)
        (title / "metadata.json").write_text("new widget")
        # The original profile must reject this manifest, without restoring it.
        with self.assertRaisesRegex(ValueError, "Unexpected backup targets"):
            profile.common.restore(self.roots, backup)
        self.assertEqual(original.read_text(), "new top panel")
        profile.common.restore(self.roots, backup, profile.TARGETS)
        self.assertEqual(original.read_text(), "old bottom panel and shortcuts")
        self.assertFalse(title.exists())
        profile.common.restore(self.roots, backup, profile.TARGETS)

    def test_appearance_uses_two_color_calls_and_keeps_accent(self):
        with patch.object(profile.common, "run") as run, \
                patch.object(profile, "verify_settings"), \
                patch.object(profile, "stored_accent", return_value="#AABBCC"):
            profile.activate(self.roots["config"], "qdbus6", "#aabbcc")
        calls = [call.args for call in run.call_args_list]
        self.assertIn(("plasma-apply-colorscheme", "EndvosDark"), calls)
        self.assertIn(("plasma-apply-colorscheme", "--accent-color", "#aabbcc"), calls)
        self.assertLess(calls.index(("plasma-apply-colorscheme", "EndvosDark")),
                        calls.index(("plasma-apply-colorscheme", "--accent-color", "#aabbcc")))
        self.assertFalse(any("kvantum" in str(call).lower() for call in calls))

    def test_missing_accent_readback_cannot_be_mistaken_for_default_success(self):
        with patch.object(profile.common, "run"), patch.object(profile, "verify_settings"), \
                patch.object(profile, "stored_accent", return_value=None):
            with self.assertRaisesRegex(ValueError, "accent color readback"):
                profile.activate(self.roots["config"], "qdbus6", profile.DEFAULT_ACCENT)

    def test_widget_repeat_skips_same_version_and_replaces_changed_assets(self):
        source, destination = self.base / "source", self.base / "installed"
        source.mkdir()
        (source / "main.qml").write_text("widget content")
        profile.common.copy(source, destination)
        with patch.object(profile.common, "run") as run:
            profile.install_widget(source, destination)
            run.assert_not_called()
            (destination / "main.qml").write_text("user customization")
            profile.install_widget(source, destination)
            run.assert_called_once_with("kpackagetool6", "--type", "Plasma/Applet", "--install", str(source))
        self.assertFalse(destination.exists())

    def test_existing_accent_formats_and_default(self):
        for stored, expected in (("123,45,67", "#7b2d43"), ("#AABBCC", "#AABBCC"),
                                 ("999,1,2", profile.DEFAULT_ACCENT), ("", profile.DEFAULT_ACCENT)):
            with self.subTest(stored=stored), patch.object(profile.common, "run", return_value=stored):
                self.assertEqual(profile.current_accent(self.roots["config"]), expected)

    def test_launcher_seed_contains_only_real_desktop_files(self):
        apps = self.roots["data"] / "applications"
        apps.mkdir()
        (apps / "org.kde.dolphin.desktop").write_text("[Desktop Entry]\n")
        with patch.object(profile, "data_directories", return_value=[self.roots["data"]]):
            self.assertEqual(profile.available_launchers(), ["org.kde.dolphin.desktop"])

    def test_staging_preserves_base_color_roles_and_patches_menu(self):
        schemes = self.roots["data"] / "color-schemes"
        schemes.mkdir()
        (schemes / "BreezeDark.colors").write_text(
            "[General]\nName=Breeze Dark\n[Colors:Window]\nBackgroundNormal=1,2,3\n"
            "[Colors:View]\nForegroundInactive=4,5,6\n[Colors:Button]\n[Colors:Tooltip]\n"
            "[Colors:Selection]\nBackgroundNormal=7,8,9\n[ColorEffects:Disabled]\nIntensityAmount=0.1\n")
        menu = self.base / "menu"
        (menu / "contents/ui").mkdir(parents=True)
        (menu / "contents/ui/WeatherCard.qml").write_text(
            "running: true\n    function fetchWeatherFromAPI() {\n    }\n")
        with patch.object(profile, "data_directories", return_value=[self.roots["data"]]):
            staged = profile.build_assets(menu, self.base / "stage")
        colors = configparser.ConfigParser()
        colors.read(staged / profile.ASSETS[0])
        self.assertEqual(colors["Colors:Window"]["BackgroundNormal"], "28,38,41")
        self.assertEqual(colors["Colors:View"]["ForegroundInactive"], "4,5,6")
        self.assertEqual(colors["Colors:Selection"]["BackgroundNormal"], "7,8,9")
        self.assertEqual(colors["ColorEffects:Disabled"]["IntensityAmount"], "0.1")
        self.assertIn("running: weatherCard.visible", (staged / profile.ASSETS[1] / "contents/ui/WeatherCard.qml").read_text())
        self.assertTrue((staged / profile.ASSETS[2] / "contents/ui/main.qml").is_file())

    def test_failed_activation_retains_new_profile_recovery(self):
        original = self.roots["config"] / "kdeglobals"
        original.write_text("old appearance")
        state = self.base / "state"
        state.mkdir()
        staged = self.base / "stage"
        for relative in profile.ASSETS:
            path = staged / relative
            if relative.endswith(".colors"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("colors")
            else:
                path.mkdir(parents=True)
        def command(*args, **kwargs):
            if args[-1] == "org.kde.PlasmaShell.dumpCurrentLayoutJS":
                return "// live old panel"
            return ""
        def fail(*args):
            original.write_text("partial appearance")
            raise ValueError("activation failed")
        with patch.object(profile.common, "prerequisites", return_value="qdbus6"), \
                patch.object(profile.common, "evaluate"), \
                patch.object(profile.common, "source_archive"), \
                patch.object(profile.common, "extract"), \
                patch.object(profile, "build_assets", return_value=staged), \
                patch.object(profile.common, "roots", return_value=self.roots), \
                patch.object(profile.common, "xdg", return_value=self.base / "cache"), \
                patch.object(profile.common, "run", side_effect=command), \
                patch.object(profile, "widget_ready"), \
                patch.object(profile, "available_launchers", return_value=[]), \
                patch.object(profile, "activate", side_effect=fail):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaisesRegex(ValueError, "activation failed"):
                    profile.apply_profile(argparse.Namespace(install_packages=False, accent="#123456"), state)
        backup = next(state.iterdir())
        self.assertEqual(json.loads((backup / "manifest.json").read_text())["status"], "failed")
        profile.common.restore(self.roots, backup, profile.TARGETS)
        self.assertEqual(original.read_text(), "old appearance")


if __name__ == "__main__":
    unittest.main()
