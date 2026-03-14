from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

import fitz

logger = logging.getLogger(__name__)


class PDFReader:
    """Read PDF files from disk and extract text per page.

    This service is intentionally OCR-ready: page payloads include placeholders
    that can be populated by a future OCR pipeline when embedded text is poor.
    """

    def read(self, pdf_path: Path) -> Dict[str, Any]:
        """Read and parse a PDF from disk.

        Returns a dictionary with:
        - source_path: str
        - page_count: int
        - pages: list[dict] with per-page text and stats
        - raw_text: str (all pages concatenated)
        """
        self._validate_pdf_path(pdf_path)

        logger.info("Opening PDF for extraction: %s", pdf_path)
        pages: List[Dict[str, Any]] = []
        try:
            with fitz.open(pdf_path) as doc:
                for page_number, page in enumerate(doc, start=1):
                    text = page.get_text("text") or ""
                    clean_text = text.strip()
                    page_payload = {
                        "page_number": page_number,
                        "text": clean_text,
                        "char_count": len(clean_text),
                        "word_count": len(clean_text.split()) if clean_text else 0,
                        "needs_ocr": not bool(clean_text),
                    }
                    pages.append(page_payload)

                    if clean_text:
                        logger.debug(
                            "Extracted page %s with %s chars",
                            page_number,
                            len(clean_text),
                        )
                    else:
                        logger.warning(
                            "Page %s has no embedded text. OCR may be needed in the future.",
                            page_number,
                        )
        except Exception as exc:  # pragma: no cover - parser edge cases
            logger.exception("Failed to parse PDF: %s", pdf_path)
            raise RuntimeError(f"Unable to parse PDF: {pdf_path}") from exc

        raw_text = "\n\n".join(page["text"] for page in pages if page["text"])
        if not raw_text:
            logger.warning("PDF extracted with poor/no text: %s", pdf_path)

        logger.info("Finished extraction for %s (%s pages)", pdf_path.name, len(pages))
        return {
            "source_path": str(pdf_path),
            "page_count": len(pages),
            "pages": pages,
            "raw_text": raw_text,
        }

    def _validate_pdf_path(self, pdf_path: Path) -> None:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not pdf_path.is_file():
            raise ValueError(f"PDF path is not a file: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected .pdf file, got: {pdf_path}")
