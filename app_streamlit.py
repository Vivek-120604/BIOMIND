"""Streamlit interface for BioMind biomedical research assistant."""

from __future__ import annotations

import streamlit as st

from app import chain, fetcher, indexer

st.set_page_config(
    page_title="BioMind — Biomedical Research Assistant",
    page_icon="🧬",
    layout="wide",
)

st.markdown(
    "# 🧬 BioMind\n"
    "**Biomedical Research Assistant powered by arXiv + BM25 + Groq**\n"
    "Search live research papers and get AI-powered answers grounded in real science."
)

tab1, tab2 = st.tabs(["🔍 Search Papers", "🧠 Ask a Question"])

with tab1:
    st.subheader("Search Papers")
    col1, col2 = st.columns(2)
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g. CRISPR gene editing cancer",
            key="search_query",
        )
    with col2:
        max_results = st.slider(
            "Max Results",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
        )

    if st.button("Search", key="search_button"):
        if not query.strip():
            st.warning("Enter a search query to fetch biomedical papers.")
        else:
            with st.spinner("Searching arXiv..."):
                papers = fetcher.fetch_papers(query.strip(), max_results=int(max_results))

            if papers:
                st.success(f"Found {len(papers)} papers")

                # Display results table
                display_data = [
                    {
                        "Title": paper["title"],
                        "Authors": paper["authors"],
                        "Published": paper["published"],
                        "arXiv ID": paper["arxiv_id"],
                    }
                    for paper in papers
                ]
                st.dataframe(display_data, use_container_width=True)

                # Display abstracts
                with st.expander("📄 Paper Abstracts"):
                    for index, paper in enumerate(papers, start=1):
                        st.markdown(f"**{index}. {paper['title']}**")
                        st.caption(f"Authors: {paper['authors']}")
                        st.caption(f"Published: {paper['published']}")
                        st.caption(f"arXiv ID: {paper['arxiv_id']}")
                        st.caption(f"PDF: {paper['pdf_url']}")
                        st.markdown(paper["summary"])
                        st.divider()
            else:
                st.error("No papers found. Try refining your search query.")

with tab2:
    st.subheader("Ask a Question")
    query = st.text_input(
        "Search Query",
        placeholder="e.g. metformin drug interactions diabetes",
        key="ask_query",
    )
    question = st.text_area(
        "Question",
        placeholder="e.g. What are the main side effects reported?",
        height=100,
    )
    k = st.slider(
        "Number of Papers",
        min_value=3,
        max_value=10,
        value=5,
        step=1,
    )

    if st.button("Ask", key="ask_button"):
        if not query.strip() or not question.strip():
            st.warning("Enter both a search query and a question.")
        else:
            with st.spinner("Searching papers and generating answer..."):
                result = chain.search_and_answer(
                    query=query.strip(),
                    question=question.strip(),
                    k=int(k),
                )

            st.markdown("### Answer")
            st.write(result["answer"])

            with st.expander("Sources"):
                if result["sources"]:
                    for source in result["sources"]:
                        st.write(f"- **{source['title']}** ({source['arxiv_id']})")
                else:
                    st.info("No sources available.")

            indexed = indexer.get_index_size()
            cached = len(fetcher.get_cached_papers())
            st.caption(
                f"📊 Indexed papers: {indexed} | Cached papers: {cached} | Papers searched: {result['papers_searched']}"
            )

st.divider()
st.markdown(
    "<p style='color: gray; font-size: 0.875rem; font-style: italic;'>"
    "⚠️ **Disclaimer:** BioMind is for research purposes only. "
    "Always consult a qualified medical professional for medical advice."
    "</p>",
    unsafe_allow_html=True,
)
