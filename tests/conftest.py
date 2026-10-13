"""Test configuration: make web/davinci_core.py importable and provide a
sandboxed temp workspace so file-tool tests never touch the real repo."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))

import davinci_core as core  # noqa: E402


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    """A throwaway workspace with the core module's globals pointed at it."""
    monkeypatch.setattr(core, "WORKSPACE", tmp_path)
    monkeypatch.setattr(core, "_WORKSPACE_RESOLVED", tmp_path.resolve())
    monkeypatch.setattr(core, "OUTPUT_DIR", tmp_path / "output")
    (tmp_path / "output").mkdir()
    (tmp_path / "sources").mkdir()
    return tmp_path


@pytest.fixture(autouse=True)
def clean_model_env(monkeypatch):
    """Model-selection tests start from a clean environment."""
    for var in ("ANTHROPIC_MODEL", "ANTHROPIC_MODEL_FAST", "ANTHROPIC_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
