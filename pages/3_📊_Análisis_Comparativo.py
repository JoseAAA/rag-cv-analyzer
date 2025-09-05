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

from src.rag_pipeline import load_llm_and_retriever, format_docs, load_embedding_model
from src.vector_store import get_db_stats
from src.config import DB_DIRECTORY, RETRIEVER_K

# --- Plantilla de Prompt Específica del Módulo ---

COMPARISON_PROMPT_TEMPLATE = """
Actúas como un analista de talento experto. Tu tarea es crear una tabla comparativa en formato Markdown y un resumen final basados en el contexto y el criterio de comparación proporcionados.

**Contexto de CVs Proporcionado:**
{context}

**Criterio de Comparación:**
{question}

**Instrucciones de Salida:**
1.  **Tabla Comparativa:** Genera una tabla en Markdown que compare a los candidatos. Usa los nombres de archivo de los CVs como cabeceras de las columnas.
2.  **Análisis y Resumen:** Después de la tabla, escribe un párrafo titulado "**Análisis y Resumen**" donde expliques las fortalezas y debilidades de cada candidato respecto al criterio y ofrezcas una recomendación final.
3.  Si el contexto no es suficiente para responder, indícalo claramente.

**Respuesta en Markdown:**
"""

st.set_page_config(
    page_title="Análisis Comparativo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análisis Comparativo de Candidatos")
st.markdown("Selecciona a los finalistas y compáralos cabeza a cabeza.")

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
            "Ej: Compara su experiencia en el desarrollo de APIs REST con "
            "Python y FastAPI. ¿Qué bases de datos han utilizado?"
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
                    embeddings = load_embedding_model()
                    vector_store = Chroma(
                        persist_directory=str(DB_DIRECTORY),
                        embedding_function=embeddings
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