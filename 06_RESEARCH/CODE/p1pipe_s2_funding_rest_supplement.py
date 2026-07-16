#!/usr/bin/env python3
"""
Supplement Step 2 funding gaps with Binance fapi REST via curl.

This is a narrow fallback for symbols where Data Vision monthly archives cover
through 2026-05 but Python HTTPS calls intermittently failed for 2026-06.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_OI_FUNDING_2026"
FUNDING_DIR = DATA_DIR / "funding_8h"
METRICS_DIR = DATA_DIR / "metrics_4h"
MANIFEST_PATH = DATA_DIR / "manifest.json"
AUDIT_PATH = ROOT / "06_RESEARCH" / "CODE" / "output" / "p1pipe_s2_oifunding_audit.json"
END = pd.Timestamp("2026-06-22 23:59:59")
START = pd.Timestamp("2025-01-01 00:00:00")
REST_URL = "https://fapi.binance.com/fapi/v1/fundingRate"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ms(ts: pd.Timestamp) -> int:
    return int(ts.tz_localize("UTC").timestamp() * 1000)


def curl_json(symbol: str, start: pd.Timestamp) -> tuple[dict, list[dict]]:
    params = {
        "symbol": f"{symbol}USDT",
        "startTime": ms(start),
        "endTime": ms(END),
        "limit": 1000,
    }
    url = f"{REST_URL}?{urlencode(params)}"
    result = subprocess.run(
        ["curl", "-sS", "--max-time", "30", url],
        check=False,
        capture_output=True,
    )
    payload = result.stdout
    record = {
        "kind": "funding_rest_curl_supplement",
        "symbol": symbol,
        "url": url,
        "ok": False,
        "status": None,
        "size_bytes": len(payload),
        "sha256": sha256_bytes(payload) if payload else None,
        "error_type": None,
        "error": None,
    }
    if result.returncode != 0:
        record["error_type"] = "curl_error"
        record["error"] = result.stderr.decode("utf-8", errors="replace")[:500]
        return record, []
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except Exception as error:  # noqa: BLE001
        record["error_type"] = type(error).__name__
        record["error"] = str(error)
        return record, []
    if isinstance(parsed, dict):
        record["error_type"] = "BinanceRESTError"
        record["error"] = json.dumps(parsed, ensure_ascii=False)[:500]
        return record, []
    record["ok"] = True
    record["status"] = 200
    return record, parsed


def recompute_audit(manifest: dict) -> None:
    symbols = manifest["symbols"]
    funding = []
    metrics = []
    for symbol in symbols:
        fpath = FUNDING_DIR / f"{symbol}USDT_funding_8h.csv"
        mpath = METRICS_DIR / f"{symbol}USDT_metrics_4h.csv"
        fdf = pd.read_csv(fpath, parse_dates=["datetime"]) if fpath.exists() else pd.DataFrame()
        mdf = pd.read_csv(mpath, parse_dates=["datetime"]) if mpath.exists() else pd.DataFrame()
        funding.append(
            {
                "symbol": symbol,
                "output_file": str(fpath.relative_to(ROOT)),
                "rows": int(len(fdf)),
                "start": fdf["datetime"].min().isoformat() if not fdf.empty else None,
                "end": fdf["datetime"].max().isoformat() if not fdf.empty else None,
                "output_sha256": sha256_file(fpath) if fpath.exists() else None,
                "coverage": coverage(fdf, "8h"),
            }
        )
        metrics.append(
            {
                "symbol": symbol,
                "output_file": str(mpath.relative_to(ROOT)),
                "rows": int(len(mdf)),
                "start": mdf["datetime"].min().isoformat() if not mdf.empty else None,
                "end": mdf["datetime"].max().isoformat() if not mdf.empty else None,
                "output_sha256": sha256_file(mpath) if mpath.exists() else None,
                "coverage": coverage(mdf, "4h"),
            }
        )
    audit = {
        "task_id": "P1-RES-039-PIPELINE-S2",
        "generated_at": utc_now_iso(),
        "requested_window": {"start": START.date().isoformat(), "end": END.date().isoformat()},
        "symbols": symbols,
        "funding": funding,
        "metrics": metrics,
        "manifest_file": str(MANIFEST_PATH.relative_to(ROOT)),
        "output_dir": str(DATA_DIR.relative_to(ROOT)),
        "summary": {
            "funding_symbols_with_rows": sum(1 for item in funding if item["rows"] > 0),
            "metrics_symbols_with_rows": sum(1 for item in metrics if item["rows"] > 0),
            "funding_empty_symbols": [item["symbol"] for item in funding if item["rows"] == 0],
            "metrics_empty_symbols": [item["symbol"] for item in metrics if item["rows"] == 0],
            "funding_partial_symbols": [
                item["symbol"] for item in funding if item["coverage"]["coverage_status"] != "covers_requested_window"
            ],
            "metrics_partial_symbols": [
                item["symbol"] for item in metrics if item["coverage"]["coverage_status"] != "covers_requested_window"
            ],
        },
    }
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")


def coverage(df: pd.DataFrame, freq: str) -> dict:
    if df.empty:
        return {
            "coverage_status": "empty",
            "expected_start": START.date().isoformat(),
            "expected_end": END.date().isoformat(),
            "frequency": freq,
        }
    actual_start = df["datetime"].min().date().isoformat()
    actual_end = df["datetime"].max().date().isoformat()
    return {
        "coverage_status": (
            "partial"
            if actual_start > START.date().isoformat() or actual_end < END.date().isoformat()
            else "covers_requested_window"
        ),
        "expected_start": START.date().isoformat(),
        "expected_end": END.date().isoformat(),
        "actual_start_date": actual_start,
        "actual_end_date": actual_end,
        "frequency": freq,
    }


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = manifest.setdefault("records", [])
    supplemented = []
    for symbol in manifest["symbols"]:
        path = FUNDING_DIR / f"{symbol}USDT_funding_8h.csv"
        df = pd.read_csv(path, parse_dates=["datetime"])
        if df.empty or df["datetime"].max() >= END - pd.Timedelta(hours=8):
            continue
        start = df["datetime"].max() + pd.Timedelta(milliseconds=1)
        record, rows = curl_json(symbol, start)
        records.append(record)
        if rows:
            add = pd.DataFrame(
                [
                    {
                        "datetime": pd.to_datetime(int(row["fundingTime"]), unit="ms", utc=True).tz_convert(None),
                        "funding_interval_hours": 8,
                        "last_funding_rate": float(row["fundingRate"]),
                        "source": "binance_fapi_rest_curl_supplement",
                    }
                    for row in rows
                ]
            )
            merged = pd.concat([df, add], ignore_index=True)
            merged = merged.sort_values("datetime").drop_duplicates("datetime", keep="last")
            merged.to_csv(path, index=False)
            supplemented.append({"symbol": symbol, "rows_added": int(len(add)), "new_end": merged["datetime"].max().isoformat()})
        else:
            supplemented.append({"symbol": symbol, "rows_added": 0, "new_end": df["datetime"].max().isoformat()})
    manifest["supplement_completed_at"] = utc_now_iso()
    manifest["record_count"] = len(records)
    manifest["funding_rest_curl_supplement"] = supplemented
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    recompute_audit(manifest)
    print(json.dumps({"supplemented": supplemented}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
