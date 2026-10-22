"""Define document-domain models shared across editor features."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 11


@dataclass(frozen=True, slots=True)
class TextStyle:
    """Describe inline styling for a text span.

    - Instances are immutable and compare by value, so equal styles can be
      merged.
    - None for a font or color field means "inherit the editor default".
    - Colors are ``#rrggbb`` hex strings.
    """

    font_family: str | None = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    font_size: int | None = None
    foreground_color: str | None = None
    background_color: str | None = None


@dataclass(frozen=True, slots=True)
class TextSpan:
    """Represent a contiguous run of text with a single style.

    Instances are immutable; build a new span to change text or style.
    """

    text: str
    style: TextStyle = field(default_factory=TextStyle)


OBJECT_REPLACEMENT_CHAR = "\N{OBJECT REPLACEMENT CHARACTER}"


@dataclass(frozen=True, slots=True)
class ImageRef:
    """Describe one embedded image anchored at a character offset.

    - The image occupies exactly one ``OBJECT_REPLACEMENT_CHAR`` position in
      the document's plain text at ``offset``.
    - ``width_px`` and ``height_px`` are the encoded image's pixel size; the
      ``display_`` fields are the size shown in the editor.
    - Instances are immutable.
    """

    offset: int
    image_bytes: bytes
    image_format: Literal["png", "jpeg"]
    width_px: int
    height_px: int
    display_width_px: int
    display_height_px: int


@dataclass(frozen=True, slots=True)
class DocumentModel:
    """Represent the full editor document as styled spans.

    - Instances are immutable.
    - Each image is anchored to an ``OBJECT_REPLACEMENT_CHAR`` in the span
      text; image offsets index into ``plain_text``.
    """

    spans: tuple[TextSpan, ...]
    images: tuple[ImageRef, ...] = ()

    @property
    def plain_text(self) -> str:
        """Return the plain-text view of the document.

        Images appear as ``OBJECT_REPLACEMENT_CHAR`` placeholders.
        """
        return "".join(span.text for span in self.spans)
