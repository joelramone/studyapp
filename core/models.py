from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    title: str
    content: str
    index: int


class Document(BaseModel):
    source_path: Path
    title: str
    raw_text: str
    chapters: List[Chapter] = Field(default_factory=list)


class Concept(BaseModel):
    name: str
    description: str
    tags: List[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    chapter_index: int
    summary_md: str
    concepts: List[Concept]
    mindmap_md: str
    flashcards_csv: str
    exam_questions_md: str
