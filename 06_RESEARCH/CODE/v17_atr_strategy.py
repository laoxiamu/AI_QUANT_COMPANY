#!/usr/bin/env python3
"""0B17 ATR stop strategy: ATR x1.9 main test and x3.5 stress test."""

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
    INITIAL_CAPITAL,
    PERIODS,
    RISK_FRACTION,
    SYMBOL_ORDER,
    build_candidates,
    load_pre_holdout_data,
    metrics,
    slice_metrics,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
FEE_RATE = 0.0005
SLIPPAGE_RATE = 0.001
FUNDING_RATE = 0.0001
HOLDING_BARS = 24
LEVERAGE_CAP = 1.0
ATR_MULTIPLES = (1.9, 3.5)
COMMON_START = pd.Timestamp("2020-08-11 04:00:00")
COMMON_END = pd.Timestamp("2024-12-09 12:00:00")


@dataclass
class Position:
    symbol: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    stop_price: float
    atr14: float
    atr_multiple: float
    initial_qty: float
    remaining_qty: float
    initial_notional: float
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
    candidate_count: int
    rejected_conflicts: int
    rejected_invalid_risk: int
    rejected_no_capacity: int
    capped_entries: int
    exposure_scaled_entries: int
    max_gross_leverage: float


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


def prepare_data() -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
    pd.DataFrame,
]:
    bars, funding = load_pre_holdout_data()
    candidates = build_candidates(bars)
    atr_values: list[dict[str, object]] = []
    for symbol, frame in bars.items():
        frame = frame.copy()
        frame["atr14"] = true_range(frame).rolling(14, min_periods=14).mean()
        bars[symbol] = frame
        indexed = frame.set_index("datetime")
        for event in candidates[candidates["symbol"] == symbol].itertuples(
            index=False
        ):
            atr_values.append(
                {
                    "symbol": symbol,
                    "signal_time": event.signal_time,
                    "atr14": float(indexed.loc[event.signal_time, "atr14"]),
                }
            )
    candidates = candidates.merge(
        pd.DataFrame(atr_values),
        on=["symbol", "signal_time"],
        how="left",
        validate="one_to_one",
    )
    if candidates["atr14"].isna().any():
        raise ValueError("ATR merge failed")
    return bars, funding, candidates


def _bar_maps(
    bars: dict[str, pd.DataFrame],
) -> tuple[pd.DatetimeIndex, dict[str, dict[pd.Timestamp, object]]]:
    timeline = pd.DatetimeIndex(
        sorted(set().union(*(set(frame["datetime"]) for frame in bars.values())))
    )
    maps = {
        symbol: {row.datetime: row for row in frame.itertuples(index=False)}
        for symbol, frame in bars.items()
    }
    return timeline, maps


def _funding_times(
    funding: dict[str, pd.DataFrame],
) -> dict[str, set[pd.Timestamp]]:
    return {
        symbol: set(frame["datetime"])
        for symbol, frame in funding.items()
    }


def run_backtest(
    bars_by_symbol: dict[str, pd.DataFrame],
    funding_by_symbol: dict[str, pd.DataFrame],
    candidates: pd.DataFrame,
    atr_multiple: float,
    symbols: Iterable[str] = SYMBOL_ORDER,
) -> BacktestResult:
    active_symbols = tuple(symbols)
    selected_bars = {
        symbol: bars_by_symbol[symbol] for symbol in active_symbols
    }
    timeline, bar_maps = _bar_maps(selected_bars)
    funding_times = _funding_times(
        {symbol: funding_by_symbol[symbol] for symbol in active_symbols}
    )
    selected_candidates = candidates[
        candidates["symbol"].isin(active_symbols)
    ].copy()
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
    capped_entries = 0
    exposure_scaled_entries = 0
    max_gross_leverage = 0.0

    def equity(now: pd.Timestamp, field: str) -> float:
        value = cash
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            value += position.remaining_qty * (mark - position.entry_price)
        return value

    def gross_exposure(now: pd.Timestamp, field: str) -> float:
        total = 0.0
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            total += position.remaining_qty * mark
        return total

    def close_position(
        position: Position,
        now: pd.Timestamp,
        raw_close: float,
        reason: str,
    ) -> None:
        nonlocal cash
        exit_price = raw_close * (1 - SLIPPAGE_RATE)
        gross = position.remaining_qty * (exit_price - position.entry_price)
        exit_fee = position.remaining_qty * exit_price * FEE_RATE
        cash += gross - exit_fee
        position.realized_gross += gross
        position.fees += exit_fee
        position.remaining_qty = 0.0
        net_pnl = (
            position.realized_gross - position.fees - position.funding_cost
        )
        trade_records.append(
            {
                "symbol": position.symbol,
                "signal_time": position.signal_time,
                "entry_time": position.entry_time,
                "exit_time": now,
                "entry_price": position.entry_price,
                "stop_price": position.stop_price,
                "atr14": position.atr14,
                "atr_multiple": position.atr_multiple,
                "atr_risk_pct": position.nominal_risk / position.entry_price,
                "exit_price": exit_price,
                "exit_reason": reason,
                "initial_quantity": position.initial_qty,
                "initial_notional": position.initial_notional,
                "nominal_pct_of_entry_equity": (
                    position.initial_notional / position.entry_equity
                ),
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

        # Existing positions settle fixed approximate funding before new entries.
        for symbol, position in positions.items():
            if now in funding_times[symbol]:
                row = current_rows[symbol]
                mark = float(row.open) if row is not None else last_price[symbol]
                payment = position.remaining_qty * mark * FUNDING_RATE
                cash -= payment
                position.funding_cost += payment

        entries = candidate_map.get(now)
        if entries is not None:
            entry_equity = equity(now, "open")
            valid_entries: list[dict[str, object]] = []
            for candidate in entries.itertuples(index=False):
                if candidate.symbol in held_at_open:
                    rejected_conflicts += 1
                    continue
                entry_price = float(candidate.raw_entry_open) * (
                    1 + SLIPPAGE_RATE
                )
                nominal_risk = float(candidate.atr14) * atr_multiple
                stop_price = entry_price - nominal_risk
                if nominal_risk <= 0 or stop_price <= 0:
                    rejected_invalid_risk += 1
                    continue
                risk_budget = entry_equity * RISK_FRACTION
                desired_qty = risk_budget / nominal_risk
                desired_notional = desired_qty * entry_price
                capped_notional = min(desired_notional, entry_equity)
                if capped_notional < desired_notional:
                    capped_entries += 1
                valid_entries.append(
                    {
                        "candidate": candidate,
                        "entry_price": entry_price,
                        "stop_price": stop_price,
                        "nominal_risk": nominal_risk,
                        "risk_budget": risk_budget,
                        "desired_qty": capped_notional / entry_price,
                        "desired_notional": capped_notional,
                    }
                )

            desired_total = sum(
                float(item["desired_notional"]) for item in valid_entries
            )
            available_notional = max(
                0.0,
                (
                    entry_equity * LEVERAGE_CAP
                    - gross_exposure(now, "open")
                )
                / (1 + FEE_RATE),
            )
            scale = (
                min(1.0, available_notional / desired_total)
                if desired_total > 0
                else 0.0
            )
            for item in valid_entries:
                candidate = item["candidate"]
                quantity = float(item["desired_qty"]) * scale
                if quantity <= 0:
                    rejected_no_capacity += 1
                    continue
                if scale < 1:
                    exposure_scaled_entries += 1
                entry_price = float(item["entry_price"])
                initial_notional = quantity * entry_price
                fee = initial_notional * FEE_RATE
                cash -= fee
                positions[candidate.symbol] = Position(
                    symbol=candidate.symbol,
                    signal_time=candidate.signal_time,
                    entry_time=now,
                    entry_price=entry_price,
                    stop_price=float(item["stop_price"]),
                    atr14=float(candidate.atr14),
                    atr_multiple=atr_multiple,
                    initial_qty=quantity,
                    remaining_qty=quantity,
                    initial_notional=initial_notional,
                    risk_budget=quantity * float(item["nominal_risk"]),
                    nominal_risk=float(item["nominal_risk"]),
                    entry_equity=entry_equity,
                    entry_fee=fee,
                    fees=fee,
                )

        # Entry bar is bar one. Low triggers stop; execution is this bar's close.
        for symbol, position in list(positions.items()):
            row = current_rows[symbol]
            if row is None:
                continue
            position.holding_bars += 1
            if float(row.low) <= position.stop_price:
                close_position(position, now, float(row.close), "STOP_CLOSE")
                del positions[symbol]
            elif position.holding_bars == HOLDING_BARS:
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
        candidate_count=len(selected_candidates),
        rejected_conflicts=rejected_conflicts,
        rejected_invalid_risk=rejected_invalid_risk,
        rejected_no_capacity=rejected_no_capacity,
        capped_entries=capped_entries,
        exposure_scaled_entries=exposure_scaled_entries,
        max_gross_leverage=max_gross_leverage,
    )


def summary(result: BacktestResult) -> dict[str, object]:
    base = metrics(result.equity, result.trades, starting_equity=INITIAL_CAPITAL)
    trades = result.trades
    stop_mask = trades["exit_reason"] == "STOP_CLOSE"
    time_mask = trades["exit_reason"] == "TIME_T24"
    base.update(
        {
            "stop_count": int(stop_mask.sum()),
            "time_exit_count": int(time_mask.sum()),
            "stop_rate": float(stop_mask.mean()),
            "average_nominal_pct": float(
                trades["nominal_pct_of_entry_equity"].mean()
            ),
            "median_nominal_pct": float(
                trades["nominal_pct_of_entry_equity"].median()
            ),
            "average_atr_risk_pct": float(trades["atr_risk_pct"].mean()),
            "total_fees": float(trades["total_fees"].sum()),
            "funding_cost": float(trades["funding_cost"].sum()),
            "total_costs": float(
                trades["total_fees"].sum() + trades["funding_cost"].sum()
            ),
            "candidate_count": result.candidate_count,
            "rejected_conflicts": result.rejected_conflicts,
            "rejected_invalid_risk": result.rejected_invalid_risk,
            "rejected_no_capacity": result.rejected_no_capacity,
            "capped_entries": result.capped_entries,
            "exposure_scaled_entries": result.exposure_scaled_entries,
            "max_gross_leverage": result.max_gross_leverage,
        }
    )
    return base


def boundaries() -> list[pd.Timestamp]:
    span = COMMON_END - COMMON_START
    return [
        COMMON_START,
        (COMMON_START + span / 3).floor("4h"),
        (COMMON_START + span * 2 / 3).floor("4h"),
        COMMON_END + pd.Timedelta(hours=4),
    ]


def payload(
    bars: dict[str, pd.DataFrame],
    funding: dict[str, pd.DataFrame],
    candidates: pd.DataFrame,
    atr_multiple: float,
) -> tuple[BacktestResult, dict[str, object]]:
    portfolio = run_backtest(
        bars, funding, candidates, atr_multiple, SYMBOL_ORDER
    )
    by_symbol = {}
    for symbol in SYMBOL_ORDER:
        result = run_backtest(
            bars, funding, candidates, atr_multiple, (symbol,)
        )
        by_symbol[symbol] = summary(result)
    bounds = boundaries()
    result_payload = {
        "atr_multiple": atr_multiple,
        "portfolio": summary(portfolio),
        "by_symbol": by_symbol,
        "walk_forward": [
            {
                "window": index + 1,
                **slice_metrics(
                    portfolio.equity,
                    portfolio.trades,
                    bounds[index],
                    bounds[index + 1],
                ),
            }
            for index in range(3)
        ],
        "periods": {
            label: slice_metrics(
                portfolio.equity, portfolio.trades, start, end
            )
            for label, start, end in PERIODS
        },
    }
    main = result_payload["portfolio"]
    result_payload["strategy_passed"] = bool(
        main["sharpe"] > 1.0 and abs(main["max_drawdown"]) < 0.25
    )
    return portfolio, result_payload


def plot_equity(results: dict[str, BacktestResult]) -> None:
    figure, axis = plt.subplots(figsize=(13, 6))
    for label, result in results.items():
        axis.plot(result.equity.index, result.equity, label=label, linewidth=1.2)
    axis.axhline(INITIAL_CAPITAL, color="black", linewidth=0.7, alpha=0.5)
    axis.set_title("0B17 ATR Stop Strategy")
    axis.set_xlabel("UTC time")
    axis.set_ylabel("Equity (USDT)")
    axis.grid(alpha=0.2)
    axis.legend()
    figure.tight_layout()
    figure.savefig(OUTPUT / "v17_atr_equity_curve.png", dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bars, funding, candidates = prepare_data()
    results: dict[str, BacktestResult] = {}
    report: dict[str, object] = {
        "experiment": "0B17_ATR_strategy",
        "holdout_accessed": False,
        "parameters": {
            "atr_method": (
                "ATR14 at Sweep bar, simple rolling mean of standard True Range"
            ),
            "holding_bars": HOLDING_BARS,
            "risk_fraction": RISK_FRACTION,
            "leverage_cap": LEVERAGE_CAP,
            "fee_each_side": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "fixed 0.01% at each 8H settlement",
            "stop_execution": "bar close after low breaches stop",
        },
    }
    for multiple in ATR_MULTIPLES:
        result, result_payload = payload(
            bars, funding, candidates, multiple
        )
        key = f"atr_{str(multiple).replace('.', '_')}"
        results[key] = result
        report[key] = result_payload
        result.trades.to_csv(
            OUTPUT / f"v17_atr_{multiple:.1f}_trades.csv",
            index=False,
            date_format="%Y-%m-%d %H:%M:%S",
        )
        result.equity.to_csv(
            OUTPUT / f"v17_atr_{multiple:.1f}_equity.csv", header=True
        )

    results["atr_1_9"].trades.to_csv(
        OUTPUT / "v17_atr_trades.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    with (OUTPUT / "v17_atr_metrics.json").open("w") as handle:
        json.dump(report, handle, indent=2, default=str)
    plot_equity(results)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
