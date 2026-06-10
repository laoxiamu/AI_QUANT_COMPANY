"""Synthetic tests for P1-06 macro-bull-gated long TSMOM."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p1_06_tsmom_macro_bull import (
    ADX_ENTRY,
    ADX_EXIT,
    ADX_PERIOD,
    MACRO_MA_DAYS,
    calculate_adx,
    desired_long_position,
    hysteresis_regime,
    prior_daily_bull_state,
    run_backtest,
)


def test_frozen_adx_constants() -> None:
    assert ADX_PERIOD == 14
    assert ADX_ENTRY == 25
    assert ADX_EXIT == 20
    assert MACRO_MA_DAYS == 200


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
    assert desired_long_position(1, True, True) == 1
    assert desired_long_position(1, True, False) == 0
    assert desired_long_position(1, True, pd.NA) == 0
    assert desired_long_position(1, False, True) == 0
    assert desired_long_position(-1, True, True) == 0
    assert desired_long_position(0, True, True) == 0


def test_macro_state_uses_only_previous_completed_day() -> None:
    dates = pd.date_range("2020-01-01", periods=205 * 6, freq="4h")
    close = pd.Series(np.arange(len(dates)), dtype=float)
    original = prior_daily_bull_state(pd.Series(dates), close)
    changed = close.copy()
    changed.iloc[-1] = -1_000_000
    perturbed = prior_daily_bull_state(pd.Series(dates), changed)
    pd.testing.assert_series_equal(original, perturbed)


def test_macro_warmup_is_unknown_and_blocks_long() -> None:
    dates = pd.date_range("2020-01-01", periods=20 * 6, freq="4h")
    close = pd.Series(np.arange(len(dates)), dtype=float)
    state = prior_daily_bull_state(pd.Series(dates), close)
    assert state.isna().all()
    assert desired_long_position(1, True, state.iloc[-1]) == 0


def test_macro_bear_transition_exits_at_next_open() -> None:
    dates = pd.date_range("2022-01-01", periods=4, freq="4h")
    bars = pd.DataFrame({
        "datetime": dates,
        "open": [100.0, 101.0, 102.0, 103.0],
        "high": [101.0, 102.0, 103.0, 104.0],
        "low": [99.0, 100.0, 101.0, 102.0],
        "close": [100.5, 101.5, 102.5, 103.5],
        "execution_long": [0, 1, 1, 0],
        "execution_signal": [0, 1, 1, 1],
        "execution_adx": [np.nan, 30.0, 30.0, 30.0],
        "execution_macro_bull": [pd.NA, True, True, False],
        "signal_time": dates - pd.Timedelta(hours=4),
    })
    funding = pd.DataFrame(columns=["datetime", "last_funding_rate"])
    result = run_backtest(
        {"BTC": bars},
        {"BTC": funding},
        include_fees=False,
        include_slippage=False,
        include_funding=False,
        symbols=("BTC",),
    )
    assert len(result.trades) == 1
    trade = result.trades.iloc[0]
    assert trade["entry_time"] == dates[1]
    assert trade["exit_time"] == dates[3]
    assert trade["exit_reason"] == "MACRO_BEAR_EXIT"
    assert (result.trades["direction"] == 1).all()
