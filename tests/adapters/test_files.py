"""Exercise file loading edge cases for the disk adapter."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.adapters.files import read_rtf, write_rtf
from src.domains.documents.models import DocumentModel, TextSpan



def test_read_rtf_rejects_microsoft_rtf_content() -> None:
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "legacy.rtf"
        file_path.write_text(r"{\rtf1\ansi Legacy RTF}", encoding="utf-8")

        with pytest.raises(ValueError, match="not a Plain Text RTF"):
            read_rtf(file_path)


def test_write_rtf_uses_utf8_plain_text_rtf() -> None:
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "notes.rtf"
        document = DocumentModel(spans=(TextSpan(text="Grüße"),))

        write_rtf(file_path, document)

        assert file_path.read_bytes().startswith(b"PTRTF/1\n")
        assert read_rtf(file_path) == document