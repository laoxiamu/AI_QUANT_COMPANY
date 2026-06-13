from pathlib import Path
import math
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from a1_event_study_framework import (  # noqa: E402
    align_windows,
    compute_car,
    monotonicity_test,
    permutation_test,
)


def test_align_windows_uses_first_close_after_event_without_prelook() -> None:
    prices = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2024-01-01 00:00:00Z",
                    "2024-01-01 01:00:00Z",
                    "2024-01-02 01:00:00Z",
                    "2024-01-03 01:00:00Z",
                    "2024-12-09 20:00:00Z",
                ],
                utc=True,
            ),
            "close": [50.0, 100.0, 110.0, 121.0, 999.0],
        }
    )
    episodes = pd.DataFrame(
        {
            "episode_id": [7],
            "event_time": pd.to_datetime(["2024-01-01 00:30:00Z"], utc=True),
            "symbol": ["BTCUSDT"],
            "oi_quantile": [0.10],
        }
    )

    result = align_windows(episodes, prices, horizons=[24, 48])

    assert result["t0_time"].tolist() == [
        pd.Timestamp("2024-01-01 01:00:00"),
        pd.Timestamp("2024-01-01 01:00:00"),
    ]
    ret_24h = result.loc[result["horizon"] == 24, "log_return"].iloc[0]
    assert ret_24h == pytest.approx(math.log(110.0 / 100.0))
    assert (result["t0_close"] == 100.0).all()


def test_compute_car_mean_and_median_are_correct() -> None:
    windows = pd.DataFrame(
        {
            "horizon": [24, 24, 48],
            "log_return": [0.10, 0.30, -0.20],
        }
    )

    car = compute_car(windows)
    row_24h = car[car["horizon"] == 24].iloc[0]

    assert row_24h["n"] == 2
    assert row_24h["mean_log_return"] == pytest.approx(0.20)
    assert row_24h["median_log_return"] == pytest.approx(0.20)


def test_monotonicity_test_returns_expected_format() -> None:
    windows = pd.DataFrame(
        {
            "horizon": [24, 24, 24, 24],
            "log_return": [0.01, 0.02, 0.03, 0.04],
            "oi_quantile": [0.10, 0.30, 0.60, 0.90],
        }
    )

    result = monotonicity_test(windows, "oi_quantile")

    assert set(
        [
            "horizon",
            "quantile_col",
            "bucket",
            "bucket_order",
            "n",
            "mean_log_return",
            "spearman_r",
            "monotonic_direction",
        ]
    ).issubset(result.columns)
    assert result["bucket"].tolist() == ["Q1", "Q2", "Q3", "Q4"]
    assert result["spearman_r"].iloc[0] == pytest.approx(1.0)
    assert result["monotonic_direction"].iloc[0] == "increasing"


def test_permutation_test_p_value_is_in_unit_interval() -> None:
    windows = pd.DataFrame(
        {
            "horizon": [24, 24, 24, 48, 48, 48],
            "log_return": [0.01, -0.02, 0.03, 0.04, -0.01, 0.02],
        }
    )

    result = permutation_test(windows, n_perm=200, seed=42)

    assert result["seed"] == 42
    assert result["n_perm"] == 200
    for payload in result["horizons"].values():
        assert 0.0 <= payload["p_value"] <= 1.0
