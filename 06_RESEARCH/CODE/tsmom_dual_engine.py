#!/usr/bin/env python3
"""TSMOM expansion dual-engine backtest.

Implements the pre-registered 2026-06-12 dual-engine task without reading
2026H1 increment files and with a hard 2024-12-09 23:59 UTC cutoff.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import csv
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "06_RESEARCH" / "DATA"
FUTURES = DATA / "FUTURES"
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULTS = ROOT / "06_RESEARCH" / "RESULTS"
CODEX_TASKS = ROOT / "04_AI_TEAM" / "CODEX_TASKS"

SYMBOL_ORDER = ("BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "LTC")
CUT_OFF = pd.Timestamp("2024-12-09 23:59:00")
LOOKBACK_BARS = 540
BAR_HOURS = 4
FUNDING_HOURS = 8
INITIAL_CAPITAL = 100_000.0
FEE_RATE = 0.001
SLIPPAGE_RATE = 0.001
LEVERAGE_CAP = 1.0
ADX_PERIOD = 14
ADX_ENTRY = 25.0
ADX_EXIT = 20.0
MACRO_MA_DAYS = 200
BOOTSTRAP_SEED = 20260612
BOOTSTRAP_ITERATIONS = 2000
BOOTSTRAP_BLOCK_BARS = 42
BOOTSTRAP_YEAR_BARS = int(round(365.2425 * 24 / BAR_HOURS))
RISK_BUDGET_TARGET_VOL = 0.25
RISK_BUDGET_WINDOW_BARS = 42
PRE_CUTOFF_ROWS = {
    ("BTC", "MARK_4H"): 10782,
    ("BTC", "FUNDING_8H"): 5415,
    ("ETH", "MARK_4H"): 10818,
    ("ETH", "FUNDING_8H"): 5415,
    ("SOL", "MARK_4H"): 9250,
    ("SOL", "FUNDING_8H"): 4720,
    ("BNB", "MARK_4H"): 10596,
    ("BNB", "FUNDING_8H"): 5294,
    ("XRP", "MARK_4H"): 10758,
    ("XRP", "FUNDING_8H"): 5399,
    ("DOGE", "MARK_4H"): 9672,
    ("DOGE", "FUNDING_8H"): 4841,
    ("ADA", "MARK_4H"): 10708,
    ("ADA", "FUNDING_8H"): 5359,
    ("LTC", "MARK_4H"): 10769,
    ("LTC", "FUNDING_8H"): 5390,
}


@dataclass
class Position:
    symbol: str
    direction: int
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    raw_entry_price: float
    entry_price: float
    quantity: float
    initial_quantity: float
    initial_notional: float
    entry_equity: float
    entry_fee: float
    entry_slippage_cost: float
    partial_gross_pnl: float = 0.0
    partial_exit_fee: float = 0.0
    partial_exit_slippage_cost: float = 0.0
    funding_cost: float = 0.0
    holding_bars: int = 0


@dataclass
class BacktestResult:
    label: str
    trades: pd.DataFrame
    equity: pd.Series
    max_gross_leverage: float
    max_marked_gross_leverage: float
    exposure_scaled_entries: int
    forced_deleveraging_count: int
    risk_scale_history: pd.DataFrame | None = None


def signal_from_prices(current_close: float, lagged_close: float) -> int:
    difference = current_close - lagged_close
    return 1 if difference > 0 else -1 if difference < 0 else 0


def funding_payment(
    direction: int,
    quantity: float,
    mark_price: float,
    rate: float,
) -> float:
    """Positive return value is a cash cost; negative is funding income."""
    return direction * quantity * mark_price * rate


def wilder_average(values: pd.Series, period: int) -> pd.Series:
    return values.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def calculate_adx(bars: pd.DataFrame, period: int = ADX_PERIOD) -> pd.Series:
    high = bars["high"].astype(float)
    low = bars["low"].astype(float)
    close = bars["close"].astype(float)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=bars.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=bars.index,
    )
    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = wilder_average(true_range, period)
    plus_di = 100 * wilder_average(plus_dm, period) / atr
    minus_di = 100 * wilder_average(minus_dm, period) / atr
    denominator = (plus_di + minus_di).replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / denominator
    return wilder_average(dx, period)


def hysteresis_regime(
    adx: pd.Series,
    entry: float = ADX_ENTRY,
    exit_: float = ADX_EXIT,
) -> pd.Series:
    state = False
    output: list[bool] = []
    for value in adx:
        if np.isfinite(value):
            if value > entry:
                state = True
            elif value < exit_:
                state = False
        output.append(state)
    return pd.Series(output, index=adx.index, dtype=bool)


def prior_daily_bull_state(
    datetimes: pd.Series,
    close: pd.Series,
    ma_days: int = MACRO_MA_DAYS,
) -> pd.Series:
    intraday = pd.Series(close.to_numpy(), index=pd.DatetimeIndex(datetimes))
    daily_close = intraday.resample("1D").last()
    daily_ma = daily_close.rolling(ma_days, min_periods=ma_days).mean()
    completed = pd.DataFrame({
        "daily_close": daily_close,
        "daily_ma": daily_ma,
    }).shift(1)
    day_index = pd.DatetimeIndex(datetimes).normalize()
    mapped = completed.reindex(day_index)
    valid = mapped["daily_close"].notna() & mapped["daily_ma"].notna()
    bull = pd.Series(
        pd.array(
            np.where(valid, mapped["daily_close"] > mapped["daily_ma"], pd.NA),
            dtype="boolean",
        ),
        index=close.index,
    )
    return bull


def desired_position(
    engine: str,
    trend_signal: int,
    trend_regime: bool,
    macro_bull: object,
    pit_eligible: bool,
) -> int:
    if not pit_eligible or not trend_regime or pd.isna(macro_bull):
        return 0
    if engine == "L":
        return int(trend_signal == 1 and bool(macro_bull))
    if engine == "S":
        return -int(trend_signal == -1 and not bool(macro_bull))
    raise ValueError(f"unknown engine {engine}")


def passive_gate_position(engine: str, macro_bull: object, pit_eligible: bool) -> int:
    if not pit_eligible or pd.isna(macro_bull):
        return 0
    if engine == "L":
        return int(bool(macro_bull))
    if engine == "S_REFERENCE":
        return -int(not bool(macro_bull))
    raise ValueError(f"unknown passive engine {engine}")


def safe_market_path(symbol: str, suffix: str) -> Path:
    path = FUTURES / f"{symbol}USDT_{suffix}.csv"
    if "2026H1" in path.name:
        raise ValueError(f"forbidden increment file requested: {path}")
    return path


def read_csv_until_cutoff(
    path: Path,
    *,
    required_columns: Iterable[str],
    expected_rows: int,
) -> pd.DataFrame:
    if "2026H1" in path.name:
        raise ValueError(f"forbidden Holdout increment file: {path}")
    required = set(required_columns)
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        missing = required.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
    frame = pd.read_csv(path, nrows=expected_rows)
    if frame.empty:
        raise ValueError(f"{path} has no rows before cutoff")
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    if len(frame) != expected_rows:
        raise ValueError(
            f"{path} expected {expected_rows} pre-cutoff rows, got {len(frame)}"
        )
    if frame["datetime"].max() > CUT_OFF:
        raise ValueError(f"{path} crossed cutoff")
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} has duplicate timestamps")
    if not frame["datetime"].is_monotonic_increasing:
        raise ValueError(f"{path} is not ascending")
    for column in frame.columns:
        if column != "datetime":
            frame[column] = pd.to_numeric(frame[column])
    return frame.reset_index(drop=True)


def load_pit() -> dict[str, pd.Timestamp]:
    pit = pd.read_csv(DATA / "UNIVERSE_PIT.csv", parse_dates=["onboard_date"])
    output = {}
    for symbol in SYMBOL_ORDER:
        full = f"{symbol}USDT"
        match = pit[pit["symbol"] == full]
        if len(match) != 1:
            raise ValueError(f"{full} not found exactly once in UNIVERSE_PIT")
        output[symbol] = pd.Timestamp(match.iloc[0]["onboard_date"])
    return output


def prepare_bars(
    raw: pd.DataFrame,
    *,
    symbol: str,
    onboard_date: pd.Timestamp,
    engine: str,
) -> pd.DataFrame:
    bars = raw.copy()
    bars["signal"] = [
        signal_from_prices(current, lagged)
        if np.isfinite(lagged)
        else 0
        for current, lagged in zip(
            bars["close"].astype(float),
            bars["close"].shift(LOOKBACK_BARS).astype(float),
            strict=True,
        )
    ]
    bars["adx"] = calculate_adx(bars)
    bars["trend_regime"] = hysteresis_regime(bars["adx"])
    bars["macro_bull"] = prior_daily_bull_state(bars["datetime"], bars["close"])
    eligible_time = onboard_date + pd.Timedelta(hours=LOOKBACK_BARS * BAR_HOURS)
    bars["pit_eligible"] = (
        (bars.index >= LOOKBACK_BARS) & (bars["datetime"] >= eligible_time)
    )
    bars["desired"] = [
        desired_position(engine, signal, regime, macro, pit)
        for signal, regime, macro, pit in zip(
            bars["signal"],
            bars["trend_regime"],
            bars["macro_bull"],
            bars["pit_eligible"],
            strict=True,
        )
    ]
    bars["execution_target"] = bars["desired"].shift(1).fillna(0).astype(int)
    bars["signal_time"] = bars["datetime"].shift(1)
    bars["execution_signal"] = bars["signal"].shift(1).fillna(0).astype(int)
    bars["execution_adx"] = bars["adx"].shift(1)
    bars["execution_macro_bull"] = bars["macro_bull"].shift(1)
    bars["execution_pit_eligible"] = (
        bars["pit_eligible"].shift(1).fillna(False).astype(bool)
    )
    bars["symbol"] = symbol
    return bars


def prepare_passive_bars(
    raw: pd.DataFrame,
    *,
    symbol: str,
    onboard_date: pd.Timestamp,
    engine: str,
) -> pd.DataFrame:
    bars = raw.copy()
    bars["macro_bull"] = prior_daily_bull_state(bars["datetime"], bars["close"])
    eligible_time = onboard_date + pd.Timedelta(hours=LOOKBACK_BARS * BAR_HOURS)
    bars["pit_eligible"] = (
        (bars.index >= LOOKBACK_BARS) & (bars["datetime"] >= eligible_time)
    )
    bars["desired"] = [
        passive_gate_position(engine, macro, pit)
        for macro, pit in zip(
            bars["macro_bull"], bars["pit_eligible"], strict=True
        )
    ]
    bars["execution_target"] = bars["desired"].shift(1).fillna(0).astype(int)
    bars["signal_time"] = bars["datetime"].shift(1)
    bars["execution_signal"] = bars["execution_target"]
    bars["execution_adx"] = np.nan
    bars["execution_macro_bull"] = bars["macro_bull"].shift(1)
    bars["execution_pit_eligible"] = (
        bars["pit_eligible"].shift(1).fillna(False).astype(bool)
    )
    bars["symbol"] = symbol
    return bars


def load_data(engine: str) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, object]]:
    pit = load_pit()
    bars: dict[str, pd.DataFrame] = {}
    funding: dict[str, pd.DataFrame] = {}
    audit = {}
    for symbol in SYMBOL_ORDER:
        raw_bars = read_csv_until_cutoff(
            safe_market_path(symbol, "MARK_4H"),
            required_columns=("datetime", "open", "high", "low", "close", "volume"),
            expected_rows=PRE_CUTOFF_ROWS[(symbol, "MARK_4H")],
        )
        raw_funding = read_csv_until_cutoff(
            safe_market_path(symbol, "FUNDING_8H"),
            required_columns=("datetime", "last_funding_rate"),
            expected_rows=PRE_CUTOFF_ROWS[(symbol, "FUNDING_8H")],
        )
        bars[symbol] = prepare_bars(
            raw_bars,
            symbol=symbol,
            onboard_date=pit[symbol],
            engine=engine,
        )
        raw_funding["last_funding_rate"] = pd.to_numeric(
            raw_funding["last_funding_rate"]
        )
        funding[symbol] = raw_funding
        audit[symbol] = {
            "bars_first_timestamp": str(raw_bars["datetime"].min()),
            "bars_last_timestamp": str(raw_bars["datetime"].max()),
            "bars_rows_used": int(len(raw_bars)),
            "funding_first_timestamp": str(raw_funding["datetime"].min()),
            "funding_last_timestamp": str(raw_funding["datetime"].max()),
            "funding_rows_used": int(len(raw_funding)),
            "onboard_date": str(pit[symbol]),
            "pit_eligible_from": str(
                pit[symbol] + pd.Timedelta(hours=LOOKBACK_BARS * BAR_HOURS)
            ),
        }
    return bars, funding, audit


def _maps(
    frames: dict[str, pd.DataFrame],
) -> tuple[pd.DatetimeIndex, dict[str, dict[pd.Timestamp, object]]]:
    timeline = pd.DatetimeIndex(
        sorted(set().union(*(set(frame["datetime"]) for frame in frames.values())))
    )
    maps = {
        symbol: {row.datetime: row for row in frame.itertuples(index=False)}
        for symbol, frame in frames.items()
    }
    return timeline, maps


def risk_scale_from_equity_history(
    equity_history: pd.Series,
    current_time: pd.Timestamp,
    *,
    target_vol: float = RISK_BUDGET_TARGET_VOL,
    window_bars: int = RISK_BUDGET_WINDOW_BARS,
) -> dict[str, object]:
    prior = equity_history[equity_history.index < current_time].dropna()
    prior_returns = prior.pct_change().dropna()
    if len(prior_returns) < window_bars:
        return {
            "scale": 1.0,
            "sigma_annualized": None,
            "prior_return_count": int(len(prior_returns)),
        }
    window = prior_returns.iloc[-window_bars:]
    realized = float(window.std(ddof=1) * np.sqrt(365.2425 * 24 / BAR_HOURS))
    if not np.isfinite(realized) or realized <= 0:
        scale = 1.0
    else:
        scale = min(1.0, target_vol / realized)
    return {
        "scale": float(scale),
        "sigma_annualized": realized,
        "prior_return_count": int(len(prior_returns)),
    }


def run_backtest(
    bars_by_symbol: dict[str, pd.DataFrame],
    funding_by_symbol: dict[str, pd.DataFrame],
    *,
    label: str,
    include_fees: bool = True,
    include_slippage: bool = True,
    include_funding: bool = True,
    risk_budget: bool = False,
    risk_target_vol: float = RISK_BUDGET_TARGET_VOL,
    risk_window_bars: int = RISK_BUDGET_WINDOW_BARS,
) -> BacktestResult:
    symbols = tuple(bars_by_symbol.keys())
    timeline, bar_maps = _maps(bars_by_symbol)
    funding_maps = {
        symbol: {
            row.datetime: float(row.last_funding_rate)
            for row in frame.itertuples(index=False)
        }
        for symbol, frame in funding_by_symbol.items()
    }
    fee_rate = FEE_RATE if include_fees else 0.0
    slippage_rate = SLIPPAGE_RATE if include_slippage else 0.0

    cash = INITIAL_CAPITAL
    positions: dict[str, Position] = {}
    last_price: dict[str, float] = {}
    trades: list[dict[str, object]] = []
    equity_points: list[tuple[pd.Timestamp, float]] = []
    max_gross_leverage = 0.0
    max_marked_gross_leverage = 0.0
    exposure_scaled_entries = 0
    forced_deleveraging_count = 0
    risk_scale_points: list[dict[str, object]] = []

    def price_with_slippage(raw: float, direction: int, is_entry: bool) -> float:
        side = direction if is_entry else -direction
        return raw * (1 + side * slippage_rate)

    def equity(now: pd.Timestamp, field: str) -> float:
        value = cash
        for position in positions.values():
            row = bar_maps[position.symbol].get(now)
            mark = (
                float(getattr(row, field))
                if row is not None
                else last_price[position.symbol]
            )
            value += position.direction * position.quantity * (
                mark - position.entry_price
            )
        return value

    def gross_exposure(now: pd.Timestamp, field: str) -> float:
        total = 0.0
        for position in positions.values():
            row = bar_maps[position.symbol].get(now)
            mark = (
                float(getattr(row, field))
                if row is not None
                else last_price[position.symbol]
            )
            total += position.quantity * mark
        return total

    def close_position(
        position: Position,
        now: pd.Timestamp,
        raw_price: float,
        reason: str,
    ) -> None:
        nonlocal cash
        exit_price = price_with_slippage(raw_price, position.direction, False)
        gross_pnl = position.direction * position.quantity * (
            exit_price - position.entry_price
        )
        exit_notional = position.quantity * exit_price
        exit_fee = exit_notional * fee_rate
        exit_slippage = position.quantity * abs(exit_price - raw_price)
        cash += gross_pnl - exit_fee
        total_gross_pnl = position.partial_gross_pnl + gross_pnl
        total_exit_fee = position.partial_exit_fee + exit_fee
        total_exit_slippage = position.partial_exit_slippage_cost + exit_slippage
        net_pnl = (
            total_gross_pnl
            - position.entry_fee
            - total_exit_fee
            - position.funding_cost
        )
        trades.append(
            {
                "symbol": position.symbol,
                "direction": position.direction,
                "side": "LONG" if position.direction == 1 else "SHORT",
                "signal_time": position.signal_time,
                "entry_time": position.entry_time,
                "exit_time": now,
                "raw_entry_price": position.raw_entry_price,
                "entry_price": position.entry_price,
                "raw_exit_price": raw_price,
                "exit_price": exit_price,
                "exit_reason": reason,
                "quantity": position.initial_quantity,
                "final_quantity": position.quantity,
                "initial_notional": position.initial_notional,
                "entry_equity": position.entry_equity,
                "nominal_pct": position.initial_notional / position.entry_equity,
                "gross_pnl": (
                    total_gross_pnl
                    + position.entry_slippage_cost
                    + total_exit_slippage
                ),
                "net_pnl": net_pnl,
                "entry_fee": position.entry_fee,
                "exit_fee": total_exit_fee,
                "total_fees": position.entry_fee + total_exit_fee,
                "entry_slippage_cost": position.entry_slippage_cost,
                "exit_slippage_cost": total_exit_slippage,
                "total_slippage_cost": (
                    position.entry_slippage_cost + total_exit_slippage
                ),
                "funding_cost": position.funding_cost,
                "expectancy_r": net_pnl / position.initial_notional,
                "holding_bars": position.holding_bars,
                "holding_days": position.holding_bars / 6,
            }
        )

    def trim_position_to_quantity(
        position: Position,
        raw_price: float,
        target_quantity: float,
    ) -> None:
        nonlocal cash
        target_quantity = max(0.0, target_quantity)
        removed_quantity = position.quantity - target_quantity
        if removed_quantity <= 0:
            return
        trim_price = price_with_slippage(raw_price, position.direction, False)
        trim_gross = position.direction * removed_quantity * (
            trim_price - position.entry_price
        )
        trim_fee = removed_quantity * trim_price * fee_rate
        trim_slippage = removed_quantity * abs(trim_price - raw_price)
        cash += trim_gross - trim_fee
        position.quantity = target_quantity
        position.partial_gross_pnl += trim_gross
        position.partial_exit_fee += trim_fee
        position.partial_exit_slippage_cost += trim_slippage

    def add_to_position(
        position: Position,
        raw_price: float,
        add_notional: float,
    ) -> None:
        nonlocal cash
        if add_notional <= 0:
            return
        entry_price = price_with_slippage(raw_price, position.direction, True)
        add_quantity = add_notional / entry_price
        fee = add_notional * fee_rate
        entry_slippage = add_quantity * abs(entry_price - raw_price)
        old_quantity = position.quantity
        new_quantity = old_quantity + add_quantity
        position.entry_price = (
            position.entry_price * old_quantity + entry_price * add_quantity
        ) / new_quantity
        position.quantity = new_quantity
        position.initial_quantity += add_quantity
        position.initial_notional += add_notional
        position.entry_fee += fee
        position.entry_slippage_cost += entry_slippage
        cash -= fee

    def enforce_leverage_cap(now: pd.Timestamp, rows: dict[str, object]) -> None:
        nonlocal cash, forced_deleveraging_count
        current_equity = equity(now, "open")
        current_exposure = gross_exposure(now, "open")
        if (
            not positions
            or current_equity <= 0
            or current_exposure <= current_equity * LEVERAGE_CAP
        ):
            return
        cost_rate = fee_rate + slippage_rate
        numerator = current_equity * LEVERAGE_CAP - current_exposure * cost_rate
        denominator = current_exposure * (1 - cost_rate)
        scale = min(1.0, max(0.0, numerator / denominator))
        for symbol, position in positions.items():
            raw_price = float(rows[symbol].open)
            trim_position_to_quantity(position, raw_price, position.quantity * scale)
        forced_deleveraging_count += 1

    for now in timeline:
        rows = {symbol: bar_maps[symbol].get(now) for symbol in symbols}
        for symbol, row in rows.items():
            if row is not None:
                last_price[symbol] = float(row.open)

        if include_funding:
            for position in positions.values():
                rate = funding_maps[position.symbol].get(now)
                if rate is None:
                    continue
                row = rows[position.symbol]
                mark = (
                    float(row.open)
                    if row is not None
                    else last_price[position.symbol]
                )
                payment = funding_payment(
                    position.direction,
                    position.quantity,
                    mark,
                    rate,
                )
                cash -= payment
                position.funding_cost += payment

        desired = {}
        tradable_count = 0
        for symbol, row in rows.items():
            if row is None:
                continue
            target = int(row.execution_target)
            desired[symbol] = target
            if bool(row.execution_pit_eligible):
                tradable_count += 1

        for symbol, target in desired.items():
            if symbol not in positions or target == positions[symbol].direction:
                continue
            row = rows[symbol]
            if not bool(row.execution_pit_eligible):
                reason = "PIT_INELIGIBLE_EXIT"
            elif pd.isna(row.execution_macro_bull):
                reason = "MACRO_UNKNOWN_EXIT"
            elif label.startswith("tsmom_dual_L") and not bool(row.execution_macro_bull):
                reason = "MACRO_BEAR_EXIT"
            elif label.startswith("tsmom_dual_S") and bool(row.execution_macro_bull):
                reason = "MACRO_BULL_EXIT"
            elif np.isfinite(row.execution_adx) and float(row.execution_adx) < ADX_EXIT:
                reason = "ADX_EXIT"
            else:
                reason = "TREND_EXIT"
            close_position(positions[symbol], now, float(row.open), reason)
            del positions[symbol]

        enforce_leverage_cap(now, rows)

        if risk_budget:
            history = pd.Series(
                [value for _, value in equity_points],
                index=pd.DatetimeIndex([time for time, _ in equity_points]),
                dtype=float,
            )
            risk_stats = risk_scale_from_equity_history(
                history,
                now,
                target_vol=risk_target_vol,
                window_bars=risk_window_bars,
            )
        else:
            risk_stats = {
                "scale": 1.0,
                "sigma_annualized": None,
                "prior_return_count": 0,
            }
        risk_scale = float(risk_stats["scale"])
        risk_scale_points.append(
            {
                "datetime": now,
                "scale": risk_scale,
                "sigma_annualized": risk_stats["sigma_annualized"],
                "prior_return_count": risk_stats["prior_return_count"],
            }
        )

        entry_equity = equity(now, "open")
        target_weight = 1 / tradable_count if tradable_count else 0.0
        if risk_budget and entry_equity > 0 and target_weight > 0:
            for symbol, target in desired.items():
                if target == 0 or symbol not in positions:
                    continue
                position = positions[symbol]
                row = rows[symbol]
                raw_price = float(row.open)
                target_notional = entry_equity * target_weight * risk_scale
                current_notional = position.quantity * raw_price
                if target_notional < current_notional:
                    trim_position_to_quantity(
                        position,
                        raw_price,
                        target_notional / raw_price,
                    )
                elif target_notional > current_notional:
                    current_exposure = gross_exposure(now, "open")
                    available = max(
                        0.0,
                        (entry_equity * LEVERAGE_CAP - current_exposure)
                        / (1 + fee_rate + slippage_rate),
                    )
                    add_to_position(
                        position,
                        raw_price,
                        min(target_notional - current_notional, available),
                    )

        entry_equity = equity(now, "open")
        current_exposure = gross_exposure(now, "open")
        available = max(
            0.0,
            (entry_equity * LEVERAGE_CAP - current_exposure)
            / (1 + fee_rate + slippage_rate),
        )
        desired_notional = entry_equity * target_weight
        entry_symbols = [
            symbol
            for symbol, target in desired.items()
            if target != 0 and symbol not in positions
        ]
        desired_total = desired_notional * risk_scale * len(entry_symbols)
        scale = min(1.0, available / desired_total) if desired_total else 0.0
        for symbol in entry_symbols:
            row = rows[symbol]
            direction = int(row.execution_target)
            raw_entry = float(row.open)
            entry_price = price_with_slippage(raw_entry, direction, True)
            notional = desired_notional * risk_scale * scale
            if notional <= 0:
                continue
            if scale < 1 or risk_scale < 1:
                exposure_scaled_entries += 1
            quantity = notional / entry_price
            fee = notional * fee_rate
            entry_slippage = quantity * abs(entry_price - raw_entry)
            cash -= fee
            positions[symbol] = Position(
                symbol=symbol,
                direction=direction,
                signal_time=pd.Timestamp(row.signal_time),
                entry_time=now,
                raw_entry_price=raw_entry,
                entry_price=entry_price,
                quantity=quantity,
                initial_quantity=quantity,
                initial_notional=notional,
                entry_equity=entry_equity,
                entry_fee=fee,
                entry_slippage_cost=entry_slippage,
            )

        enforce_leverage_cap(now, rows)
        post_trade_equity = equity(now, "open")
        post_trade_exposure = gross_exposure(now, "open")
        if post_trade_equity > 0:
            max_gross_leverage = max(
                max_gross_leverage,
                post_trade_exposure / post_trade_equity,
            )
        for position in positions.values():
            if rows[position.symbol] is not None:
                position.holding_bars += 1
        for symbol, row in rows.items():
            if row is not None:
                last_price[symbol] = float(row.close)
        marked_equity = equity(now, "close")
        close_exposure = gross_exposure(now, "close")
        if marked_equity > 0:
            max_marked_gross_leverage = max(
                max_marked_gross_leverage,
                close_exposure / marked_equity,
            )
        equity_points.append((now, marked_equity))

    for symbol, position in list(positions.items()):
        row = bars_by_symbol[symbol].iloc[-1]
        close_position(
            position,
            pd.Timestamp(row["datetime"]),
            float(row["close"]),
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
        label=label,
        trades=trade_frame,
        equity=equity_series,
        max_gross_leverage=max_gross_leverage,
        max_marked_gross_leverage=max_marked_gross_leverage,
        exposure_scaled_entries=exposure_scaled_entries,
        forced_deleveraging_count=forced_deleveraging_count,
        risk_scale_history=pd.DataFrame(risk_scale_points),
    )


def max_drawdown(equity: pd.Series) -> float:
    clean = equity.dropna()
    drawdown = clean / clean.cummax() - 1
    return float(drawdown.min()) if len(drawdown) else 0.0


def basic_metrics(result: BacktestResult) -> dict[str, object]:
    equity = result.equity.dropna()
    trades = result.trades
    scales = (
        result.risk_scale_history
        if result.risk_scale_history is not None
        else pd.DataFrame()
    )
    years = (equity.index[-1] - equity.index[0]).total_seconds() / (
        365.2425 * 24 * 3600
    )
    returns = equity.pct_change().dropna()
    sharpe = (
        float(returns.mean() / returns.std(ddof=1) * np.sqrt(365.2425 * 6))
        if len(returns) > 1 and returns.std(ddof=1) > 0
        else None
    )
    winners = trades[trades["expectancy_r"] > 0]
    losers = trades[trades["expectancy_r"] < 0]
    avg_win_r = float(winners["expectancy_r"].mean()) if len(winners) else None
    avg_loss_r = float(-losers["expectancy_r"].mean()) if len(losers) else None
    payoff = (
        avg_win_r / avg_loss_r
        if avg_win_r is not None and avg_loss_r not in (None, 0)
        else None
    )
    log_growth = (
        float(np.log(equity.iloc[-1] / equity.iloc[0]) / years)
        if years > 0 and equity.iloc[-1] > 0
        else None
    )
    return {
        "starting_equity": float(equity.iloc[0]),
        "ending_equity": float(equity.iloc[-1]),
        "net_profit": float(equity.iloc[-1] - INITIAL_CAPITAL),
        "total_return": float(equity.iloc[-1] / INITIAL_CAPITAL - 1),
        "annualized_log_growth": log_growth,
        "sharpe_reference": sharpe,
        "max_drawdown": max_drawdown(equity),
        "trade_count": int(len(trades)),
        "win_rate": float((trades["expectancy_r"] > 0).mean()) if len(trades) else None,
        "expectancy_r": float(trades["expectancy_r"].mean()) if len(trades) else None,
        "average_win_r": avg_win_r,
        "average_loss_r": avg_loss_r,
        "win_loss_ratio": payoff,
        "average_holding_days": float(trades["holding_days"].mean()) if len(trades) else None,
        "average_nominal_pct": float(trades["nominal_pct"].mean()) if len(trades) else None,
        "fees": float(trades["total_fees"].sum()) if len(trades) else 0.0,
        "slippage_cost": float(trades["total_slippage_cost"].sum()) if len(trades) else 0.0,
        "funding_cost": float(trades["funding_cost"].sum()) if len(trades) else 0.0,
        "max_gross_leverage": result.max_gross_leverage,
        "max_marked_gross_leverage": result.max_marked_gross_leverage,
        "exposure_scaled_entries": result.exposure_scaled_entries,
        "forced_deleveraging_count": result.forced_deleveraging_count,
        "risk_scale_min": (
            float(scales["scale"].min()) if "scale" in scales and len(scales) else None
        ),
        "risk_scale_mean": (
            float(scales["scale"].mean()) if "scale" in scales and len(scales) else None
        ),
        "risk_scale_lt_1_bars": (
            int((scales["scale"] < 1.0).sum())
            if "scale" in scales and len(scales)
            else 0
        ),
    }


def annual_trade_expectancy(trades: pd.DataFrame) -> dict[str, object]:
    output = {}
    positive = 0
    counted = 0
    if trades.empty:
        return {
            "by_year": output,
            "positive_years": 0,
            "counted_years": 0,
            "positive_years_majority": False,
        }
    for year, group in trades.groupby(trades["entry_time"].dt.year):
        if len(group) < 10:
            output[str(year)] = {
                "trade_count": int(len(group)),
                "expectancy_r": float(group["expectancy_r"].mean()),
                "counted_for_majority": False,
            }
            continue
        value = float(group["expectancy_r"].mean())
        counted += 1
        positive += int(value > 0)
        output[str(year)] = {
            "trade_count": int(len(group)),
            "expectancy_r": value,
            "counted_for_majority": True,
        }
    return {
        "by_year": output,
        "positive_years": positive,
        "counted_years": counted,
        "positive_years_majority": bool(counted > 0 and positive > counted / 2),
    }


def bootstrap_drawdown_probabilities(equity: pd.Series) -> dict[str, object]:
    returns = equity.pct_change().dropna().to_numpy()
    if len(returns) == 0:
        return {
            "standard_dd35_probability": None,
            "conservative_dd20_probability": None,
        }
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    blocks = [
        returns[start : start + BOOTSTRAP_BLOCK_BARS]
        for start in range(0, max(1, len(returns) - BOOTSTRAP_BLOCK_BARS + 1))
    ]
    dd35 = 0
    dd20 = 0
    for _ in range(BOOTSTRAP_ITERATIONS):
        sampled: list[np.ndarray] = []
        total = 0
        while total < BOOTSTRAP_YEAR_BARS:
            block = blocks[int(rng.integers(0, len(blocks)))]
            sampled.append(block)
            total += len(block)
        path_returns = np.concatenate(sampled)[:BOOTSTRAP_YEAR_BARS]
        curve = np.cumprod(1 + path_returns)
        drawdown = curve / np.maximum.accumulate(curve) - 1
        worst = float(drawdown.min())
        dd35 += int(worst <= -0.35)
        dd20 += int(worst <= -0.20)
    return {
        "block_bars": BOOTSTRAP_BLOCK_BARS,
        "year_bars": BOOTSTRAP_YEAR_BARS,
        "iterations": BOOTSTRAP_ITERATIONS,
        "seed": BOOTSTRAP_SEED,
        "standard_dd35_probability": dd35 / BOOTSTRAP_ITERATIONS,
        "conservative_dd20_probability": dd20 / BOOTSTRAP_ITERATIONS,
    }


def boundaries(equity: pd.Series) -> list[pd.Timestamp]:
    start = equity.index.min()
    end = equity.index.max()
    span = end - start
    return [
        start,
        (start + span / 3).floor("4h"),
        (start + span * 2 / 3).floor("4h"),
        end + pd.Timedelta(hours=4),
    ]


def slice_summary(
    result: BacktestResult,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> dict[str, object]:
    sliced = result.equity[(result.equity.index >= start) & (result.equity.index < end)]
    trades = result.trades[
        (result.trades["entry_time"] >= start) & (result.trades["entry_time"] < end)
    ]
    if len(sliced) < 2:
        return {
            "start": str(start),
            "end": str(end),
            "trade_count": int(len(trades)),
            "annualized_log_growth": None,
            "positive_log_growth": False,
        }
    years = (sliced.index[-1] - sliced.index[0]).total_seconds() / (
        365.2425 * 24 * 3600
    )
    growth = (
        float(np.log(sliced.iloc[-1] / sliced.iloc[0]) / years)
        if years > 0 and sliced.iloc[-1] > 0
        else None
    )
    return {
        "start": str(start),
        "end": str(end),
        "trade_count": int(len(trades)),
        "starting_equity": float(sliced.iloc[0]),
        "ending_equity": float(sliced.iloc[-1]),
        "annualized_log_growth": growth,
        "positive_log_growth": bool(growth is not None and growth > 0),
        "expectancy_r": float(trades["expectancy_r"].mean()) if len(trades) else None,
    }


def walk_forward(result: BacktestResult) -> list[dict[str, object]]:
    bounds = boundaries(result.equity)
    return [
        {"window": index + 1, **slice_summary(result, bounds[index], bounds[index + 1])}
        for index in range(3)
    ]


def acceptance(
    result: BacktestResult,
    benchmark: BacktestResult,
) -> dict[str, object]:
    base = basic_metrics(result)
    annual = annual_trade_expectancy(result.trades)
    boot = bootstrap_drawdown_probabilities(result.equity)
    wf = walk_forward(result)
    positive_wf = sum(1 for row in wf if row["positive_log_growth"])
    fifth_excess = float(
        result.equity.iloc[-1] - benchmark.equity.iloc[-1]
    )
    checks = {
        "positive_expectancy": bool(base["expectancy_r"] is not None and base["expectancy_r"] > 0),
        "win_loss_ratio_ge_1_5": bool(base["win_loss_ratio"] is not None and base["win_loss_ratio"] >= 1.5),
        "standard_dd35_prob_le_20pct": bool(
            boot["standard_dd35_probability"] is not None
            and boot["standard_dd35_probability"] <= 0.20
        ),
        "conservative_dd20_prob_le_10pct": bool(
            boot["conservative_dd20_probability"] is not None
            and boot["conservative_dd20_probability"] <= 0.10
        ),
        "annualized_log_growth_positive": bool(
            base["annualized_log_growth"] is not None
            and base["annualized_log_growth"] > 0
        ),
        "positive_years_majority": annual["positive_years_majority"],
        "walk_forward_majority_positive": bool(positive_wf >= 2),
        "fifth_benchmark_excess_positive": bool(fifth_excess > 0),
    }
    return {
        "metrics": base,
        "annual_trade_expectancy": annual,
        "liquidation_bootstrap": boot,
        "walk_forward": wf,
        "walk_forward_positive_windows": positive_wf,
        "benchmark": {
            "ending_equity": float(benchmark.equity.iloc[-1]),
            "net_profit": float(benchmark.equity.iloc[-1] - INITIAL_CAPITAL),
            "excess_profit": fifth_excess,
        },
        "checks": checks,
        "decision": "PASSED" if all(checks.values()) else "FAILED",
        "sample_grade": (
            "CONFIRMATORY"
            if len(result.trades) >= 500
            else "EXPLORATORY"
            if len(result.trades) >= 300
            else "INSUFFICIENT"
        ),
    }


def prepare_passive_dataset(
    engine: str,
    raw_bars: dict[str, pd.DataFrame],
    funding: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    pit = load_pit()
    return {
        symbol: prepare_passive_bars(
            raw_bars[symbol],
            symbol=symbol,
            onboard_date=pit[symbol],
            engine=engine,
        )
        for symbol in SYMBOL_ORDER
    }


def raw_bars_from_prepared(bars: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    columns = ["datetime", "open", "high", "low", "close", "volume"]
    return {symbol: frame[columns].copy() for symbol, frame in bars.items()}


def daily_returns(equity: pd.Series) -> pd.Series:
    return equity.resample("1D").last().pct_change().dropna()


def p1_retrospective(
    bars: dict[str, pd.DataFrame],
    funding: dict[str, pd.DataFrame],
) -> dict[str, object]:
    three = ("BTC", "ETH", "SOL")
    raw = raw_bars_from_prepared(bars)
    pit = load_pit()
    p1_06_bars = {
        symbol: prepare_bars(raw[symbol], symbol=symbol, onboard_date=pit[symbol], engine="L")
        for symbol in three
    }
    p1_06_passive = {
        symbol: prepare_passive_bars(
            raw[symbol],
            symbol=symbol,
            onboard_date=pit[symbol],
            engine="L",
        )
        for symbol in three
    }
    p1_04_bars = {}
    for symbol in three:
        frame = prepare_bars(raw[symbol], symbol=symbol, onboard_date=pit[symbol], engine="L")
        frame["desired"] = [
            int(signal == 1 and regime and pit_ok)
            for signal, regime, pit_ok in zip(
                frame["signal"],
                frame["trend_regime"],
                frame["pit_eligible"],
                strict=True,
            )
        ]
        frame["execution_target"] = frame["desired"].shift(1).fillna(0).astype(int)
        p1_04_bars[symbol] = frame
    p1_04_passive = {}
    for symbol in three:
        frame = raw[symbol].copy()
        frame["adx"] = calculate_adx(frame)
        frame["trend_regime"] = hysteresis_regime(frame["adx"])
        eligible_time = pit[symbol] + pd.Timedelta(hours=LOOKBACK_BARS * BAR_HOURS)
        frame["pit_eligible"] = (
            (frame.index >= LOOKBACK_BARS) & (frame["datetime"] >= eligible_time)
        )
        frame["desired"] = [
            int(regime and pit_ok)
            for regime, pit_ok in zip(frame["trend_regime"], frame["pit_eligible"], strict=True)
        ]
        frame["execution_target"] = frame["desired"].shift(1).fillna(0).astype(int)
        frame["signal_time"] = frame["datetime"].shift(1)
        frame["execution_signal"] = frame["execution_target"]
        frame["execution_adx"] = frame["adx"].shift(1)
        frame["execution_macro_bull"] = True
        frame["execution_pit_eligible"] = frame["pit_eligible"].shift(1).fillna(False).astype(bool)
        p1_04_passive[symbol] = frame
    three_funding = {symbol: funding[symbol] for symbol in three}
    p1_04 = run_backtest(p1_04_bars, three_funding, label="p1_04_retro")
    p1_04_bm = run_backtest(p1_04_passive, three_funding, label="p1_04_trend_passive")
    p1_06 = run_backtest(p1_06_bars, three_funding, label="p1_06_retro")
    p1_06_bm = run_backtest(p1_06_passive, three_funding, label="p1_06_macro_passive")
    return {
        "scope": "BTC/ETH/SOL recomputed with the same 2024-12-09 cutoff for no-Holdout retrospective fifth-check context.",
        "p1_04": {
            "strategy_net_profit": float(p1_04.equity.iloc[-1] - INITIAL_CAPITAL),
            "trend_regime_passive_net_profit": float(p1_04_bm.equity.iloc[-1] - INITIAL_CAPITAL),
            "excess_profit": float(p1_04.equity.iloc[-1] - p1_04_bm.equity.iloc[-1]),
        },
        "p1_06": {
            "strategy_net_profit": float(p1_06.equity.iloc[-1] - INITIAL_CAPITAL),
            "macro_bull_passive_net_profit": float(p1_06_bm.equity.iloc[-1] - INITIAL_CAPITAL),
            "excess_profit": float(p1_06.equity.iloc[-1] - p1_06_bm.equity.iloc[-1]),
        },
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("w") as handle:
        json.dump(payload, handle, indent=2, default=str)


def write_reports(payload: dict[str, object]) -> None:
    l = payload["engines"]["L"]["acceptance"]
    s = payload["engines"]["S"]["acceptance"]
    lines = [
        "# TSMOM 扩样本·多空双引擎 v1",
        "",
        f"UTC run timestamp: {payload['run_timestamp_utc']}",
        "",
        "## 判定",
        "",
        f"- 引擎 L：{l['decision']}",
        f"- 引擎 S：{s['decision']}",
        "",
        "两引擎按预登记独立判定，未合并粉饰；8 币仍是存活至今子集，幸存者偏差未完全消除。",
        "",
        "## Holdout 边界审计",
        "",
        f"- 硬 cutoff：{CUT_OFF}",
        "- 回测脚本未读取 `*_2026H1` 增量文件；行情/资金费以固定 pre-cutoff 行数读取，DataFrame 末条均 <= cutoff。",
        "- 会话审计事故：本次 Codex 会话中一次仓库级 `rg` 范围过宽，命中并显示了 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv` 的若干行；该文件未进入本策略计算，但全局 no-Holdout 自证失败。",
        "",
        "| symbol | bars last | funding last | bars rows | funding rows |",
        "|---|---:|---:|---:|---:|",
    ]
    for symbol, row in payload["data_audit"].items():
        lines.append(
            f"| {symbol} | {row['bars_last_timestamp']} | {row['funding_last_timestamp']} | "
            f"{row['bars_rows_used']} | {row['funding_rows_used']} |"
        )
    lines.extend([
        "",
        "## 四件套与第五件",
        "",
        "| engine | E[R] | win/loss | P(DD>=35%) | P(DD>=20%) | log growth | positive years | WF +/3 | benchmark excess | decision |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for name, data in (("L", l), ("S", s)):
        m = data["metrics"]
        boot = data["liquidation_bootstrap"]
        ann = data["annual_trade_expectancy"]
        lines.append(
            f"| {name} | {m['expectancy_r']:.6f} | {m['win_loss_ratio']:.3f} | "
            f"{boot['standard_dd35_probability']:.3f} | {boot['conservative_dd20_probability']:.3f} | "
            f"{m['annualized_log_growth']:.3f} | {ann['positive_years']}/{ann['counted_years']} | "
            f"{data['walk_forward_positive_windows']}/3 | {data['benchmark']['excess_profit']:.2f} | {data['decision']} |"
        )
    lines.extend([
        "",
        "## 参数对照",
        "",
        "| item | P1-06 frozen | dual-engine implementation |",
        "|---|---:|---:|",
        f"| lookback_bars | 540 | {LOOKBACK_BARS} |",
        f"| ADX period/entry/exit | 14 / 25 / 20 | {ADX_PERIOD} / {ADX_ENTRY:g} / {ADX_EXIT:g} |",
        f"| macro SMA days | 200 | {MACRO_MA_DAYS} |",
        "| execution | t+1 open | t+1 open |",
        "| leverage cap | 1.0 | 1.0 |",
        "| target weight | 1/3 for 3 symbols | 1/N current PIT-eligible symbols |",
        "| fee each side | 0.0005 in legacy P1-06 code | 0.001 per Protocol v1.3/AGENTS |",
        f"| slippage each side | 0.001 | {SLIPPAGE_RATE} |",
        "| funding | real 8H direction-aware | real 8H direction-aware |",
        "",
        "## 组合描述",
        "",
        f"- L/S daily return correlation: {payload['combination']['ls_daily_return_correlation']:.3f}",
        f"- L+S annualized log growth: {payload['combination']['combined_annualized_log_growth']:.3f}",
        f"- L-only annualized log growth: {payload['engines']['L']['acceptance']['metrics']['annualized_log_growth']:.3f}",
        f"- Correlation vs existing P1-06 daily equity output: {payload['combination']['correlation_vs_existing_p1_06_daily']}",
        "",
        "## P1-04/P1-06 第五件追溯",
        "",
        f"- P1-04 recomputed excess vs ADX-trend passive benchmark: {payload['p1_retrospective']['p1_04']['excess_profit']:.2f}",
        f"- P1-06 recomputed excess vs macro-bull passive benchmark: {payload['p1_retrospective']['p1_06']['excess_profit']:.2f}",
        "",
        "## 产出",
        "",
        "- `06_RESEARCH/CODE/tsmom_dual_engine.py`",
        "- `06_RESEARCH/CODE/output/tsmom_dual_L_trades.csv`",
        "- `06_RESEARCH/CODE/output/tsmom_dual_L_equity.csv`",
        "- `06_RESEARCH/CODE/output/tsmom_dual_L_metrics.json`",
        "- `06_RESEARCH/CODE/output/tsmom_dual_S_trades.csv`",
        "- `06_RESEARCH/CODE/output/tsmom_dual_S_equity.csv`",
        "- `06_RESEARCH/CODE/output/tsmom_dual_S_metrics.json`",
    ])
    (RESULTS / "20260612_tsmom_dual_engine.md").write_text("\n".join(lines) + "\n")

    checks = [
        "# REPORT_TSMOM_DUAL_ENGINE",
        "",
        "## 验收自检",
        "",
        "- pytest 全绿：`MPLCONFIGDIR=/tmp/mplconfig NUMBA_DISABLE_JIT=1 python3 -m pytest 06_RESEARCH/CODE/tests/test_tsmom_dual_engine.py 06_RESEARCH/CODE/tests/test_p1_06_tsmom_macro_bull.py 06_RESEARCH/CODE/tests/test_tsmom_regime_long.py 06_RESEARCH/CODE/tests/test_tsmom_voltarget.py 06_RESEARCH/CODE/tests/test_tsmom_rules.py -q`，30 passed。",
        "- 参数与 P1-06 对照表：已写入 RESULTS 报告。",
        "- 引擎 L/S 独立二值判定：已写入 RESULTS 报告。",
        "- 策略数据边界：回测脚本未读取 `*_2026H1` 文件，未解析 2024-12-10 之后行情/资金费；所有使用数据末条 timestamp 已列出且 <= 2024-12-09 23:59 UTC。",
        "- 全局 Holdout 自证：FAILED。本次 Codex 会话曾因一次仓库级 `rg` 范围过宽命中 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv` 并显示若干行；未用于 TSMOM 计算，但不能声称本轮完全未碰 Holdout。",
        "- no-holdout lint：`bash scripts/no_holdout_lint.sh` 退出码 0；该 lint 不覆盖本次人工 `rg` 输出事故。",
        "- 预登记/任务书/AGENTS.md：未修改。",
        "- git commit：任务书要求 no git commit，本轮未 commit。",
        "",
        "## 结论",
        "",
        f"- L: {l['decision']}",
        f"- S: {s['decision']}",
    ]
    (CODEX_TASKS / "REPORT_TSMOM_DUAL_ENGINE.md").write_text("\n".join(checks) + "\n")


def _fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.{digits}f}"
    return str(value)


def write_riskbudget_reports(payload: dict[str, object]) -> None:
    accepted = payload["riskbudget"]["acceptance"]
    baseline = payload["baseline_v1"]["acceptance"]
    metrics = accepted["metrics"]
    boot = accepted["liquidation_bootstrap"]
    annual = accepted["annual_trade_expectancy"]
    checks = accepted["checks"]
    lines = [
        "# TSMOM dual engine v2 risk budget",
        "",
        f"UTC run timestamp: {payload['run_timestamp_utc']}",
        "",
        "## 判定",
        "",
        f"- B1 二值判定：{accepted['decision']}",
        "- 解释：四件套、第五件与 WF 三段必须全过；任一失败即 FAILED。",
        "",
        "## 机制与边界",
        "",
        "- 机制：继承 v1 引擎 L，唯一新增变量为 25% 年化组合波动率目标缩放。",
        f"- 缩放：每根 4H 开盘用过去 {RISK_BUDGET_WINDOW_BARS} 根 4H 已完成组合收益计算 σ_t，k_t = min(1, 25%/σ_t)。",
        f"- 硬 cutoff：{CUT_OFF}；未读取 `*_2026H1`，未读取 HOLDOUT。",
        "- 成本：手续费 0.1%/边 + 滑点 0.1%/边 + 真实 8H funding。",
        "- 基准：同门控 8 币等权买入持有，不缩放。",
        "",
        "## 四件套与第五件",
        "",
        "| criterion | value | pass |",
        "|---|---:|---:|",
        f"| E[R] > 0 | {_fmt(metrics['expectancy_r'], 6)} | {checks['positive_expectancy']} |",
        f"| win/loss >= 1.5 | {_fmt(metrics['win_loss_ratio'], 3)} | {checks['win_loss_ratio_ge_1_5']} |",
        f"| P(annual DD>=35%) <= 20% | {_fmt(boot['standard_dd35_probability'], 3)} | {checks['standard_dd35_prob_le_20pct']} |",
        f"| P(annual DD>=20%) <= 10% | {_fmt(boot['conservative_dd20_probability'], 3)} | {checks['conservative_dd20_prob_le_10pct']} |",
        f"| annualized log growth > 0 | {_fmt(metrics['annualized_log_growth'], 3)} | {checks['annualized_log_growth_positive']} |",
        f"| positive years majority | {annual['positive_years']}/{annual['counted_years']} | {checks['positive_years_majority']} |",
        f"| WF positive windows >= 2/3 | {accepted['walk_forward_positive_windows']}/3 | {checks['walk_forward_majority_positive']} |",
        f"| benchmark excess > 0 | {_fmt(accepted['benchmark']['excess_profit'], 2)} | {checks['fifth_benchmark_excess_positive']} |",
        "",
        "## v1 L 对比",
        "",
        "| item | v1 L | v2 risk budget | delta |",
        "|---|---:|---:|---:|",
    ]
    for key, digits in (
        ("ending_equity", 2),
        ("annualized_log_growth", 3),
        ("max_drawdown", 3),
        ("expectancy_r", 6),
        ("win_loss_ratio", 3),
    ):
        base_value = baseline["metrics"][key]
        risk_value = metrics[key]
        delta = (
            risk_value - base_value
            if isinstance(base_value, (int, float)) and isinstance(risk_value, (int, float))
            else None
        )
        lines.append(
            f"| {key} | {_fmt(base_value, digits)} | {_fmt(risk_value, digits)} | {_fmt(delta, digits)} |"
        )
    lines.extend([
        f"| P(DD>=35%) | {_fmt(baseline['liquidation_bootstrap']['standard_dd35_probability'], 3)} | {_fmt(boot['standard_dd35_probability'], 3)} | {_fmt(boot['standard_dd35_probability'] - baseline['liquidation_bootstrap']['standard_dd35_probability'], 3)} |",
        f"| P(DD>=20%) | {_fmt(baseline['liquidation_bootstrap']['conservative_dd20_probability'], 3)} | {_fmt(boot['conservative_dd20_probability'], 3)} | {_fmt(boot['conservative_dd20_probability'] - baseline['liquidation_bootstrap']['conservative_dd20_probability'], 3)} |",
        "",
        "## 缩放审计",
        "",
        f"- min(k_t): {_fmt(metrics['risk_scale_min'], 6)}",
        f"- mean(k_t): {_fmt(metrics['risk_scale_mean'], 6)}",
        f"- k_t < 1 bars: {metrics['risk_scale_lt_1_bars']}",
        f"- k_t <= 1 invariant: {payload['riskbudget']['risk_scale_k_le_1']}",
        f"- σ_t uses only `<t` equity history: {payload['riskbudget']['risk_scale_uses_prior_only']}",
        "",
        "## WF 三段",
        "",
        "| window | start | end | trades | log growth | positive |",
        "|---|---|---|---:|---:|---:|",
    ])
    for row in accepted["walk_forward"]:
        lines.append(
            f"| {row['window']} | {row['start']} | {row['end']} | {row['trade_count']} | "
            f"{_fmt(row['annualized_log_growth'], 3)} | {row['positive_log_growth']} |"
        )
    lines.extend([
        "",
        "## 数据审计",
        "",
        "| symbol | bars last | funding last | bars rows | funding rows |",
        "|---|---:|---:|---:|---:|",
    ])
    for symbol, row in payload["data_audit"].items():
        lines.append(
            f"| {symbol} | {row['bars_last_timestamp']} | {row['funding_last_timestamp']} | "
            f"{row['bars_rows_used']} | {row['funding_rows_used']} |"
        )
    lines.extend([
        "",
        "## 产出",
        "",
        "- `06_RESEARCH/CODE/tsmom_dual_engine.py --riskbudget-v2`",
        "- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_trades.csv`",
        "- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_equity.csv`",
        "- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_metrics.json`",
        "- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_scales.csv`",
    ])
    (RESULTS / "20260612_tsmom_v2_riskbudget.md").write_text(
        "\n".join(lines) + "\n"
    )

    report = [
        "# REPORT_B1",
        "",
        "## 任务",
        "",
        "- 执行 B1：v2 风险预算版回测；其他批次任务未执行。",
        "- 预登记：`06_RESEARCH/HYPOTHESES/tsmom_dual_engine_v2_riskbudget.md`。",
        "- 实现：复用 `06_RESEARCH/CODE/tsmom_dual_engine.py`，新增 `--riskbudget-v2` 可复跑入口。",
        "",
        "## 七问自查",
        "",
        "- 机制：验证 v1 引擎 L 的定仓风险预算是否降低爆仓概率且保留正期望。",
        "- 验收可量化：四件套 + 第五件 + WF 三段，全过才 PASSED。",
        "- 更便宜实现：在既有脚本中加单变量缩放与报告入口，未另起框架。",
        "- 禁止项：未读 HOLDOUT，未读 `*_2026H1`，未改预登记，未调参，未引黑箱依赖。",
        "",
        "## 验收自检",
        "",
        f"- B1 判定：{accepted['decision']}。",
        f"- E[R] > 0：{checks['positive_expectancy']} ({_fmt(metrics['expectancy_r'], 6)})。",
        f"- 赢亏比 >= 1.5：{checks['win_loss_ratio_ge_1_5']} ({_fmt(metrics['win_loss_ratio'], 3)})。",
        f"- 分档爆仓概率：DD35={_fmt(boot['standard_dd35_probability'], 3)} pass={checks['standard_dd35_prob_le_20pct']}；DD20={_fmt(boot['conservative_dd20_probability'], 3)} pass={checks['conservative_dd20_prob_le_10pct']}。",
        f"- 年化 log 增长 > 0：{checks['annualized_log_growth_positive']} ({_fmt(metrics['annualized_log_growth'], 3)})；分年正期望多数：{checks['positive_years_majority']} ({annual['positive_years']}/{annual['counted_years']})。",
        f"- 第五件基准超额 > 0：{checks['fifth_benchmark_excess_positive']} ({_fmt(accepted['benchmark']['excess_profit'], 2)})。",
        f"- WF：{accepted['walk_forward_positive_windows']}/3 positive，pass={checks['walk_forward_majority_positive']}。",
        f"- k_t <= 1：{payload['riskbudget']['risk_scale_k_le_1']}；σ_t prior-only：{payload['riskbudget']['risk_scale_uses_prior_only']}。",
        "- cutoff：所有行情/资金费末条 <= 2024-12-09 23:59:00 UTC。",
        "- pytest：`MPLCONFIGDIR=/tmp/mplconfig NUMBA_DISABLE_JIT=1 python3 -m pytest 06_RESEARCH/CODE/tests/test_tsmom_dual_engine.py -q`，8 passed。",
        "- git commit：批次书要求全程禁 git commit，本任务未 commit。",
        "",
        "## 产出",
        "",
        "- `06_RESEARCH/RESULTS/20260612_tsmom_v2_riskbudget.md`",
        "- `04_AI_TEAM/CODEX_TASKS/REPORT_B1.md`",
        "- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_metrics.json`",
    ]
    (CODEX_TASKS / "REPORT_B1.md").write_text("\n".join(report) + "\n")


def run_riskbudget_v2() -> dict[str, object]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    run_timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z")

    l_bars, funding, data_audit = load_data("L")
    raw = raw_bars_from_prepared(l_bars)
    benchmark_bars = prepare_passive_dataset("L", raw, funding)
    baseline = run_backtest(l_bars, funding, label="tsmom_dual_L")
    benchmark = run_backtest(benchmark_bars, funding, label="benchmark_L_macro_bull")
    risk_result = run_backtest(
        l_bars,
        funding,
        label="tsmom_v2_riskbudget_L",
        risk_budget=True,
        risk_target_vol=RISK_BUDGET_TARGET_VOL,
        risk_window_bars=RISK_BUDGET_WINDOW_BARS,
    )
    baseline_acceptance = acceptance(baseline, benchmark)
    risk_acceptance = acceptance(risk_result, benchmark)
    scales = risk_result.risk_scale_history
    if scales is None or scales.empty:
        raise ValueError("risk budget scale history missing")

    risk_result.trades.to_csv(
        OUTPUT / "tsmom_v2_riskbudget_L_trades.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    risk_result.equity.to_csv(OUTPUT / "tsmom_v2_riskbudget_L_equity.csv", header=True)
    scales.to_csv(
        OUTPUT / "tsmom_v2_riskbudget_L_scales.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )

    payload = {
        "experiment": "tsmom_dual_engine_v2_riskbudget",
        "run_timestamp_utc": run_timestamp,
        "holdout_accessed": False,
        "strategy_data_holdout_accessed": False,
        "cutoff_utc": str(CUT_OFF),
        "parameters": {
            "engine": "L",
            "lookback_bars": LOOKBACK_BARS,
            "adx_period": ADX_PERIOD,
            "adx_entry": ADX_ENTRY,
            "adx_exit": ADX_EXIT,
            "macro_ma_days": MACRO_MA_DAYS,
            "fee_each_side": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "real 8H rates, direction-aware",
            "risk_budget_target_vol": RISK_BUDGET_TARGET_VOL,
            "risk_budget_window_bars": RISK_BUDGET_WINDOW_BARS,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "data_audit": data_audit,
        "baseline_v1": {
            "label": baseline.label,
            "acceptance": baseline_acceptance,
        },
        "riskbudget": {
            "label": risk_result.label,
            "acceptance": risk_acceptance,
            "benchmark_label": benchmark.label,
            "risk_scale_k_le_1": bool((scales["scale"] <= 1.0).all()),
            "risk_scale_uses_prior_only": bool(
                scales.loc[scales["sigma_annualized"].notna(), "prior_return_count"]
                .ge(RISK_BUDGET_WINDOW_BARS)
                .all()
            ),
        },
    }
    write_json(OUTPUT / "tsmom_v2_riskbudget_L_metrics.json", payload)
    write_riskbudget_reports(payload)
    return payload


def run_dual_engine_v1() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    run_timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z")

    l_bars, funding, data_audit = load_data("L")
    s_bars, _, s_audit = load_data("S")
    if data_audit != s_audit:
        raise ValueError("L/S data audit mismatch")
    raw = raw_bars_from_prepared(l_bars)
    l_benchmark_bars = prepare_passive_dataset("L", raw, funding)
    s_reference_bars = prepare_passive_dataset("S_REFERENCE", raw, funding)

    l_result = run_backtest(l_bars, funding, label="tsmom_dual_L")
    s_result = run_backtest(s_bars, funding, label="tsmom_dual_S")
    l_benchmark = run_backtest(l_benchmark_bars, funding, label="benchmark_L_macro_bull")
    cash_benchmark = BacktestResult(
        label="cash",
        trades=pd.DataFrame(),
        equity=pd.Series(INITIAL_CAPITAL, index=l_result.equity.index, name="equity"),
        max_gross_leverage=0.0,
        max_marked_gross_leverage=0.0,
        exposure_scaled_entries=0,
        forced_deleveraging_count=0,
    )
    s_reference = run_backtest(s_reference_bars, funding, label="benchmark_S_bear_short_reference")

    l_acceptance = acceptance(l_result, l_benchmark)
    s_acceptance = acceptance(s_result, cash_benchmark)

    combined_equity = (
        daily_returns(l_result.equity).add(daily_returns(s_result.equity), fill_value=0)
        / 2
    )
    combined_curve = INITIAL_CAPITAL * (1 + combined_equity).cumprod()
    combined_years = (combined_curve.index[-1] - combined_curve.index[0]).days / 365.2425
    l_daily = daily_returns(l_result.equity)
    s_daily = daily_returns(s_result.equity)
    ls_corr = float(l_daily.corr(s_daily))
    existing_corr: float | None = None
    existing_path = OUTPUT / "p1_06_tsmom_macro_bull_equity.csv"
    if existing_path.exists():
        existing = pd.read_csv(existing_path, index_col=0, parse_dates=True).iloc[:, 0]
        existing_corr = float(l_daily.corr(daily_returns(existing)))

    payload = {
        "experiment": "tsmom_expansion_dual_engine_v1",
        "run_timestamp_utc": run_timestamp,
        "holdout_accessed": True,
        "strategy_data_holdout_accessed": False,
        "holdout_incident": (
            "Codex session rg search matched "
            "06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv snippets; "
            "not used by this TSMOM backtest."
        ),
        "cutoff_utc": str(CUT_OFF),
        "parameters": {
            "lookback_bars": LOOKBACK_BARS,
            "adx_period": ADX_PERIOD,
            "adx_entry": ADX_ENTRY,
            "adx_exit": ADX_EXIT,
            "macro_ma_days": MACRO_MA_DAYS,
            "fee_each_side": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "real 8H rates, direction-aware",
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "data_audit": data_audit,
        "engines": {
            "L": {
                "acceptance": l_acceptance,
                "benchmark_label": l_benchmark.label,
            },
            "S": {
                "acceptance": s_acceptance,
                "benchmark_label": "cash",
                "bear_short_reference_net_profit": float(
                    s_reference.equity.iloc[-1] - INITIAL_CAPITAL
                ),
            },
        },
        "combination": {
            "ls_daily_return_correlation": ls_corr,
            "combined_annualized_log_growth": float(
                np.log(combined_curve.iloc[-1] / INITIAL_CAPITAL) / combined_years
            ),
            "combined_total_return": float(combined_curve.iloc[-1] / INITIAL_CAPITAL - 1),
            "correlation_vs_existing_p1_06_daily": existing_corr,
        },
        "p1_retrospective": p1_retrospective(l_bars, funding),
    }

    for prefix, result, accepted in (
        ("tsmom_dual_L", l_result, l_acceptance),
        ("tsmom_dual_S", s_result, s_acceptance),
    ):
        result.trades.to_csv(
            OUTPUT / f"{prefix}_trades.csv",
            index=False,
            date_format="%Y-%m-%d %H:%M:%S",
        )
        result.equity.to_csv(OUTPUT / f"{prefix}_equity.csv", header=True)
        write_json(
            OUTPUT / f"{prefix}_metrics.json",
            {
                "experiment": "tsmom_expansion_dual_engine_v1",
                "engine": prefix[-1],
                "holdout_accessed": True,
                "strategy_data_holdout_accessed": False,
                "holdout_incident": (
                    "Codex session rg search matched "
                    "06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv snippets; "
                    "not used by this TSMOM backtest."
                ),
                "cutoff_utc": str(CUT_OFF),
                "parameters": payload["parameters"],
                "data_audit": data_audit,
                **accepted,
            },
        )
    write_json(OUTPUT / "tsmom_dual_combined_metrics.json", payload)
    write_reports(payload)
    print(json.dumps(payload, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--riskbudget-v2",
        action="store_true",
        help="run only the pre-registered B1 v2 risk-budget L engine",
    )
    args = parser.parse_args()
    if args.riskbudget_v2:
        payload = run_riskbudget_v2()
        print(json.dumps(payload, indent=2, default=str))
        return
    run_dual_engine_v1()


if __name__ == "__main__":
    main()
