#!/usr/bin/env python3
"""0B12: no stop, t+24 exit, fixed 10% notional diagnostic."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

from v4_strategy_backtest import (
    BAR_HOURS,
    FEE_RATE,
    INITIAL_CAPITAL,
    PERIODS,
    SLIPPAGE_RATE,
    SYMBOL_ORDER,
    build_candidates,
    load_pre_holdout_data,
    metrics,
    slice_metrics,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
HOLDING_BARS = 24
NOTIONAL_FRACTION = 0.10
SUBSETS = {
    "three_symbols": SYMBOL_ORDER,
    "btc_eth": ("BTC", "ETH"),
}
COMMON_START = pd.Timestamp("2020-08-11 04:00:00")
COMMON_END = pd.Timestamp("2024-12-09 12:00:00")


@dataclass
class Position:
    symbol: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    quantity: float
    initial_notional: float
    entry_equity: float
    entry_fee: float
    fees: float
    funding_cost: float = 0.0
    holding_bars: int = 0


@dataclass
class BacktestResult:
    trades: pd.DataFrame
    equity: pd.Series
    candidate_events: int
    rejected_conflicts: int
    rejected_no_capacity: int
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
    trades: list[dict[str, object]] = []
    equity_points: list[tuple[pd.Timestamp, float]] = []
    rejected_conflicts = 0
    rejected_no_capacity = 0
    max_gross_leverage = 0.0

    def equity(now: pd.Timestamp, field: str) -> float:
        value = cash
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            value += position.quantity * (mark - position.entry_price)
        return value

    def gross_exposure(now: pd.Timestamp, field: str) -> float:
        total = 0.0
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            total += position.quantity * mark
        return total

    def close_position(
        position: Position,
        now: pd.Timestamp,
        raw_exit_price: float,
        reason: str,
    ) -> None:
        nonlocal cash
        exit_price = raw_exit_price * (1 - SLIPPAGE_RATE)
        gross_pnl = position.quantity * (exit_price - position.entry_price)
        exit_fee = position.quantity * exit_price * FEE_RATE
        cash += gross_pnl - exit_fee
        net_pnl = gross_pnl - position.fees - exit_fee - position.funding_cost
        trade_return = net_pnl / position.initial_notional
        trades.append(
            {
                "symbol": position.symbol,
                "signal_time": position.signal_time,
                "entry_time": position.entry_time,
                "exit_time": now,
                "entry_price": position.entry_price,
                "exit_price": exit_price,
                "exit_reason": reason,
                "initial_quantity": position.quantity,
                "initial_notional": position.initial_notional,
                "entry_equity": position.entry_equity,
                "entry_fee": position.entry_fee,
                "total_fees": position.fees + exit_fee,
                "funding_cost": position.funding_cost,
                "gross_pnl": gross_pnl,
                "net_pnl": net_pnl,
                "net_return_on_entry_equity": net_pnl / position.entry_equity,
                "trade_return_on_notional": trade_return,
                # Shared helper requires this field; it is not an R multiple here.
                "expectancy_r": trade_return,
                "holding_bars": position.holding_bars,
                "holding_hours": position.holding_bars * BAR_HOURS,
            }
        )

    for now in timeline:
        current_rows = {
            symbol: bar_maps[symbol].get(now) for symbol in active_symbols
        }
        for symbol, row in current_rows.items():
            if row is not None:
                last_price[symbol] = float(row.open)

        held_at_open = set(positions)
        for symbol, position in positions.items():
            if now in funding_maps[symbol]:
                row = current_rows[symbol]
                mark = float(row.open) if row is not None else last_price[symbol]
                payment = position.quantity * mark * funding_maps[symbol][now]
                cash -= payment
                position.funding_cost += payment

        entries = candidate_map.get(now)
        if entries is not None:
            entry_equity = equity(now, "open")
            available = max(
                0.0,
                (entry_equity - gross_exposure(now, "open")) / (1 + FEE_RATE),
            )
            for candidate in entries.itertuples(index=False):
                if candidate.symbol in held_at_open:
                    rejected_conflicts += 1
                    continue
                desired_notional = entry_equity * NOTIONAL_FRACTION
                notional = min(desired_notional, available)
                if notional <= 0:
                    rejected_no_capacity += 1
                    continue
                entry_price = float(candidate.raw_entry_open) * (1 + SLIPPAGE_RATE)
                quantity = notional / entry_price
                fee = notional * FEE_RATE
                cash -= fee
                positions[candidate.symbol] = Position(
                    symbol=candidate.symbol,
                    signal_time=candidate.signal_time,
                    entry_time=now,
                    entry_price=entry_price,
                    quantity=quantity,
                    initial_notional=notional,
                    entry_equity=entry_equity,
                    entry_fee=fee,
                    fees=fee,
                )
                available -= notional * (1 + FEE_RATE)

        # Entry bar is bar one. No price-based exit is evaluated.
        for symbol, position in list(positions.items()):
            row = current_rows[symbol]
            if row is None:
                continue
            position.holding_bars += 1
            if position.holding_bars == HOLDING_BARS:
                close_position(position, now, float(row.close), "TIME_T24")
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
        close_position(
            position,
            pd.Timestamp(last_row["datetime"]),
            float(last_row["close"]),
            "RESEARCH_END",
        )
        del positions[symbol]
    if equity_points:
        equity_points[-1] = (equity_points[-1][0], cash)

    trade_frame = pd.DataFrame(trades).sort_values(
        ["entry_time", "symbol"]
    ).reset_index(drop=True)
    equity_series = pd.Series(
        [value for _, value in equity_points],
        index=pd.DatetimeIndex([time for time, _ in equity_points]),
        name="equity",
    )
    return BacktestResult(
        trades=trade_frame,
        equity=equity_series,
        candidate_events=len(selected_candidates),
        rejected_conflicts=rejected_conflicts,
        rejected_no_capacity=rejected_no_capacity,
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
    bounds = _boundaries()
    largest = trades.loc[trades["net_pnl"].idxmin()]
    summary.update(
        {
            "average_trade_return_on_notional": float(
                trades["trade_return_on_notional"].mean()
            ),
            "median_trade_return_on_notional": float(
                trades["trade_return_on_notional"].median()
            ),
            "total_fees": float(trades["total_fees"].sum()),
            "total_funding": float(trades["funding_cost"].sum()),
            "total_costs": costs,
            "candidate_events": result.candidate_events,
            "rejected_conflicts": result.rejected_conflicts,
            "rejected_no_capacity": result.rejected_no_capacity,
            "max_gross_leverage": result.max_gross_leverage,
            "research_end_count": int(
                (trades["exit_reason"] == "RESEARCH_END").sum()
            ),
            "largest_loss": {
                "symbol": largest["symbol"],
                "entry_time": str(largest["entry_time"]),
                "exit_time": str(largest["exit_time"]),
                "net_pnl": float(largest["net_pnl"]),
                "return_on_notional": float(
                    largest["trade_return_on_notional"]
                ),
                "percent_entry_equity": float(
                    largest["net_pnl"] / largest["entry_equity"]
                ),
            },
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


def plot_equities(results: dict[str, BacktestResult]) -> None:
    figure, axis = plt.subplots(figsize=(13, 6))
    for name, result in results.items():
        axis.plot(result.equity.index, result.equity, label=name, linewidth=1.2)
    axis.axhline(INITIAL_CAPITAL, color="black", linewidth=0.7, alpha=0.5)
    axis.set_title("0B12 No-Stop t+24 Diagnostic")
    axis.set_ylabel("Equity (USDT)")
    axis.set_xlabel("UTC time")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "no_stop_equity_curve.png", dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bars, funding = load_pre_holdout_data()
    candidates = build_candidates(bars)
    results: dict[str, BacktestResult] = {}
    summaries: dict[str, object] = {
        "configuration": {
            "holding_bars": HOLDING_BARS,
            "notional_fraction": NOTIONAL_FRACTION,
            "stop_loss": None,
            "fee_rate": FEE_RATE,
            "slippage_rate": SLIPPAGE_RATE,
            "initial_capital": INITIAL_CAPITAL,
        }
    }
    for name, symbols in SUBSETS.items():
        result = run_backtest(bars, funding, candidates, symbols)
        results[name] = result
        summaries[name] = summarize(result)
        result.trades.to_csv(
            OUTPUT_DIR / f"no_stop_t24_{name}_trades.csv",
            index=False,
            date_format="%Y-%m-%d %H:%M:%S",
        )
        result.equity.to_csv(
            OUTPUT_DIR / f"no_stop_t24_{name}_equity.csv", header=True
        )

        time_trades = result.trades[
            result.trades["exit_reason"] == "TIME_T24"
        ]
        if len(time_trades) and not (
            time_trades["holding_bars"] == HOLDING_BARS
        ).all():
            raise AssertionError(f"{name}: invalid time-exit holding bars")
        if not set(result.trades["exit_reason"]).issubset(
            {"TIME_T24", "RESEARCH_END"}
        ):
            raise AssertionError(f"{name}: price-based exit detected")

    with (OUTPUT_DIR / "no_stop_t24_metrics.json").open("w") as handle:
        json.dump(summaries, handle, indent=2, default=str)
    plot_equities(results)
    print(json.dumps(summaries, indent=2, default=str))


if __name__ == "__main__":
    main()
