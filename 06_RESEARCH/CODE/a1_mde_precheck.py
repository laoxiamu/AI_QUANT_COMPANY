#!/usr/bin/env python3
"""A-1 OI-drop MDE precheck.

This script intentionally computes only event counts and unconditional MARK
return variances. It does not compute event-conditioned or post-event returns.
"""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")

CUTOFF_EXCLUSIVE = pd.Timestamp("2024-12-10T00:00:00Z")
OI_PCTL_THRESHOLD = 0.01
MERGE_WINDOW = pd.Timedelta(hours=24)
HORIZONS = (24, 48, 72)
ALPHA_ONE_SIDED = 0.05
MECHANISM_EFFECT_BOUNDS = (0.015, 0.03)


def parse_feature_ts(raw: str) -> pd.Timestamp:
    return pd.Timestamp(raw)


def parse_mark_ts(raw: str) -> pd.Timestamp:
    return pd.Timestamp(datetime.fromisoformat(raw).replace(tzinfo=timezone.utc))


def iter_rows_before_cutoff(path: Path, time_col: str, parser):
    """Yield CSV rows before the research cutoff, assuming ascending time."""
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ts = parser(row[time_col])
            if ts >= CUTOFF_EXCLUSIVE:
                break
            yield ts, row


def bool_from_csv(raw: str) -> bool:
    return str(raw).strip().lower() == "true"


def extract_oi_drop_episode_count(symbol: str) -> dict[str, int | str]:
    """Count rolling-P1 6h OI-drop episodes after warmup, merged within 24h."""
    path = OUTPUT_DIR / f"a1_oi_features_{symbol}.csv"
    trigger_count = 0
    episode_count = 0
    last_trigger_ts: pd.Timestamp | None = None

    for ts, row in iter_rows_before_cutoff(path, "ts", parse_feature_ts):
        if bool_from_csv(row["warmup"]):
            continue
        raw_pctl = row["d6h_rolling_pctl"]
        if raw_pctl == "":
            continue
        if float(raw_pctl) > OI_PCTL_THRESHOLD:
            continue

        trigger_count += 1
        if last_trigger_ts is None or ts - last_trigger_ts > MERGE_WINDOW:
            episode_count += 1
        last_trigger_ts = ts

    return {
        "symbol": symbol,
        "p1_trigger_rows": trigger_count,
        "episodes_merged_24h": episode_count,
    }


def load_mark_closes(symbol: str) -> pd.Series:
    """Load pre-cutoff MARK closes only."""
    path = DATA_DIR / f"{symbol}_MARK_1H.csv"
    rows: list[tuple[pd.Timestamp, float]] = []
    for ts, row in iter_rows_before_cutoff(path, "datetime", parse_mark_ts):
        close_raw = row["close"]
        if close_raw == "":
            continue
        close = float(close_raw)
        if close > 0:
            rows.append((ts, close))

    if not rows:
        return pd.Series(dtype=float)

    series = pd.Series(
        [close for _, close in rows],
        index=pd.DatetimeIndex([ts for ts, _ in rows], tz="UTC"),
        name=symbol,
        dtype=float,
    )
    return series[~series.index.duplicated(keep="last")].sort_index()


def unconditional_log_returns(symbol: str, closes: pd.Series, horizon_hours: int) -> pd.Series:
    """Compute unconditional h-hour log returns with both endpoints pre-cutoff."""
    horizon = pd.Timedelta(hours=horizon_hours)
    close_by_time = closes.to_dict()
    returns: list[tuple[pd.Timestamp, float]] = []

    for ts, close in closes.items():
        end_ts = ts + horizon
        if end_ts >= CUTOFF_EXCLUSIVE:
            continue
        future_close = close_by_time.get(end_ts)
        if future_close is None:
            continue
        returns.append((ts, math.log(float(future_close)) - math.log(float(close))))

    if not returns:
        return pd.Series(dtype=float, name=f"{symbol}_{horizon_hours}h")

    return pd.Series(
        [value for _, value in returns],
        index=pd.DatetimeIndex([ts for ts, _ in returns], tz="UTC"),
        name=f"{symbol}_{horizon_hours}h",
        dtype=float,
    )


def sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def compute_variance_rows() -> list[dict[str, float | int | str]]:
    closes_by_symbol = {symbol: load_mark_closes(symbol) for symbol in SYMBOLS}
    rows: list[dict[str, float | int | str]] = []

    for horizon in HORIZONS:
        pooled: list[float] = []
        by_symbol_counts: dict[str, int] = {}
        for symbol, closes in closes_by_symbol.items():
            returns = unconditional_log_returns(symbol, closes, horizon)
            by_symbol_counts[symbol] = int(len(returns))
            pooled.extend(float(value) for value in returns)

        variance = sample_variance(pooled)
        rows.append(
            {
                "horizon_hours": horizon,
                "return_obs": len(pooled),
                "variance": variance,
                "stdev": math.sqrt(variance),
                "btc_obs": by_symbol_counts["BTCUSDT"],
                "eth_obs": by_symbol_counts["ETHUSDT"],
                "sol_obs": by_symbol_counts["SOLUSDT"],
            }
        )

    return rows


def split_work_holdout_count(total_events: int) -> tuple[int, int]:
    holdout = total_events // 5
    return total_events - holdout, holdout


def compute_mde(stdev: float, usable_n: int) -> float:
    """One-sided alpha-only detectable mean threshold: z_(1-alpha)*sigma/sqrt(n)."""
    z_alpha = NormalDist().inv_cdf(1.0 - ALPHA_ONE_SIDED)
    return z_alpha * stdev / math.sqrt(usable_n)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    count_rows = [extract_oi_drop_episode_count(symbol) for symbol in SYMBOLS]
    total_episodes = int(sum(int(row["episodes_merged_24h"]) for row in count_rows))
    usable_n, holdout_n = split_work_holdout_count(total_episodes)

    variance_rows = compute_variance_rows()
    mde_rows: list[dict[str, float | int | str]] = []
    for row in variance_rows:
        mde = compute_mde(float(row["stdev"]), usable_n)
        mde_rows.append(
            {
                "horizon_hours": int(row["horizon_hours"]),
                "usable_n_after_holdout": usable_n,
                "alpha_one_sided": ALPHA_ONE_SIDED,
                "z_1_minus_alpha": NormalDist().inv_cdf(1.0 - ALPHA_ONE_SIDED),
                "stdev_unconditional_log_return": float(row["stdev"]),
                "mde_log_return": mde,
                "mde_pct": mde * 100.0,
                "mechanism_lower_pct": MECHANISM_EFFECT_BOUNDS[0] * 100.0,
                "mechanism_upper_pct": MECHANISM_EFFECT_BOUNDS[1] * 100.0,
                "passes_power_gate_precheck": bool(mde <= MECHANISM_EFFECT_BOUNDS[1]),
            }
        )

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": "BATCH_20260612N/B4",
        "cutoff_exclusive_utc": CUTOFF_EXCLUSIVE.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbols": list(SYMBOLS),
        "oi_trigger": {
            "feature": "d6h_rolling_pctl",
            "threshold": OI_PCTL_THRESHOLD,
            "warmup_excluded": True,
            "merge_window_hours": int(MERGE_WINDOW / pd.Timedelta(hours=1)),
        },
        "holdout_presplit": {
            "rule": "pooled chronological event ordinals with ordinal mod 5 == 4 held out; count-only precheck does not write or read holdout files",
            "total_episodes": total_episodes,
            "holdout_n": holdout_n,
            "usable_n": usable_n,
        },
        "mde_formula": "MDE_h = z_(1-alpha) * sqrt(Var[r_h]) / sqrt(n_work), alpha=0.05 one-sided",
        "count_rows": count_rows,
        "variance_rows": variance_rows,
        "mde_rows": mde_rows,
        "overall_power_gate_precheck": all(bool(row["passes_power_gate_precheck"]) for row in mde_rows),
    }

    counts_path = OUTPUT_DIR / "a1_mde_precheck_counts.csv"
    variance_path = OUTPUT_DIR / "a1_mde_precheck_unconditional_variance.csv"
    mde_path = OUTPUT_DIR / "a1_mde_precheck_mde.csv"
    summary_path = OUTPUT_DIR / "a1_mde_precheck_summary.json"

    pd.DataFrame(count_rows).to_csv(counts_path, index=False)
    pd.DataFrame(variance_rows).to_csv(variance_path, index=False)
    pd.DataFrame(mde_rows).to_csv(mde_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
