from __future__ import annotations

from typing import List

from agents.base_agent import BaseAgent
from core.models import Concept
from prompts.templates import CONCEPT_PROMPT


class ConceptAgent(BaseAgent):
    def run(self, chapter_text: str) -> List[Concept]:
        payload = self.generate_json(CONCEPT_PROMPT, chapter_text)
        concepts: List[Concept] = []
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    concepts.append(
                        Concept(
                            name=str(item.get("name", "Unnamed concept")),
                            description=str(item.get("description", "")),
                            tags=[str(tag) for tag in item.get("tags", [])],
                        )
                    )
        if concepts:
            return concepts
        return [
            Concept(
                name="Concept extraction unavailable",
                description="Configure OPENAI_API_KEY to generate rich concepts.",
                tags=["fallback"],
            )
        ]
