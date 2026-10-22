"""Normalize document spans and traverse embedded image positions."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from src.domains.documents.models import (
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    TextSpan,
    TextStyle,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from src.domains.documents.models import ImageRef


def append_span(
    spans: list[TextSpan],
    text: str,
    style: TextStyle,
) -> None:
    """Append text to the span list, extending the last span when possible.

    - Mutates ``spans`` in place.
    - Empty text is ignored.
    """
    if not text:
        return
    if spans and spans[-1].style == style:
        spans[-1] = replace(spans[-1], text=spans[-1].text + text)
        return
    spans.append(TextSpan(text=text, style=style))


def coalesce_spans(
    spans: list[TextSpan],
) -> DocumentModel:
    """Merge adjacent spans that share the same style.

    - Empty spans are dropped.
    - The returned document has no images; callers carry images separately.
    - The input list is not mutated.
    """
    merged_spans: list[TextSpan] = []

    for span in spans:
        append_span(merged_spans, span.text, span.style)

    return DocumentModel(spans=tuple(merged_spans))


def iter_text_images(
    text: str,
    start_offset: int,
    images_by_offset: Mapping[int, ImageRef],
) -> Iterator[tuple[str, ImageRef | None]]:
    """Yield text segments and the image following each segment.

    - Image lookup uses document offsets, including unmatched placeholders.
    - Unmatched placeholders are omitted and yield None for their image.
    - Empty segments are retained, including the final segment with no image,
      so callers can preserve formatting boundaries.
    """
    text_start = 0
    for text_index, current_char in enumerate(text):
        if current_char == OBJECT_REPLACEMENT_CHAR:
            yield (
                text[text_start:text_index],
                images_by_offset.get(start_offset + text_index),
            )
            text_start = text_index + 1
    yield text[text_start:], None
