"""Persist document models to and from disk."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.domains.documents.plain_text_rtf import (
    format_plain_text_rtf,
    parse_plain_text_rtf,
)

if TYPE_CHECKING:
    from pathlib import Path

    from src.domains.documents.models import DocumentModel


def read_rtf(file_path: Path) -> DocumentModel:
    """Read a Plain Text RTF document from disk.

    - The file is decoded as UTF-8.
    - Raises PlainTextRtfError when the content is not valid Plain Text RTF.
    """
    return parse_plain_text_rtf(file_path.read_text(encoding="utf-8"))


def write_rtf(file_path: Path, document: DocumentModel) -> None:
    """Write a document model to disk as Plain Text RTF.

    - The target file is overwritten.
    - The file is written as UTF-8 with LF line endings on every platform.
    """
    with file_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(format_plain_text_rtf(document))
