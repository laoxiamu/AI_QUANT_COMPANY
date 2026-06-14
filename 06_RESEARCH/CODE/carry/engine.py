"""Stateful single-symbol delta-neutral carry engine."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from carry.config import EngineConfig
from carry.trigger import build_refractory_schedule


@dataclass(frozen=True)
class BacktestResult:
    timeline: pd.DataFrame
    events: pd.DataFrame
    summary: dict[str, float | int | bool]
    initial_capital: float

    @property
    def event_counts(self) -> dict[str, int]:
        if self.events.empty:
            return {"buffer_breach": 0, "liquidation": 0, "rebalance": 0}
        counts = self.events["event_type"].value_counts()
        return {
            name: int(counts.get(name, 0))
            for name in ("buffer_breach", "liquidation", "rebalance")
        }


@dataclass(frozen=True)
class _MarginAction:
    spot_qty: float
    perp_qty: float
    margin_equity: float
    cost: float
    liquidated: bool
    event: dict[str, object] | None


def _apply_margin_policy(
    *,
    timestamp: pd.Timestamp,
    spot_qty: float,
    perp_qty: float,
    spot_price: float,
    mark_price: float,
    margin_equity: float,
    config: EngineConfig,
) -> _MarginAction:
    if perp_qty <= 0:
        return _MarginAction(
            spot_qty,
            perp_qty,
            margin_equity,
            0.0,
            False,
            None,
        )
    perp_notional = perp_qty * mark_price
    health = margin_health(
        margin_equity,
        perp_notional,
        config.minimum_maintenance_margin_rate,
        buffer_multiple=config.maintenance_buffer_multiple,
    )
    if health == "healthy":
        return _MarginAction(
            spot_qty,
            perp_qty,
            margin_equity,
            0.0,
            False,
            None,
        )
    if health == "liquidation":
        cost = config.costs.trade_cost(
            spot_turnover=0.0,
            perp_turnover=perp_notional,
            event=True,
        ).total
        updated_margin = margin_equity - cost
        return _MarginAction(
            spot_qty,
            0.0,
            updated_margin,
            cost,
            True,
            {
                "timestamp": timestamp,
                "event_type": "liquidation",
                "margin_equity": updated_margin,
                "mark_notional": perp_notional,
            },
        )

    maximum_buffered_notional = max(
        margin_equity
        / (
            config.maintenance_buffer_multiple
            * config.minimum_maintenance_margin_rate
        ),
        0.0,
    )
    reduction = min(maximum_buffered_notional / perp_notional, 1.0)
    new_spot_qty = spot_qty * reduction
    new_perp_qty = perp_qty * reduction
    spot_turnover = abs(new_spot_qty - spot_qty) * spot_price
    perp_turnover = abs(new_perp_qty - perp_qty) * mark_price
    cost = config.costs.trade_cost(
        spot_turnover=spot_turnover,
        perp_turnover=perp_turnover,
    ).total
    updated_margin = margin_equity - perp_turnover * (
        config.costs.fee_rate + config.costs.slippage_rate
    )
    return _MarginAction(
        new_spot_qty,
        new_perp_qty,
        updated_margin,
        cost,
        False,
        {
            "timestamp": timestamp,
            "event_type": "buffer_breach",
            "margin_equity": margin_equity,
            "mark_notional": perp_notional,
        },
    )


def funding_cashflow(short_notional: float, funding_rate: float) -> float:
    """Positive funding is received by the short perpetual leg."""
    if short_notional < 0:
        raise ValueError("short_notional must be non-negative")
    return short_notional * funding_rate


def delta_drift_ratio(
    spot_notional: float,
    perp_notional: float,
    reference_notional: float,
) -> float:
    if reference_notional <= 0:
        raise ValueError("reference_notional must be positive")
    return abs(spot_notional - perp_notional) / reference_notional


def should_rebalance(drift_ratio: float, *, threshold: float = 0.05) -> bool:
    return drift_ratio > threshold


def margin_health(
    margin_equity: float,
    mark_notional: float,
    minimum_maintenance_margin_rate: float,
    *,
    buffer_multiple: float = 3.0,
) -> str:
    minimum = mark_notional * minimum_maintenance_margin_rate
    if margin_equity < minimum:
        return "liquidation"
    if margin_equity < minimum * buffer_multiple:
        return "buffer_breach"
    return "healthy"


def _normalize_marks(marks: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "mark_price"}
    missing = required.difference(marks.columns)
    if missing:
        raise ValueError(f"marks missing columns: {sorted(missing)}")
    frame = marks.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["mark_price"] = pd.to_numeric(frame["mark_price"], errors="raise")
    if "spot_price" not in frame:
        frame["spot_price"] = frame["mark_price"]
    frame["spot_price"] = pd.to_numeric(frame["spot_price"], errors="raise")
    frame = frame.sort_values("timestamp").drop_duplicates(
        "timestamp",
        keep="last",
    )
    if frame.empty or (frame[["spot_price", "mark_price"]] <= 0).any().any():
        raise ValueError("marks must contain positive prices")
    return frame.reset_index(drop=True)


def _normalize_funding(funding: pd.DataFrame) -> pd.Series:
    if funding.empty:
        return pd.Series(dtype=float)
    required = {"timestamp", "funding_rate"}
    missing = required.difference(funding.columns)
    if missing:
        raise ValueError(f"funding missing columns: {sorted(missing)}")
    frame = funding.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["funding_rate"] = pd.to_numeric(
        frame["funding_rate"],
        errors="raise",
    )
    return frame.groupby("timestamp", sort=True)["funding_rate"].sum()


def _normalize_scales(
    timestamps: pd.DatetimeIndex,
    target_scale: pd.Series | None,
) -> pd.Series:
    if target_scale is None:
        return pd.Series(1.0, index=timestamps)
    scales = target_scale.copy()
    if not isinstance(scales.index, pd.DatetimeIndex):
        raise TypeError("target_scale must use a DatetimeIndex")
    if scales.index.tz is None:
        scales.index = scales.index.tz_localize("UTC")
    else:
        scales.index = scales.index.tz_convert("UTC")
    scales = scales.sort_index().reindex(timestamps, method="ffill").fillna(1.0)
    if ((scales <= 0) | (scales > 1)).any():
        raise ValueError("target scales must be in (0, 1]")
    return scales.astype(float)


def run_symbol_backtest(
    marks: pd.DataFrame,
    funding: pd.DataFrame,
    config: EngineConfig,
    *,
    target_scale: pd.Series | None = None,
) -> BacktestResult:
    """Run an auditable isolated-margin long-spot/short-perp simulation."""
    price = _normalize_marks(marks)
    funding_by_time = _normalize_funding(funding)
    timestamps = pd.DatetimeIndex(price["timestamp"])
    scales = _normalize_scales(timestamps, target_scale)

    first = price.iloc[0]
    opening_notional = config.base_notional * float(scales.iloc[0])
    opening = config.costs.trade_cost(
        spot_turnover=opening_notional,
        perp_turnover=opening_notional,
    )
    opening_basis = config.costs.basis_cost(
        notional=opening_notional,
        entry_basis_rate=config.entry_basis_rate,
    )
    full_opening = config.costs.trade_cost(
        spot_turnover=config.base_notional,
        perp_turnover=config.base_notional,
    )
    full_opening_basis = config.costs.basis_cost(
        notional=config.base_notional,
        entry_basis_rate=config.entry_basis_rate,
    )
    spot_open_cost = opening_notional * (
        config.costs.fee_rate + config.costs.slippage_rate
    )
    perp_open_cost = spot_open_cost
    spot_qty = opening_notional / first["spot_price"]
    perp_qty = opening_notional / first["mark_price"]
    initial_margin = config.base_notional / config.leverage + perp_open_cost
    initial_capital = (
        config.base_notional
        + config.base_notional / config.leverage
        + full_opening.total
        + full_opening_basis
    )
    margin_equity = initial_margin
    cumulative_pnl = 0.0
    total_funding = 0.0
    total_cost = 0.0
    liquidated = False
    events: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []

    opening_cost = opening.total + opening_basis
    cumulative_pnl -= opening_cost
    margin_equity -= perp_open_cost
    total_cost += opening_cost

    previous_spot = float(first["spot_price"])
    previous_mark = float(first["mark_price"])
    previous_scale = float(scales.iloc[0])

    for row_index, current in price.iterrows():
        timestamp = current["timestamp"]
        spot_price = float(current["spot_price"])
        mark_price = float(current["mark_price"])
        price_pnl = 0.0
        funding_pnl = 0.0
        trading_cost = opening_cost if row_index == 0 else 0.0

        if row_index > 0:
            spot_pnl = spot_qty * (spot_price - previous_spot)
            perp_pnl = perp_qty * (previous_mark - mark_price)
            price_pnl = spot_pnl + perp_pnl
            cumulative_pnl += price_pnl
            margin_equity += perp_pnl

            if not liquidated and perp_qty > 0:
                action = _apply_margin_policy(
                    timestamp=timestamp,
                    spot_qty=spot_qty,
                    perp_qty=perp_qty,
                    spot_price=spot_price,
                    mark_price=mark_price,
                    margin_equity=margin_equity,
                    config=config,
                )
                spot_qty = action.spot_qty
                perp_qty = action.perp_qty
                margin_equity = action.margin_equity
                cumulative_pnl -= action.cost
                total_cost += action.cost
                trading_cost += action.cost
                liquidated = action.liquidated
                if action.event is not None:
                    events.append(action.event)

            rate = float(funding_by_time.get(timestamp, 0.0))
            if not liquidated and perp_qty > 0 and rate != 0:
                funding_pnl = funding_cashflow(perp_qty * mark_price, rate)
                cumulative_pnl += funding_pnl
                margin_equity += funding_pnl
                total_funding += funding_pnl
                if funding_pnl < 0:
                    action = _apply_margin_policy(
                        timestamp=timestamp,
                        spot_qty=spot_qty,
                        perp_qty=perp_qty,
                        spot_price=spot_price,
                        mark_price=mark_price,
                        margin_equity=margin_equity,
                        config=config,
                    )
                    spot_qty = action.spot_qty
                    perp_qty = action.perp_qty
                    margin_equity = action.margin_equity
                    cumulative_pnl -= action.cost
                    total_cost += action.cost
                    trading_cost += action.cost
                    liquidated = action.liquidated
                    if action.event is not None:
                        events.append(action.event)

            requested_scale = float(scales.loc[timestamp])
            if not liquidated:
                if not np.isclose(requested_scale, previous_scale):
                    leverage_cap = max(margin_equity, 0.0) * config.leverage
                    buffer_cap = max(margin_equity, 0.0) / (
                        config.maintenance_buffer_multiple
                        * config.minimum_maintenance_margin_rate
                    )
                    requested_notional = min(
                        config.base_notional * requested_scale,
                        leverage_cap,
                        buffer_cap,
                    )
                    requested_spot_qty = requested_notional / spot_price
                    requested_perp_qty = requested_notional / mark_price
                    spot_turnover = (
                        abs(requested_spot_qty - spot_qty) * spot_price
                    )
                    perp_turnover = (
                        abs(requested_perp_qty - perp_qty) * mark_price
                    )
                    resize = config.costs.trade_cost(
                        spot_turnover=spot_turnover,
                        perp_turnover=perp_turnover,
                    )
                    cumulative_pnl -= resize.total
                    margin_equity -= perp_turnover * (
                        config.costs.fee_rate + config.costs.slippage_rate
                    )
                    total_cost += resize.total
                    trading_cost += resize.total
                    spot_qty = requested_spot_qty
                    perp_qty = requested_perp_qty

                if (
                    timestamp.hour == 0
                    and timestamp.minute == 0
                    and timestamp.second == 0
                ):
                    spot_notional = spot_qty * spot_price
                    perp_notional = perp_qty * mark_price
                    drift = delta_drift_ratio(
                        spot_notional,
                        perp_notional,
                        config.base_notional * requested_scale,
                    )
                    if should_rebalance(
                        drift,
                        threshold=config.delta_rebalance_threshold,
                    ):
                        leverage_cap = max(margin_equity, 0.0) * config.leverage
                        buffer_cap = max(margin_equity, 0.0) / (
                            config.maintenance_buffer_multiple
                            * config.minimum_maintenance_margin_rate
                        )
                        matched_notional = min(
                            spot_notional,
                            perp_notional,
                            leverage_cap,
                            buffer_cap,
                        )
                        desired_spot_qty = matched_notional / spot_price
                        desired_perp_qty = matched_notional / mark_price
                        spot_turnover = (
                            abs(desired_spot_qty - spot_qty) * spot_price
                        )
                        perp_turnover = (
                            abs(desired_perp_qty - perp_qty) * mark_price
                        )
                        rebalance = config.costs.trade_cost(
                            spot_turnover=spot_turnover,
                            perp_turnover=perp_turnover,
                        )
                        cumulative_pnl -= rebalance.total
                        margin_equity -= (
                            perp_turnover
                            * (
                                config.costs.fee_rate
                                + config.costs.slippage_rate
                            )
                        )
                        total_cost += rebalance.total
                        trading_cost += rebalance.total
                        spot_qty = desired_spot_qty
                        perp_qty = desired_perp_qty
                        events.append(
                            {
                                "timestamp": timestamp,
                                "event_type": "rebalance",
                                "drift_ratio": drift,
                                "spot_turnover": spot_turnover,
                                "perp_turnover": perp_turnover,
                            }
                        )

        current_spot_notional = spot_qty * spot_price
        current_perp_notional = perp_qty * mark_price
        reference_notional = max(
            config.base_notional * float(scales.loc[timestamp]),
            np.finfo(float).eps,
        )
        drift = delta_drift_ratio(
            current_spot_notional,
            current_perp_notional,
            reference_notional,
        )
        rows.append(
            {
                "timestamp": timestamp,
                "spot_price": spot_price,
                "mark_price": mark_price,
                "spot_qty": spot_qty,
                "perp_short_qty": perp_qty,
                "target_scale": float(scales.loc[timestamp]),
                "price_pnl": price_pnl,
                "funding_pnl": funding_pnl,
                "trading_cost": trading_cost,
                "cumulative_pnl": cumulative_pnl,
                "equity": initial_capital + cumulative_pnl,
                "margin_equity": margin_equity,
                "delta_drift_ratio": drift,
                "liquidated": liquidated,
            }
        )
        previous_spot = spot_price
        previous_mark = mark_price
        previous_scale = float(scales.loc[timestamp])

    if config.close_at_end:
        last = rows[-1]
        close = config.costs.trade_cost(
            spot_turnover=spot_qty * last["spot_price"],
            perp_turnover=perp_qty * last["mark_price"],
        )
        exit_basis = config.costs.basis_cost(
            notional=min(
                spot_qty * last["spot_price"],
                perp_qty * last["mark_price"],
            ),
            exit_basis_rate=config.exit_basis_rate,
        )
        close_cost = close.total + exit_basis
        cumulative_pnl -= close_cost
        margin_equity -= perp_qty * last["mark_price"] * (
            config.costs.fee_rate + config.costs.slippage_rate
        )
        total_cost += close_cost
        rows[-1]["trading_cost"] += close_cost
        rows[-1]["cumulative_pnl"] = cumulative_pnl
        rows[-1]["equity"] = initial_capital + cumulative_pnl
        rows[-1]["margin_equity"] = margin_equity
        spot_qty = 0.0
        perp_qty = 0.0
        rows[-1]["spot_qty"] = 0.0
        rows[-1]["perp_short_qty"] = 0.0

    event_frame = pd.DataFrame(events)
    timeline = pd.DataFrame(rows)
    return BacktestResult(
        timeline=timeline,
        events=event_frame,
        summary={
            "net_pnl": float(cumulative_pnl),
            "funding_pnl": float(total_funding),
            "trading_cost": float(total_cost),
            "liquidated": liquidated,
            "buffer_breach_count": int(
                (event_frame.get("event_type") == "buffer_breach").sum()
                if not event_frame.empty
                else 0
            ),
            "liquidation_count": int(
                (event_frame.get("event_type") == "liquidation").sum()
                if not event_frame.empty
                else 0
            ),
        },
        initial_capital=float(initial_capital),
    )


def run_trigger_comparison(
    marks: pd.DataFrame,
    funding: pd.DataFrame,
    oi_percentile: pd.Series,
    config: EngineConfig,
) -> dict[str, BacktestResult]:
    schedule = build_refractory_schedule(oi_percentile)
    return {
        "without_trigger": run_symbol_backtest(marks, funding, config),
        "with_trigger": run_symbol_backtest(
            marks,
            funding,
            config,
            target_scale=schedule.scale,
        ),
    }
