"""
Página del Módulo 0: Gestión de la Base de Conocimiento (CVs).

Este módulo permite a los usuarios cargar, procesar y gestionar los CVs que
conforman la base de conocimiento para el sistema RAG.
"""
import streamlit as st
from src.vector_store import (
    get_db_stats,
    procesar_archivos_cargados,
    eliminar_toda_la_base_de_datos
)

st.set_page_config(
    page_title="Gestión de CVs",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Carga y Gestión de CVs")
st.markdown("Carga, procesa y administra los CVs de los candidatos.")
st.markdown("---")

# --- Columnas para la UI ---
col_upload, col_status = st.columns([0.6, 0.4])

with col_upload:
    st.header("Cargar Nuevos CVs")
    
    uploaded_files = st.file_uploader(
        label="Selecciona uno o más CVs en formato PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help="Puedes arrastrar y soltar varios archivos a la vez."
    )

    process_button = st.button(
        "Procesar y Añadir a la Base de Datos",
        type="primary",
        use_container_width=True
    )
    if process_button:
        if uploaded_files:
            procesar_archivos_cargados(uploaded_files)
        else:
            st.warning("Por favor, selecciona al menos un archivo PDF para procesar.")

    st.markdown("--- ")
    st.header("Mantenimiento de la Base de Datos")

    with st.expander("⚠️ Opciones de Mantenimiento Avanzadas"):
        st.warning(
            "Esta acción es irreversible y reiniciará la base de datos, "
            "eliminando todos los CVs procesados.", 
            icon="🚨"
        )
        
        if st.button("Reiniciar Base de Datos Permanentemente", use_container_width=True):
            eliminar_toda_la_base_de_datos()
            st.rerun()

with col_status:
    st.header("Estado Actual")
    
    with st.container(border=True):
        db_stats = get_db_stats()
        
        st.metric("Total de CVs Procesados", db_stats["cv_count"])
        # st.metric("Segmentos de Información Analizados", db_stats["chunk_count"])
        
        if db_stats["cv_names"]:
            with st.expander("**Ver Nombres de los CVs Analizados**"):
                cv_list_str = "\n".join([f"- {name}" for name in db_stats["cv_names"]])
                st.code(cv_list_str, language="markdown")
        else:
            st.info("La base de datos está actualmente vacía.")
