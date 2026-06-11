#!/usr/bin/env python3
"""Build A-2 funding extreme event tables with no lookahead."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
HOLDOUT_DIR = ROOT / "06_RESEARCH" / "DATA" / "HOLDOUT"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
FUNDING_COLUMN = "last_funding_rate"
WINDOW_DAYS = 365
MIN_HISTORY_DAYS = 180
MERGE_WINDOW = pd.Timedelta(hours=24)

NEGATIVE_TIERS = (("P5", 0.05), ("P2.5", 0.025), ("P1", 0.01))
POSITIVE_TIERS = (("P95", 0.95), ("P97.5", 0.975), ("P99", 0.99))
OUTPUT_COLUMNS = [
    "event_time",
    "symbol",
    "side",
    "tier",
    "funding_value",
    "rolling_pctl",
]


def empirical_percentile(prior_values: pd.Series, value: float) -> float:
    """Midrank percentile of value against prior observations only."""
    lower = (prior_values < value).sum()
    equal = (prior_values == value).sum()
    return float((lower + 0.5 * equal) / len(prior_values))


def add_rolling_percentiles(
    funding: pd.DataFrame,
    *,
    time_col: str = "datetime",
    value_col: str = FUNDING_COLUMN,
) -> pd.DataFrame:
    """Add no-lookahead rolling percentiles and warmup flags.

    The percentile for row t uses observations with timestamps in
    [t - 365 days, t). During the first year this is an expanding window,
    but rows with less than 180 calendar days of prior history are warmup.
    """
    df = funding.sort_values(time_col).reset_index(drop=True).copy()
    times = pd.to_datetime(df[time_col], utc=True)
    values = df[value_col].astype(float)
    percentiles: list[float | None] = []
    warmup: list[bool] = []

    left = 0
    for idx, current_time in enumerate(times):
        cutoff = current_time - pd.Timedelta(days=WINDOW_DAYS)
        while left < idx and times.iloc[left] < cutoff:
            left += 1

        prior_times = times.iloc[left:idx]
        prior_values = values.iloc[left:idx]
        has_min_history = (
            len(prior_times) > 0
            and prior_times.iloc[0] <= current_time - pd.Timedelta(days=MIN_HISTORY_DAYS)
        )
        is_warmup = not has_min_history
        warmup.append(is_warmup)
        if is_warmup:
            percentiles.append(None)
        else:
            percentiles.append(empirical_percentile(prior_values, values.iloc[idx]))

    df["event_time"] = times.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df["rolling_pctl"] = percentiles
    df["warmup"] = warmup
    return df


def merge_extreme_readings(readings: pd.DataFrame) -> pd.DataFrame:
    """Collapse same-symbol/same-side/same-tier readings within 24h."""
    if readings.empty:
        return readings.loc[:, OUTPUT_COLUMNS].copy()

    rows = readings.sort_values("event_time_dt").to_dict("records")
    events: list[dict[str, object]] = []
    last_reading_time: pd.Timestamp | None = None
    for row in rows:
        reading_time = row["event_time_dt"]
        if last_reading_time is not None and reading_time - last_reading_time <= MERGE_WINDOW:
            last_reading_time = reading_time
            continue
        events.append(row)
        last_reading_time = reading_time

    return pd.DataFrame(events).loc[:, OUTPUT_COLUMNS]


def extract_symbol_events(symbol: str, funding: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    featured = add_rolling_percentiles(funding)
    featured["symbol"] = symbol
    featured["funding_value"] = featured[FUNDING_COLUMN].astype(float)
    featured["event_time_dt"] = pd.to_datetime(featured["event_time"], utc=True)
    usable = featured.loc[~featured["warmup"]].copy()
    warmup_excluded = int(featured["warmup"].sum())

    event_frames: list[pd.DataFrame] = []
    for tier, threshold in NEGATIVE_TIERS:
        mask = usable["rolling_pctl"] <= threshold
        readings = usable.loc[mask].copy()
        readings["side"] = "neg"
        readings["tier"] = tier
        event_frames.append(merge_extreme_readings(readings))

    for tier, threshold in POSITIVE_TIERS:
        mask = usable["rolling_pctl"] >= threshold
        readings = usable.loc[mask].copy()
        readings["side"] = "pos"
        readings["tier"] = tier
        event_frames.append(merge_extreme_readings(readings))

    events = pd.concat(event_frames, ignore_index=True)
    return events, warmup_excluded


def build_events(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, dict[str, int]]:
    frames: list[pd.DataFrame] = []
    warmup_by_symbol: dict[str, int] = {}
    for symbol in SYMBOLS:
        path = data_dir / f"{symbol}_FUNDING_8H.csv"
        funding = pd.read_csv(path, parse_dates=["datetime"])
        events, warmup_count = extract_symbol_events(symbol, funding)
        frames.append(events)
        warmup_by_symbol[symbol] = warmup_count

    all_events = pd.concat(frames, ignore_index=True)
    all_events = all_events.sort_values(
        ["event_time", "symbol", "side", "tier"],
        kind="mergesort",
    ).reset_index(drop=True)
    return all_events.loc[:, OUTPUT_COLUMNS], warmup_by_symbol


def split_work_holdout(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordinals = pd.Series(range(len(events)), index=events.index)
    holdout_mask = ordinals.mod(5) == 4
    holdout = events.loc[holdout_mask].reset_index(drop=True)
    work = events.loc[~holdout_mask].reset_index(drop=True)
    return work, holdout


def tier_counts(events: pd.DataFrame) -> dict[str, int]:
    if events.empty:
        return {}
    counts = (
        events.groupby(["side", "tier"], sort=True)
        .size()
        .rename("events")
        .reset_index()
    )
    return {
        f"{row.side}_{row.tier}": int(row.events)
        for row in counts.itertuples(index=False)
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HOLDOUT_DIR.mkdir(parents=True, exist_ok=True)

    all_events, warmup_by_symbol = build_events(DATA_DIR)
    work, holdout = split_work_holdout(all_events)

    work_path = OUTPUT_DIR / "a2_events_work.csv"
    holdout_path = HOLDOUT_DIR / "a2_events_holdout.csv"
    summary_path = OUTPUT_DIR / "a2_events_summary.json"

    work.to_csv(work_path, index=False)
    holdout.to_csv(holdout_path, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbols": list(SYMBOLS),
        "window_days": WINDOW_DAYS,
        "min_history_days": MIN_HISTORY_DAYS,
        "merge_window_hours": int(MERGE_WINDOW / pd.Timedelta(hours=1)),
        "total_events": int(len(all_events)),
        "work_events": int(len(work)),
        "holdout_events": int(len(holdout)),
        "work_to_holdout_ratio": float(len(work) / len(holdout)) if len(holdout) else None,
        "warmup_excluded_by_symbol": warmup_by_symbol,
        "warmup_excluded_total": int(sum(warmup_by_symbol.values())),
        "tier_counts_all": tier_counts(all_events),
        "tier_counts_work": tier_counts(work),
        "tier_counts_holdout": tier_counts(holdout),
        "outputs": {
            "work": str(work_path.relative_to(ROOT)),
            "holdout": str(holdout_path.relative_to(ROOT)),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
