from __future__ import annotations

from pathlib import Path

from agents.base_agent import BaseAgent
from core.schemas import FlashcardAgentResponse
from prompts.templates import FLASHCARD_PROMPT


class FlashcardAgent(BaseAgent):
    output_name = "flashcards"

    def run(self, chapter_text: str, output_dir: Path | None = None) -> FlashcardAgentResponse:
        result = self.generate_structured(
            prompt=FLASHCARD_PROMPT,
            chapter_text=chapter_text,
            response_model=FlashcardAgentResponse,
        )
        if output_dir:
            self.save_json_output(result, output_dir)
            self.save_text_output(result.to_csv(), output_dir, filename="flashcards.csv")
        return result

    def fallback(self, chapter_text: str, response_model: type[FlashcardAgentResponse]) -> FlashcardAgentResponse:
        preview = chapter_text[:180].replace("\n", " ").strip()
        return response_model(
            flashcards=[
                {
                    "front": "¿Qué falta para generar flashcards reales?",
                    "back": "Configurar OPENAI_API_KEY y reintentar.",
                    "tags": ["fallback", "setup"],
                    "difficulty": "easy",
                    "explanation": f"Contexto detectado: {preview}",
                }
            ]
        )
