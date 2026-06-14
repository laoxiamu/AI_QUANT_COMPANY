#!/usr/bin/env python3
"""Custodian-only A-1 episode generation, split, and authenticated sealing.

This entry point must be run by the independent custodian principal. It never
computes event-post returns. The executor must be a separate process and must
not import or call this module.
"""

from __future__ import annotations

import csv
import gc
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from a1_tiera_core import (
    CUTOFF_EXCLUSIVE,
    SYMBOLS,
    add_mark_direction,
    add_nominal_oi_features,
    apply_refractory,
    encrypt_aes256_gcm,
    release_plaintext,
    rolling_midrank_percentile,
    severity_label,
    sha256_bytes,
    sha256_file,
    split_work_sealed,
    trigger_rows,
)


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
WORK_DIR = ROOT / "06_RESEARCH" / "DATA" / "A1_WORK"
WORK_PATH = WORK_DIR / "work_episodes.csv"
SEALED_PATH = WORK_DIR / "sealed_holdout.enc"
MANIFEST_PATH = WORK_DIR / "A1_HOLDOUT_MANIFEST.json"
KEY_PATH = Path.home() / ".aiquant_sealed" / "a1" / "a1_key.bin"

EPISODE_COLUMNS = [
    "event_time_utc",
    "symbol",
    "oi_notional",
    "d6h_pct",
    "d6h_rolling_pctl",
    "r6h_mark",
    "severity",
    "severity_code",
    "funding_time_utc",
    "funding_value",
    "funding_rolling_pctl",
    "a2_overlap",
    "regime",
]


def _read_rows_before_cutoff(
    path: Path,
    *,
    time_column: str,
    value_columns: tuple[str, ...],
) -> pd.DataFrame:
    """Read an ascending CSV only until the exclusive preregistered cutoff."""
    rows: list[dict[str, object]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = {time_column, *value_columns} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
        for row in reader:
            timestamp = pd.to_datetime(row[time_column], utc=True)
            if timestamp >= CUTOFF_EXCLUSIVE:
                break
            item: dict[str, object] = {"ts": timestamp}
            for column in value_columns:
                item[column] = pd.to_numeric(row[column], errors="coerce")
            rows.append(item)
    return pd.DataFrame(rows)


def load_hourly_nominal_oi(symbol: str) -> pd.DataFrame:
    path = DATA_DIR / f"{symbol}_METRICS_5M.csv"
    raw = _read_rows_before_cutoff(
        path,
        time_column="create_time",
        value_columns=("sum_open_interest_value",),
    )
    raw["hour"] = raw["ts"].dt.floor("h")
    observed = (
        raw.sort_values("ts")
        .groupby("hour", sort=True)
        .tail(1)
        .set_index("hour")["sum_open_interest_value"]
        .rename("oi_notional")
    )
    grid = pd.date_range(
        observed.index.min(),
        CUTOFF_EXCLUSIVE - pd.Timedelta(hours=1),
        freq="1h",
        tz="UTC",
    )
    return observed.reindex(grid).rename_axis("ts").reset_index()


def load_mark(symbol: str) -> pd.DataFrame:
    path = DATA_DIR / f"{symbol}_MARK_1H.csv"
    frame = _read_rows_before_cutoff(
        path,
        time_column="datetime",
        value_columns=("close",),
    ).rename(columns={"close": "mark_close"})
    if frame["ts"].duplicated().any():
        raise ValueError(f"{path.name} contains duplicate timestamps")
    return frame.sort_values("ts").reset_index(drop=True)


def load_funding(symbol: str) -> pd.DataFrame:
    path = DATA_DIR / f"{symbol}_FUNDING_8H.csv"
    frame = _read_rows_before_cutoff(
        path,
        time_column="datetime",
        value_columns=("last_funding_rate",),
    ).rename(columns={"last_funding_rate": "funding_value"})
    if frame["ts"].duplicated().any():
        raise ValueError(f"{path.name} contains duplicate timestamps")
    frame = frame.sort_values("ts").reset_index(drop=True)
    frame["funding_rolling_pctl"] = rolling_midrank_percentile(
        frame["ts"],
        frame["funding_value"],
        min_observations=1,
    )
    return frame


def daily_regime(mark: pd.DataFrame) -> pd.DataFrame:
    """Build prior-complete-day close/SMA200 regimes without forward fill."""
    prices = mark.copy()
    prices["day"] = prices["ts"].dt.floor("D")
    complete_closes = prices.loc[prices["ts"].dt.hour == 23, ["day", "mark_close"]]
    full_days = pd.date_range(
        prices["day"].min(),
        prices["day"].max(),
        freq="1D",
        tz="UTC",
    )
    daily = (
        complete_closes.drop_duplicates("day", keep="last")
        .set_index("day")
        .reindex(full_days)
        .rename_axis("day")
        .reset_index()
    )
    daily["sma200"] = daily["mark_close"].rolling(200, min_periods=200).mean()
    daily["regime"] = np.where(
        daily["sma200"].isna(),
        "unknown",
        np.where(daily["mark_close"] > daily["sma200"], "bull", "bear"),
    )
    return daily


def annotate_episodes(
    symbol: str,
    episodes: pd.DataFrame,
    funding: pd.DataFrame,
    regimes: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    funding_times = pd.DatetimeIndex(funding["ts"])
    regime_map = regimes.set_index("day")["regime"]
    for episode in episodes.itertuples(index=False):
        event_time = pd.Timestamp(episode.ts)
        funding_index = int(funding_times.searchsorted(event_time, side="left")) - 1
        if funding_index >= 0:
            funding_row = funding.iloc[funding_index]
            funding_time = pd.Timestamp(funding_row["ts"])
            funding_value = float(funding_row["funding_value"])
            funding_percentile = float(funding_row["funding_rolling_pctl"])
            if not np.isfinite(funding_percentile):
                funding_percentile = None
        else:
            funding_time = None
            funding_value = None
            funding_percentile = None
        label, code = severity_label(float(episode.d6h_rolling_pctl))
        prior_day = event_time.floor("D") - pd.Timedelta(days=1)
        rows.append(
            {
                "event_time_utc": event_time,
                "symbol": symbol,
                "oi_notional": float(episode.oi_notional),
                "d6h_pct": float(episode.d6h_pct),
                "d6h_rolling_pctl": float(episode.d6h_rolling_pctl),
                "r6h_mark": float(episode.r6h_mark),
                "severity": label,
                "severity_code": code,
                "funding_time_utc": funding_time,
                "funding_value": funding_value,
                "funding_rolling_pctl": funding_percentile,
                "a2_overlap": (
                    None
                    if funding_percentile is None
                    else int(funding_percentile >= 0.95)
                ),
                "regime": regime_map.get(prior_day, "unknown"),
            }
        )
    return pd.DataFrame(rows, columns=EPISODE_COLUMNS)


def build_pooled_episodes() -> tuple[pd.DataFrame, dict[str, object]]:
    frames: list[pd.DataFrame] = []
    audit: dict[str, object] = {}
    for symbol in SYMBOLS:
        hourly = load_hourly_nominal_oi(symbol)
        mark = load_mark(symbol)
        funding = load_funding(symbol)
        features = add_mark_direction(add_nominal_oi_features(hourly), mark)
        triggers = trigger_rows(features)
        episodes = apply_refractory(triggers)
        annotated = annotate_episodes(symbol, episodes, funding, daily_regime(mark))
        frames.append(annotated)
        audit[symbol] = {
            "hourly_oi_rows": int(len(hourly)),
            "hourly_oi_missing": int(hourly["oi_notional"].isna().sum()),
            "trigger_rows": int(len(triggers)),
            "episode_rows": int(len(episodes)),
        }
    pooled = pd.concat(frames, ignore_index=True)
    pooled = pooled.sort_values(
        ["event_time_utc", "symbol"], kind="mergesort"
    ).reset_index(drop=True)
    return pooled, audit


def _csv_bytes(frame: pd.DataFrame) -> bytes:
    output = frame.copy()
    for column in ("event_time_utc", "funding_time_utc"):
        output[column] = pd.to_datetime(output[column], utc=True).dt.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    return output.to_csv(index=False, lineterminator="\n").encode("utf-8")


def _exclusive_write_key(key: bytes) -> None:
    if ROOT in KEY_PATH.parents:
        raise AssertionError("custodian key path must be outside the project")
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, key)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> None:
    for path in (WORK_PATH, SEALED_PATH, MANIFEST_PATH, KEY_PATH):
        if path.exists():
            raise FileExistsError(f"one-time custodian output already exists: {path}")
    # Fail before loading event inputs when this process is not the authorized
    # external custodian principal.
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

    pooled, source_audit = build_pooled_episodes()
    work, sealed = split_work_sealed(pooled)
    work_payload = _csv_bytes(work)
    sealed_payload = bytearray(_csv_bytes(sealed))
    key = os.urandom(32)
    nonce = os.urandom(12)
    encrypted = encrypt_aes256_gcm(bytes(sealed_payload), key, nonce)

    _exclusive_write_key(key)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_write(WORK_PATH, work_payload)
    _atomic_write(SEALED_PATH, encrypted)

    generated_at = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "task_id": "A1_TIERA",
        "generated_at_utc": generated_at,
        "cutoff_exclusive_utc": CUTOFF_EXCLUSIVE.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "custodian": "main-session independent principal",
        "split_rule": "sort (event_time_utc, symbol); every fifth row sealed",
        "work_rows": int(len(work)),
        "sealed_rows": int(len(sealed)),
        "schema": EPISODE_COLUMNS,
        "git_hash": _git_head(),
        "generation_code_sha256": {
            "a1_tiera_custodian.py": sha256_file(Path(__file__)),
            "a1_tiera_core.py": sha256_file(Path(__file__).with_name("a1_tiera_core.py")),
        },
        "work_plaintext_sha256": sha256_bytes(work_payload),
        "sealed_plaintext_sha256": sha256_bytes(bytes(sealed_payload)),
        "sealed_ciphertext_sha256": sha256_bytes(encrypted),
        "cipher": "AES-256-GCM",
        "format": "12B nonce || ciphertext || 16B GCM tag",
        "key_location": "~/.aiquant_sealed/a1/a1_key.bin",
        "unseal_condition": "Tier A PASS and Founder approval",
        "one_time_use": {
            "used": False,
            "used_at_utc": None,
            "approved_by": None,
            "purpose": None,
        },
        "source_audit": source_audit,
        "implementation_differences": [
            "Rebuilt from sum_open_interest_value; prior feature used sum_open_interest.",
            "Warmup uses only the v5 d6h valid-day and valid-observation predicate.",
            "Trigger includes the frozen r6h_mark < 0 condition before refractory.",
        ],
    }
    _atomic_write(
        MANIFEST_PATH,
        (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )

    # Custodian and executor are separate processes. Drop sealed plaintext
    # references here; executor code never imports this module or decrypts .enc.
    release_plaintext(sealed_payload)
    del sealed_payload, sealed, pooled, key, nonce
    gc.collect()
    print(
        json.dumps(
            {
                "status": "custodian_complete",
                "work_rows": len(work),
                "sealed_rows": manifest["sealed_rows"],
                "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
