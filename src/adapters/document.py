"""Adapt document and image files for the editor interface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.adapters.files import read_rtf, write_rtf

if TYPE_CHECKING:
    from pathlib import Path

    from src.domains.documents.models import DocumentModel


class DocumentAdapter:
    """Provide the editor's file operations for documents and images.

    - Holds no state; every operation is a static method.
    """

    @staticmethod
    def load_document(file_path: Path) -> DocumentModel:
        """Load a Plain Text RTF document from disk.

        Raises PlainTextRtfError when the content is not valid Plain Text RTF.
        """
        return read_rtf(file_path)

    @staticmethod
    def save_document(
        file_path: Path,
        document: DocumentModel,
    ) -> None:
        """Save a document to disk as Plain Text RTF.

        The target file is overwritten.
        """
        write_rtf(file_path, document)

    @staticmethod
    def read_image_bytes(file_path: Path) -> bytes:
        """Read the encoded image data at the selected path.

        The bytes are returned as stored; the format is not validated here.
        """
        return file_path.read_bytes()
