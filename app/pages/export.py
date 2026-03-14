from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import csv
from io import StringIO

import streamlit as st

if __package__:
    from .utils import chapter_dir, list_processed_documents, read_text_if_exists, zip_folder_bytes
else:
    from app.pages.utils import chapter_dir, list_processed_documents, read_text_if_exists, zip_folder_bytes


def _get_document() -> dict | None:
    docs = list_processed_documents()
    if not docs:
        return None
    slug = st.session_state.get("selected_doc_slug")
    if slug:
        for doc in docs:
            if doc["slug"] == slug:
                return doc
    st.session_state["selected_doc_slug"] = docs[0]["slug"]
    return docs[0]


def _parse_csv(content: str) -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(content)))


def render() -> None:
    st.subheader("5) Export")
    st.write("Descarga resultados por documento/capítulo y exporta flashcards en CSV.")

    doc = _get_document()
    if not doc:
        st.info("No hay documentos procesados para exportar.")
        return

    chapter_indexes = [ch["index"] for ch in doc.get("chapters", [])]

    export_scope = st.radio("Ámbito", ["Documento completo", "Capítulo"], horizontal=True)
    selected_chapter = None
    folder = doc["path"]

    if export_scope == "Capítulo":
        if not chapter_indexes:
            st.warning("El documento no tiene capítulos.")
            return
        selected_chapter = st.selectbox("Capítulo", options=chapter_indexes)
        folder = chapter_dir(doc, selected_chapter)

    zip_bytes = zip_folder_bytes(folder)
    st.download_button(
        label="Descargar carpeta ZIP",
        data=zip_bytes,
        file_name=f"{folder.name}.zip",
        mime="application/zip",
        use_container_width=True,
    )

    st.markdown("### Exportar flashcards CSV")
    if export_scope == "Capítulo":
        csv_content = read_text_if_exists(folder / "flashcards.csv")
        if not csv_content:
            st.info("No hay flashcards en este capítulo.")
            return
        st.download_button(
            label="Descargar flashcards CSV",
            data=csv_content,
            file_name=f"{doc['slug']}_chapter_{selected_chapter:02d}_flashcards.csv",
            mime="text/csv",
            use_container_width=True,
        )
        return

    rows: list[dict[str, str]] = []
    for idx in chapter_indexes:
        ch_path = chapter_dir(doc, idx)
        csv_content = read_text_if_exists(ch_path / "flashcards.csv")
        if not csv_content.strip():
            continue
        for row in _parse_csv(csv_content):
            row["chapter"] = str(idx)
            rows.append(row)

    if not rows:
        st.info("No hay flashcards para consolidar en este documento.")
        return

    fieldnames = ["chapter", "front", "back", "tags", "difficulty"]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})

    st.download_button(
        label="Descargar flashcards CSV consolidado",
        data=buffer.getvalue(),
        file_name=f"{doc['slug']}_flashcards.csv",
        mime="text/csv",
        use_container_width=True,
    )
