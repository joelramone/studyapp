from __future__ import annotations

import logging
from pathlib import Path

import fitz

logger = logging.getLogger(__name__)


class PDFReader:
    """Read text content from PDF files using PyMuPDF."""

    def read(self, pdf_path: Path) -> str:
        if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
            raise FileNotFoundError(f"Invalid PDF path: {pdf_path}")

        logger.info("Reading PDF: %s", pdf_path)
        try:
            with fitz.open(pdf_path) as doc:
                pages = [page.get_text("text") for page in doc]
        except Exception as exc:  # pragma: no cover - external parser edge cases
            logger.exception("Failed to read PDF: %s", pdf_path)
            raise RuntimeError(f"Unable to parse PDF: {pdf_path}") from exc

        text = "\n".join(page.strip() for page in pages if page.strip())
        if not text:
            raise ValueError("The PDF does not contain extractable text")
        return text
