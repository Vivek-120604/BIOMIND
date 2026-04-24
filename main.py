"""Entrypoint that runs the unified BioMind web app."""

from __future__ import annotations

import uvicorn

from app import api

def main() -> None:
    """Run the single public BioMind server with UI, REST API, and MCP endpoints."""

    uvicorn.run(api.app, host="0.0.0.0", port=7860, log_level="info")


if __name__ == "__main__":
    main()
