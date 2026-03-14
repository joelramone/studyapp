from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Wrapper around OpenAI chat completion with safe fallback behavior."""

    def __init__(self) -> None:
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def generate_text(self, system_prompt: str, user_content: str) -> str:
        if not self.client:
            logger.warning("OPENAI_API_KEY not configured; returning local fallback text")
            return self.local_fallback(user_content)

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
            )
            return response.output_text.strip()
        except Exception as exc:  # pragma: no cover - external API
            logger.exception("OpenAI request failed")
            raise RuntimeError("OpenAI API call failed") from exc

    def generate_json(self, system_prompt: str, user_content: str) -> Any:
        text = self.generate_text(system_prompt, user_content)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Model did not return valid JSON; applying fallback JSON")
            return []

    def local_fallback(self, user_content: str) -> str:
        preview = user_content[:300].replace("\n", " ")
        return f"Fallback output generated without OpenAI API. Context: {preview}..."
