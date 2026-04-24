"""FastAPI application for searching papers and asking BioMind questions."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import chain, fetcher, indexer

app = FastAPI(title="BioMind API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

