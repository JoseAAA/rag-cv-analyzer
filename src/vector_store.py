"""
Módulo para la gestión de la base de datos vectorial (ChromaDB).

Este módulo encapsula toda la interacción con la base de datos, incluyendo
la sincronización (borrado y carga) de CVs y la obtención de estadísticas.
"""
import os
import ntpath
from typing import List, Dict, Any, Set

import streamlit as st
import chromadb
from langchain_core.documents import Document
from langchain_chroma import Chroma

# unstructured para el procesamiento avanzado de documentos
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

def sincronizar_vector_db() -> None:
    """Vacía y reconstruye la DB vectorial desde los CVs en el directorio."""
    with st.spinner(f"Sincronizando CVs desde la carpeta '{CV_DIRECTORY}'..."):
        client = chromadb.PersistentClient(path=str(DB_DIRECTORY))
        collection = client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

        if collection.count() > 0:
            st.info(f"Vaciando base de datos... Se eliminarán {collection.count()} registros.")
            collection.delete(ids=collection.get()['ids'])

        pdf_files: List[str] = [f for f in os.listdir(CV_DIRECTORY) if f.endswith('.pdf')]
        if not pdf_files:
            st.warning("No se encontraron archivos PDF. La base de datos está vacía.")
            st.cache_resource.clear()
            st.cache_data.clear()
            return

        with st.spinner("Procesando CVs con la nueva estrategia... Esto será rápido."):
            all_chunks = _load_and_chunk_cvs(pdf_files)
        
        st.info(f"Cargados y divididos {len(pdf_files)} CVs en {len(all_chunks)} fragmentos semánticos.")

        if all_chunks:
            _add_chunks_to_db(all_chunks, client)
            st.success(f"✅ Base de datos vectorial sincronizada. {len(pdf_files)} CVs procesados.")
        else:
            st.warning("No se pudo extraer contenido de los CVs. La base de datos está vacía.")

        st.cache_resource.clear()
        st.cache_data.clear()

def _load_and_chunk_cvs(pdf_files: List[str]) -> List[Document]:
    """Carga y procesa los CVs usando la pipeline de unstructured con la estrategia 'fast'."""
    all_chunks: List[Document] = []
    for filename in pdf_files:
        file_path = os.path.join(CV_DIRECTORY, filename)
        try:
            # 1. Particionar el documento usando la estrategia "fast". No necesita dependencias externas.
            elements = partition_pdf(
                filename=file_path,
                strategy="fast",
                languages=["eng", "spa"],
                infer_table_structure=True,
                extract_images_in_pdf=False
            )
            
            # 2. Agrupar los elementos en chunks semánticos basados en los títulos.
            chunks = chunk_by_title(
                elements=elements,
                max_characters=CHUNK_SIZE,
                new_after_n_chars=int(CHUNK_SIZE * 0.8),
                combine_text_under_n_chars=int(CHUNK_OVERLAP / 2)
            )

            # 3. Convertir los chunks de unstructured a Documentos de LangChain.
            for chunk in chunks:
                metadata = {"source": filename, "page_number": chunk.metadata.page_number or 1}
                doc = Document(page_content=chunk.text, metadata=metadata)
                all_chunks.append(doc)

            st.write(f"- Procesado: {filename}")
        except Exception as e:
            st.warning(f"No se pudo procesar el archivo '{filename}'. Error: {e}")
            continue
    return all_chunks

def _add_chunks_to_db(chunks: List[Document], client: chromadb.Client) -> None:
    """Crea los embeddings y añade los documentos a ChromaDB."""
    embeddings = load_embedding_model()
    vector_store = Chroma(
        client=client,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
    )
    vector_store.add_documents(documents=chunks)

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
        return {"cv_count": 0, "chunk_count": 0, "cv_names": []}