"""
Página del Módulo 1: Ranking de Candidatos.

Esta página contiene la funcionalidad principal de la aplicación original:
permitir al reclutador definir los requisitos de un puesto y obtener un
ranking de los mejores candidatos basado en un análisis RAG.
"""
from typing import List, Dict, Any, Optional
from operator import itemgetter

import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.vectorstores import VectorStoreRetriever

from src.vector_store import get_db_stats
from src.rag_pipeline import load_llm_and_retriever, format_docs
from src.config import PROMPT_TEMPLATE, TOP_K_CANDIDATES

st.set_page_config(
    page_title="Ranking de Candidatos",
    page_icon="🔎",
    layout="wide"
)

# --- Funciones de Lógica de la Aplicación ---

def build_query(
    job_title: str, min_experience: int, skills: str, reqs: str
) -> str:
    """Construye la consulta completa para el LLM a partir de los filtros de la UI."""
    query_parts: List[str] = [
        f"Busco un '{job_title}' con al menos {min_experience} años de experiencia."
    ]
    if skills:
        query_parts.append(f"Habilidades indispensables: {skills}.")
    if reqs:
        query_parts.append(f"Otros requisitos importantes: {reqs}")
    return " ".join(query_parts)

def get_rag_chain(
    retriever: VectorStoreRetriever, llm: ChatGoogleGenerativeAI
) -> Runnable:
    """Crea y devuelve la cadena de RAG (LangChain) completa."""
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    parser = JsonOutputParser()
    # Se usa () para romper la línea de la cadena de forma legible
    return (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
        }
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
        expander_title = (
            f"📄 **{candidate.get('file_name', 'N/A')}** - "
            f"Afinidad: **{candidate.get('affinity', 'N/A')}**"
        )
        with st.expander(expander_title):
            st.subheader(
                f"Puesto Encontrado: {candidate.get('job_title_found', 'N/A')}"
            )
            st.markdown("**Resumen:**")
            st.markdown(candidate.get('summary', 'Sin resumen.'))
            st.markdown("**Análisis de Requisitos Clave:**")
            st.markdown(candidate.get('key_requirements_analysis', 'Sin análisis.'))

# --- Funciones de la Interfaz de Usuario (UI) ---

def render_sidebar() -> Dict[str, Any]:
    """Renderiza la barra lateral y devuelve los filtros de búsqueda."""
    with st.sidebar:
        st.header("📊 Estadísticas de la Base de Datos")
        db_stats = get_db_stats()
        col1, col2 = st.columns(2)
        col1.metric("CVs Indexados", db_stats["cv_count"])
        col2.metric("Fragmentos", db_stats["chunk_count"])

        if db_stats["cv_names"]:
            with st.expander("Ver CVs Analizados"):
                for cv_name in db_stats["cv_names"]:
                    st.markdown(f"- 📄 {cv_name}")
        
        st.markdown("---")
        st.header("🔍 Filtros de Búsqueda")
        return {
            "job_title": st.text_input(
                "Título del Puesto", placeholder="Ej: Ingeniero de Software"
            ),
            "min_experience": st.slider("Años de experiencia", 0, 20, 3),
            "skills": st.text_input(
                "Habilidades (separadas por coma)",
                placeholder="Ej: Python, Power BI"
            ),
            "reqs": st.text_area(
                "Requisitos Adicionales",
                placeholder="Ej: Disponibilidad para viajar..."
            ),
            "analyze": st.button(
                "Analizar CVs", type="primary", use_container_width=True
            )
        }

def render_main_content(
    filters: Dict[str, Any],
    llm: Optional[ChatGoogleGenerativeAI],
    retriever: Optional[VectorStoreRetriever]
) -> None:
    """Renderiza el contenido principal de la página."""
    if not llm or not retriever:
        st.warning(
            """**La base de datos de CVs parece estar vacía.**

            Por favor, ve al módulo **'📂 Gestión de CVs'** para cargar y procesar
            los documentos primero.""",
            icon="📂"
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
    st.title("🔎 Ranking de Candidatos")
    st.markdown("Encuentra a los mejores perfiles para un puesto de trabajo específico.")

    filters = render_sidebar()
    llm, retriever = load_llm_and_retriever()
    render_main_content(filters, llm, retriever)

if __name__ == "__main__":
    main()