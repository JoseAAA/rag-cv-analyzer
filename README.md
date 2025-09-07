# Asistente de Reclutamiento con RAG y Gemini

Un sistema de análisis de CVs de código abierto, portable y de alta calidad, diseñado para acelerar y potenciar los procesos de reclutamiento utilizando LLMs.

<div align="center">
  <img 
    src="https://raw.githubusercontent.com/JoseAAA/rag-cv-analyzer/main/assets/screenshot.png" 
    alt="Reporte de Mensajes" 
    width="600" 
    height="350" />
</div>

Este proyecto utiliza una arquitectura de Retrieval-Augmented Generation (RAG) para conectar un potente modelo de lenguaje (Google Gemini) con una base de conocimiento privada, permitiendo un análisis semántico profundo que va más allá de la simple búsqueda de palabras clave.

---

## ✨ Kit de Herramientas del Reclutador

Esta aplicación se estructura como un "Kit de Herramientas" multi-página, donde cada módulo está diseñado para una tarea específica del proceso de selección:

*   **📂 Gestión de CVs:** Sube, procesa y elimina CVs directamente desde una interfaz web interactiva.
*   **🔎 Ranking de Candidatos:** Pega la descripción de un puesto y obtén un ranking de los mejores candidatos de tu base de datos, con resúmenes y análisis de idoneidad.
*   **💬 Chat Interactivo con CVs:** Mantén una conversación en lenguaje natural con la base de conocimiento completa. Realiza preguntas abiertas y obtén respuestas consolidadas de todos los perfiles.
*   **📊 Análisis Comparativo:** Selecciona de 2 a 3 finalistas y compáralos con criterios específicos, generando una tabla de resumen para facilitar la decisión final.

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

## ⚙️ Configuración Avanzada (Opcional)

El archivo `src/config.py` actúa como el "panel de control" central de la aplicación. Aquí puedes ajustar fácilmente parámetros clave como:

*   **Modelos de IA:** Cambiar el modelo de lenguaje (LLM) o el modelo de embeddings.
*   **Comportamiento del LLM:** Ajustar la "temperatura" para controlar la creatividad de las respuestas.
*   **Procesamiento de Documentos:** Modificar el tamaño de los fragmentos de texto (chunks) o la estrategia de extracción de PDFs.
*   **Prompts:** Personalizar las instrucciones que se le dan a la IA para cada módulo (chat, ranking, comparación).

Todos los parámetros están documentados con comentarios claros y utilizan un lenguaje sencillo para facilitar su modificación, incluso para usuarios no técnicos.

---

## 🚀 Guía de Inicio Rápido

### Pre-requisitos
*   [Git](https://git-scm.com/downloads) (para clonar el repositorio).
*   Python 3.9 o superior.
*   Una clave de API de Google. Puedes obtener una de forma gratuita en [Google AI Studio](https://aistudio.google.com/app/apikey).

### 1. Instalación

```bash
# Clona este repositorio
git clone https://github.com/JoseAAA/rag-cv-analyzer.git
cd rag-cv-analyzer

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

El proyecto utiliza un archivo `.env` para gestionar las claves de API de forma segura.

#### Guía Rápida para Obtener tu API Key de Google AI Studio

1.  Visita [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Asegúrate de haber iniciado sesión con tu cuenta de Google.
3.  Haz clic en **"Get API Key in a new project"** o **"Create API Key"** si ya tienes un proyecto.
4.  Copia la clave generada. ¡Guárdala en un lugar seguro!

---

1.  En la raíz del proyecto, encontrarás un archivo llamado `.env.example`.
2.  Crea una copia de este archivo y renómbrala a `.env`.
3.  Abre el nuevo archivo `.env` y añade tu clave de API de Google de la siguiente manera:
    ```
    GOOGLE_API_KEY='tu-clave-de-api-aqui'
    ```

---

## ▶️ Manual de Uso

1.  **Ejecuta la Aplicación:** Desde tu terminal (con el entorno virtual activado), corre el siguiente comando:
    ```bash
    streamlit run app.py
    ```
2.  **Carga tus CVs:** En el navegador, ve al módulo **"📂 Gestión de CVs"** en la barra lateral. Sube todos los CVs en formato PDF que quieras analizar y haz clic en "Procesar".
3.  **Usa las Herramientas:** Una vez procesados los CVs, navega a los otros módulos para rankear, chatear o comparar a los candidatos.

---

## 📈 Posibles Mejoras y Extensiones

Este proyecto es una base excelente. Aquí hay algunas ideas para llevarlo más allá:

*   **Evaluación de Calidad (RAGAs):** Integrar un framework como [RAGAs](https://github.com/explodinggradients/ragas) para medir objetivamente la calidad de las respuestas del sistema.
*   **Extracción de Entidades:** Usar el LLM para extraer información estructurada (nombre, email, teléfono, etc.) de los CVs y mostrarla en una tabla filtrable.
*   **Dockerización:** Crear un `Dockerfile` para encapsular la aplicación y facilitar su despliegue en cualquier sistema.
*   **Pruebas Automatizadas:** Implementar una suite de pruebas con `pytest` para garantizar la fiabilidad y mantenibilidad a largo plazo.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el proyecto, no dudes en abrir un *issue* o enviar un *pull request*.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Eres libre de usarlo, modificarlo y distribuirlo.
