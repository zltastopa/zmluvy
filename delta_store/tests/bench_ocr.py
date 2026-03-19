"""Benchmark: ThreadPoolExecutor vs ProcessPoolExecutor for PDF→text (OCR).

Picks 50 PDFs (mix of native-text and scanned), runs both approaches,
compares wall-clock time and output quality (text identity).

Usage:
    uv run python delta_store/tests/bench_ocr.py
    uv run python delta_store/tests/bench_ocr.py --n 100 --workers 8
"""

from __future__ import annotations

import os
import random
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from settings import get_path

PDF_DIR = Path(get_path("CRZ_PDF_DIR", "data/pdfs"))


def convert_one(args: tuple) -> tuple:
    """Convert a single PDF to text. Returns (fname, status, text, elapsed_ms)."""
    fname, pdf_dir, text_dir, force = args
    pdf_path = str(Path(pdf_dir) / fname)
    txt_path = Path(text_dir) / fname.replace(".pdf", ".txt")

    start = time.perf_counter()

    # Native extraction
    from pipeline.pdf_to_text import extract_text as _pdftotext
    text = None
    try:
        text = _pdftotext(pdf_path)
    except Exception:
        pass

    if text and text.strip():
        txt_path.write_text(text)
        elapsed = (time.perf_counter() - start) * 1000
        return (fname, "native", text.strip(), elapsed)

    # OCR fallback
    try:
        import logging
        import ocrmypdf
        logging.getLogger("ocrmypdf").setLevel(logging.ERROR)
        logging.getLogger("PIL").setLevel(logging.ERROR)

        ocr_pdf = Path(pdf_dir) / f".bench_ocr_{os.getpid()}_{fname}"
        ocrmypdf.ocr(
            pdf_path,
            str(ocr_pdf),
            language="slk+ces",
            skip_text=True,
            progress_bar=False,
            pages="1-10",
            tesseract_timeout=60,
        )
        text = _pdftotext(str(ocr_pdf))
        ocr_pdf.unlink(missing_ok=True)

        if text and text.strip():
            txt_path.write_text(text)
            elapsed = (time.perf_counter() - start) * 1000
            return (fname, "ocr", text.strip(), elapsed)

        elapsed = (time.perf_counter() - start) * 1000
        return (fname, "ocr_fail", "", elapsed)

    except Exception as e:
        Path(pdf_dir).joinpath(f".bench_ocr_{os.getpid()}_{fname}").unlink(missing_ok=True)
        elapsed = (time.perf_counter() - start) * 1000
        return (fname, "fail", "", elapsed)


def run_pool(executor_cls, label: str, pdf_files: list[str], workers: int) -> dict:
    """Run conversion with given executor, return results dict."""
    with tempfile.TemporaryDirectory(prefix=f"bench_{label}_") as text_dir:
        task_args = [(f, str(PDF_DIR), text_dir, True) for f in pdf_files]

        results = {}
        wall_start = time.perf_counter()

        with executor_cls(max_workers=workers) as pool:
            futures = {pool.submit(convert_one, a): a[0] for a in task_args}
            for future in as_completed(futures):
                fname, status, text, elapsed_ms = future.result()
                results[fname] = {
                    "status": status,
                    "text": text,
                    "elapsed_ms": elapsed_ms,
                    "text_len": len(text),
                }

        wall_elapsed = (time.perf_counter() - wall_start) * 1000

    return {"results": results, "wall_ms": wall_elapsed}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark Thread vs Process pool for OCR")
    parser.add_argument("--n", type=int, default=50, help="Number of PDFs to test (default: 50)")
    parser.add_argument("--workers", type=int, default=0, help="Workers (default: cpu_count, capped at 8)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for PDF selection")
    args = parser.parse_args()

    workers = args.workers if args.workers > 0 else min(os.cpu_count() or 4, 8)

    # Pick N random PDFs
    all_pdfs = sorted(f for f in os.listdir(PDF_DIR) if f.endswith(".pdf") and os.path.getsize(PDF_DIR / f) > 0)
    random.seed(args.seed)
    pdf_files = random.sample(all_pdfs, min(args.n, len(all_pdfs)))

    print(f"Benchmark: {len(pdf_files)} PDFs, {workers} workers, cpu_count={os.cpu_count()}")
    print(f"PDF dir: {PDF_DIR}")
    print()

    # --- Run ThreadPoolExecutor (old) ---
    print(f"Running ThreadPoolExecutor ({workers} workers)...")
    thread_out = run_pool(ThreadPoolExecutor, "thread", pdf_files, workers)
    print(f"  Wall time: {thread_out['wall_ms']:.0f} ms")

    # --- Run ProcessPoolExecutor (new) ---
    print(f"Running ProcessPoolExecutor ({workers} workers)...")
    process_out = run_pool(ProcessPoolExecutor, "process", pdf_files, workers)
    print(f"  Wall time: {process_out['wall_ms']:.0f} ms")

    # --- Compare ---
    print()
    print("=" * 80)
    print(f"{'Metric':<35s}  {'Thread':>12s}  {'Process':>12s}  {'Speedup':>8s}")
    print("-" * 80)

    t_wall = thread_out["wall_ms"]
    p_wall = process_out["wall_ms"]
    speedup = t_wall / p_wall if p_wall > 0 else 0
    print(f"{'Wall clock (ms)':<35s}  {t_wall:>12.0f}  {p_wall:>12.0f}  {speedup:>7.2f}x")

    # Per-file stats
    t_res = thread_out["results"]
    p_res = process_out["results"]

    # Status comparison
    for status in ["native", "ocr", "ocr_fail", "fail"]:
        t_cnt = sum(1 for r in t_res.values() if r["status"] == status)
        p_cnt = sum(1 for r in p_res.values() if r["status"] == status)
        print(f"  {status + ' count':<33s}  {t_cnt:>12d}  {p_cnt:>12d}")

    # Timing for OCR files only
    t_ocr_times = [r["elapsed_ms"] for r in t_res.values() if r["status"] == "ocr"]
    p_ocr_times = [r["elapsed_ms"] for r in p_res.values() if r["status"] == "ocr"]

    if t_ocr_times and p_ocr_times:
        t_ocr_avg = sum(t_ocr_times) / len(t_ocr_times)
        p_ocr_avg = sum(p_ocr_times) / len(p_ocr_times)
        print(f"{'Avg OCR time per file (ms)':<35s}  {t_ocr_avg:>12.0f}  {p_ocr_avg:>12.0f}  {t_ocr_avg/p_ocr_avg if p_ocr_avg > 0 else 0:>7.2f}x")

    t_native_times = [r["elapsed_ms"] for r in t_res.values() if r["status"] == "native"]
    p_native_times = [r["elapsed_ms"] for r in p_res.values() if r["status"] == "native"]

    if t_native_times and p_native_times:
        t_nat_avg = sum(t_native_times) / len(t_native_times)
        p_nat_avg = sum(p_native_times) / len(p_native_times)
        print(f"{'Avg native time per file (ms)':<35s}  {t_nat_avg:>12.0f}  {p_nat_avg:>12.0f}  {t_nat_avg/p_nat_avg if p_nat_avg > 0 else 0:>7.2f}x")

    # Quality check: text output identity
    print()
    print("Quality check (text output identity):")
    identical, different, both_empty = 0, 0, 0
    diff_files = []
    for fname in pdf_files:
        t_text = t_res[fname]["text"]
        p_text = p_res[fname]["text"]
        if t_text == p_text:
            if t_text == "":
                both_empty += 1
            else:
                identical += 1
        else:
            different += 1
            t_len = t_res[fname]["text_len"]
            p_len = p_res[fname]["text_len"]
            diff_files.append((fname, t_len, p_len, t_res[fname]["status"], p_res[fname]["status"]))

    print(f"  Identical output: {identical}/{len(pdf_files)}")
    print(f"  Both empty/failed: {both_empty}/{len(pdf_files)}")
    print(f"  Different output:  {different}/{len(pdf_files)}")

    if diff_files:
        print()
        print("  Files with different output:")
        for fname, t_len, p_len, t_st, p_st in diff_files[:10]:
            print(f"    {fname}: thread={t_st}({t_len} chars) vs process={p_st}({p_len} chars)")

    # Summary
    print()
    print("=" * 80)
    print(f"RESULT: ProcessPoolExecutor is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than ThreadPoolExecutor")
    if different == 0:
        print("QUALITY: Outputs are identical — no regression.")
    else:
        print(f"QUALITY: {different} files differ — review above for details.")


if __name__ == "__main__":
    main()
