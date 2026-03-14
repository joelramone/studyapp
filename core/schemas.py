from __future__ import annotations

import csv
from io import StringIO
from typing import List

from pydantic import Field, model_validator

from core.models import (
    ArchitectureComponent,
    ConceptItem,
    DomainModel,
    ExamQuestion,
    Flashcard,
    MindmapNode,
    Relationship,
    utc_now,
)


class ConceptAgentResponse(DomainModel):
    schema_version: str = "1.0"
    generated_at: str = Field(default_factory=lambda: utc_now().isoformat())
    concepts: List[ConceptItem] = Field(default_factory=list)


class ArchitectureFlowStep(DomainModel):
    order: int = Field(ge=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    component_ids: List[str] = Field(default_factory=list)


class ArchitectureAgentResponse(DomainModel):
    schema_version: str = "1.0"
    generated_at: str = Field(default_factory=lambda: utc_now().isoformat())
    summary_md: str = ""
    components: List[ArchitectureComponent] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    flow_steps: List[ArchitectureFlowStep] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_flow_order(self) -> "ArchitectureAgentResponse":
        if self.flow_steps:
            expected = list(range(1, len(self.flow_steps) + 1))
            current = [step.order for step in self.flow_steps]
            if expected != current:
                raise ValueError("flow_steps.order must be sequential starting at 1")
        return self


class FlashcardAgentResponse(DomainModel):
    schema_version: str = "1.0"
    generated_at: str = Field(default_factory=lambda: utc_now().isoformat())
    flashcards: List[Flashcard] = Field(default_factory=list)

    def to_csv(self) -> str:
        stream = StringIO()
        writer = csv.writer(stream)
        writer.writerow(["id", "front", "back", "difficulty", "tags", "explanation"])
        for item in self.flashcards:
            writer.writerow(
                [
                    item.id,
                    item.front,
                    item.back,
                    item.difficulty,
                    "|".join(item.tags),
                    item.explanation or "",
                ]
            )
        return stream.getvalue()


class ExamAgentResponse(DomainModel):
    schema_version: str = "1.0"
    generated_at: str = Field(default_factory=lambda: utc_now().isoformat())
    questions: List[ExamQuestion] = Field(default_factory=list)


class MindmapAgentResponse(DomainModel):
    schema_version: str = "1.0"
    generated_at: str = Field(default_factory=lambda: utc_now().isoformat())
    root: MindmapNode
    markdown: str = ""

    def as_markdown(self) -> str:
        if self.markdown:
            return self.markdown

        lines: List[str] = []

        def walk(node: MindmapNode, depth: int = 0) -> None:
            lines.append(f"{'  ' * depth}- {node.title}")
            for child in node.children:
                walk(child, depth + 1)

        walk(self.root)
        return "\n".join(lines)
