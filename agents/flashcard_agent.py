from __future__ import annotations

from agents.base_agent import BaseAgent
from prompts.templates import FLASHCARD_PROMPT


class FlashcardAgent(BaseAgent):
    def run(self, chapter_text: str) -> str:
        output = self.generate_text(FLASHCARD_PROMPT, chapter_text)
        if output.startswith("Fallback output"):
            return "question,answer,difficulty\nWhat is this chapter about?,Set OPENAI_API_KEY to generate flashcards,easy"
        return output
