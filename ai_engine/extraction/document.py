"""Document text extraction — PDF, DOCX, TXT.

Refactored from the original ``extraction.py``. Streamlit-free; works on bytes.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePath
from typing import BinaryIO

import docx2txt
import pdfplumber


class UnsupportedFileType(ValueError):
    pass


@dataclass(frozen=True)
class ExtractedDocument:
    file_name: str
    text: str
    char_count: int

    @property
    def is_empty(self) -> bool:
        return self.char_count == 0


def extract_text(file_name: str, content: bytes | BinaryIO) -> ExtractedDocument:
    """Extract plain text from a single resume file.

    Args:
        file_name: original filename (used for extension dispatch).
        content: raw bytes OR a file-like object.

    Raises:
        UnsupportedFileType: if extension isn't .pdf, .docx, or .txt.
    """
    suffix = PurePath(file_name).suffix.lower()
    if isinstance(content, (bytes, bytearray)):
        stream = BytesIO(content)
    else:
        stream = content

    if suffix == ".pdf":
        text = _extract_pdf(stream)
    elif suffix == ".docx":
        text = docx2txt.process(stream) or ""
    elif suffix == ".txt":
        text = stream.read().decode("utf-8", errors="ignore")
    else:
        raise UnsupportedFileType(f"Unsupported extension: {suffix}")

    text = text.strip()
    return ExtractedDocument(file_name=file_name, text=text, char_count=len(text))


def _extract_pdf(stream: BinaryIO) -> str:
    parts: list[str] = []
    with pdfplumber.open(stream) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)
