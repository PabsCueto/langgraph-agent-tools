import os

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.types import interrupt

load_dotenv()

BASE_URL = os.getenv(
    "URL_SHORTENER_BASE_URL",
    "https://vqz32732g8.execute-api.us-east-1.amazonaws.com/Prod",
)
API_KEY = os.getenv("URL_SHORTENER_API_KEY")
ADMIN_TOKEN = os.getenv("URL_SHORTENER_ADMIN_TOKEN")


def _headers() -> dict:
    if not API_KEY:
        raise RuntimeError(
            "Falta URL_SHORTENER_API_KEY en tu .env (copia .env.example a .env y llénalo)"
        )
    return {"x-api-key": API_KEY}


@tool
def crear_link_corto(url: str) -> str:
    """Crea un link corto para la URL dada usando el url-shortener desplegado en AWS."""
    response = httpx.post(f"{BASE_URL}/shorten", json={"url": url}, headers=_headers())
    response.raise_for_status()
    data = response.json()
    shortcode = data.get("shortcode")
    short_url = f"{BASE_URL}/{shortcode}"
    return f"shortcode: {shortcode} | link corto (funcional): {short_url} | url original: {data.get('original_url', url)}"


@tool
def obtener_stats(shortcode: str) -> str:
    """Obtiene las estadísticas (clics) de un shortcode existente."""
    response = httpx.get(f"{BASE_URL}/stats/{shortcode}", headers=_headers())
    response.raise_for_status()
    return str(response.json())


@tool
def borrar_link(shortcode: str) -> str:
    """Borra permanentemente un shortcode existente. Acción irreversible:
    pausa la ejecución y espera aprobación humana explícita antes de borrar nada."""
    if not ADMIN_TOKEN:
        raise RuntimeError(
            "Falta URL_SHORTENER_ADMIN_TOKEN en tu .env (lo sacas de Secrets Manager)"
        )

    # interrupt() congela el grafo aquí mismo y regresa el control a quien
    # llamó invoke(). El valor que pases queda disponible en
    # resultado["__interrupt__"][0].value para mostrárselo al humano.
    aprobado = interrupt(
        f"¿Confirmas borrar el shortcode '{shortcode}'? Esta acción no se puede deshacer. (si/no)"
    )

    # Al reanudar con Command(resume=...), ese valor es lo que regresa
    # interrupt() aquí — como si nunca se hubiera pausado.
    if str(aprobado).strip().lower() not in ("si", "sí", "s", "yes", "y"):
        return f"Borrado de '{shortcode}' cancelado — no se aprobó."

    headers = _headers()
    headers["x-admin-token"] = ADMIN_TOKEN
    response = httpx.delete(f"{BASE_URL}/admin/{shortcode}", headers=headers)
    response.raise_for_status()
    return f"Shortcode '{shortcode}' eliminado correctamente."
