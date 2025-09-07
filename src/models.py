import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings

from .config import EMBEDDING_MODEL_NAME

@st.cache_resource
def load_embedding_model() -> HuggingFaceEmbeddings:
    """Carga y cachea el modelo de embeddings de HuggingFace."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)