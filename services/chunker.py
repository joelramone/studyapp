from __future__ import annotations

from typing import List


class TextChunker:
    """Create overlapping text chunks suitable for LLM prompts."""

    def __init__(self, chunk_size: int = 1400, overlap: int = 200) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        if not text.strip():
            return []

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end].strip())
            if end == len(text):
                break
            start = end - self.overlap
        return [chunk for chunk in chunks if chunk]
