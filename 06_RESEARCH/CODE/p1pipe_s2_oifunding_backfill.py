#!/usr/bin/env python3
"""
P1-RES-039-PIPELINE Step 2: Binance Data Vision OI metrics + funding backfill.

Scope:
- Free public sources only.
- Writes a new data directory; never overwrites legacy FUTURES data.
- Downloads post-2025 data needed by the unlock-event pipeline.
- Records per-file checksums and HTTP statuses in a manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[2]
S1_JSON = ROOT / "06_RESEARCH" / "CODE" / "output" / "p1pipe_s1_panel_audit.json"
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_OI_FUNDING_2026"
OUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
AUDIT_PATH = OUT_DIR / "p1pipe_s2_oifunding_audit.json"
MANIFEST_PATH = DATA_DIR / "manifest.json"
FUNDING_DIR = DATA_DIR / "funding_8h"
METRICS_DIR = DATA_DIR / "metrics_4h"

DATA_VISION = "https://data.binance.vision/data/futures/um"
BINANCE_FUNDING_REST = "https://fapi.binance.com/fapi/v1/fundingRate"
USER_AGENT = "AI-Quant-Research/1.0"


@dataclass(frozen=True)
class FetchResult:
    url: str
    ok: bool
    status: int | None
    size_bytes: int
    sha256: str | None
    error_type: str | None
    error: str | None
    payload: bytes | None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2025-01-01", help="UTC inclusive start date")
    parser.add_argument("--end", default="2026-06-22", help="UTC inclusive end date")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--symbols", default="", help="Comma-separated symbols without USDT suffix")
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument("--skip-funding", action="store_true")
    return parser.parse_args()


def load_symbols(symbol_arg: str) -> list[str]:
    if symbol_arg.strip():
        return [s.strip().upper().replace("USDT", "") for s in symbol_arg.split(",") if s.strip()]
    data = json.loads(S1_JSON.read_text(encoding="utf-8"))
    return list(data["post_2025_event_eligible_universe"])


def request_bytes(url: str, timeout: int) -> FetchResult:
    started = time.time()
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
            status = getattr(response, "status", None)
        sha = hashlib.sha256(payload).hexdigest()
        return FetchResult(url, True, status, len(payload), sha, None, None, payload)
    except HTTPError as error:
        payload = error.read()
        return FetchResult(
            url=url,
            ok=False,
            status=error.code,
            size_bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest() if payload else None,
            error_type="HTTPError",
            error=str(error),
            payload=None,
        )
    except (URLError, TimeoutError, OSError) as error:
        return FetchResult(url, False, None, 0, None, type(error).__name__, str(error), None)


def month_starts(start: date, end: date) -> list[date]:
    current = date(start.year, start.month, 1)
    months = []
    while current <= end:
        months.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def day_range(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def csv_from_zip(payload: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        csv_names = [name for name in zf.namelist() if name.endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"expected one csv in zip, got {csv_names}")
        with zf.open(csv_names[0]) as handle:
            return pd.read_csv(handle)


def funding_month_url(symbol: str, month: date) -> str:
    return (
        f"{DATA_VISION}/monthly/fundingRate/{symbol}USDT/"
        f"{symbol}USDT-fundingRate-{month.year:04d}-{month.month:02d}.zip"
    )


def metrics_day_url(symbol: str, day: date) -> str:
    return (
        f"{DATA_VISION}/daily/metrics/{symbol}USDT/"
        f"{symbol}USDT-metrics-{day.year:04d}-{day.month:02d}-{day.day:02d}.zip"
    )


def parse_funding_frame(df: pd.DataFrame, source: str) -> pd.DataFrame:
    out = df.copy()
    if "calc_time" not in out.columns or "last_funding_rate" not in out.columns:
        raise ValueError(f"funding frame missing required columns: {list(out.columns)}")
    out["datetime"] = pd.to_datetime(pd.to_numeric(out["calc_time"]), unit="ms", utc=True).dt.tz_convert(None)
    out["last_funding_rate"] = pd.to_numeric(out["last_funding_rate"], errors="coerce")
    if "funding_interval_hours" in out.columns:
        out["funding_interval_hours"] = pd.to_numeric(out["funding_interval_hours"], errors="coerce")
    else:
        out["funding_interval_hours"] = 8
    out["source"] = source
    return out[["datetime", "funding_interval_hours", "last_funding_rate", "source"]].dropna(
        subset=["datetime", "last_funding_rate"]
    )


def fetch_funding_rest(symbol: str, start: date, end: date, timeout: int) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    end_dt = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=timezone.utc)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    params = {"symbol": f"{symbol}USDT", "startTime": start_ms, "endTime": end_ms, "limit": 1000}
    url = f"{BINANCE_FUNDING_REST}?{urlencode(params)}"
    result: FetchResult
    try:
        response = requests.get(BINANCE_FUNDING_REST, params=params, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        payload_bytes = response.content
        result = FetchResult(
            url=response.url,
            ok=response.status_code == 200,
            status=response.status_code,
            size_bytes=len(payload_bytes),
            sha256=hashlib.sha256(payload_bytes).hexdigest() if payload_bytes else None,
            error_type=None if response.status_code == 200 else "HTTPStatus",
            error=None if response.status_code == 200 else response.text[:500],
            payload=payload_bytes if response.status_code == 200 else None,
        )
    except requests.RequestException as error:
        result = FetchResult(url, False, None, 0, None, type(error).__name__, str(error), None)
    record = {
        "kind": "funding_rest",
        "symbol": symbol,
        "url": result.url,
        "ok": result.ok,
        "status": result.status,
        "size_bytes": result.size_bytes,
        "sha256": result.sha256,
        "error_type": result.error_type,
        "error": result.error,
    }
    if not result.ok or result.payload is None:
        return [record], pd.DataFrame(columns=["datetime", "funding_interval_hours", "last_funding_rate", "source"])
    payload = json.loads(result.payload.decode("utf-8"))
    if isinstance(payload, dict):
        record["ok"] = False
        record["error_type"] = "BinanceRESTError"
        record["error"] = json.dumps(payload, ensure_ascii=False)
        return [record], pd.DataFrame(columns=["datetime", "funding_interval_hours", "last_funding_rate", "source"])
    rows = []
    for item in payload:
        rows.append(
            {
                "datetime": pd.to_datetime(int(item["fundingTime"]), unit="ms", utc=True).tz_convert(None),
                "funding_interval_hours": 8,
                "last_funding_rate": float(item["fundingRate"]),
                "source": "binance_fapi_rest",
            }
        )
    return [record], pd.DataFrame(rows)


def fetch_symbol_funding(symbol: str, start: date, end: date, timeout: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    frames: list[pd.DataFrame] = []
    for month in month_starts(start, end):
        # Current month is normally unavailable as a monthly Data Vision archive; REST supplements it.
        if month == date(end.year, end.month, 1):
            continue
        url = funding_month_url(symbol, month)
        result = request_bytes(url, timeout)
        records.append(
            {
                "kind": "funding_datavision_monthly",
                "symbol": symbol,
                "period": month.strftime("%Y-%m"),
                "url": result.url,
                "ok": result.ok,
                "status": result.status,
                "size_bytes": result.size_bytes,
                "sha256": result.sha256,
                "error_type": result.error_type,
                "error": result.error,
            }
        )
        if result.ok and result.payload:
            try:
                frames.append(parse_funding_frame(csv_from_zip(result.payload), "binance_data_vision_monthly"))
            except Exception as error:  # noqa: BLE001 - persisted for audit
                records[-1]["ok"] = False
                records[-1]["error_type"] = type(error).__name__
                records[-1]["error"] = str(error)
        time.sleep(0.05)

    rest_records, rest_frame = fetch_funding_rest(symbol, date(end.year, end.month, 1), end, timeout)
    records.extend(rest_records)
    if not rest_frame.empty:
        frames.append(rest_frame)

    if frames:
        out = pd.concat(frames, ignore_index=True)
        out = out.sort_values("datetime").drop_duplicates("datetime", keep="last")
        out = out[(out["datetime"] >= pd.Timestamp(start)) & (out["datetime"] <= pd.Timestamp(end) + pd.Timedelta(days=1))]
    else:
        out = pd.DataFrame(columns=["datetime", "funding_interval_hours", "last_funding_rate", "source"])

    path = FUNDING_DIR / f"{symbol}USDT_funding_8h.csv"
    out.to_csv(path, index=False)
    ok_records = [r for r in records if r["ok"]]
    summary = {
        "symbol": symbol,
        "output_file": str(path.relative_to(ROOT)),
        "rows": int(len(out)),
        "start": out["datetime"].min().isoformat() if not out.empty else None,
        "end": out["datetime"].max().isoformat() if not out.empty else None,
        "successful_source_files_or_calls": len(ok_records),
        "failed_source_files_or_calls": len(records) - len(ok_records),
        "output_sha256": sha256_file(path),
    }
    return records, summary


def parse_metrics_frame(df: pd.DataFrame) -> pd.DataFrame:
    required = ["create_time", "sum_open_interest", "sum_open_interest_value"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"metrics frame missing columns: {missing}")
    out = df.copy()
    out["create_time"] = pd.to_datetime(out["create_time"], utc=True).dt.tz_convert(None)
    numeric_cols = [c for c in out.columns if c not in {"create_time", "symbol"}]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["datetime"] = out["create_time"].dt.floor("4h")
    agg = out.sort_values("create_time").groupby("datetime", as_index=False).agg(
        sum_open_interest_last=("sum_open_interest", "last"),
        sum_open_interest_value_last=("sum_open_interest_value", "last"),
        sum_open_interest_mean=("sum_open_interest", "mean"),
        sum_open_interest_value_mean=("sum_open_interest_value", "mean"),
        count_toptrader_long_short_ratio_last=("count_toptrader_long_short_ratio", "last"),
        sum_toptrader_long_short_ratio_last=("sum_toptrader_long_short_ratio", "last"),
        count_long_short_ratio_last=("count_long_short_ratio", "last"),
        sum_taker_long_short_vol_ratio_last=("sum_taker_long_short_vol_ratio", "last"),
        observations=("create_time", "count"),
    )
    return agg


def fetch_one_metrics_day(symbol: str, day: date, timeout: int) -> tuple[dict[str, Any], pd.DataFrame | None]:
    url = metrics_day_url(symbol, day)
    result = request_bytes(url, timeout)
    record = {
        "kind": "metrics_datavision_daily",
        "symbol": symbol,
        "date": day.isoformat(),
        "url": result.url,
        "ok": result.ok,
        "status": result.status,
        "size_bytes": result.size_bytes,
        "sha256": result.sha256,
        "error_type": result.error_type,
        "error": result.error,
    }
    if result.ok and result.payload:
        try:
            return record, parse_metrics_frame(csv_from_zip(result.payload))
        except Exception as error:  # noqa: BLE001
            record["ok"] = False
            record["error_type"] = type(error).__name__
            record["error"] = str(error)
    return record, None


def fetch_symbol_metrics(
    symbol: str, start: date, end: date, timeout: int, workers: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    days = day_range(start, end)
    records: list[dict[str, Any]] = []
    frames: list[pd.DataFrame] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_one_metrics_day, symbol, day, timeout): day for day in days}
        for idx, future in enumerate(as_completed(futures), 1):
            record, frame = future.result()
            records.append(record)
            if frame is not None and not frame.empty:
                frames.append(frame)
            if idx % 100 == 0:
                print(f"[metrics] {symbol}: {idx}/{len(days)} days processed")

    if frames:
        out = pd.concat(frames, ignore_index=True)
        out = out.sort_values("datetime").drop_duplicates("datetime", keep="last")
    else:
        out = pd.DataFrame(
            columns=[
                "datetime",
                "sum_open_interest_last",
                "sum_open_interest_value_last",
                "sum_open_interest_mean",
                "sum_open_interest_value_mean",
                "count_toptrader_long_short_ratio_last",
                "sum_toptrader_long_short_ratio_last",
                "count_long_short_ratio_last",
                "sum_taker_long_short_vol_ratio_last",
                "observations",
            ]
        )
    path = METRICS_DIR / f"{symbol}USDT_metrics_4h.csv"
    out.to_csv(path, index=False)
    ok_records = [r for r in records if r["ok"]]
    summary = {
        "symbol": symbol,
        "output_file": str(path.relative_to(ROOT)),
        "rows": int(len(out)),
        "start": out["datetime"].min().isoformat() if not out.empty else None,
        "end": out["datetime"].max().isoformat() if not out.empty else None,
        "successful_daily_archives": len(ok_records),
        "failed_daily_archives": len(records) - len(ok_records),
        "output_sha256": sha256_file(path),
    }
    return records, summary


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def coverage_gaps(summary: dict[str, Any], expected_start: date, expected_end: date, freq: str) -> dict[str, Any]:
    if summary["rows"] == 0 or summary["start"] is None or summary["end"] is None:
        return {"coverage_status": "empty", "expected_start": expected_start.isoformat(), "expected_end": expected_end.isoformat()}
    start = pd.Timestamp(summary["start"]).date().isoformat()
    end = pd.Timestamp(summary["end"]).date().isoformat()
    return {
        "coverage_status": "partial" if start > expected_start.isoformat() or end < expected_end.isoformat() else "covers_requested_window",
        "expected_start": expected_start.isoformat(),
        "expected_end": expected_end.isoformat(),
        "actual_start_date": start,
        "actual_end_date": end,
        "frequency": freq,
    }


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    symbols = load_symbols(args.symbols)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FUNDING_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "task_id": "P1-RES-039-PIPELINE-S2",
        "generated_at": utc_now_iso(),
        "requested_window": {"start": start.isoformat(), "end": end.isoformat()},
        "source": {
            "funding_datavision": f"{DATA_VISION}/monthly/fundingRate/{{SYMBOL}}USDT/",
            "metrics_datavision": f"{DATA_VISION}/daily/metrics/{{SYMBOL}}USDT/",
            "funding_rest_supplement": BINANCE_FUNDING_REST,
        },
        "discipline": {
            "holdout_touched": False,
            "paid_api_used": False,
            "legacy_data_overwritten": False,
            "data_output_dir": str(DATA_DIR.relative_to(ROOT)),
        },
        "symbols": symbols,
        "records": [],
    }
    audit: dict[str, Any] = {
        "task_id": "P1-RES-039-PIPELINE-S2",
        "generated_at": utc_now_iso(),
        "requested_window": {"start": start.isoformat(), "end": end.isoformat()},
        "symbols": symbols,
        "funding": [],
        "metrics": [],
    }

    for idx, symbol in enumerate(symbols, 1):
        print(f"[symbol] {idx}/{len(symbols)} {symbol}")
        if not args.skip_funding:
            records, summary = fetch_symbol_funding(symbol, start, end, args.timeout)
            manifest["records"].extend(records)
            summary["coverage"] = coverage_gaps(summary, start, end, "8h")
            audit["funding"].append(summary)
            write_manifest(manifest)
        if not args.skip_metrics:
            records, summary = fetch_symbol_metrics(symbol, start, end, args.timeout, max(1, args.workers))
            manifest["records"].extend(records)
            summary["coverage"] = coverage_gaps(summary, start, end, "4h")
            audit["metrics"].append(summary)
            write_manifest(manifest)

    manifest["completed_at"] = utc_now_iso()
    manifest["record_count"] = len(manifest["records"])
    write_manifest(manifest)

    audit["completed_at"] = utc_now_iso()
    audit["manifest_file"] = str(MANIFEST_PATH.relative_to(ROOT))
    audit["output_dir"] = str(DATA_DIR.relative_to(ROOT))
    audit["summary"] = {
        "funding_symbols_with_rows": sum(1 for item in audit["funding"] if item["rows"] > 0),
        "metrics_symbols_with_rows": sum(1 for item in audit["metrics"] if item["rows"] > 0),
        "funding_empty_symbols": [item["symbol"] for item in audit["funding"] if item["rows"] == 0],
        "metrics_empty_symbols": [item["symbol"] for item in audit["metrics"] if item["rows"] == 0],
        "funding_partial_symbols": [
            item["symbol"] for item in audit["funding"] if item["coverage"]["coverage_status"] != "covers_requested_window"
        ],
        "metrics_partial_symbols": [
            item["symbol"] for item in audit["metrics"] if item["coverage"]["coverage_status"] != "covers_requested_window"
        ],
    }
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(AUDIT_PATH)


if __name__ == "__main__":
    main()
