from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from core.config import settings
from core.models import Chapter, Chunk, Document, DocumentInputMode, DocumentStatus
from core.schemas import NotesInputPayload
from services.chapter_splitter import ChapterSplitter
from services.chunker import TextChunker
from services.pdf_reader import PDFReader
from services.storage import LocalStorage

logger = logging.getLogger(__name__)


class StudyBrainOrchestrator:
    """Run processing pipelines for PDF and manual notes."""

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
            input_mode=DocumentInputMode.PDF,
            chapters=chapters,
            status=DocumentStatus.PROCESSED,
            metadata={
                "input_mode": DocumentInputMode.PDF.value,
                "page_count": extraction["page_count"],
                "reader": "pymupdf",
                "ocr_ready": True,
                "empty_text_pages": sum(1 for page in pages if page.get("needs_ocr")),
            },
        )

        chunks_by_chapter = self._chunk_document_chapters(document)
        return self._build_and_save_pipeline_output(document, pages, chunks_by_chapter)

    def process_notes(self, payload: NotesInputPayload) -> Dict[str, Any]:
        logger.info("Starting notes processing pipeline for title=%s", payload.title)
        notes_text = payload.notes.strip()
        chapters = self.splitter.split(notes_text)
        if not chapters:
            chapters = [
                Chapter(
                    index=1,
                    title="Notes",
                    content=notes_text,
                    metadata={"heuristic": "manual_notes", "start_char": 0, "end_char": len(notes_text)},
                )
            ]

        document = Document(
            source_path=Path(f"notes://{payload.title}"),
            title=payload.title,
            raw_text=notes_text,
            language=payload.language,
            input_mode=DocumentInputMode.NOTES,
            chapters=chapters,
            status=DocumentStatus.PROCESSED,
            metadata={
                "input_mode": DocumentInputMode.NOTES.value,
                "page_count": 0,
                "reader": "notes",
                "ocr_ready": False,
                "empty_text_pages": 0,
                "chunking_skipped": True,
            },
        )

        chunks_by_chapter: Dict[int, List[Chunk]] = {chapter.index: [] for chapter in document.chapters}
        return self._build_and_save_pipeline_output(document, [], chunks_by_chapter)

    def _chunk_document_chapters(self, document: Document) -> Dict[int, List[Chunk]]:
        chunks_by_chapter: Dict[int, List[Chunk]] = {}
        for chapter in document.chapters:
            try:
                chapter_chunks = self.chunker.chunk_chapter(chapter)
            except Exception as exc:
                logger.exception("Chunking failed for chapter %s", chapter.index)
                raise RuntimeError(f"Failed to chunk chapter {chapter.index}") from exc
            chunks_by_chapter[chapter.index] = chapter_chunks
        return chunks_by_chapter

    def _build_and_save_pipeline_output(
        self,
        document: Document,
        pages: List[Dict[str, Any]],
        chunks_by_chapter: Dict[int, List[Chunk]],
    ) -> Dict[str, Any]:
        output_path = self.storage.save_processed_document(document, pages, chunks_by_chapter)

        pipeline_output = {
            "document": {
                "document_id": document.id,
                "title": document.title,
                "slug": document.slug,
                "source_path": str(document.source_path),
                "metadata": document.metadata,
                "output_path": str(output_path),
                "input_mode": document.input_mode.value,
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
            "Pipeline finished for %s | input_mode=%s | chapters=%s | chunks=%s",
            document.title,
            document.input_mode.value,
            len(document.chapters),
            sum(len(value) for value in chunks_by_chapter.values()),
        )
        return pipeline_output
