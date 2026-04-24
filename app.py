"""Gradio interface for BioMind."""

from __future__ import annotations

import gradio as gr

from app import chain, fetcher, indexer


def search_ui(query: str, max_results: int) -> tuple[list[list[str]], str]:
    """Search for papers through the BioMind core functions and format them for Gradio."""

    if not query.strip():
        return [], "Enter a search query to fetch biomedical papers."

    papers = fetcher.fetch_papers(query.strip(), max_results=int(max_results))
    rows = [
        [
            paper["title"],
            paper["authors"],
            paper["published"],
            paper["arxiv_id"],
        ]
        for paper in papers
    ]
    abstracts = []
    for index, paper in enumerate(papers, start=1):
        abstracts.append(
            "\n".join(
                [
                    f"{index}. {paper['title']}",
                    f"Authors: {paper['authors']}",
                    f"Published: {paper['published']}",
                    f"arXiv ID: {paper['arxiv_id']}",
                    f"PDF: {paper['pdf_url']}",
                    "",
                    paper["summary"],
                ]
            )
        )
    abstract_text = "\n\n" + ("\n\n" + ("-" * 80) + "\n\n").join(abstracts) if abstracts else "No papers found."
    return rows, abstract_text.strip()


def ask_ui(query: str, question: str, k: int) -> tuple[str, str, str]:
    """Ask BioMind a grounded question and return the answer, sources, and status text."""

    if not query.strip() or not question.strip():
        return (
            "Enter both a search query and a question.",
            "No sources available.",
            "Index status unavailable.",
        )

    result = chain.search_and_answer(
        query=query.strip(),
        question=question.strip(),
        k=int(k),
    )
    sources = "\n".join(
        f"- {source['title']} ({source['arxiv_id']})"
        for source in result["sources"]
    ) or "No sources available."
    status_text = (
        f"Indexed papers: {indexer.get_index_size()} | "
        f"Cached papers: {len(fetcher.get_cached_papers())} | "
        f"Papers searched for answer: {result['papers_searched']}"
    )
    return result["answer"], sources, status_text


with gr.Blocks(title="BioMind — Biomedical Research Assistant") as demo:
    gr.Markdown(
        "# 🧬 BioMind\n"
        "**Biomedical Research Assistant powered by arXiv + BM25 + Groq**\n"
        "Search live research papers and get AI-powered answers grounded \n"
        "in real science."
    )

    with gr.Tab("🔍 Search Papers"):
        query_input = gr.Textbox(
            label="Search Query",
            placeholder="e.g. CRISPR gene editing cancer",
        )
        max_results_input = gr.Slider(
            minimum=5,
            maximum=20,
            value=10,
            step=1,
            label="Max Results",
        )
        search_button = gr.Button("Search")
        search_results = gr.Dataframe(
            headers=["Title", "Authors", "Published", "arXiv ID"],
            datatype=["str", "str", "str", "str"],
            label="Paper Results",
            interactive=False,
            row_count=(0, "dynamic"),
            col_count=(4, "fixed"),
        )
        with gr.Accordion("📄 Paper Abstracts", open=False):
            abstracts_output = gr.Textbox(
                label="Abstracts",
                lines=20,
                interactive=False,
            )
        search_button.click(
            fn=search_ui,
            inputs=[query_input, max_results_input],
            outputs=[search_results, abstracts_output],
        )

    with gr.Tab("🧠 Ask a Question"):
        ask_query_input = gr.Textbox(
            label="Search Query",
            placeholder="e.g. metformin drug interactions diabetes",
        )
        question_input = gr.Textbox(
            label="Question",
            placeholder="e.g. What are the main side effects reported?",
        )
        k_input = gr.Slider(
            minimum=3,
            maximum=10,
            value=5,
            step=1,
            label="Number of Papers",
        )
        ask_button = gr.Button("Ask")
        answer_output = gr.Textbox(
            label="Answer",
            lines=10,
            interactive=False,
        )
        with gr.Accordion("Sources", open=False):
            sources_output = gr.Textbox(
                label="Sources",
                lines=8,
                interactive=False,
            )
        status_output = gr.Textbox(
            label="Status",
            interactive=False,
        )
        gr.Markdown(
            "<p style='color: gray; font-style: italic;'>"
            "⚠️ BioMind is for research purposes only. "
            "Always consult a qualified medical professional."
            "</p>"
        )
        ask_button.click(
            fn=ask_ui,
            inputs=[ask_query_input, question_input, k_input],
            outputs=[answer_output, sources_output, status_output],
        )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
why 