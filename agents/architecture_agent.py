from __future__ import annotations

from pathlib import Path

from agents.base_agent import BaseAgent
from core.schemas import ArchitectureAgentResponse
from prompts.templates import ARCHITECTURE_PROMPT


class ArchitectureAgent(BaseAgent):
    output_name = "architecture"

    def run(self, chapter_text: str, output_dir: Path | None = None) -> ArchitectureAgentResponse:
        result = self.generate_structured(
            prompt=ARCHITECTURE_PROMPT,
            chapter_text=chapter_text,
            response_model=ArchitectureAgentResponse,
        )
        if output_dir:
            self.save_json_output(result, output_dir)
            self.save_text_output(result.summary_md, output_dir, filename="summary.md")
        return result

    def fallback(self, chapter_text: str, response_model: type[ArchitectureAgentResponse]) -> ArchitectureAgentResponse:
        preview = chapter_text[:280].replace("\n", " ").strip() or "Contenido no disponible"
        return response_model(
            summary_md=(
                "## Resumen de arquitectura (fallback)\n"
                "No se pudo consultar OpenAI. Configura OPENAI_API_KEY para análisis detallado.\n\n"
                f"Contexto detectado: {preview}"
            ),
            components=[
                {
                    "id": "cmp_input",
                    "name": "Entrada del capítulo",
                    "component_type": "other",
                    "description": "Texto fuente a analizar.",
                    "responsibilities": ["Aportar contexto"],
                }
            ],
            relationships=[],
            flow_steps=[
                {
                    "order": 1,
                    "title": "Cargar contexto",
                    "description": "Se utiliza el texto del capítulo como única fuente.",
                    "component_ids": ["cmp_input"],
                }
            ],
            use_cases=["Inicializar integración OpenAI"],
            common_errors=["OPENAI_API_KEY ausente o inválida"],
        )
