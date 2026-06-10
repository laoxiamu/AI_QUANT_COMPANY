#!/usr/bin/env python3
"""0B14 MAE/MFE analysis for the no-stop t+24 trades."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from v4_strategy_backtest import load_pre_holdout_data


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
TRADES_PATH = OUTPUT / "no_stop_t24_three_symbols_trades.csv"
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.80, 0.90)


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


def period_label(timestamp: pd.Timestamp) -> str:
    if timestamp < pd.Timestamp("2021-01-01"):
        return "2019-2020"
    if timestamp < pd.Timestamp("2022-01-01"):
        return "2021"
    if timestamp < pd.Timestamp("2023-01-01"):
        return "2022"
    return "2023-2024"


def quantile_dict(series: pd.Series) -> dict[str, float]:
    return {
        f"p{int(q * 100)}": float(series.quantile(q))
        for q in QUANTILES
    }


def grouped_summary(frame: pd.DataFrame, column: str) -> list[dict[str, object]]:
    rows = []
    for group, values in frame.groupby(column, sort=False):
        winners = values[values["is_winner"]]
        losers = values[~values["is_winner"]]
        rows.append(
            {
                column: group,
                "trade_count": int(len(values)),
                "winner_count": int(len(winners)),
                "loser_count": int(len(losers)),
                "mae_all": quantile_dict(values["mae_pct"]),
                "mae_winners": quantile_dict(winners["mae_pct"]),
                "mae_losers": quantile_dict(losers["mae_pct"]),
                "mean_mae_pct": float(values["mae_pct"].mean()),
                "mean_mfe_pct": float(values["mfe_pct"].mean()),
            }
        )
    return rows


def build_excursions() -> pd.DataFrame:
    bars_by_symbol, _ = load_pre_holdout_data()
    bars_by_symbol = {
        symbol: frame.assign(
            atr14=true_range(frame).rolling(14, min_periods=14).mean()
        ).set_index("datetime")
        for symbol, frame in bars_by_symbol.items()
    }
    trades = pd.read_csv(
        TRADES_PATH,
        parse_dates=["signal_time", "entry_time", "exit_time"],
    )
    records: list[dict[str, object]] = []
    for trade in trades.itertuples(index=False):
        bars = bars_by_symbol[trade.symbol]
        path = bars.loc[trade.entry_time : trade.exit_time]
        if len(path) != 24:
            raise ValueError(
                f"{trade.symbol} {trade.entry_time}: expected 24 bars, got {len(path)}"
            )
        entry_price = float(trade.entry_price)
        mae_pct = max(
            0.0, float((entry_price - path["low"].min()) / entry_price * 100)
        )
        mfe_pct = max(
            0.0, float((path["high"].max() - entry_price) / entry_price * 100)
        )
        signal_atr = float(bars.loc[trade.signal_time, "atr14"])
        atr_pct = signal_atr / entry_price * 100
        records.append(
            {
                "symbol": trade.symbol,
                "signal_time": trade.signal_time,
                "entry_time": trade.entry_time,
                "exit_time": trade.exit_time,
                "period": period_label(trade.signal_time),
                "entry_price": entry_price,
                "net_pnl": float(trade.net_pnl),
                "trade_return_pct": float(trade.trade_return_on_notional) * 100,
                "is_winner": bool(trade.net_pnl > 0),
                "mae_pct": mae_pct,
                "mfe_pct": mfe_pct,
                "mfe_mae_ratio": (
                    mfe_pct / mae_pct if mae_pct > 0 else None
                ),
                "atr14_at_signal": signal_atr,
                "atr14_pct_of_entry": atr_pct,
                "mae_atr_multiple": mae_pct / atr_pct,
            }
        )
    return pd.DataFrame(records)


def save_charts(frame: pd.DataFrame) -> None:
    winners = frame[frame["is_winner"]]
    losers = frame[~frame["is_winner"]]

    figure, axes = plt.subplots(1, 2, figsize=(14, 5))
    bins = np.linspace(0, frame["mae_pct"].max(), 32)
    axes[0].hist(
        winners["mae_pct"], bins=bins, alpha=0.65, label="Winners", color="#2ca02c"
    )
    axes[0].hist(
        losers["mae_pct"], bins=bins, alpha=0.65, label="Losers", color="#d62728"
    )
    axes[0].axvline(
        winners["mae_pct"].quantile(0.80),
        color="black",
        linestyle="--",
        label="Winner MAE p80",
    )
    axes[0].set_title("MAE Distribution")
    axes[0].set_xlabel("MAE (% of entry)")
    axes[0].set_ylabel("Trades")
    axes[0].legend()

    axes[1].boxplot(
        [winners["mae_pct"], losers["mae_pct"]],
        tick_labels=["Winners", "Losers"],
        showfliers=True,
    )
    axes[1].set_title("Winner vs Loser MAE")
    axes[1].set_ylabel("MAE (% of entry)")
    figure.tight_layout()
    figure.savefig(OUTPUT / "mae_distribution_chart.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(
        losers["mae_pct"],
        losers["trade_return_pct"],
        alpha=0.65,
        color="#d62728",
        label="Losers",
    )
    axis.scatter(
        winners["mae_pct"],
        winners["trade_return_pct"],
        alpha=0.65,
        color="#2ca02c",
        label="Winners",
    )
    axis.axvline(
        winners["mae_pct"].quantile(0.80),
        color="black",
        linestyle="--",
        label="Winner MAE p80",
    )
    axis.axhline(0, color="gray", linewidth=0.8)
    axis.set_title("MAE vs Final t+24 Return")
    axis.set_xlabel("MAE (% of entry)")
    axis.set_ylabel("Net return on notional (%)")
    axis.legend()
    axis.grid(alpha=0.2)
    figure.tight_layout()
    figure.savefig(OUTPUT / "mae_vs_return_scatter.png", dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame = build_excursions()
    winners = frame[frame["is_winner"]]
    losers = frame[~frame["is_winner"]]
    winner_ratios = winners["mfe_mae_ratio"].replace([np.inf, -np.inf], np.nan)

    metrics = {
        "input": str(TRADES_PATH.relative_to(ROOT)),
        "holdout_accessed": False,
        "method": {
            "path": "entry bar through exit bar inclusive",
            "expected_bars": 24,
            "entry_price": "executed entry including 0.05% slippage",
            "mae_floor": 0.0,
            "atr": "simple rolling mean of standard True Range, 14 bars",
        },
        "trade_count": int(len(frame)),
        "winner_count": int(len(winners)),
        "loser_count": int(len(losers)),
        "mae_quantiles": {
            "all": quantile_dict(frame["mae_pct"]),
            "winners": quantile_dict(winners["mae_pct"]),
            "losers": quantile_dict(losers["mae_pct"]),
        },
        "mfe_quantiles": {
            "all": quantile_dict(frame["mfe_pct"]),
            "winners": quantile_dict(winners["mfe_pct"]),
            "losers": quantile_dict(losers["mfe_pct"]),
        },
        "winner_mfe_mae_ratio": {
            "median": float(winner_ratios.median()),
            "mean": float(winner_ratios.mean()),
        },
        "winner_mae_atr_multiple": quantile_dict(
            winners["mae_atr_multiple"]
        ),
        "by_symbol": grouped_summary(frame, "symbol"),
        "by_period": grouped_summary(frame, "period"),
        "current_stop_comparison": {
            "sweep_low_average_distance_pct": 2.326035723490167,
            "ref_low_average_distance_pct": 1.378290878174997,
            "winner_mae_p80_pct": float(winners["mae_pct"].quantile(0.80)),
            "winner_mae_atr_multiple_p80": float(
                winners["mae_atr_multiple"].quantile(0.80)
            ),
        },
    }
    frame.to_csv(OUTPUT / "mae_trade_level.csv", index=False)
    with (OUTPUT / "mae_metrics.json").open("w") as handle:
        json.dump(metrics, handle, indent=2, default=str)
    save_charts(frame)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
