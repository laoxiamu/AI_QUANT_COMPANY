"""Synthetic tests for P1-02 volatility-targeted TSMOM sizing."""

from pathlib import Path
import sys

import pytest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p1_02_tsmom_voltarget import (
    LEVERAGE_CAP,
    SINGLE_WEIGHT_CAP,
    VOL_TARGET,
    VOL_WINDOW,
    annualized_volatility,
    scale_weights_to_gross_cap,
    volatility_weight,
)


def test_frozen_constants() -> None:
    assert VOL_WINDOW == 180
    assert VOL_TARGET == pytest.approx(0.20)
    assert SINGLE_WEIGHT_CAP == pytest.approx(0.50)
    assert LEVERAGE_CAP == pytest.approx(1.0)


def test_volatility_weight_is_inverse_volatility() -> None:
    assert volatility_weight(0.40) == pytest.approx(0.50)
    assert volatility_weight(0.80) == pytest.approx(0.25)
    assert volatility_weight(1.60) == pytest.approx(0.125)


def test_low_volatility_is_capped_without_leverage() -> None:
    assert volatility_weight(0.10) == pytest.approx(0.50)


def test_missing_or_invalid_volatility_means_no_position() -> None:
    assert volatility_weight(float("nan")) == 0.0
    assert volatility_weight(0.0) == 0.0
    assert volatility_weight(-0.1) == 0.0


def test_gross_weights_are_scaled_proportionally() -> None:
    scaled = scale_weights_to_gross_cap(
        {"BTC": 0.5, "ETH": 0.4, "SOL": 0.3}
    )
    assert sum(scaled.values()) == pytest.approx(1.0)
    assert scaled["BTC"] / scaled["ETH"] == pytest.approx(0.5 / 0.4)
    assert scaled["ETH"] / scaled["SOL"] == pytest.approx(0.4 / 0.3)


def test_weights_below_cap_are_not_scaled_up() -> None:
    weights = {"BTC": 0.2, "ETH": 0.15, "SOL": 0.1}
    assert scale_weights_to_gross_cap(weights) == weights


def test_volatility_uses_only_current_and_past_prices() -> None:
    close = pd.Series([100 + index * 0.1 for index in range(220)])
    original = annualized_volatility(close)
    changed = close.copy()
    changed.iloc[200:] *= 3
    perturbed = annualized_volatility(changed)
    pd.testing.assert_series_equal(original.iloc[:200], perturbed.iloc[:200])
