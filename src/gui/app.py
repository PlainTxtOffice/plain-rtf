"""Create and run the desktop editor application."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

from src.adapters.document import DocumentAdapter
from src.config.logging import configure_logging
from src.config.path_handler import ROOT_DIR, STORAGE_MODE
from src.gui.views.root_window import RootWindow

if TYPE_CHECKING:
    from pathlib import Path


def _show_storage_error(error: OSError) -> None:
    """Explain a startup storage failure in a dialog and close its window."""
    parent = tk.Tk()
    parent.withdraw()
    advice = (
        "Move the portable executable to a writable folder and try again. "
        "Portable data will not be redirected to AppData."
        if STORAGE_MODE == "portable"
        else "Check that your account can write to this folder and try again."
    )
    try:
        messagebox.showerror(
            title="Cannot write application data",
            message=f"Cannot write to {ROOT_DIR}.\n\n{advice}\n\n{error}",
            parent=parent,
        )
    finally:
        parent.destroy()


def launch_app(startup_path: Path | None = None) -> None:
    """Launch the desktop editor and block until its window closes.

    - Configures application logging before any window is created.
    - Shows a dialog and stops if application storage cannot be written.
    - Opens `startup_path` in the new window when one is supplied.
    - Runs the Tk event loop on the calling thread.
    """
    try:
        configure_logging("rtf-editor")
    except (OSError, ValueError) as error:
        storage_error = error if isinstance(error, OSError) else error.__cause__
        if not isinstance(storage_error, OSError):
            raise
        _show_storage_error(storage_error)
        return
    document_adapter = DocumentAdapter()
    root_window = RootWindow(
        document_adapter=document_adapter,
        startup_path=startup_path,
    )
    root_window.run()
