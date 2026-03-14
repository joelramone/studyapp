from __future__ import annotations

import logging
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from core.models import dump_json_file
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    """Shared behavior for OpenAI-backed agents with validated outputs."""

    output_name: str = "output"

    def __init__(self) -> None:
        self.openai = OpenAIClient()

    def generate_structured(self, *, prompt: str, chapter_text: str, response_model: type[T]) -> T:
        if self.openai.enabled:
            return self.openai.generate_structured(
                system_prompt=prompt,
                user_content=chapter_text,
                response_model=response_model,
                max_attempts=2,
            )

        logger.warning("OPENAI_API_KEY not configured; using deterministic local fallback")
        return self.fallback(chapter_text, response_model)

    def fallback(self, chapter_text: str, response_model: type[T]) -> T:
        raise NotImplementedError

    def save_json_output(self, output: BaseModel, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{self.output_name}.json"
        dump_json_file(output, path)
        return path

    def save_text_output(self, content: str, output_dir: Path, *, filename: str) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        return path
