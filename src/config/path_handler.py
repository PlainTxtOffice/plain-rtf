"""Define base path constants for development and packaged builds.

- Development builds resolve every root to the repository root.
- Portable builds keep writable files in one folder beside the executable.
- Installed builds use per-user storage; assets always come from the bundle.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

IS_COMPILED = bool(
    globals().get("__compiled__", False) or getattr(sys, "frozen", False),
)
DEV_ROOT = Path(__file__).resolve().parents[2]
APP_DATA_DIR_NAME = "plain-rtf"


def _look_compiled_containing_dir() -> Path:
    """Return the directory that contains the compiled executable.

    - Prefers the containing directory that the Nuitka ``__compiled__``
      metadata reports.
    - Falls back to the directory of the entry point script.
    """
    compiled_info = globals().get("__compiled__")
    containing_dir = getattr(compiled_info, "containing_dir", None)
    if containing_dir:
        return Path(containing_dir).resolve()
    return Path(sys.argv[0]).resolve().parent


_BUNDLE_ROOT_PARENT_INDEX = 2


def _look_bundle_root() -> Path:
    """Return the root directory that hosts bundled application assets.

    - Uses the directory two levels above this module inside the bundle.
    - Falls back to the executable's directory when the module path is too
      shallow to have that ancestor.
    """
    module_path = Path(__file__).resolve()
    if len(module_path.parents) > _BUNDLE_ROOT_PARENT_INDEX:
        return module_path.parents[_BUNDLE_ROOT_PARENT_INDEX]
    return _look_compiled_containing_dir()


def _look_runtime_storage() -> tuple[str, Path, Path | None]:
    """Select the storage mode, writable root, and optional per-user root.

    - Keeps portable storage beside the executable without an AppData fallback.
    - Returns values so each exported constant is assigned only once.
    """
    if not IS_COMPILED:
        return "development", DEV_ROOT, None
    if (BUNDLE_ROOT / "portable.marker").is_file():
        portable_root = APP_ROOT / f"{Path(sys.argv[0]).stem}-data"
        return "portable", portable_root, None
    local_app_data = os.environ.get("LOCALAPPDATA")
    user_root = (
        Path(local_app_data)
        if local_app_data
        else Path.home() / "AppData/Local"
    )
    user_data_dir = user_root / APP_DATA_DIR_NAME
    return "installed", user_data_dir, user_data_dir


APP_ROOT = _look_compiled_containing_dir() if IS_COMPILED else DEV_ROOT
BUNDLE_ROOT = _look_bundle_root() if IS_COMPILED else DEV_ROOT
STORAGE_MODE, ROOT_DIR, USER_DATA_DIR = _look_runtime_storage()

ASSETS_DIR = BUNDLE_ROOT / "assets"
LOGS_DIR = ROOT_DIR / "logs"
EXPORTS_DIR = ROOT_DIR / "exports"
BACKUPS_DIR = EXPORTS_DIR / "backups"
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
