"""Embed raster images in the editor text widget.

- Keeps per-widget registries keyed by Tk image name, holding weak
  references to each widget so registries vanish with the widget.
- The photo registry keeps Tk images alive; Tk drops an embedded image
  whose PhotoImage is garbage-collected.
- The ImageRef registry preserves the original encoded bytes, so reading
  a document back never uses the scaled display copy.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from PIL import Image, ImageTk

from src.domains.documents.images import decode_image

if TYPE_CHECKING:
    from tkinter import Text

    from src.domains.documents.models import ImageRef

FALLBACK_MAX_WIDTH_PX = 760
EDITOR_HORIZONTAL_PADDING_PX = 32
PHOTOS_BY_WIDGET: WeakKeyDictionary[
    Text,
    dict[str, ImageTk.PhotoImage],
] = WeakKeyDictionary()
IMAGE_REFS_BY_WIDGET: WeakKeyDictionary[
    Text,
    dict[str, ImageRef],
] = WeakKeyDictionary()


def init_image_registry(text_widget: Text) -> None:
    """Create empty image registries for a widget.

    - Replaces any registries already present for the widget.
    - Must run before `insert_image_at` or `clear_images` is used on the
      widget; those raise KeyError for an unregistered widget.
    """
    PHOTOS_BY_WIDGET[text_widget] = {}
    IMAGE_REFS_BY_WIDGET[text_widget] = {}


def clear_images(text_widget: Text) -> None:
    """Forget all registered images for a widget.

    - Does not delete embedded images from the widget's text; callers clear
      the text separately.
    - Raises KeyError when the widget has no registries.
    """
    PHOTOS_BY_WIDGET[text_widget].clear()
    IMAGE_REFS_BY_WIDGET[text_widget].clear()


def look_image_ref(text_widget: Text, image_name: str) -> ImageRef | None:
    """Return the image data registered under a Tk image name.

    Returns None when the name or the widget is not registered.
    """
    return IMAGE_REFS_BY_WIDGET.get(text_widget, {}).get(image_name)


def look_clipboard_image_bytes(clipboard_content: object) -> bytes | None:
    """Extract encoded image bytes from grabbed clipboard content.

    - Expects the value of `PIL.ImageGrab.grabclipboard()`: a PIL image,
      a list of file paths, or None.
    - A clipboard bitmap is returned as PNG-encoded bytes.
    - For a file list, reads each file and returns the raw bytes of the
      first one that decodes as an image; unreadable and non-image files
      are skipped.
    - Returns None when no image is present.
    """
    if isinstance(clipboard_content, Image.Image):
        buffer = BytesIO()
        clipboard_content.save(buffer, format="PNG")
        return buffer.getvalue()

    if isinstance(clipboard_content, list):
        for raw_path in clipboard_content:
            file_path = Path(raw_path)
            try:
                file_bytes = file_path.read_bytes()
            except OSError:
                continue
            try:
                decode_image(file_bytes)
            except ValueError:
                continue
            return file_bytes

    return None


def _look_max_display_width(text_widget: Text) -> int:
    """Return the widest image width in pixels that fits the text area.

    - Falls back to a fixed width before the widget is mapped, when Tk
      reports a width of 1 or less.
    - Never returns less than 50 pixels.
    """
    widget_width = text_widget.winfo_width()
    if widget_width <= 1:
        return FALLBACK_MAX_WIDTH_PX
    return max(50, widget_width - EDITOR_HORIZONTAL_PADDING_PX)


def insert_image_at(
    text_widget: Text,
    index: str,
    image_ref: ImageRef,
) -> str:
    """Embed one image in the widget at the given index.

    - The display copy is scaled to the entry's display size, or the
      natural size when unset, then shrunk proportionally to fit the text
      area.
    - The stored ImageRef keeps the original bytes and dimensions.
    - Registers the photo and the ImageRef under the returned Tk image
      name; the widget must have registries from `init_image_registry`.
    - Raises OSError when Pillow cannot read the stored bytes.
    """
    with Image.open(BytesIO(image_ref.image_bytes)) as image:
        image.load()
        target_width = image_ref.display_width_px or image.width
        target_height = image_ref.display_height_px or image.height
        max_width = _look_max_display_width(text_widget)
        if target_width > max_width:
            scale = max_width / target_width
            target_width = max_width
            target_height = max(1, round(target_height * scale))
        target_size = (max(1, target_width), max(1, target_height))
        display_image = (
            image.resize(target_size)
            if target_size != image.size
            else image.copy()
        )

    photo = ImageTk.PhotoImage(display_image)
    image_name = text_widget.image_create(index, image=photo)
    PHOTOS_BY_WIDGET[text_widget][image_name] = photo
    IMAGE_REFS_BY_WIDGET[text_widget][image_name] = image_ref
    return image_name


def insert_image_bytes_at_cursor(
    text_widget: Text,
    image_bytes: bytes,
) -> bool:
    """Decode raw bytes and insert the image at the cursor.

    Returns False without changing the widget when the bytes are not a
    readable image, and True after the image is inserted.
    """
    try:
        image_ref = decode_image(image_bytes)
    except ValueError:
        return False

    insert_image_at(text_widget, "insert", image_ref)
    return True
