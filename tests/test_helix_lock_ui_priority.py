"""Static UI priority tests that do not need a graphical display."""
import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "helix_lock_app.py"


def test_app_source_compiles_without_display():
    compile(APP.read_text(encoding="utf-8"), str(APP), "exec")


def test_primary_tab_precedes_settings_info_and_optional_modules():
    source = APP.read_text(encoding="utf-8")
    start = source.index("    def _build(self):")
    end = source.index("    def _logo(", start)
    body = source[start:end]
    labels = ["self.tabs.add(self.file_tab", "self.tabs.add(self.settings_tab",
              "self.tabs.add(self.info_tab", "self.tabs.add(self.dashboard_tab",
              "self.tabs.add(self.fp_tab", "self.tabs.add(self.trust_tab"]
    offsets = [body.index(label) for label in labels]
    assert offsets == sorted(offsets)
    assert "self.tabs.select(self.file_tab)" in body


def test_main_workflow_keeps_key_and_actions():
    source = APP.read_text(encoding="utf-8")
    start = source.index("    def _build_files(self):")
    end = source.index("    def _build_settings(self):", start)
    body = source[start:end]
    assert "self._pick_source" in body
    assert "self._pick_key" in body
    assert "self._generate_key" in body
    assert "self._encrypt" in body
    assert "self._decrypt" in body


def test_settings_share_existing_key_mode():
    source = APP.read_text(encoding="utf-8")
    start = source.index("    def _build_settings(self):")
    end = source.index("    def _build_information(self):", start)
    body = source[start:end]
    assert body.count("variable=self.mode") == 2
    assert body.count("command=self._refresh_mode") == 2
