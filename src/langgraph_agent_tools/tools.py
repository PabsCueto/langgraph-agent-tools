import os

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

BASE_URL = os.getenv(
    "URL_SHORTENER_BASE_URL",
    "https://vqz32732g8.execute-api.us-east-1.amazonaws.com/Prod",
)
API_KEY = os.getenv("URL_SHORTENER_API_KEY")


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
