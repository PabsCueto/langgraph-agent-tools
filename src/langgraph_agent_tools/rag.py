from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# src/langgraph_agent_tools/rag.py -> sube 3 niveles para llegar a la raíz del repo
DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"

# src/langgraph_agent_tools/rag.py -> sube 3 niveles para llegar a la raíz del repo
DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"


def _cargar_documentos() -> list[Document]:
    documentos = []
    for archivo in sorted(DOCS_DIR.glob("*.md")):
        texto = archivo.read_text(encoding="utf-8")
        documentos.append(Document(page_content=texto, metadata={"fuente": archivo.name}))
    return documentos


def _construir_retriever():
    documentos = _cargar_documentos()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    fragmentos = splitter.split_documents(documentos)

    # Reutiliza tu misma GOOGLE_API_KEY — nivel gratuito confirmado para este modelo.
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # InMemoryVectorStore vive en langchain-core (ya instalado) — sin base de
    # datos externa ni dependencias pesadas. Se reconstruye en memoria cada
    # vez que arranca el programa.
    vectorstore = InMemoryVectorStore(embeddings)
    vectorstore.add_documents(fragmentos)
    return vectorstore.as_retriever(search_kwargs={"k": 3})


_retriever = _construir_retriever()


@tool
def buscar_en_documentacion(pregunta: str) -> str:
    """Busca en la documentación del proyecto (README, decisiones de diseño,
    bugs encontrados) para responder preguntas sobre cómo funciona este agente."""
    fragmentos = _retriever.invoke(pregunta)
    if not fragmentos:
        return "No encontré nada relevante en la documentación."
    return "\n\n---\n\n".join(
        f"(de {f.metadata.get('fuente', 'documento')}):\n{f.page_content}"
        for f in fragmentos
    )