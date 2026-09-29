from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .rag import buscar_en_documentacion
from .tools import crear_link_corto, obtener_stats
from .utils import extraer_texto, imprimir_rastro

load_dotenv()

# Nota: la API de create_agent es reciente (LangChain 1.0, octubre 2025) y puede
# tener pequeños cambios entre versiones. Si algo aquí truena, revisa
# https://docs.langchain.com/oss/python/learn para el ejemplo más actual.

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

agent = create_agent(
    model,
    tools=[crear_link_corto, obtener_stats, buscar_en_documentacion],
)


def main() -> None:
    pregunta = input("Pídele algo al agente: ")
    resultado = agent.invoke({"messages": [HumanMessage(content=pregunta)]})
    imprimir_rastro(resultado["messages"])
    print("Respuesta final:", extraer_texto(resultado["messages"][-1]))


if __name__ == "__main__":
    main()
