"""Shared environment-backed configuration for repo scripts."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"

# Load repo-local .env once for every entrypoint that imports this module.
load_dotenv(ENV_PATH)


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def get_path(name: str, default: str) -> str:
    value = os.getenv(name, default)
    path = Path(value)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return str(path)
