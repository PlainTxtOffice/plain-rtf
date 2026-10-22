"""Normalize embedded images and update their document positions.

Owns byte conversion and image references without filesystem or widget I/O.
"""

from __future__ import annotations

from dataclasses import replace
from io import BytesIO
from typing import Literal

from PIL import Image

from src.domains.documents.models import ImageRef

PASSTHROUGH_FORMATS: dict[str, Literal["png", "jpeg"]] = {
    "PNG": "png",
    "JPEG": "jpeg",
}


def decode_image(image_bytes: bytes) -> ImageRef:
    """Decode image bytes, converting unsupported formats to PNG.

    - Accepts any format Pillow can read.
    - PNG and JPEG bytes pass through unchanged; other formats are
      re-encoded as PNG, converting uncommon modes to RGBA first.
    - The returned entry has offset 0 and a display size equal to the
      natural pixel size.
    - Raises ValueError when Pillow cannot read the bytes as an image.
    """
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
            source_format = (image.format or "").upper()
            width_px, height_px = image.size
            if source_format in PASSTHROUGH_FORMATS:
                image_format: Literal["png", "jpeg"] = PASSTHROUGH_FORMATS[
                    source_format
                ]
                encoded_bytes = image_bytes
            else:
                buffer = BytesIO()
                converted = (
                    image
                    if image.mode in {"1", "L", "LA", "P", "RGB", "RGBA"}
                    else image.convert("RGBA")
                )
                converted.save(buffer, format="PNG")
                image_format = "png"
                encoded_bytes = buffer.getvalue()
    except OSError as error:
        msg = "The selected data is not a supported image."
        raise ValueError(msg) from error

    return ImageRef(
        offset=0,
        image_bytes=encoded_bytes,
        image_format=image_format,
        width_px=width_px,
        height_px=height_px,
        display_width_px=width_px,
        display_height_px=height_px,
    )


def replace_image_offset(image_ref: ImageRef, offset: int) -> ImageRef:
    """Return a copy of an image entry anchored at a new offset.

    The original entry is not mutated.
    """
    return replace(image_ref, offset=offset)
