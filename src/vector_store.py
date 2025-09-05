"""
Módulo para la gestión de la base de datos vectorial (ChromaDB).

Este módulo encapsula toda la interacción con la base de datos, incluyendo
la carga, el procesamiento y la eliminación de documentos.
"""
import os
import ntpath
from typing import List, Dict, Any, Set, IO

import streamlit as st
import chromadb
from langchain_core.documents import Document
from langchain_chroma import Chroma
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from .config import (
    CV_DIRECTORY,
    DB_DIRECTORY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_COLLECTION_NAME
)
from .rag_pipeline import load_embedding_model

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
    """Elimina por completo la colección de ChromaDB."""
    with st.spinner("Eliminando la base de datos vectorial..."):
        try:
            client = chromadb.PersistentClient(path=str(DB_DIRECTORY))
            # Usamos delete_collection para una eliminación completa y limpia.
            client.delete_collection(name=CHROMA_COLLECTION_NAME)
            _clear_streamlit_caches()
            st.success("✅ Base de datos eliminada con éxito.")
        except Exception as e:
            # ChromaDB puede lanzar una excepción si la colección no existe.
            st.warning(f"La base de datos ya estaba vacía o no se pudo eliminar: {e}")

@st.cache_data(ttl=30)
def get_db_stats() -> Dict[str, Any]:
    """Consulta la DB para obtener estadísticas sobre los datos indexados."""
    try:
        client = chromadb.PersistentClient(path=str(DB_DIRECTORY))
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
        # Si la colección no existe, get_collection lanza una excepción.
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
                strategy="fast",
                languages=["eng", "spa"],
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
    """Crea los embeddings y añade los documentos a ChromaDB."""
    embeddings = load_embedding_model()
    vector_store = Chroma(
        persist_directory=str(DB_DIRECTORY),
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
    )
    vector_store.add_documents(documents=chunks)

def _clear_streamlit_caches() -> None:
    """Limpia las cachés de Streamlit para forzar la recarga de recursos y datos."""
    st.cache_resource.clear()
    st.cache_data.clear()

# --- Función Legada (No usada por la nueva UI) ---

def sincronizar_vector_db() -> None:
    """[LEGADO] Vacía y reconstruye la DB desde los CVs en el directorio local."""
    eliminar_toda_la_base_de_datos()
    pdf_files: List[str] = [f for f in os.listdir(CV_DIRECTORY) if f.endswith('.pdf')]
    if not pdf_files:
        st.warning("No se encontraron archivos PDF en la carpeta de datos.")
        return

    archivos_con_ruta = [os.path.join(CV_DIRECTORY, fname) for fname in pdf_files]
    all_chunks = _chunk_archivos(archivos_con_ruta)
    
    if all_chunks:
        _add_chunks_to_db(all_chunks)
        st.success(f"✅ Base de datos vectorial sincronizada desde disco. {len(pdf_files)} CVs procesados.")
    else:
        st.warning("No se pudo extraer contenido de los CVs locales.")
    
    _clear_streamlit_caches()
