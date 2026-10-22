"""Read and write the editor's Plain Text RTF document format.

- Owns conversion between Plain Text RTF strings and DocumentModel objects.
- Does not perform filesystem I/O.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from io import BytesIO
from typing import Literal
from urllib.parse import quote, unquote

from PIL import Image

from src.domains.documents.content import (
    append_span,
    coalesce_spans,
    iter_text_images,
)
from src.domains.documents.models import (
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    ImageRef,
    TextSpan,
    TextStyle,
)

DEFAULT_STYLE = TextStyle()


FORMAT_HEADER = "PTRTF/1"
OPEN_MARKER = "[["
CLOSE_MARKER = "]]"
STYLE_END_MARKER = "[[/]]"
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-f]{6}$")
ATTRIBUTE_NAME_PATTERN = re.compile(r"^[a-z]+$")
SUPPORTED_IMAGE_FORMATS: dict[str, Literal["png", "jpeg"]] = {
    "PNG": "png",
    "JPEG": "jpeg",
}


class PlainTextRtfError(ValueError):
    """Signal invalid Plain Text RTF document content."""


def _escape_text(text: str) -> str:
    """Escape backslashes and square brackets so text cannot open a marker."""
    return (
        text.replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace(
            "]",
            "\\]",
        )
    )


def _format_style_attributes(style: TextStyle) -> str:
    """Return the marker attribute list for a style.

    - Only non-default fields are written, joined by ``;``.
    - Font family names are percent-encoded.
    - Returns an empty string for the default style.
    """
    attributes: list[str] = []
    if style.font_family is not None:
        attributes.append(f"font={quote(style.font_family, safe='')}")
    if style.font_size is not None:
        attributes.append(f"size={style.font_size}")
    if style.foreground_color is not None:
        attributes.append(f"color={style.foreground_color}")
    if style.bold:
        attributes.append("bold=true")
    if style.italic:
        attributes.append("italic=true")
    if style.underline:
        attributes.append("underline=true")
    if style.strikethrough:
        attributes.append("strikethrough=true")
    if style.background_color is not None:
        attributes.append(f"background={style.background_color}")
    return ";".join(attributes)


def _format_styled_text(text: str, style: TextStyle) -> str:
    """Return escaped text, wrapped in a style span unless the style is default.

    Empty text with a non-default style still produces an empty style span.
    """
    escaped_text = _escape_text(text)
    attributes = _format_style_attributes(style)
    if not attributes:
        return escaped_text
    return (
        f"{OPEN_MARKER}{attributes}{CLOSE_MARKER}"
        f"{escaped_text}{STYLE_END_MARKER}"
    )


def _format_image(image: ImageRef) -> str:
    """Return an image marker with the display size and base64 payload."""
    payload = base64.b64encode(image.image_bytes).decode("ascii")
    return (
        f"{OPEN_MARKER}image={image.image_format};"
        f"width={image.display_width_px};height={image.display_height_px};"
        f"payload={payload}{CLOSE_MARKER}"
    )


def _format_span(
    span: TextSpan,
    start_offset: int,
    images_by_offset: dict[int, ImageRef],
) -> str:
    """Format one span, replacing image placeholders with image markers.

    - ``start_offset`` is the span's position in the document's plain text.
    - A placeholder with no image at its offset is dropped from the output.
    """
    parts: list[str] = []
    for text, image in iter_text_images(
        span.text, start_offset, images_by_offset
    ):
        parts.append(_format_styled_text(text, span.style))
        if image is not None:
            parts.append(_format_image(image))
    return "".join(parts)


def format_plain_text_rtf(document: DocumentModel) -> str:
    """Format a document model as a Plain Text RTF document.

    - Output starts with the ``PTRTF/1`` header line.
    - Adjacent spans with equal styles are merged before formatting.
    - Images are embedded inline as base64 markers at their offsets.
    """
    normalized_document = coalesce_spans(list(document.spans))
    images_by_offset = {image.offset: image for image in document.images}
    parts = [FORMAT_HEADER, "\n"]
    offset = 0
    for span in normalized_document.spans:
        parts.append(_format_span(span, offset, images_by_offset))
        offset += len(span.text)
    return "".join(parts)


def _read_attributes(marker_content: str) -> dict[str, str]:
    """Parse ``name=value`` pairs separated by ``;`` from a marker.

    Raises PlainTextRtfError when the marker is empty, a name is not lowercase
    letters, an assignment has no ``=``, or a name repeats.
    """
    if not marker_content:
        msg = "Plain Text RTF markers must contain attributes."
        raise PlainTextRtfError(msg)

    attributes: dict[str, str] = {}
    for assignment in marker_content.split(";"):
        name, separator, value = assignment.partition("=")
        if not separator or not ATTRIBUTE_NAME_PATTERN.fullmatch(name):
            msg = "Plain Text RTF contains an invalid marker attribute."
            raise PlainTextRtfError(msg)
        if name in attributes:
            msg = "Plain Text RTF marker attributes must be unique."
            raise PlainTextRtfError(msg)
        attributes[name] = value
    return attributes


def _look_positive_integer(value: str | None) -> int | None:
    """Return the value as a positive integer, or None when it is not one."""
    if value is None or not value.isdecimal():
        return None
    result = int(value)
    return result if result > 0 else None


def _look_color(value: str | None) -> str | None:
    """Return the value if it is a lowercase ``#rrggbb`` color, else None."""
    if value is None or not HEX_COLOR_PATTERN.fullmatch(value):
        return None
    return value


def _look_font_family(value: str | None) -> str | None:
    """Return the percent-decoded font family, or None when it is empty."""
    if not value:
        return None
    font_family = unquote(value)
    return font_family or None


def _look_enabled(value: str | None) -> bool:
    """Return True only for the exact flag value ``true``."""
    return value == "true"


def _read_style(attributes: dict[str, str]) -> TextStyle:
    """Build a text style from marker attributes.

    - Invalid or unknown values fall back to the default for that field
      instead of raising.
    - Unknown attribute names are ignored.
    """
    return TextStyle(
        font_family=_look_font_family(attributes.get("font")),
        font_size=_look_positive_integer(attributes.get("size")),
        foreground_color=_look_color(attributes.get("color")),
        bold=_look_enabled(attributes.get("bold")),
        italic=_look_enabled(attributes.get("italic")),
        underline=_look_enabled(attributes.get("underline")),
        strikethrough=_look_enabled(attributes.get("strikethrough")),
        background_color=_look_color(attributes.get("background")),
    )


def _read_image(
    attributes: dict[str, str],
    offset: int,
) -> ImageRef:
    """Build an image reference from image marker attributes.

    - The marker must give ``png`` or ``jpeg``, a positive display width and
      height, and a base64 payload.
    - The payload must decode to an image whose real format matches the
      marker.
    - Pixel size comes from the decoded image, not from the marker.
    - Raises PlainTextRtfError when any rule fails.
    """
    marker_format = attributes.get("image")
    display_width_px = _look_positive_integer(attributes.get("width"))
    display_height_px = _look_positive_integer(attributes.get("height"))
    payload = attributes.get("payload")
    if marker_format == "png":
        image_format: Literal["png", "jpeg"] = "png"
    elif marker_format == "jpeg":
        image_format = "jpeg"
    else:
        msg = "Plain Text RTF contains an invalid image marker."
        raise PlainTextRtfError(msg)

    if display_width_px is None or display_height_px is None or payload is None:
        msg = "Plain Text RTF contains an invalid image marker."
        raise PlainTextRtfError(msg)

    try:
        image_bytes = base64.b64decode(payload, validate=True)
        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
            actual_format = SUPPORTED_IMAGE_FORMATS.get(
                (image.format or "").upper(),
            )
            width_px, height_px = image.size
    except (OSError, ValueError) as error:
        msg = "Plain Text RTF contains an invalid image payload."
        raise PlainTextRtfError(msg) from error

    if actual_format != image_format:
        msg = "Plain Text RTF image format does not match its payload."
        raise PlainTextRtfError(msg)

    return ImageRef(
        offset=offset,
        image_bytes=image_bytes,
        image_format=image_format,
        width_px=width_px,
        height_px=height_px,
        display_width_px=display_width_px,
        display_height_px=display_height_px,
    )


def _read_escape(body: str, index: int) -> tuple[str, int]:
    """Read the escape sequence starting at a backslash.

    - Returns the decoded character and the index after the sequence.
    - A backslash not followed by a backslash or square bracket is kept as a
      literal backslash.
    """
    escaped_char = body[index + 1 : index + 2]
    if escaped_char and escaped_char in "\\[]":
        return escaped_char, index + 2
    return "\\", index + 1


@dataclass
class _BodyReader:
    """Collect spans and images while reading a Plain Text RTF body.

    - Mutable parse state; use one instance per parse.
    - ``offset`` tracks the current position in the document's plain text,
      where each image counts as one character.
    """

    body: str
    spans: list[TextSpan] = field(default_factory=list)
    images: list[ImageRef] = field(default_factory=list)
    offset: int = 0

    def read_escaped_text(
        self,
        start_index: int,
        style: TextStyle,
        *,
        stop_at_style_end: bool,
    ) -> int:
        """Read text in one style and return the index where reading stopped.

        - Appends spans and images to the reader as they are found.
        - With ``stop_at_style_end``, reads a style span's content and returns
          the index after its end marker; reaching the end of the body first
          raises PlainTextRtfError.
        - Without it, reads to the end of the body; a stray end marker raises
          PlainTextRtfError.
        """
        body = self.body
        text_parts: list[str] = []
        index = start_index
        while index < len(body):
            if body[index] == "\\":
                text, index = _read_escape(body, index)
                text_parts.append(text)
                continue

            if body.startswith(STYLE_END_MARKER, index):
                if not stop_at_style_end:
                    msg = (
                        "Plain Text RTF contains an unexpected style end "
                        "marker."
                    )
                    raise PlainTextRtfError(msg)
                self._flush_text(text_parts, style)
                return index + len(STYLE_END_MARKER)

            if body.startswith(OPEN_MARKER, index):
                self._flush_text(text_parts, style)
                index = self._read_marker(
                    index,
                    style,
                    in_style_span=stop_at_style_end,
                )
                continue

            text_parts.append(body[index])
            index += 1

        self._flush_text(text_parts, style)
        if stop_at_style_end:
            msg = "Plain Text RTF contains an unclosed style span."
            raise PlainTextRtfError(msg)
        return index

    def _flush_text(self, text_parts: list[str], style: TextStyle) -> None:
        """Move buffered text into the span list and advance ``offset``.

        Clears ``text_parts`` in place.
        """
        text = "".join(text_parts)
        append_span(self.spans, text, style)
        self.offset += len(text)
        text_parts.clear()

    def _read_marker(
        self,
        index: int,
        style: TextStyle,
        *,
        in_style_span: bool,
    ) -> int:
        """Read the marker at ``index`` and return the index after it.

        - An image marker adds an image and one placeholder character in the
          surrounding style.
        - Any other marker opens a style span, which is read through its end
          marker.
        - Raises PlainTextRtfError for an unclosed marker or a style span
          opened inside another style span.
        """
        body = self.body
        marker_end = body.find(CLOSE_MARKER, index + len(OPEN_MARKER))
        if marker_end < 0:
            msg = "Plain Text RTF contains an unclosed marker."
            raise PlainTextRtfError(msg)
        attributes = _read_attributes(
            body[index + len(OPEN_MARKER) : marker_end],
        )
        if "image" in attributes:
            self.images.append(_read_image(attributes, self.offset))
            append_span(self.spans, OBJECT_REPLACEMENT_CHAR, style)
            self.offset += 1
            return marker_end + len(CLOSE_MARKER)
        if in_style_span:
            msg = "Plain Text RTF style spans must not be nested."
            raise PlainTextRtfError(msg)
        return self.read_escaped_text(
            marker_end + len(CLOSE_MARKER),
            _read_style(attributes),
            stop_at_style_end=True,
        )


def parse_plain_text_rtf(content: str) -> DocumentModel:
    """Parse a Plain Text RTF document into a document model.

    - CRLF and CR line endings are normalized to LF first.
    - The first line must be the ``PTRTF/1`` header.
    - Style spans must be closed and must not be nested.
    - Raises PlainTextRtfError when the content breaks any format rule.
    """
    normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")
    header, separator, body = normalized_content.partition("\n")
    if header != FORMAT_HEADER:
        msg = "This file is not a Plain Text RTF document."
        raise PlainTextRtfError(msg)
    if not separator:
        body = ""

    reader = _BodyReader(body)
    reader.read_escaped_text(0, DEFAULT_STYLE, stop_at_style_end=False)
    return DocumentModel(spans=tuple(reader.spans), images=tuple(reader.images))
