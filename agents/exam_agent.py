from __future__ import annotations

from agents.base_agent import BaseAgent
from prompts.templates import EXAM_PROMPT


class ExamAgent(BaseAgent):
    def run(self, chapter_text: str) -> str:
        return self.generate_text(EXAM_PROMPT, chapter_text)
