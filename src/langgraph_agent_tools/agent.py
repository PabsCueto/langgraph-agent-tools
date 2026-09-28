from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .tools import crear_link_corto, obtener_stats

load_dotenv()

# Nota: la API de create_agent es reciente (LangChain 1.0, octubre 2025) y puede
# tener pequeños cambios entre versiones. Si algo aquí truena, revisa
# https://docs.langchain.com/oss/python/learn para el ejemplo más actual.

model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

agent = create_agent(model, tools=[crear_link_corto, obtener_stats])


def _extraer_texto(mensaje) -> str:
    """Gemini 3.x regresa el contenido como una lista de bloques (para
    soportar 'thought signatures'), no como string plano. Esto lo normaliza."""
    contenido = mensaje.content
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        return "".join(
            bloque.get("text", "")
            for bloque in contenido
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        )
    return str(contenido)


def main() -> None:
    pregunta = input("Pídele algo al agente: ")
    resultado = agent.invoke({"messages": [HumanMessage(content=pregunta)]})

    print("\n--- Rastro de mensajes (para verificar si sí llamó la tool) ---")
    for mensaje in resultado["messages"]:
        llamadas = getattr(mensaje, "tool_calls", None)
        extra = f" | tool_calls={llamadas}" if llamadas else ""
        print(f"[{mensaje.type}]{extra} content={mensaje.content}")
    print("--- fin del rastro ---\n")

    print("Respuesta final:", _extraer_texto(resultado["messages"][-1]))

if __name__ == "__main__":
    main()