"""Exercise document image normalization without a GUI."""

from __future__ import annotations

import unittest
from io import BytesIO

from PIL import Image

from src.domains.documents.images import decode_image, replace_image_offset


def make_image_bytes(
    image_format: str = "PNG",
    size: tuple[int, int] = (4, 2),
) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, (255, 0, 0)).save(buffer, format=image_format)
    return buffer.getvalue()


class DocumentImageTests(unittest.TestCase):
    """Preserve encoded image content and document positions."""

    def test_decode_png_keeps_original_bytes(self) -> None:
        png_bytes = make_image_bytes("PNG")
        image_ref = decode_image(png_bytes)
        self.assertEqual(image_ref.image_bytes, png_bytes)
        self.assertEqual(image_ref.image_format, "png")
        self.assertEqual(image_ref.width_px, 4)
        self.assertEqual(image_ref.height_px, 2)
        self.assertEqual(image_ref.display_width_px, 4)

    def test_decode_jpeg_keeps_original_bytes(self) -> None:
        jpeg_bytes = make_image_bytes("JPEG")
        image_ref = decode_image(jpeg_bytes)
        self.assertEqual(image_ref.image_bytes, jpeg_bytes)
        self.assertEqual(image_ref.image_format, "jpeg")

    def test_decode_bmp_converts_to_png(self) -> None:
        bmp_bytes = make_image_bytes("BMP")
        image_ref = decode_image(bmp_bytes)
        self.assertEqual(image_ref.image_format, "png")
        self.assertEqual(image_ref.width_px, 4)
        with Image.open(BytesIO(image_ref.image_bytes)) as converted:
            self.assertEqual(converted.format, "PNG")

    def test_decode_garbage_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            decode_image(b"not an image at all")

    def test_offset_replacement_preserves_image(self) -> None:
        original = decode_image(make_image_bytes())
        moved = replace_image_offset(original, 7)
        self.assertEqual(original.offset, 0)
        self.assertEqual(moved.offset, 7)
        self.assertEqual(replace_image_offset(moved, 0), original)
