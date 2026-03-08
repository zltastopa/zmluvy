#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
#     "python-dotenv",
#     "sqlite-utils",
#     "tqdm",
# ]
# ///
"""Unified CLI runner for the CRZ pipeline.

Usage:
    uv run run.py pdf2text                         # convert PDFs to text
    uv run run.py extract                          # LLM extraction on unprocessed texts
    uv run run.py extract --limit 10 --model google/gemini-2.5-flash-lite
    uv run run.py enrich                           # scrape FinStat for top suppliers
    uv run run.py enrich --ico 51671824            # enrich single company
    uv run run.py flags                            # evaluate all red flag rules
    uv run run.py flags --rule hidden_entities     # evaluate one rule
    uv run run.py flags --list                     # list all rules
"""
import argparse
import sys
import subprocess
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent / "pipeline"


def run_script(name, extra_args):
    """Run a pipeline script via uv run, forwarding extra CLI args."""
    script = PIPELINE_DIR / name
    if not script.exists():
        print(f"Error: {script} not found")
        sys.exit(1)
    cmd = ["uv", "run", "python", str(script)] + extra_args
    print(f"$ {' '.join(cmd)}")
    sys.exit(subprocess.call(cmd))


def main():
    parser = argparse.ArgumentParser(
        description="CRZ pipeline runner",
        usage="uv run run.py <command> [options]",
    )
    parser.add_argument(
        "command",
        choices=["pdf2text", "extract", "enrich", "flags"],
        help="pdf2text: PDF->text | extract: LLM extraction | enrich: FinStat scraper | flags: red flag evaluator",
    )

    args, extra = parser.parse_known_args()

    scripts = {
        "pdf2text": "pdf_to_text.py",
        "extract": "extract_contracts.py",
        "enrich": "enrich_suppliers.py",
        "flags": "flag_contracts.py",
    }

    run_script(scripts[args.command], extra)


if __name__ == "__main__":
    main()
