#!/usr/bin/env python3
"""0B15 volatility-compression grouping for the frozen v4 events."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from v4_strategy_backtest import (
    EVENTS_PATH,
    SLIPPAGE_RATE,
    SYMBOL_ORDER,
    build_candidates,
    load_pre_holdout_data,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
HORIZONS = (6, 12, 24)
BOOTSTRAP_SAMPLES = 1_000
BOOTSTRAP_SEED = 20260606


def true_range(frame: pd.DataFrame) -> pd.Series:
    previous_close = frame["close"].shift(1)
    return pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous_close).abs(),
            (frame["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def add_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    tr = true_range(frame)
    frame["atr14"] = tr.rolling(14, min_periods=14).mean()
    frame["atr50"] = tr.rolling(50, min_periods=50).mean()
    middle = frame["close"].rolling(20, min_periods=20).mean()
    deviation = frame["close"].rolling(20, min_periods=20).std(ddof=0)
    frame["bbw"] = (4 * deviation) / middle
    # At each bar this threshold uses only BBW observations available by then.
    frame["bbw_historical_median"] = frame["bbw"].expanding(
        min_periods=20
    ).median()
    return frame


def bootstrap_difference(
    compression: np.ndarray,
    expansion: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, float | bool]:
    differences = np.empty(BOOTSTRAP_SAMPLES)
    for index in range(BOOTSTRAP_SAMPLES):
        left = rng.choice(compression, size=len(compression), replace=True)
        right = rng.choice(expansion, size=len(expansion), replace=True)
        differences[index] = left.mean() - right.mean()
    lower, upper = np.quantile(differences, [0.025, 0.975])
    return {
        "mean_difference": float(compression.mean() - expansion.mean()),
        "ci_95_lower": float(lower),
        "ci_95_upper": float(upper),
        "bootstrap_p_one_sided": float(
            (np.count_nonzero(differences <= 0) + 1)
            / (BOOTSTRAP_SAMPLES + 1)
        ),
        "significant_positive_5pct": bool(lower > 0),
    }


def enrich_events() -> pd.DataFrame:
    bars_by_symbol, _ = load_pre_holdout_data()
    candidates = build_candidates(bars_by_symbol)
    events = pd.read_csv(EVENTS_PATH, parse_dates=["datetime"])
    events = events.merge(
        candidates[
            [
                "symbol",
                "signal_time",
                "entry_time",
                "raw_entry_open",
                "sweep_low",
            ]
        ],
        left_on=["symbol", "datetime"],
        right_on=["symbol", "signal_time"],
        how="left",
        validate="one_to_one",
    )
    if events["entry_time"].isna().any():
        raise ValueError("Event/candidate merge failed")

    enriched: list[dict[str, object]] = []
    for symbol in SYMBOL_ORDER:
        bars = add_indicators(bars_by_symbol[symbol]).reset_index(drop=True)
        positions = pd.Series(np.arange(len(bars)), index=bars["datetime"])
        for event in events[events["symbol"] == symbol].itertuples(index=False):
            signal_index = int(positions.loc[event.datetime])
            previous = bars.iloc[signal_index - 1]
            path6 = bars.iloc[signal_index + 1 : signal_index + 7]
            if len(path6) != 6:
                raise ValueError(f"{symbol} {event.datetime}: incomplete t+6 path")
            entry_price = float(event.raw_entry_open) * (1 + SLIPPAGE_RATE)
            mae6 = max(
                0.0,
                float((entry_price - path6["low"].min()) / entry_price),
            )
            record = event._asdict()
            record.update(
                {
                    "atr14_previous": float(previous["atr14"]),
                    "atr50_previous": float(previous["atr50"]),
                    "bbw_previous": float(previous["bbw"]),
                    "bbw_historical_median": float(
                        previous["bbw_historical_median"]
                    ),
                    "scheme_a_group": (
                        "compression"
                        if previous["atr14"] < previous["atr50"]
                        else "expansion"
                    ),
                    "scheme_b_group": (
                        "compression"
                        if previous["bbw"]
                        < previous["bbw_historical_median"]
                        else "expansion"
                    ),
                    "mae_first6": mae6,
                    "sweep_stop_hit_first6": bool(
                        path6["low"].min() <= event.sweep_low
                    ),
                }
            )
            enriched.append(record)
    result = pd.DataFrame(enriched)
    if len(result) != 425:
        raise ValueError(f"Expected 425 events, got {len(result)}")
    return result


def analyze_scheme(
    frame: pd.DataFrame,
    group_column: str,
    rng: np.random.Generator,
) -> dict[str, object]:
    result: dict[str, object] = {
        "group_counts": frame[group_column].value_counts().to_dict(),
        "returns": {},
        "stop_proxy": {},
        "period_distribution": {},
    }
    for horizon in HORIZONS:
        return_column = f"future_ret_{horizon}"
        compression = frame.loc[
            frame[group_column] == "compression", return_column
        ].to_numpy()
        expansion = frame.loc[
            frame[group_column] == "expansion", return_column
        ].to_numpy()
        test = stats.ttest_ind(
            compression,
            expansion,
            equal_var=False,
            alternative="greater",
        )
        result["returns"][f"t{horizon}"] = {
            "compression": {
                "count": int(len(compression)),
                "mean": float(compression.mean()),
                "median": float(np.median(compression)),
                "std": float(compression.std(ddof=1)),
            },
            "expansion": {
                "count": int(len(expansion)),
                "mean": float(expansion.mean()),
                "median": float(np.median(expansion)),
                "std": float(expansion.std(ddof=1)),
            },
            "welch_t_stat": float(test.statistic),
            "welch_one_sided_p": float(test.pvalue),
            "bootstrap": bootstrap_difference(compression, expansion, rng),
        }

    for group, values in frame.groupby(group_column):
        result["stop_proxy"][group] = {
            "sweep_low_hit_first6_rate": float(
                values["sweep_stop_hit_first6"].mean()
            ),
            "mean_mae_first6": float(values["mae_first6"].mean()),
            "median_mae_first6": float(values["mae_first6"].median()),
            "mae_first6_p80": float(values["mae_first6"].quantile(0.80)),
        }
        counts = pd.crosstab(values["period"], values[group_column])
        result["period_distribution"][group] = {
            period: {
                "count": int(counts.loc[period, group]),
                "share_within_group": float(
                    counts.loc[period, group] / len(values)
                ),
            }
            for period in counts.index
        }
    result["events_2022"] = (
        frame.loc[frame["period"] == "2022", group_column]
        .value_counts()
        .to_dict()
    )
    return result


def save_chart(frame: pd.DataFrame) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(14, 10))
    schemes = [
        ("scheme_a_group", "Scheme A: ATR14 vs ATR50"),
        ("scheme_b_group", "Scheme B: BBW vs Historical Median"),
    ]
    colors = {"compression": "#1f77b4", "expansion": "#ff7f0e"}
    for row, (column, title) in enumerate(schemes):
        means = frame.groupby(column)[
            ["future_ret_6", "future_ret_12", "future_ret_24"]
        ].mean()
        means.T.plot(
            kind="bar",
            ax=axes[row, 0],
            color=[colors.get(index, "#777777") for index in means.index],
        )
        axes[row, 0].set_title(f"{title}: Mean Forward Return")
        axes[row, 0].set_ylabel("Return")
        axes[row, 0].tick_params(axis="x", rotation=0)
        axes[row, 0].grid(axis="y", alpha=0.2)

        stop_rates = frame.groupby(column)["sweep_stop_hit_first6"].mean()
        axes[row, 1].bar(
            stop_rates.index,
            stop_rates.values,
            color=[colors.get(index, "#777777") for index in stop_rates.index],
        )
        axes[row, 1].set_title(f"{title}: Sweep Stop Hit by t+6")
        axes[row, 1].set_ylabel("Hit rate")
        axes[row, 1].set_ylim(0, 1)
        axes[row, 1].grid(axis="y", alpha=0.2)
    figure.tight_layout()
    figure.savefig(OUTPUT / "vol_compression_charts.png", dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame = enrich_events()
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    metrics = {
        "event_count": int(len(frame)),
        "holdout_accessed": False,
        "definitions": {
            "scheme_a": "ATR14[t-1] < ATR50[t-1]",
            "scheme_b": (
                "BBW20[t-1] < expanding historical BBW median available at t-1"
            ),
            "atr": "simple rolling mean of standard True Range",
            "bootstrap_samples": BOOTSTRAP_SAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "scheme_a": analyze_scheme(frame, "scheme_a_group", rng),
        "scheme_b": analyze_scheme(frame, "scheme_b_group", rng),
    }
    frame.to_csv(OUTPUT / "vol_compression_event_groups.csv", index=False)
    with (OUTPUT / "vol_compression_metrics.json").open("w") as handle:
        json.dump(metrics, handle, indent=2, default=str)
    save_chart(frame)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
