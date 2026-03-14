from __future__ import annotations

from pathlib import Path

from agents.base_agent import BaseAgent
from core.schemas import ConceptAgentResponse
from prompts.templates import CONCEPT_PROMPT


class ConceptAgent(BaseAgent):
    output_name = "concepts"

    def run(self, chapter_text: str, output_dir: Path | None = None) -> ConceptAgentResponse:
        result = self.generate_structured(
            prompt=CONCEPT_PROMPT,
            chapter_text=chapter_text,
            response_model=ConceptAgentResponse,
        )
        if output_dir:
            self.save_json_output(result, output_dir)
        return result

    def fallback(self, chapter_text: str, response_model: type[ConceptAgentResponse]) -> ConceptAgentResponse:
        preview = chapter_text[:400].replace("\n", " ").strip() or "Contenido no disponible"
        return response_model(
            summary="Fallback local: configura OPENAI_API_KEY para extracción completa.",
            concepts=[
                {
                    "name": "Capítulo sin análisis remoto",
                    "description": preview,
                    "tags": ["fallback", "setup"],
                }
            ],
            definitions=[
                {
                    "term": "OPENAI_API_KEY",
                    "definition": "Variable requerida para habilitar análisis real con modelos OpenAI.",
                }
            ],
            relationships=[
                {
                    "source_term": "OPENAI_API_KEY",
                    "target_term": "Análisis de conceptos",
                    "relation": "habilita",
                    "explanation": "Sin API key, solo se genera salida local mínima.",
                }
            ],
            tags=["fallback", "configuración"],
        )
