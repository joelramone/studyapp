from __future__ import annotations

import streamlit as st

from app.pages.utils import list_processed_documents


def render() -> None:
    st.subheader("2) Documents")
    st.write("Explora documentos procesados, capítulos detectados y selecciona contexto de trabajo.")

    docs = list_processed_documents()
    if not docs:
        st.info("No hay documentos procesados todavía. Ve a Upload para procesar un PDF.")
        return

    doc_options = {f"{doc['metadata'].get('title', doc['slug'])} ({doc['slug']})": doc for doc in docs}
    current_slug = st.session_state.get("selected_doc_slug")

    default_label = next(iter(doc_options))
    if current_slug:
        for label, doc in doc_options.items():
            if doc["slug"] == current_slug:
                default_label = label
                break

    selected_label = st.selectbox(
        "Documento",
        options=list(doc_options.keys()),
        index=list(doc_options.keys()).index(default_label),
    )
    selected_doc = doc_options[selected_label]
    st.session_state["selected_doc_slug"] = selected_doc["slug"]

    st.markdown("### Información del documento")
    m = selected_doc["metadata"]
    st.dataframe(
        [
            {
                "title": m.get("title", "-"),
                "pages": m.get("page_count", 0),
                "chapters": m.get("chapter_count", 0),
                "chunks": m.get("chunk_count", 0),
                "status": m.get("status", "-"),
            }
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Capítulos detectados")
    if not selected_doc["chapters"]:
        st.warning("No se detectaron capítulos para este documento.")
        return

    for chapter in selected_doc["chapters"]:
        col_a, col_b, col_c = st.columns([1, 5, 2])
        with col_a:
            st.markdown(f"**#{chapter['index']}**")
        with col_b:
            st.write(chapter.get("title") or f"Capítulo {chapter['index']}")
        with col_c:
            if st.button("Seleccionar", key=f"pick_ch_{selected_doc['slug']}_{chapter['index']}"):
                st.session_state["selected_chapter_index"] = chapter["index"]
                st.success(f"Capítulo {chapter['index']} seleccionado.")

    selected_chapter = st.session_state.get("selected_chapter_index")
    if selected_chapter:
        st.info(f"Contexto activo: capítulo {selected_chapter}")
