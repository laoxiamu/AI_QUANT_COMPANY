#!/usr/bin/env python3
"""Phase 1 P1-02: volatility-targeted 90-day time-series momentum."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from v4_strategy_backtest import (
    INITIAL_CAPITAL,
    SYMBOL_CONFIG,
    SYMBOL_ORDER,
    metrics,
    slice_metrics,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
LOOKBACK_BARS = 540
FEE_RATE = 0.0005
SLIPPAGE_RATE = 0.001
VOL_WINDOW = 180
VOL_TARGET = 0.20
SINGLE_WEIGHT_CAP = 0.50
LEVERAGE_CAP = 1.0
ANNUALIZATION = np.sqrt(6 * 365)


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
class Result:
    trades: pd.DataFrame
    equity: pd.Series
    exposure: pd.DataFrame
    max_gross_leverage: float
    max_marked_gross_leverage: float
    exposure_scaled_entries: int
    forced_deleveraging_count: int
    rebalance_count: int
    gross_scale_count: int


def signal_from_prices(current_close: float, lagged_close: float) -> int:
    difference = current_close - lagged_close
    return 1 if difference > 0 else -1 if difference < 0 else 0


def execution_price(raw_price: float, direction: int, is_entry: bool) -> float:
    side = direction if is_entry else -direction
    return raw_price * (1 + side * SLIPPAGE_RATE)


def funding_payment(
    direction: int,
    quantity: float,
    mark_price: float,
    rate: float,
) -> float:
    """Positive return value is a cash cost; negative is funding income."""
    return direction * quantity * mark_price * rate


def volatility_weight(
    annualized_volatility: float,
    target: float = VOL_TARGET,
    cap: float = SINGLE_WEIGHT_CAP,
) -> float:
    if not np.isfinite(annualized_volatility) or annualized_volatility <= 0:
        return 0.0
    return float(np.clip(target / annualized_volatility, 0.0, cap))


def annualized_volatility(close: pd.Series) -> pd.Series:
    log_return = np.log(close).diff()
    return (
        log_return.rolling(VOL_WINDOW, min_periods=VOL_WINDOW).std()
        * ANNUALIZATION
    )


def scale_weights_to_gross_cap(
    weights: dict[str, float],
    gross_cap: float = LEVERAGE_CAP,
) -> dict[str, float]:
    gross = sum(abs(weight) for weight in weights.values())
    if gross <= gross_cap or gross == 0:
        return dict(weights)
    scale = gross_cap / gross
    return {symbol: weight * scale for symbol, weight in weights.items()}


def load_pre_holdout() -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
]:
    bars_by_symbol = {}
    funding_by_symbol = {}
    for symbol, config in SYMBOL_CONFIG.items():
        research_rows = config["expected_research_rows"]
        bars = pd.read_csv(
            config["bars"],
            parse_dates=["datetime"],
            nrows=research_rows,
        )
        if len(bars) != research_rows:
            raise ValueError(f"{symbol} research snapshot changed")
        if bars["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} Holdout boundary crossed")
        if bars["datetime"].duplicated().any():
            raise ValueError(f"{symbol} duplicate bars")
        if not bars["datetime"].is_monotonic_increasing:
            raise ValueError(f"{symbol} bars not ascending")
        bars["signal"] = np.sign(
            bars["close"] - bars["close"].shift(LOOKBACK_BARS)
        ).replace(0, np.nan).ffill().fillna(0).astype(int)
        bars["execution_signal"] = bars["signal"].shift(1).fillna(0).astype(int)
        bars["signal_time"] = bars["datetime"].shift(1)
        bars["annualized_volatility"] = annualized_volatility(bars["close"])
        bars["target_weight"] = bars["annualized_volatility"].map(
            volatility_weight
        )
        bars["execution_weight"] = bars["target_weight"].shift(1).fillna(0.0)
        bars["execution_volatility"] = bars[
            "annualized_volatility"
        ].shift(1)
        bars_by_symbol[symbol] = bars

        funding = pd.read_csv(
            config["funding"],
            parse_dates=["datetime"],
            nrows=config["funding_research_rows"],
        )
        if len(funding) != config["funding_research_rows"]:
            raise ValueError(f"{symbol} funding snapshot changed")
        if funding["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} funding Holdout boundary crossed")
        if funding["datetime"].duplicated().any():
            raise ValueError(f"{symbol} duplicate funding timestamps")
        funding["last_funding_rate"] = pd.to_numeric(
            funding["last_funding_rate"]
        )
        funding_by_symbol[symbol] = funding
    return bars_by_symbol, funding_by_symbol


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


def run_backtest(
    bars_by_symbol: dict[str, pd.DataFrame],
    funding_by_symbol: dict[str, pd.DataFrame],
    *,
    include_fees: bool,
    include_slippage: bool,
    include_funding: bool,
    symbols: tuple[str, ...] = SYMBOL_ORDER,
) -> Result:
    common_end = min(
        pd.Timestamp(bars_by_symbol[symbol]["datetime"].max())
        for symbol in symbols
    )
    selected = {
        symbol: bars_by_symbol[symbol][
            bars_by_symbol[symbol]["datetime"] <= common_end
        ].reset_index(drop=True)
        for symbol in symbols
    }
    timeline, bar_maps = _maps(selected)
    funding_maps = {
        symbol: {
            row.datetime: float(row.last_funding_rate)
            for row in funding_by_symbol[symbol].itertuples(index=False)
        }
        for symbol in symbols
    }
    fee_rate = FEE_RATE if include_fees else 0.0
    slippage_rate = SLIPPAGE_RATE if include_slippage else 0.0

    cash = INITIAL_CAPITAL
    positions: dict[str, Position] = {}
    last_price: dict[str, float] = {}
    trades: list[dict[str, object]] = []
    equity_points: list[tuple[pd.Timestamp, float]] = []
    exposure_points: list[dict[str, object]] = []
    max_gross_leverage = 0.0
    max_marked_gross_leverage = 0.0
    exposure_scaled_entries = 0
    forced_deleveraging_count = 0
    rebalance_count = 0
    gross_scale_count = 0

    def price_with_slippage(raw: float, direction: int, is_entry: bool) -> float:
        side = direction if is_entry else -direction
        return raw * (1 + side * slippage_rate)

    def equity(now: pd.Timestamp, field: str) -> float:
        value = cash
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            value += (
                position.direction
                * position.quantity
                * (mark - position.entry_price)
            )
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
        raw_price: float,
        reason: str,
    ) -> None:
        nonlocal cash
        exit_price = price_with_slippage(
            raw_price, position.direction, is_entry=False
        )
        gross_pnl = (
            position.direction
            * position.quantity
            * (exit_price - position.entry_price)
        )
        exit_notional = position.quantity * exit_price
        exit_fee = exit_notional * fee_rate
        exit_slippage = position.quantity * abs(exit_price - raw_price)
        cash += gross_pnl - exit_fee
        total_gross_pnl = position.partial_gross_pnl + gross_pnl
        total_exit_fee = position.partial_exit_fee + exit_fee
        total_exit_slippage = (
            position.partial_exit_slippage_cost + exit_slippage
        )
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
                "gross_pnl": total_gross_pnl
                + position.entry_slippage_cost
                + total_exit_slippage,
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

    def reduce_position(
        position: Position,
        now: pd.Timestamp,
        raw_price: float,
        removed_quantity: float,
    ) -> None:
        nonlocal cash
        exit_price = price_with_slippage(
            raw_price,
            position.direction,
            is_entry=False,
        )
        gross_pnl = (
            position.direction
            * removed_quantity
            * (exit_price - position.entry_price)
        )
        exit_fee = removed_quantity * exit_price * fee_rate
        exit_slippage = removed_quantity * abs(exit_price - raw_price)
        cash += gross_pnl - exit_fee
        position.quantity -= removed_quantity
        position.partial_gross_pnl += gross_pnl
        position.partial_exit_fee += exit_fee
        position.partial_exit_slippage_cost += exit_slippage

    def increase_position(
        position: Position,
        raw_price: float,
        added_quantity: float,
    ) -> None:
        nonlocal cash
        entry_price = price_with_slippage(
            raw_price,
            position.direction,
            is_entry=True,
        )
        added_notional = added_quantity * entry_price
        entry_fee = added_notional * fee_rate
        entry_slippage = added_quantity * abs(entry_price - raw_price)
        old_quantity = position.quantity
        position.entry_price = (
            position.entry_price * old_quantity
            + entry_price * added_quantity
        ) / (old_quantity + added_quantity)
        position.quantity += added_quantity
        position.initial_quantity += added_quantity
        position.initial_notional += added_notional
        position.entry_fee += entry_fee
        position.entry_slippage_cost += entry_slippage
        cash -= entry_fee

    def enforce_leverage_cap(
        now: pd.Timestamp,
        rows: dict[str, object],
    ) -> None:
        nonlocal cash, forced_deleveraging_count
        current_equity = equity(now, "open")
        current_exposure = gross_exposure(now, "open")
        if (
            not positions
            or current_equity <= 0
            or current_exposure <= current_equity * LEVERAGE_CAP * (1 + 1e-10)
        ):
            return
        cost_rate = fee_rate + slippage_rate
        numerator = (
            current_equity * LEVERAGE_CAP
            - current_exposure * cost_rate
        )
        denominator = current_exposure * (1 - cost_rate)
        scale = min(1.0, max(0.0, numerator / denominator))
        for symbol, position in positions.items():
            raw_price = float(rows[symbol].open)
            removed_quantity = position.quantity * (1 - scale)
            if removed_quantity <= 0:
                continue
            reduce_position(position, now, raw_price, removed_quantity)
        forced_deleveraging_count += 1

    for now in timeline:
        rows = {symbol: bar_maps[symbol].get(now) for symbol in symbols}
        for symbol, row in rows.items():
            if row is not None:
                last_price[symbol] = float(row.open)

        # Existing positions settle funding before any t+1-open signal change.
        if include_funding:
            for symbol, position in positions.items():
                rate = funding_maps[symbol].get(now)
                if rate is None:
                    continue
                row = rows[symbol]
                mark = float(row.open) if row is not None else last_price[symbol]
                payment = funding_payment(
                    position.direction, position.quantity, mark, rate
                )
                cash -= payment
                position.funding_cost += payment

        desired = {}
        raw_weights = {}
        for symbol, row in rows.items():
            if row is None:
                continue
            desired[symbol] = int(row.execution_signal)
            raw_weights[symbol] = (
                float(row.execution_weight) if desired[symbol] != 0 else 0.0
            )
        target_weights = scale_weights_to_gross_cap(raw_weights)
        if sum(raw_weights.values()) > LEVERAGE_CAP + 1e-12:
            gross_scale_count += 1

        changes = [
            symbol
            for symbol, target in desired.items()
            if target != 0
            and (
                symbol not in positions
                or positions[symbol].direction != target
            )
        ]
        for symbol in changes:
            if symbol in positions:
                close_position(
                    positions[symbol],
                    now,
                    float(rows[symbol].open),
                    "FLIP",
                )
                del positions[symbol]

        pre_trade_equity = equity(now, "open")
        for symbol in symbols:
            row = rows[symbol]
            if row is None:
                continue
            direction = desired[symbol]
            target_notional = (
                pre_trade_equity * target_weights.get(symbol, 0.0)
            )
            raw_price = float(row.open)
            target_quantity = (
                target_notional / raw_price if target_notional > 0 else 0.0
            )
            if direction == 0 or target_quantity <= 0:
                continue
            if symbol not in positions:
                entry_price = price_with_slippage(
                    raw_price,
                    direction,
                    is_entry=True,
                )
                quantity = target_notional / entry_price
                fee = target_notional * fee_rate
                entry_slippage = quantity * abs(entry_price - raw_price)
                cash -= fee
                positions[symbol] = Position(
                    symbol=symbol,
                    direction=direction,
                    signal_time=pd.Timestamp(row.signal_time),
                    entry_time=now,
                    raw_entry_price=raw_price,
                    entry_price=entry_price,
                    quantity=quantity,
                    initial_quantity=quantity,
                    initial_notional=target_notional,
                    entry_equity=pre_trade_equity,
                    entry_fee=fee,
                    entry_slippage_cost=entry_slippage,
                )
                continue
            position = positions[symbol]
            delta = target_quantity - position.quantity
            tolerance = max(1e-12, target_quantity * 1e-10)
            if abs(delta) <= tolerance:
                continue
            rebalance_count += 1
            if delta > 0:
                increase_position(position, raw_price, delta)
            else:
                reduce_position(position, now, raw_price, -delta)

        enforce_leverage_cap(now, rows)
        post_trade_equity = equity(now, "open")
        post_trade_exposure = gross_exposure(now, "open")
        if post_trade_equity > 0:
            max_gross_leverage = max(
                max_gross_leverage,
                post_trade_exposure / post_trade_equity,
            )
        exposure_row: dict[str, object] = {
            "datetime": now,
            "equity_open": post_trade_equity,
            "gross_open": (
                post_trade_exposure / post_trade_equity
                if post_trade_equity > 0
                else 0.0
            ),
            "raw_target_gross": sum(raw_weights.values()),
            "target_gross": sum(target_weights.values()),
            "gross_scaled": sum(raw_weights.values()) > LEVERAGE_CAP + 1e-12,
        }
        for symbol in symbols:
            symbol_row = rows[symbol]
            if symbol_row is None:
                exposure_row[f"{symbol}_target_weight"] = 0.0
                exposure_row[f"{symbol}_raw_target_weight"] = 0.0
                exposure_row[f"{symbol}_actual_weight"] = 0.0
                exposure_row[f"{symbol}_execution_volatility"] = np.nan
                continue
            raw_price = float(symbol_row.open)
            actual_notional = (
                positions[symbol].quantity * raw_price
                if symbol in positions
                else 0.0
            )
            exposure_row[f"{symbol}_target_weight"] = target_weights.get(
                symbol, 0.0
            )
            exposure_row[f"{symbol}_raw_target_weight"] = raw_weights.get(
                symbol, 0.0
            )
            exposure_row[f"{symbol}_actual_weight"] = (
                actual_notional / post_trade_equity
                if post_trade_equity > 0
                else 0.0
            )
            exposure_row[f"{symbol}_execution_volatility"] = float(
                symbol_row.execution_volatility
            )
        exposure_points.append(exposure_row)

        for symbol, position in positions.items():
            if rows[symbol] is not None:
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
        row = selected[symbol].iloc[-1]
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
    exposure_frame = pd.DataFrame(exposure_points).set_index("datetime")
    return Result(
        trades=trade_frame,
        equity=equity_series,
        exposure=exposure_frame,
        max_gross_leverage=max_gross_leverage,
        max_marked_gross_leverage=max_marked_gross_leverage,
        exposure_scaled_entries=exposure_scaled_entries,
        forced_deleveraging_count=forced_deleveraging_count,
        rebalance_count=rebalance_count,
        gross_scale_count=gross_scale_count,
    )


def summarize(result: Result) -> dict[str, object]:
    base = metrics(result.equity, result.trades, starting_equity=INITIAL_CAPITAL)
    trades = result.trades
    years = (
        (result.equity.index[-1] - result.equity.index[0]).total_seconds()
        / (365.2425 * 24 * 3600)
    )
    exposure = result.exposure
    active_rows = exposure[exposure["target_gross"] > 0]
    weight_columns = [
        column
        for column in exposure.columns
        if column.endswith("_actual_weight")
    ]
    raw_weight_columns = [
        column
        for column in exposure.columns
        if column.endswith("_raw_target_weight")
    ]
    raw_weight_values = active_rows[raw_weight_columns].stack()
    positive_raw_weights = raw_weight_values[raw_weight_values > 0]
    base.update(
        {
            "average_holding_days": float(trades["holding_days"].mean()),
            "segments_per_year": float(len(trades) / years),
            "segments_per_year_per_symbol": float(
                len(trades) / years / len(SYMBOL_ORDER)
            ),
            "average_nominal_pct": float(trades["nominal_pct"].mean()),
            "long_trade_count": int((trades["direction"] == 1).sum()),
            "short_trade_count": int((trades["direction"] == -1).sum()),
            "long_net_pnl": float(
                trades.loc[trades["direction"] == 1, "net_pnl"].sum()
            ),
            "short_net_pnl": float(
                trades.loc[trades["direction"] == -1, "net_pnl"].sum()
            ),
            "fees": float(trades["total_fees"].sum()),
            "slippage_cost": float(trades["total_slippage_cost"].sum()),
            "funding_cost": float(trades["funding_cost"].sum()),
            "total_costs": float(
                trades["total_fees"].sum()
                + trades["total_slippage_cost"].sum()
                + trades["funding_cost"].sum()
            ),
            "max_gross_leverage": result.max_gross_leverage,
            "max_marked_gross_leverage": result.max_marked_gross_leverage,
            "exposure_scaled_entries": result.exposure_scaled_entries,
            "forced_deleveraging_count": result.forced_deleveraging_count,
            "rebalance_count": result.rebalance_count,
            "gross_scale_count": result.gross_scale_count,
            "gross_scale_frequency": (
                float(active_rows["gross_scaled"].mean())
                if len(active_rows)
                else 0.0
            ),
            "volatility_shrink_frequency": (
                float((positive_raw_weights < SINGLE_WEIGHT_CAP).mean())
                if len(positive_raw_weights)
                else 0.0
            ),
            "average_gross_exposure": (
                float(active_rows["gross_open"].mean())
                if len(active_rows)
                else 0.0
            ),
            "peak_gross_exposure": float(exposure["gross_open"].max()),
            "average_target_gross": (
                float(active_rows["target_gross"].mean())
                if len(active_rows)
                else 0.0
            ),
            "average_actual_weights": {
                column.removesuffix("_actual_weight"): float(
                    active_rows[column].mean()
                )
                for column in weight_columns
            },
            "average_target_weights": {
                symbol: float(
                    active_rows[f"{symbol}_target_weight"].mean()
                )
                for symbol in {
                    column.removesuffix("_actual_weight")
                    for column in weight_columns
                }
            },
            "volatility_shrink_frequency_by_symbol": {
                symbol: float(
                    (
                        active_rows[f"{symbol}_raw_target_weight"]
                        .loc[
                            active_rows[f"{symbol}_raw_target_weight"] > 0
                        ]
                        < SINGLE_WEIGHT_CAP
                    ).mean()
                )
                for symbol in {
                    column.removesuffix("_actual_weight")
                    for column in weight_columns
                }
            },
        }
    )
    return base


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


def report_payload(
    bars: dict[str, pd.DataFrame],
    funding: dict[str, pd.DataFrame],
) -> tuple[Result, dict[str, object]]:
    net = run_backtest(
        bars,
        funding,
        include_fees=True,
        include_slippage=True,
        include_funding=True,
    )
    gross = run_backtest(
        bars,
        funding,
        include_fees=False,
        include_slippage=False,
        include_funding=False,
    )
    bounds = boundaries(net.equity)
    by_symbol = {}
    for symbol in SYMBOL_ORDER:
        result = run_backtest(
            bars,
            funding,
            include_fees=True,
            include_slippage=True,
            include_funding=True,
            symbols=(symbol,),
        )
        by_symbol[symbol] = summarize(result)
    payload = {
        "portfolio": summarize(net),
        "gross_zero_cost": summarize(gross),
        "by_symbol": by_symbol,
        "walk_forward": [
            {
                "window": index + 1,
                **slice_metrics(
                    net.equity,
                    net.trades,
                    bounds[index],
                    bounds[index + 1],
                ),
            }
            for index in range(3)
        ],
        "period_2022": slice_metrics(
            net.equity,
            net.trades,
            pd.Timestamp("2022-01-01"),
            pd.Timestamp("2023-01-01"),
        ),
    }
    main = payload["portfolio"]
    gross_main = payload["gross_zero_cost"]
    payload["strategy_passed"] = bool(
        main["sharpe"] > 1.0 and abs(main["max_drawdown"]) < 0.25
    )
    payload["cost_limited"] = bool(
        not payload["strategy_passed"] and gross_main["sharpe"] > 1.0
    )
    return net, payload


def plot_equity(equity: pd.Series) -> None:
    figure, axis = plt.subplots(figsize=(13, 6))
    axis.plot(equity.index, equity.values, linewidth=1.2)
    axis.axhline(INITIAL_CAPITAL, color="black", linewidth=0.7, alpha=0.5)
    axis.set_title("P1-02 TSMOM Volatility Target")
    axis.set_xlabel("UTC time")
    axis.set_ylabel("Equity (USDT)")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    figure.savefig(OUTPUT / "p1_02_tsmom_voltarget_equity_curve.png", dpi=160)
    plt.close(figure)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bars, funding = load_pre_holdout()
    result, payload = report_payload(bars, funding)
    output = {
        "experiment": "v6_tsmom_trend_v2",
        "holdout_accessed": False,
        "parameters": {
            "lookback_bars": LOOKBACK_BARS,
            "lookback_days": 90,
            "signal": "sign(close[t] - close[t-540])",
            "execution": "signal at t close, execute t+1 open",
            "volatility_window_bars": VOL_WINDOW,
            "volatility_target": VOL_TARGET,
            "single_weight_cap": SINGLE_WEIGHT_CAP,
            "leverage_cap": LEVERAGE_CAP,
            "rebalance_policy": (
                "direction changes only on signal flip; position size follows "
                "prior-close volatility target at each 4H open"
            ),
            "leverage_audit": (
                "cap enforced at each 4H open; marked leverage may drift "
                "within the following bar before the next risk-cap check"
            ),
            "fee_each_side": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "real historical 8H rates, direction-aware",
            "missing_funding_before_first_record": "zero/no settlement record",
        },
        **payload,
    }
    result.trades.to_csv(
        OUTPUT / "p1_02_tsmom_voltarget_trades.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    result.equity.to_csv(
        OUTPUT / "p1_02_tsmom_voltarget_equity.csv",
        header=True,
    )
    with (OUTPUT / "p1_02_tsmom_voltarget_metrics.json").open("w") as handle:
        json.dump(output, handle, indent=2, default=str)
    plot_equity(result.equity)
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
