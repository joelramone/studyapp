from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from core.config import configure_logging, ensure_directories, settings
from core.orchestrator import StudyBrainOrchestrator

configure_logging()
ensure_directories()
logger = logging.getLogger(__name__)


st.set_page_config(page_title="study_brain", page_icon="🧠", layout="wide")
st.title("🧠 study_brain")
st.caption("Segundo cerebro técnico para estudiar documentación en PDF")

st.sidebar.header("Configuración")
st.sidebar.write(f"Modelo: `{settings.openai_model}`")
st.sidebar.write(f"Output: `{settings.output_dir}`")

uploaded_pdf = st.file_uploader("Sube un PDF técnico", type=["pdf"])

if uploaded_pdf:
    target_path = settings.data_dir / "pdfs" / uploaded_pdf.name
    target_path.write_bytes(uploaded_pdf.getbuffer())
    st.success(f"PDF guardado en: {target_path}")

    if st.button("Procesar PDF", type="primary"):
        orchestrator = StudyBrainOrchestrator()
        try:
            with st.spinner("Generando material de estudio..."):
                outputs = orchestrator.process_pdf(Path(target_path))
            st.success(f"Proceso completado. Capítulos procesados: {len(outputs)}")

            for out in outputs:
                with st.expander(f"Capítulo {out.chapter_index}", expanded=False):
                    st.markdown("### summary.md")
                    st.markdown(out.summary_md)

                    st.markdown("### concepts.json")
                    st.json([concept.model_dump() for concept in out.concepts])

                    st.markdown("### mindmap.md")
                    st.code(out.mindmap_md, language="markdown")

                    st.markdown("### flashcards.csv")
                    st.code(out.flashcards_csv, language="csv")

                    st.markdown("### exam_questions.md")
                    st.markdown(out.exam_questions_md)
        except Exception as exc:
            logger.exception("Error while processing PDF")
            st.error(f"Error al procesar PDF: {exc}")
else:
    st.info("Carga un PDF para comenzar.")
