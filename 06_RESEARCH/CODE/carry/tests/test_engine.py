import pandas as pd
import pytest

from carry.config import EngineConfig
from carry.costs import CostModel
from carry.engine import (
    delta_drift_ratio,
    funding_cashflow,
    margin_health,
    run_symbol_backtest,
    run_trigger_comparison,
    should_rebalance,
)


ZERO_COST = CostModel(fee_rate=0.0, slippage_rate=0.0)


def _marks(
    timestamps: list[str],
    spot_prices: list[float],
    perp_prices: list[float] | None = None,
) -> pd.DataFrame:
    if perp_prices is None:
        perp_prices = spot_prices
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(timestamps, utc=True),
            "spot_price": spot_prices,
            "mark_price": perp_prices,
        }
    )


def _funding(timestamp: str, rate: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime([timestamp], utc=True),
            "funding_rate": [rate],
        }
    )


def test_equal_quantity_legs_cancel_price_move_leaving_funding_pnl() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-01T08:00:00Z"],
        [100.0, 120.0],
    )
    result = run_symbol_backtest(
        marks,
        _funding("2024-01-01T08:00:00Z", 0.001),
        EngineConfig(base_notional=1_000.0, costs=ZERO_COST),
    )

    last = result.timeline.iloc[-1]
    assert last["price_pnl"] == pytest.approx(0.0)
    assert result.summary["funding_pnl"] == pytest.approx(1.2)
    assert result.summary["net_pnl"] == pytest.approx(1.2)


def test_short_receives_positive_funding_and_pays_negative_funding() -> None:
    assert funding_cashflow(1_000.0, 0.001) == pytest.approx(1.0)
    assert funding_cashflow(1_000.0, -0.001) == pytest.approx(-1.0)


def test_rebalance_uses_strictly_greater_than_five_percent() -> None:
    assert delta_drift_ratio(1_000.0, 1_051.0, 1_000.0) == pytest.approx(
        0.051
    )
    assert should_rebalance(0.051, threshold=0.05)
    assert not should_rebalance(0.05, threshold=0.05)


def test_engine_does_not_retarget_notional_between_daily_checks() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
        [100.0, 110.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        close_at_end=False,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        config,
    )

    assert result.timeline.iloc[-1]["spot_qty"] == pytest.approx(10.0)
    assert result.timeline.iloc[-1]["perp_short_qty"] == pytest.approx(10.0)


def test_engine_rebalances_perp_at_midnight_when_drift_exceeds_threshold() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
        [100.0, 100.0],
        [100.0, 106.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        close_at_end=False,
        minimum_maintenance_margin_rate=0.001,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        config,
    )

    assert result.event_counts["rebalance"] == 1
    last = result.timeline.iloc[-1]
    spot_notional = last["spot_qty"] * last["spot_price"]
    perp_notional = last["perp_short_qty"] * last["mark_price"]
    assert spot_notional == pytest.approx(perp_notional)
    assert perp_notional <= last["margin_equity"] * config.leverage


def test_engine_does_not_rebalance_at_half_past_midnight() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-02T00:30:00Z"],
        [100.0, 100.0],
        [100.0, 106.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        close_at_end=False,
        minimum_maintenance_margin_rate=0.001,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        config,
    )

    assert result.event_counts["rebalance"] == 0


def test_opening_cost_reserve_keeps_perp_leverage_at_or_below_cap() -> None:
    marks = _marks(["2024-01-01T00:00:00Z"], [100.0])
    config = EngineConfig(base_notional=1_000.0, close_at_end=False)

    result = run_symbol_backtest(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        config,
    )

    first = result.timeline.iloc[0]
    leverage = (
        first["perp_short_qty"] * first["mark_price"]
        / first["margin_equity"]
    )
    assert leverage <= config.leverage


def test_margin_health_distinguishes_buffer_breach_and_liquidation() -> None:
    assert margin_health(20.0, 100.0, 0.10, buffer_multiple=3.0) == (
        "buffer_breach"
    )
    assert margin_health(9.0, 100.0, 0.10, buffer_multiple=3.0) == (
        "liquidation"
    )


def test_buffer_breach_is_logged_and_reduces_both_legs_without_liquidation() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
        [100.0, 116.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        leverage=2.0,
        minimum_maintenance_margin_rate=0.10,
        close_at_end=False,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        config,
    )

    assert result.event_counts["buffer_breach"] == 1
    assert result.event_counts["liquidation"] == 0
    last = result.timeline.iloc[-1]
    assert last["spot_qty"] * last["spot_price"] == pytest.approx(
        last["perp_short_qty"] * last["mark_price"]
    )


def test_mark_price_spike_liquidates_short_leg_and_logs_event() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
        [100.0, 160.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        leverage=2.0,
        minimum_maintenance_margin_rate=0.10,
        close_at_end=False,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        config,
    )

    assert result.event_counts["liquidation"] == 1
    assert result.event_counts["buffer_breach"] == 0
    assert result.events.iloc[0]["event_type"] == "liquidation"
    assert result.timeline.iloc[-1]["perp_short_qty"] == 0.0
    assert result.timeline.iloc[-1]["spot_qty"] > 0.0


def test_positive_funding_cannot_rescue_a_position_already_below_minimum() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-01T08:00:00Z"],
        [100.0, 140.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        leverage=2.0,
        minimum_maintenance_margin_rate=0.10,
        close_at_end=False,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        _funding("2024-01-01T08:00:00Z", 0.05),
        config,
    )

    assert result.event_counts["liquidation"] == 1
    assert result.summary["funding_pnl"] == 0.0


def test_negative_funding_can_trigger_immediate_margin_liquidation() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-01T08:00:00Z"],
        [100.0, 100.0],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        leverage=2.0,
        minimum_maintenance_margin_rate=0.10,
        close_at_end=False,
        costs=ZERO_COST,
    )

    result = run_symbol_backtest(
        marks,
        _funding("2024-01-01T08:00:00Z", -0.50),
        config,
    )

    assert result.summary["funding_pnl"] == pytest.approx(-500.0)
    assert result.event_counts["liquidation"] == 1
    assert result.timeline.iloc[-1]["perp_short_qty"] == 0.0


def test_trigger_comparison_produces_enabled_and_disabled_equity_curves() -> None:
    marks = _marks(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T08:00:00Z",
            "2024-01-01T16:00:00Z",
        ],
        [100.0, 100.0, 100.0],
    )
    oi = pd.Series(
        [0.50, 0.01, 0.50],
        index=marks["timestamp"],
    )

    comparison = run_trigger_comparison(
        marks,
        _funding("2024-01-01T16:00:00Z", 0.001),
        oi,
        EngineConfig(base_notional=1_000.0, costs=ZERO_COST),
    )

    assert set(comparison) == {"without_trigger", "with_trigger"}
    assert (
        comparison["with_trigger"].timeline["target_scale"].iloc[-1] == 0.5
    )
    assert (
        comparison["with_trigger"].summary["funding_pnl"]
        < comparison["without_trigger"].summary["funding_pnl"]
    )


def test_trigger_variant_keeps_same_capital_and_restores_after_refractory() -> None:
    marks = _marks(
        ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
        [100.0, 100.0],
    )
    oi = pd.Series(
        [0.01, 0.50],
        index=marks["timestamp"],
    )
    config = EngineConfig(
        base_notional=1_000.0,
        close_at_end=False,
        costs=ZERO_COST,
    )

    comparison = run_trigger_comparison(
        marks,
        pd.DataFrame(columns=["timestamp", "funding_rate"]),
        oi,
        config,
    )

    enabled = comparison["with_trigger"]
    disabled = comparison["without_trigger"]
    assert enabled.initial_capital == disabled.initial_capital
    last = enabled.timeline.iloc[-1]
    assert last["target_scale"] == 1.0
    assert last["spot_qty"] * last["spot_price"] == pytest.approx(1_000.0)
    assert last["perp_short_qty"] * last["mark_price"] == pytest.approx(
        1_000.0
    )
