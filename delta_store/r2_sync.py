"""Sync Delta Lake tables and crz.db between local disk and Cloudflare R2.

Public downloads use httpx against R2_PUBLIC_URL (no credentials needed).
Uploads use boto3 with R2 credentials.

Usage:
    uv run python -m delta_store.r2_sync download [--include-db]
    uv run python -m delta_store.r2_sync upload
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import boto3
import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = Path(__file__).resolve().parent / "tables"
CRZ_DB_PATH = REPO_ROOT / "crz.db"

# R2 object prefixes
TABLES_PREFIX = "delta_store/tables/"
CRZ_DB_KEY = "crz.db"


def get_s3_client():
    """Create a boto3 S3 client configured for Cloudflare R2."""
    endpoint = os.getenv("R2_ENDPOINT_URL")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    if not all([endpoint, access_key, secret_key]):
        sys.exit(
            "ERROR: R2 credentials not configured. "
            "Set R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY."
        )
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def _public_url() -> str | None:
    return os.getenv("R2_PUBLIC_URL", "").rstrip("/") or None


def _bucket() -> str:
    bucket = os.getenv("R2_BUCKET")
    if not bucket:
        sys.exit("ERROR: R2_BUCKET not set.")
    return bucket


def _list_objects(client, bucket: str, prefix: str):
    """List all objects under a prefix, handling pagination."""
    objects = []
    continuation_token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix}
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token
        resp = client.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []):
            objects.append(obj)
        if not resp.get("IsTruncated"):
            break
        continuation_token = resp["NextContinuationToken"]
    return objects


def download_tables(target_dir: Path | None = None):
    """Download Delta tables from R2 to local disk.

    Uses R2_PUBLIC_URL for unauthenticated downloads if available,
    otherwise falls back to boto3 with credentials.
    """
    target = target_dir or TABLES_DIR
    public_url = _public_url()

    if public_url:
        _download_tables_public(public_url, target)
    else:
        _download_tables_s3(target)


def _download_tables_public(public_url: str, target: Path):
    """Download tables via public R2 URL using httpx."""
    # We need the object listing from S3 API to know what files exist.
    # Use boto3 if credentials are available, otherwise require R2_BUCKET
    # with credentials for listing (public URL doesn't support listing).
    client = None
    bucket = os.getenv("R2_BUCKET")
    if bucket and os.getenv("R2_ACCESS_KEY_ID"):
        client = get_s3_client()
        objects = _list_objects(client, bucket, TABLES_PREFIX)
    else:
        # Fall back to boto3-less listing via the index — not possible
        # with plain R2 public URLs. Use S3 credentials for listing.
        sys.exit(
            "ERROR: Public downloads require R2_BUCKET + credentials "
            "for listing objects. Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY."
        )

    downloaded = 0
    skipped = 0
    with httpx.Client(timeout=120, follow_redirects=True) as http:
        for obj in objects:
            key = obj["Key"]
            rel = key[len(TABLES_PREFIX):]
            if not rel:
                continue
            local_path = target / rel
            # Skip if same size already exists locally
            if local_path.exists() and local_path.stat().st_size == obj["Size"]:
                skipped += 1
                continue
            local_path.parent.mkdir(parents=True, exist_ok=True)
            url = f"{public_url}/{key}"
            resp = http.get(url)
            resp.raise_for_status()
            local_path.write_bytes(resp.content)
            downloaded += 1

    print(f"  Downloaded {downloaded} files, skipped {skipped} (already up to date)")


def _download_tables_s3(target: Path):
    """Download tables via boto3 S3 API with credentials."""
    client = get_s3_client()
    bucket = _bucket()
    objects = _list_objects(client, bucket, TABLES_PREFIX)

    downloaded = 0
    skipped = 0
    for obj in objects:
        key = obj["Key"]
        rel = key[len(TABLES_PREFIX):]
        if not rel:
            continue
        local_path = target / rel
        if local_path.exists() and local_path.stat().st_size == obj["Size"]:
            skipped += 1
            continue
        local_path.parent.mkdir(parents=True, exist_ok=True)
        client.download_file(bucket, key, str(local_path))
        downloaded += 1

    print(f"  Downloaded {downloaded} files, skipped {skipped} (already up to date)")


def upload_tables(source_dir: Path | None = None):
    """Upload local Delta tables to R2."""
    source = source_dir or TABLES_DIR
    client = get_s3_client()
    bucket = _bucket()

    if not source.exists():
        print(f"  No tables directory at {source}, nothing to upload.")
        return

    # Get existing objects for size comparison
    existing = {}
    for obj in _list_objects(client, bucket, TABLES_PREFIX):
        existing[obj["Key"]] = obj["Size"]

    # Track which R2 keys correspond to local files
    local_keys = set()
    uploaded = 0
    skipped = 0
    for local_path in sorted(source.rglob("*")):
        if not local_path.is_file():
            continue
        rel = local_path.relative_to(source)
        key = f"{TABLES_PREFIX}{rel}"
        local_keys.add(key)
        local_size = local_path.stat().st_size
        if key in existing and existing[key] == local_size:
            skipped += 1
            continue
        client.upload_file(str(local_path), bucket, key)
        uploaded += 1

    # Delete stale R2 objects (e.g. parquet files removed by vacuum)
    deleted = 0
    for key in existing:
        rel = key[len(TABLES_PREFIX):]
        if rel and key not in local_keys:
            client.delete_object(Bucket=bucket, Key=key)
            deleted += 1

    print(
        f"  Uploaded {uploaded}, skipped {skipped} (up to date), "
        f"deleted {deleted} stale"
    )


def download_crz_db(target_path: Path | None = None):
    """Download crz.db from R2 (for agents that need the SQLite fallback)."""
    target = target_path or CRZ_DB_PATH
    public_url = _public_url()

    if public_url:
        url = f"{public_url}/{CRZ_DB_KEY}"
        print(f"  Downloading crz.db from {url}...")
        with httpx.Client(timeout=300, follow_redirects=True) as http:
            with http.stream("GET", url) as resp:
                resp.raise_for_status()
                with open(target, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        f.write(chunk)
    else:
        client = get_s3_client()
        bucket = _bucket()
        print(f"  Downloading crz.db from s3://{bucket}/{CRZ_DB_KEY}...")
        client.download_file(bucket, CRZ_DB_KEY, str(target))

    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"  Downloaded crz.db ({size_mb:.0f} MB)")


def main():
    parser = argparse.ArgumentParser(
        description="Sync Delta tables with Cloudflare R2"
    )
    parser.add_argument(
        "action", choices=["download", "upload"], help="download or upload"
    )
    parser.add_argument(
        "--include-db",
        action="store_true",
        help="Also download crz.db (for agents)",
    )
    args = parser.parse_args()

    if args.action == "download":
        print("Downloading tables from R2...")
        download_tables()
        if args.include_db:
            print("Downloading crz.db from R2...")
            download_crz_db()
    elif args.action == "upload":
        print("Uploading tables to R2...")
        upload_tables()


if __name__ == "__main__":
    main()
