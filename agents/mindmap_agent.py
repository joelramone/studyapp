from __future__ import annotations

from pathlib import Path

from agents.base_agent import BaseAgent
from core.schemas import MindmapAgentResponse
from prompts.templates import MINDMAP_PROMPT


class MindmapAgent(BaseAgent):
    output_name = "mindmap"

    def run(self, chapter_text: str, output_dir: Path | None = None) -> MindmapAgentResponse:
        result = self.generate_structured(
            prompt=MINDMAP_PROMPT,
            chapter_text=chapter_text,
            response_model=MindmapAgentResponse,
        )
        if output_dir:
            self.save_json_output(result, output_dir)
            self.save_text_output(result.as_markdown(), output_dir, filename="mindmap.md")
            if result.mermaid.strip():
                self.save_text_output(result.mermaid, output_dir, filename="mindmap.mmd")
        return result

    def fallback(self, chapter_text: str, response_model: type[MindmapAgentResponse]) -> MindmapAgentResponse:
        preview = chapter_text[:120].replace("\n", " ").strip() or "Capítulo"
        markdown = f"- {preview}\n  - Configurar OPENAI_API_KEY\n  - Reintentar generación"
        mermaid = (
            "mindmap\n"
            "  root((Fallback))\n"
            "    Configurar_OPENAI_API_KEY\n"
            "    Reintentar_generacion"
        )
        return response_model(
            root={
                "title": preview,
                "node_type": "root",
                "children": [
                    {"title": "Configurar OPENAI_API_KEY", "node_type": "topic"},
                    {"title": "Reintentar generación", "node_type": "topic"},
                ],
            },
            markdown=markdown,
            mermaid=mermaid,
        )
