"""Synthetic tests for P1-01 TSMOM execution and funding rules."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p1_01_tsmom import (
    execution_price,
    funding_payment,
    signal_from_prices,
)


def test_tsmom_signal_direction() -> None:
    assert signal_from_prices(110, 100) == 1
    assert signal_from_prices(90, 100) == -1
    assert signal_from_prices(100, 100) == 0


def test_long_and_short_execution_slippage() -> None:
    assert execution_price(100, 1, True) == pytest.approx(100.1)
    assert execution_price(100, 1, False) == pytest.approx(99.9)
    assert execution_price(100, -1, True) == pytest.approx(99.9)
    assert execution_price(100, -1, False) == pytest.approx(100.1)


def test_funding_direction_for_positive_rate() -> None:
    assert funding_payment(1, 2, 10_000, 0.0001) == pytest.approx(2.0)
    assert funding_payment(-1, 2, 10_000, 0.0001) == pytest.approx(-2.0)


def test_funding_direction_for_negative_rate() -> None:
    assert funding_payment(1, 2, 10_000, -0.0001) == pytest.approx(-2.0)
    assert funding_payment(-1, 2, 10_000, -0.0001) == pytest.approx(2.0)
