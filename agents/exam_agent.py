from __future__ import annotations

from pathlib import Path

from agents.base_agent import BaseAgent
from core.schemas import ExamAgentResponse
from prompts.templates import EXAM_PROMPT


class ExamAgent(BaseAgent):
    output_name = "exam"

    def run(self, chapter_text: str, output_dir: Path | None = None) -> ExamAgentResponse:
        result = self.generate_structured(
            prompt=EXAM_PROMPT,
            chapter_text=chapter_text,
            response_model=ExamAgentResponse,
        )
        if output_dir:
            self.save_json_output(result, output_dir)
            markdown = self._to_markdown(result)
            self.save_text_output(markdown, output_dir, filename="exam_questions.md")
        return result

    def _to_markdown(self, response: ExamAgentResponse) -> str:
        sections: list[tuple[str, list]] = [
            ("Multiple Choice", response.multiple_choice),
            ("Short Answer", response.short_answer),
            ("Scenario Based", response.scenario_based),
        ]
        lines = ["# Exam Questions", ""]
        for title, items in sections:
            lines.append(f"## {title}")
            if not items:
                lines.append("- (sin preguntas)")
                lines.append("")
                continue
            for idx, q in enumerate(items, start=1):
                lines.append(f"{idx}. **{q.prompt}**")
                if q.choices:
                    for choice in q.choices:
                        lines.append(f"   - {choice}")
                lines.append(f"   - Respuesta: {q.correct_answer}")
                if q.explanation:
                    lines.append(f"   - Justificación: {q.explanation}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def fallback(self, chapter_text: str, response_model: type[ExamAgentResponse]) -> ExamAgentResponse:
        preview = chapter_text[:140].replace("\n", " ").strip()
        return response_model(
            multiple_choice=[
                {
                    "prompt": "¿Qué configuración habilita la generación real de exámenes?",
                    "question_type": "multiple_choice",
                    "choices": ["OPENAI_API_KEY", "CHUNK_SIZE", "LOG_LEVEL"],
                    "correct_answer": "OPENAI_API_KEY",
                    "explanation": "Sin API key no se invoca el modelo remoto.",
                    "difficulty": "easy",
                    "tags": ["setup"],
                }
            ],
            short_answer=[
                {
                    "prompt": "Explica en una frase el propósito de este capítulo.",
                    "question_type": "short_answer",
                    "correct_answer": preview or "No hay contenido suficiente.",
                    "explanation": "Resumen mínimo basado en entrada local.",
                    "difficulty": "medium",
                }
            ],
            scenario_based=[
                {
                    "prompt": "Escenario: el output JSON llega incompleto. ¿Qué estrategia aplica este agente?",
                    "question_type": "short_answer",
                    "correct_answer": "Reintenta con prompt de reparación y valida con Pydantic.",
                    "explanation": "Se aplica fallback de corrección en la capa cliente.",
                    "difficulty": "medium",
                    "tags": ["resiliencia", "validación"],
                }
            ],
        )
