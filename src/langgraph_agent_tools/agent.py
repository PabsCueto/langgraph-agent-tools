from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from .rag import buscar_en_documentacion
from .tools import borrar_link, crear_link_corto, obtener_stats
from .utils import extraer_texto, imprimir_rastro

load_dotenv()

# Note: the create_agent API is recent (LangChain 1.0, October 2025) and may change.
# tener pequeños cambios entre versiones. Si algo aquí truena, revisa
# https://docs.langchain.com/oss/python/learn para el ejemplo más actual.

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

# checkpointer es obligatorio para poder usar interrupt(): sin él, LangGraph
# no tiene dónde guardar el estado mientras espera tu respuesta.
agent = create_agent(
    model,
    tools=[crear_link_corto, obtener_stats, buscar_en_documentacion, borrar_link],
    checkpointer=InMemorySaver(),
)

# thread_id identifica esta "conversación" para el checkpointer. Para un
# script de terminal, un valor fijo es suficiente.
CONFIG = {"configurable": {"thread_id": "sesion-terminal"}}


def main() -> None:
    pregunta = input("Pídele algo al agente: ")
    resultado = agent.invoke({"messages": [HumanMessage(content=pregunta)]}, config=CONFIG)

    # Si el grafo se pausó, el resultado trae la clave "__interrupt__" en vez
    # de haber terminado normalmente. Mientras siga apareciendo, seguimos
    # preguntando y reanudando con Command(resume=...).
    while "__interrupt__" in resultado:
        pregunta_confirmacion = resultado["__interrupt__"][0].value
        print(f"\n⏸  {pregunta_confirmacion}")
        respuesta_humano = input("> ")
        resultado = agent.invoke(Command(resume=respuesta_humano), config=CONFIG)

    imprimir_rastro(resultado["messages"])
    print("Respuesta final:", extraer_texto(resultado["messages"][-1]))


if __name__ == "__main__":
    main()
