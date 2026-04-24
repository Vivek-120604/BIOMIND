"""BM25 indexing and retrieval helpers for BioMind."""

from __future__ import annotations

import logging
from typing import List

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

_corpus: List[List[str]] = []
_papers: list[dict] = []
_index: BM25Okapi | None = None


def _tokenize(text: str) -> list[str]:
    """Normalize a string into lowercase whitespace tokens for BM25 retrieval."""

    return text.lower().split()


def build_index(papers: list[dict]) -> BM25Okapi:
    """Build a BM25 index from paper titles and abstracts and store it for reuse."""

    global _corpus, _papers, _index

    _papers = list(papers)
    _corpus = [
        _tokenize(f"{paper.get('title', '')} {paper.get('summary', '')}")
        for paper in _papers
    ]
    _index = BM25Okapi(_corpus) if _corpus else BM25Okapi([[]])
    return _index


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Retrieve the top matching papers from the current BM25 index for a query."""

    if not _papers or _index is None or not _corpus:
        logger.warning("BM25 index is empty; returning no search results.")
        return []

    query_tokens = _tokenize(query)
    scores = _index.get_scores(query_tokens)
    ranked = sorted(
        enumerate(scores),
        key=lambda item: item[1],
        reverse=True,
    )

    results: list[dict] = []
    for idx, score in ranked[:k]:
        paper = dict(_papers[idx])
        paper["bm25_score"] = float(score)
        results.append(paper)

    return results


def get_index_size() -> int:
    """Return the number of papers currently stored in the active BM25 index."""

    return len(_papers)

