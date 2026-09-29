from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from .rag import buscar_en_documentacion
from .tools import crear_link_corto, obtener_stats
from .utils import extraer_texto, imprimir_rastro

load_dotenv()


class State(TypedDict):
    # add_messages es el "reducer": en vez de reemplazar la lista de mensajes
    # en cada paso, sabe que debe agregarlos al final. Sin esto, cada nodo
    # borraría el historial del anterior.
    messages: Annotated[list, add_messages]


tools = [crear_link_corto, obtener_stats, buscar_en_documentacion]

# bind_tools() es lo que le "enseña" al modelo qué herramientas existen y con
# qué forma de argumentos — sin esto, jamás generaría un tool_call.
model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite").bind_tools(tools)


def nodo_agente(state: State) -> dict:
    """El único trabajo de este nodo: mirar los mensajes hasta ahora y decidir
    qué responder (texto final, o una llamada a herramienta)."""
    return {"messages": [model.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("agente", nodo_agente)
graph_builder.add_node("herramientas", ToolNode(tools))

graph_builder.add_edge(START, "agente")

# tools_condition ya viene incluido en LangGraph: revisa si el último mensaje
# trae tool_calls. Si sí, regresa "tools" (lo mapeamos a nuestro nodo
# "herramientas"); si no, regresa END y el grafo termina ahí.
graph_builder.add_conditional_edges(
    "agente",
    tools_condition,
    {"tools": "herramientas", END: END},
)

# Este edge es el que convierte esto en un bucle real: después de ejecutar
# la herramienta, siempre regresa al agente para que decida el siguiente paso
# (llamar otra herramienta, o ya responder con el resultado).
graph_builder.add_edge("herramientas", "agente")

graph = graph_builder.compile()


def main() -> None:
    pregunta = input("Pídele algo al agente (versión StateGraph): ")
    resultado = graph.invoke({"messages": [HumanMessage(content=pregunta)]})
    imprimir_rastro(resultado["messages"])
    print("Respuesta final:", extraer_texto(resultado["messages"][-1]))


if __name__ == "__main__":
    main()
