"""Entrypoint that runs the FastAPI backend and Gradio frontend together."""

from __future__ import annotations

import importlib.util
import threading
from pathlib import Path

import uvicorn

from app import api


def _load_gradio_module():
    """Load the root Gradio UI module without conflicting with the app package name."""

    module_path = Path(__file__).with_name("app.py")
    spec = importlib.util.spec_from_file_location("biomind_ui", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the BioMind Gradio UI module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_api() -> None:
    """Run the FastAPI backend on port 8000 for programmatic access."""

    uvicorn.run(api.app, host="0.0.0.0", port=8000, log_level="info")


def run_gradio() -> None:
    """Run the Gradio interface on port 7860 for interactive use."""

    gradio_module = _load_gradio_module()
    gradio_module.demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


def main() -> None:
    """Start both the API server and the UI server in separate threads."""

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    run_gradio()


if __name__ == "__main__":
    main()
