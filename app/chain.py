"""Groq LLM chain that answers questions using BM25-retrieved papers."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app import fetcher, indexer

load_dotenv()

SYSTEM_PROMPT = """You are BioMind, an expert biomedical research assistant.
Answer questions based strictly on the provided research papers.
Always cite the paper title and authors when referencing information.
If the answer cannot be found in the provided papers, say:
'I could not find relevant information in the current search results. Try refining your search query.'
Never hallucinate medical or scientific facts."""


def build_llm() -> ChatGroq:
    """Create Groq LLM instance.
    
    Returns:
        Configured ChatGroq instance.
    """
    return ChatGroq(
        model="llama3-8b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )


def search_and_answer(
    query: str,
    question: str | None = None,
    k: int = 5
) -> dict:
    """Fetch papers, build BM25 index, retrieve top-k, answer with Groq.
    
    Args:
        query: Search query to fetch papers from arXiv.
        question: Specific question to answer. If None, uses query.
        k: Number of papers to retrieve for answering.
        
    Returns:
        Dictionary with answer, sources, and papers_searched count.
    """
    if question is None:
        question = query

    papers = fetcher.fetch_papers(query, max_results=10)
    if not papers:
        return {
            "answer": "No papers found for this query. Try a different search term.",
            "sources": [],
            "papers_searched": 0,
        }

    indexer.build_index(papers)
    retrieved = indexer.retrieve(question, k=k)

    if not retrieved:
        return {
            "answer": "No relevant papers found for this question.",
            "sources": [],
            "papers_searched": len(papers),
        }

    context = ""
    for i, p in enumerate(retrieved, 1):
        context += f"\n[{i}] Title: {p['title']}\n"
        context += f"Authors: {p['authors']}\n"
        context += f"Published: {p['published']}\n"
        context += f"Abstract: {p['summary']}\n"

    llm = build_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
    ]
    response = llm.invoke(messages)

    sources = [
        {
            "title": p["title"],
            "arxiv_id": p["arxiv_id"],
            "pdf_url": p["pdf_url"]
        }
        for p in retrieved
    ]

    return {
        "answer": response.content,
        "sources": sources,
        "papers_searched": len(papers),
    }

