"""
Punto de entrada principal para la aplicación Streamlit "Asistente de Reclutamiento".

Este script construye la interfaz de usuario (UI) y orquesta las llamadas a los
módulos de lógica de negocio (`vector_store`, `rag_pipeline`) definidos en `src`.
"""
from typing import List, Dict, Any, Optional
from operator import itemgetter

import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.vectorstores import VectorStoreRetriever

from src.vector_store import sincronizar_vector_db, get_db_stats
from src.rag_pipeline import load_llm_and_retriever, format_docs
from src.config import PROMPT_TEMPLATE, TOP_K_CANDIDATES

# --- Funciones de Lógica de la Aplicación ---

def build_query(job_title: str, min_experience: int, skills: str, reqs: str) -> str:
    """Construye la consulta completa para el LLM a partir de los filtros de la UI."""
    query_parts: List[str] = [
        f"Busco un '{job_title}' con al menos {min_experience} años de experiencia."
    ]
    if skills:
        query_parts.append(f"Habilidades indispensables: {skills}.")
    if reqs:
        query_parts.append(f"Otros requisitos importantes: {reqs}")
    return " ".join(query_parts)

def get_rag_chain(retriever: VectorStoreRetriever, llm: ChatGoogleGenerativeAI) -> Runnable:
    """Crea y devuelve la cadena de RAG (LangChain) completa."""
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    parser = JsonOutputParser()
    return (
        {"context": itemgetter("question") | retriever | format_docs, "question": itemgetter("question")}
        | prompt
        | llm
        | parser
    )

def process_and_display_results(query: str, response: List[Dict[str, Any]]) -> None:
    """Procesa la respuesta del LLM, la ordena y la muestra en la UI."""
    st.markdown("#### 📝 Consulta del Reclutador:")
    st.info(query)
    st.markdown("---")

    if not response:
        st.warning("No se encontraron candidatos que cumplan los requisitos.")
        return

    affinity_map = {"Alta": 3, "Media": 2, "Baja": 1, "N/A": 0}
    
    filtered = [cand for cand in response if cand.get("is_job_title_match")]
    sorted_candidates = sorted(
        filtered,
        key=lambda x: affinity_map.get(x.get("affinity", "N/A"), 0),
        reverse=True
    )
    top_k = sorted_candidates[:TOP_K_CANDIDATES]

    if not top_k:
        st.warning("Ningún candidato cumple el requisito de puesto de trabajo.")
        return

    st.markdown(f"#### 🏆 Top {len(top_k)} Candidatos Encontrados:")
    for candidate in top_k:
        with st.container(border=True):
            st.subheader(f"📄 {candidate.get('file_name', 'N/A')}")
            col1, col2 = st.columns(2)
            col1.metric("Afinidad", candidate.get('affinity', 'N/A'))
            col2.metric("Puesto Encontrado", candidate.get('job_title_found', 'N/A'))
            st.markdown("**Resumen:**")
            st.markdown(candidate.get('summary', 'Sin resumen.'))
            st.markdown("**Análisis de Requisitos Clave:**")
            st.markdown(candidate.get('key_requirements_analysis', 'Sin análisis.'))

# --- Funciones de la Interfaz de Usuario (UI) ---

def render_sidebar() -> Dict[str, Any]:
    """Renderiza la barra lateral y devuelve los filtros de búsqueda."""
    with st.sidebar:
        st.header("⚙️ Controles")
        if st.button("🔄 Sincronizar Base de Datos de CVs", use_container_width=True):
            sincronizar_vector_db()
            st.rerun()

        st.markdown("---")
        st.header("📊 Estadísticas de la Base de Datos")
        db_stats = get_db_stats()
        col1, col2 = st.columns(2)
        col1.metric("CVs Indexados", db_stats["cv_count"])
        col2.metric("Fragmentos Totales", db_stats["chunk_count"])

        if db_stats["cv_names"]:
            with st.expander("Ver CVs Analizados"):
                for cv_name in db_stats["cv_names"]:
                    st.markdown(f"- 📄 {cv_name}")
        
        st.markdown("---")
        st.header("🔍 Filtros de Búsqueda")
        return {
            "job_title": st.text_input("Título del Puesto", placeholder="Ej: Ingeniero de Software"),
            "min_experience": st.slider("Años de experiencia", 0, 20, 3),
            "skills": st.text_input("Habilidades (separadas por coma)", placeholder="Ej: Python, Power BI"),
            "reqs": st.text_area("Requisitos Adicionales", placeholder="Ej: Disponibilidad para viajar..."),
            "analyze": st.button("Analizar CVs", type="primary", use_container_width=True)
        }

def render_main_content(
    filters: Dict[str, Any],
    llm: Optional[ChatGoogleGenerativeAI],
    retriever: Optional[VectorStoreRetriever]
) -> None:
    """Renderiza el contenido principal, incluyendo el mensaje de bienvenida o los resultados."""
    if not llm or not retriever:
        st.header("👋 ¡Bienvenido!")
        st.info(
            """**La base de datos de CVs parece estar vacía.**
            1.  Asegúrate de que tus CVs en PDF están en la carpeta `data/CVs`.
            2.  Haz clic en **"🔄 Sincronizar Base de Datos"** para empezar.""",
            icon="💡"
        )
        return

    st.header("Resultados del Análisis")
    if filters["analyze"]:
        if not filters["job_title"]:
            st.warning("Por favor, introduce un Título del Puesto.")
            return

        query = build_query(**{k: v for k, v in filters.items() if k != 'analyze'})
        rag_chain = get_rag_chain(retriever, llm)
        
        with st.spinner(f"Analizando candidatos para '{filters['job_title']}'..."):
            try:
                response = rag_chain.invoke({"question": query})
                process_and_display_results(query, response)
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la respuesta de la IA: {e}")
                st.warning("Intenta de nuevo. Si el error persiste, revisa el prompt.")
    else:
        st.info("Define los criterios en la barra lateral y haz clic en 'Analizar CVs'.")

def main():
    """Función principal que construye y ejecuta la interfaz de Streamlit."""
    st.set_page_config(page_title="Asistente de Reclutamiento IA", layout="wide")
    st.title("🚀 Asistente Inteligente de Reclutamiento")
    st.markdown("Analiza CVs para encontrar al candidato ideal basado en tus criterios.")

    filters = render_sidebar()
    llm, retriever = load_llm_and_retriever()
    render_main_content(filters, llm, retriever)

if __name__ == "__main__":
    main()
