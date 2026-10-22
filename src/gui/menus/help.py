"""Build the Help menu and related dialogs for the desktop editor."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

KEYBOARD_SHORTCUTS_TEXT = (
    "Ctrl+N  New document\n"
    "Ctrl+O  Open document\n"
    "Ctrl+S  Save document\n"
    "Ctrl+Shift+S  Save document as\n"
    "Ctrl+B  Bold\n"
    "Ctrl+I  Italic\n"
    "Ctrl+U  Underline"
)

RTF_SUPPORT_TEXT = (
    "RTF Editor stores Plain Text RTF documents, not Microsoft RTF.\n\n"
    "Supported: plain text, font families and sizes, text and background "
    "colors, basic inline formatting, lists, tables, and embedded PNG and "
    "JPEG images.\n\n"
    "Files are UTF-8 text and begin with PTRTF/1."
)

ABOUT_TEXT = (
    "RTF Editor\n\n"
    "Tiny desktop editor for quick rich-text notes on Windows.\n\n"
    "Use it for lightweight RTF editing with practical formatting support."
)


@dataclass(frozen=True, slots=True)
class HelpMenuActions:
    """Hold the callbacks invoked by the Help menu items.

    - Instances are immutable; each field is a zero-argument command.
    - Command return values are ignored by the menu.
    """

    show_keyboard_shortcuts: Callable[[], object]
    show_rtf_support: Callable[[], object]
    show_about: Callable[[], object]


def build_help_menu(
    parent_menu: tk.Menu,
    menu_actions: HelpMenuActions,
) -> tk.Menu:
    """Create the Help menu as a child of the parent menu.

    Returns the menu without attaching it; the caller adds the cascade.
    """
    help_menu = tk.Menu(parent_menu, tearoff=False)
    help_menu.add_command(
        label="Keyboard Shortcuts",
        command=menu_actions.show_keyboard_shortcuts,
    )
    help_menu.add_command(
        label="RTF Support",
        command=menu_actions.show_rtf_support,
    )
    help_menu.add_separator()
    help_menu.add_command(
        label="About RTF Editor",
        command=menu_actions.show_about,
    )
    return help_menu


def show_keyboard_shortcuts(parent: tk.Misc) -> None:
    """Show the editor's keyboard shortcuts in a modal info dialog.

    Blocks until the user dismisses the dialog owned by `parent`.
    """
    messagebox.showinfo(
        title="Keyboard Shortcuts",
        message=KEYBOARD_SHORTCUTS_TEXT,
        parent=parent,
    )


def show_rtf_support(parent: tk.Misc) -> None:
    """Show the supported Plain Text RTF features in a modal info dialog.

    Blocks until the user dismisses the dialog owned by `parent`.
    """
    messagebox.showinfo(
        title="RTF Support",
        message=RTF_SUPPORT_TEXT,
        parent=parent,
    )


def show_about(parent: tk.Misc) -> None:
    """Show the application summary in a modal info dialog.

    Blocks until the user dismisses the dialog owned by `parent`.
    """
    messagebox.showinfo(
        title="About RTF Editor",
        message=ABOUT_TEXT,
        parent=parent,
    )
