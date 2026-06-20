"""Manifest records with row counts, time ranges, and SHA256 hashes."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_file_record(path: Path, frame: pd.DataFrame, *, source: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": str(path),
        "rows": int(len(frame)),
        "sha256": sha256_file(path),
        "source": source,
    }
    if "timestamp" in frame.columns and len(frame):
        timestamps = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce").dropna()
        if len(timestamps):
            record["start"] = timestamps.min().isoformat().replace("+00:00", "Z")
            record["end"] = timestamps.max().isoformat().replace("+00:00", "Z")
    return record


def write_manifest(path: Path, records: list[dict[str, Any]], *, status: str) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": status, "files": records}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    tmp.replace(path)
