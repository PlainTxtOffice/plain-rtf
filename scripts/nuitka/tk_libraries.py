"""Expose Tcl/Tk runtime libraries to Nuitka, including Python 3.14 zipfs."""

# ruff: noqa: INP001
from __future__ import annotations

import json
import sys
import tempfile
import tkinter as tk
from pathlib import Path


def prepare_libraries(input_dir: Path) -> dict[str, str]:
    """Locate Tcl/Tk or copy embedded libraries into fresh build inputs.

    Uses the selected interpreter's libraries. Embedded zipfs content is
    copied by Tcl itself because Python filesystem APIs cannot read it.
    Build inputs are retained alongside Nuitka's other intermediates.
    """
    root = tk.Tk()
    root.withdraw()
    try:
        sources = {
            "tcl": str(root.tk.call("info", "library")),
            "tk": str(root.tk.call("set", "tk_library")),
        }
        if not any("zipfs:" in value for value in sources.values()):
            return sources
        input_dir.mkdir(parents=True, exist_ok=True)
        snapshot = Path(tempfile.mkdtemp(prefix="tk-", dir=input_dir))
        libraries = {}
        for name, source in sources.items():
            target = snapshot / name
            root.tk.call("file", "copy", "--", source, str(target))
            libraries[name] = str(target)
        # Nuitka's Windows tk-inter plugin also enumerates a tcl8 sibling.
        # Tcl 9's embedded distribution has no such directory.
        (snapshot / "tcl8").mkdir()
        return libraries
    finally:
        root.destroy()


if __name__ == "__main__":
    sys.stdout.write(json.dumps(prepare_libraries(Path(sys.argv[1]))))
