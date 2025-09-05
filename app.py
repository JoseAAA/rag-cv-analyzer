"""
Página de Inicio - Asistente Inteligente de Reclutamiento.

Esta es la página principal de la aplicación. Actúa como un portal de bienvenida
y explica los diferentes módulos disponibles en el "Kit de Herramientas para Reclutadores".
"""
import streamlit as st

st.set_page_config(
    page_title="Inicio | Asistente de Reclutamiento",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Asistente Inteligente de Reclutamiento")
st.markdown("#### Un sistema de análisis de CVs para encontrar al candidato ideal.")
st.markdown("---")

st.info(
    """
    **¡Bienvenido al Kit de Herramientas para Reclutadores!**

    Esta aplicación está diseñada para potenciar y agilizar tu proceso de selección.
    Utiliza el menú de la izquierda para navegar entre los diferentes módulos.
    """
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.header("📂 Gestión de CVs")
        st.markdown(
            """
            - **Carga y procesa** nuevos CVs en formato PDF.
            - **Visualiza** los documentos que ya están en tu base de conocimiento.
            - **Gestiona** tu base de datos de candidatos.
            """
        )

    with st.container(border=True):
        st.header("💬 Chat con CVs")
        st.markdown(
            """
            - **Conversa** directamente con los CVs de tus candidatos.
            - Realiza **preguntas abiertas** y obtén respuestas consolidadas.
            - Ej: *¿Quién tiene experiencia en el sector financiero?*
            """
        )

with col2:
    with st.container(border=True):
        st.header("🔎 Ranking de Candidatos")
        st.markdown(
            """
            - **Define los requisitos** de un puesto de trabajo.
            - Obtén un **ranking de los mejores candidatos** basado en la descripción.
            - Extrae **datos clave** y resúmenes de idoneidad para cada perfil.
            """
        )

    with st.container(border=True):
        st.header("📊 Análisis Comparativo")
        st.markdown(
            """
            - **Selecciona** a varios finalistas de tu interés.
            - **Compara** sus perfiles cabeza a cabeza basado en criterios específicos.
            - Genera una **tabla comparativa** para facilitar la decisión final.
            """
        )

st.sidebar.success("Selecciona un módulo para comenzar.")