---
title: BioMind
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# BioMind turns live arXiv biomedical literature into grounded answers with exact-term BM25 retrieval.

## Overview
BioMind is a biomedical research assistant that searches live arXiv papers, indexes them with BM25, and answers questions using a Groq-hosted LLM grounded in retrieved abstracts. It is built for researchers, students, and biotech builders who need fast paper discovery without relying on stale local corpora. BM25 is intentionally used instead of vector search because biomedical queries often depend on exact matches for drugs, gene symbols, pathways, and protein names where loose semantic retrieval can be unsafe. The project is portfolio-worthy because it combines live arXiv ingestion, vectorless RAG, a production-style FastAPI backend, a Gradio frontend, and both local and remote MCP server access for agent tool use.

## Why BM25 for Biomedical Research?
Biomedical search often fails when semantic retrieval over-generalizes precise terminology. Exact identifiers such as drug names, gene IDs, and protein sequences need direct lexical matching so the system retrieves the right papers instead of merely related concepts. A search for `BRCA1` should return BRCA1 papers, not papers about vaguely similar cancer genetics topics that happen to live nearby in embedding space. BM25 makes that tradeoff explicit and predictable.

## Architecture
```text
User → Gradio UI → FastAPI → arXiv API (live papers)
                           → BM25 Indexer → Groq LLM → Answer
AI Agent → Remote MCP (/mcp/sse, /mcp/messages) → search_papers / ask_biomind tools
Claude Desktop / local client → stdio MCP server → same BioMind tools
```

## Tech Stack
| Component | Technology | Purpose |
| --- | --- | --- |
| Paper ingestion | arXiv Python library | Fetch live biomedical and AI-adjacent research papers |
| Retrieval | rank-bm25 | Build a vectorless BM25 index over titles and abstracts |
| LLM orchestration | LangChain + Groq | Generate grounded answers with cited sources |
| Backend API | FastAPI | Serve search, question-answering, and index status endpoints |
| Frontend | Gradio | Provide a simple research workflow UI |
| Agent integration | MCP Python SDK | Expose BioMind as tools for external AI agents |
| Runtime | uv + Python 3.11 | Manage dependencies, locking, and execution |
| Deployment | Docker + uv | Containerize the full application stack with the same resolver |

## Getting Started

### Using uv
```bash
git clone https://github.com/yourusername/BioMind
cd BioMind
uv sync
cp .env.example .env   # add your GROQ_API_KEY
uv run python main.py
```

### Exporting requirements.txt for environments that require it
```bash
uv export --format requirements-txt --no-hashes > requirements.txt
```

## API Reference

### FastAPI Endpoints

`POST /search`
```json
{
  "input": {
    "query": "CRISPR gene editing",
    "max_results": 10
  },
  "output": {
    "papers": [
      {
        "title": "string",
        "authors": "string",
        "summary": "string",
        "published": "YYYY-MM-DD",
        "pdf_url": "string",
        "arxiv_id": "string"
      }
    ],
    "total": 1,
    "query": "CRISPR gene editing"
  }
}
```

`POST /ask`
```json
{
  "input": {
    "query": "CRISPR cancer treatment",
    "question": "What are the latest findings?",
    "k": 5
  },
  "output": {
    "answer": "string",
    "sources": [
      {
        "title": "string",
        "arxiv_id": "string"
      }
    ],
    "papers_searched": 5,
    "query": "CRISPR cancer treatment"
  }
}
```

`GET /index/status`
```json
{
  "output": {
    "indexed_papers": 10,
    "cache_size": 25
  }
}
```

### MCP Tools

`search_papers(query: str, max_results: int = 10)`
```json
{
  "input": {
    "query": "protein folding",
    "max_results": 10
  },
  "output": {
    "papers": [
      {
        "title": "string",
        "authors": "string",
        "summary": "string",
        "published": "YYYY-MM-DD",
        "pdf_url": "string",
        "arxiv_id": "string"
      }
    ],
    "total": 1
  }
}
```

`ask_biomind(query: str, question: str)`
```json
{
  "input": {
    "query": "metformin diabetes interactions",
    "question": "What side effects are reported?"
  },
  "output": {
    "answer": "string",
    "sources": [
      {
        "title": "string",
        "arxiv_id": "string"
      }
    ],
    "papers_searched": 5,
    "fetched_count": 10
  }
}
```

`get_index_status()`
```json
{
  "input": {},
  "output": {
    "indexed_papers": 10,
    "cache_size": 25
  }
}
```

### Remote MCP Endpoints

`GET /mcp`
```json
{
  "output": {
    "server": "biomind",
    "transport": "sse",
    "sse_endpoint": "/mcp/sse",
    "message_endpoint": "/mcp/messages"
  }
}
```

`GET /mcp/sse`
```text
Opens a remote MCP Server-Sent Events session and sends the client the POST message endpoint with a session_id.
```

`POST /mcp/messages?session_id=<id>`
```json
{
  "input": "JSON-RPC client message for the active MCP session",
  "output": "202 Accepted"
}
```

## Project Structure
```text
BioMind/
├── app/
│   ├── __init__.py
│   ├── fetcher.py
│   ├── indexer.py
│   ├── chain.py
│   └── api.py
├── mcp_server/
│   ├── __init__.py
│   └── server.py
├── data/
│   └── .gitkeep
├── app.py
├── main.py
├── mcp_config.json
├── .env.example
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── Dockerfile
└── README.md
```

## Disclaimer
"BioMind is a research tool built for educational and portfolio purposes. It is not a medical device and should not be used for clinical decision making."
