from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import streamlit as st

from core.config import settings
from core.orchestrator import StudyBrainOrchestrator
from core.schemas import NotesInputPayload


def _list_saved_pdfs() -> list[Path]:
    pdf_dir = settings.data_dir / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.name.lower())


def _render_pdf_mode(orchestrator: StudyBrainOrchestrator) -> None:
    st.markdown("### Modo PDF")
    uploaded_items = st.file_uploader(
        "Subir PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Los archivos se guardan en data/pdfs.",
    )

    if uploaded_items:
        if st.button("Guardar archivos", type="primary", width="stretch"):
            saved_names: list[str] = []
            for item in uploaded_items:
                target_path = settings.data_dir / "pdfs" / item.name
                target_path.write_bytes(item.getbuffer())
                saved_names.append(item.name)
            st.session_state["uploaded_files"] = saved_names
            st.success(f"Se guardaron {len(saved_names)} archivo(s).")

    st.markdown("#### Archivos cargados")
    existing_pdfs = _list_saved_pdfs()
    if not existing_pdfs:
        st.info("No hay PDFs cargados todavía.")
        return

    st.dataframe(
        [{"filename": pdf.name, "size_kb": round(pdf.stat().st_size / 1024, 2)} for pdf in existing_pdfs],
        width="stretch",
        hide_index=True,
    )

    selected = st.multiselect(
        "Selecciona archivos para procesar",
        options=[pdf.name for pdf in existing_pdfs],
        default=[existing_pdfs[-1].name],
    )

    if st.button("Procesar PDFs seleccionados", type="primary", width="stretch"):
        if not selected:
            st.warning("Selecciona al menos un PDF.")
            return

        status = st.status("Iniciando procesamiento...", expanded=True)
        processed_count = 0

        for filename in selected:
            try:
                pdf_path = settings.data_dir / "pdfs" / filename
                status.update(label=f"Procesando {filename}...", state="running")
                with st.spinner(f"Extrayendo y segmentando {filename}"):
                    payload = orchestrator.process_pdf(pdf_path)
                slug = payload["document"]["slug"]
                st.session_state["selected_doc_slug"] = slug
                st.session_state["selected_chapter_index"] = 1
                processed_count += 1
                status.write(f"✅ {filename} procesado ({len(payload['chapters'])} capítulos)")
            except Exception as exc:
                status.write(f"❌ Error en {filename}: {exc}")
                st.error(f"Error procesando {filename}: {exc}")

        if processed_count:
            status.update(label=f"Procesamiento finalizado ({processed_count}/{len(selected)})", state="complete")
        else:
            status.update(label="No se pudo procesar ningún archivo", state="error")


def _render_notes_mode(orchestrator: StudyBrainOrchestrator) -> None:
    st.markdown("### Modo Notes")
    with st.form("notes_input_form", clear_on_submit=False):
        notes_title = st.text_input("Título del documento", placeholder="Ej: Resumen de Redes - NotebookLM")
        notes_language = st.selectbox("Idioma", options=["es", "en", "pt"], index=0)
        notes_text = st.text_area(
            "Pega aquí tus notas o resumen",
            height=260,
            placeholder="Pega el contenido generado en NotebookLM o tus notas manuales.",
        )
        submit_notes = st.form_submit_button("Procesar Notes", type="primary", width="stretch")

    if not submit_notes:
        return

    try:
        payload = NotesInputPayload(title=notes_title, notes=notes_text, language=notes_language)
    except Exception as exc:
        st.error(f"Entrada inválida: {exc}")
        return

    with st.status("Procesando notes...", expanded=True) as status:
        status.write("Creando documento desde notes")
        result = orchestrator.process_notes(payload)
        status.write("Documento creado y persistido")
        status.update(label="Notes procesadas", state="complete")

    st.session_state["selected_doc_slug"] = result["document"]["slug"]
    st.session_state["selected_chapter_index"] = 1
    st.success(f"Notes procesadas correctamente: {result['document']['title']}")


def render() -> None:
    st.subheader("1) Upload")
    st.write("Elige modo de entrada: PDF o Notes.")

    input_mode = st.radio(
        "Modo de entrada",
        options=["PDF", "Notes"],
        horizontal=True,
        help="PDF extrae texto desde archivo. Notes permite pegar texto manualmente.",
    )

    orchestrator = StudyBrainOrchestrator()

    if input_mode == "PDF":
        _render_pdf_mode(orchestrator)
    else:
        _render_notes_mode(orchestrator)
