"""FastAPI application for BioMind."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import fetcher, indexer
from app.chain import search_and_answer

app = FastAPI(
    title="BioMind API",
    version="1.0.0",
    description="Biomedical research assistant powered by arXiv, BM25, and Groq"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    """Request model for paper search."""
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(default=10, ge=1, le=50, description="Max papers to return")


class AskRequest(BaseModel):
    """Request model for Q&A over papers."""
    query: str = Field(..., min_length=1, description="Search query for papers")
    question: str | None = Field(default=None, description="Question to answer")
    k: int = Field(default=5, ge=1, le=20, description="Papers to retrieve")


@app.post("/search")
def search_papers(request: SearchRequest) -> dict:
    """Fetch papers from arXiv for a query.
    
    Args:
        request: SearchRequest with query and max_results.
        
    Returns:
        Dictionary with papers list, total count, and query.
    """
    try:
        papers = fetcher.fetch_papers(request.query, request.max_results)
        return {
            "papers": papers,
            "total": len(papers),
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(request: AskRequest) -> dict:
    """Search papers and answer question using BM25 + Groq.
    
    Args:
        request: AskRequest with query, question, and k.
        
    Returns:
        Dictionary with answer, sources, papers_searched, and query.
    """
    try:
        result = search_and_answer(
            request.query,
            request.question,
            request.k
        )
        return {
            **result,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
def get_status() -> dict:
    """Health check and index status.
    
    Returns:
        Dictionary with status, indexed_papers count, and cache_size.
    """
    return {
        "status": "healthy",
        "indexed_papers": indexer.get_index_size(),
        "cache_size": len(fetcher.get_cached_papers()),
    }


@app.get("/health")
def health_check() -> dict:
    """Simple health check endpoint.
    
    Returns:
        Dictionary with ok status.
    """
    return {"status": "ok"}
