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
seguridad en qué se diferencian los dos frameworks.

## Stack

- Python 3.13, gestionado con `uv`
- LangChain (`create_agent`) / LangGraph (`StateGraph`)
- httpx para llamar la API propia ya desplegada en AWS

## Setup

1. `uv sync`
2. Copia `.env.example` a `.env` y llena tus credenciales (API key del modelo
   y `x-api-key` de tu API Gateway)
3. `uv run langgraph-agent-tools` (o `uv run python -m langgraph_agent_tools.agent`)

## Estado actual

- [x] Entorno y dependencias con `uv`
- [x] Tools que llaman los endpoints reales del url-shortener
- [x] Primer agente funcional con `create_agent`
- [ ] Misma lógica reconstruida como `StateGraph`
- [ ] Documentar decisiones de diseño y bugs reales encontrados

## Bugs encontrados

- **Alucinación de URL corta**: la tool `crear_link_corto` originalmente regresaba
  el JSON crudo de la API (`shortcode`, `original_url`), sin la URL corta ya
  armada. El modelo, al no tener ese dato explícito, la inventó combinando
  `original_url` + shortcode — un link que parecía válido pero no redirigía a
  nada. Corrección: la tool ahora arma la URL completa en código antes de
  devolverla, para que el modelo solo la repita en vez de construirla.