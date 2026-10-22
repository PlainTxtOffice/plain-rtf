"""Exercise text buffer mapping between models and Tk Text widgets."""

from __future__ import annotations

import tkinter as tk
import unittest

from src.domains.documents.models import (
    DocumentModel,
    TextSpan,
    TextStyle,
)
from src.gui.views.text_buffer import (
    apply_selection_font_family,
    create_style_tags,
    handle_return_in_list,
    load_document_into_text,
    read_document_from_text,
)


class TextBufferTests(unittest.TestCase):
    """Round-trip and style behavior for the editor Text widget."""

    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.text = tk.Text(self.root)
        self.text.pack()
        create_style_tags(self.text)

    def tearDown(self) -> None:
        self.root.destroy()

    def test_round_trip_plain_document(self) -> None:
        document = DocumentModel(
            spans=(TextSpan(text="hello world"),),
        )
        load_document_into_text(self.text, document)
        self.assertEqual(read_document_from_text(self.text), document)

    def test_round_trip_mixed_styles(self) -> None:
        document = DocumentModel(
            spans=(
                TextSpan(text="plain "),
                TextSpan(text="bold", style=TextStyle(bold=True)),
                TextSpan(text=" "),
                TextSpan(
                    text="big",
                    style=TextStyle(font_family="Times New Roman", font_size=18),
                ),
                TextSpan(text=" "),
                TextSpan(
                    text="red",
                    style=TextStyle(foreground_color="#ff0000"),
                ),
                TextSpan(text=" "),
                TextSpan(
                    text="highlight",
                    style=TextStyle(background_color="#fff59d"),
                ),
                TextSpan(text=" "),
                TextSpan(
                    text="strike",
                    style=TextStyle(strikethrough=True),
                ),
            ),
        )
        load_document_into_text(self.text, document)
        self.assertEqual(read_document_from_text(self.text), document)

    def test_apply_selection_font_family_preserves_other_style_fields(self) -> None:
        self.text.insert("1.0", "formatted")
        self.text.tag_add("sel", "1.0", "1.9")

        changed = apply_selection_font_family(self.text, "Courier New")

        self.assertTrue(changed)
        self.assertEqual(
            read_document_from_text(self.text),
            DocumentModel(
                spans=(
                    TextSpan(
                        text="formatted",
                        style=TextStyle(font_family="Courier New"),
                    ),
                ),
            ),
        )

    def test_invalid_hex_color_falls_back_to_default_style_tag(self) -> None:
        document = DocumentModel(
            spans=(
                TextSpan(
                    text="x",
                    style=TextStyle(
                        foreground_color="not-a-hex-color",
                        background_color="also-not-a-hex-color",
                    ),
                ),
            ),
        )
        load_document_into_text(self.text, document)
        out = read_document_from_text(self.text)
        self.assertEqual(
            out,
            DocumentModel(spans=(TextSpan(text="x"),)),
        )

class ReturnInListTests(unittest.TestCase):
    """Enter-key continuation of bulleted and numbered lists."""

    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.text = tk.Text(self.root)
        self.text.pack()

    def tearDown(self) -> None:
        self.root.destroy()

    def _content(self) -> str:
        return self.text.get("1.0", "end-1c")

    def test_enter_continues_bullet_list(self) -> None:
        self.text.insert("1.0", "• first")
        self.text.mark_set("insert", "end-1c")
        result = handle_return_in_list(self.text)
        self.assertEqual(result, "break")
        self.assertEqual(self._content(), "• first\n• ")

    def test_enter_continues_numbered_list_and_increments(self) -> None:
        self.text.insert("1.0", "1. first")
        self.text.mark_set("insert", "end-1c")
        result = handle_return_in_list(self.text)
        self.assertEqual(result, "break")
        self.assertEqual(self._content(), "1. first\n2. ")

    def test_numbered_list_preserves_separator(self) -> None:
        self.text.insert("1.0", "3) item")
        self.text.mark_set("insert", "end-1c")
        handle_return_in_list(self.text)
        self.assertEqual(self._content(), "3) item\n4) ")

    def test_enter_on_empty_bullet_strips_marker(self) -> None:
        self.text.insert("1.0", "• ")
        self.text.mark_set("insert", "end-1c")
        result = handle_return_in_list(self.text)
        self.assertEqual(result, "break")
        self.assertEqual(self._content(), "")

    def test_enter_on_empty_numbered_strips_marker(self) -> None:
        self.text.insert("1.0", "2. ")
        self.text.mark_set("insert", "end-1c")
        result = handle_return_in_list(self.text)
        self.assertEqual(result, "break")
        self.assertEqual(self._content(), "")

    def test_enter_outside_list_falls_through(self) -> None:
        self.text.insert("1.0", "plain paragraph")
        self.text.mark_set("insert", "end-1c")
        result = handle_return_in_list(self.text)
        self.assertIsNone(result)
        self.assertEqual(self._content(), "plain paragraph")

    def test_enter_before_bullet_prefix_falls_through(self) -> None:
        self.text.insert("1.0", "• item")
        self.text.mark_set("insert", "1.0")
        result = handle_return_in_list(self.text)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
