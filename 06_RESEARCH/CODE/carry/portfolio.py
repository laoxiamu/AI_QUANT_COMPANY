"""Frozen BTC/ETH weighting and portfolio aggregation."""

from __future__ import annotations

from dataclasses import dataclass, replace

import pandas as pd

from carry.config import EngineConfig
from carry.engine import BacktestResult, run_trigger_comparison


DEFAULT_WEIGHTS = {"BTCUSDT": 0.7, "ETHUSDT": 0.3}


@dataclass(frozen=True)
class PortfolioBacktestResult:
    timeline: pd.DataFrame
    events: pd.DataFrame
    summary: dict[str, float | int | bool]
    symbol_results: dict[str, BacktestResult]


def _aggregate_variant(
    symbol_results: dict[str, BacktestResult],
) -> PortfolioBacktestResult:
    pnl_columns = []
    event_frames = []
    for symbol, result in symbol_results.items():
        pnl = result.timeline.set_index("timestamp")["cumulative_pnl"].rename(
            symbol
        )
        pnl_columns.append(pnl)
        if not result.events.empty:
            event_frame = result.events.copy()
            event_frame.insert(0, "symbol", symbol)
            event_frames.append(event_frame)

    cumulative_by_symbol = (
        pd.concat(pnl_columns, axis=1).sort_index().ffill().fillna(0.0)
    )
    initial_capital = sum(
        result.initial_capital for result in symbol_results.values()
    )
    timeline = cumulative_by_symbol.copy()
    timeline["cumulative_pnl"] = cumulative_by_symbol.sum(axis=1)
    timeline["equity"] = initial_capital + timeline["cumulative_pnl"]
    timeline = timeline.reset_index()
    events = (
        pd.concat(event_frames, ignore_index=True)
        if event_frames
        else pd.DataFrame(columns=["symbol", "timestamp", "event_type"])
    )
    return PortfolioBacktestResult(
        timeline=timeline,
        events=events,
        summary={
            "net_pnl": float(
                sum(result.summary["net_pnl"] for result in symbol_results.values())
            ),
            "funding_pnl": float(
                sum(
                    result.summary["funding_pnl"]
                    for result in symbol_results.values()
                )
            ),
            "trading_cost": float(
                sum(
                    result.summary["trading_cost"]
                    for result in symbol_results.values()
                )
            ),
            "buffer_breach_count": int(
                sum(
                    result.summary["buffer_breach_count"]
                    for result in symbol_results.values()
                )
            ),
            "liquidation_count": int(
                sum(
                    result.summary["liquidation_count"]
                    for result in symbol_results.values()
                )
            ),
            "liquidated": any(
                bool(result.summary["liquidated"])
                for result in symbol_results.values()
            ),
            "initial_capital": float(initial_capital),
        },
        symbol_results=symbol_results,
    )


def run_portfolio_comparison(
    inputs: dict[str, tuple[pd.DataFrame, pd.DataFrame, pd.Series]],
    *,
    config: EngineConfig,
    weights: dict[str, float] | None = None,
) -> dict[str, PortfolioBacktestResult]:
    selected_weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
    if set(inputs) != set(selected_weights):
        raise ValueError("inputs and weights must contain the same symbols")
    if any(weight <= 0 for weight in selected_weights.values()):
        raise ValueError("weights must be positive")
    if abs(sum(selected_weights.values()) - 1.0) > 1e-12:
        raise ValueError("weights must sum to 1")

    variants: dict[str, dict[str, BacktestResult]] = {
        "without_trigger": {},
        "with_trigger": {},
    }
    for symbol, weight in selected_weights.items():
        marks, funding, oi_percentile = inputs[symbol]
        symbol_config = replace(
            config,
            base_notional=config.base_notional * weight,
        )
        comparison = run_trigger_comparison(
            marks,
            funding,
            oi_percentile,
            symbol_config,
        )
        for variant, result in comparison.items():
            variants[variant][symbol] = result

    return {
        variant: _aggregate_variant(results)
        for variant, results in variants.items()
    }
