"""Time-exit sensitivity for the frozen v4 bullish Sweep candidates.

Runs t+6, t+12, and t+24 with one execution engine for both the three-symbol
portfolio and the BTC+ETH subset. The entry bar counts as holding bar one.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from v4_strategy_backtest import (
    BAR_HOURS,
    FEE_RATE,
    INITIAL_CAPITAL,
    PERIODS,
    RISK_FRACTION,
    SLIPPAGE_RATE,
    SYMBOL_ORDER,
    build_candidates,
    load_pre_holdout_data,
    metrics,
    run_backtest as run_v4_backtest,
    slice_metrics,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
HOLDING_WINDOWS = (6, 12, 24)
SUBSETS = {
    "three_symbols": SYMBOL_ORDER,
    "btc_eth": ("BTC", "ETH"),
}
COMMON_START = pd.Timestamp("2020-08-11 04:00:00")
COMMON_END = pd.Timestamp("2024-12-09 12:00:00")
BOOTSTRAP_SAMPLES = 10_000
BOOTSTRAP_SEED = 20260606


@dataclass
class Position:
    symbol: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    stop: float
    initial_qty: float
    remaining_qty: float
    risk_budget: float
    nominal_risk: float
    entry_equity: float
    entry_fee: float
    fees: float
    funding_cost: float = 0.0
    realized_gross: float = 0.0
    holding_bars: int = 0


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.Series
    rejected_conflicts: int
    rejected_invalid_risk: int
    rejected_no_capacity: int
    exposure_scaled_entries: int
    max_gross_leverage: float


def _bar_maps(
    bars_by_symbol: dict[str, pd.DataFrame],
) -> tuple[pd.DatetimeIndex, dict[str, dict[pd.Timestamp, object]]]:
    timeline = pd.DatetimeIndex(
        sorted(set().union(*(set(frame["datetime"]) for frame in bars_by_symbol.values())))
    )
    maps = {
        symbol: {row.datetime: row for row in frame.itertuples(index=False)}
        for symbol, frame in bars_by_symbol.items()
    }
    return timeline, maps


def _funding_maps(
    funding_by_symbol: dict[str, pd.DataFrame],
) -> dict[str, dict[pd.Timestamp, float]]:
    return {
        symbol: {
            row.datetime: float(row.last_funding_rate)
            for row in frame.itertuples(index=False)
        }
        for symbol, frame in funding_by_symbol.items()
    }


def run_backtest(
    bars_by_symbol: dict[str, pd.DataFrame],
    funding_by_symbol: dict[str, pd.DataFrame],
    candidates: pd.DataFrame,
    holding_window: int,
    symbols: Iterable[str],
) -> BacktestResult:
    active_symbols = tuple(symbols)
    selected_bars = {symbol: bars_by_symbol[symbol] for symbol in active_symbols}
    timeline, bar_maps = _bar_maps(selected_bars)
    funding_maps = _funding_maps(
        {symbol: funding_by_symbol[symbol] for symbol in active_symbols}
    )
    selected_candidates = candidates[candidates["symbol"].isin(active_symbols)]
    candidate_map = {
        timestamp: group.sort_values("symbol")
        for timestamp, group in selected_candidates.groupby("entry_time")
    }

    cash = INITIAL_CAPITAL
    positions: dict[str, Position] = {}
    last_price: dict[str, float] = {}
    trade_records: list[dict[str, object]] = []
    equity_points: list[tuple[pd.Timestamp, float]] = []
    rejected_conflicts = 0
    rejected_invalid_risk = 0
    rejected_no_capacity = 0
    exposure_scaled_entries = 0
    max_gross_leverage = 0.0

    def equity(now: pd.Timestamp, mark_field: str) -> float:
        value = cash
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, mark_field)) if row is not None else last_price[symbol]
            value += position.remaining_qty * (mark - position.entry_price)
        return value

    def gross_exposure(now: pd.Timestamp, mark_field: str) -> float:
        total = 0.0
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, mark_field)) if row is not None else last_price[symbol]
            total += position.remaining_qty * mark
        return total

    def close_position(
        position: Position,
        trigger_price: float,
    ) -> float:
        nonlocal cash
        execution_price = trigger_price * (1 - SLIPPAGE_RATE)
        gross = position.remaining_qty * (execution_price - position.entry_price)
        fee = position.remaining_qty * execution_price * FEE_RATE
        cash += gross - fee
        position.realized_gross += gross
        position.fees += fee
        position.remaining_qty = 0.0
        return execution_price

    def record_closed(
        position: Position,
        exit_time: pd.Timestamp,
        exit_price: float,
        reason: str,
    ) -> None:
        net_pnl = position.realized_gross - position.fees - position.funding_cost
        trade_records.append(
            {
                "symbol": position.symbol,
                "signal_time": position.signal_time,
                "entry_time": position.entry_time,
                "exit_time": exit_time,
                "entry_price": position.entry_price,
                "sweep_low": position.stop,
                "exit_price": exit_price,
                "exit_reason": reason,
                "initial_quantity": position.initial_qty,
                "initial_notional": position.initial_qty * position.entry_price,
                "risk_budget": position.risk_budget,
                "nominal_risk": position.nominal_risk,
                "entry_equity": position.entry_equity,
                "entry_fee": position.entry_fee,
                "total_fees": position.fees,
                "funding_cost": position.funding_cost,
                "gross_pnl": position.realized_gross,
                "net_pnl": net_pnl,
                "net_return_on_entry_equity": net_pnl / position.entry_equity,
                "expectancy_r": net_pnl / position.risk_budget,
                "holding_bars": position.holding_bars,
                "holding_hours": position.holding_bars * BAR_HOURS,
                "holding_window": holding_window,
            }
        )

    for now in timeline:
        current_rows = {
            symbol: bar_maps[symbol].get(now) for symbol in active_symbols
        }
        for symbol, row in current_rows.items():
            if row is not None:
                last_price[symbol] = float(row.open)

        had_position_at_open = set(positions)

        # Funding settles before new entries at the same timestamp, matching v4.
        for symbol, position in list(positions.items()):
            if now in funding_maps[symbol]:
                row = current_rows[symbol]
                mark = float(row.open) if row is not None else last_price[symbol]
                payment = position.remaining_qty * mark * funding_maps[symbol][now]
                cash -= payment
                position.funding_cost += payment

        entries = candidate_map.get(now)
        if entries is not None:
            valid_entries: list[dict[str, object]] = []
            entry_equity = equity(now, "open")
            for candidate in entries.itertuples(index=False):
                if candidate.symbol in had_position_at_open:
                    rejected_conflicts += 1
                    continue
                entry_price = float(candidate.raw_entry_open) * (1 + SLIPPAGE_RATE)
                nominal_risk = entry_price - float(candidate.sweep_low)
                if nominal_risk <= 0:
                    rejected_invalid_risk += 1
                    continue
                desired_qty = entry_equity * RISK_FRACTION / nominal_risk
                valid_entries.append(
                    {
                        "candidate": candidate,
                        "entry_price": entry_price,
                        "nominal_risk": nominal_risk,
                        "desired_qty": desired_qty,
                        "desired_notional": desired_qty * entry_price,
                    }
                )
            desired_total = sum(float(item["desired_notional"]) for item in valid_entries)
            available_notional = max(
                0.0,
                (entry_equity - gross_exposure(now, "open")) / (1 + FEE_RATE),
            )
            scale = min(1.0, available_notional / desired_total) if desired_total else 0.0
            for item in valid_entries:
                candidate = item["candidate"]
                quantity = float(item["desired_qty"]) * scale
                if quantity <= 0:
                    rejected_no_capacity += 1
                    continue
                if scale < 1:
                    exposure_scaled_entries += 1
                entry_price = float(item["entry_price"])
                nominal_risk = float(item["nominal_risk"])
                fee = quantity * entry_price * FEE_RATE
                cash -= fee
                positions[candidate.symbol] = Position(
                    symbol=candidate.symbol,
                    signal_time=candidate.signal_time,
                    entry_time=now,
                    entry_price=entry_price,
                    stop=float(candidate.sweep_low),
                    initial_qty=quantity,
                    remaining_qty=quantity,
                    risk_budget=quantity * nominal_risk,
                    nominal_risk=nominal_risk,
                    entry_equity=entry_equity,
                    entry_fee=fee,
                    fees=fee,
                )

        # Entry bar is bar one. Stop is always evaluated before time exit.
        for symbol, position in list(positions.items()):
            row = current_rows[symbol]
            if row is None:
                continue
            position.holding_bars += 1
            if float(row.low) <= position.stop:
                exit_price = close_position(position, position.stop)
                reason = "STOP"
            elif position.holding_bars == holding_window:
                exit_price = close_position(position, float(row.close))
                reason = "TIME"
            else:
                continue
            record_closed(position, now, exit_price, reason)
            del positions[symbol]

        for symbol, row in current_rows.items():
            if row is not None:
                last_price[symbol] = float(row.close)
        marked_equity = equity(now, "close")
        marked_exposure = gross_exposure(now, "close")
        if marked_equity > 0:
            max_gross_leverage = max(
                max_gross_leverage, marked_exposure / marked_equity
            )
        equity_points.append((now, marked_equity))

    for symbol, position in list(positions.items()):
        last_row = selected_bars[symbol].iloc[-1]
        exit_time = pd.Timestamp(last_row["datetime"])
        exit_price = close_position(position, float(last_row["close"]))
        record_closed(position, exit_time, exit_price, "RESEARCH_END")
        del positions[symbol]
    if equity_points:
        equity_points[-1] = (equity_points[-1][0], cash)

    trades = pd.DataFrame(trade_records).sort_values(
        ["entry_time", "symbol"]
    ).reset_index(drop=True)
    equity_series = pd.Series(
        [value for _, value in equity_points],
        index=pd.DatetimeIndex([time for time, _ in equity_points]),
        name="equity",
    )
    return BacktestResult(
        trades=trades,
        equity=equity_series,
        rejected_conflicts=rejected_conflicts,
        rejected_invalid_risk=rejected_invalid_risk,
        rejected_no_capacity=rejected_no_capacity,
        exposure_scaled_entries=exposure_scaled_entries,
        max_gross_leverage=max_gross_leverage,
    )


def _boundaries() -> list[pd.Timestamp]:
    span = COMMON_END - COMMON_START
    return [
        COMMON_START,
        (COMMON_START + span / 3).floor("4h"),
        (COMMON_START + span * 2 / 3).floor("4h"),
        COMMON_END + pd.Timedelta(hours=4),
    ]


def summarize(result: BacktestResult) -> dict[str, object]:
    trades = result.trades
    summary = metrics(result.equity, trades, starting_equity=INITIAL_CAPITAL)
    costs = float(trades["total_fees"].sum() + trades["funding_cost"].sum())
    gross_before_costs = float(summary["net_profit"]) + costs
    stops = trades[trades["exit_reason"] == "STOP"]
    times = trades[trades["exit_reason"] == "TIME"]
    bounds = _boundaries()
    summary.update(
        {
            "stop_count": int(len(stops)),
            "time_exit_count": int(len(times)),
            "research_end_count": int((trades["exit_reason"] == "RESEARCH_END").sum()),
            "stop_rate": float(len(stops) / len(trades)) if len(trades) else None,
            "average_stop_holding_bars": (
                float(stops["holding_bars"].mean()) if len(stops) else None
            ),
            "average_stop_net_pnl": (
                float(stops["net_pnl"].mean()) if len(stops) else None
            ),
            "average_time_exit_net_pnl": (
                float(times["net_pnl"].mean()) if len(times) else None
            ),
            "total_costs": costs,
            "gross_before_costs": gross_before_costs,
            "costs_as_pct_of_gross_profit": (
                costs / gross_before_costs if gross_before_costs > 0 else None
            ),
            "rejected_conflicts": result.rejected_conflicts,
            "rejected_invalid_risk": result.rejected_invalid_risk,
            "rejected_no_capacity": result.rejected_no_capacity,
            "exposure_scaled_entries": result.exposure_scaled_entries,
            "max_gross_leverage": result.max_gross_leverage,
            "walk_forward": [
                {
                    "window": index + 1,
                    **slice_metrics(
                        result.equity,
                        trades,
                        bounds[index],
                        bounds[index + 1],
                    ),
                }
                for index in range(3)
            ],
            "periods": {
                label: slice_metrics(result.equity, trades, start, end)
                for label, start, end in PERIODS
            },
        }
    )
    return summary


def paired_daily_bootstrap(
    left: pd.Series,
    right: pd.Series,
) -> dict[str, float | bool]:
    aligned = pd.concat([left.rename("left"), right.rename("right")], axis=1).ffill()
    daily = aligned.resample("1D").last().pct_change().dropna()
    differences = (daily["left"] - daily["right"]).to_numpy()
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    samples = rng.choice(
        differences,
        size=(BOOTSTRAP_SAMPLES, len(differences)),
        replace=True,
    ).mean(axis=1)
    lower, upper = np.quantile(samples, [0.025, 0.975])
    return {
        "mean_daily_return_difference": float(differences.mean()),
        "ci_95_lower": float(lower),
        "ci_95_upper": float(upper),
        "significant_at_5pct": bool(lower > 0 or upper < 0),
    }


def plot_equities(
    results: dict[str, dict[int, BacktestResult]],
    output_path: Path,
) -> None:
    figure, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
    colors = {6: "#1f77b4", 12: "#2ca02c", 24: "#d62728"}
    for axis, (subset, subset_results) in zip(axes, results.items()):
        for window, result in subset_results.items():
            axis.plot(
                result.equity.index,
                result.equity.values,
                label=f"t+{window}",
                color=colors[window],
                linewidth=1.2,
            )
        axis.set_title(subset.replace("_", " ").title())
        axis.set_ylabel("Equity (USDT)")
        axis.grid(alpha=0.25)
        axis.legend()
    axes[-1].set_xlabel("UTC time")
    figure.suptitle("Time Exit Sensitivity: Unified t+6 / t+12 / t+24")
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bars, funding = load_pre_holdout_data()
    candidates = build_candidates(bars)
    v4_btc_eth = run_v4_backtest(
        bars, funding, candidates, symbols=SUBSETS["btc_eth"]
    )
    results: dict[str, dict[int, BacktestResult]] = {}
    summaries: dict[str, dict[str, object]] = {}

    for subset, symbols in SUBSETS.items():
        results[subset] = {}
        summaries[subset] = {}
        for window in HOLDING_WINDOWS:
            result = run_backtest(
                bars, funding, candidates, holding_window=window, symbols=symbols
            )
            results[subset][window] = result
            summaries[subset][f"t{window}"] = summarize(result)
            prefix = f"time_sensitivity_{subset}_t{window}"
            result.trades.to_csv(
                OUTPUT_DIR / f"{prefix}_trades.csv",
                index=False,
                date_format="%Y-%m-%d %H:%M:%S",
            )
            result.equity.to_csv(OUTPUT_DIR / f"{prefix}_equity.csv", header=True)

            time_trades = result.trades[result.trades["exit_reason"] == "TIME"]
            if len(time_trades) and not (
                time_trades["holding_bars"] == window
            ).all():
                raise AssertionError(f"{subset} t+{window} exited on wrong bar")
            if (result.trades["holding_bars"] < 1).any():
                raise AssertionError("Holding-bar count must include entry bar")

    comparisons: dict[str, dict[str, object]] = {}
    for subset, subset_results in results.items():
        comparisons[subset] = {
            "t6_minus_t12": paired_daily_bootstrap(
                subset_results[6].equity, subset_results[12].equity
            ),
            "t24_minus_t12": paired_daily_bootstrap(
                subset_results[24].equity, subset_results[12].equity
            ),
        }

    output = {
        "experiment": "time_exit_sensitivity",
        "diagnostic_only": True,
        "holdout_accessed": False,
        "v6_comparator": "t+12 from this unified implementation",
        "parameters": {
            "holding_windows": list(HOLDING_WINDOWS),
            "entry_bar_is_holding_bar_one": True,
            "stop_precedes_time_exit": True,
            "initial_capital": INITIAL_CAPITAL,
            "risk_per_trade": RISK_FRACTION,
            "leverage_cap": 1.0,
            "taker_fee": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "historical Binance 8H; missing settlements 0.01%",
            "data_scope": "fixed pre-Holdout nrows inherited from v4",
        },
        "event_candidates": int(len(candidates)),
        "funding_data": {
            symbol: {
                "settlements": int(len(frame)),
                "historical_settlements": int((~frame["is_approximate"]).sum()),
                "approximate_settlements": int(frame["is_approximate"].sum()),
            }
            for symbol, frame in funding.items()
        },
        "v4_btc_eth_baseline": summarize(v4_btc_eth),
        "results": summaries,
        "paired_daily_return_bootstrap": comparisons,
    }
    metrics_path = OUTPUT_DIR / "time_sensitivity_metrics.json"
    metrics_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    plot_equities(results, OUTPUT_DIR / "time_sensitivity_equity_curves.png")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
