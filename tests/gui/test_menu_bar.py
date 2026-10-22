"""Exercise menu-bar wiring for the desktop editor."""

from __future__ import annotations

import tkinter as tk
import unittest

from src.gui.menus.file import FileMenuActions
from src.gui.menus.format import FormatMenuActions
from src.gui.menus.help import HelpMenuActions
from src.gui.menus.menu import (
    MenuBarActions,
    build_menu_bar,
)


class MenuBarTests(unittest.TestCase):
    """Verify the top-level menu structure and callback wiring."""

    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.calls: list[str] = []

    def tearDown(self) -> None:
        self.root.destroy()

    def test_build_menu_bar_adds_help_menu_actions(self) -> None:
        build_menu_bar(self.root, self._build_actions())

        menu_bar = self.root.nametowidget(self.root["menu"])
        help_menu = self.root.nametowidget(menu_bar.entrycget(2, "menu"))

        help_labels = [
            help_menu.entrycget(index, "label")
            for index in (0, 1, 3)
        ]

        self.assertEqual(menu_bar.index("end"), 2)
        self.assertEqual(menu_bar.type(2), "cascade")
        self.assertEqual(
            help_labels,
            ["Keyboard Shortcuts", "RTF Support", "About RTF Editor"],
        )

        help_menu.invoke(0)
        help_menu.invoke(1)
        help_menu.invoke(3)

        self.assertEqual(
            self.calls,
            ["show_keyboard_shortcuts", "show_rtf_support", "show_about"],
        )

    def test_build_menu_bar_adds_insert_image_command(self) -> None:
        build_menu_bar(self.root, self._build_actions())

        menu_bar = self.root.nametowidget(self.root["menu"])
        format_menu = self.root.nametowidget(menu_bar.entrycget(1, "menu"))

        entry_indexes = {
            format_menu.entrycget(index, "label"): index
            for index in range(format_menu.index("end") + 1)
            if format_menu.type(index) != "separator"
        }

        self.assertIn("Insert Image...", entry_indexes)
        self.assertEqual(
            entry_indexes["Insert Image..."],
            entry_indexes["Insert Table"] + 1,
        )

        format_menu.invoke(entry_indexes["Insert Image..."])

        self.assertEqual(self.calls, ["insert_image"])

    def test_build_menu_bar_lists_font_families(self) -> None:
        build_menu_bar(self.root, self._build_actions())

        menu_bar = self.root.nametowidget(self.root["menu"])
        format_menu = self.root.nametowidget(menu_bar.entrycget(1, "menu"))
        font_menu = self.root.nametowidget(format_menu.entrycget(4, "menu"))

        self.assertEqual(
            [font_menu.entrycget(index, "label") for index in range(3)],
            ["Automatic", "Arial", "Courier New"],
        )

        font_menu.invoke(2)

        self.assertEqual(self.calls, ["set_font_family:Courier New"])

    def _build_actions(self) -> MenuBarActions:
        return MenuBarActions(
            file_menu=FileMenuActions(
                new_file=lambda: self._record("new_file"),
                open_file=lambda: self._record("open_file"),
                save_file=lambda: self._record("save_file"),
                save_file_as=lambda: self._record("save_file_as"),
                close_window=lambda: self._record("close_window"),
            ),
            format_menu=FormatMenuActions(
                toggle_bold=lambda: self._record("toggle_bold"),
                toggle_italic=lambda: self._record("toggle_italic"),
                toggle_underline=lambda: self._record("toggle_underline"),
                toggle_strikethrough=lambda: self._record(
                    "toggle_strikethrough"
                ),
                set_font_family=lambda family: self._record(
                    f"set_font_family:{family}"
                ),
                set_font_size_auto=lambda: self._record("set_font_size_auto"),
                set_font_size_10=lambda: self._record("set_font_size_10"),
                set_font_size_11=lambda: self._record("set_font_size_11"),
                set_font_size_12=lambda: self._record("set_font_size_12"),
                set_font_size_14=lambda: self._record("set_font_size_14"),
                set_font_size_18=lambda: self._record("set_font_size_18"),
                set_color_auto=lambda: self._record("set_color_auto"),
                set_color_black=lambda: self._record("set_color_black"),
                set_color_red=lambda: self._record("set_color_red"),
                set_color_green=lambda: self._record("set_color_green"),
                set_color_blue=lambda: self._record("set_color_blue"),
                set_background_auto=lambda: self._record(
                    "set_background_auto"
                ),
                set_background_yellow=lambda: self._record(
                    "set_background_yellow"
                ),
                set_background_green=lambda: self._record(
                    "set_background_green"
                ),
                set_background_blue=lambda: self._record(
                    "set_background_blue"
                ),
                toggle_bullet_list=lambda: self._record("toggle_bullet_list"),
                toggle_numbered_list=lambda: self._record(
                    "toggle_numbered_list"
                ),
                insert_table=lambda: self._record("insert_table"),
                insert_image=lambda: self._record("insert_image"),
            ),
            help_menu=HelpMenuActions(
                show_keyboard_shortcuts=lambda: self._record(
                    "show_keyboard_shortcuts"
                ),
                show_rtf_support=lambda: self._record("show_rtf_support"),
                show_about=lambda: self._record("show_about"),
            ),
            font_families=("Arial", "Courier New"),
        )

    def _record(self, action_name: str) -> None:
        self.calls.append(action_name)


if __name__ == "__main__":
    unittest.main()
