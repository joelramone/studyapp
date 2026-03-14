from __future__ import annotations

import sys
from pathlib import Path


def ensure_repo_root_on_path() -> Path:
    """Ensure the repository root is available in sys.path.

    This allows absolute imports like ``from app...``, ``from core...`` and
    ``from agents...`` to work when running:

        streamlit run app/streamlit_app.py
    """

    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root
