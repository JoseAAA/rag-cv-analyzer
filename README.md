# Asistente de Reclutamiento con RAG y Gemini

Un sistema de análisis de CVs de código abierto, portable y de alta calidad, diseñado para acelerar y potenciar los procesos de reclutamiento utilizando LLMs.

Este proyecto utiliza una arquitectura de Retrieval-Augmented Generation (RAG) para conectar un potente modelo de lenguaje (Google Gemini) con una base de conocimiento privada (un directorio de CVs), permitiendo un análisis semántico profundo que va más allá de la simple búsqueda de palabras clave.

---

## ✨ Características Principales

*   **Procesamiento Inteligente de Documentos:** Utiliza **`unstructured`** para analizar la maquetación de los CVs, extrayendo texto de forma limpia y preservando la estructura original del documento.
*   **Chunking Semántico:** En lugar de realizar cortes arbitrarios, agrupa la información por las secciones lógicas del CV (Experiencia, Educación, etc.), proveyendo un contexto de muchísima mayor calidad al LLM.
*   **Arquitectura Portable:** **Cero dependencias de sistema.** El proyecto es 100% portable y fácil de instalar en cualquier máquina con Python, lo que lo hace ideal para compartir y colaborar.
*   **Calidad de Búsqueda Superior:** Impulsado por modelos de embedding de alto rendimiento de Hugging Face para encontrar a los candidatos más relevantes.
*   **Interfaz Intuitiva:** Interfaz web interactiva creada con **Streamlit** para un uso fácil y amigable.

---

## 🛠️ Stack Tecnológico

Este proyecto integra un stack moderno de herramientas de IA y Python:

*   **Backend y Lógica:** [Python 3.9+](https://www.python.org/)
*   **Framework Web:** [Streamlit](https://streamlit.io/)
*   **Orquestación LLM:** [LangChain](https://www.langchain.com/)
*   **Procesamiento de Documentos:** [Unstructured](https://unstructured.io/)
*   **Modelo de Lenguaje (LLM):** [Google Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/)
*   **Base de Datos Vectorial:** [ChromaDB](https://www.trychroma.com/)
*   **Modelo de Embeddings:** [Hugging Face `intfloat/multilingual-e5-base`](https://huggingface.co/intfloat/multilingual-e5-base)

---

## 🧠 Cómo Funciona

El sistema sigue una arquitectura RAG optimizada para el análisis de CVs:

1.  **Ingesta Inteligente:** Los CVs en formato PDF son procesados por `unstructured`. La librería analiza la estructura del documento y lo divide en elementos lógicos (títulos, párrafos, listas).
2.  **Chunking Semántico:** Los elementos extraídos se agrupan de forma coherente usando la función `chunk_by_title`. Esto asegura que la información de una misma sección (p. ej., un puesto de trabajo completo) permanezca unida en un solo "chunk".
3.  **Embedding:** Cada chunk de texto se convierte en un vector numérico (embedding) usando el modelo `multilingual-e5-base`, que captura su significado semántico.
4.  **Almacenamiento:** Estos vectores se guardan en una base de datos vectorial local de ChromaDB.
5.  **Recuperación y Síntesis:** Cuando un usuario realiza una consulta, el sistema busca en la base de datos los chunks de CV más relevantes. Estos chunks, junto con la consulta, se envían a Gemini, que analiza el contexto y genera una respuesta estructurada y razonada, identificando a los mejores candidatos.

---

## 🚀 Guía de Inicio Rápido

### Pre-requisitos
*   Python 3.9 o superior.
*   Una clave de API de Google. Puedes obtener una de forma gratuita en [Google AI Studio](https://aistudio.google.com/app/apikey).

### 1. Instalación

No se requiere ninguna instalación de software externo, solo dependencias de Python.

```bash
# Clona este repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio

# Crea y activa un entorno virtual (recomendado)
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
# source venv/bin/activate

# Instala todas las librerías necesarias
pip install -r requirements.txt
```

### 2. Configuración de la API Key

El proyecto usa los secretos de Streamlit para gestionar la API Key de forma segura.

*   Crea una carpeta en la raíz del proyecto llamada `.streamlit`.
*   Dentro de ella, crea un archivo llamado `secrets.toml`.
*   Añade tu clave al archivo con el siguiente formato:
    ```toml
    GOOGLE_API_KEY = "TU_API_KEY_DE_GOOGLE_AQUI"
    ```

---

## ▶️ Manual de Uso

1.  **Añade tus CVs:** Coloca los CVs en formato PDF en la carpeta `data/CVs/`.
2.  **Ejecuta la Aplicación:** Desde tu terminal (con el entorno virtual activado), corre el siguiente comando:
    ```bash
    streamlit run app.py
    ```
3.  **Sincroniza la Base de Datos:** En la interfaz de la aplicación, haz clic en el botón **"🔄 Sincronizar Base de Datos de CVs"**. Este proceso lee los PDFs, los procesa y los carga en la base de datos vectorial. Solo necesitas hacerlo la primera vez o cuando añadas, elimines o modifiques los CVs.
4.  **Realiza tu Análisis:** Usa los filtros de la barra lateral para definir tu búsqueda y haz clic en **"Analizar CVs"**.

---

## 🔧 Configuración y Personalización

Puedes ajustar el comportamiento del análisis modificando las variables en `src/config.py`:

*   `EMBEDDING_MODEL_NAME`: Puedes cambiar el modelo de embedding por otro de Hugging Face si lo deseas.
*   `RETRIEVER_K`: Controla cuántos fragmentos de texto se recuperan de la base de datos para dar contexto al LLM. Un número mayor puede dar más contexto, pero consume más tokens.
*   `TOP_K_CANDIDATES`: Define el número máximo de candidatos que se mostrarán en la lista final de resultados.

---

## 📈 Posibles Mejoras y Extensiones

Este proyecto es una base excelente. Aquí hay algunas ideas para llevarlo más allá:

*   **Evaluación de Calidad (RAGAs):** Integrar un framework como [RAGAs](https://github.com/explodinggradients/ragas) para evaluar y medir objetivamente la calidad de las respuestas del sistema.
*   **Subida de Archivos Interactiva:** Modificar la interfaz de Streamlit para permitir subir, listar y eliminar CVs directamente desde el navegador.
*   **Extracción de Entidades:** Usar el LLM para extraer información estructurada (nombre, email, teléfono, etc.) de los CVs y mostrarla en una tabla.
*   **Historial de Búsquedas:** Guardar los resultados de los análisis en una base de datos para poder consultarlos y compararlos en el futuro.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el proyecto, no dudes en abrir un *issue* o enviar un *pull request*.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Eres libre de usarlo, modificarlo y distribuirlo.