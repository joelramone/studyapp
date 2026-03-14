from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.config import settings
from core.orchestrator import StudyBrainOrchestrator


def _list_saved_pdfs() -> list[Path]:
    pdf_dir = settings.data_dir / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.name.lower())


def render() -> None:
    st.subheader("1) Upload")
    st.write("Sube uno o varios PDFs y ejecútalos en el pipeline base.")

    uploaded_items = st.file_uploader(
        "Subir PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Los archivos se guardan en data/pdfs.",
    )

    if uploaded_items:
        if st.button("Guardar archivos", type="primary", use_container_width=True):
            saved_names: list[str] = []
            for item in uploaded_items:
                target_path = settings.data_dir / "pdfs" / item.name
                target_path.write_bytes(item.getbuffer())
                saved_names.append(item.name)
            st.session_state["uploaded_files"] = saved_names
            st.success(f"Se guardaron {len(saved_names)} archivo(s).")

    st.markdown("### Archivos cargados")
    existing_pdfs = _list_saved_pdfs()
    if not existing_pdfs:
        st.info("No hay PDFs cargados todavía.")
        return

    st.dataframe(
        [{"filename": pdf.name, "size_kb": round(pdf.stat().st_size / 1024, 2)} for pdf in existing_pdfs],
        use_container_width=True,
        hide_index=True,
    )

    selected = st.multiselect(
        "Selecciona archivos para procesar",
        options=[pdf.name for pdf in existing_pdfs],
        default=[existing_pdfs[-1].name],
    )

    if st.button("Procesar seleccionados", type="primary", use_container_width=True):
        if not selected:
            st.warning("Selecciona al menos un PDF.")
            return

        orchestrator = StudyBrainOrchestrator()
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
