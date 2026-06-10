#!/usr/bin/env python3
"""Download and audit official Binance Futures daily metrics archives."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from http.client import HTTPException
from io import BytesIO
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
BASE = "https://data.binance.vision/data/futures/um/daily/metrics"
LATEST = date(2026, 6, 5)
STARTS = {
    "BTCUSDT": date(2020, 9, 1),
    "ETHUSDT": date(2021, 12, 1),
    "SOLUSDT": date(2021, 12, 1),
}


def archive_url(symbol: str, day: date) -> str:
    return f"{BASE}/{symbol}/{symbol}-metrics-{day}.zip"


def download_day(symbol: str, day: date) -> pd.DataFrame:
    url = archive_url(symbol, day)
    for attempt in range(4):
        try:
            request = Request(url, headers={"User-Agent": "AI-Quant-Research/1.0"})
            with urlopen(request, timeout=30) as response:
                payload = response.read()
            with ZipFile(BytesIO(payload)) as archive:
                names = archive.namelist()
                if len(names) != 1:
                    raise ValueError(f"{symbol} {day}: unexpected archive")
                return pd.read_csv(archive.open(names[0]))
        except (HTTPError, URLError, TimeoutError, OSError, HTTPException):
            if attempt == 3:
                raise
            time.sleep(0.5 * 2**attempt)
    raise RuntimeError("unreachable")


def date_range(start: date, end: date) -> list[date]:
    return [
        start + timedelta(days=offset)
        for offset in range((end - start).days + 1)
    ]


def audit_symbol(symbol: str) -> dict[str, object]:
    days = date_range(STARTS[symbol], LATEST)
    output_path = DATA_DIR / f"{symbol}_METRICS_5M.csv"
    duplicate_count = 0
    if output_path.exists():
        combined = pd.read_csv(output_path, parse_dates=["create_time"])
    else:
        frames: dict[date, pd.DataFrame] = {}
        failures: list[str] = []
        with ThreadPoolExecutor(max_workers=16) as executor:
            jobs = {
                executor.submit(download_day, symbol, day): day
                for day in days
            }
            for future in as_completed(jobs):
                day = jobs[future]
                try:
                    frames[day] = future.result()
                except Exception as error:
                    failures.append(f"{day}: {type(error).__name__}")
        if failures:
            raise RuntimeError(f"{symbol} download failures: {failures[:10]}")

        combined = pd.concat(
            [frames[day] for day in sorted(frames)],
            ignore_index=True,
        )
        combined["create_time"] = pd.to_datetime(combined["create_time"])
        raw_rows = len(combined)
        combined = combined.sort_values("create_time").drop_duplicates(
            "create_time"
        )
        duplicate_count = raw_rows - len(combined)
        combined.to_csv(output_path, index=False)

    intervals = combined["create_time"].diff().dropna()
    expected_rows = len(days) * 288
    metric_columns = [
        column
        for column in combined.columns
        if column not in {"create_time", "symbol"}
    ]
    field_coverage = {}
    for column in metric_columns:
        valid = combined.loc[combined[column].notna(), ["create_time", column]]
        field_coverage[column] = {
            "valid_rows": int(len(valid)),
            "null_rows": int(combined[column].isna().sum()),
            "first_valid_timestamp": str(valid["create_time"].min()),
            "last_valid_timestamp": str(valid["create_time"].max()),
            "valid_calendar_days": int(
                valid["create_time"].dt.normalize().nunique()
            ),
            "observations_grade": (
                "CONFIRMATORY" if len(valid) >= 500 else "EXPLORATORY"
            ),
        }
    return {
        "symbol": symbol,
        "source": BASE,
        "archive_start": str(STARTS[symbol]),
        "archive_end": str(LATEST),
        "calendar_days": len(days),
        "rows": int(len(combined)),
        "expected_5m_rows": expected_rows,
        "coverage_ratio": float(len(combined) / expected_rows),
        "first_timestamp": str(combined["create_time"].min()),
        "last_timestamp": str(combined["create_time"].max()),
        "frequency_mode": str(intervals.mode().iloc[0]),
        "timestamp_jitter_from_exact_5m": int(
            (intervals != pd.Timedelta(minutes=5)).sum()
        ),
        "gaps_over_6m": int(
            (intervals > pd.Timedelta(minutes=6)).sum()
        ),
        "null_count_by_column": {
            column: int(combined[column].isna().sum())
            for column in combined.columns
        },
        "duplicate_timestamps_removed": int(duplicate_count),
        "columns": combined.columns.tolist(),
        "field_coverage": field_coverage,
        "output": str(output_path.relative_to(ROOT)),
        "observations_grade": (
            "CONFIRMATORY" if len(combined) >= 500 else "EXPLORATORY"
        ),
        "covers_2021_bull": bool(
            combined["create_time"].min() <= pd.Timestamp("2021-01-01")
            and combined["create_time"].max() >= pd.Timestamp("2021-12-31")
        ),
        "covers_2022_bear": bool(
            combined["create_time"].min() <= pd.Timestamp("2022-01-01")
            and combined["create_time"].max() >= pd.Timestamp("2022-12-31")
        ),
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "source": "official Binance public data archive",
        "latest_checked": str(LATEST),
        "symbols": [audit_symbol(symbol) for symbol in STARTS],
    }
    path = OUTPUT_DIR / "p1_03_data_recon_oi.json"
    path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
