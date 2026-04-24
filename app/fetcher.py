"""Utilities for fetching biomedical research papers from arXiv."""

from __future__ import annotations

from typing import Dict, List

import arxiv

ALLOWED_CATEGORY_PREFIXES = ("q-bio", "cs.AI", "cs.LG", "stat.ML")
_paper_cache: List[Dict[str, str]] = []
_paper_ids: set[str] = set()


def _is_allowed_category(categories: List[str]) -> bool:
    """Return True when a paper belongs to one of the supported arXiv categories."""

    for category in categories:
        for allowed in ALLOWED_CATEGORY_PREFIXES:
            if category == allowed or category.startswith(f"{allowed}."):
                return True
    return False


def fetch_papers(query: str, max_results: int = 10) -> list[dict]:
    """Fetch papers from arXiv, filter them by category, and cache unique results."""

    if not query or not query.strip():
        return []

    search = arxiv.Search(
        query=query.strip(),
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    client = arxiv.Client()
    papers: list[dict] = []

    for result in client.results(search):
        categories = list(getattr(result, "categories", []) or [])
        if not _is_allowed_category(categories):
            continue

        paper = {
            "title": result.title.strip(),
            "authors": ", ".join(author.name for author in result.authors),
            "summary": " ".join(result.summary.split()),
            "published": result.published.strftime("%Y-%m-%d"),
            "pdf_url": result.pdf_url,
            "arxiv_id": result.entry_id.rsplit("/", maxsplit=1)[-1],
        }
        papers.append(paper)

        if paper["arxiv_id"] not in _paper_ids:
            _paper_cache.append(paper)
            _paper_ids.add(paper["arxiv_id"])

    return papers


def get_cached_papers() -> list[dict]:
    """Return a copy of the in-memory paper cache collected during this process."""

    return list(_paper_cache)


def clear_cache() -> None:
    """Clear all cached papers so the application starts with a fresh state."""

    _paper_cache.clear()
    _paper_ids.clear()

