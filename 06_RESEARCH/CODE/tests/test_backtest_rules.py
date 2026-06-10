"""Offline regression tests for the pre-registered backtest rules."""

from datetime import datetime, timedelta, timezone

import pytest

from backtest_rules import (
    BarAction,
    FundingSettlement,
    PositionRegistry,
    evaluate_long_bar,
    long_funding_cost,
)


UTC = timezone.utc


def at(hour: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=hour)


def test_take_profit_executes_when_stop_is_not_touched() -> None:
    decision = evaluate_long_bar(
        high=103, low=99, stop_price=98, take_profit_1=102
    )

    assert decision.action is BarAction.TAKE_PROFIT_1
    assert decision.exit_price == 102
    assert decision.position_fraction == 0.5


def test_stop_executes_when_take_profit_is_not_touched() -> None:
    decision = evaluate_long_bar(
        high=101, low=97, stop_price=98, take_profit_1=102
    )

    assert decision.action is BarAction.STOP
    assert decision.exit_price == 98
    assert decision.position_fraction == 1.0


def test_stop_wins_when_same_bar_touches_stop_and_take_profit() -> None:
    decision = evaluate_long_bar(
        high=103, low=97, stop_price=98, take_profit_1=102
    )

    assert decision.action is BarAction.STOP
    assert decision.exit_price == 98
    assert decision.position_fraction == 1.0


def test_same_symbol_same_direction_signal_is_rejected() -> None:
    positions = PositionRegistry()

    assert positions.try_open("BTCUSDT", "LONG") is True
    assert positions.try_open("BTCUSDT", "LONG") is False
    assert positions.count == 1


def test_different_symbol_same_direction_signal_is_accepted() -> None:
    positions = PositionRegistry()

    assert positions.try_open("BTCUSDT", "LONG") is True
    assert positions.try_open("ETHUSDT", "LONG") is True
    assert positions.count == 2


def test_same_symbol_signal_is_accepted_after_position_closes() -> None:
    positions = PositionRegistry()
    assert positions.try_open("BTCUSDT", "LONG") is True

    positions.close("BTCUSDT", "LONG")

    assert positions.try_open("BTCUSDT", "LONG") is True
    assert positions.count == 1


def test_three_funding_settlements_are_charged_once_each() -> None:
    settlements = [
        FundingSettlement(at(hour), rate=0.0001, notional=10_000)
        for hour in (8, 16, 24)
    ]

    cost = long_funding_cost(
        settlements, entry_time=at(0), exit_time=at(24)
    )

    assert cost == pytest.approx(10_000 * 0.0001 * 3)


def test_multiple_settlements_use_each_rate_and_notional_once() -> None:
    settlements = [
        FundingSettlement(at(8), rate=0.0001, notional=10_000),
        FundingSettlement(at(16), rate=-0.0002, notional=8_000),
        FundingSettlement(at(24), rate=0.0003, notional=5_000),
    ]

    cost = long_funding_cost(
        settlements, entry_time=at(0), exit_time=at(24)
    )

    assert cost == pytest.approx(1.0 - 1.6 + 1.5)


def test_funding_stops_after_position_closes() -> None:
    settlements = [
        FundingSettlement(at(hour), rate=0.0001, notional=10_000)
        for hour in (0, 8, 16, 24)
    ]

    cost = long_funding_cost(
        settlements, entry_time=at(0), exit_time=at(16)
    )

    assert cost == pytest.approx(2.0)
