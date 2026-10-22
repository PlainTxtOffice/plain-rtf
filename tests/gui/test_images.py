"""Exercise image embedding helpers for the editor widget."""

from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from src.domains.documents.images import decode_image, replace_image_offset
from src.domains.documents.models import (
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    ImageRef,
    TextSpan,
)
from src.gui.views.images import (
    init_image_registry,
    insert_image_at,
    insert_image_bytes_at_cursor,
    look_clipboard_image_bytes,
    look_image_ref,
)
from src.gui.views.text_buffer import (
    count_document_characters,
    create_style_tags,
    load_document_into_text,
    read_document_from_text,
)


def make_image_bytes(
    image_format: str = "PNG",
    size: tuple[int, int] = (4, 2),
) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, (255, 0, 0)).save(buffer, format=image_format)
    return buffer.getvalue()


class ImageHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.text = tk.Text(self.root)
        self.text.pack()
        init_image_registry(self.text)

    def tearDown(self) -> None:
        self.root.destroy()

    def test_insert_image_at_registers_widget_image(self) -> None:
        image_ref = decode_image(make_image_bytes())
        self.text.insert("1.0", "ab")
        image_name = insert_image_at(self.text, "1.1", image_ref)
        self.assertEqual(look_image_ref(self.text, image_name), image_ref)
        self.assertEqual(len(self.text.image_names()), 1)

    def test_insert_image_bytes_at_cursor(self) -> None:
        inserted = insert_image_bytes_at_cursor(
            self.text,
            make_image_bytes(),
        )
        self.assertTrue(inserted)
        self.assertEqual(len(self.text.image_names()), 1)

    def test_insert_invalid_bytes_returns_false(self) -> None:
        inserted = insert_image_bytes_at_cursor(self.text, b"junk")
        self.assertFalse(inserted)
        self.assertEqual(len(self.text.image_names()), 0)

    def test_oversized_image_is_scaled_to_fit(self) -> None:
        wide_bytes = make_image_bytes("PNG", size=(5000, 100))
        image_ref = decode_image(wide_bytes)
        image_name = insert_image_at(self.text, "1.0", image_ref)
        # Display is scaled down, but the stored ImageRef keeps the
        # original dimensions for lossless save.
        stored = look_image_ref(self.text, image_name)
        self.assertIsNotNone(stored)
        assert stored is not None
        self.assertEqual(stored.width_px, 5000)


class ImageRoundTripTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.text = tk.Text(self.root)
        self.text.pack()
        create_style_tags(self.text)

    def tearDown(self) -> None:
        self.root.destroy()

    def _document_with_image(self) -> DocumentModel:
        image_ref = decode_image(make_image_bytes())
        return DocumentModel(
            spans=(TextSpan(text=f"ab{OBJECT_REPLACEMENT_CHAR}cd"),),
            images=(replace_image_offset(image_ref, 2),),
        )

    def test_load_renders_image_not_placeholder_char(self) -> None:
        load_document_into_text(self.text, self._document_with_image())
        self.assertEqual(self.text.get("1.0", "end-1c"), "abcd")
        self.assertEqual(len(self.text.image_names()), 1)

    def test_round_trip_document_with_image(self) -> None:
        document = self._document_with_image()
        load_document_into_text(self.text, document)
        result = read_document_from_text(self.text)
        self.assertEqual(result.plain_text, document.plain_text)
        self.assertEqual(len(result.images), 1)
        self.assertEqual(result.images[0], document.images[0])

    def test_count_document_characters_includes_images(self) -> None:
        load_document_into_text(self.text, self._document_with_image())
        self.assertEqual(count_document_characters(self.text), 5)

    def test_corrupt_image_bytes_dropped_on_load(self) -> None:
        document = DocumentModel(
            spans=(TextSpan(text=f"a{OBJECT_REPLACEMENT_CHAR}b"),),
            images=(
                ImageRef(
                    offset=1,
                    image_bytes=b"\xde\xad\xbe\xef",
                    image_format="png",
                    width_px=1,
                    height_px=1,
                    display_width_px=1,
                    display_height_px=1,
                ),
            ),
        )
        load_document_into_text(self.text, document)
        self.assertEqual(self.text.get("1.0", "end-1c"), "ab")
        self.assertEqual(len(self.text.image_names()), 0)
        result = read_document_from_text(self.text)
        self.assertEqual(result.plain_text, "ab")
        self.assertEqual(result.images, ())

    def test_image_only_document_reads_back(self) -> None:
        image_ref = decode_image(make_image_bytes())
        document = DocumentModel(
            spans=(TextSpan(text=OBJECT_REPLACEMENT_CHAR),),
            images=(replace_image_offset(image_ref, 0),),
        )
        load_document_into_text(self.text, document)
        result = read_document_from_text(self.text)
        self.assertEqual(len(result.images), 1)
        self.assertEqual(result.plain_text, OBJECT_REPLACEMENT_CHAR)


class ClipboardImageTests(unittest.TestCase):
    def test_pil_image_content_encodes_to_png(self) -> None:
        image = Image.new("RGB", (2, 2), (0, 255, 0))
        image_bytes = look_clipboard_image_bytes(image)
        self.assertIsNotNone(image_bytes)
        assert image_bytes is not None
        with Image.open(BytesIO(image_bytes)) as decoded:
            self.assertEqual(decoded.format, "PNG")

    def test_file_list_content_reads_image_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "clip.png"
            image_path.write_bytes(make_image_bytes())
            image_bytes = look_clipboard_image_bytes([str(image_path)])
        self.assertEqual(image_bytes, make_image_bytes())

    def test_none_and_text_content_return_none(self) -> None:
        self.assertIsNone(look_clipboard_image_bytes(None))
        self.assertIsNone(look_clipboard_image_bytes("plain text"))
        self.assertIsNone(look_clipboard_image_bytes(["/missing/file.png"]))
