from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import csv
import json
from io import StringIO

import streamlit as st

if __package__:
    from .utils import chapter_dir, list_processed_documents, read_text_if_exists
else:
    from app.pages.utils import chapter_dir, list_processed_documents, read_text_if_exists


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


def _json_view(path: Path) -> None:
    if not path.exists():
        st.info("Sin contenido generado todavía.")
        return
    st.json(json.loads(path.read_text(encoding="utf-8")))


def _csv_table(content: str) -> list[dict]:
    reader = csv.DictReader(StringIO(content))
    return list(reader)


def render() -> None:
    st.subheader("4) Results")
    st.write("Consulta contenido generado por capítulo.")

    doc = _get_document()
    if not doc:
        st.info("No hay resultados. Procesa un documento primero.")
        return

    chapters = [ch["index"] for ch in doc.get("chapters", [])]
    if not chapters:
        st.warning("No hay capítulos para mostrar resultados.")
        return

    selected = st.selectbox(
        "Capítulo",
        options=chapters,
        index=0 if st.session_state.get("selected_chapter_index") not in chapters else chapters.index(st.session_state["selected_chapter_index"]),
        key="results_chapter",
    )
    st.session_state["selected_chapter_index"] = selected
    ch_dir = chapter_dir(doc, selected)

    tabs = st.tabs(["Summary", "Concepts", "Architecture", "Mindmap", "Flashcards", "Exam"])

    with tabs[0]:
        summary = read_text_if_exists(ch_dir / "summary.md")
        if summary:
            st.markdown(summary)
        else:
            st.info("No hay summary generado.")

    with tabs[1]:
        _json_view(ch_dir / "concepts.json")

    with tabs[2]:
        _json_view(ch_dir / "architecture.json")

    with tabs[3]:
        mindmap_md = read_text_if_exists(ch_dir / "mindmap.md")
        mindmap_mmd = read_text_if_exists(ch_dir / "mindmap.mmd")
        if mindmap_md:
            st.markdown(mindmap_md)
        else:
            st.info("No hay mindmap markdown generado.")
        if mindmap_mmd:
            st.markdown("#### Mermaid")
            st.code(mindmap_mmd, language="mermaid")

    with tabs[4]:
        csv_content = read_text_if_exists(ch_dir / "flashcards.csv")
        if csv_content:
            rows = _csv_table(csv_content)
            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("CSV generado sin filas de flashcards.")
            st.code(csv_content, language="csv")
        else:
            st.info("No hay flashcards generadas.")

    with tabs[5]:
        exam = read_text_if_exists(ch_dir / "exam_questions.md")
        if exam:
            st.markdown(exam)
        else:
            st.info("No hay examen generado.")
