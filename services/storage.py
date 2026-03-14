from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from core.models import Chunk, Document

logger = logging.getLogger(__name__)


class LocalStorage:
    """Persist processed document artifacts on local filesystem."""

    def __init__(self, base_output_dir: Path) -> None:
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def document_dir(self, document: Document) -> Path:
        safe_slug = document.slug or document.title.replace(" ", "_").lower()
        path = self.base_output_dir / safe_slug
        path.mkdir(parents=True, exist_ok=True)
        return path

    def chapter_dir(self, document: Document, chapter_index: int) -> Path:
        path = self.document_dir(document) / f"chapter_{chapter_index:02d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_processed_document(
        self,
        document: Document,
        pages: List[Dict[str, Any]],
        chunks_by_chapter: Dict[int, List[Chunk]],
    ) -> Path:
        root = self.document_dir(document)

        self.save_json(root / "metadata.json", self._build_metadata(document, pages, chunks_by_chapter))
        self.save_text(root / "raw_text.md", document.raw_text)
        self.save_json(root / "pages.json", pages)
        self.save_json(root / "chapters_index.json", self._build_chapters_index(document, chunks_by_chapter))

        for chapter in document.chapters:
            chapter_path = self.chapter_dir(document, chapter.index)
            self.save_text(chapter_path / "source.md", chapter.content)

        logger.info("Saved processed document '%s' to %s", document.title, root)
        return root

    def _build_metadata(
        self,
        document: Document,
        pages: List[Dict[str, Any]],
        chunks_by_chapter: Dict[int, List[Chunk]],
    ) -> Dict[str, Any]:
        return {
            "document_id": document.id,
            "title": document.title,
            "slug": document.slug,
            "source_path": str(document.source_path),
            "input_mode": document.input_mode,
            "status": document.status,
            "language": document.language,
            "page_count": len(pages),
            "chapter_count": len(document.chapters),
            "chunk_count": sum(len(items) for items in chunks_by_chapter.values()),
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
            "metadata": document.metadata,
        }

    def _build_chapters_index(
        self,
        document: Document,
        chunks_by_chapter: Dict[int, List[Chunk]],
    ) -> List[Dict[str, Any]]:
        index: List[Dict[str, Any]] = []
        for chapter in document.chapters:
            chapter_chunks = chunks_by_chapter.get(chapter.index, [])
            index.append(
                {
                    "chapter_id": chapter.id,
                    "index": chapter.index,
                    "title": chapter.title,
                    "char_count": len(chapter.content),
                    "chunk_count": len(chapter_chunks),
                    "metadata": chapter.metadata,
                }
            )
        return index

    def save_text(self, path: Path, content: str) -> None:
        logger.debug("Writing text file: %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def save_json(self, path: Path, payload: Any) -> None:
        logger.debug("Writing JSON file: %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
