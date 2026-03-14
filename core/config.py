from __future__ import annotations

import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime configuration."""

    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    openai_temperature: float = Field(default=0.1)
    openai_max_output_tokens: int = Field(default=3500)
    data_dir: Path = Field(default=Path("data"))
    output_dir: Path = Field(default=Path("output"))
    log_level: str = Field(default="INFO")
    chunk_size: int = Field(default=1400)
    chunk_overlap: int = Field(default=200)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()


def configure_logging() -> None:
    """Configure app-level logging once."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_directories() -> None:
    """Create required runtime directories."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "pdfs").mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
