"""
Módulo de configuración centralizada para la aplicación.

Contiene todas las constantes y parámetros importantes, como rutas de directorios,
nombres de modelos, y configuraciones para el procesamiento de datos y la pipeline de RAG.
"""
from pathlib import Path
from typing import Final

# --- Nombres de Modelos ---
# Modelo de embeddings de HuggingFace. 
# "intfloat/multilingual-e5-base" es un modelo de alta calidad que ofrece un gran balance rendimiento/calidad.
EMBEDDING_MODEL_NAME: Final[str] = "intfloat/multilingual-e5-base"

# --- Parámetros para la Ingesta y el Splitting ---
CHUNK_SIZE: Final[int] = 1000
CHUNK_OVERLAP: Final[int] = 100

# --- Rutas Principales ---
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
CV_DIRECTORY: Final[Path] = BASE_DIR / "data" / "CVs"
DB_DIRECTORY: Final[Path] = BASE_DIR / f"vector_db_{EMBEDDING_MODEL_NAME.replace('/', '_')}"

# Modelo de lenguaje de Google GenAI. 
# "gemini-1.5-flash-latest" es rápido y eficiente en costes.
LLM_MODEL_NAME: Final[str] = "gemini-1.5-flash-latest"

# --- Configuración de la Base de Datos Vectorial ---
# Nombre de la colección en ChromaDB donde se almacenan los embeddings.
CHROMA_COLLECTION_NAME: Final[str] = "langchain"

# --- Parámetros del Retriever ---
# Número de documentos relevantes a recuperar de la base de datos.
RETRIEVER_K: Final[int] = 20

# --- Parámetros de Análisis ---
# Número máximo de candidatos a mostrar en los resultados finales.
TOP_K_CANDIDATES: Final[int] = 5

# --- Prompt Template ---
# Plantilla de prompt para el LLM que define el rol, el contexto y el formato de salida.
PROMPT_TEMPLATE: Final[str] = """
Actúas como un \"Talent Sourcer\" de élite con IA. Tu objetivo es analizar el 
contexto de varios CVs para encontrar a los candidatos que mejor se ajusten a la 
pregunta del reclutador y devolver los resultados en formato JSON.

**Contexto de CVs Proporcionado:**
El contexto a continuación contiene varios fragmentos de texto, cada uno extraído 
de un CV diferente. Cada fragmento está claramente delimitado por 
`--- INICIO DEL FRAGMENTO DEL CV: [nombre_del_archivo.pdf] ---` y 
`--- FIN DEL FRAGMENTO DEL CV: [nombre_del_archivo.pdf] ---`.

**REGLA CRÍTICA:** Basa tu análisis para cada candidato EXCLUSIVAMENTE en los 
fragmentos que provienen de su propio archivo de CV. NUNCA mezcles información 
entre diferentes archivos.

{context}

**Pregunta del Reclutador:**
{question}

**Proceso y Formato de Salida Obligatorio:**
1.  **Análisis Interno (Paso a Paso):** Para cada candidato:
    a.  Identifica su puesto de trabajo más relevante (`job_title_found`).
    b.  **Análisis de Puesto (CRÍTICO):** Compara la `Pregunta del Reclutador` con 
        la experiencia y el `job_title_found` del candidato. Determina si el rol 
        del candidato es **semánticamente equivalente** al puesto buscado, aunque 
        no se llamen igual. Por ejemplo, si se busca un "Científico de Datos", 
        roles como "Analista de Datos Senior con experiencia en Machine Learning" 
        o "Ingeniero BI con especialización en modelos predictivos" son 
        equivalentes. Basado en este análisis, establece el campo booleano 
        `is_job_title_match` en `true` o `false`.
    c.  Evalúa la afinidad general (Alta, Media, Baja) basándote en las 
        habilidades y experiencia.

2.  **Generación de JSON:** Genera una respuesta JSON que sea una lista de objetos. 
    Cada objeto debe representar a un candidato y seguir ESTRICTAMENTE la 
    siguiente estructura:

    ```json
    {{
      "file_name": "nombre_del_archivo.pdf",
      "job_title_found": "El puesto de trabajo más relevante que encontraste en el CV",
      "is_job_title_match": true,
      "affinity": "Alta | Media | Baja",
      "summary": "Un resumen conciso de por qué el candidato es o no es una buena opción, justificando la decisión de 'is_job_title_match'.",
      "key_requirements_analysis": "Análisis de cómo el candidato cumple (o no) con los requisitos clave. Formatea tu respuesta como una lista de puntos usando guiones (-), donde cada punto esté en una nueva línea (usa \n)."
    }}
    ```

**REGLAS PARA EL JSON DE SALIDA:**
- Tu respuesta DEBE ser un único bloque de código JSON válido, comenzando con `[` y terminando con `]`.
- NO incluyas ningún texto, explicación o markdown antes o después del bloque de código JSON.
- Si no encuentras ningún candidato relevante en el contexto, devuelve una lista JSON vacía: `[]`.
- El campo `is_job_title_match` debe ser un booleano (`true` o `false`), sin comillas.
- Asegúrate de que todas las cadenas de texto dentro del JSON (como el `summary`) 
  usen comillas dobles y escapa cualquier comilla doble interna con \"

**INICIA TU RESPUESTA JSON AQUÍ:**
"""