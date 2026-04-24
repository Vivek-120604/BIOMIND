"""Entrypoint for running the remote HTTP/SSE MCP server."""

from __future__ import annotations

import os

import uvicorn

from mcp_server.http_app import app


def main() -> None:
    """Run the remote BioMind MCP service on the configured HTTP port."""

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
