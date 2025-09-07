"""
Página del Módulo 2: Chat Interactivo con CVs.

Este módulo proporciona una interfaz de chat para que los usuarios puedan
conversar directamente con la base de conocimiento de CVs, permitiendo
preguntas abiertas y exploratorias.
"""
from operator import itemgetter

import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.vectorstores import VectorStoreRetriever

from src.rag_pipeline import load_llm_and_retriever, format_docs
from src.config import CHAT_PROMPT_TEMPLATE

st.set_page_config(
    page_title="Chat con CVs",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Chat Interactivo con CVs")
st.markdown(
    "Realiza preguntas en lenguaje natural y obtén respuestas consolidadas de todos los CVs."
)

# --- Lógica de la Cadena de Chat ---

def get_chat_rag_chain(
    retriever: VectorStoreRetriever, llm: ChatGoogleGenerativeAI
) -> Runnable:
    """Crea y devuelve la cadena de RAG específica para el chat conversacional."""
    prompt = ChatPromptTemplate.from_template(CHAT_PROMPT_TEMPLATE)
    parser = StrOutputParser()
    
    return (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
        }
        | prompt
        | llm
        | parser
    )

# --- Renderizado de la Interfaz ---

llm, retriever = load_llm_and_retriever()

if not llm or not retriever:
    st.warning(
        """**La base de datos de CVs parece estar vacía.**

        Por favor, ve al módulo **'📂 Gestión de CVs'** para cargar y procesar
        los documentos primero.""",
        icon="📂"
    )
    st.stop()

# Inicializar el historial del chat en el estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos del historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Aceptar la entrada del usuario
if prompt := st.chat_input("¿Qué te gustaría saber de estos candidatos?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            rag_chain = get_chat_rag_chain(retriever, llm)
            try:
                response = rag_chain.invoke({"question": prompt})
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                error_message = f"Ocurrió un error al contactar a la IA: {e}"
                st.error(error_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_message}
                )
