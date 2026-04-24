"""MCP server that exposes BioMind search and question-answering tools."""

from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from app import chain, fetcher, indexer

server = Server("Biomind")


async def _json_text(payload: dict) -> list[TextContent]:
    """Convert a Python dictionary into MCP text content containing JSON."""

    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of BioMind tools available through the MCP server."""

    return [
        Tool(
            name="search_papers",
            description=(
                "Search arXiv for biomedical research papers on a topic. "
                "Returns titles, authors, abstracts and PDF links. Use this "
                "to find papers before asking questions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="ask_biomind",
            description=(
                "Search arXiv for papers on query, then answer the specific "
                "question using BM25 retrieval over the fetched papers. "
                "Returns answer with citations. Best for specific scientific "
                "questions about drugs, genes, diseases, or research findings."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "question": {"type": "string"},
                },
                "required": ["query", "question"],
            },
        ),
        Tool(
            name="get_index_status",
            description=(
                "Returns the current number of papers indexed in BM25 and "
                "cached. Use this to check if BioMind has papers loaded before "
                "asking questions."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch MCP tool calls to the matching BioMind application functions."""

    if name == "search_papers":
        result = fetcher.fetch_papers(
            arguments["query"],
            max_results=arguments.get("max_results", 10),
        )
        return await _json_text({"papers": result, "total": len(result)})

    if name == "ask_biomind":
        result = chain.search_and_answer(
            query=arguments["query"],
            question=arguments["question"],
        )
        return await _json_text(result)

    if name == "get_index_status":
        result = {
            "indexed_papers": indexer.get_index_size(),
            "cache_size": len(fetcher.get_cached_papers()),
        }
        return await _json_text(result)

    raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Start the BioMind MCP server over standard input and output."""

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

