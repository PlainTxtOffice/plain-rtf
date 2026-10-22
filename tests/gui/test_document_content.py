"""Check that document rendering and serialization agree on image placement."""

from __future__ import annotations

import tkinter as tk
from dataclasses import replace
from io import BytesIO

import pytest
from PIL import Image

from src.domains.documents.models import (
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    ImageRef,
    TextSpan,
    TextStyle,
)
from src.domains.documents.plain_text_rtf import (
    format_plain_text_rtf,
    parse_plain_text_rtf,
)
from src.gui.views.text_buffer import (
    create_style_tags,
    load_document_into_text,
    read_document_from_text,
)


@pytest.mark.parametrize(
    ("text", "offsets", "expected_text", "expected_offsets"),
    [
        ("", (), "", ()),
        ("plain", (), "plain", ()),
        ("@a@", (0, 2), "@a@", (0, 2)),
        ("@@", (0, 1), "@@", (0, 1)),
        ("@a@b@", (2,), "a@b", (1,)),
        ("@a@", (), "a", ()),
    ],
)
def test_consumers_preserve_image_positions(
    text, offsets, expected_text, expected_offsets
) -> None:
    payload = BytesIO()
    Image.new("RGB", (4, 2), "red").save(payload, format="PNG")
    image = ImageRef(0, payload.getvalue(), "png", 4, 2, 4, 2)
    document = DocumentModel(
        spans=(
            TextSpan("prefix", TextStyle(italic=True)),
            TextSpan(text.replace("@", OBJECT_REPLACEMENT_CHAR)),
            TextSpan("suffix", TextStyle(bold=True)),
        ),
        images=tuple(replace(image, offset=6 + offset) for offset in offsets),
    )
    expected = DocumentModel(
        spans=(
            TextSpan("prefix", TextStyle(italic=True)),
            *(
                (TextSpan(expected_text.replace("@", OBJECT_REPLACEMENT_CHAR)),)
                if expected_text
                else ()
            ),
            TextSpan("suffix", TextStyle(bold=True)),
        ),
        images=tuple(
            replace(image, offset=6 + offset) for offset in expected_offsets
        ),
    )

    assert parse_plain_text_rtf(format_plain_text_rtf(document)) == expected

    root = tk.Tk()
    root.withdraw()
    try:
        widget = tk.Text(root)
        create_style_tags(widget)
        load_document_into_text(widget, document)
        result = read_document_from_text(widget)
        assert result == expected
        assert not widget.edit_modified()
    finally:
        root.destroy()
