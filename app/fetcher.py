"""Fetches research papers from arXiv API."""

from __future__ import annotations

import arxiv

_paper_cache: list[dict] = []


def fetch_papers(query: str, max_results: int = 10) -> list[dict]:
    """Fetch papers from arXiv for a given query. Returns list of dicts.
    
    Args:
        query: Search query string for arXiv.
        max_results: Maximum number of papers to return.
        
    Returns:
        List of paper dictionaries with title, authors, summary, etc.
    """
    global _paper_cache
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers: list[dict] = []
    for result in client.results(search):
        paper = {
            "title": result.title,
            "authors": ", ".join(a.name for a in result.authors),
            "summary": result.summary,
            "published": str(result.published.date()),
            "pdf_url": result.pdf_url,
            "arxiv_id": result.entry_id.split("/")[-1],
        }
        papers.append(paper)
    _paper_cache = papers
    return papers


def get_cached_papers() -> list[dict]:
    """Return currently cached papers.
    
    Returns:
        List of paper dictionaries from the most recent fetch.
    """
    return _paper_cache


def clear_cache() -> None:
    """Clear the paper cache."""
    global _paper_cache
    _paper_cache = []
