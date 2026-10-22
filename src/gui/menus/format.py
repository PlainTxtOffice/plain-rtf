"""Build the Format menu for the desktop editor."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class FormatMenuActions:
    """Hold the callbacks invoked by the Format menu items.

    - Instances are immutable; command return values are ignored.
    - `set_font_family` takes a family name, or None for automatic.
    - All other fields are zero-argument commands.
    """

    toggle_bold: Callable[[], object]
    toggle_italic: Callable[[], object]
    toggle_underline: Callable[[], object]
    toggle_strikethrough: Callable[[], object]
    set_font_family: Callable[[str | None], object]
    set_font_size_auto: Callable[[], object]
    set_font_size_10: Callable[[], object]
    set_font_size_11: Callable[[], object]
    set_font_size_12: Callable[[], object]
    set_font_size_14: Callable[[], object]
    set_font_size_18: Callable[[], object]
    set_color_auto: Callable[[], object]
    set_color_black: Callable[[], object]
    set_color_red: Callable[[], object]
    set_color_green: Callable[[], object]
    set_color_blue: Callable[[], object]
    set_background_auto: Callable[[], object]
    set_background_yellow: Callable[[], object]
    set_background_green: Callable[[], object]
    set_background_blue: Callable[[], object]
    toggle_bullet_list: Callable[[], object]
    toggle_numbered_list: Callable[[], object]
    insert_table: Callable[[], object]
    insert_image: Callable[[], object]


def build_format_menu(
    parent_menu: tk.Menu,
    menu_actions: FormatMenuActions,
    font_families: tuple[str, ...],
) -> tk.Menu:
    """Create the Format menu as a child of the parent menu.

    - Returns the menu without attaching it; the caller adds the cascade.
    - The Font submenu lists "Automatic" first, which passes None, then one
      item per entry in `font_families`, in the given order.
    - Accelerator labels are display-only; key bindings are owned elsewhere.
    """
    format_menu = tk.Menu(parent_menu, tearoff=False)
    format_menu.add_command(
        label="Bold",
        accelerator="Ctrl+B",
        command=menu_actions.toggle_bold,
    )
    format_menu.add_command(
        label="Italic",
        accelerator="Ctrl+I",
        command=menu_actions.toggle_italic,
    )
    format_menu.add_command(
        label="Underline",
        accelerator="Ctrl+U",
        command=menu_actions.toggle_underline,
    )
    format_menu.add_command(
        label="Strikethrough",
        command=menu_actions.toggle_strikethrough,
    )

    font_menu = tk.Menu(format_menu, tearoff=False)
    font_menu.add_command(
        label="Automatic",
        command=lambda: menu_actions.set_font_family(None),
    )
    for font_family in font_families:
        font_menu.add_command(
            label=font_family,
            command=partial(menu_actions.set_font_family, font_family),
        )
    format_menu.add_cascade(label="Font", menu=font_menu)

    size_menu = tk.Menu(format_menu, tearoff=False)
    size_menu.add_command(
        label="Automatic",
        command=menu_actions.set_font_size_auto,
    )
    size_menu.add_command(label="10 pt", command=menu_actions.set_font_size_10)
    size_menu.add_command(label="11 pt", command=menu_actions.set_font_size_11)
    size_menu.add_command(label="12 pt", command=menu_actions.set_font_size_12)
    size_menu.add_command(label="14 pt", command=menu_actions.set_font_size_14)
    size_menu.add_command(label="18 pt", command=menu_actions.set_font_size_18)
    format_menu.add_cascade(label="Font Size", menu=size_menu)

    color_menu = tk.Menu(format_menu, tearoff=False)
    color_menu.add_command(
        label="Automatic",
        command=menu_actions.set_color_auto,
    )
    color_menu.add_command(
        label="Black",
        command=menu_actions.set_color_black,
    )
    color_menu.add_command(
        label="Red",
        command=menu_actions.set_color_red,
    )
    color_menu.add_command(
        label="Green",
        command=menu_actions.set_color_green,
    )
    color_menu.add_command(
        label="Blue",
        command=menu_actions.set_color_blue,
    )
    format_menu.add_separator()
    format_menu.add_cascade(label="Text Color", menu=color_menu)

    background_menu = tk.Menu(format_menu, tearoff=False)
    background_menu.add_command(
        label="Automatic",
        command=menu_actions.set_background_auto,
    )
    background_menu.add_command(
        label="Yellow",
        command=menu_actions.set_background_yellow,
    )
    background_menu.add_command(
        label="Green",
        command=menu_actions.set_background_green,
    )
    background_menu.add_command(
        label="Blue",
        command=menu_actions.set_background_blue,
    )
    format_menu.add_cascade(label="Background Color", menu=background_menu)

    format_menu.add_separator()
    format_menu.add_command(
        label="Bullet List",
        command=menu_actions.toggle_bullet_list,
    )
    format_menu.add_command(
        label="Numbered List",
        command=menu_actions.toggle_numbered_list,
    )
    format_menu.add_separator()
    format_menu.add_command(
        label="Insert Table",
        command=menu_actions.insert_table,
    )
    format_menu.add_command(
        label="Insert Image...",
        command=menu_actions.insert_image,
    )
    return format_menu
