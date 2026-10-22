"""Exercise document-domain model invariants."""

from __future__ import annotations

from src.domains.documents.models import (
    DEFAULT_FONT_FAMILY,
    OBJECT_REPLACEMENT_CHAR,
    DocumentModel,
    ImageRef,
    TextSpan,
    TextStyle,
)


class TestTextStyle:
    def test_font_family_defaults_to_document_default(self) -> None:
        style = TextStyle()

        assert style.font_family is None
        assert DEFAULT_FONT_FAMILY == "Segoe UI"


class TestImageRef:
    def test_image_ref_holds_image_data(self) -> None:
        image_ref = ImageRef(
            offset=3,
            image_bytes=b"\x89PNG",
            image_format="png",
            width_px=10,
            height_px=20,
            display_width_px=5,
            display_height_px=10,
        )
        assert image_ref.offset == 3
        assert image_ref.image_format == "png"

    def test_document_model_defaults_to_no_images(self) -> None:
        document = DocumentModel(spans=(TextSpan(text="hi"),))
        assert document.images == ()

    def test_placeholder_char_is_object_replacement(self) -> None:
        assert OBJECT_REPLACEMENT_CHAR == "￼"
