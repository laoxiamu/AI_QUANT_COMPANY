from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))

from dec070_filter_audit import (  # noqa: E402
    classify_adtv,
    classify_jump_frequency,
    classify_tier,
    complete_utc_dates,
    valid_four_hour_log_returns,
)


def test_absolute_threshold_boundaries() -> None:
    assert classify_adtv(10_000_000) == "pass"
    assert classify_adtv(5_000_000) == "edge"
    assert classify_adtv(4_999_999) == "fail"

    assert classify_jump_frequency(0.002) == "pass"
    assert classify_jump_frequency(0.003) == "edge"
    assert classify_jump_frequency(0.0030001) == "fail"


def test_partial_evidence_tier_rules() -> None:
    assert classify_tier("pass", "pass") == "Tier 1-clean"
    assert classify_tier("pass", "edge") == "Tier 1-watch"
    assert classify_tier("edge", "edge") == "Tier 1-watch"
    assert classify_tier("pass", "fail") == "exclude"
    assert classify_tier("na", "pass") == "N.A."


def test_returns_exclude_non_four_hour_gap() -> None:
    frame = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2024-01-01T00:00:00Z",
                    "2024-01-01T04:00:00Z",
                    "2024-01-01T12:00:00Z",
                ],
                utc=True,
            ),
            "close": [100.0, 110.0, 220.0],
        }
    )
    returns = valid_four_hour_log_returns(frame)
    assert len(returns) == 1
    assert returns.index.tolist() == [1]


def test_complete_day_requires_six_expected_bar_opens() -> None:
    frame = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2024-01-01T00:00:00Z",
                    "2024-01-01T04:00:00Z",
                    "2024-01-01T08:00:00Z",
                    "2024-01-01T12:00:00Z",
                    "2024-01-01T16:00:00Z",
                    "2024-01-01T20:00:00Z",
                    "2024-01-02T00:00:00Z",
                    "2024-01-02T04:00:00Z",
                ],
                utc=True,
            )
        }
    )
    dates = complete_utc_dates(frame)
    assert [value.date().isoformat() for value in dates] == ["2024-01-01"]
