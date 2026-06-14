"""Acceptance-input metrics and auditable bootstrap helpers."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd


def _return_series(values: Iterable[float] | pd.Series) -> pd.Series:
    series = pd.Series(values, copy=True, dtype=float).dropna()
    if ((series <= -1.0)).any():
        raise ValueError("returns must be greater than -1")
    return series


def compute_metrics(returns: pd.Series) -> dict[str, float | int]:
    series = _return_series(returns)
    if series.empty:
        raise ValueError("returns must not be empty")
    positive_sum = float(series[series > 0].sum())
    negative_sum = float(-series[series < 0].sum())
    profit_factor = (
        positive_sum / negative_sum if negative_sum > 0 else math.inf
    )
    equity = (1.0 + series).cumprod()
    drawdown = equity / equity.cummax() - 1.0

    if isinstance(returns.index, pd.DatetimeIndex):
        index = pd.DatetimeIndex(returns.loc[series.index].index)
        if index.tz is None:
            index = index.tz_localize("UTC")
        elapsed_years = max(
            (index.max() - index.min()).total_seconds()
            / (365.2425 * 24 * 60 * 60),
            1.0 / 365.2425,
        )
        annualized_log_growth = float(np.log1p(series).sum() / elapsed_years)
        annual_returns = (1.0 + series).groupby(index.year).prod() - 1.0
        positive_year_ratio = float((annual_returns > 0).mean())
    else:
        annualized_log_growth = float(np.log1p(series).mean())
        positive_year_ratio = float("nan")

    return {
        "net_expected_return": float(series.mean()),
        "profit_factor": float(profit_factor),
        "positive_year_ratio": positive_year_ratio,
        "annualized_log_growth": annualized_log_growth,
        "geometric_growth": float(math.expm1(annualized_log_growth)),
        "max_drawdown": float(drawdown.min()),
        "observations": int(len(series)),
    }


def three_way_walk_forward(returns: pd.Series) -> list[dict[str, float | int]]:
    if not isinstance(returns.index, pd.DatetimeIndex):
        raise TypeError("walk-forward returns must use a DatetimeIndex")
    series = _return_series(returns.sort_index())
    if len(series) < 3:
        raise ValueError("at least three observations are required")
    index = pd.DatetimeIndex(series.index)
    start = index.min()
    span = index.max() - start
    boundaries = (start + span / 3, start + span * 2 / 3)
    masks = (
        index < boundaries[0],
        (index >= boundaries[0]) & (index < boundaries[1]),
        index >= boundaries[1],
    )
    output: list[dict[str, float | int]] = []
    for number, mask in enumerate(masks, start=1):
        segment = series.loc[mask]
        if segment.empty:
            raise ValueError("time-based walk-forward produced an empty segment")
        metrics = compute_metrics(segment)
        output.append({"segment": number, **metrics})
    return output


def moving_block_bootstrap_pvalue(
    values: Iterable[float],
    *,
    block_size: int = 9,
    iterations: int = 10_000,
    seed: int = 20260615,
) -> dict[str, float | int]:
    sample = np.asarray(list(values), dtype=float)
    sample = sample[np.isfinite(sample)]
    if len(sample) < 2:
        raise ValueError("at least two finite values are required")
    if not 1 <= block_size <= len(sample):
        raise ValueError("block_size must be between 1 and sample length")
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    observed = float(sample.mean())
    centered = sample - observed
    rng = np.random.default_rng(seed)
    blocks_needed = math.ceil(len(sample) / block_size)
    bootstrap_means = np.empty(iterations)
    offsets = np.arange(block_size)
    for iteration in range(iterations):
        starts = rng.integers(0, len(sample), size=blocks_needed)
        indices = (starts[:, None] + offsets) % len(sample)
        draw = centered[indices.ravel()[: len(sample)]]
        bootstrap_means[iteration] = draw.mean()
    p_value = (1 + int((bootstrap_means >= observed).sum())) / (
        iterations + 1
    )
    return {
        "observed_mean": observed,
        "p_value": float(p_value),
        "block_size": block_size,
        "iterations": iterations,
        "seed": seed,
    }


def cluster_bootstrap_pvalue(
    values: Iterable[float],
    clusters: Iterable[object],
    *,
    iterations: int = 10_000,
    seed: int = 20260615,
) -> dict[str, float | int]:
    frame = pd.DataFrame({"value": list(values), "cluster": list(clusters)})
    frame = frame.dropna(subset=["value", "cluster"])
    if frame.empty:
        raise ValueError("cluster sample must not be empty")
    observed = float(frame["value"].mean())
    frame["centered"] = frame["value"] - observed
    groups = [
        group["centered"].to_numpy(dtype=float)
        for _, group in frame.groupby("cluster", sort=False)
    ]
    rng = np.random.default_rng(seed)
    bootstrap_means = np.empty(iterations)
    for iteration in range(iterations):
        selected = rng.integers(0, len(groups), size=len(groups))
        draw = np.concatenate([groups[index] for index in selected])
        bootstrap_means[iteration] = draw.mean()
    p_value = (1 + int((bootstrap_means >= observed).sum())) / (
        iterations + 1
    )
    return {
        "observed_mean": observed,
        "p_value": float(p_value),
        "clusters": len(groups),
        "iterations": iterations,
        "seed": seed,
    }
