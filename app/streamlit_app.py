from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import logging

import streamlit as st

from app.pages import documents, export, process, results, upload
from core.config import configure_logging, ensure_directories, settings

configure_logging()
ensure_directories()
logger = logging.getLogger(__name__)


st.set_page_config(page_title="study_brain", page_icon="🧠", layout="wide")


def _init_session_state() -> None:
    st.session_state.setdefault("uploaded_files", [])
    st.session_state.setdefault("selected_doc_slug", None)
    st.session_state.setdefault("selected_chapter_index", None)
    st.session_state.setdefault(
        "selected_outputs",
        {
            "architecture": True,
            "concepts": True,
            "mindmap": True,
            "flashcards": True,
            "exam": True,
        },
    )


def _sidebar() -> str:
    st.sidebar.header("study_brain")
    st.sidebar.caption("Segundo cerebro técnico para estudiar desde PDFs o Notes")
    st.sidebar.divider()
    st.sidebar.write(f"Modelo: `{settings.openai_model}`")
    st.sidebar.write(f"Input PDFs: `{settings.data_dir / 'pdfs'}`")
    st.sidebar.write(f"Output: `{settings.output_dir}`")
    st.sidebar.divider()
    return st.sidebar.radio(
        "Navegación",
        options=["Upload", "Documents", "Process", "Results", "Export"],
        key="active_page",
    )


def main() -> None:
    _init_session_state()
    st.title("🧠 study_brain")

    page = _sidebar()

    if page == "Upload":
        upload.render()
    elif page == "Documents":
        documents.render()
    elif page == "Process":
        process.render()
    elif page == "Results":
        results.render()
    elif page == "Export":
        export.render()
    else:
        logger.error("Unknown page selected: %s", page)
        st.error("Página desconocida")


if __name__ == "__main__":
    main()
