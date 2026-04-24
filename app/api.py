"""FastAPI application for searching papers and asking BioMind questions."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import gradio as gr
from starlette.requests import Request
from starlette.routing import Route

from app import chain, fetcher, indexer
from mcp.server.sse import SseServerTransport
from mcp_server.core import server as mcp_server

app = FastAPI(title="BioMind API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_mcp_transport = SseServerTransport("/mcp/messages")


class SearchRequest(BaseModel):
    """Request body for searching live biomedical papers from arXiv."""

    query: str = Field(..., min_length=1)
    max_results: int = Field(default=10, ge=1, le=20)


class AskRequest(BaseModel):
    """Request body for asking a grounded question over fetched papers."""

    query: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    k: int = Field(default=5, ge=1, le=10)


@app.post("/search")
def search_papers(request: SearchRequest) -> dict:
    """Fetch papers from arXiv and return structured search results."""

    papers = fetcher.fetch_papers(request.query, max_results=request.max_results)
    return {
        "papers": papers,
        "total": len(papers),
        "query": request.query,
    }


@app.post("/ask")
def ask_question(request: AskRequest) -> dict:
    """Search papers, retrieve the most relevant ones, and answer the given question."""

    result = chain.search_and_answer(
        query=request.query,
        question=request.question,
        k=request.k,
    )
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "papers_searched": result["papers_searched"],
        "query": request.query,
    }


@app.get("/index/status")
def get_index_status() -> dict:
    """Return the current BM25 index size and the number of cached papers."""

    return {
        "indexed_papers": indexer.get_index_size(),
        "cache_size": len(fetcher.get_cached_papers()),
    }


@app.get("/health")
def healthcheck() -> dict:
    """Return a simple health response so deployments can check server readiness."""

    return {"status": "ok"}


@app.get("/mcp")
def mcp_info() -> dict:
    """Describe the public MCP endpoints exposed by this BioMind deployment."""

    return {
        "server": "biomind",
        "transport": "sse",
        "sse_endpoint": "/mcp/sse",
        "message_endpoint": "/mcp/messages",
    }


async def mcp_sse(request: Request):
    """Open a remote MCP SSE session so internet clients can call BioMind tools."""

    async with _mcp_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


async def mcp_messages(request: Request):
    """Receive JSON-RPC POST messages for an existing BioMind MCP SSE session."""

    await _mcp_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


app.router.routes.append(Route("/mcp/sse", endpoint=mcp_sse, methods=["GET"]))
app.router.routes.append(
    Route("/mcp/messages", endpoint=mcp_messages, methods=["POST"])
)


def _load_gradio_demo():
    """Load the root Gradio UI module and return the Blocks demo object."""

    module_path = Path(__file__).resolve().parent.parent / "app.py"
    spec = importlib.util.spec_from_file_location("biomind_ui", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the BioMind Gradio UI module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.demo


app = gr.mount_gradio_app(app, _load_gradio_demo(), path="/")
