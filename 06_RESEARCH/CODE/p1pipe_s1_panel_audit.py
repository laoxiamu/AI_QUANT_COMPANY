#!/usr/bin/env python3
"""
P1-RES-039-PIPELINE Step 1: FUTURES_EXPANDED_2026 panel integrity audit.

Reads only local price panels. Emits JSON for the step report.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OLD_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED"
NEW_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED_2026"
OUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
OUT_PATH = OUT_DIR / "p1pipe_s1_panel_audit.json"
EXPECTED_STEP = pd.Timedelta(hours=4)
TARGET_MONTH = pd.Period("2026-06", freq="M")
POST_2025_START = pd.Timestamp("2025-01-01 00:00:00")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def symbol_from_path(path: Path) -> str:
    return path.name.replace("USDT_4H.csv", "")


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["datetime"])
    required = ["datetime", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    return df.sort_values("datetime").reset_index(drop=True)


def gap_summary(df: pd.DataFrame) -> dict[str, Any]:
    diffs = df["datetime"].diff().dropna()
    bad = diffs[diffs != EXPECTED_STEP]
    duplicate_count = int(df["datetime"].duplicated().sum())
    examples = []
    if not bad.empty:
        for idx, delta in bad.head(10).items():
            examples.append(
                {
                    "prev": df.loc[idx - 1, "datetime"].isoformat(),
                    "current": df.loc[idx, "datetime"].isoformat(),
                    "delta_hours": delta.total_seconds() / 3600.0,
                }
            )
    return {
        "duplicate_timestamps": duplicate_count,
        "non_4h_gap_count": int(len(bad)),
        "non_4h_gap_examples": examples,
    }


def audit_symbol(symbol: str, old_path: Path | None, new_path: Path) -> dict[str, Any]:
    new_df = load_csv(new_path)
    item: dict[str, Any] = {
        "symbol": symbol,
        "new_file": str(new_path.relative_to(ROOT)),
        "new_rows": int(len(new_df)),
        "new_start": new_df["datetime"].iloc[0].isoformat(),
        "new_end": new_df["datetime"].iloc[-1].isoformat(),
        "new_reaches_2026_06": pd.Period(new_df["datetime"].iloc[-1], freq="M") >= TARGET_MONTH,
        "new_integrity": gap_summary(new_df),
        "new_integrity_from_2025": gap_summary(new_df[new_df["datetime"] >= POST_2025_START].reset_index(drop=True)),
        "old_file": str(old_path.relative_to(ROOT)) if old_path else None,
        "old_rows": None,
        "old_start": None,
        "old_end": None,
        "seam_status": "no_old_symbol",
        "old_last_bar_present_in_new": None,
        "new_next_bar_after_old_end": None,
        "seam_gap_hours": None,
        "overlap_duplicate_count_if_naively_concat": None,
        "old_values_match_new_at_old_end": None,
    }

    if old_path is None:
        return item

    old_df = load_csv(old_path)
    old_end = old_df["datetime"].iloc[-1]
    item["old_rows"] = int(len(old_df))
    item["old_start"] = old_df["datetime"].iloc[0].isoformat()
    item["old_end"] = old_end.isoformat()

    old_last_mask = new_df["datetime"] == old_end
    item["old_last_bar_present_in_new"] = bool(old_last_mask.any())
    item["overlap_duplicate_count_if_naively_concat"] = int(
        pd.Index(old_df["datetime"]).intersection(pd.Index(new_df["datetime"])).size
    )

    if old_last_mask.any():
        new_idx = int(new_df.index[old_last_mask][0])
        if new_idx + 1 < len(new_df):
            next_time = new_df.loc[new_idx + 1, "datetime"]
            item["new_next_bar_after_old_end"] = next_time.isoformat()
            item["seam_gap_hours"] = (next_time - old_end).total_seconds() / 3600.0
        old_last = old_df.iloc[-1]
        new_last = new_df.loc[new_idx]
        item["old_values_match_new_at_old_end"] = all(
            float(old_last[col]) == float(new_last[col]) for col in ["open", "high", "low", "close", "volume"]
        )
        if item["seam_gap_hours"] == 4.0:
            item["seam_status"] = "continuous_by_new_panel"
        else:
            item["seam_status"] = "old_end_present_but_next_bar_not_4h"
    else:
        future = new_df[new_df["datetime"] > old_end]
        if not future.empty:
            first_after = future.iloc[0]["datetime"]
            item["new_next_bar_after_old_end"] = first_after.isoformat()
            item["seam_gap_hours"] = (first_after - old_end).total_seconds() / 3600.0
        item["seam_status"] = "old_end_missing_from_new"

    return item


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    old_files = {symbol_from_path(p): p for p in OLD_DIR.glob("*USDT_4H.csv")}
    new_files = {symbol_from_path(p): p for p in NEW_DIR.glob("*USDT_4H.csv")}

    symbols = sorted(new_files)
    assets = [audit_symbol(symbol, old_files.get(symbol), new_files[symbol]) for symbol in symbols]
    missing_from_new = sorted(set(old_files) - set(new_files))
    new_only = sorted(set(new_files) - set(old_files))
    strict_usable = [
        a["symbol"]
        for a in assets
        if a["new_reaches_2026_06"]
        and a["new_integrity"]["duplicate_timestamps"] == 0
        and a["new_integrity"]["non_4h_gap_count"] == 0
    ]
    post_2025_usable = [
        a["symbol"]
        for a in assets
        if a["new_reaches_2026_06"]
        and a["new_integrity_from_2025"]["duplicate_timestamps"] == 0
        and a["new_integrity_from_2025"]["non_4h_gap_count"] == 0
    ]

    output = {
        "task_id": "P1-RES-039-PIPELINE-S1",
        "generated_at": utc_now_iso(),
        "discipline": {
            "holdout_touched": False,
            "backtest_performed": False,
            "parameter_tuning_performed": False,
            "data_reads": [
                "06_RESEARCH/DATA/FUTURES_EXPANDED",
                "06_RESEARCH/DATA/FUTURES_EXPANDED_2026",
            ],
        },
        "old_panel_symbol_count": len(old_files),
        "new_panel_symbol_count": len(new_files),
        "missing_old_symbols_from_new_panel": missing_from_new,
        "new_only_symbols": new_only,
        "strict_full_panel_usable_universe": strict_usable,
        "strict_full_panel_usable_universe_count": len(strict_usable),
        "post_2025_event_eligible_universe": post_2025_usable,
        "post_2025_event_eligible_universe_count": len(post_2025_usable),
        "assets": assets,
        "summary": {
            "all_new_assets_reach_2026_06": all(a["new_reaches_2026_06"] for a in assets),
            "assets_with_duplicate_timestamps": [
                a["symbol"] for a in assets if a["new_integrity"]["duplicate_timestamps"] > 0
            ],
            "assets_with_non_4h_gaps": [
                a["symbol"] for a in assets if a["new_integrity"]["non_4h_gap_count"] > 0
            ],
            "assets_with_non_4h_gaps_from_2025": [
                a["symbol"] for a in assets if a["new_integrity_from_2025"]["non_4h_gap_count"] > 0
            ],
            "assets_with_continuous_old_new_seam": [
                a["symbol"] for a in assets if a["seam_status"] == "continuous_by_new_panel"
            ],
            "assets_with_noncontinuous_old_new_seam": [
                a["symbol"]
                for a in assets
                if a["old_file"] is not None and a["seam_status"] != "continuous_by_new_panel"
            ],
        },
    }
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_PATH)


if __name__ == "__main__":
    main()
