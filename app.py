"""Gradio UI for BioMind."""

from __future__ import annotations

import os

import httpx
import gradio as gr

BASE_URL = os.getenv("BIOMIND_API_URL", "http://127.0.0.1:8000")


def search_papers(query: str, max_results: int) -> tuple[str, list, str]:
    """Search arXiv papers and return as list for display.
    
    Args:
        query: Search query string.
        max_results: Maximum number of results.
        
    Returns:
        Tuple of (status_message, results_table, abstracts_text).
    """
    if not query.strip():
        return "Please enter a search query.", [], ""
    
    try:
        response = httpx.post(
            f"{BASE_URL}/search",
            json={"query": query, "max_results": int(max_results)},
            timeout=60.0,
        )
        if response.status_code == 200:
            data = response.json()
            papers = data["papers"]
            if not papers:
                return "No papers found.", [], ""
            
            rows = [
                [p["title"], p["authors"], p["published"], p["arxiv_id"]]
                for p in papers
            ]
            abstracts = "\n\n---\n\n".join(
                [f"**{p['title']}**\n\n"
                 f"*Authors:* {p['authors']}\n\n"
                 f"*Published:* {p['published']}\n\n"
                 f"{p['summary']}"
                 for p in papers]
            )
            return f"Found {len(papers)} papers.", rows, abstracts
        else:
            return f"Error: {response.text}", [], ""
    except Exception as e:
        return f"Error: {str(e)}", [], ""


def ask_question(query: str, question: str, k: int) -> tuple[str, str]:
    """Search papers and answer question using BM25 + Groq.
    
    Args:
        query: Search query to fetch papers.
        question: Question to answer.
        k: Number of papers to retrieve.
        
    Returns:
        Tuple of (answer_text, sources_text).
    """
    if not query.strip():
        return "Please enter a search query.", ""
    
    try:
        response = httpx.post(
            f"{BASE_URL}/ask",
            json={
                "query": query,
                "question": question if question.strip() else None,
                "k": int(k),
            },
            timeout=120.0,
        )
        if response.status_code == 200:
            data = response.json()
            answer = data["answer"]
            sources = data["sources"]
            papers_searched = data.get("papers_searched", 0)
            
            sources_md = ""
            if sources:
                sources_md = "### 📚 Sources\n\n"
                for source in sources:
                    sources_md += f"- **[{source['title']}]({source['pdf_url']})**\n"
                    sources_md += f"  arXiv: `{source['arxiv_id']}`\n"
            
            sources_md += f"\n\n*Papers searched: {papers_searched}*"
            
            return answer, sources_md
        else:
            return f"Error: {response.text}", ""
    except Exception as e:
        return f"Error: {str(e)}", ""


with gr.Blocks(
    title="BioMind",
    theme=gr.themes.Soft(),
    css="footer {visibility: hidden}"
) as demo:
    gr.Markdown(
        """
        # 🧬 BioMind
        **Biomedical Research Assistant powered by arXiv + BM25 + Groq**
        
        Search live research papers and get AI-powered answers grounded in real science.
        """
    )

    with gr.Tab("🔍 Search Papers"):
        with gr.Row():
            with gr.Column(scale=3):
                search_query = gr.Textbox(
                    label="Search Query",
                    placeholder="e.g. CRISPR gene editing cancer",
                    lines=2,
                )
            with gr.Column(scale=1):
                max_results_slider = gr.Slider(
                    minimum=5,
                    maximum=20,
                    value=10,
                    step=1,
                    label="Max Results",
                )
        
        search_button = gr.Button("Search arXiv", variant="primary", size="lg")
        search_status = gr.Textbox(
            label="Status",
            interactive=False,
            show_label=True,
        )
        
        results_table = gr.Dataframe(
            headers=["Title", "Authors", "Published", "arXiv ID"],
            interactive=False,
            label="Results",
        )
        
        with gr.Accordion("📄 Paper Abstracts", open=False):
            abstracts_output = gr.Markdown(label="Abstracts")

        search_button.click(
            fn=search_papers,
            inputs=[search_query, max_results_slider],
            outputs=[search_status, results_table, abstracts_output],
        )

    with gr.Tab("🧠 Ask a Question"):
        with gr.Row():
            with gr.Column():
                ask_query = gr.Textbox(
                    label="Search Query (what to fetch from arXiv)",
                    placeholder="e.g. metformin drug interactions diabetes",
                    lines=2,
                )
        
        with gr.Row():
            with gr.Column():
                ask_question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g. What are the main side effects reported?",
                    lines=3,
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                k_slider = gr.Slider(
                    minimum=3,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Papers to retrieve",
                )
        
        ask_button = gr.Button("Ask BioMind", variant="primary", size="lg")
        
        answer_output = gr.Textbox(
            label="Answer",
            interactive=False,
            lines=12,
        )
        
        with gr.Accordion("📚 Sources", open=True):
            sources_output = gr.Markdown(label="Sources")
        
        gr.Markdown(
            "_⚠️ **Disclaimer:** BioMind is for research purposes only. "
            "Always consult a qualified medical professional for medical advice._"
        )

        ask_button.click(
            fn=ask_question,
            inputs=[ask_query, ask_question_input, k_slider],
            outputs=[answer_output, sources_output],
        )
