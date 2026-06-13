#!/usr/bin/env python3
"""A-1 event-study framework prepared before preregistration freeze.

This module defines auditable, small functions for the A-1 OI collapse event
study. It must not import from or access any HOLDOUT path. It also must not
read post-cutoff market rows.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


CUTOFF_TS = pd.Timestamp("2024-12-09 23:59:59")
DEFAULT_HORIZONS = [24, 48, 72]


def _assert_no_holdout_path(path: str | Path) -> None:
    """Reject HOLDOUT paths; this framework is work-sample only."""
    parts = {part.upper() for part in Path(path).parts}
    assert "HOLDOUT" not in parts, "HOLDOUT path access is forbidden"


def _to_utc_naive(series: pd.Series | pd.Index) -> pd.Series | pd.Index:
    """Convert timestamps to UTC-naive pandas timestamps for stable compares."""
    converted = pd.to_datetime(series, utc=True)
    if isinstance(converted, pd.DatetimeIndex):
        return converted.tz_convert(None)
    return converted.dt.tz_convert(None)


def _normalise_price_frame(price_df: pd.DataFrame) -> pd.DataFrame:
    """Return price data indexed by sorted UTC-naive datetimes with close numeric."""
    frame = price_df.copy()
    if not isinstance(frame.index, pd.DatetimeIndex):
        if "datetime" not in frame.columns:
            raise ValueError("price_df must have a DatetimeIndex or a datetime column")
        frame["datetime"] = _to_utc_naive(frame["datetime"])
        frame = frame.set_index("datetime")
    else:
        frame.index = _to_utc_naive(frame.index)
    if "close" not in frame.columns:
        raise ValueError("price_df must contain a close column")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    return frame.sort_index()


def _event_time_column(episodes: pd.DataFrame) -> str:
    """Resolve the event timestamp column used by an episode table."""
    for column in ("event_time", "event_ts", "ts", "datetime"):
        if column in episodes.columns:
            return column
    raise ValueError("episodes must contain one of event_time/event_ts/ts/datetime")


def _spearman_from_pairs(x_values: list[float], y_values: list[float]) -> float:
    """Compute Spearman rank correlation using pandas ranks and numpy Pearson."""
    if len(x_values) < 2 or len(y_values) < 2:
        return math.nan
    x_rank = pd.Series(x_values, dtype="float64").rank(method="average").to_numpy()
    y_rank = pd.Series(y_values, dtype="float64").rank(method="average").to_numpy()
    if np.std(x_rank) == 0 or np.std(y_rank) == 0:
        return math.nan
    return float(np.corrcoef(x_rank, y_rank)[0, 1])


def load_episodes(path: str) -> pd.DataFrame:
    """Read an A-1 episode list.

    Args:
        path: CSV path for an episode table. The path must not contain
            `HOLDOUT`. Expected timestamp column names are `event_time`,
            `event_ts`, `ts`, or `datetime`.

    Returns:
        A DataFrame sorted by `event_time` with UTC-naive `event_time`.
        If no `episode_id` column exists, one is assigned from row order.
    """
    _assert_no_holdout_path(path)
    episodes = pd.read_csv(path)
    time_col = _event_time_column(episodes)
    episodes = episodes.copy()
    episodes["event_time"] = _to_utc_naive(episodes[time_col])
    if "episode_id" not in episodes.columns:
        episodes["episode_id"] = np.arange(len(episodes), dtype=int)
    return episodes.sort_values(["event_time", "episode_id"]).reset_index(drop=True)


def align_windows(
    episodes: pd.DataFrame,
    price_df: pd.DataFrame,
    horizons: Iterable[int] = DEFAULT_HORIZONS,
) -> pd.DataFrame:
    """Align episode timestamps to forward price windows.

    Args:
        episodes: DataFrame with at least an event timestamp column. Optional
            columns such as `symbol` and OI quantile fields are carried through.
        price_df: Price DataFrame with `close` and either a DatetimeIndex or
            `datetime` column. If `symbol` exists in both inputs, prices are
            filtered per episode symbol.
        horizons: Horizon lengths in hours. Defaults to 24/48/72.

    Returns:
        One row per episode per horizon with `log_return`, t0 close, horizon
        close, and timestamp audit columns. Rows without enough future price
        data are omitted.

    Raises:
        AssertionError: if price data contains rows after 2024-12-09 23:59:59.

    Notes:
        This function must not import from or access any HOLDOUT path. The t0
        close is the first close at or after the event time, never a pre-event
        close.
    """
    prices = _normalise_price_frame(price_df)
    price_df = prices
    assert price_df.index.max() <= pd.Timestamp("2024-12-09 23:59:59")
    events = episodes.copy()
    time_col = _event_time_column(events)
    events["event_time"] = _to_utc_naive(events[time_col])
    if "episode_id" not in events.columns:
        events["episode_id"] = np.arange(len(events), dtype=int)

    rows: list[dict[str, object]] = []
    for event in events.sort_values("event_time").itertuples(index=False):
        event_dict = event._asdict()
        symbol = event_dict.get("symbol")
        symbol_prices = prices
        if symbol is not None and "symbol" in prices.columns:
            symbol_prices = prices[prices["symbol"] == symbol]
        symbol_prices = symbol_prices[symbol_prices["close"].notna()]
        if symbol_prices.empty:
            continue

        event_time = pd.Timestamp(event_dict["event_time"])
        pos = symbol_prices.index.searchsorted(event_time, side="left")
        if pos >= len(symbol_prices):
            continue
        t0_time = symbol_prices.index[pos]
        t0_close = float(symbol_prices.iloc[pos]["close"])
        if t0_close <= 0:
            continue

        for horizon in horizons:
            target_time = t0_time + pd.Timedelta(hours=int(horizon))
            end_pos = symbol_prices.index.searchsorted(target_time, side="left")
            if end_pos >= len(symbol_prices):
                continue
            end_time = symbol_prices.index[end_pos]
            end_close = float(symbol_prices.iloc[end_pos]["close"])
            if end_close <= 0:
                continue
            row = {
                "episode_id": event_dict["episode_id"],
                "symbol": symbol,
                "event_time": event_time,
                "t0_time": t0_time,
                "horizon": int(horizon),
                "horizon_end_time": end_time,
                "t0_close": t0_close,
                "horizon_close": end_close,
                "log_return": math.log(end_close / t0_close),
            }
            for key, value in event_dict.items():
                if key not in row and key not in {"Index"}:
                    row[key] = value
            rows.append(row)
    return pd.DataFrame(rows)


def compute_car(window_df: pd.DataFrame) -> pd.DataFrame:
    """Compute CAR-style event mean, median, and t-stat by horizon.

    Args:
        window_df: Output from `align_windows`, requiring `horizon` and
            `log_return` columns.

    Returns:
        DataFrame with `horizon`, `n`, `mean_log_return`,
        `median_log_return`, and `t_stat`. `t_stat` is NaN when there are fewer
        than two observations or zero sample variance.
    """
    required = {"horizon", "log_return"}
    missing = required - set(window_df.columns)
    if missing:
        raise ValueError(f"window_df missing columns: {sorted(missing)}")
    rows: list[dict[str, object]] = []
    for horizon, group in window_df.groupby("horizon", sort=True):
        returns = pd.to_numeric(group["log_return"], errors="coerce").dropna()
        n = int(len(returns))
        mean = float(returns.mean()) if n else math.nan
        median = float(returns.median()) if n else math.nan
        std = float(returns.std(ddof=1)) if n > 1 else math.nan
        t_stat = mean / (std / math.sqrt(n)) if n > 1 and std > 0 else math.nan
        rows.append(
            {
                "horizon": int(horizon),
                "n": n,
                "mean_log_return": mean,
                "median_log_return": median,
                "t_stat": t_stat,
            }
        )
    return pd.DataFrame(rows)


def monotonicity_test(window_df: pd.DataFrame, quantile_col: str) -> pd.DataFrame:
    """Run fixed-four-bin OI monotonicity checks with Spearman correlation.

    Args:
        window_df: Output from `align_windows`, including `horizon`,
            `log_return`, and the requested OI quantile column.
        quantile_col: Column containing precomputed OI rolling percentile or
            fixed quantile bucket labels. Numeric values are cut into fixed
            `[0, .25, .5, .75, 1]` bins; no full-sample quantiles are computed.

    Returns:
        DataFrame with one row per horizon/bucket: bucket order, observations,
        bucket mean, horizon-level Spearman r, and a monotonicity direction flag.
    """
    required = {"horizon", "log_return", quantile_col}
    missing = required - set(window_df.columns)
    if missing:
        raise ValueError(f"window_df missing columns: {sorted(missing)}")
    frame = window_df.loc[:, ["horizon", "log_return", quantile_col]].copy()
    frame["log_return"] = pd.to_numeric(frame["log_return"], errors="coerce")
    numeric_quantiles = pd.to_numeric(frame[quantile_col], errors="coerce")
    if numeric_quantiles.notna().all():
        frame["bucket"] = pd.cut(
            numeric_quantiles,
            bins=[-math.inf, 0.25, 0.50, 0.75, math.inf],
            labels=["Q1", "Q2", "Q3", "Q4"],
        )
        frame["bucket_order"] = frame["bucket"].map({"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}).astype(int)
    else:
        categories = sorted(str(value) for value in frame[quantile_col].dropna().unique())
        order_map = {category: index + 1 for index, category in enumerate(categories)}
        frame["bucket"] = frame[quantile_col].map(lambda value: str(value))
        frame["bucket_order"] = frame["bucket"].map(order_map)

    rows: list[dict[str, object]] = []
    for horizon, group in frame.dropna(subset=["log_return", "bucket_order"]).groupby("horizon", sort=True):
        bucketed = (
            group.groupby(["bucket", "bucket_order"], observed=True, sort=True)["log_return"]
            .agg(["count", "mean"])
            .reset_index()
            .sort_values("bucket_order")
        )
        means = bucketed["mean"].astype(float).tolist()
        orders = bucketed["bucket_order"].astype(float).tolist()
        spearman_r = _spearman_from_pairs(orders, means)
        monotonic_direction = "none"
        if len(means) >= 2 and all(left <= right for left, right in zip(means, means[1:])):
            monotonic_direction = "increasing"
        elif len(means) >= 2 and all(left >= right for left, right in zip(means, means[1:])):
            monotonic_direction = "decreasing"
        for item in bucketed.itertuples(index=False):
            rows.append(
                {
                    "horizon": int(horizon),
                    "quantile_col": quantile_col,
                    "bucket": str(item.bucket),
                    "bucket_order": int(item.bucket_order),
                    "n": int(item.count),
                    "mean_log_return": float(item.mean),
                    "spearman_r": spearman_r,
                    "monotonic_direction": monotonic_direction,
                }
            )
    return pd.DataFrame(rows)


def permutation_test(window_df: pd.DataFrame, n_perm: int = 10000, seed: int = 42) -> dict:
    """Run one-sided sign-flip permutation tests for positive event mean.

    Args:
        window_df: Output from `align_windows`, requiring `horizon` and
            `log_return`.
        n_perm: Number of random sign-flip permutations.
        seed: Pre-registered random seed for reproducibility.

    Returns:
        Dictionary with seed, permutation count, alternative, and per-horizon
        observed mean and one-sided p-value in `[0, 1]`.
    """
    required = {"horizon", "log_return"}
    missing = required - set(window_df.columns)
    if missing:
        raise ValueError(f"window_df missing columns: {sorted(missing)}")
    rng = np.random.default_rng(seed)
    result: dict[str, object] = {
        "seed": seed,
        "n_perm": n_perm,
        "alternative": "greater",
        "horizons": {},
    }
    for horizon, group in window_df.groupby("horizon", sort=True):
        values = pd.to_numeric(group["log_return"], errors="coerce").dropna().to_numpy(dtype=float)
        if len(values) == 0:
            result["horizons"][int(horizon)] = {"n": 0, "observed_mean": math.nan, "p_value": math.nan}
            continue
        observed = float(values.mean())
        signs = rng.choice(np.array([-1.0, 1.0]), size=(int(n_perm), len(values)))
        perm_means = (signs * values).mean(axis=1)
        p_value = float((1 + np.sum(perm_means >= observed)) / (int(n_perm) + 1))
        result["horizons"][int(horizon)] = {
            "n": int(len(values)),
            "observed_mean": observed,
            "p_value": p_value,
        }
    return result


def _load_price_until_cutoff(path: str, cutoff: pd.Timestamp) -> pd.DataFrame:
    """Load price rows up to cutoff and stop before post-cutoff market data."""
    _assert_no_holdout_path(path)
    rows: list[dict[str, object]] = []
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ts = pd.to_datetime(row.get("datetime") or row.get("ts"), utc=True).tz_convert(None)
            if ts > cutoff + pd.Timedelta(hours=23, minutes=59, seconds=59):
                break
            row["datetime"] = ts
            rows.append(row)
    frame = pd.DataFrame(rows)
    if "close" in frame.columns:
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    return frame


def run_full_study(episode_path: str, price_path: str, cutoff: str) -> dict:
    """Run the prepared A-1 event-study pipeline after preregistration freeze.

    Args:
        episode_path: CSV path for the preregistered work-sample episodes.
        price_path: CSV path for pre-cutoff price data.
        cutoff: Must equal `2024-12-09`.

    Returns:
        Dictionary containing aligned windows, CAR summary, and permutation
        p-values. Callers may add the preregistered monotonicity column after
        freezing it in the hypothesis document.
    """
    assert pd.Timestamp(cutoff) == pd.Timestamp("2024-12-09"), "cutoff mismatch"
    _assert_no_holdout_path(episode_path)
    _assert_no_holdout_path(price_path)
    episodes = load_episodes(episode_path)
    price_df = _load_price_until_cutoff(price_path, pd.Timestamp(cutoff))
    windows = align_windows(episodes, price_df, horizons=DEFAULT_HORIZONS)
    return {
        "windows": windows,
        "car": compute_car(windows),
        "permutation": permutation_test(windows, n_perm=10000, seed=42),
    }
