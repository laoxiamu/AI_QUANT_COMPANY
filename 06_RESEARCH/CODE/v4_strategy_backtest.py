"""Full P&L backtest for the pre-registered v4 bullish Sweep events.

Signal detection is intentionally not repeated. The frozen event file supplies
the Sweep timestamps, while the pre-Holdout OHLCV files supply the next-bar
entry price and the Sweep candle low used as the stop.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from vectorbt.returns.accessors import ReturnsAccessor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
EVENTS_PATH = OUTPUT_DIR / "events_v5_sweep_regime_bull_v4.csv"
INITIAL_CAPITAL = 100_000.0
RISK_FRACTION = 0.01
FEE_RATE = 0.0004
SLIPPAGE_RATE = 0.0005
APPROXIMATE_FUNDING_RATE = 0.0001
TP1_FRACTION = 0.5
BAR_HOURS = 4
HOLDOUT_FRACTION = 0.2
SYMBOL_ORDER = ("BTC", "ETH", "SOL")
PERIODS = (
    ("2019-2020", pd.Timestamp("2019-01-01"), pd.Timestamp("2021-01-01")),
    ("2021", pd.Timestamp("2021-01-01"), pd.Timestamp("2022-01-01")),
    ("2022", pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01")),
    (
        "2023-2024",
        pd.Timestamp("2023-01-01"),
        pd.Timestamp("2025-01-01"),
    ),
)
SYMBOL_CONFIG = {
    "BTC": {
        "bars": PROJECT_ROOT / "BTC_USDT_4H.csv",
        "registered_total_rows": 16267,
        "expected_research_rows": 13013,
        "holdout_start": pd.Timestamp("2024-12-09 16:00:00"),
        "funding": PROJECT_ROOT
        / "06_RESEARCH/DATA/FUTURES/BTCUSDT_FUNDING_8H.csv",
        "funding_research_rows": 5414,
    },
    "ETH": {
        "bars": PROJECT_ROOT / "ETH_USDT_4H.csv",
        "registered_total_rows": 16267,
        "expected_research_rows": 13013,
        "holdout_start": pd.Timestamp("2024-12-09 16:00:00"),
        "funding": PROJECT_ROOT
        / "06_RESEARCH/DATA/FUTURES/ETHUSDT_FUNDING_8H.csv",
        "funding_research_rows": 5414,
    },
    "SOL": {
        "bars": PROJECT_ROOT / "SOL_USDT_4H.csv",
        "registered_total_rows": 12743,
        "expected_research_rows": 10194,
        "holdout_start": pd.Timestamp("2025-04-06 04:00:00"),
        "funding": PROJECT_ROOT
        / "06_RESEARCH/DATA/FUTURES/SOLUSDT_FUNDING_8H.csv",
        "funding_research_rows": 4997,
    },
}


@dataclass
class Position:
    symbol: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    stop: float
    tp1: float
    tp2: float
    initial_qty: float
    remaining_qty: float
    risk_budget: float
    nominal_risk: float
    entry_equity: float
    entry_fee: float
    fees: float
    funding_cost: float = 0.0
    realized_gross: float = 0.0
    tp1_hit: bool = False
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


def load_pre_holdout_data() -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
]:
    bars_by_symbol: dict[str, pd.DataFrame] = {}
    funding_by_symbol: dict[str, pd.DataFrame] = {}
    required = {"datetime", "open", "high", "low", "close", "volume"}
    for symbol, config in SYMBOL_CONFIG.items():
        research_rows = int(
            config["registered_total_rows"] * (1 - HOLDOUT_FRACTION)
        )
        bars = pd.read_csv(
            config["bars"],
            parse_dates=["datetime"],
            nrows=research_rows,
        )
        if len(bars) != config["expected_research_rows"]:
            raise ValueError(f"{symbol} bar snapshot changed")
        if required.difference(bars.columns):
            raise ValueError(f"{symbol} bars missing required columns")
        if bars["datetime"].duplicated().any():
            raise ValueError(f"{symbol} bars contain duplicate timestamps")
        if not bars["datetime"].is_monotonic_increasing:
            raise ValueError(f"{symbol} bars are not ascending")
        if bars["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} Holdout boundary was crossed")

        funding = pd.read_csv(
            config["funding"],
            parse_dates=["datetime"],
            nrows=config["funding_research_rows"],
        )
        if len(funding) != config["funding_research_rows"]:
            raise ValueError(f"{symbol} funding snapshot changed")
        if funding["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} funding Holdout boundary was crossed")
        if funding["datetime"].duplicated().any():
            raise ValueError(f"{symbol} funding has duplicate timestamps")
        funding["last_funding_rate"] = pd.to_numeric(
            funding["last_funding_rate"]
        )
        settlements = pd.DataFrame({
            "datetime": pd.date_range(
                bars["datetime"].min().floor("D"),
                bars["datetime"].max(),
                freq="8h",
            )
        })
        funding = settlements.merge(
            funding[["datetime", "last_funding_rate"]],
            on="datetime",
            how="left",
        )
        funding["is_approximate"] = funding[
            "last_funding_rate"
        ].isna()
        funding["last_funding_rate"] = funding[
            "last_funding_rate"
        ].fillna(APPROXIMATE_FUNDING_RATE)
        bars_by_symbol[symbol] = bars.reset_index(drop=True)
        funding_by_symbol[symbol] = funding.reset_index(drop=True)
    return bars_by_symbol, funding_by_symbol


def build_candidates(
    bars_by_symbol: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    events = pd.read_csv(EVENTS_PATH, parse_dates=["datetime"])
    expected = {"symbol", "datetime", "close", "ref_low"}
    if expected.difference(events.columns):
        raise ValueError("Frozen event file schema changed")
    candidates: list[dict[str, object]] = []
    for symbol in SYMBOL_ORDER:
        bars = bars_by_symbol[symbol]
        indexed = bars.set_index("datetime")
        positions = pd.Series(
            np.arange(len(bars)),
            index=bars["datetime"],
        )
        symbol_events = events[events["symbol"] == symbol]
        for event in symbol_events.itertuples(index=False):
            if event.datetime not in positions.index:
                raise ValueError(f"{symbol} event missing from research bars")
            signal_index = int(positions.loc[event.datetime])
            if signal_index + 1 >= len(bars):
                continue
            signal_bar = indexed.loc[event.datetime]
            if not np.isclose(
                float(signal_bar["close"]),
                float(event.close),
                rtol=0,
                atol=1e-9,
            ):
                raise ValueError(f"{symbol} event close does not match bars")
            next_bar = bars.iloc[signal_index + 1]
            candidates.append(
                {
                    "symbol": symbol,
                    "signal_time": event.datetime,
                    "entry_time": next_bar["datetime"],
                    "raw_entry_open": float(next_bar["open"]),
                    "sweep_low": float(signal_bar["low"]),
                    "ref_low": float(event.ref_low),
                }
            )
    frame = pd.DataFrame(candidates).sort_values(
        ["entry_time", "symbol", "signal_time"]
    )
    if frame.duplicated(["symbol", "entry_time"]).any():
        raise ValueError("Multiple events map to one symbol entry bar")
    return frame.reset_index(drop=True)


def _bar_maps(
    bars_by_symbol: dict[str, pd.DataFrame],
) -> tuple[pd.DatetimeIndex, dict[str, dict[pd.Timestamp, object]]]:
    timeline = pd.DatetimeIndex(
        sorted(
            set().union(
                *[
                    set(frame["datetime"])
                    for frame in bars_by_symbol.values()
                ]
            )
        )
    )
    maps = {
        symbol: {
            row.datetime: row
            for row in frame.itertuples(index=False)
        }
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
    symbols: Iterable[str] = SYMBOL_ORDER,
) -> BacktestResult:
    active_symbols = tuple(symbols)
    selected_bars = {
        symbol: bars_by_symbol[symbol] for symbol in active_symbols
    }
    selected_funding = {
        symbol: funding_by_symbol[symbol] for symbol in active_symbols
    }
    selected_candidates = candidates[
        candidates["symbol"].isin(active_symbols)
    ].copy()
    timeline, bar_maps = _bar_maps(selected_bars)
    funding_maps = _funding_maps(selected_funding)
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

    def equity(mark_field: str = "close") -> float:
        value = cash
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            if row is not None:
                mark = float(getattr(row, mark_field))
            else:
                mark = last_price[symbol]
            value += position.remaining_qty * (
                mark - position.entry_price
            )
        return value

    def gross_exposure(mark_field: str = "open") -> float:
        total = 0.0
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            if row is not None:
                mark = float(getattr(row, mark_field))
            else:
                mark = last_price[symbol]
            total += position.remaining_qty * mark
        return total

    def close_quantity(
        position: Position,
        quantity: float,
        trigger_price: float,
    ) -> tuple[float, float]:
        nonlocal cash
        execution_price = trigger_price * (1 - SLIPPAGE_RATE)
        gross = quantity * (execution_price - position.entry_price)
        fee = quantity * execution_price * FEE_RATE
        cash += gross - fee
        position.realized_gross += gross
        position.fees += fee
        position.remaining_qty -= quantity
        if position.remaining_qty < 1e-12:
            position.remaining_qty = 0.0
        return execution_price, fee

    def record_closed(
        position: Position,
        exit_time: pd.Timestamp,
        exit_price: float,
        reason: str,
    ) -> None:
        net_pnl = (
            position.realized_gross
            - position.fees
            - position.funding_cost
        )
        trade_records.append(
            {
                "symbol": position.symbol,
                "signal_time": position.signal_time,
                "entry_time": position.entry_time,
                "exit_time": exit_time,
                "entry_price": position.entry_price,
                "sweep_low": position.stop,
                "tp1": position.tp1,
                "tp2": position.tp2,
                "exit_price": exit_price,
                "exit_reason": reason,
                "tp1_hit": position.tp1_hit,
                "initial_quantity": position.initial_qty,
                "initial_notional": (
                    position.initial_qty * position.entry_price
                ),
                "risk_budget": position.risk_budget,
                "nominal_risk": position.nominal_risk,
                "entry_equity": position.entry_equity,
                "entry_fee": position.entry_fee,
                "total_fees": position.fees,
                "funding_cost": position.funding_cost,
                "gross_pnl": position.realized_gross,
                "net_pnl": net_pnl,
                "net_return_on_entry_equity": (
                    net_pnl / position.entry_equity
                ),
                "expectancy_r": net_pnl / position.risk_budget,
                "holding_bars": position.holding_bars,
                "holding_hours": position.holding_bars * BAR_HOURS,
            }
        )

    for now in timeline:
        current_rows = {
            symbol: bar_maps[symbol].get(now)
            for symbol in active_symbols
        }
        for symbol, row in current_rows.items():
            if row is not None:
                last_price[symbol] = float(row.open)

        had_position_at_open = set(positions)

        # Existing longs pay/receive funding at the settlement instant.
        for symbol, position in list(positions.items()):
            if now in funding_maps[symbol]:
                row = current_rows[symbol]
                mark = (
                    float(row.open)
                    if row is not None
                    else last_price[symbol]
                )
                payment = (
                    position.remaining_qty
                    * mark
                    * funding_maps[symbol][now]
                )
                cash -= payment
                position.funding_cost += payment

        # Intrabar ordering is conservative: stop before either target.
        for symbol, position in list(positions.items()):
            row = current_rows[symbol]
            if row is None:
                continue
            position.holding_bars += 1
            exit_price = np.nan
            reason = ""
            if float(row.low) <= position.stop:
                exit_price, _ = close_quantity(
                    position,
                    position.remaining_qty,
                    position.stop,
                )
                reason = "STOP"
            else:
                if (
                    not position.tp1_hit
                    and float(row.high) >= position.tp1
                ):
                    exit_price, _ = close_quantity(
                        position,
                        position.initial_qty * TP1_FRACTION,
                        position.tp1,
                    )
                    position.tp1_hit = True
                if (
                    position.remaining_qty > 0
                    and float(row.high) >= position.tp2
                ):
                    exit_price, _ = close_quantity(
                        position,
                        position.remaining_qty,
                        position.tp2,
                    )
                    reason = "TP2"
            if position.remaining_qty == 0:
                record_closed(position, now, float(exit_price), reason)
                del positions[symbol]

        entries = candidate_map.get(now)
        if entries is not None:
            valid_entries: list[dict[str, object]] = []
            entry_equity = equity("open")
            for candidate in entries.itertuples(index=False):
                if candidate.symbol in had_position_at_open:
                    rejected_conflicts += 1
                    continue
                raw_open = float(candidate.raw_entry_open)
                execution_entry = raw_open * (1 + SLIPPAGE_RATE)
                nominal_risk = execution_entry - float(candidate.sweep_low)
                if nominal_risk <= 0:
                    rejected_invalid_risk += 1
                    continue
                risk_budget = entry_equity * RISK_FRACTION
                desired_qty = risk_budget / nominal_risk
                valid_entries.append(
                    {
                        "candidate": candidate,
                        "entry_price": execution_entry,
                        "nominal_risk": nominal_risk,
                        "risk_budget": risk_budget,
                        "desired_qty": desired_qty,
                        "desired_notional": desired_qty * execution_entry,
                    }
                )

            desired_total = sum(
                float(item["desired_notional"]) for item in valid_entries
            )
            available_notional = max(
                0.0,
                (
                    entry_equity - gross_exposure("open")
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
                nominal_risk = float(item["nominal_risk"])
                fee = quantity * entry_price * FEE_RATE
                cash -= fee
                positions[candidate.symbol] = Position(
                    symbol=candidate.symbol,
                    signal_time=candidate.signal_time,
                    entry_time=now,
                    entry_price=entry_price,
                    stop=float(candidate.sweep_low),
                    tp1=entry_price + nominal_risk,
                    tp2=entry_price + 2 * nominal_risk,
                    initial_qty=quantity,
                    remaining_qty=quantity,
                    risk_budget=quantity * nominal_risk,
                    nominal_risk=nominal_risk,
                    entry_equity=entry_equity,
                    entry_fee=fee,
                    fees=fee,
                )

        for symbol, row in current_rows.items():
            if row is not None:
                last_price[symbol] = float(row.close)
        marked_equity = equity("close")
        marked_exposure = gross_exposure("close")
        if marked_equity > 0:
            max_gross_leverage = max(
                max_gross_leverage,
                marked_exposure / marked_equity,
            )
        equity_points.append((now, marked_equity))

    # Close any position at that symbol's final pre-Holdout close.
    for symbol, position in list(positions.items()):
        last_row = selected_bars[symbol].iloc[-1]
        exit_time = pd.Timestamp(last_row["datetime"])
        exit_price, _ = close_quantity(
            position,
            position.remaining_qty,
            float(last_row["close"]),
        )
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


def metrics(
    equity: pd.Series,
    trades: pd.DataFrame,
    starting_equity: float | None = None,
) -> dict[str, float | int | None]:
    clean = equity.dropna()
    if clean.empty:
        return {}
    base = (
        float(starting_equity)
        if starting_equity is not None
        else float(clean.iloc[0])
    )
    returns = ReturnsAccessor.from_value(clean, freq="4h")
    years = (
        (clean.index[-1] - clean.index[0]).total_seconds()
        / (365.2425 * 24 * 3600)
    )
    total_return = float(clean.iloc[-1] / base - 1)
    annual_return = (
        float((clean.iloc[-1] / base) ** (1 / years) - 1)
        if years > 0 and clean.iloc[-1] > 0
        else None
    )
    winners = trades[trades["net_pnl"] > 0]
    losers = trades[trades["net_pnl"] < 0]
    avg_win = float(winners["net_pnl"].mean()) if len(winners) else None
    avg_loss = float(-losers["net_pnl"].mean()) if len(losers) else None
    payoff = (
        avg_win / avg_loss
        if avg_win is not None and avg_loss not in (None, 0)
        else None
    )
    funding_cost = (
        float(trades["funding_cost"].sum()) if len(trades) else 0.0
    )
    net_profit = float(clean.iloc[-1] - base)
    return {
        "starting_equity": base,
        "ending_equity": float(clean.iloc[-1]),
        "net_profit": net_profit,
        "total_return": total_return,
        "annualized_return": annual_return,
        "sharpe": float(returns.sharpe_ratio()),
        "sortino": float(returns.sortino_ratio()),
        "max_drawdown": float(returns.max_drawdown()),
        "trade_count": int(len(trades)),
        "win_rate": (
            float((trades["net_pnl"] > 0).mean()) if len(trades) else None
        ),
        "average_payoff_ratio": payoff,
        "expectancy_r": (
            float(trades["expectancy_r"].mean()) if len(trades) else None
        ),
        "average_holding_bars": (
            float(trades["holding_bars"].mean()) if len(trades) else None
        ),
        "funding_cost": funding_cost,
        "funding_as_pct_of_net_profit": (
            funding_cost / net_profit if net_profit != 0 else None
        ),
        "total_fees": (
            float(trades["total_fees"].sum()) if len(trades) else 0.0
        ),
    }


def slice_metrics(
    equity: pd.Series,
    trades: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> dict[str, object]:
    sliced = equity[(equity.index >= start) & (equity.index < end)]
    period_trades = trades[
        (trades["entry_time"] >= start) & (trades["entry_time"] < end)
    ]
    if sliced.empty:
        return {"start": str(start), "end": str(end), "trade_count": 0}
    return {
        "start": str(start),
        "end": str(end),
        **metrics(
            sliced,
            period_trades,
            starting_equity=float(sliced.iloc[0]),
        ),
    }


def plot_equity(equity: pd.Series, output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(12, 6))
    axis.plot(equity.index, equity.values, color="#145DA0", linewidth=1.3)
    axis.set_title("v4 Sweep Dual-Regime Strategy Equity")
    axis.set_xlabel("UTC time")
    axis.set_ylabel("Equity (USDT)")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bars, funding = load_pre_holdout_data()
    candidates = build_candidates(bars)
    portfolio = run_backtest(bars, funding, candidates)
    portfolio.trades.to_csv(
        OUTPUT_DIR / "v4_strategy_trades.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    portfolio.equity.to_csv(
        OUTPUT_DIR / "v4_strategy_equity_curve.csv",
        header=True,
    )
    plot_equity(
        portfolio.equity,
        OUTPUT_DIR / "v4_strategy_equity_curve.png",
    )

    symbol_metrics = {}
    for symbol in SYMBOL_ORDER:
        result = run_backtest(bars, funding, candidates, symbols=(symbol,))
        symbol_metrics[symbol] = {
            **metrics(
                result.equity,
                result.trades,
                starting_equity=INITIAL_CAPITAL,
            ),
            "candidate_count": int(
                (candidates["symbol"] == symbol).sum()
            ),
            "rejected_conflicts": result.rejected_conflicts,
        }

    common_start = pd.Timestamp("2020-08-11 04:00:00")
    common_end = pd.Timestamp("2024-12-09 12:00:00")
    span = common_end - common_start
    boundaries = [
        common_start,
        (common_start + span / 3).floor("4h"),
        (common_start + span * 2 / 3).floor("4h"),
        common_end + pd.Timedelta(hours=4),
    ]
    walk_forward = [
        {
            "window": index + 1,
            **slice_metrics(
                portfolio.equity,
                portfolio.trades,
                boundaries[index],
                boundaries[index + 1],
            ),
        }
        for index in range(3)
    ]
    period_metrics = {
        label: slice_metrics(
            portfolio.equity,
            portfolio.trades,
            start,
            end,
        )
        for label, start, end in PERIODS
    }
    output = {
        "experiment": "v5_sweep_regime_bull_v4_strategy",
        "engine": "custom intrabar execution + VectorBT returns metrics",
        "holdout_accessed": False,
        "parameters": {
            "initial_capital": INITIAL_CAPITAL,
            "risk_per_trade": RISK_FRACTION,
            "leverage_cap": 1.0,
            "taker_fee": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "historical Binance 8H funding, pre-Holdout rows only",
            "funding_fallback": (
                "missing settlements use fixed 0.01% per 8H"
            ),
            "entry": "next 4H bar open after frozen Sweep event",
            "stop": "Sweep candle low",
            "targets": "50% at 1R, remaining 50% at 2R",
        },
        "event_candidates": int(len(candidates)),
        "funding_data": {
            symbol: {
                "settlements": int(len(frame)),
                "historical_settlements": int(
                    (~frame["is_approximate"]).sum()
                ),
                "approximate_settlements": int(
                    frame["is_approximate"].sum()
                ),
            }
            for symbol, frame in funding.items()
        },
        "portfolio": {
            **metrics(
                portfolio.equity,
                portfolio.trades,
                starting_equity=INITIAL_CAPITAL,
            ),
            "rejected_conflicts": portfolio.rejected_conflicts,
            "rejected_invalid_risk": portfolio.rejected_invalid_risk,
            "rejected_no_capacity": portfolio.rejected_no_capacity,
            "exposure_scaled_entries": portfolio.exposure_scaled_entries,
            "max_gross_leverage": portfolio.max_gross_leverage,
        },
        "by_symbol": symbol_metrics,
        "walk_forward": walk_forward,
        "periods": period_metrics,
    }
    output["strategy_passed"] = (
        output["portfolio"]["sharpe"] > 1.0
        and abs(output["portfolio"]["max_drawdown"]) < 0.25
    )
    with (OUTPUT_DIR / "v4_strategy_metrics.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
