"""Shared environment-backed configuration and utilities for repo scripts."""

from __future__ import annotations

import os
import re
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


def get_r2_config():
    """Return R2 config dict if R2_BUCKET is set, else None."""
    bucket = os.getenv("R2_BUCKET")
    if not bucket:
        return None
    return {
        "endpoint_url": os.getenv("R2_ENDPOINT_URL"),
        "access_key_id": os.getenv("R2_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("R2_SECRET_ACCESS_KEY"),
        "bucket": bucket,
        "public_url": os.getenv("R2_PUBLIC_URL"),
    }


_COMPANY_SUFFIX_RE = re.compile(
    r'\s*,?\s*'
    r'(s\.?\s*r\.?\s*o\.?|a\.?\s*s\.?|spol\.\s*s\s*r\.?\s*o\.?'
    r'|v\.?\s*o\.?\s*s\.?|k\.?\s*s\.?|s\.?\s*e\.?'
    r'|n\.?\s*o\.?|o\.?\s*z\.?|z\.?\s*s\.?)'
    r'\s*\.?\s*$',
    re.IGNORECASE,
)


def normalize_company_name(name: str) -> str:
    """Normalize a Slovak company name for fuzzy matching.

    Strips legal-form suffixes (s.r.o., a.s., etc.), punctuation, and extra
    whitespace, then lowercases.
    """
    n = name.strip().lower()
    n = _COMPANY_SUFFIX_RE.sub('', n)
    n = re.sub(r'[,."\']+', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n
