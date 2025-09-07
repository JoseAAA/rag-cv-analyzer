"""
Módulo de Configuración Centralizada.

Este archivo es el \"panel de control\" de la aplicación. Contiene todos los
parámetros clave para que puedas ajustar el comportamiento del asistente
de reclutamiento sin necesidad de tocar el código fuente.
"""
from pathlib import Path
from typing import Final, List

# ==============================================================================
# SECCIÓN 1: RUTAS Y DIRECTORIOS
# ==============================================================================
# Rutas principales. No es necesario modificar esto a menos que se reestructure
# el proyecto.
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
CV_DIRECTORY: Final[Path] = BASE_DIR / "data" / "CVs"
DB_DIRECTORY_BASE_NAME: Final[str] = "vector_db"


# ==============================================================================
# SECCIÓN 2: MODELOS DE INTELIGENCIA ARTIFICIAL
# ==============================================================================

# --- Modelo de Embeddings (Para \"entender\" el texto de los CVs) ---
# Modelo recomendado: \"intfloat/multilingual-e5-base\" (multilingüe, buen balance).
EMBEDDING_MODEL_NAME: Final[str] = "intfloat/multilingual-e5-base"

# --- Modelo de Lenguaje (Para \"generar\" las respuestas) ---
# Modelo recomendado: \"gemini-1.5-flash-latest\" (rápido y de bajo coste).
LLM_MODEL_NAME: Final[str] = "gemini-1.5-flash-latest"

# --- Comportamiento del Modelo de Lenguaje ---
# La \"temperatura\" controla la creatividad del modelo (rango: 0.0 a 1.0).
# - Valores bajos (ej. 0.1): producen respuestas más directas y consistentes.
# - Valores altos (ej. 0.9): producen respuestas más creativas y diversas.
LLM_TEMPERATURE: Final[float] = 0.1


# ==============================================================================
# SECCIÓN 3: PROCESAMIENTO Y ANÁLISIS DE DOCUMENTOS
# ==============================================================================

# --- División de Documentos (Chunking) ---
# Tamaño máximo de cada fragmento de texto para análisis (en caracteres).
CHUNK_SIZE: Final[int] = 1000
# Solapamiento entre fragmentos para no perder contexto (en caracteres).
CHUNK_OVERLAP: Final[int] = 100

# --- Procesamiento de PDFs ---
# Estrategia de extracción: \"fast\" (rápida) o \"hi_res\" (más precisa, lenta).
PDF_PROCESSING_STRATEGY: Final[str] = "fast"
# Idiomas a detectar en los CVs para mejorar la extracción de texto.
PDF_PROCESSING_LANGUAGES: Final[List[str]] = ["spa", "eng"]

# --- Búsqueda de Información (Retriever) ---
# Número de fragmentos de CVs que la IA consultará para formular una respuesta.
RETRIEVER_K: Final[int] = 20

# --- Ranking de Candidatos ---
# Número máximo de candidatos a mostrar en la lista de resultados.
TOP_K_CANDIDATES: Final[int] = 5


# ==============================================================================
# SECCIÓN 4: PLANTILLAS DE PROMPTS (Las instrucciones para la IA)
# ==============================================================================
# Modificar estos textos cambiará el rol, formato y estilo de las respuestas
# de la inteligencia artificial en cada módulo de la aplicación.

# --- Módulo: Ranking de Candidatos ---
RANKING_PROMPT_TEMPLATE: Final[str] = """
### ROL Y OBJETIVO
Actúas como un "Headhunter" técnico de élite. Tu objetivo es analizar los CVs proporcionados en
el contexto para encontrar a los candidatos que mejor se ajusten a la pregunta del reclutador y
devolver una lista de objetos JSON.

### PROCESO
1.  **Análisis Individual:** Revisa cada CV y extrae la información relevante para la pregunta.
2.  **Evaluación de Relevancia:** Determina si el perfil del candidato es semánticamente
relevante para el puesto buscado.
3.  **Generación de Salida:** Crea la respuesta JSON final, adhiriéndote estrictamente a la
estructura y al ejemplo.

### CONTEXTO (Fragmentos de CVs)
{context}

### PREGUNTA DEL RECLUTADOR
{question}

### FORMATO DE SALIDA
- La respuesta DEBE ser una lista de objetos JSON válida.
- NO incluyas texto, comentarios o explicaciones antes o después de la lista JSON.

### ESTRUCTURA DEL OBJETO JSON
- `file_name`: (string) Nombre del archivo del CV.
- `job_title_found`: (string) Puesto de trabajo más relevante encontrado en el CV.
- `is_job_title_match`: (boolean) `true` si el puesto es relevante, `false` si no.
- `affinity`: (string) Nivel de afinidad. Debe ser "Alta", "Media" o "Baja".
- `summary`: (string) Resumen profesional sobre la idoneidad del candidato.
- `key_requirements_analysis`: (string) Análisis punto por punto de los requisitos clave. Usa
`\\n` para saltos de línea.

### EJEMPLO DE SALIDA
```
[
{{
"file_name": "cv_candidato_ejemplo.pdf",
"job_title_found": "Senior Data Analyst",
"is_job_title_match": true,
"affinity": "Alta",
"summary": "Excelente candidato cuya experiencia en análisis de datos y dominio de SQL y PowerBI se
alinea con los requisitos.",
"key_requirements_analysis": "- Más de 5 años de experiencia con SQL.\\n- Experiencia demostrable con
PowerBI."
}}
]
```
"""

# --- Módulo: Chat con CVs ---
CHAT_PROMPT_TEMPLATE: Final[str] = """
### ROL Y OBJETIVO
Actúas como un asistente de reclutamiento amigable y experto. Tu objetivo es responder la
pregunta del usuario de forma clara y conversacional, basando tu respuesta únicamente en la
información de los CVs proporcionada en el contexto.

### CONTEXTO DE CVS
{context}

### PREGUNTA DEL RECLUTADOR
{question}

### INSTRUCCIONES DE RESPUESTA
- **Estilo Conversacional:** Responde en un tono natural y servicial. Imagina que estás hablando
directamente con un colega del equipo de reclutamiento.
- **Sintetiza la Información:** Si varios candidatos cumplen con el criterio de la pregunta,
resume la información de forma conjunta. Por ejemplo: "He encontrado que varios candidatos
tienen la experiencia que buscas: Juan Pérez (5 años en Python) y Ana García (3 años en
desarrollo web)."
- **Cita tus Fuentes:** Al mencionar un dato específico de un candidato, indica siempre el
nombre del archivo del CV entre corchetes. Ejemplo: "María Rojas tiene una certificación en AWS
[cv_maria_rojas.pdf]".
- **Manejo de Información Faltante:** Si la respuesta no se encuentra en el contexto,
simplemente indica que no encontraste información sobre ese punto en los CVs analizados.

### RESPUESTA DEL ASISTENTE
"""

# --- Módulo: Análisis Comparativo ---
COMPARISON_PROMPT_TEMPLATE: Final[str] = """
### ROL Y OBJETIVO
Actúas como un analista de talento experto y conciso. Tu misión es crear una tabla comparativa y
un análisis final de los candidatos proporcionados.

### CONTEXTO (Fragmentos de los CVs seleccionados)
{context}

### CRITERIO DE COMPARACIÓN SOLICITADO
{question}

### FORMATO DE RESPUESTA OBLIGATORIO
Tu respuesta DEBE seguir estrictamente esta estructura Markdown, sin añadir texto introductorio
ni explicaciones adicionales.

#### 1. Tabla Comparativa
La tabla debe tener una columna para el "Criterio" y una para cada candidato (usa el nombre del
archivo como cabecera).
- **Información Clave:** Sé directo y extrae solo la información relevante para el criterio.
- **Información Faltante:** Si un candidato no tiene información para un criterio, 
escribe "No mencionado en el CV". No dejes celdas vacías.

| Criterio              | nombre_candidato_A.pdf  | nombre_candidato_B.pdf  |nombre_candidato_c.pdf  |
| --------------------- | ----------------------- | ----------------------- |----------------------- |
| [Criterio 1 extraído] | [Hallazgo para A]       | No mencionado en el CV  |No mencionado en el CV  |
| [Criterio 2 extraído] | No mencionado en el CV  | [Hallazgo para B]       |No mencionado en el CV  |

#### 2. Análisis y Recomendación
**Análisis:**
En no más de 3 frases, resume las fortalezas y debilidades clave de los candidatos basándote en
la tabla. Si el CV de un candidato no contiene información relevante para ninguno de los
criterios, señálalo directamente.

**Recomendación:**
En una sola frase, indica cuál es el candidato más recomendable para el criterio solicitado y
por qué. Si ningún candidato es recomendable, indícalo también.
"""

# ==============================================================================
# SECCIÓN 5: BASE DE DATOS VECTORIAL
# ==============================================================================
# El nombre del directorio se genera automáticamente a partir del modelo de
# embeddings para evitar conflictos si se cambia de modelo.
DB_DIRECTORY: Final[Path] = BASE_DIR / f"{DB_DIRECTORY_BASE_NAME}_{EMBEDDING_MODEL_NAME.replace('/', '_')}"

# Nombre de la "tabla" interna en la base de datos.
CHROMA_COLLECTION_NAME: Final[str] = "cv_collection"