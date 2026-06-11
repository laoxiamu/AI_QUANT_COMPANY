from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from features.a2_funding_features import (
    add_rolling_percentiles,
    merge_extreme_readings,
    split_work_holdout,
)


def test_rolling_percentile_uses_only_prior_values() -> None:
    dates = pd.date_range("2020-01-01", periods=181, freq="D")
    df = pd.DataFrame(
        {
            "datetime": dates,
            "last_funding_rate": [0.0] * 180 + [1.0],
        }
    )

    base = add_rolling_percentiles(df)
    changed_future = df.copy()
    changed_future.loc[180, "last_funding_rate"] = -1_000.0
    perturbed = add_rolling_percentiles(changed_future)

    assert base.loc[179, "warmup"]
    assert not base.loc[180, "warmup"]
    assert base.loc[180, "rolling_pctl"] == 1.0
    assert perturbed.loc[180, "rolling_pctl"] == 0.0


def test_merge_rule_collapses_23h_but_keeps_25h_gap() -> None:
    readings = pd.DataFrame(
        {
            "event_time_dt": pd.to_datetime(
                [
                    "2021-01-01 00:00:00Z",
                    "2021-01-01 23:00:00Z",
                    "2021-01-03 00:00:00Z",
                ]
            ),
            "event_time": [
                "2021-01-01T00:00:00Z",
                "2021-01-01T23:00:00Z",
                "2021-01-03T00:00:00Z",
            ],
            "symbol": ["BTCUSDT", "BTCUSDT", "BTCUSDT"],
            "side": ["neg", "neg", "neg"],
            "tier": ["P5", "P5", "P5"],
            "funding_value": [-0.01, -0.02, -0.03],
            "rolling_pctl": [0.01, 0.02, 0.03],
        }
    )

    events = merge_extreme_readings(readings)

    assert events["event_time"].tolist() == [
        "2021-01-01T00:00:00Z",
        "2021-01-03T00:00:00Z",
    ]


def test_holdout_split_is_deterministic_mod_five() -> None:
    events = pd.DataFrame(
        {
            "event_time": [f"2021-01-{day:02d}T00:00:00Z" for day in range(1, 11)],
            "symbol": ["BTCUSDT"] * 10,
            "side": ["neg"] * 10,
            "tier": ["P5"] * 10,
            "funding_value": [-0.01] * 10,
            "rolling_pctl": [0.01] * 10,
        }
    )

    work, holdout = split_work_holdout(events)

    assert holdout["event_time"].tolist() == [
        "2021-01-05T00:00:00Z",
        "2021-01-10T00:00:00Z",
    ]
    assert work["event_time"].tolist() == [
        "2021-01-01T00:00:00Z",
        "2021-01-02T00:00:00Z",
        "2021-01-03T00:00:00Z",
        "2021-01-04T00:00:00Z",
        "2021-01-06T00:00:00Z",
        "2021-01-07T00:00:00Z",
        "2021-01-08T00:00:00Z",
        "2021-01-09T00:00:00Z",
    ]
