"""Shared OpenRouter helpers for repo scripts."""

from __future__ import annotations

import confpath  # noqa: F401

import os
import sys
from pathlib import Path

from settings import get_env


OPENROUTER_BASE = get_env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def load_openrouter_api_key() -> str:
    """Load OpenRouter API key from env or repo-local key file."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        key_file = Path(__file__).resolve().parent / ".openrouter_key"
        if not key_file.exists():
            key_file = Path(__file__).resolve().parent.parent / ".openrouter_key"
        if key_file.exists():
            key = key_file.read_text().strip()
    if not key:
        print("Error: set OPENROUTER_API_KEY in .env/env or create .openrouter_key")
        sys.exit(1)
    return key
