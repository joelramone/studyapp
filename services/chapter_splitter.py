from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from core.models import Chapter

logger = logging.getLogger(__name__)


class ChapterSplitter:
    """Split extracted text into chapter-like sections using heuristics + fallback."""

    # Common heading patterns in technical books and docs.
    _HEADING_PATTERNS = [
        re.compile(r"(?im)^\s*(chapter|cap[ií]tulo)\s+\d+[\.:\-\)]?\s*(.*)$"),
        re.compile(r"(?im)^\s*\d+\s*[\.)]\s+.+$"),
        re.compile(r"(?im)^\s*\d+\.\d+(?:\.\d+)?\s+.+$"),
        re.compile(r"(?m)^[A-Z][A-Z0-9\s\-:]{6,}$"),
    ]

    def split(self, text: str, min_chapter_chars: int = 800) -> List[Chapter]:
        if not text or not text.strip():
            logger.warning("Chapter split requested with empty text")
            return []

        normalized_text = text.strip()
        candidates = self._detect_heading_candidates(normalized_text)
        if candidates:
            chapters = self._build_chapters_from_candidates(normalized_text, candidates, min_chapter_chars)
            if chapters:
                logger.info("Split text into %s chapters via heading heuristics", len(chapters))
                return chapters

        logger.info("No reliable headings detected; using fallback chapter segmentation")
        return self._fallback_split(normalized_text)

    def _detect_heading_candidates(self, text: str) -> List[Dict[str, Any]]:
        lines = text.splitlines(keepends=True)
        candidates: List[Dict[str, Any]] = []
        offset = 0

        for line in lines:
            line_stripped = line.strip()
            line_len = len(line)
            if not line_stripped:
                offset += line_len
                continue

            if self._looks_like_heading(line_stripped):
                candidates.append({"title": line_stripped, "start": offset})
            offset += line_len

        unique: List[Dict[str, Any]] = []
        seen_positions = set()
        for candidate in sorted(candidates, key=lambda item: item["start"]):
            if candidate["start"] in seen_positions:
                continue
            seen_positions.add(candidate["start"])
            unique.append(candidate)

        logger.debug("Detected %s heading candidates", len(unique))
        return unique

    def _looks_like_heading(self, line: str) -> bool:
        if len(line) > 120:
            return False
        return any(pattern.match(line) for pattern in self._HEADING_PATTERNS)

    def _build_chapters_from_candidates(
        self,
        text: str,
        candidates: List[Dict[str, Any]],
        min_chapter_chars: int,
    ) -> List[Chapter]:
        chapters: List[Chapter] = []

        # Ensure we capture preface/introduction content before first heading.
        if candidates and candidates[0]["start"] > min_chapter_chars:
            candidates = [{"title": "Introducción", "start": 0}] + candidates
        elif candidates and candidates[0]["start"] > 0:
            candidates = [{"title": candidates[0]["title"], "start": 0}] + candidates[1:]

        for i, candidate in enumerate(candidates):
            start = candidate["start"]
            end = candidates[i + 1]["start"] if i + 1 < len(candidates) else len(text)
            content = text[start:end].strip()
            if len(content) < max(150, min_chapter_chars // 5):
                logger.debug("Skipping tiny candidate chapter at span %s:%s", start, end)
                continue

            chapters.append(
                Chapter(
                    index=len(chapters) + 1,
                    title=self._normalize_title(candidate["title"], len(chapters) + 1),
                    content=content,
                    metadata={"heuristic": "heading", "start_char": start, "end_char": end},
                )
            )

        if len(chapters) <= 1:
            return []
        return chapters

    def _fallback_split(self, text: str, target_chars: int = 4500, overlap: int = 250) -> List[Chapter]:
        chapters: List[Chapter] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + target_chars, text_len)
            if end < text_len:
                boundary = text.rfind("\n\n", start, end)
                if boundary != -1 and boundary > start + (target_chars // 2):
                    end = boundary

            content = text[start:end].strip()
            if content:
                chapters.append(
                    Chapter(
                        index=len(chapters) + 1,
                        title=f"Capítulo {len(chapters) + 1}",
                        content=content,
                        metadata={"heuristic": "fallback", "start_char": start, "end_char": end},
                    )
                )

            if end >= text_len:
                break
            start = max(end - overlap, 0)

        logger.info("Fallback created %s chapters", len(chapters))
        return chapters

    def _normalize_title(self, raw_title: str, index: int) -> str:
        title = re.sub(r"\s+", " ", raw_title).strip("-: ")
        return title if title else f"Capítulo {index}"
