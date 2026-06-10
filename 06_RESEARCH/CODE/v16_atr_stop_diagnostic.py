#!/usr/bin/env python3
"""0B16 diagnostic comparison of structure and ATR stop distances."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from v4_strategy_backtest import (
    SLIPPAGE_RATE,
    SYMBOL_ORDER,
    build_candidates,
    load_pre_holdout_data,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
V4_TRADES = OUTPUT / "v4_strategy_trades.csv"
MAE_TRADES = OUTPUT / "mae_trade_level.csv"
ATR_MULTIPLE = 3.5
QUANTILES = (0.25, 0.50, 0.75, 0.80, 0.90)


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


def quantiles(series: pd.Series) -> dict[str, float]:
    return {
        f"p{int(q * 100)}": float(series.quantile(q))
        for q in QUANTILES
    }


def event_stop_distances() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    bars_by_symbol, _ = load_pre_holdout_data()
    candidates = build_candidates(bars_by_symbol)
    indexed: dict[str, pd.DataFrame] = {}
    for symbol, frame in bars_by_symbol.items():
        frame = frame.copy()
        frame["atr14"] = true_range(frame).rolling(14, min_periods=14).mean()
        indexed[symbol] = frame.set_index("datetime")

    rows: list[dict[str, object]] = []
    for event in candidates.itertuples(index=False):
        entry_price = float(event.raw_entry_open) * (1 + SLIPPAGE_RATE)
        atr14 = float(indexed[event.symbol].loc[event.signal_time, "atr14"])
        sweep_distance = (entry_price - float(event.sweep_low)) / entry_price
        ref_distance = (entry_price - float(event.ref_low)) / entry_price
        atr_distance = ATR_MULTIPLE * atr14 / entry_price
        compound_distance = max(ref_distance, atr_distance)
        rows.append(
            {
                "symbol": event.symbol,
                "signal_time": event.signal_time,
                "entry_time": event.entry_time,
                "entry_price": entry_price,
                "period": (
                    "2019-2020"
                    if event.signal_time < pd.Timestamp("2021-01-01")
                    else "2021"
                    if event.signal_time < pd.Timestamp("2022-01-01")
                    else "2022"
                    if event.signal_time < pd.Timestamp("2023-01-01")
                    else "2023-2024"
                ),
                "sweep_low": float(event.sweep_low),
                "ref_low": float(event.ref_low),
                "atr14": atr14,
                "sweep_distance": sweep_distance,
                "ref_distance": ref_distance,
                "atr35_distance": atr_distance,
                "compound_distance": compound_distance,
                "atr35_stop_price": entry_price * (1 - atr_distance),
                "atr19_stop_price": entry_price * (
                    1 - 1.9 * atr14 / entry_price
                ),
                "compound_stop_price": entry_price * (1 - compound_distance),
            }
        )
    result = pd.DataFrame(rows)
    if len(result) != 425:
        raise ValueError(f"Expected 425 events, got {len(result)}")
    return result, indexed


def stop_summary(frame: pd.DataFrame) -> dict[str, object]:
    columns = {
        "sweep_low": "sweep_distance",
        "ref_low": "ref_distance",
        "atr_3_5": "atr35_distance",
        "max_ref_atr_3_5": "compound_distance",
    }
    result: dict[str, object] = {}
    for name, column in columns.items():
        values = frame[column] * 100
        result[name] = {
            "mean_pct": float(values.mean()),
            "median_pct": float(values.median()),
            **quantiles(values),
        }
    result["comparisons"] = {
        "ref_wider_than_sweep_rate": float(
            (frame["ref_distance"] > frame["sweep_distance"]).mean()
        ),
        "ref_narrower_than_sweep_rate": float(
            (frame["ref_distance"] < frame["sweep_distance"]).mean()
        ),
        "atr35_wider_than_ref_rate": float(
            (frame["atr35_distance"] > frame["ref_distance"]).mean()
        ),
        "atr35_wider_than_sweep_rate": float(
            (frame["atr35_distance"] > frame["sweep_distance"]).mean()
        ),
        "atr35_gt_ref_gt_sweep_rate": float(
            (
                (frame["atr35_distance"] > frame["ref_distance"])
                & (frame["ref_distance"] > frame["sweep_distance"])
            ).mean()
        ),
        "compound_uses_atr_rate": float(
            (frame["atr35_distance"] > frame["ref_distance"]).mean()
        ),
    }
    return result


def theoretical_avoidance(
    event_frame: pd.DataFrame,
    bars: dict[str, pd.DataFrame],
) -> dict[str, object]:
    trades = pd.read_csv(
        V4_TRADES,
        parse_dates=["signal_time", "entry_time", "exit_time"],
    )
    stops = trades[trades["exit_reason"] == "STOP"].copy()
    stop_map = event_frame.set_index(["symbol", "signal_time"])
    records: list[dict[str, object]] = []
    for trade in stops.itertuples(index=False):
        event = stop_map.loc[(trade.symbol, trade.signal_time)]
        path = bars[trade.symbol].loc[trade.entry_time : trade.exit_time]
        path_low = float(path["low"].min())
        atr_stop = float(event["atr35_stop_price"])
        atr19_stop = float(event["atr19_stop_price"])
        compound_stop = float(event["compound_stop_price"])
        records.append(
            {
                "symbol": trade.symbol,
                "signal_time": trade.signal_time,
                "holding_bars": int(trade.holding_bars),
                "path_low_to_original_exit": path_low,
                "atr35_stop_price": atr_stop,
                "compound_stop_price": compound_stop,
                "atr35_original_stop_avoided": bool(path_low > atr_stop),
                "atr19_original_stop_avoided": bool(path_low > atr19_stop),
                "compound_original_stop_avoided": bool(path_low > compound_stop),
            }
        )
    replay = pd.DataFrame(records)
    first_bar = replay[replay["holding_bars"] == 1]
    return {
        "original_stop_count": int(len(replay)),
        "first_bar_stop_count": int(len(first_bar)),
        "atr35": {
            "all_original_stops_avoided_count": int(
                replay["atr35_original_stop_avoided"].sum()
            ),
            "all_original_stops_avoided_rate": float(
                replay["atr35_original_stop_avoided"].mean()
            ),
            "first_bar_stops_avoided_count": int(
                first_bar["atr35_original_stop_avoided"].sum()
            ),
            "first_bar_stops_avoided_rate": float(
                first_bar["atr35_original_stop_avoided"].mean()
            ),
        },
        "atr19": {
            "all_original_stops_avoided_count": int(
                replay["atr19_original_stop_avoided"].sum()
            ),
            "all_original_stops_avoided_rate": float(
                replay["atr19_original_stop_avoided"].mean()
            ),
            "first_bar_stops_avoided_count": int(
                first_bar["atr19_original_stop_avoided"].sum()
            ),
            "first_bar_stops_avoided_rate": float(
                first_bar["atr19_original_stop_avoided"].mean()
            ),
        },
        "compound": {
            "all_original_stops_avoided_count": int(
                replay["compound_original_stop_avoided"].sum()
            ),
            "all_original_stops_avoided_rate": float(
                replay["compound_original_stop_avoided"].mean()
            ),
            "first_bar_stops_avoided_count": int(
                first_bar["compound_original_stop_avoided"].sum()
            ),
            "first_bar_stops_avoided_rate": float(
                first_bar["compound_original_stop_avoided"].mean()
            ),
        },
    }


def mae_coverage() -> dict[str, float | int]:
    mae = pd.read_csv(MAE_TRADES)
    winners = mae[mae["is_winner"].astype(str).str.lower() == "true"].copy()
    atr35_distance_pct = winners["atr14_pct_of_entry"] * ATR_MULTIPLE
    atr19_distance_pct = winners["atr14_pct_of_entry"] * 1.9
    return {
        "winner_count": int(len(winners)),
        "winner_mae_p80_pct": float(winners["mae_pct"].quantile(0.80)),
        "winner_mae_atr_multiple_p80": float(
            winners["mae_atr_multiple"].quantile(0.80)
        ),
        "atr35_winner_mae_coverage_rate": float(
            (winners["mae_pct"] <= atr35_distance_pct).mean()
        ),
        "atr19_winner_mae_coverage_rate": float(
            (winners["mae_pct"] <= atr19_distance_pct).mean()
        ),
    }


def save_chart(frame: pd.DataFrame) -> None:
    columns = [
        ("sweep_distance", "sweep_low"),
        ("ref_distance", "ref_low"),
        ("atr35_distance", "ATR x3.5"),
        ("compound_distance", "max(ref, ATR)"),
    ]
    figure, axes = plt.subplots(1, 2, figsize=(14, 6))
    for column, label in columns:
        axes[0].hist(
            frame[column] * 100,
            bins=35,
            histtype="step",
            linewidth=1.5,
            label=label,
        )
    axes[0].set_title("Stop Distance Distribution")
    axes[0].set_xlabel("Distance from entry (%)")
    axes[0].set_ylabel("Events")
    axes[0].legend()
    axes[0].grid(alpha=0.2)

    period_means = frame.groupby("period")[
        [column for column, _ in columns]
    ].mean() * 100
    period_means.plot(kind="bar", ax=axes[1])
    axes[1].set_title("Mean Stop Distance by Period")
    axes[1].set_ylabel("Distance from entry (%)")
    axes[1].tick_params(axis="x", rotation=0)
    axes[1].legend([label for _, label in columns])
    axes[1].grid(axis="y", alpha=0.2)
    figure.tight_layout()
    figure.savefig(OUTPUT / "atr_vs_structure_stop_charts.png", dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame, bars = event_stop_distances()
    overall = stop_summary(frame)
    period_summary = {
        period: stop_summary(values)
        for period, values in frame.groupby("period", sort=False)
    }
    metrics = {
        "event_count": int(len(frame)),
        "holdout_accessed": False,
        "atr_definition": (
            "ATR14 at Sweep bar, simple rolling mean of standard True Range"
        ),
        "atr_multiple": ATR_MULTIPLE,
        "overall": overall,
        "by_period": period_summary,
        "theoretical_original_stop_avoidance": theoretical_avoidance(
            frame, bars
        ),
        "mae_comparison": mae_coverage(),
    }
    frame.to_csv(OUTPUT / "atr_stop_event_distances.csv", index=False)
    with (OUTPUT / "atr_stop_metrics.json").open("w") as handle:
        json.dump(metrics, handle, indent=2, default=str)
    save_chart(frame)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
