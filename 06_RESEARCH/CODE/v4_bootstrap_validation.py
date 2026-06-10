"""Dependence-aware bootstrap validation for v5_sweep_regime_bull_v4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVENTS_PATH = (
    PROJECT_ROOT
    / "06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv"
)
JSON_PATH = (
    PROJECT_ROOT
    / "06_RESEARCH/CODE/output/v4_bootstrap_validation.json"
)
FIGURE_PATH = (
    PROJECT_ROOT
    / "06_RESEARCH/RESULTS/"
    "20260606_v4_bootstrap_null_distributions.png"
)
HORIZONS = (6, 12, 24)
DEFAULT_ITERATIONS = 10_000
DEFAULT_BLOCK_SIZE = 20
DEFAULT_SEED = 20260606


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--block-size", type=int, default=DEFAULT_BLOCK_SIZE)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def load_events(path: Path) -> pd.DataFrame:
    events = pd.read_csv(path, parse_dates=["datetime"])
    required = {
        "symbol",
        "datetime",
        *(f"future_ret_{horizon}" for horizon in HORIZONS),
    }
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
    if len(events) != 425:
        raise ValueError(f"Expected 425 registered events, found {len(events)}")
    if events[list(required)].isna().any().any():
        raise ValueError("Bootstrap input contains null values")
    if events.duplicated(["symbol", "datetime"]).any():
        raise ValueError("Bootstrap input contains duplicate symbol/time events")
    counts = events.groupby("symbol").size().to_dict()
    if counts != {"BTC": 185, "ETH": 143, "SOL": 97}:
        raise ValueError(f"Unexpected per-symbol event counts: {counts}")
    return events.sort_values(["symbol", "datetime"]).reset_index(drop=True)


def circular_mbb_indices(
    sample_size: int,
    block_size: int,
    iterations: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Return circular moving-block indices with exactly sample_size draws."""
    if not 1 <= block_size <= sample_size:
        raise ValueError("block_size must be between 1 and each group size")
    block_count = int(np.ceil(sample_size / block_size))
    starts = rng.integers(0, sample_size, size=(iterations, block_count))
    offsets = np.arange(block_size)
    indices = (starts[:, :, None] + offsets) % sample_size
    return indices.reshape(iterations, -1)[:, :sample_size]


def bootstrap_horizon(
    events: pd.DataFrame,
    horizon: int,
    iterations: int,
    block_size: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Build zero-null and ordinary MBB distributions by symbol."""
    null_sums = np.zeros(iterations)
    raw_sums = np.zeros(iterations)
    total_size = 0
    column = f"future_ret_{horizon}"

    for _, group in events.groupby("symbol", sort=True):
        values = group.sort_values("datetime")[column].to_numpy(dtype=float)
        indices = circular_mbb_indices(
            len(values), block_size, iterations, rng
        )
        raw_draws = values[indices]
        null_draws = (values - values.mean())[indices]
        raw_sums += raw_draws.sum(axis=1)
        null_sums += null_draws.sum(axis=1)
        total_size += len(values)

    return null_sums / total_size, raw_sums / total_size


def circular_block_totals(values: np.ndarray, block_size: int) -> np.ndarray:
    extended = np.concatenate([values, values[: block_size - 1]])
    cumulative = np.concatenate([[0.0], np.cumsum(extended)])
    starts = np.arange(len(values))
    return cumulative[starts + block_size] - cumulative[starts]


def calendar_block_bootstrap(
    events: pd.DataFrame,
    horizon: int,
    iterations: int,
    block_size: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, dict[str, int | str]]:
    """Resample synchronized 4H blocks, preserving cross-symbol dependence."""
    start = events["datetime"].min()
    end = events["datetime"].max()
    calendar = pd.date_range(start, end, freq="4h")
    position = pd.Series(np.arange(len(calendar)), index=calendar)
    raw_at_time = np.zeros(len(calendar))
    null_at_time = np.zeros(len(calendar))
    count_at_time = np.zeros(len(calendar))
    column = f"future_ret_{horizon}"

    for _, group in events.groupby("symbol", sort=True):
        values = group[column].to_numpy(dtype=float)
        indices = position.loc[group["datetime"]].to_numpy(dtype=int)
        raw_at_time[indices] += values
        null_at_time[indices] += values - values.mean()
        count_at_time[indices] += 1

    full_blocks, remainder = divmod(len(calendar), block_size)
    raw_block_sums = circular_block_totals(raw_at_time, block_size)
    null_block_sums = circular_block_totals(null_at_time, block_size)
    count_block_sums = circular_block_totals(count_at_time, block_size)
    if remainder:
        raw_partial_sums = circular_block_totals(raw_at_time, remainder)
        null_partial_sums = circular_block_totals(null_at_time, remainder)
        count_partial_sums = circular_block_totals(count_at_time, remainder)

    null_means = np.empty(iterations)
    raw_means = np.empty(iterations)
    batch_size = 250
    for batch_start in range(0, iterations, batch_size):
        batch_end = min(batch_start + batch_size, iterations)
        size = batch_end - batch_start
        starts = rng.integers(
            0, len(calendar), size=(size, full_blocks)
        )
        raw_sums = raw_block_sums[starts].sum(axis=1)
        null_sums = null_block_sums[starts].sum(axis=1)
        counts = count_block_sums[starts].sum(axis=1)
        if remainder:
            partial_starts = rng.integers(0, len(calendar), size=size)
            raw_sums += raw_partial_sums[partial_starts]
            null_sums += null_partial_sums[partial_starts]
            counts += count_partial_sums[partial_starts]
        if np.any(counts == 0):
            raise RuntimeError("Calendar bootstrap produced an empty sample")
        raw_means[batch_start:batch_end] = raw_sums / counts
        null_means[batch_start:batch_end] = null_sums / counts

    metadata = {
        "calendar_start": str(start),
        "calendar_end": str(end),
        "calendar_4h_rows": len(calendar),
        "block_size_4h_bars": block_size,
    }
    return null_means, raw_means, metadata


def summarize(
    observed: float,
    null_distribution: np.ndarray,
    raw_distribution: np.ndarray,
) -> dict[str, float | int | list[float]]:
    extreme_count = int(np.count_nonzero(null_distribution >= observed))
    p_value = (extreme_count + 1) / (len(null_distribution) + 1)
    percentile = 100.0 * float(np.mean(null_distribution < observed))
    ci = np.quantile(raw_distribution, [0.025, 0.975])
    return {
        "observed_mean": observed,
        "null_mean": float(null_distribution.mean()),
        "null_std": float(null_distribution.std(ddof=1)),
        "extreme_count": extreme_count,
        "p_one_sided_greater": float(p_value),
        "observed_null_percentile": percentile,
        "bootstrap_mean": float(raw_distribution.mean()),
        "bootstrap_ci_95_percentile": [float(ci[0]), float(ci[1])],
    }


def plot_null_distributions(
    distributions: dict[int, np.ndarray],
    results: dict[str, dict[str, float | int | list[float]]],
    path: Path,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for axis, horizon in zip(axes, HORIZONS):
        null = distributions[horizon] * 100
        observed = float(results[str(horizon)]["observed_mean"]) * 100
        p_value = float(results[str(horizon)]["p_one_sided_greater"])
        axis.hist(null, bins=55, color="#4C78A8", alpha=0.82)
        axis.axvline(
            observed,
            color="#D62728",
            linewidth=2,
            label=f"Observed {observed:.3f}%",
        )
        axis.axvline(0, color="#222222", linewidth=1, linestyle="--")
        axis.set_title(f"t+{horizon}: p={p_value:.6f}")
        axis.set_xlabel("Mean future log return (%) under H0")
        axis.set_ylabel("Bootstrap frequency")
        axis.legend()
    fig.suptitle("v4 synchronized zero-centered 4H block bootstrap (N=10,000)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    if args.iterations <= 0:
        raise ValueError("iterations must be positive")
    events = load_events(EVENTS_PATH)
    rng = np.random.default_rng(args.seed)
    sensitivity_rng = np.random.default_rng(args.seed + 1)
    null_distributions = {}
    results = {}
    sensitivity_results = {}
    calendar_metadata = None

    for horizon in HORIZONS:
        null_distribution, raw_distribution, metadata = (
            calendar_block_bootstrap(
                events,
                horizon,
                args.iterations,
                args.block_size,
                rng,
            )
        )
        sensitivity_null, sensitivity_raw = bootstrap_horizon(
            events,
            horizon,
            args.iterations,
            args.block_size,
            sensitivity_rng,
        )
        observed = float(events[f"future_ret_{horizon}"].mean())
        null_distributions[horizon] = null_distribution
        results[str(horizon)] = summarize(
            observed,
            null_distribution,
            raw_distribution,
        )
        sensitivity_results[str(horizon)] = summarize(
            observed,
            sensitivity_null,
            sensitivity_raw,
        )
        calendar_metadata = metadata

    output = {
        "experiment": "v5_sweep_regime_bull_v4",
        "validation": (
            "zero_centered_synchronized_calendar_moving_block_bootstrap"
        ),
        "holdout_accessed": False,
        "input": str(EVENTS_PATH.relative_to(PROJECT_ROOT)),
        "event_count": len(events),
        "event_counts_by_symbol": {
            key: int(value)
            for key, value in events.groupby("symbol").size().items()
        },
        "parameters": {
            "iterations": args.iterations,
            "block_size_4h_bars": args.block_size,
            "random_seed": args.seed,
            "one_sided_alternative": "combined mean > 0",
            "p_value_estimator": "(extreme_count + 1) / (N + 1)",
        },
        "calendar": calendar_metadata,
        "method_note": (
            "Pure permutation is invalid because it leaves the mean unchanged. "
            "Returns are demeaned within symbol, placed on one common 4H "
            "calendar, and resampled in synchronized circular 20-bar blocks. "
            "This retains event clustering, overlapping-window dependence, and "
            "contemporaneous cross-symbol dependence within sampled blocks. "
            "The non-centered version supplies the percentile confidence "
            "interval."
        ),
        "results": results,
        "sensitivity_independent_symbol_event_mbb": {
            "block_size_event_observations": args.block_size,
            "random_seed": args.seed + 1,
            "results": sensitivity_results,
        },
        "figure": str(FIGURE_PATH.relative_to(PROJECT_ROOT)),
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
    plot_null_distributions(
        null_distributions,
        results,
        FIGURE_PATH,
    )

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
