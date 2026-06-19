"""Audit inputs for the approved carry v4 feasibility run.

This script deliberately does not run the earlier simplified carry engine as a
v4 acceptance executor. It records whether the frozen v4-required source fields
are present before any work/sealed split or acceptance calculation is claimed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RESEARCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RESEARCH_ROOT.parent
DATA = RESEARCH_ROOT / "DATA"
FUTURES = DATA / "FUTURES"
OUTPUT = RESEARCH_ROOT / "CODE" / "output"
CUTOFF = "2024-12-10T00:00:00Z"
CUTOFF_PREFIX = "2024-12-10"


FILES = {
    "BTCUSDT_funding_8h": FUTURES / "BTCUSDT_FUNDING_8H.csv",
    "ETHUSDT_funding_8h": FUTURES / "ETHUSDT_FUNDING_8H.csv",
    "BTCUSDT_mark_1h": FUTURES / "BTCUSDT_MARK_1H.csv",
    "ETHUSDT_mark_1h": FUTURES / "ETHUSDT_MARK_1H.csv",
    "BTCUSDT_spot_1h": DATA / "BTCUSDT_SPOT_1H.csv",
    "ETHUSDT_spot_1h": DATA / "ETHUSDT_SPOT_1H.csv",
    "BTCUSDT_metrics_5m": FUTURES / "BTCUSDT_METRICS_5M.csv",
    "ETHUSDT_metrics_5m": FUTURES / "ETHUSDT_METRICS_5M.csv",
}


V4_REQUIRED_INPUTS = {
    "funding_actual_8h": {
        "available_from": ["BTCUSDT_funding_8h", "ETHUSDT_funding_8h"],
        "status": "available",
    },
    "spot_1h_open_close": {
        "available_from": ["BTCUSDT_spot_1h", "ETHUSDT_spot_1h"],
        "status": "missing_open",
        "reason": "spot files expose close only; v4 needs next 1H open for spot executions",
    },
    "perpetual_contract_1h_ohlc": {
        "available_from": [],
        "status": "missing",
        "reason": "only mark OHLC files are present; v4 basis attribution requires contract OHLC separately from mark",
    },
    "mark_1h_ohlc": {
        "available_from": ["BTCUSDT_mark_1h", "ETHUSDT_mark_1h"],
        "status": "available",
    },
    "index_1h_close": {
        "available_from": [],
        "status": "missing",
        "reason": "v4 depeg and delta reference require Binance index close",
    },
    "oi_5m": {
        "available_from": ["BTCUSDT_metrics_5m", "ETHUSDT_metrics_5m"],
        "status": "available",
    },
    "historical_leverage_brackets": {
        "available_from": [],
        "status": "missing",
        "reason": "v4 requires floor/cap/mmr/cum at each historical hour",
    },
    "liquidation_clearance_fee_rate": {
        "available_from": [],
        "status": "missing",
        "reason": "v4 requires historical clearance fee by bracket",
    },
    "withdrawal_status": {
        "available_from": [],
        "status": "missing",
        "reason": "v4 requires frozen BTC/ETH/USDT withdrawal status or announcements",
    },
    "usdtusd_cross_indices": {
        "available_from": [],
        "status": "missing",
        "reason": "v4 requires BTCUSD/ETHUSD coin-m and BTCUSDT/ETHUSDT USD-M index cross prices",
    },
    "adl_execution_records": {
        "available_from": [],
        "status": "missing",
        "reason": "v4 requires official execution quantity and price if ADL occurs",
    },
}


def forbid_holdout_or_sealed(path: Path) -> None:
    parts = [part.upper() for part in path.parts]
    resolved_parts = [part.upper() for part in path.resolve(strict=False).parts]
    if any("HOLDOUT" in part or "SEALED" in part for part in parts + resolved_parts):
        raise ValueError(f"forbidden input path: {path}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sniff_csv(path: Path) -> dict[str, Any]:
    forbid_holdout_or_sealed(path)
    exists = path.exists()
    payload: dict[str, Any] = {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "exists": exists,
    }
    if not exists:
        return payload

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        rows = 0
        pre_cutoff_rows = 0
        post_cutoff_rows = 0
        min_ts: str | None = None
        max_ts: str | None = None
        time_col = next(
            (
                name
                for name in ("datetime", "open_time", "create_time", "timestamp", "time")
                if name in columns
            ),
            None,
        )
        for row in reader:
            rows += 1
            if time_col:
                value = row.get(time_col)
                if value:
                    min_ts = value if min_ts is None or value < min_ts else min_ts
                    max_ts = value if max_ts is None or value > max_ts else max_ts
                    if value[:10] < CUTOFF_PREFIX:
                        pre_cutoff_rows += 1
                    else:
                        post_cutoff_rows += 1
    payload.update(
        {
            "columns": columns,
            "rows": rows,
            "pre_cutoff_rows": pre_cutoff_rows if time_col else None,
            "post_cutoff_rows": post_cutoff_rows if time_col else None,
            "time_column": time_col,
            "min_timestamp_raw": min_ts,
            "max_timestamp_raw": max_ts,
            "sha256": sha256_file(path),
        }
    )
    return payload


def build_audit() -> dict[str, Any]:
    file_audit = {name: sniff_csv(path) for name, path in FILES.items()}
    hard_missing = {
        name: item
        for name, item in V4_REQUIRED_INPUTS.items()
        if item["status"] not in {"available"}
    }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cutoff_exclusive_utc": CUTOFF,
        "protocol": "CARRY_DELTA_NEUTRAL_PREREG_v4",
        "holdout_or_sealed_input_read": False,
        "file_audit": file_audit,
        "v4_required_input_status": V4_REQUIRED_INPUTS,
        "v4_acceptance_executable": len(hard_missing) == 0,
        "hard_missing_or_incomplete_inputs": hard_missing,
        "executor_decision": (
            "do_not_run_simplified_engine_as_v4_acceptance"
            if hard_missing
            else "inputs_complete_for_executor"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT / "carry_feasibility_v4_input_audit.json",
    )
    args = parser.parse_args()
    audit = build_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
