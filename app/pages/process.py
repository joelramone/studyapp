from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import traceback

import streamlit as st

from agents.architecture_agent import ArchitectureAgent
from agents.concept_agent import ConceptAgent
from agents.exam_agent import ExamAgent
from agents.flashcard_agent import FlashcardAgent
from agents.mindmap_agent import MindmapAgent
from services.openai_client import OpenAIClient, OpenAIServiceError
if __package__:
    from .utils import chapter_dir, list_processed_documents, read_text_if_exists
else:
    from app.pages.utils import chapter_dir, list_processed_documents, read_text_if_exists


OUTPUT_LABELS = {
    "architecture": "architecture",
    "concepts": "concepts",
    "mindmap": "mindmap",
    "flashcards": "flashcards",
    "exam": "exam questions",
}


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


def _run_for_chapter(chapter_path: Path, selected_outputs: dict[str, bool]) -> list[str]:
    content = read_text_if_exists(chapter_path / "source.md")
    if not content.strip():
        raise RuntimeError(f"No se encontró texto fuente en {chapter_path / 'source.md'}")

    generated: list[str] = []

    if selected_outputs.get("architecture"):
        architecture = ArchitectureAgent().run(content, chapter_path)
        (chapter_path / "summary.md").write_text(architecture.summary_md, encoding="utf-8")
        generated.append("architecture")

    if selected_outputs.get("concepts"):
        ConceptAgent().run(content, chapter_path)
        generated.append("concepts")

    if selected_outputs.get("mindmap"):
        MindmapAgent().run(content, chapter_path)
        generated.append("mindmap")

    if selected_outputs.get("flashcards"):
        FlashcardAgent().run(content, chapter_path)
        generated.append("flashcards")

    if selected_outputs.get("exam"):
        ExamAgent().run(content, chapter_path)
        generated.append("exam")

    return generated


def _render_openai_error(error: OpenAIServiceError, chapter_index: int) -> None:
    st.error(f"Error en capítulo {chapter_index}: {error.user_message}")
    st.warning(f"Acción sugerida: {error.actionable_hint}")
    st.caption(
        f"Categoría: {error.category.value} | Reintento recomendado: {'sí' if error.retryable else 'no'} | "
        f"Fallback local disponible: {'sí' if error.fallback_allowed else 'no'}"
    )


def _render_connectivity_status() -> None:
    status = OpenAIClient().health_check()
    if status.ok:
        st.success(status.user_message)
        return

    st.warning(status.user_message)
    if status.actionable_hint:
        st.caption(f"Troubleshooting: {status.actionable_hint}")


def render() -> None:
    st.subheader("3) Process")
    st.write("Ejecuta el pipeline de agentes por capítulo o documento completo.")
    _render_connectivity_status()

    doc = _get_document()
    if not doc:
        st.info("No hay documentos procesados. Ve a Upload para comenzar.")
        return

    st.markdown(f"**Documento activo:** `{doc['metadata'].get('title', doc['slug'])}`")

    with st.expander("Outputs a generar", expanded=True):
        for key in OUTPUT_LABELS:
            current = st.session_state["selected_outputs"].get(key, True)
            st.session_state["selected_outputs"][key] = st.checkbox(
                OUTPUT_LABELS[key], value=current, key=f"out_{key}"
            )

    chapters = doc.get("chapters", [])
    if not chapters:
        st.warning("El documento no tiene capítulos detectados.")
        return

    chapter_indexes = [ch["index"] for ch in chapters]
    selected_chapter = st.selectbox(
        "Capítulo",
        options=chapter_indexes,
        index=0
        if st.session_state.get("selected_chapter_index") not in chapter_indexes
        else chapter_indexes.index(st.session_state["selected_chapter_index"]),
    )
    st.session_state["selected_chapter_index"] = selected_chapter

    cols = st.columns(2)
    if cols[0].button("Procesar capítulo seleccionado", type="primary", width="stretch"):
        chapter_path = chapter_dir(doc, selected_chapter)
        try:
            with st.status(f"Procesando capítulo {selected_chapter}", expanded=True) as status:
                status.write("Iniciando agentes...")
                generated = _run_for_chapter(chapter_path, st.session_state["selected_outputs"])
                status.write(f"Outputs generados: {', '.join(generated)}")
                status.update(label="Capítulo procesado", state="complete")
            st.success(f"Capítulo {selected_chapter} procesado correctamente.")
        except OpenAIServiceError as exc:
            _render_openai_error(exc, selected_chapter)
            st.code(traceback.format_exc())
        except Exception as exc:
            st.error(f"Error en capítulo {selected_chapter}: {exc}")
            st.code(traceback.format_exc())

    if cols[1].button("Procesar documento completo", width="stretch"):
        done = 0
        with st.status("Procesando documento completo", expanded=True) as status:
            for idx in chapter_indexes:
                path = chapter_dir(doc, idx)
                try:
                    status.write(f"▶ Capítulo {idx}")
                    _run_for_chapter(path, st.session_state["selected_outputs"])
                    done += 1
                    status.write(f"✅ Capítulo {idx} completado")
                except OpenAIServiceError as exc:
                    status.write(f"⚠️ Capítulo {idx}: {exc.user_message}")
                    status.write(f"Acción sugerida: {exc.actionable_hint}")
                except Exception as exc:
                    status.write(f"❌ Capítulo {idx} con error: {exc}")
            status.update(
                label=f"Finalizado ({done}/{len(chapter_indexes)})",
                state="complete" if done else "error",
            )

    st.markdown("### Reproceso rápido por capítulo")
    for idx in chapter_indexes:
        col_a, col_b = st.columns([4, 2])
        with col_a:
            st.write(f"Capítulo {idx}")
        with col_b:
            if st.button("Reprocesar", key=f"reprocess_{doc['slug']}_{idx}", width="stretch"):
                try:
                    with st.spinner(f"Reprocesando capítulo {idx}..."):
                        _run_for_chapter(chapter_dir(doc, idx), st.session_state["selected_outputs"])
                    st.success(f"Capítulo {idx} reprocesado.")
                except OpenAIServiceError as exc:
                    _render_openai_error(exc, idx)
                except Exception as exc:
                    st.error(f"Error reprocesando capítulo {idx}: {exc}")
