"""Synthetic tests for P1-04 ADX regime-first long TSMOM."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p1_04_tsmom_regime_long import (
    ADX_ENTRY,
    ADX_EXIT,
    ADX_PERIOD,
    calculate_adx,
    desired_long_position,
    hysteresis_regime,
)


def test_frozen_adx_constants() -> None:
    assert ADX_PERIOD == 14
    assert ADX_ENTRY == 25
    assert ADX_EXIT == 20


def test_hysteresis_enters_exits_and_holds_band() -> None:
    adx = pd.Series([np.nan, 19, 26, 24, 21, 19, 23, 26])
    assert hysteresis_regime(adx).tolist() == [
        False,
        False,
        True,
        True,
        True,
        False,
        False,
        True,
    ]


def test_adx_uses_only_current_and_past_bars() -> None:
    size = 100
    close = pd.Series(np.linspace(100, 130, size))
    bars = pd.DataFrame({
        "high": close + 1,
        "low": close - 1,
        "close": close,
    })
    original = calculate_adx(bars)
    changed = bars.copy()
    changed.loc[80:, ["high", "low", "close"]] *= 2
    perturbed = calculate_adx(changed)
    pd.testing.assert_series_equal(original.iloc[:80], perturbed.iloc[:80])


def test_flat_market_never_enters_trend_regime() -> None:
    bars = pd.DataFrame({
        "high": [101.0] * 100,
        "low": [99.0] * 100,
        "close": [100.0] * 100,
    })
    assert not hysteresis_regime(calculate_adx(bars)).any()


def test_position_is_long_only_and_requires_both_conditions() -> None:
    assert desired_long_position(1, True) == 1
    assert desired_long_position(1, False) == 0
    assert desired_long_position(-1, True) == 0
    assert desired_long_position(0, True) == 0
