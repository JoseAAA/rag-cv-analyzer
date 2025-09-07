"""
Módulo para la lógica de la pipeline de RAG (Retrieval-Augmented Generation).

Este módulo se encarga de inicializar los componentes de LangChain, como el
modelo de embeddings, el LLM y el retriever.
"""
import os
import ntpath
from typing import Tuple, List, Optional

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from .config import (
    EMBEDDING_MODEL_NAME,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    RETRIEVER_K,
    CHROMA_COLLECTION_NAME
)
from .vector_store import get_chroma_client, get_db_stats

# Cargar variables de entorno desde el archivo .env
load_dotenv()

from .models import load_embedding_model

@st.cache_resource
def load_llm_and_retriever() -> Tuple[Optional[ChatGoogleGenerativeAI], Optional[VectorStoreRetriever]]:
    """Carga y cachea el LLM de Gemini y el retriever de ChromaDB.

    Returns:
        Una tupla (llm, retriever). Devuelve (None, None) si la DB está vacía
        o falta la API key.
    """
    # La forma más robusta de saber si la DB está vacía es ver sus estadísticas
    db_stats = get_db_stats()
    if db_stats["cv_count"] == 0:
        return None, None

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        st.error(
            "API Key de Google no encontrada. Asegúrate de crear un archivo .env "
            "y añadir GOOGLE_API_KEY='tu-clave-aqui'"
        )
        return None, None

    try:
        embeddings = load_embedding_model()
        client = get_chroma_client() # Usa el cliente centralizado
        
        vector_store = Chroma(
            client=client,
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=embeddings
        )
        
        retriever = vector_store.as_retriever(search_kwargs={'k': RETRIEVER_K})
        
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            google_api_key=google_api_key,
            temperature=LLM_TEMPERATURE
        )
        
        return llm, retriever
    except Exception as e:
        st.error(f"Error al inicializar los servicios de IA: {e}")
        return None, None

def format_docs(docs: List[Document]) -> str:
    """Formatea los documentos recuperados para ser insertados en el prompt.

    Args:
        docs: Una lista de objetos Document de LangChain.

    Returns:
        Un string único con el contenido de todos los documentos, cada uno
        delimitado por un encabezado que indica su archivo de origen.
    """
    return "\n\n".join(
        f"--- INICIO DEL FRAGMENTO DEL CV: {ntpath.basename(doc.metadata.get('source', 'N/A'))} ---"
        f"{doc.page_content}\n"
        f"--- FIN DEL FRAGMENTO DEL CV: {ntpath.basename(doc.metadata.get('source', 'N/A'))} ---"
        for doc in docs
    )