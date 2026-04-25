"""Builds BM25 index over papers and retrieves relevant ones."""

from __future__ import annotations

from rank_bm25 import BM25Okapi

_index: BM25Okapi | None = None
_papers: list[dict] = []
_corpus: list[list[str]] = []


def build_index(papers: list[dict]) -> None:
    """Build BM25 index from a list of paper dicts.
    
    Args:
        papers: List of paper dictionaries containing title and summary.
    """
    global _index, _papers, _corpus
    _papers = papers
    _corpus = [
        (p["title"] + " " + p["summary"]).lower().split()
        for p in papers
    ]
    _index = BM25Okapi(_corpus)


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Retrieve top-k most relevant papers for a query string.
    
    Args:
        query: Search query string to retrieve papers for.
        k: Number of top results to return.
        
    Returns:
        List of top-k paper dictionaries with BM25 scores.
    """
    if _index is None or not _papers:
        return []
    
    tokens = query.lower().split()
    scores = _index.get_scores(tokens)
    top_k_indices = sorted(
        range(len(scores)), 
        key=lambda i: scores[i], 
        reverse=True
    )[:k]
    
    results: list[dict] = []
    for i in top_k_indices:
        paper = dict(_papers[i])
        paper["bm25_score"] = float(scores[i])
        results.append(paper)
    
    return results


def get_index_size() -> int:
    """Return number of indexed papers.
    
    Returns:
        Count of papers in the current index.
    """
    return len(_papers)
