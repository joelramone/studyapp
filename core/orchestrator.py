from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from core.config import settings
from core.models import Chunk, Document, DocumentStatus
from services.chapter_splitter import ChapterSplitter
from services.chunker import TextChunker
from services.pdf_reader import PDFReader
from services.storage import LocalStorage

logger = logging.getLogger(__name__)


class StudyBrainOrchestrator:
    """Run the PDF processing pipeline: reader -> splitter -> chunker -> storage."""

    def __init__(self) -> None:
        self.reader = PDFReader()
        self.splitter = ChapterSplitter()
        self.chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)
        self.storage = LocalStorage(settings.output_dir)

    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        logger.info("Starting PDF processing pipeline for %s", pdf_path)

        extraction = self.reader.read(pdf_path)
        raw_text = extraction["raw_text"]
        pages = extraction["pages"]

        chapters = self.splitter.split(raw_text)
        if not chapters:
            logger.warning("No chapters could be created from PDF '%s'", pdf_path)

        document = Document(
            source_path=pdf_path,
            title=pdf_path.stem,
            raw_text=raw_text if raw_text else " ",
            chapters=chapters,
            status=DocumentStatus.PROCESSED,
            metadata={
                "page_count": extraction["page_count"],
                "reader": "pymupdf",
                "ocr_ready": True,
                "empty_text_pages": sum(1 for page in pages if page.get("needs_ocr")),
            },
        )

        chunks_by_chapter: Dict[int, List[Chunk]] = {}
        for chapter in document.chapters:
            try:
                chapter_chunks = self.chunker.chunk_chapter(chapter)
            except Exception as exc:
                logger.exception("Chunking failed for chapter %s", chapter.index)
                raise RuntimeError(f"Failed to chunk chapter {chapter.index}") from exc
            chunks_by_chapter[chapter.index] = chapter_chunks

        output_path = self.storage.save_processed_document(document, pages, chunks_by_chapter)

        pipeline_output = {
            "document": {
                "document_id": document.id,
                "title": document.title,
                "slug": document.slug,
                "source_path": str(document.source_path),
                "metadata": document.metadata,
                "output_path": str(output_path),
            },
            "pages": pages,
            "chapters": [
                {
                    "chapter_id": chapter.id,
                    "index": chapter.index,
                    "title": chapter.title,
                    "content": chapter.content,
                    "metadata": chapter.metadata,
                    "chunks": [chunk.model_dump(mode="json") for chunk in chunks_by_chapter.get(chapter.index, [])],
                }
                for chapter in document.chapters
            ],
        }

        logger.info(
            "Pipeline finished for %s | chapters=%s | chunks=%s",
            pdf_path.name,
            len(document.chapters),
            sum(len(value) for value in chunks_by_chapter.values()),
        )
        return pipeline_output
