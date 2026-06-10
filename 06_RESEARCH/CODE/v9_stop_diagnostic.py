"""Diagnose exit timing in the existing v4 strategy trade ledger.

This is a read-only analysis of v4_strategy_trades.csv. It does not rebuild
signals, load price data, run a strategy, or access Holdout data.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "06_RESEARCH/CODE/output/v4_strategy_trades.csv"
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
CHART_PATH = OUTPUT_DIR / "v4_stop_diagnostic_charts.png"
JSON_PATH = OUTPUT_DIR / "v4_stop_diagnostic_metrics.json"

EXPECTED_EXIT_REASONS = {"STOP", "TP2", "RESEARCH_END"}
PERIOD_ORDER = ["2019-2020", "2021", "2022", "2023-2024"]
SYMBOL_ORDER = ["BTC", "ETH", "SOL"]
BUCKET_ORDER = ["1-3", "4-6", "7-9", "10-11", "12+"]


def as_number(value: object) -> int | float | None:
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, int)):
        return int(value)
    return float(value)


def load_trades() -> pd.DataFrame:
    required = {
        "symbol",
        "entry_time",
        "exit_time",
        "exit_reason",
        "tp1_hit",
        "expectancy_r",
        "net_pnl",
        "holding_bars",
    }
    trades = pd.read_csv(
        INPUT_PATH,
        parse_dates=["entry_time", "exit_time"],
    )
    missing = required.difference(trades.columns)
    if missing:
        raise ValueError(f"Trade ledger missing columns: {sorted(missing)}")
    if trades.empty:
        raise ValueError("Trade ledger is empty")
    if trades[list(required)].isna().any().any():
        raise ValueError("Required trade fields contain null values")
    unknown_reasons = set(trades["exit_reason"]) - EXPECTED_EXIT_REASONS
    if unknown_reasons:
        raise ValueError(f"Unknown exit reasons: {sorted(unknown_reasons)}")
    if (trades["holding_bars"] < 1).any():
        raise ValueError("holding_bars must be at least one")

    elapsed_bars = (
        (trades["exit_time"] - trades["entry_time"])
        / pd.Timedelta(hours=4)
    )
    if not np.allclose(elapsed_bars, trades["holding_bars"]):
        raise ValueError("holding_bars disagrees with entry/exit timestamps")

    years = trades["entry_time"].dt.year
    period = np.select(
        [
            years.between(2019, 2020),
            years.eq(2021),
            years.eq(2022),
            years.between(2023, 2024),
        ],
        PERIOD_ORDER,
        default="OUT_OF_SCOPE",
    )
    if (period == "OUT_OF_SCOPE").any():
        bad_years = sorted(years[period == "OUT_OF_SCOPE"].unique())
        raise ValueError(f"Entry years outside diagnostic periods: {bad_years}")
    trades["period"] = pd.Categorical(
        period,
        categories=PERIOD_ORDER,
        ordered=True,
    )
    trades["holding_bucket"] = pd.Categorical(
        pd.cut(
            trades["holding_bars"],
            bins=[0, 3, 6, 9, 11, np.inf],
            labels=BUCKET_ORDER,
        ),
        categories=BUCKET_ORDER,
        ordered=True,
    )
    return trades


def exit_summary(trades: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    counts = trades["exit_reason"].value_counts()
    for reason in ["STOP", "TP2", "RESEARCH_END"]:
        subset = trades[trades["exit_reason"] == reason]
        rows.append({
            "exit_reason": reason,
            "trade_count": int(len(subset)),
            "share": float(len(subset) / len(trades)),
            "average_holding_bars": (
                float(subset["holding_bars"].mean()) if len(subset) else None
            ),
            "median_holding_bars": (
                float(subset["holding_bars"].median()) if len(subset) else None
            ),
            "average_expectancy_r": (
                float(subset["expectancy_r"].mean()) if len(subset) else None
            ),
            "average_net_pnl": (
                float(subset["net_pnl"].mean()) if len(subset) else None
            ),
            "tp1_hit_rate": (
                float(subset["tp1_hit"].mean()) if len(subset) else None
            ),
            "ledger_count_check": int(counts.get(reason, 0)),
        })
    return rows


def layered_summary(
    trades: pd.DataFrame,
    column: str,
    order: list[str],
) -> list[dict[str, object]]:
    rows = []
    for label in order:
        subset = trades[trades[column] == label]
        stops = subset[subset["exit_reason"] == "STOP"]
        rows.append({
            column: label,
            "trade_count": int(len(subset)),
            "stop_count": int(len(stops)),
            "stop_rate": float(len(stops) / len(subset)) if len(subset) else None,
            "average_holding_bars": (
                float(subset["holding_bars"].mean()) if len(subset) else None
            ),
            "median_holding_bars": (
                float(subset["holding_bars"].median()) if len(subset) else None
            ),
            "average_expectancy_r": (
                float(subset["expectancy_r"].mean()) if len(subset) else None
            ),
            "stop_average_holding_bars": (
                float(stops["holding_bars"].mean()) if len(stops) else None
            ),
            "stop_median_holding_bars": (
                float(stops["holding_bars"].median()) if len(stops) else None
            ),
            "stops_by_t6_close": (
                float((stops["holding_bars"] <= 6).mean())
                if len(stops)
                else None
            ),
        })
    return rows


def build_metrics(trades: pd.DataFrame) -> dict[str, object]:
    stops = trades[trades["exit_reason"] == "STOP"]
    stop_bars = stops["holding_bars"]
    exact_counts = stop_bars.value_counts().sort_index()
    bucket_table = pd.crosstab(
        trades["holding_bucket"],
        trades["exit_reason"],
        dropna=False,
    ).reindex(BUCKET_ORDER, fill_value=0)
    for reason in ["STOP", "TP2", "RESEARCH_END"]:
        if reason not in bucket_table:
            bucket_table[reason] = 0

    return {
        "input": str(INPUT_PATH.relative_to(PROJECT_ROOT)),
        "trade_count": int(len(trades)),
        "overall_average_expectancy_r": float(trades["expectancy_r"].mean()),
        "exit_summary": exit_summary(trades),
        "stop_timing": {
            "count": int(len(stops)),
            "mean_holding_bars": float(stop_bars.mean()),
            "median_holding_bars": float(stop_bars.median()),
            "p25_holding_bars": float(stop_bars.quantile(0.25)),
            "p75_holding_bars": float(stop_bars.quantile(0.75)),
            "mode_holding_bars": int(stop_bars.mode().iloc[0]),
            "strictly_before_t6": float((stop_bars < 6).mean()),
            "by_t6_close": float((stop_bars <= 6).mean()),
            "strictly_before_t12": float((stop_bars < 12).mean()),
            "by_t12_close": float((stop_bars <= 12).mean()),
            "exact_bar_counts": {
                str(int(bar)): int(count)
                for bar, count in exact_counts.items()
            },
        },
        "holding_bucket_by_exit": [
            {
                "holding_bucket": bucket,
                "STOP": int(bucket_table.loc[bucket, "STOP"]),
                "TP2": int(bucket_table.loc[bucket, "TP2"]),
                "RESEARCH_END": int(
                    bucket_table.loc[bucket, "RESEARCH_END"]
                ),
            }
            for bucket in BUCKET_ORDER
        ],
        "by_symbol": layered_summary(trades, "symbol", SYMBOL_ORDER),
        "by_period": layered_summary(trades, "period", PERIOD_ORDER),
    }


def plot_diagnostics(
    trades: pd.DataFrame,
    metrics: dict[str, object],
) -> None:
    stops = trades[trades["exit_reason"] == "STOP"]
    max_display_bar = 24
    figure, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    stop_plot = stops["holding_bars"].clip(upper=max_display_bar)
    tp2_plot = trades.loc[
        trades["exit_reason"] == "TP2", "holding_bars"
    ].clip(upper=max_display_bar)
    bins = np.arange(0.5, max_display_bar + 1.5, 1)
    axes[0].hist(
        [stop_plot, tp2_plot],
        bins=bins,
        label=["STOP", "TP2"],
        color=["#C94C4C", "#2E8B57"],
        alpha=0.8,
        stacked=False,
    )
    axes[0].axvline(6, color="#555555", linestyle="--", linewidth=1)
    axes[0].axvline(12, color="#222222", linestyle=":", linewidth=1)
    axes[0].set_title("Exit timing by actual exit reason")
    axes[0].set_xlabel("Holding bars (24 includes all 24+)")
    axes[0].set_ylabel("Trade count")
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.25)

    period_rows = metrics["by_period"]
    periods = [row["period"] for row in period_rows]
    stop_rates = [100 * row["stop_rate"] for row in period_rows]
    bars = axes[1].bar(periods, stop_rates, color="#4C78A8")
    axes[1].set_title("Stop rate by entry period")
    axes[1].set_xlabel("Entry period")
    axes[1].set_ylabel("STOP share (%)")
    axes[1].set_ylim(0, 100)
    axes[1].grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, stop_rates):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            value + 2,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    figure.suptitle("v4 strategy stop diagnostic (existing trades only)")
    figure.tight_layout()
    figure.savefig(CHART_PATH, dpi=180)
    plt.close(figure)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trades = load_trades()
    metrics = build_metrics(trades)
    plot_diagnostics(trades, metrics)
    with JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=True, indent=2)
        handle.write("\n")

    timing = metrics["stop_timing"]
    print(
        "Diagnostic complete: "
        f"{metrics['trade_count']} trades, "
        f"{timing['count']} stops, "
        f"median stop bar {timing['median_holding_bars']:.0f}, "
        f"{timing['by_t6_close']:.1%} stopped by t+6 close."
    )
    print(f"JSON: {JSON_PATH}")
    print(f"Chart: {CHART_PATH}")


if __name__ == "__main__":
    main()
