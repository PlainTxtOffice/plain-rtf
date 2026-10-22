"""Build the File menu for the desktop editor."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class FileMenuActions:
    """Hold the callbacks invoked by the File menu items.

    - Instances are immutable; each field is a zero-argument command.
    - Command return values are ignored by the menu.
    """

    new_file: Callable[[], object]
    open_file: Callable[[], object]
    save_file: Callable[[], object]
    save_file_as: Callable[[], object]
    close_window: Callable[[], object]


def build_file_menu(
    parent_menu: tk.Menu,
    menu_actions: FileMenuActions,
) -> tk.Menu:
    """Create the File menu as a child of the parent menu.

    - Returns the menu without attaching it; the caller adds the cascade.
    - Accelerator labels are display-only; key bindings are owned elsewhere.
    """
    file_menu = tk.Menu(parent_menu, tearoff=False)
    file_menu.add_command(
        label="New",
        accelerator="Ctrl+N",
        command=menu_actions.new_file,
    )
    file_menu.add_command(
        label="Open...",
        accelerator="Ctrl+O",
        command=menu_actions.open_file,
    )
    file_menu.add_command(
        label="Save",
        accelerator="Ctrl+S",
        command=menu_actions.save_file,
    )
    file_menu.add_command(
        label="Save As...",
        accelerator="Ctrl+Shift+S",
        command=menu_actions.save_file_as,
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=menu_actions.close_window)
    return file_menu
