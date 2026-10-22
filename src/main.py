"""Launch the desktop editor application."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from src.gui.app import launch_app

if TYPE_CHECKING:
    from collections.abc import Sequence


def _get_startup_path(argv: Sequence[str]) -> Path | None:
    """Return the first startup file path, if one was provided.

    Extra arguments are ignored.
    """
    if not argv:
        return None

    return Path(argv[0])


def main(argv: Sequence[str] | None = None) -> None:
    """Launch the desktop application.

    Reads ``sys.argv`` when ``argv`` is None.
    """
    startup_args = sys.argv[1:] if argv is None else argv
    launch_app(_get_startup_path(startup_args))


if __name__ == "__main__":
    main()
