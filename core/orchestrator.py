from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from agents.architecture_agent import ArchitectureAgent
from agents.concept_agent import ConceptAgent
from agents.exam_agent import ExamAgent
from agents.flashcard_agent import FlashcardAgent
from agents.mindmap_agent import MindmapAgent
from core.config import settings
from core.models import AgentOutput, Chapter, Document
from services.chapter_splitter import ChapterSplitter
from services.chunker import TextChunker
from services.pdf_reader import PDFReader
from services.storage import LocalStorage

logger = logging.getLogger(__name__)


class StudyBrainOrchestrator:
    """Coordinates reading, chapter segmentation, agent generation and storage."""

    def __init__(self) -> None:
        self.reader = PDFReader()
        self.splitter = ChapterSplitter()
        self.chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)
        self.storage = LocalStorage(settings.output_dir)

        self.summary_agent = ArchitectureAgent()
        self.concept_agent = ConceptAgent()
        self.mindmap_agent = MindmapAgent()
        self.flashcard_agent = FlashcardAgent()
        self.exam_agent = ExamAgent()

    def process_pdf(self, pdf_path: Path) -> List[AgentOutput]:
        raw_text = self.reader.read(pdf_path)
        chapters = self.splitter.split(raw_text)
        document = Document(source_path=pdf_path, title=pdf_path.stem, raw_text=raw_text, chapters=chapters)

        outputs: List[AgentOutput] = []
        for chapter in document.chapters:
            outputs.append(self._process_chapter(document.title, chapter))
        return outputs

    def _process_chapter(self, document_title: str, chapter: Chapter) -> AgentOutput:
        logger.info("Processing chapter %s: %s", chapter.index, chapter.title)
        chapter_context = "\n\n".join(self.chunker.chunk(chapter.content)[:3]) or chapter.content

        summary_md = self.summary_agent.run(chapter_context)
        concepts = self.concept_agent.run(chapter_context)
        mindmap_md = self.mindmap_agent.run(chapter_context)
        flashcards_csv = self.flashcard_agent.run(chapter_context)
        exam_questions_md = self.exam_agent.run(chapter_context)

        output = AgentOutput(
            chapter_index=chapter.index,
            summary_md=summary_md,
            concepts=concepts,
            mindmap_md=mindmap_md,
            flashcards_csv=flashcards_csv,
            exam_questions_md=exam_questions_md,
        )
        self._persist(document_title, output)
        return output

    def _persist(self, document_title: str, output: AgentOutput) -> None:
        chapter_dir = self.storage.chapter_dir(document_title, output.chapter_index)
        self.storage.save_text(chapter_dir / "summary.md", output.summary_md)
        self.storage.save_json(
            chapter_dir / "concepts.json",
            [concept.model_dump() for concept in output.concepts],
        )
        self.storage.save_text(chapter_dir / "mindmap.md", output.mindmap_md)
        self.storage.save_text(chapter_dir / "flashcards.csv", output.flashcards_csv)
        self.storage.save_text(chapter_dir / "exam_questions.md", output.exam_questions_md)
