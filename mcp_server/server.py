"""MCP Server exposing BioMind as tools for AI agents."""

from __future__ import annotations

import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from app.chain import search_and_answer
from app import fetcher, indexer

# Create MCP server instance
server = Server("biomind")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for AI agents.
    
    Returns:
        List of Tool definitions with name, description, and input schema.
    """
    return [
        Tool(
            name="search_papers",
            description=(
                "Search arXiv for biomedical research papers. "
                "Returns titles, authors, abstracts and PDF links. "
                "Use this to find relevant papers before asking questions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for arXiv"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of papers to return"
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="ask_biomind",
            description=(
                "Search arXiv papers and answer a specific biomedical question "
                "using BM25 retrieval and Groq LLM. "
                "Returns answer with citations to source papers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to fetch papers from arXiv"
                    },
                    "question": {
                        "type": "string",
                        "description": "Specific biomedical question to answer"
                    },
                    "k": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of papers to retrieve for answering"
                    },
                },
                "required": ["query", "question"],
            },
        ),
        Tool(
            name="get_status",
            description=(
                "Returns current BM25 index size and paper cache count. "
                "Use this to check what data is currently indexed."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[TextContent]:
    """Route tool calls to the correct function.
    
    Args:
        name: Name of the tool to call.
        arguments: Tool arguments from the AI agent.
        
    Returns:
        List containing TextContent with JSON response.
    """
    if name == "search_papers":
        papers = fetcher.fetch_papers(
            arguments["query"],
            arguments.get("max_results", 10)
        )
        return [
            TextContent(
                type="text",
                text=json.dumps({"papers": papers})
            )
        ]

    elif name == "ask_biomind":
        result = search_and_answer(
            arguments["query"],
            arguments.get("question"),
            arguments.get("k", 5),
        )
        return [
            TextContent(
                type="text",
                text=json.dumps(result)
            )
        ]

    elif name == "get_status":
        result = {
            "indexed_papers": indexer.get_index_size(),
            "cache_size": len(fetcher.get_cached_papers()),
        }
        return [
            TextContent(
                type="text",
                text=json.dumps(result)
            )
        ]

    return [
        TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )
    ]


async def main() -> None:
    """Start MCP server over stdio.
    
    This function runs the MCP server using stdio transport,
    allowing AI agents to communicate via JSON-RPC over standard input/output.
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
