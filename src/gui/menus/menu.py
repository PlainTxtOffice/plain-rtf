"""Build the desktop editor menu bar."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

from src.gui.menus.file import FileMenuActions, build_file_menu
from src.gui.menus.format import (
    FormatMenuActions,
    build_format_menu,
)
from src.gui.menus.help import (
    HelpMenuActions,
    build_help_menu,
)


@dataclass(frozen=True, slots=True)
class MenuBarActions:
    """Hold the per-menu callbacks and data needed to build the menu bar.

    - Instances are immutable.
    - `font_families` populates the Format menu's Font submenu in order.
    """

    file_menu: FileMenuActions
    format_menu: FormatMenuActions
    help_menu: HelpMenuActions
    font_families: tuple[str, ...]


def build_menu_bar(
    root_window: tk.Tk,
    menu_actions: MenuBarActions,
) -> None:
    """Create the menu bar and attach it to the root window.

    - Adds the File, Format, and Help cascades in that order.
    - Mutates `root_window` by replacing its configured menu.
    """
    menu_bar = tk.Menu(root_window, tearoff=False)
    menu_bar.add_cascade(
        label="File",
        menu=build_file_menu(menu_bar, menu_actions.file_menu),
    )
    menu_bar.add_cascade(
        label="Format",
        menu=build_format_menu(
            menu_bar,
            menu_actions.format_menu,
            menu_actions.font_families,
        ),
    )
    menu_bar.add_cascade(
        label="Help",
        menu=build_help_menu(menu_bar, menu_actions.help_menu),
    )
    root_window.configure(menu=menu_bar)
