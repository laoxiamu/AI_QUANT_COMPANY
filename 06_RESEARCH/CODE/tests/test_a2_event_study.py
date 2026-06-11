from pathlib import Path
import sys
import math

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from a2_event_study import (
    block_bootstrap_p_value,
    event_window_returns,
    non_overlapping_events,
)


def test_window_returns_use_first_close_after_event_without_prelook() -> None:
    prices = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2021-01-01 00:00:00Z",
                    "2021-01-01 01:00:00Z",
                    "2021-01-02 01:00:00Z",
                    "2021-01-03 01:00:00Z",
                    "2021-01-04 01:00:00Z",
                ],
                utc=True,
            ),
            "close": [1.0, 100.0, 110.0, 121.0, 133.1],
        }
    )
    events = pd.DataFrame(
        {
            "event_time": ["2021-01-01T00:00:00Z"],
            "event_time_dt": pd.to_datetime(["2021-01-01 00:00:00Z"], utc=True),
            "symbol": ["BTCUSDT"],
            "side": ["neg"],
            "tier": ["P5"],
            "funding_value": [-0.01],
            "rolling_pctl": [0.01],
        }
    )

    result = event_window_returns(events, {"BTCUSDT": prices})

    assert result.loc[0, "t0_close_time"] == "2021-01-01T01:00:00Z"
    assert result.loc[0, "t0_close"] == 100.0
    assert round(result.loc[0, "ret_24h"], 12) == round(math.log(110.0 / 100.0), 12)


def test_non_overlapping_events_keep_first_event_in_72h_window() -> None:
    events = pd.DataFrame(
        {
            "event_time_dt": pd.to_datetime(
                [
                    "2021-01-01 00:00:00Z",
                    "2021-01-02 00:00:00Z",
                    "2021-01-04 00:00:00Z",
                    "2021-01-07 00:00:00Z",
                ],
                utc=True,
            ),
            "event_time": [
                "2021-01-01T00:00:00Z",
                "2021-01-02T00:00:00Z",
                "2021-01-04T00:00:00Z",
                "2021-01-07T00:00:00Z",
            ],
        }
    )

    kept = non_overlapping_events(events)

    assert kept["event_time"].tolist() == [
        "2021-01-01T00:00:00Z",
        "2021-01-04T00:00:00Z",
        "2021-01-07T00:00:00Z",
    ]


def test_block_bootstrap_is_reproducible_with_fixed_seed() -> None:
    data = pd.DataFrame(
        {
            "event_time_dt": pd.to_datetime(
                [
                    "2021-01-01 00:00:00Z",
                    "2021-01-02 00:00:00Z",
                    "2021-01-10 00:00:00Z",
                    "2021-01-11 00:00:00Z",
                ],
                utc=True,
            ),
            "ret_24h": [0.01, -0.02, 0.03, 0.04],
        }
    )

    first = block_bootstrap_p_value(data, "ret_24h", alternative="greater", seed=20260611, n_iter=200)
    second = block_bootstrap_p_value(data, "ret_24h", alternative="greater", seed=20260611, n_iter=200)

    assert first == second
    assert first["seed"] == 20260611
