from __future__ import annotations

import json
import logging
import socket
from enum import Enum
from typing import Any, TypeVar

import httpx
from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OpenAIErrorCategory(str, Enum):
    DNS = "dns"
    CONNECTION = "connection"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    EMPTY_RESPONSE = "empty_response"
    STRUCTURED_OUTPUT = "structured_output"
    CONFIGURATION = "configuration"


class OpenAIServiceError(RuntimeError):
    def __init__(
        self,
        *,
        category: OpenAIErrorCategory,
        message: str,
        user_message: str,
        actionable_hint: str,
        retryable: bool,
        fallback_allowed: bool,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.user_message = user_message
        self.actionable_hint = actionable_hint
        self.retryable = retryable
        self.fallback_allowed = fallback_allowed
        self.cause = cause


class OpenAIHealthStatus(BaseModel):
    ok: bool
    category: OpenAIErrorCategory | None = None
    detail: str
    user_message: str
    actionable_hint: str


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
            raise OpenAIServiceError(
                category=OpenAIErrorCategory.CONFIGURATION,
                message="OPENAI_API_KEY is not configured",
                user_message="No hay clave de OpenAI configurada.",
                actionable_hint="Define OPENAI_API_KEY en tu archivo .env y reinicia la app.",
                retryable=False,
                fallback_allowed=True,
            )

        try:
            response = self.client.responses.create(
                model=self.model,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
            )
        except Exception as exc:  # pragma: no cover - network/runtime
            mapped_error = self._map_openai_exception(exc)
            logger.error(
                "OpenAI request failed | category=%s retryable=%s fallback_allowed=%s detail=%s",
                mapped_error.category.value,
                mapped_error.retryable,
                mapped_error.fallback_allowed,
                mapped_error,
            )
            raise mapped_error from exc

        output = (response.output_text or "").strip()
        if not output:
            raise OpenAIServiceError(
                category=OpenAIErrorCategory.EMPTY_RESPONSE,
                message="OpenAI returned empty output",
                user_message="OpenAI devolvió una respuesta vacía.",
                actionable_hint="Reintenta la ejecución. Si persiste, cambia de modelo o reduce el tamaño del capítulo.",
                retryable=True,
                fallback_allowed=True,
            )
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
            except OpenAIServiceError:
                raise
            except Exception as exc:  # pragma: no cover - parse/runtime
                latest_error = exc
                logger.warning(
                    "Structured generation parse/validation failed | attempt=%s/%s error=%s",
                    attempt,
                    max_attempts,
                    exc,
                )
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

        logger.error(
            "Structured response generation failed after %s attempts | last_error=%s",
            max_attempts,
            latest_error,
        )
        raise OpenAIServiceError(
            category=OpenAIErrorCategory.STRUCTURED_OUTPUT,
            message="Could not generate a valid structured response",
            user_message="No se pudo validar la salida estructurada del modelo.",
            actionable_hint="Reintenta. Si falla nuevamente, reduce el texto de entrada o ajusta el prompt.",
            retryable=True,
            fallback_allowed=True,
            cause=latest_error,
        ) from latest_error

    def health_check(self) -> OpenAIHealthStatus:
        if not self.client:
            return OpenAIHealthStatus(
                ok=False,
                category=OpenAIErrorCategory.CONFIGURATION,
                detail="OPENAI_API_KEY is not configured",
                user_message="No hay clave de OpenAI configurada.",
                actionable_hint="Define OPENAI_API_KEY en .env para habilitar el procesamiento con OpenAI.",
            )

        try:
            self.client.responses.create(
                model=self.model,
                max_output_tokens=16,
                input=[{"role": "user", "content": "Responde con OK"}],
            )
            return OpenAIHealthStatus(
                ok=True,
                detail="OpenAI connectivity check passed",
                user_message="Conectividad con OpenAI OK.",
                actionable_hint="",
            )
        except Exception as exc:  # pragma: no cover - network/runtime
            mapped_error = self._map_openai_exception(exc)
            return OpenAIHealthStatus(
                ok=False,
                category=mapped_error.category,
                detail=str(mapped_error),
                user_message=mapped_error.user_message,
                actionable_hint=mapped_error.actionable_hint,
            )

    def _map_openai_exception(self, exc: Exception) -> OpenAIServiceError:
        if isinstance(exc, AuthenticationError):
            return OpenAIServiceError(
                category=OpenAIErrorCategory.AUTHENTICATION,
                message=f"OpenAI authentication failed: {exc}",
                user_message="Autenticación con OpenAI fallida.",
                actionable_hint="Verifica OPENAI_API_KEY y que la clave esté activa en tu cuenta.",
                retryable=False,
                fallback_allowed=True,
                cause=exc,
            )

        if isinstance(exc, APITimeoutError):
            return OpenAIServiceError(
                category=OpenAIErrorCategory.TIMEOUT,
                message=f"OpenAI request timeout: {exc}",
                user_message="OpenAI no respondió a tiempo (timeout).",
                actionable_hint="Reintenta. Revisa latencia de red, proxy y firewall.",
                retryable=True,
                fallback_allowed=True,
                cause=exc,
            )

        if isinstance(exc, APIConnectionError):
            dns_related = self._is_dns_error(exc)
            if dns_related:
                return OpenAIServiceError(
                    category=OpenAIErrorCategory.DNS,
                    message=f"OpenAI DNS resolution failed: {exc}",
                    user_message="No se pudo resolver el dominio de OpenAI (DNS).",
                    actionable_hint="Revisa DNS del sistema, configuración corporativa/proxy y conectividad a internet.",
                    retryable=True,
                    fallback_allowed=True,
                    cause=exc,
                )
            return OpenAIServiceError(
                category=OpenAIErrorCategory.CONNECTION,
                message=f"OpenAI connection error: {exc}",
                user_message="No se pudo establecer conexión con OpenAI.",
                actionable_hint="Verifica proxy, firewall y acceso saliente HTTPS al endpoint de OpenAI.",
                retryable=True,
                fallback_allowed=True,
                cause=exc,
            )

        if isinstance(exc, httpx.TimeoutException):
            return OpenAIServiceError(
                category=OpenAIErrorCategory.TIMEOUT,
                message=f"HTTP timeout calling OpenAI: {exc}",
                user_message="La llamada HTTP a OpenAI excedió el timeout.",
                actionable_hint="Reintenta y verifica red/proxy/firewall.",
                retryable=True,
                fallback_allowed=True,
                cause=exc,
            )

        if self._is_dns_error(exc):
            return OpenAIServiceError(
                category=OpenAIErrorCategory.DNS,
                message=f"DNS resolution failure when calling OpenAI: {exc}",
                user_message="Error de DNS al conectar con OpenAI.",
                actionable_hint="Configura DNS válido (por ejemplo 8.8.8.8 / 1.1.1.1) o revisa resolución interna.",
                retryable=True,
                fallback_allowed=True,
                cause=exc,
            )

        return OpenAIServiceError(
            category=OpenAIErrorCategory.CONNECTION,
            message=f"Unexpected OpenAI connectivity error: {exc}",
            user_message="Error de conectividad al usar OpenAI.",
            actionable_hint="Revisa red, proxy y firewall; luego reintenta.",
            retryable=True,
            fallback_allowed=True,
            cause=exc,
        )

    @staticmethod
    def _is_dns_error(exc: Exception) -> bool:
        if isinstance(exc, socket.gaierror):
            return True

        current: Exception | None = exc
        visited: set[int] = set()
        while current is not None and id(current) not in visited:
            visited.add(id(current))
            message = str(current).lower()
            if "getaddrinfo" in message or "name or service not known" in message:
                return True
            if isinstance(current, socket.gaierror):
                return True

            next_exc: Exception | None = None
            if current.__cause__ and isinstance(current.__cause__, Exception):
                next_exc = current.__cause__
            elif current.__context__ and isinstance(current.__context__, Exception):
                next_exc = current.__context__
            current = next_exc

        return False
