"""
Página del Módulo 3: Análisis Comparativo de Candidatos.

Este módulo permite al usuario seleccionar a 2 o 3 candidatos y compararlos
cabeza a cabeza según un criterio específico, generando una tabla en Markdown.
"""
import streamlit as st
from operator import itemgetter

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma

from src.rag_pipeline import load_llm_and_retriever, format_docs
from src.vector_store import get_db_stats, get_chroma_client
from src.config import RETRIEVER_K, COMPARISON_PROMPT_TEMPLATE, CHROMA_COLLECTION_NAME
from src.models import load_embedding_model

st.set_page_config(
    page_title="Análisis Comparativo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análisis Comparativo de Candidatos")
st.markdown("Selecciona a los finalistas para una comparación detallada de sus perfiles.")

# --- Carga de Datos y UI ---

llm, _ = load_llm_and_retriever()
db_stats = get_db_stats()

if not llm or db_stats["cv_count"] == 0:
    st.warning(
        """**La base de datos de CVs parece estar vacía.**

        Por favor, ve al módulo **'📂 Gestión de CVs'** para cargar y procesar
        los documentos primero.""",
        icon="📂"
    )
    st.stop()

st.info("**Paso 1:** Selecciona de 2 a 3 candidatos de la lista para comparar.")

selected_cvs = st.multiselect(
    label="Selecciona los candidatos a comparar",
    options=db_stats["cv_names"],
    max_selections=3,
    placeholder="Elige 2 o 3 CVs"
)

if len(selected_cvs) >= 2:
    st.info("**Paso 2:** Define el criterio para la comparación.")
    comparison_criterion = st.text_area(
        label="Criterio de Comparación",
        placeholder=(
            "Ej: ¿Quién tiene más años de experiencia en liderazgo de equipos?"
            " Compara también sus habilidades en Python y SQL."
        )
    )

    if st.button("Generar Comparativa", type="primary", use_container_width=True):
        if not comparison_criterion.strip():
            st.warning("Por favor, introduce un criterio de comparación.")
        else:
            spinner_text = f"Generando comparación para: {', '.join(selected_cvs)}..."
            with st.spinner(spinner_text):
                try:
                    # --- Lógica de Backend para la Comparación ---
                    client = get_chroma_client() # Usa el cliente centralizado
                    vector_store = Chroma(
                        client=client,
                        collection_name=CHROMA_COLLECTION_NAME,
                        embedding_function=load_embedding_model()
                    )
                    
                    search_kwargs = {
                        'k': RETRIEVER_K,
                        'filter': {
                            'source': {
                                '$in': selected_cvs
                            }
                        }
                    }
                    filtered_retriever = vector_store.as_retriever(
                        search_kwargs=search_kwargs
                    )

                    prompt = ChatPromptTemplate.from_template(COMPARISON_PROMPT_TEMPLATE)
                    parser = StrOutputParser()
                    
                    comparison_chain = (
                        {
                            "context": itemgetter("question") | filtered_retriever | format_docs,
                            "question": itemgetter("question")
                        }
                        | prompt
                        | llm
                        | parser
                    )
                    
                    response = comparison_chain.invoke(
                        {"question": comparison_criterion}
                    )
                    
                    st.markdown("---")
                    st.header("Resultados de la Comparativa")
                    st.markdown(response)

                except Exception as e:
                    st.error(f"Ocurrió un error al generar la comparación: {e}")