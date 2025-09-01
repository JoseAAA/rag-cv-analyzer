"""
Módulo para la lógica de la pipeline de RAG (Retrieval-Augmented Generation).

Este módulo se encarga de inicializar los componentes de LangChain, como el
modelo de embeddings, el LLM y el retriever.
"""
import os
import ntpath
from typing import Tuple, List, Optional

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

# Importaciones actualizadas para LangChain v0.2+
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from .config import (
    DB_DIRECTORY,
    EMBEDDING_MODEL_NAME,
    LLM_MODEL_NAME,
    RETRIEVER_K
)

@st.cache_resource
def load_embedding_model() -> HuggingFaceEmbeddings:
    """Carga y cachea el modelo de embeddings de HuggingFace.
    
    Esta función se cachea para asegurar que el modelo se cargue en memoria
    una sola vez durante la vida de la aplicación.
    
    Returns:
        Una instancia del modelo de embeddings.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

@st.cache_resource
def load_llm_and_retriever() -> Tuple[Optional[ChatGoogleGenerativeAI], Optional[VectorStoreRetriever]]:
    """Carga y cachea el LLM de Gemini y el retriever de ChromaDB.

    Utiliza el modelo de embeddings cacheado para inicializar el retriever.

    Returns:
        Una tupla conteniendo el objeto LLM y el objeto retriever. Si algo
        falla (DB no encontrada, API key ausente), devuelve (None, None).
    """
    persist_directory = str(DB_DIRECTORY)
    if not os.path.isdir(persist_directory) or not os.listdir(persist_directory):
        return None, None

    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("API Key de Google no encontrada. Añádela a .streamlit/secrets.toml")
        return None, None

    # Usa la función cacheada para obtener el modelo de embeddings
    embeddings = load_embedding_model()
    
    vector_store = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings
    )
    
    retriever = vector_store.as_retriever(search_kwargs={'k': RETRIEVER_K})
    
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=google_api_key,
        temperature=0.1
    )
    
    return llm, retriever

def format_docs(docs: List[Document]) -> str:
    """Formatea los documentos recuperados para ser insertados en el prompt.

    Args:
        docs: Una lista de objetos Document de LangChain.

    Returns:
        Un string único con el contenido de todos los documentos, cada uno
        delimitado por un encabezado que indica su archivo de origen.
    """
    return "\n\n".join(
        f"--- INICIO DEL FRAGMENTO DEL CV: {ntpath.basename(doc.metadata.get('source', 'N/A'))} ---\n"
        f"{doc.page_content}\n"
        f"--- FIN DEL FRAGMENTO DEL CV: {ntpath.basename(doc.metadata.get('source', 'N/A'))} ---"
        for doc in docs
    )