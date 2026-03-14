from __future__ import annotations

from agents.base_agent import BaseAgent
from prompts.templates import SUMMARY_PROMPT


class ArchitectureAgent(BaseAgent):
    """Generates chapter summary markdown."""

    def run(self, chapter_text: str) -> str:
        return self.generate_text(SUMMARY_PROMPT, chapter_text)
