#!/usr/bin/env python3
"""P0-RES-038-B1 Phase A free-data audit and descriptive statistics.

This script is intentionally descriptive only:
- no backtest;
- no holdout reads;
- no fitted thresholds or full-sample quantile triggers;
- fixed OI reset bins are used only to summarize gross drift magnitudes.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
LIQ_DIR = ROOT / "06_RESEARCH" / "DATA" / "LIQUIDATIONS"
FUT_EXP_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED"
FUT_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
OUT_PATH = OUT_DIR / "p0res038_phasea_free_data_audit.json"

COST_GATES_BP = {"low": 70, "medium": 110, "cascade_high": 210}
OI_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
OI_DROP_BINS = [
    ("drop_2_to_5pct", -0.05, -0.02),
    ("drop_5_to_10pct", -0.10, -0.05),
    ("drop_ge_10pct", -np.inf, -0.10),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def quantiles_bp(values: pd.Series | np.ndarray) -> dict[str, float | None]:
    s = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        return {k: None for k in ("min", "p10", "p25", "p50", "p75", "p90", "p95", "max")}
    qs = s.quantile([0.10, 0.25, 0.50, 0.75, 0.90, 0.95])
    return {
        "min": round(float(s.min()), 4),
        "p10": round(float(qs.loc[0.10]), 4),
        "p25": round(float(qs.loc[0.25]), 4),
        "p50": round(float(qs.loc[0.50]), 4),
        "p75": round(float(qs.loc[0.75]), 4),
        "p90": round(float(qs.loc[0.90]), 4),
        "p95": round(float(qs.loc[0.95]), 4),
        "max": round(float(s.max()), 4),
    }


def read_liquidations() -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    file_rows: dict[str, int] = {}
    top_keys: Counter[str] = Counter()
    order_keys: Counter[str] = Counter()
    bad_rows = 0

    for path in sorted(LIQ_DIR.glob("*.jsonl")):
        n = 0
        with path.open() as handle:
            for line in handle:
                n += 1
                try:
                    payload = json.loads(line)
                    order = payload.get("o", {})
                    top_keys.update(payload.keys())
                    order_keys.update(order.keys())
                    qty = pd.to_numeric(order.get("z") or order.get("q"), errors="coerce")
                    avg_price = pd.to_numeric(order.get("ap") or order.get("p"), errors="coerce")
                    rows.append(
                        {
                            "file": path.name,
                            "event_time": pd.to_datetime(order.get("T") or payload.get("E"), unit="ms", utc=True),
                            "recv_time": pd.to_datetime(payload.get("recv_ts"), unit="ms", utc=True),
                            "symbol": order.get("s"),
                            "side": order.get("S"),
                            "order_type": order.get("o"),
                            "time_in_force": order.get("f"),
                            "status": order.get("X"),
                            "qty": float(qty) if pd.notna(qty) else np.nan,
                            "avg_price": float(avg_price) if pd.notna(avg_price) else np.nan,
                            "notional_usdt": float(abs(qty * avg_price)) if pd.notna(qty) and pd.notna(avg_price) else np.nan,
                        }
                    )
                except Exception:
                    bad_rows += 1
        file_rows[path.name] = n

    df = pd.DataFrame(rows)
    if not df.empty:
        df["date_utc"] = df["event_time"].dt.strftime("%Y-%m-%d")
        df["hour_utc"] = df["event_time"].dt.floor("h")
        df["bar_4h"] = df["event_time"].dt.floor("4h")

    audit = {
        "path": rel(LIQ_DIR),
        "files": file_rows,
        "rows": int(sum(file_rows.values())),
        "parsed_rows": int(len(df)),
        "bad_rows": int(bad_rows),
        "first_event_utc": None if df.empty else df["event_time"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_event_utc": None if df.empty else df["event_time"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unique_symbols": 0 if df.empty else int(df["symbol"].nunique()),
        "top_level_keys": sorted(top_keys.keys()),
        "order_keys": sorted(order_keys.keys()),
        "side_counts": {} if df.empty else {str(k): int(v) for k, v in df["side"].value_counts().to_dict().items()},
        "status_counts": {} if df.empty else {str(k): int(v) for k, v in df["status"].value_counts().to_dict().items()},
        "order_type_counts": {} if df.empty else {str(k): int(v) for k, v in df["order_type"].value_counts().to_dict().items()},
        "time_in_force_counts": {} if df.empty else {str(k): int(v) for k, v in df["time_in_force"].value_counts().to_dict().items()},
        "notional_usdt_quantiles": {} if df.empty else quantiles_bp(df["notional_usdt"]),
        "known_truncation": "Binance !forceOrder@arr pushes only the largest liquidation order per symbol per 1000 ms; local rows are a lower-bound sample, not full liquidation volume.",
    }
    return df, audit


def audit_futures_expanded() -> dict[str, Any]:
    files = sorted(FUT_EXP_DIR.glob("*_4H.csv"))
    per_file = {}
    all_columns: Counter[str] = Counter()
    total_rows = 0
    starts: list[pd.Timestamp] = []
    ends: list[pd.Timestamp] = []

    for path in files:
        df = pd.read_csv(path)
        cols = df.columns.tolist()
        all_columns.update(cols)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        intervals = df["datetime"].diff().dropna()
        expected = int(((df["datetime"].max() - df["datetime"].min()) / pd.Timedelta(hours=4)) + 1)
        gaps = int((intervals > pd.Timedelta(hours=4)).sum())
        per_file[path.name] = {
            "rows": int(len(df)),
            "columns": cols,
            "first_utc": df["datetime"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_utc": df["datetime"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "expected_4h_grid_rows": expected,
            "missing_or_duplicate_grid_rows": int(expected - len(df)),
            "gaps_over_4h": gaps,
        }
        total_rows += len(df)
        starts.append(df["datetime"].min())
        ends.append(df["datetime"].max())

    return {
        "path": rel(FUT_EXP_DIR),
        "csv_files": len(files),
        "total_rows": int(total_rows),
        "global_first_utc": min(starts).strftime("%Y-%m-%dT%H:%M:%SZ") if starts else None,
        "global_last_utc": max(ends).strftime("%Y-%m-%dT%H:%M:%SZ") if ends else None,
        "columns_seen": sorted(all_columns.keys()),
        "has_oi_field": any("open_interest" in c.lower() or c.lower() == "oi" for c in all_columns),
        "has_funding_field": any("funding" in c.lower() for c in all_columns),
        "sample_files": dict(list(per_file.items())[:5]),
        "per_file": per_file,
    }


def audit_local_oi_auxiliary() -> dict[str, Any]:
    symbols = {}
    for symbol in OI_SYMBOLS:
        metrics_path = FUT_DIR / f"{symbol}_METRICS_5M.csv"
        mark_paths = sorted(FUT_DIR.glob(f"{symbol}_MARK_4H*.csv"))
        metrics = pd.read_csv(metrics_path, usecols=["create_time", "sum_open_interest", "sum_open_interest_value"])
        metrics["create_time"] = pd.to_datetime(metrics["create_time"], utc=True)
        symbols[symbol] = {
            "metrics_path": rel(metrics_path),
            "metrics_rows": int(len(metrics)),
            "metrics_first_utc": metrics["create_time"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "metrics_last_utc": metrics["create_time"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "metrics_columns_used": ["create_time", "sum_open_interest", "sum_open_interest_value"],
            "mark_4h_paths": [rel(p) for p in mark_paths],
        }
    return {
        "path": rel(FUT_DIR),
        "note": "Local auxiliary source for OI reset; FUTURES_EXPANDED itself has OHLCV only.",
        "symbols": symbols,
    }


def liquidation_cluster_descriptive(liq: pd.DataFrame, fut_exp_audit: dict[str, Any]) -> dict[str, Any]:
    if liq.empty:
        return {"status": "no_liquidation_rows"}

    clusters = (
        liq.groupby(["symbol", "side", "bar_4h"], dropna=False)
        .agg(rows=("notional_usdt", "size"), notional_usdt=("notional_usdt", "sum"))
        .reset_index()
    )
    clusters["size_bucket"] = pd.cut(
        clusters["notional_usdt"],
        bins=[-np.inf, 1_000, 10_000, 100_000, 1_000_000, np.inf],
        labels=["lt_1k", "1k_10k", "10k_100k", "100k_1m", "ge_1m"],
    )

    fut_last = pd.to_datetime(fut_exp_audit["global_last_utc"])
    fut_first = pd.to_datetime(fut_exp_audit["global_first_utc"])
    overlap = clusters[(clusters["bar_4h"] >= fut_first) & (clusters["bar_4h"] <= fut_last)]

    return {
        "rows": int(len(clusters)),
        "first_cluster_utc": clusters["bar_4h"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_cluster_utc": clusters["bar_4h"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notional_usdt_quantiles_by_4h_symbol_side": quantiles_bp(clusters["notional_usdt"]),
        "bucket_counts": {str(k): int(v) for k, v in clusters["size_bucket"].value_counts().sort_index().to_dict().items()},
        "top_10_symbols_by_notional": {
            str(k): round(float(v), 2)
            for k, v in clusters.groupby("symbol")["notional_usdt"].sum().sort_values(ascending=False).head(10).to_dict().items()
        },
        "futures_expanded_overlap_clusters": int(len(overlap)),
        "gross_drift_status": "UNAVAILABLE: LIQUIDATIONS are 2026-06-15..2026-06-21; FUTURES_EXPANDED ends 2024-12-09, so no legal local join for 1-4x4H drift.",
    }


def read_mark_4h(symbol: str) -> pd.DataFrame:
    frames = []
    for path in sorted(FUT_DIR.glob(f"{symbol}_MARK_4H*.csv")):
        df = pd.read_csv(path, usecols=["datetime", "close"])
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        frames.append(df)
    out = pd.concat(frames, ignore_index=True).drop_duplicates("datetime").sort_values("datetime")
    return out.rename(columns={"datetime": "ts", "close": "close"})


def read_oi_4h(symbol: str) -> pd.DataFrame:
    path = FUT_DIR / f"{symbol}_METRICS_5M.csv"
    df = pd.read_csv(path, usecols=["create_time", "sum_open_interest"])
    df["create_time"] = pd.to_datetime(df["create_time"], utc=True)
    df["sum_open_interest"] = pd.to_numeric(df["sum_open_interest"], errors="coerce")
    hourly = (
        df.sort_values("create_time")
        .set_index("create_time")["sum_open_interest"]
        .resample("4h")
        .last()
        .rename("oi")
        .reset_index()
        .rename(columns={"create_time": "ts"})
    )
    return hourly


def classify_oi_drop(value: float) -> str | None:
    for label, low, high in OI_DROP_BINS:
        if value <= high and value > low:
            return label
    return None


def oi_reset_descriptive() -> dict[str, Any]:
    event_frames = []
    symbol_audit = {}
    for symbol in OI_SYMBOLS:
        oi = read_oi_4h(symbol)
        mark = read_mark_4h(symbol)
        df = oi.merge(mark, on="ts", how="inner").sort_values("ts").reset_index(drop=True)
        df["oi_change_24h"] = df["oi"].pct_change(6, fill_method=None)
        df["past_price_logret_24h"] = np.log(df["close"] / df["close"].shift(6))
        for k in range(1, 5):
            df[f"fwd_logret_{k}x4h"] = np.log(df["close"].shift(-k) / df["close"])
        df["drop_bucket"] = df["oi_change_24h"].apply(lambda x: classify_oi_drop(float(x)) if pd.notna(x) else None)
        events = df[df["drop_bucket"].notna()].copy()
        events["symbol"] = symbol
        events["event_sign_from_prior_24h_price"] = np.sign(events["past_price_logret_24h"])
        events = events[events["event_sign_from_prior_24h_price"] != 0]
        event_frames.append(events)
        symbol_audit[symbol] = {
            "joined_4h_rows": int(len(df)),
            "first_utc": df["ts"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_utc": df["ts"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "oi_drop_events_fixed_bins": int(len(events)),
        }

    events_all = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()
    if events_all.empty:
        return {"symbol_audit": symbol_audit, "status": "no_fixed_bin_oi_drop_events"}

    by_bucket: dict[str, Any] = {}
    for bucket in [label for label, _, _ in OI_DROP_BINS]:
        sub = events_all[events_all["drop_bucket"] == bucket].copy()
        bucket_payload: dict[str, Any] = {"events": int(len(sub))}
        if sub.empty:
            by_bucket[bucket] = bucket_payload
            continue
        bucket_payload["oi_change_24h_bp"] = quantiles_bp(sub["oi_change_24h"] * 10_000)
        bucket_payload["past_price_logret_24h_bp"] = quantiles_bp(sub["past_price_logret_24h"] * 10_000)
        windows = {}
        for k in range(1, 5):
            raw_bp = sub[f"fwd_logret_{k}x4h"] * 10_000
            continuation_bp = sub["event_sign_from_prior_24h_price"] * raw_bp
            exhaustion_bp = -continuation_bp
            abs_bp = raw_bp.abs()
            windows[f"{k}x4h"] = {
                "valid_events": int(raw_bp.notna().sum()),
                "raw_forward_logret_bp": quantiles_bp(raw_bp),
                "continuation_bp": quantiles_bp(continuation_bp),
                "exhaustion_bp": quantiles_bp(exhaustion_bp),
                "absolute_gross_drift_bp": quantiles_bp(abs_bp),
            }
        bucket_payload["windows"] = windows
        by_bucket[bucket] = bucket_payload

    monotonic_probe = {}
    for k in range(1, 5):
        p90s = [
            by_bucket[bucket].get("windows", {}).get(f"{k}x4h", {}).get("absolute_gross_drift_bp", {}).get("p90")
            for bucket, _, _ in OI_DROP_BINS
        ]
        monotonic_probe[f"{k}x4h_abs_p90_non_decreasing_by_drop_severity"] = (
            None if any(v is None for v in p90s) else bool(all(p90s[i] <= p90s[i + 1] for i in range(len(p90s) - 1)))
        )
        monotonic_probe[f"{k}x4h_abs_p90_values_bp"] = p90s

    max_upper = None
    for bucket_payload in by_bucket.values():
        for window_payload in bucket_payload.get("windows", {}).values():
            p95 = window_payload["absolute_gross_drift_bp"]["p95"]
            if p95 is not None:
                max_upper = p95 if max_upper is None else max(max_upper, p95)

    return {
        "definition": "OI reset event = fixed 24h OI drop bins on 4H-resampled Binance metrics; direction sign = prior 24h price log-return sign. Continuation and exhaustion are both reported; neither is selected.",
        "symbol_audit": symbol_audit,
        "total_fixed_bin_events": int(len(events_all)),
        "events_by_symbol": {str(k): int(v) for k, v in events_all["symbol"].value_counts().to_dict().items()},
        "events_by_bucket": {str(k): int(v) for k, v in events_all["drop_bucket"].value_counts().reindex([label for label, _, _ in OI_DROP_BINS], fill_value=0).to_dict().items()},
        "by_bucket": by_bucket,
        "monotonic_probe": monotonic_probe,
        "max_observed_abs_gross_drift_p95_bp_across_bins_windows": max_upper,
        "cost_gates_bp": COST_GATES_BP,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    liq, liq_audit = read_liquidations()
    fut_exp_audit = audit_futures_expanded()
    payload = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task_id": "P0-RES-038-B1-PHASEA",
        "cost_gates_bp": COST_GATES_BP,
        "liquidations_audit": liq_audit,
        "futures_expanded_audit": fut_exp_audit,
        "local_oi_auxiliary_audit": audit_local_oi_auxiliary(),
        "liquidation_cluster_descriptive": liquidation_cluster_descriptive(liq, fut_exp_audit),
        "oi_reset_descriptive": oi_reset_descriptive(),
        "holdout_read_statement": "No HOLDOUT path is read by this script.",
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(json.dumps({"output": rel(OUT_PATH), "generated_at_utc": payload["generated_at_utc"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
