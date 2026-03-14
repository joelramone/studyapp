from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LocalStorage:
    """Persist chapter outputs as local files."""

    def __init__(self, base_output_dir: Path) -> None:
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def chapter_dir(self, document_name: str, chapter_index: int) -> Path:
        safe_doc = document_name.replace(" ", "_")
        path = self.base_output_dir / safe_doc / f"chapter_{chapter_index:02d}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_text(self, path: Path, content: str) -> None:
        logger.info("Saving text file: %s", path)
        path.write_text(content, encoding="utf-8")

    def save_json(self, path: Path, payload: Any) -> None:
        logger.info("Saving JSON file: %s", path)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
