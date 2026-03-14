from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_safe_slug(value: str) -> str:
    return "-".join(value.strip().lower().split())


class DomainModel(BaseModel):
    """Shared base model with JSON-friendly defaults for persistence."""

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        ser_json_timedelta="iso8601",
        json_encoders={Path: str},
    )


class TimestampedModel(DomainModel):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSED = "processed"
    ARCHIVED = "archived"


class DocumentInputMode(str, Enum):
    PDF = "pdf"
    NOTES = "notes"


class AgentType(str, Enum):
    CONCEPT = "concept"
    ARCHITECTURE = "architecture"
    FLASHCARD = "flashcard"
    EXAM = "exam"
    MINDMAP = "mindmap"


class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ComponentType(str, Enum):
    SERVICE = "service"
    DATABASE = "database"
    QUEUE = "queue"
    API = "api"
    WORKER = "worker"
    EXTERNAL = "external"
    UI = "ui"
    OTHER = "other"


class RelationshipType(str, Enum):
    DEPENDS_ON = "depends_on"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    PUBLISHES_TO = "publishes_to"
    SUBSCRIBES_TO = "subscribes_to"
    CALLS = "calls"
    CONTAINS = "contains"
    OTHER = "other"


class ExamQuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class MindmapNodeType(str, Enum):
    ROOT = "root"
    TOPIC = "topic"
    SUBTOPIC = "subtopic"
    DETAIL = "detail"


class ChunkType(str, Enum):
    TEXT = "text"
    CODE = "code"
    TABLE = "table"
    OTHER = "other"


class Chapter(TimestampedModel):
    id: str = Field(default_factory=lambda: f"ch_{uuid4().hex}")
    document_id: Optional[str] = None
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1)
    index: int = Field(ge=1)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()


class Chunk(TimestampedModel):
    id: str = Field(default_factory=lambda: f"chunk_{uuid4().hex}")
    chapter_id: str
    index: int = Field(ge=1)
    text: str = Field(min_length=1)
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=1)
    chunk_type: ChunkType = ChunkType.TEXT
    token_estimate: Optional[int] = Field(default=None, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_span(self) -> "Chunk":
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be greater than start_char")
        return self


class Document(TimestampedModel):
    id: str = Field(default_factory=lambda: f"doc_{uuid4().hex}")
    source_path: Path
    title: str = Field(min_length=1, max_length=400)
    slug: Optional[str] = None
    raw_text: str = Field(min_length=1)
    language: str = Field(default="es", min_length=2, max_length=10)
    input_mode: DocumentInputMode = DocumentInputMode.PDF
    status: DocumentStatus = DocumentStatus.DRAFT
    chapters: List[Chapter] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def sync_slug_and_chapters(self) -> "Document":
        if not self.slug:
            self.slug = _to_safe_slug(self.title)
        for chapter in self.chapters:
            if not chapter.document_id:
                chapter.document_id = self.id
        return self


class AgentRun(TimestampedModel):
    id: str = Field(default_factory=lambda: f"run_{uuid4().hex}")
    agent: AgentType
    status: AgentRunStatus = AgentRunStatus.PENDING
    document_id: Optional[str] = None
    chapter_id: Optional[str] = None
    input_hash: Optional[str] = None
    output_schema_version: str = "1.0"
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = Field(default=None, ge=0)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_completion_consistency(self) -> "AgentRun":
        if self.status == AgentRunStatus.COMPLETED and not self.finished_at:
            self.finished_at = utc_now()
        if self.status == AgentRunStatus.FAILED and not self.error_message:
            raise ValueError("error_message is required when status is failed")
        if self.finished_at and self.duration_ms is None:
            delta = self.finished_at - self.started_at
            self.duration_ms = max(int(delta.total_seconds() * 1000), 0)
        return self


class ConceptItem(TimestampedModel):
    id: str = Field(default_factory=lambda: f"concept_{uuid4().hex}")
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    prerequisites: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("tags", "aliases", "prerequisites")
    @classmethod
    def normalize_string_lists(cls, values: List[str]) -> List[str]:
        deduped: List[str] = []
        seen: set[str] = set()
        for value in values:
            cleaned = value.strip()
            key = cleaned.lower()
            if cleaned and key not in seen:
                seen.add(key)
                deduped.append(cleaned)
        return deduped


class ArchitectureComponent(TimestampedModel):
    id: str = Field(default_factory=lambda: f"cmp_{uuid4().hex}")
    name: str = Field(min_length=1, max_length=200)
    component_type: ComponentType = ComponentType.OTHER
    description: str = Field(min_length=1)
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Relationship(TimestampedModel):
    id: str = Field(default_factory=lambda: f"rel_{uuid4().hex}")
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    relationship_type: RelationshipType = RelationshipType.OTHER
    label: Optional[str] = Field(default=None, max_length=160)
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_nodes(self) -> "Relationship":
        if self.source_id == self.target_id:
            raise ValueError("source_id and target_id must be different")
        return self


class Flashcard(TimestampedModel):
    id: str = Field(default_factory=lambda: f"fc_{uuid4().hex}")
    front: str = Field(min_length=1)
    back: str = Field(min_length=1)
    difficulty: Difficulty = Difficulty.MEDIUM
    tags: List[str] = Field(default_factory=list)
    source_chunk_ids: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExamQuestion(TimestampedModel):
    id: str = Field(default_factory=lambda: f"q_{uuid4().hex}")
    prompt: str = Field(min_length=1)
    question_type: ExamQuestionType = ExamQuestionType.SHORT_ANSWER
    choices: List[str] = Field(default_factory=list)
    correct_answer: str = Field(min_length=1)
    explanation: Optional[str] = None
    difficulty: Difficulty = Difficulty.MEDIUM
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_question_payload(self) -> "ExamQuestion":
        if self.question_type == ExamQuestionType.MULTIPLE_CHOICE and len(self.choices) < 2:
            raise ValueError("multiple_choice questions require at least 2 choices")
        if self.question_type == ExamQuestionType.TRUE_FALSE:
            normalized = self.correct_answer.strip().lower()
            if normalized not in {"true", "false", "verdadero", "falso"}:
                raise ValueError("true_false questions require a boolean correct_answer")
        return self


class MindmapNode(TimestampedModel):
    id: str = Field(default_factory=lambda: f"node_{uuid4().hex}")
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    node_type: MindmapNodeType = MindmapNodeType.TOPIC
    children: List["MindmapNode"] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("children")
    @classmethod
    def children_limit(cls, children: List["MindmapNode"]) -> List["MindmapNode"]:
        if len(children) > 100:
            raise ValueError("mindmap nodes cannot have more than 100 direct children")
        return children


# Backward-compatible aliases used in current agents/orchestrator.
Concept = ConceptItem


class AgentOutput(DomainModel):
    chapter_index: int = Field(ge=1)
    summary_md: str
    concepts: List[ConceptItem]
    mindmap_md: str
    flashcards_csv: str
    exam_questions_md: str


def to_pretty_json(model: BaseModel) -> str:
    return model.model_dump_json(indent=2)


def dump_json_file(data: BaseModel | Dict[str, Any] | List[Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json_file(path: Path) -> Dict[str, Any] | List[Any]:
    return json.loads(path.read_text(encoding="utf-8"))
