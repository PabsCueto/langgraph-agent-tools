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

## create_agent vs StateGraph

Con las mismas dos tools y el mismo modelo, el resultado final fue idéntico
en ambas versiones — la diferencia no está en qué responden, está en cuánto
control y visibilidad tienes sobre cómo llegaron ahí. create_agent resuelve
el bucle de pensar/llamar-tool/pensar por debajo; StateGraph lo expone como
un nodo agente, un nodo de herramientas, un borde condicional y un borde que
cierra el bucle.

## Bugs encontrados

- Alucinación de URL corta: la tool crear_link_corto originalmente regresaba
  el JSON crudo de la API (shortcode, original_url), sin la URL corta ya
  armada. El modelo, al no tener ese dato explícito, la inventó combinando
  original_url más el shortcode — un link que parecía válido pero no
  redirigía a nada. Corrección: la tool ahora arma la URL completa en código
  antes de devolverla. Lección: cualquier dato exacto lo arma el código,
  nunca el modelo.

- Formato de respuesta de Gemini 3.x: AIMessage.content deja de ser un
  string plano y pasa a ser una lista de bloques porque Gemini 3 adjunta una
  firma criptográfica (thought signature) a cada bloque de razonamiento.
  Resuelto con un helper que normaliza ambos formatos.
