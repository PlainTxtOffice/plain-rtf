"""Exercise the root window's file lifecycle safety behavior."""

from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from src.adapters.document import DocumentAdapter
from src.domains.documents.models import DocumentModel, TextSpan
from src.gui.views.root_window import RootWindow


class RootWindowLifecycleTests(unittest.TestCase):
    """Cover unsaved-changes prompts, undo state, and shortcuts."""

    def setUp(self) -> None:
        self.document_adapter = DocumentAdapter()
        self.window = RootWindow(document_adapter=self.document_adapter)
        self.window.withdraw()

    def tearDown(self) -> None:
        self.window.destroy()

    def test_cancelled_save_as_keeps_unsaved_document_open(self) -> None:
        self.window._mark_dirty()

        with (
            patch(
                "src.gui.views.root_window.messagebox.askyesnocancel",
                return_value=True,
            ),
            patch(
                "src.gui.views.root_window.filedialog.asksaveasfilename",
                return_value="",
            ),
        ):
            allowed_to_proceed = self.window._prompt_for_unsaved_changes()

        self.assertFalse(allowed_to_proceed)

    def test_failed_save_keeps_unsaved_document_open(self) -> None:
        self.window._mark_dirty()

        with (
            patch(
                "src.gui.views.root_window.messagebox.askyesnocancel",
                return_value=True,
            ),
            patch(
                "src.gui.views.root_window.filedialog.asksaveasfilename",
                return_value="save-target.rtf",
            ),
            patch(
                "src.adapters.document.DocumentAdapter.save_document",
                side_effect=OSError("disk full"),
            ),
            patch("src.gui.views.root_window.messagebox.showerror"),
        ):
            allowed_to_proceed = self.window._prompt_for_unsaved_changes()

        self.assertFalse(allowed_to_proceed)

    def test_loading_document_clears_undo_history(self) -> None:
        self.window._load_document(
            DocumentModel(spans=(TextSpan(text="first document"),)),
        )
        self.window.text.insert("end", "user typed text")
        self.window._load_document(
            DocumentModel(spans=(TextSpan(text="second document"),)),
        )

        with self.assertRaises(tk.TclError):
            self.window.text.edit_undo()

    def _focus_text_in_mapped_window(self) -> None:
        self.window.deiconify()
        self.window.text.focus_force()
        self.window.update()

    def test_text_widget_suppresses_control_o_insertion(self) -> None:
        self.window.text.insert("1.0", "abc")
        self._focus_text_in_mapped_window()

        with (
            patch(
                "src.gui.views.root_window.messagebox.askyesnocancel",
                return_value=False,
            ),
            patch(
                "src.gui.views.root_window.filedialog.askopenfilename",
                return_value="",
            ),
        ):
            self.window.text.event_generate("<Control-o>")
            self.window.update()

        self.assertEqual(self.window.text.get("1.0", "end-1c"), "abc")

    def test_text_widget_suppresses_control_i_tab_insertion(self) -> None:
        self.window.text.insert("1.0", "abc")
        self.window.text.tag_add("sel", "1.0", "1.3")
        self._focus_text_in_mapped_window()

        self.window.text.event_generate("<Control-i>")
        self.window.update()

        self.assertEqual(self.window.text.get("1.0", "end-1c"), "abc")

    def test_handle_drop_inserts_image_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "dropped.png"
            buffer = BytesIO()
            Image.new("RGB", (2, 2), (0, 0, 255)).save(buffer, format="PNG")
            image_path.write_bytes(buffer.getvalue())

            # tkdnd delivers paths as a Tcl list; brace-quote the path so
            # splitlist preserves Windows backslashes, as tkdnd itself does.
            event = SimpleNamespace(data="{" + str(image_path) + "}")
            self.window._handle_drop(event)

        self.assertEqual(len(self.window.text.image_names()), 1)


if __name__ == "__main__":
    unittest.main()
