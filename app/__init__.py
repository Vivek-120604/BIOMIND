"""BioMind application package."""

from __future__ import annotations

import httpx
import gradio as gr

__version__ = "1.0.0"

# Gradio interface that calls FastAPI backend
FASTAPI_BASE_URL = "http://127.0.0.1:8000"


def search_papers(query: str, max_results: int = 10) -> str:
    """Call /search endpoint and return formatted results."""
    try:
        response = httpx.post(
            f"{FASTAPI_BASE_URL}/search",
            json={"query": query, "max_results": max_results},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get("papers"):
            return "No papers found. Try a different search query."
        
        results = f"Found {data['total']} papers for: {query}\n\n"
        for i, paper in enumerate(data["papers"][:max_results], 1):
            results += f"{i}. **{paper['title']}**\n"
            results += f"   Authors: {paper['authors']}\n"
            results += f"   Published: {paper['published']}\n"
            results += f"   Summary: {paper['summary'][:200]}...\n\n"
        return results
    except Exception as e:
        return f"Error searching papers: {str(e)}"


def ask_question(query: str, question: str, k: int = 5) -> str:
    """Call /ask endpoint and return grounded answer."""
    try:
        response = httpx.post(
            f"{FASTAPI_BASE_URL}/ask",
            json={"query": query, "question": question, "k": k},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        
        result = f"**Answer:** {data['answer']}\n\n"
        result += f"**Sources ({len(data.get('sources', []))} papers):**\n"
        for i, source in enumerate(data.get("sources", []), 1):
            if isinstance(source, dict):
                result += f"{i}. [{source['title']}](https://arxiv.org/abs/{source['arxiv_id']})\n"
            else:
                result += f"{i}. {source}\n"
        return result
    except Exception as e:
        return f"Error answering question: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="BioMind 🧬") as demo:
    gr.Markdown("""
    # 🧬 BioMind: Live Biomedical Research Assistant
    
    Search live arXiv biomedical papers and get AI-powered answers grounded in real research.
    """)
    
    with gr.Tab("Search Papers"):
        search_input = gr.Textbox(
            label="Search Query",
            placeholder="e.g., BRCA1 mutations breast cancer",
            lines=2
        )
        search_max = gr.Slider(1, 50, value=10, step=1, label="Max Results")
        search_btn = gr.Button("Search", variant="primary")
        search_output = gr.Markdown(label="Results")
        
        search_btn.click(
            search_papers,
            inputs=[search_input, search_max],
            outputs=search_output
        )
    
    with gr.Tab("Ask Question"):
        query_input = gr.Textbox(
            label="Search Query",
            placeholder="e.g., BRCA1 mutations breast cancer",
            lines=2
        )
        question_input = gr.Textbox(
            label="Question",
            placeholder="e.g., What are the latest treatments?",
            lines=2
        )
        k_input = gr.Slider(1, 20, value=5, step=1, label="Papers to Retrieve")
        ask_btn = gr.Button("Ask", variant="primary")
        ask_output = gr.Markdown(label="Answer")
        
        ask_btn.click(
            ask_question,
            inputs=[query_input, question_input, k_input],
            outputs=ask_output
        )
    
    gr.Markdown("""
    ---
    **Note:** This interface calls a FastAPI backend that fetches live papers from arXiv,
    indexes them with BM25, and uses Groq LLM for grounded answers.
    """)
