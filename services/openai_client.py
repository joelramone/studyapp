from __future__ import annotations

import json
import logging
from typing import Any, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OpenAIClient:
    """Reusable OpenAI client for deterministic text/JSON generation with validation."""

    def __init__(self) -> None:
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_output_tokens = settings.openai_max_output_tokens
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def generate_text(self, *, system_prompt: str, user_content: str) -> str:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        response = self.client.responses.create(
            model=self.model,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        output = (response.output_text or "").strip()
        if not output:
            raise RuntimeError("OpenAI returned empty output")
        return output

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_content: str,
        response_model: type[T],
        max_attempts: int = 2,
    ) -> T:
        schema = json.dumps(response_model.model_json_schema(), ensure_ascii=False, indent=2)
        strict_prompt = (
            f"{system_prompt}\n\n"
            "Devuelve EXCLUSIVAMENTE JSON válido UTF-8. Sin markdown ni texto adicional.\n"
            f"Debes cumplir exactamente este JSON Schema:\n{schema}"
        )

        latest_error: Exception | None = None
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                raw_text = self.generate_text(system_prompt=strict_prompt, user_content=user_content)
                parsed = json.loads(raw_text)
                return response_model.model_validate(parsed)
            except Exception as exc:  # pragma: no cover - network/runtime
                latest_error = exc
                if attempt >= max_attempts:
                    break

                repair_prompt = (
                    "Tu salida anterior no cumplió formato. Corrígela. "
                    "Devuelve únicamente JSON válido y completo que respete el schema."
                )
                user_content = (
                    f"Entrada original:\n{user_content}\n\n"
                    f"Salida previa inválida:\n{raw_text}\n\n"
                    f"Error detectado:\n{type(exc).__name__}: {exc}\n\n"
                    f"{repair_prompt}"
                )

        logger.warning("Structured response generation failed after %s attempts", max_attempts)
        raise RuntimeError("Could not generate a valid structured response") from latest_error
