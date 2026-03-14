from __future__ import annotations

import logging
import re
from typing import List

from core.models import Chapter

logger = logging.getLogger(__name__)


class ChapterSplitter:
    """Split text into chapters using heading-like patterns with fallback chunks."""

    HEADING_PATTERN = re.compile(
        r"(?im)^\s*(chapter|cap[ií]tulo|section|secci[oó]n)\s+([\w\.-]+)[:\-\s]*(.*)$"
    )

    def split(self, text: str) -> List[Chapter]:
        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            logger.info("No chapter headings detected; using generic segmentation")
            return self._fallback_split(text)

        chapters: List[Chapter] = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            heading_label = " ".join(part for part in match.groups() if part).strip()
            content = text[start:end].strip()
            chapters.append(Chapter(title=heading_label, content=content, index=i + 1))

        logger.info("Split into %s chapters", len(chapters))
        return chapters

    def _fallback_split(self, text: str, max_chars: int = 5000) -> List[Chapter]:
        chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)]
        return [
            Chapter(title=f"Section {idx}", content=chunk.strip(), index=idx)
            for idx, chunk in enumerate(chunks, start=1)
            if chunk.strip()
        ]
