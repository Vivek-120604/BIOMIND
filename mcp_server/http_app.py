"""Remote HTTP/SSE MCP application for BioMind."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.requests import Request
from starlette.routing import Route

from mcp.server.sse import SseServerTransport
from mcp_server.core import server as mcp_server

app = FastAPI(title="BioMind MCP", version="1.0.0")
_mcp_transport = SseServerTransport("/mcp/messages")


@app.get("/health")
def healthcheck() -> dict:
    """Return a simple health response so deployments can check server readiness."""

    return {"status": "ok"}


@app.get("/mcp")
def mcp_info() -> dict:
    """Describe the public remote MCP endpoints exposed by this BioMind service."""

    return {
        "server": "biomind",
        "transport": "sse",
        "sse_endpoint": "/mcp/sse",
        "message_endpoint": "/mcp/messages",
    }


async def mcp_sse(request: Request):
    """Open a remote MCP SSE session so internet clients can call BioMind tools."""

    async with _mcp_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


async def mcp_messages(request: Request):
    """Receive JSON-RPC POST messages for an existing BioMind MCP SSE session."""

    await _mcp_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


app.router.routes.append(Route("/mcp/sse", endpoint=mcp_sse, methods=["GET"]))
app.router.routes.append(
    Route("/mcp/messages", endpoint=mcp_messages, methods=["POST"])
)

