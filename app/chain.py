"""LLM orchestration for answering biomedical questions over BM25 results."""

from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app import fetcher, indexer

SYSTEM_PROMPT = (
    "You are BioMind, an expert biomedical research assistant. "
    "Answer questions based strictly on the provided research papers. "
    "Always cite the paper title and authors when referencing "
    "information. If the answer cannot be found in the provided "
    "papers, say 'I could not find relevant information in the "
    "current search results. Try refining your search query.' "
    "Never hallucinate medical or scientific facts."
)


def _format_context(papers: list[dict]) -> str:
    """Turn retrieved papers into a readable context block for the LLM."""

    if not papers:
        return "No papers were retrieved."

    sections: list[str] = []
    for index, paper in enumerate(papers, start=1):
        sections.append(
            "\n".join(
                [
                    f"Paper {index}",
                    f"Title: {paper['title']}",
                    f"Authors: {paper['authors']}",
                    f"Published: {paper['published']}",
                    f"Summary: {paper['summary']}",
                ]
            )
        )
    return "\n\n".join(sections)


def answer_question(question: str, papers: list[dict]) -> dict:
    """Answer a question using only the supplied papers as grounded context."""

    load_dotenv()
    sources = [
        {"title": paper["title"], "arxiv_id": paper["arxiv_id"]}
        for paper in papers
    ]

    if not papers:
        return {
            "answer": (
                "I could not find relevant information in the current search "
                "results. Try refining your search query."
            ),
            "sources": sources,
            "papers_searched": 0,
        }

    llm = ChatGroq(model="llama3-8b-8192", temperature=0)
    context = _format_context(papers)
    user_prompt = (
        f"Question: {question}\n\n"
        f"Research papers:\n{context}\n\n"
        "Write a concise answer grounded only in these papers."
    )
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    return {
        "answer": response.content,
        "sources": sources,
        "papers_searched": len(papers),
    }


def search_and_answer(query: str, question: str = None, k: int = 5) -> dict:
    """Fetch papers, build a BM25 index, retrieve the best matches, and answer a question."""

    effective_question = question or query
    papers = fetcher.fetch_papers(query)
    indexer.build_index(papers)
    retrieved_papers = indexer.retrieve(effective_question, k=k)
    answer = answer_question(effective_question, retrieved_papers)
    answer["fetched_count"] = len(papers)
    return answer

