from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8").strip()


CONCEPT_PROMPT = load_prompt("concept_prompt.md")
ARCHITECTURE_PROMPT = load_prompt("architecture_prompt.md")
MINDMAP_PROMPT = load_prompt("mindmap_prompt.md")
FLASHCARD_PROMPT = load_prompt("flashcard_prompt.md")
EXAM_PROMPT = load_prompt("exam_prompt.md")
