---
title: BioMind - Live Biomedical Research Assistant
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.1
app_file: main.py
python_version: "3.11"
---

# 🧬 **BioMind: Live Biomedical Research at Your Fingertips**

Search live arXiv biomedical papers, index them with BM25, and get AI-powered answers grounded in real science — no hallucinations, no stale data.

## 📋 Overview

**BioMind** is a biomedical research assistant that fetches live research papers from arXiv, indexes them using BM25 (keyword-based, no embeddings), and answers domain-specific questions using the Groq LLM. Built for researchers, students, and biotech builders who need fast, accurate literature discovery without relying on stale local corpora or costly semantic search. The system combines live arXiv ingestion, vectorless RAG, a Gradio frontend, a FastAPI backend, and MCP server support for AI agents.

## 🎯 Why BM25 for Biomedical Research?

Biomedical search often fails when semantic retrieval over-generalizes precise terminology. Exact identifiers—such as drug names (e.g., _BRCA1_, _metformin_), gene IDs, protein sequences, and disease codes—require direct lexical matching to retrieve the right papers. A search for `BRCA1` should return papers specifically about BRCA1, not papers about vaguely similar cancer genetics topics that happen to live nearby in embedding space. BM25 makes that tradeoff explicit and predictable, ensuring researchers find exactly what they're looking for.

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌──────────────────────────┐
│  Gradio UI (port 7860)   │  ◄──── HF Spaces exposes this
│  ┌────────────────────┐  │
│  │ Search / Ask UI    │  │
│  └────┬───────────────┘  │
│       │ httpx POST       │
│       ▼                  │
│  FastAPI (port 8000)     │
│  ┌────────────────────┐  │
│  │ /search, /ask      │  │
│  └────┬───────────────┘  │
└──────┼──────────────────┘
       │
       ├─────────────────┬────────────────┐
       ▼                 ▼                ▼
    arXiv API       BM25 Index       Groq LLM
  (live papers)    (in-memory)     (llama3-8b)

Optional: MCP Server (stdio) → AI agents can call tools
```

### Two-Server Threading Model

**main.py** starts **both** servers simultaneously:

1. **FastAPI** on `127.0.0.1:8000` in a background thread
   - Runs `/search`, `/ask`, `/status` endpoints
   - Powers the Gradio frontend

2. **Gradio** on `0.0.0.0:7860` in the main thread
   - User-facing interface
   - Calls FastAPI via httpx
   - HF Spaces exposes port 7860 to the public

This architecture ensures HF Spaces works correctly and local development is smooth.

## 💾 Tech Stack

| Component         | Technology           | Purpose                                            |
| ----------------- | -------------------- | -------------------------------------------------- |
| Paper Ingestion   | arXiv Python library | Fetch live biomedical and AI papers                |
| Retrieval         | rank-bm25            | Vectorless BM25 index over titles + abstracts      |
| LLM Orchestration | LangChain + Groq     | Generate grounded answers with citations           |
| Backend API       | FastAPI              | Serve /search, /ask, /status endpoints             |
| Frontend          | Gradio               | Interactive research workflow UI                   |
| Agent Integration | MCP Python SDK       | Expose BioMind as tools for Claude Desktop, agents |
| Runtime           | Python 3.11          | Fast, stable, widely supported                     |
| Deployment        | Docker + Python      | Containerized for HF Spaces, cloud platforms       |

## 🚀 Getting Started

### Local Development with `uv`

```bash
# Clone and enter project
git clone https://github.com/yourusername/BioMind
cd BioMind

# Install dependencies with uv (fast)
uv sync

# Configure environment
# Edit .env and add your GROQ_API_KEY

# Run both FastAPI (bg) and Gradio (fg)
uv run python main.py
```

Then open: **http://localhost:7860**

### Local Development with `pip`

```bash
# Clone and enter project
git clone https://github.com/yourusername/BioMind
cd BioMind

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and add your GROQ_API_KEY

# Run
python main.py
```

Then open: **http://localhost:7860**

### Running Individual Components

**FastAPI only** (useful for API testing):

```bash
uv run python -m uvicorn app.api:app --host 0.0.0.0 --port 8000
# Then visit: http://localhost:8000/docs
```

**MCP Server** (for Claude Desktop integration):

```bash
uv run python -m mcp_server.server
```

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "biomind": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/BioMind"
    }
  }
}
```

## 📡 API Reference

### FastAPI Endpoints

#### `POST /search`

Search arXiv for papers.

**Request:**

```json
{
  "query": "CRISPR gene editing",
  "max_results": 10
}
```

**Response:**

```json
{
  "papers": [
    {
      "title": "...",
      "authors": "...",
      "summary": "...",
      "published": "2024-04-20",
      "pdf_url": "https://...",
      "arxiv_id": "2404.12345"
    }
  ],
  "total": 1,
  "query": "CRISPR gene editing"
}
```

#### `POST /ask`

Search papers and answer a question.

**Request:**

```json
{
  "query": "CRISPR cancer treatment",
  "question": "What are the latest findings?",
  "k": 5
}
```

**Response:**

```json
{
  "answer": "Based on recent papers, CRISPR shows promise in... [citation]",
  "sources": [
    {
      "title": "CRISPR Advances in Oncology",
      "arxiv_id": "2404.12345",
      "pdf_url": "https://..."
    }
  ],
  "papers_searched": 10,
  "query": "CRISPR cancer treatment"
}
```

#### `GET /status`

Health check and index stats.

**Response:**

```json
{
  "status": "healthy",
  "indexed_papers": 25,
  "cache_size": 10
}
```

### MCP Tools

When running the MCP server, these tools are available to Claude Desktop and AI agents:

- **`search_papers(query, max_results)`** — Search arXiv, returns paper list
- **`ask_biomind(query, question, k)`** — Answer question over retrieved papers
- **`get_status()`** — Return index and cache stats

## 🤖 Claude Desktop Integration

Use BioMind as a tool in **Claude Desktop** via MCP (Model Context Protocol).

### Setup

1. **Get your Claude Desktop config path:**
   ```bash
   # macOS / Linux
   ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add BioMind to config:**
   ```json
   {
     "mcpServers": {
       "biomind": {
         "command": "uv",
         "args": ["run", "/path/to/Biomind/mcp_server/server.py"]
       }
     }
   }
   ```
   *(Replace `/path/to/Biomind` with your actual BioMind directory path)*

3. **Restart Claude Desktop**

4. **Ask Claude to use BioMind:**
   - Claude will now have access to BioMind tools
   - Say: *"Search for papers on CRISPR gene therapy"* or *"Answer: what are common BRCA1 mutations?"*
   - Claude will call BioMind, fetch live papers, and answer your question

### Available MCP Tools

| Tool | Input | Output |
|------|-------|--------|
| **search_papers** | `query`, `max_results` (1-50, default 10) | List of papers with titles, authors, abstracts, PDF links |
| **ask_biomind** | `query`, `question`, `k` (1-20, default 5) | Grounded answer with citations to source papers |
| **get_status** | (none) | Current index size and cache count |

## 🌐 Hugging Face Spaces Deployment

1. **Push to GitHub:**

   ```bash
   git add .
   git commit -m "Initial BioMind commit"
   git push origin main
   ```

2. **Create HF Space:**
   - Go to https://huggingface.co/spaces
   - Click **Create new Space**
   - Choose **Docker** SDK
   - Connect your GitHub repo

3. **Set Secret:**
   - Go to Space **Settings → Secrets**
   - Add `GROQ_API_KEY` with your Groq API key

4. **Build & Deploy:**
   - HF will auto-build Docker image
   - Watch logs for `Running on http://0.0.0.0:7860`
   - Your Space is live!

## ⚕️ Disclaimer

**⚠️ BioMind is a research tool built for educational and portfolio purposes. It is not a medical device and should not be used for clinical decision-making without consulting qualified medical professionals.**

BioMind provides Literature discovery and synthesis; final medical decisions must be made by licensed healthcare providers.

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Open an issue or PR for bugs, features, or improvements.

## 📧 Contact

Questions? Open an issue on GitHub or reach out to the team.

---

**Happy researching!** 🧬
