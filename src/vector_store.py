"""
Módulo para la gestión de la base de datos vectorial (ChromaDB).

Este módulo encapsula toda la interacción con la base de datos, incluyendo
la carga, el procesamiento y la eliminación de documentos.
Implementa un patrón de cliente único para evitar conflictos de conexión.
"""
import os
import ntpath
from typing import List, Dict, Any, Set, IO

import streamlit as st
import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from .config import (
    DB_DIRECTORY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_COLLECTION_NAME,
    PDF_PROCESSING_STRATEGY,
    PDF_PROCESSING_LANGUAGES
)
from .models import load_embedding_model

# --- Conexión Única y Centralizada a ChromaDB ---

@st.cache_resource
def get_chroma_client() -> chromadb.Client:
    """
    Crea y cachea una instancia única del cliente de ChromaDB.
    Esta es la única función que debe crear un PersistentClient.
    """
    return chromadb.PersistentClient(
        path=str(DB_DIRECTORY),
        settings=Settings(allow_reset=True)
    )

# --- Funciones Públicas de Alto Nivel ---

def procesar_archivos_cargados(archivos_cargados: List[st.runtime.uploaded_file_manager.UploadedFile]) -> None:
    """Procesa una lista de archivos cargados desde la UI y los añade a la DB."""
    if not archivos_cargados:
        st.warning("No has seleccionado ningún archivo para cargar.")
        return

    with st.spinner(f"Procesando {len(archivos_cargados)} archivo(s)... Esto puede tardar un momento."):
        all_chunks = _chunk_archivos(archivos_cargados)
        
        if not all_chunks:
            st.error("No se pudo extraer contenido de los archivos seleccionados.")
            return

        _add_chunks_to_db(all_chunks)
        st.success(f"✅ {len(archivos_cargados)} CV(s) procesados y añadidos a la base de datos.")
        _clear_streamlit_caches()

def eliminar_toda_la_base_de_datos() -> None:
    """
    Reinicia por completo la base de datos vectorial usando el cliente centralizado.
    """
    with st.spinner("Reiniciando la base de datos vectorial..."):
        try:
            client = get_chroma_client()
            client.reset()
            _clear_streamlit_caches()
            st.success("✅ Base de datos reiniciada con éxito.")
        except Exception as e:
            st.error(f"Ocurrió un error al reiniciar la base de datos: {e}")

@st.cache_data(ttl=30)
def get_db_stats() -> Dict[str, Any]:
    """Consulta la DB para obtener estadísticas sobre los datos indexados."""
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        
        if collection.count() == 0:
            return {"cv_count": 0, "chunk_count": 0, "cv_names": []}

        metadatas: List[Dict[str, Any]] = collection.get(include=["metadatas"])['metadatas']
        chunk_count: int = len(metadatas)
        
        unique_sources: Set[str] = set(
            ntpath.basename(meta['source']) for meta in metadatas if 'source' in meta
        )
        
        return {
            "cv_count": len(unique_sources),
            "chunk_count": chunk_count,
            "cv_names": sorted(list(unique_sources))
        }
    except Exception:
        return {"cv_count": 0, "chunk_count": 0, "cv_names": []}

# --- Funciones Privadas de Lógica Interna ---

def _chunk_archivos(archivos: List[IO]) -> List[Document]:
    """Función central que parte y divide una lista de archivos (en memoria o en disco)."""
    all_chunks: List[Document] = []
    progress_bar = st.progress(0, "Iniciando procesamiento...")

    for i, archivo in enumerate(archivos):
        file_name = getattr(archivo, 'name', str(archivo))
        progress_text = f"Procesando: {ntpath.basename(file_name)}..."
        progress_bar.progress((i + 1) / len(archivos), text=progress_text)

        try:
            elements = partition_pdf(
                file=archivo,  # partition_pdf puede manejar objetos de archivo en memoria
                strategy=PDF_PROCESSING_STRATEGY,
                languages=PDF_PROCESSING_LANGUAGES,
                infer_table_structure=True,
            )
            
            chunks = chunk_by_title(
                elements=elements,
                max_characters=CHUNK_SIZE,
                new_after_n_chars=int(CHUNK_SIZE * 0.8),
                combine_text_under_n_chars=int(CHUNK_OVERLAP / 2)
            )

            for chunk in chunks:
                metadata = {"source": file_name, "page_number": chunk.metadata.page_number or 1}
                doc = Document(page_content=chunk.text, metadata=metadata)
                all_chunks.append(doc)

        except Exception as e:
            st.warning(f"No se pudo procesar el archivo '{file_name}'. Error: {e}")
            continue
    
    progress_bar.empty()
    return all_chunks

def _add_chunks_to_db(chunks: List[Document]) -> None:
    """Crea los embeddings y añade los documentos a ChromaDB usando el cliente centralizado."""
    embeddings = load_embedding_model()
    client = get_chroma_client()
    
    vector_store = Chroma(
        client=client,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
    )
    vector_store.add_documents(documents=chunks)

def _clear_streamlit_caches() -> None:
    """Limpia las cachés de Streamlit para forzar la recarga de recursos y datos."""
    st.cache_resource.clear()
    st.cache_data.clear()
