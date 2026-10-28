# LangGraph Agent Tools

An AI agent built with LangChain and LangGraph, powered by Google Gemini, that operates a URL shortener API through tools. The same agent is implemented twice: once with LangChain's `create_agent` and once with a hand-built LangGraph `StateGraph`. Both versions share the same tool code.

## Features

- **Tool calling against a real API:** the agent creates short links and reads usage statistics from a URL shortener hosted on AWS.
- **Retrieval-augmented generation (RAG):** a documentation search tool backed by an in-memory vector store and Gemini embeddings. The agent answers from the documents instead of guessing.
- **Human-in-the-loop approval:** the `borrar_link` tool pauses the graph with LangGraph's `interrupt()` and deletes a link only after a human explicitly approves it.
- **Conversation memory:** each conversation is isolated by `thread_id` through a LangGraph checkpointer.

Tool names in the code are in Spanish: `crear_link_corto`, `obtener_stats`, `buscar_en_documentacion`, and `borrar_link`.

## Two implementations, one codebase

| Version | File | Approach |
|---|---|---|
| `create_agent` | `src/langgraph_agent_tools/agent.py` | High-level LangChain API; the agent loop is handled for you |
| `StateGraph` | `src/langgraph_agent_tools/graph_agent.py` | Explicit LangGraph graph with nodes, edges, and a checkpointer |

Shared code, such as model setup and tool definitions, lives in `utils.py`. Comparing the two versions shows what the high-level API hides and why an explicit graph is useful when you need control over routing, approvals, or persistence.

## Bug found during development

Early on, the model invented a short URL when the tool's output did not include the link in its response text. The fix was to make the tool return the complete URL, so the model copies data instead of generating it. This is a common failure mode: language models fill gaps in their context when a tool does not provide what they need.

## Setup

Requirements: Python 3.11 or newer, and a Google AI Studio API key (the free tier is enough).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your settings. The `.env` file is ignored by git and must never be committed. Check the code for the exact variable names, which include your Google API key and the URL shortener API settings.

## Running

```bash
python [FILE_CREATE_AGENT]
python [FILE_STATEGRAPH]
```

Try a request such as "Create a short link for https://example.com" or "Show the stats for <shortcode>". When you ask the agent to delete a link, it stops and waits for your approval in the terminal before running the deletion.

## Limitations

- The vector store lives in memory, so documents are re-indexed each time the program starts.
- Conversation memory is also in memory and is lost when the process exits.
- The URL shortener API is a demo deployment and may not be available at all times.
- The agent may answer questions it has no tool for, such as the current time. This is a known issue, documented but not yet fixed.

## License

MIT