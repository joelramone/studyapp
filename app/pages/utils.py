from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from core.config import settings


def list_processed_documents() -> list[dict]:
    docs: list[dict] = []
    for doc_dir in sorted(settings.output_dir.glob("*")):
        if not doc_dir.is_dir():
            continue

        metadata_path = doc_dir / "metadata.json"
        chapters_path = doc_dir / "chapters_index.json"
        if not metadata_path.exists():
            continue

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        chapters = []
        if chapters_path.exists():
            chapters = json.loads(chapters_path.read_text(encoding="utf-8"))

        docs.append({"slug": doc_dir.name, "path": doc_dir, "metadata": metadata, "chapters": chapters})

    return docs


def chapter_dir(doc: dict, chapter_index: int) -> Path:
    return doc["path"] / f"chapter_{chapter_index:02d}"


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def zip_folder_bytes(folder: Path) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as zip_file:
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                zip_file.write(file_path, arcname=str(file_path.relative_to(folder.parent)))
    return stream.getvalue()
