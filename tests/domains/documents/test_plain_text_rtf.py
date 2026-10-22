"""Exercise the Plain Text RTF document codec."""

from __future__ import annotations

import base64
from io import BytesIO

import pytest
from PIL import Image

from src.domains.documents.content import coalesce_spans
from src.domains.documents.models import (
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    ImageRef,
    TextSpan,
    TextStyle,
)
from src.domains.documents.plain_text_rtf import (
    FORMAT_HEADER,
    PlainTextRtfError,
    format_plain_text_rtf,
    parse_plain_text_rtf,
)


def _make_png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (4, 2), (255, 0, 0)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_round_trip_escaped_plain_text() -> None:
    document = DocumentModel(
        spans=(TextSpan(text=r"Use [[markers]] and \ literally."),),
    )

    content = format_plain_text_rtf(document)

    assert content.startswith(f"{FORMAT_HEADER}\n")
    assert parse_plain_text_rtf(content) == document


def test_round_trip_mixed_text_styles() -> None:
    document = DocumentModel(
        spans=(
            TextSpan(text="plain "),
            TextSpan(
                text="formatted",
                style=TextStyle(
                    font_family="Times New Roman",
                    font_size=18,
                    foreground_color="#ff0000",
                    bold=True,
                    italic=True,
                    underline=True,
                    strikethrough=True,
                    background_color="#fff59d",
                ),
            ),
        ),
    )

    content = format_plain_text_rtf(document)

    assert "font=Times%20New%20Roman" in content
    assert parse_plain_text_rtf(content) == document


def test_round_trip_embedded_image() -> None:
    image_bytes = _make_png_bytes()
    document = DocumentModel(
        spans=(TextSpan(text=f"before {OBJECT_REPLACEMENT_CHAR} after"),),
        images=(
            ImageRef(
                offset=7,
                image_bytes=image_bytes,
                image_format="png",
                width_px=4,
                height_px=2,
                display_width_px=40,
                display_height_px=20,
            ),
        ),
    )

    result = parse_plain_text_rtf(format_plain_text_rtf(document))

    assert result == document


def test_coalescing_matches_parser_without_mutating_input() -> None:
    bold = TextStyle(bold=True)
    spans = [
        TextSpan(""),
        TextSpan("a", bold),
        TextSpan("", TextStyle(italic=True)),
        TextSpan("b", bold),
        TextSpan("c"),
        TextSpan("d"),
        TextSpan("e", bold),
    ]
    original = list(spans)
    expected = DocumentModel(
        spans=(TextSpan("ab", bold), TextSpan("cd"), TextSpan("e", bold)),
    )

    assert coalesce_spans(spans) == expected
    assert spans == original
    assert (
        parse_plain_text_rtf(
            "PTRTF/1\n[[bold=true]]a[[/]][[italic=true]][[/]]"
            "[[bold=true]]b[[/]]cd[[bold=true]]e[[/]]"
        )
        == expected
    )
    assert (
        parse_plain_text_rtf(format_plain_text_rtf(DocumentModel(tuple(spans))))
        == expected
    )


def test_formatter_preserves_empty_style_boundaries() -> None:
    document = DocumentModel(
        spans=(TextSpan(OBJECT_REPLACEMENT_CHAR * 2, TextStyle(bold=True)),),
    )

    assert format_plain_text_rtf(document) == (
        "PTRTF/1\n" + "[[bold=true]][[/]]" * 3
    )


@pytest.mark.parametrize(
    ("payload_format", "marker_format"),
    [("BMP", "png"), ("BMP", "bmp"), ("PNG", "jpeg")],
)
def test_parser_rejects_image_format_mismatch(
    payload_format: str, marker_format: str
) -> None:
    buffer = BytesIO()
    Image.new("RGB", (4, 2), "red").save(buffer, format=payload_format)
    payload = base64.b64encode(buffer.getvalue()).decode("ascii")
    content = (
        f"PTRTF/1\n[[image={marker_format};width=4;height=2;payload={payload}]]"
    )

    with pytest.raises(PlainTextRtfError):
        parse_plain_text_rtf(content)


@pytest.mark.parametrize(
    "content",
    (
        r"{\rtf1\ansi Legacy RTF}",
        "PTRTF/1\n[[bold=true]]unclosed",
        "PTRTF/1\n[[image=png;width=1;height=1;payload=not-base64]]",
    ),
)
def test_rejects_invalid_document_content(content: str) -> None:
    with pytest.raises(PlainTextRtfError):
        parse_plain_text_rtf(content)
