# langgraph-agent-tools

Agente conversacional construido con LangChain y LangGraph que administra un
URL shortener propio, desplegado en AWS (Lambda + API Gateway + DynamoDB),
usando lenguaje natural.

## Por qué existe este proyecto

Aprender LangChain y LangGraph resolviendo el mismo problema dos veces:

1. Primero con `create_agent` de LangChain — la forma rápida de darle
   herramientas a un modelo.
2. Después como un `StateGraph` explícito de LangGraph — la forma con control
   total sobre el estado, los bordes condicionales y los bucles.

Construir ambas versiones sobre el mismo caso es lo que deja explicar con
seguridad en qué se diferencian los dos frameworks, en vez de repetir la
teoría sin haberla probado.

## Stack

- Python 3.13, gestionado con `uv`
- LangChain (`create_agent`) / LangGraph (`StateGraph`)
- Google Gemini (`gemini-3.1-flash-lite`) vía `langchain-google-genai` — nivel
  gratuito sin tarjeta, suficiente para este alcance
- httpx para llamar la API propia ya desplegada en AWS

## Setup

1. `uv sync`
2. Copia `.env.example` a `.env` y llena tus credenciales (API key de Gemini
   y `x-api-key` de tu API Gateway)
3. Corre cualquiera de las dos versiones:
   - `uv run langgraph-agent-tools` — versión `create_agent`
   - `uv run python -m langgraph_agent_tools.graph_agent` — versión `StateGraph`

## create_agent vs StateGraph: la comparación real

Construí el mismo agente (dos tools: crear un link corto, consultar sus
estadísticas) con los dos enfoques, sobre el mismo caso, para comparar de
verdad en vez de repetir la teoría:

| | `create_agent` | `StateGraph` |
|---|---|---|
| Líneas de código | ~10 | ~40 |
| El bucle (pensar → llamar tool → pensar) | Lo maneja LangChain, no se ve | Lo defines tú: nodo agente, nodo herramientas, un edge condicional y un edge que cierra el bucle |
| Qué tan rápido arrancas | Inmediato | Necesitas entender `TypedDict`, `add_messages`, `ToolNode`, `tools_condition` antes de escribir nada |
| Cuándo lo usarías | Prototipo rápido, un solo agente sin lógica especial | Necesitas inspeccionar o interrumpir el flujo, human-in-the-loop, multi-agente, persistencia |

Con las mismas dos tools y el mismo modelo, el resultado final fue idéntico
en ambas versiones — la diferencia no está en qué responden, está en cuánto
control y visibilidad tienes sobre cómo llegaron ahí.

## Bugs encontrados

- **Alucinación de URL corta**: la tool `crear_link_corto` originalmente
  regresaba el JSON crudo de la API (`shortcode`, `original_url`), sin la URL
  corta ya armada. El modelo, al no tener ese dato explícito, la inventó
  combinando `original_url` + shortcode — un link que parecía válido pero no
  redirigía a nada. Se reprodujo igual en las dos versiones (`create_agent` y
  `StateGraph`), confirmando que no era un problema del framework sino de
  diseño de la tool. Corrección: la tool ahora arma la URL completa en código
  antes de devolverla, para que el modelo solo la repita en vez de
  construirla. Lección: cualquier dato exacto (URLs, IDs, formatos) lo arma
  el código, nunca el modelo.

- **Formato de respuesta de Gemini 3.x**: `AIMessage.content` deja de ser un
  string plano y pasa a ser una lista de bloques (`[{"type": "text", "text":
  ..., "extras": {"signature": ...}}]`) porque Gemini 3 adjunta una firma
  criptográfica a cada bloque de razonamiento (thought signature) para
  encadenar llamadas a herramientas con seguridad. Resuelto con un helper
  (`utils.extraer_texto`) que normaliza ambos formatos.

  - **Incompatibilidad de plataforma (Chroma + onnxruntime)**: la elección más
  común en tutoriales de RAG es Chroma como base vectorial, pero su
  dependencia `onnxruntime` dejó de publicar wheels para macOS Intel (solo
  soporta Apple Silicon con macOS 14+). Corrección: se cambió a
  `InMemoryVectorStore` de `langchain-core` — sin dependencias externas, y
  mejor elección de cualquier forma para el tamaño de este proyecto.

- **Orden de import y variables de entorno**: `rag.py` construye el
  retriever (que necesita `GOOGLE_API_KEY`) en el momento del import, no
  cuando se llama una función. Como Python ejecuta el módulo completo al
  importarlo, sin su propio `load_dotenv()` dependía silenciosamente de qué
  otro archivo lo importara primero. Lección: cada módulo que lee variables
  de entorno debe cargarlas por sí mismo, nunca asumir que ya se cargaron.

## Estado actual

- [x] Entorno y dependencias con `uv`
- [x] Tools que llaman los endpoints reales del url-shortener
- [x] Primer agente funcional con `create_agent`
- [x] Misma lógica reconstruida como `StateGraph`
- [x] Documentar decisiones de diseño y bugs reales encontrados
- [x] Tercera tool con RAG sobre la documentación del proyecto (`docs/`)