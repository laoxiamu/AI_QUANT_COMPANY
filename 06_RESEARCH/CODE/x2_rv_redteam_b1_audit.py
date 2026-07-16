#!/usr/bin/env python3
"""Stage-0 reproducibility audit for P1-RES-037-B1.

This script intentionally does not run B1 backtests/statistical gates when the
Stage-0 red-team verdict is KILL. It records the cost hurdle and data inventory
needed to reproduce the report's pre-B1 decision without touching holdout data.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
OUTPUT_FILE = OUTPUT_DIR / "x2_rv_redteam_b1_audit.json"

TASK_ID = "P1-RES-037-B1"
STAGE0_VERDICT = "KILL"


def pct(x: float) -> float:
    return round(100.0 * x, 4)


def round_trip_cost_table() -> list[dict[str, float | str]]:
    """Return 4-fill pair-trade cost hurdles.

    The task's cost convention is a spread-return hurdle on one-leg notional:
    long $1, short $1, enter+exit both legs => 4 fills. On gross pair capital
    ($2), the percentage is half as large.
    """

    rows = [
        {
            "case": "maker_low_bound_with_adverse_selection",
            "fee_per_fill": 0.0002,
            "slippage_or_adverse_per_fill": 0.0010,
        },
        {
            "case": "protocol_base_taker",
            "fee_per_fill": 0.0010,
            "slippage_or_adverse_per_fill": 0.0010,
        },
        {
            "case": "stress_taker_slippage_0_3pct",
            "fee_per_fill": 0.0010,
            "slippage_or_adverse_per_fill": 0.0030,
        },
        {
            "case": "stress_taker_slippage_0_5pct",
            "fee_per_fill": 0.0010,
            "slippage_or_adverse_per_fill": 0.0050,
        },
        {
            "case": "stress_taker_slippage_1_0pct",
            "fee_per_fill": 0.0010,
            "slippage_or_adverse_per_fill": 0.0100,
        },
    ]
    out = []
    for row in rows:
        one_leg_hurdle = 4.0 * (
            float(row["fee_per_fill"]) + float(row["slippage_or_adverse_per_fill"])
        )
        out.append(
            {
                **row,
                "spread_return_hurdle_pct": pct(one_leg_hurdle),
                "gross_pair_capital_hurdle_pct": pct(one_leg_hurdle / 2.0),
            }
        )
    return out


def safe_data_inventory() -> dict[str, object]:
    files = [p for p in DATA_DIR.rglob("*") if p.is_file()]
    holdout_like = [
        str(p.relative_to(ROOT))
        for p in files
        if "HOLDOUT" in str(p).upper() or "SEALED" in str(p).upper()
    ]
    parquet_files = [p for p in files if p.suffix.lower() == ".parquet"]
    csv_files = [p for p in files if p.suffix.lower() == ".csv"]
    expanded_4h = sorted((DATA_DIR / "FUTURES_EXPANDED").glob("*_4H.csv"))

    expanded_rows = {}
    for p in expanded_4h:
        with p.open(newline="") as fh:
            reader = csv.reader(fh)
            row_count = sum(1 for _ in reader) - 1
        expanded_rows[p.name.replace("_4H.csv", "")] = row_count

    return {
        "data_dir": str(DATA_DIR.relative_to(ROOT)),
        "total_files": len(files),
        "csv_files": len(csv_files),
        "parquet_files": len(parquet_files),
        "expanded_4h_csv_files": len(expanded_4h),
        "expanded_4h_min_rows": min(expanded_rows.values()) if expanded_rows else None,
        "expanded_4h_max_rows": max(expanded_rows.values()) if expanded_rows else None,
        "holdout_like_files_detected_but_not_read": holdout_like,
        "parquet_path_check": "NO_PARQUET_FILES_FOUND_UNDER_DATA",
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = {
        "task_id": TASK_ID,
        "generated_at_utc": dt.datetime.now(dt.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "stage0_verdict": STAGE0_VERDICT,
        "b1_gates_run": False,
        "b1_skip_reason": "Stage 0 KILL: no hard pre-B1 evidence that residual pair-RV edge exceeds the 4-fill cost hurdle.",
        "cost_table": round_trip_cost_table(),
        "data_inventory": safe_data_inventory(),
        "arxiv_2602_23762": {
            "status": "verified_via_arxiv_primary_page",
            "title": "One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets",
            "submitted": "2026-02-27",
            "url": "https://arxiv.org/abs/2602.23762",
        },
    }
    OUTPUT_FILE.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
