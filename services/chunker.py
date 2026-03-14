from __future__ import annotations

import logging
from typing import Any, Dict, List

from core.models import Chapter, Chunk

logger = logging.getLogger(__name__)


class TextChunker:
    """Create overlapping chunks from chapter text."""

    def __init__(self, chunk_size: int = 1400, overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap must be >= 0")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        chunks: List[str] = []
        for payload in self.chunk_with_spans(text):
            chunks.append(payload["text"])
        return chunks

    def chunk_with_spans(self, text: str) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        chunks: List[Dict[str, Any]] = []
        text_len = len(text)
        start = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            current = text[start:end]
            normalized = current.strip()
            left_trim = len(current) - len(current.lstrip())
            right_trim = len(current) - len(current.rstrip())
            normalized_start = start + left_trim
            normalized_end = end - right_trim

            if normalized:
                chunks.append(
                    {
                        "index": len(chunks) + 1,
                        "text": normalized,
                        "start_char": normalized_start,
                        "end_char": normalized_end,
                        "token_estimate": self._estimate_tokens(normalized),
                    }
                )

            if end >= text_len:
                break
            start = end - self.overlap

        return chunks

    def chunk_chapter(self, chapter: Chapter) -> List[Chunk]:
        spans = self.chunk_with_spans(chapter.content)
        chunk_models: List[Chunk] = []

        for item in spans:
            chunk_models.append(
                Chunk(
                    chapter_id=chapter.id,
                    index=item["index"],
                    text=item["text"],
                    start_char=item["start_char"],
                    end_char=item["end_char"],
                    token_estimate=item["token_estimate"],
                    metadata={"strategy": "sliding_window", "overlap": self.overlap},
                )
            )

        logger.info(
            "Generated %s chunks for chapter %s (%s)",
            len(chunk_models),
            chapter.index,
            chapter.title,
        )
        return chunk_models

    def _estimate_tokens(self, text: str) -> int:
        # Pragmatic estimate for downstream planning (~4 chars/token English-like text).
        return max(1, len(text) // 4)
