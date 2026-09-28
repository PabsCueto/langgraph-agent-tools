def extraer_texto(mensaje) -> str:
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


def imprimir_rastro(mensajes) -> None:
    """Imprime cada mensaje del estado, incluyendo qué tool_calls decidió hacer el modelo."""
    print("\n--- Rastro de mensajes ---")
    for mensaje in mensajes:
        llamadas = getattr(mensaje, "tool_calls", None)
        extra = f" | tool_calls={llamadas}" if llamadas else ""
        print(f"[{mensaje.type}]{extra} content={mensaje.content}")
    print("--- fin del rastro ---\n")
