"""Convert all downloaded PDF attachments to standardized text files.

Uses pdftotext (poppler) for native text extraction. Stores output as
one .txt file per PDF in data/texts/, with the same filename stem.
Also writes a manifest CSV mapping filenames to contract metadata.
"""
import sqlite_utils
import subprocess
import os
import csv
import sys
from tqdm import tqdm

from settings import get_env, get_path


def extract_text(pdf_path):
    """Extract text from PDF using pdftotext, return text or None on failure."""
    pdftotext_bin = get_env("PDFTOTEXT_BIN", "pdftotext")
    try:
        result = subprocess.run(
            [pdftotext_bin, "-layout", pdf_path, "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


def main():
    pdf_dir = get_path("CRZ_PDF_DIR", "data/pdfs")
    text_dir = get_path("CRZ_TEXT_DIR", "data/texts")
    os.makedirs(text_dir, exist_ok=True)

    db = sqlite_utils.Database(get_path("CRZ_DB_PATH", "crz.db"))

    # Get metadata for all downloaded PDFs
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDFs to convert")

    manifest = []
    ok, fail, empty, skip = 0, 0, 0, 0

    pbar = tqdm(sorted(pdf_files), desc="PDF→text", unit="pdf")
    for fname in pbar:
        pdf_path = os.path.join(pdf_dir, fname)
        txt_path = os.path.join(text_dir, fname.replace(".pdf", ".txt"))

        # Skip if already converted
        if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            skip += 1
            text = open(txt_path).read()
        else:
            text = extract_text(pdf_path)
            if text:
                with open(txt_path, "w") as f:
                    f.write(text)
                ok += 1
            elif text == "":
                empty += 1
                pbar.set_postfix(ok=ok, fail=fail, empty=empty, skip=skip)
                continue
            else:
                fail += 1
                pbar.set_postfix(ok=ok, fail=fail, empty=empty, skip=skip)
                continue

        # Get contract metadata
        row = db.execute('''
            select z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel,
                   z.suma, z.rezort, z.druh, z.typ, z.crz_url
            from prilohy p join zmluvy z on p.zmluva_id = z.id
            where p.subor = ? limit 1
        ''', [fname]).fetchone()

        if row:
            manifest.append({
                "file": fname,
                "txt_file": fname.replace(".pdf", ".txt"),
                "zmluva_id": row[0],
                "nazov": row[1],
                "dodavatel": row[2],
                "objednavatel": row[3],
                "suma": row[4],
                "rezort": row[5],
                "druh": row[6],
                "typ": row[7],
                "crz_url": row[8],
                "text_len": len(text),
            })

        pbar.set_postfix(ok=ok, fail=fail, empty=empty, skip=skip)
    pbar.close()

    # Write manifest
    manifest_path = os.path.join(text_dir, "manifest.csv")
    if manifest:
        with open(manifest_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=manifest[0].keys())
            writer.writeheader()
            writer.writerows(manifest)

    print(f"\nDone: {ok} converted, {fail} failed, {empty} empty")
    print(f"Text files in {text_dir}/")
    print(f"Manifest: {manifest_path}")
    print(f"Using pdftotext binary: {get_env('PDFTOTEXT_BIN', 'pdftotext')}")


if __name__ == "__main__":
    main()
