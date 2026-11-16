#!/usr/bin/env python3
"""Run the annotated retrieval code also distributed inside JupyterLite.

Project: HIV Drug Resistance Maps; Created/updated: 2026-11-16.
Author: [Repository contributors; generated with Codex].
Email/organization: [Not supplied].
Input/output/dependencies: See content/study_query.py, the single implementation.
Change log: 2026-11-16 - Added repository CLI entry point.
"""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "content/study_query.py"), run_name="__main__")
