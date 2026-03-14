from __future__ import annotations

from agents.base_agent import BaseAgent
from prompts.templates import MINDMAP_PROMPT


class MindmapAgent(BaseAgent):
    def run(self, chapter_text: str) -> str:
        return self.generate_text(MINDMAP_PROMPT, chapter_text)
