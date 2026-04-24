"""Entrypoint that runs the BioMind Gradio UI."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


def main() -> None:
    """Run the Gradio UI on the public Spaces port."""

    module_path = Path(__file__).with_name("app.py")
    spec = importlib.util.spec_from_file_location("biomind_ui", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the BioMind Gradio UI module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw_port = os.getenv("PORT") or os.getenv("GRADIO_SERVER_PORT") or "7860"
    try:
        server_port = int(raw_port)
    except ValueError:
        server_port = 7860

    module.demo.launch(server_name="0.0.0.0", server_port=server_port, share=False)


if __name__ == "__main__":
    main()

