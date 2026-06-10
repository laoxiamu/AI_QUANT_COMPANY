"""Synthetic tests for P1-05 two-axis regime attribution."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p1_05_regime_attribution import (
    classify_grid,
    efficiency_ratio,
    prior_daily_bull_state,
    sample_grade,
)


def test_six_grid_labels() -> None:
    assert classify_grid(True, 30, 10, True) == "trend_up_bull"
    assert classify_grid(True, 30, 10, False) == "trend_up_bear"
    assert classify_grid(True, 10, 30, True) == "trend_down_bull"
    assert classify_grid(True, 10, 30, False) == "trend_down_bear"
    assert classify_grid(False, 30, 10, True) == "range_bull"
    assert classify_grid(False, 10, 30, False) == "range_bear"
    assert classify_grid(True, 30, 10, pd.NA) == "unknown"


def test_sample_grades_follow_dec_018() -> None:
    assert sample_grade(299) == "INSUFFICIENT"
    assert sample_grade(300) == "EXPLORATORY"
    assert sample_grade(499) == "EXPLORATORY"
    assert sample_grade(500) == "CONFIRMATORY"


def test_efficiency_ratio_is_one_for_monotonic_path() -> None:
    close = pd.Series(range(1, 70), dtype=float)
    assert efficiency_ratio(close).iloc[-1] == 1.0


def test_daily_bull_state_uses_previous_completed_day() -> None:
    dates = pd.date_range("2020-01-01", periods=205 * 6, freq="4h")
    close = pd.Series(range(len(dates)), dtype=float)
    original = prior_daily_bull_state(pd.Series(dates), close)
    changed = close.copy()
    changed.iloc[-1] = -1_000_000
    perturbed = prior_daily_bull_state(pd.Series(dates), changed)
    pd.testing.assert_series_equal(original, perturbed)


def test_daily_bull_state_does_not_call_warmup_bear() -> None:
    dates = pd.date_range("2020-01-01", periods=20 * 6, freq="4h")
    close = pd.Series(range(len(dates)), dtype=float)
    bull = prior_daily_bull_state(pd.Series(dates), close)
    assert bull.isna().all()
