from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

from .rag import buscar_en_documentacion
from .tools import borrar_link, crear_link_corto, obtener_stats
from .utils import extraer_texto, imprimir_rastro

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [crear_link_corto, obtener_stats, buscar_en_documentacion, borrar_link]
model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite").bind_tools(tools)


def nodo_agente(state: State) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("agente", nodo_agente)
graph_builder.add_node("herramientas", ToolNode(tools))

graph_builder.add_edge(START, "agente")
graph_builder.add_conditional_edges(
    "agente",
    tools_condition,
    {"tools": "herramientas", END: END},
)
graph_builder.add_edge("herramientas", "agente")

# checkpointer obligatorio para que interrupt() (dentro de borrar_link) tenga
# dónde guardar el estado mientras espera tu respuesta.
graph = graph_builder.compile(checkpointer=InMemorySaver())

CONFIG = {"configurable": {"thread_id": "sesion-terminal-stategraph"}}


def main() -> None:
    pregunta = input("Ask the agent something (StateGraph version): ")
    resultado = graph.invoke({"messages": [HumanMessage(content=pregunta)]}, config=CONFIG)

    while "__interrupt__" in resultado:
        pregunta_confirmacion = resultado["__interrupt__"][0].value
        print(f"\n⏸  {pregunta_confirmacion}")
        respuesta_humano = input("> ")
        resultado = graph.invoke(Command(resume=respuesta_humano), config=CONFIG)

    imprimir_rastro(resultado["messages"])
    print("Respuesta final:", extraer_texto(resultado["messages"][-1]))


if __name__ == "__main__":
    main()
