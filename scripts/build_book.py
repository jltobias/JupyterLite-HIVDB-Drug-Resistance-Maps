"""Build the book with interactive HTML plots, leaving the Lab renderer unchanged."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from jupyter_book.cli.main import main as jupyter_book


if __name__ == "__main__":
    # Embed Plotly.js in the generated HTML; the browser still fetches map geometry.
    os.environ["PLOTLY_RENDERER"] = "notebook"
    root = Path(__file__).resolve().parents[1]
    jupyter_book(["build", str(root), "--all", "--warningiserror", "--keep-going", *sys.argv[1:]])
