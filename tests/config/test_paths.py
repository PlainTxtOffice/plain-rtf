"""Verify storage never follows the working directory or onefile payload."""

import importlib.util
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "src/config/path_handler.py"


def load_paths(tmp_path, monkeypatch, *, compiled=True, portable=False):
    bundle = tmp_path / "unpacked bundle"
    module_path = bundle / "src/config/path_handler.py"
    module_path.parent.mkdir(parents=True)
    module_path.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    if portable:
        (bundle / "portable.marker").touch()
    executable_dir = tmp_path / "USB drive"
    if compiled:
        monkeypatch.setattr(sys, "argv", [str(executable_dir / "plain-rtf.exe")])
    user_dir = tmp_path / "User AppData"
    monkeypatch.setenv("LOCALAPPDATA", str(user_dir))
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location("test_runtime_paths", module_path)
    module = importlib.util.module_from_spec(spec)
    if compiled:
        module.__compiled__ = SimpleNamespace(containing_dir=executable_dir)
    spec.loader.exec_module(module)
    return vars(module), bundle, executable_dir, user_dir


def test_portable_uses_executable_folder(tmp_path, monkeypatch):
    paths, bundle, executable_dir, user_dir = load_paths(tmp_path, monkeypatch, portable=True)
    assert paths["STORAGE_MODE"] == "portable"
    assert paths["ROOT_DIR"] == executable_dir / "plain-rtf-data"
    assert paths["ASSETS_DIR"] == bundle / "assets"
    assert paths["LOGS_DIR"] == executable_dir / "plain-rtf-data/logs"
    assert paths["USER_DATA_DIR"] is None
    assert not executable_dir.exists()
    assert not user_dir.exists()


def test_installed_uses_user_storage(tmp_path, monkeypatch):
    paths, bundle, executable_dir, user_dir = load_paths(tmp_path, monkeypatch)
    assert paths["STORAGE_MODE"] == "installed"
    assert paths["ROOT_DIR"] == user_dir / "plain-rtf"
    assert paths["USER_DATA_DIR"] == paths["ROOT_DIR"]
    assert paths["ASSETS_DIR"] == bundle / "assets"
    assert not executable_dir.exists()
    assert not user_dir.exists()


def test_development_ignores_portable_marker(tmp_path, monkeypatch):
    paths, bundle, _, user_dir = load_paths(tmp_path, monkeypatch, compiled=False, portable=True)
    assert paths["STORAGE_MODE"] == "development"
    assert paths["ROOT_DIR"] == bundle
    assert paths["LOGS_DIR"] == bundle / "logs"
    assert not user_dir.exists()


def test_frozen_fallback_uses_argv(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "argv", [str(tmp_path / "program/plain-rtf.exe")])
    paths, _, _, _ = load_paths(tmp_path, monkeypatch, compiled=False, portable=True)
    assert paths["ROOT_DIR"] == tmp_path / "program/plain-rtf-data"


def test_renamed_portable_uses_matching_data_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "argv", [str(tmp_path / "program/My Notes.exe")])
    paths, _, _, _ = load_paths(tmp_path, monkeypatch, compiled=False, portable=True)
    assert paths["ROOT_DIR"] == tmp_path / "program/My Notes-data"


def test_storage_name_matches_metadata():
    from src.config.path_handler import APP_DATA_DIR_NAME

    metadata = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert APP_DATA_DIR_NAME == metadata["tool"]["plain-rtf"]["app-data-dir"]
