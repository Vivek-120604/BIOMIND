"""Entrypoint to run the BioMind Streamlit UI locally."""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    """Run the Streamlit UI."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app_streamlit.py",
            "--logger.level=info",
        ],
        check=False,
    )


if __name__ == "__main__":
    main()

