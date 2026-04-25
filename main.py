"""Entry point — starts FastAPI on port 8000 and Gradio on port 7860.

This is the main entry point for both local development and HF Spaces deployment.
It starts FastAPI in a background thread on 127.0.0.1:8000 and Gradio on 0.0.0.0:7860.
HF Spaces exposes port 7860 to the public.
"""

from __future__ import annotations

import threading
import time

import uvicorn

from app.api import app as fastapi_app
from app import demo as gradio_demo


def run_fastapi() -> None:
    """Run FastAPI server in background thread on 127.0.0.1:8000."""
    uvicorn.run(
        fastapi_app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True,
    )


def main() -> None:
    """Start FastAPI in background thread and Gradio on main thread."""
    # Start FastAPI in background thread
    fastapi_thread = threading.Thread(
        target=run_fastapi,
        daemon=True,
        name="FastAPI-Thread"
    )
    fastapi_thread.start()

    # Give FastAPI time to start
    time.sleep(2)

    # Start Gradio on main thread
    # This blocks until the Gradio server is stopped
    gradio_demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False,
    )


if __name__ == "__main__":
    main()

