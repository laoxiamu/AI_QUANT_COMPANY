from pathlib import Path
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from features.a1_oi_features import add_rolling_oi_percentiles, resample_oi_1h


def test_rolling_percentile_excludes_current_and_future_values() -> None:
    target_idx = 24 * 180
    dates = pd.date_range("2021-01-01", periods=target_idx + 2, freq="h", tz="UTC")
    base = pd.DataFrame(
        {
            "ts": dates,
            "oi": 1.0,
            "d6h_pct": 0.0,
            "d24h_pct": 0.0,
        }
    )
    base.loc[target_idx, ["d6h_pct", "d24h_pct"]] = 1.0
    base.loc[target_idx + 1, ["d6h_pct", "d24h_pct"]] = 2.0

    changed_future = base.copy()
    changed_future.loc[target_idx + 1, ["d6h_pct", "d24h_pct"]] = -1_000.0

    featured = add_rolling_oi_percentiles(base)
    perturbed = add_rolling_oi_percentiles(changed_future)

    assert not featured.loc[target_idx, "warmup"]
    assert featured.loc[target_idx, "d6h_rolling_pctl"] == 1.0
    assert featured.loc[target_idx, "d24h_rolling_pctl"] == 1.0
    assert perturbed.loc[target_idx, "d6h_rolling_pctl"] == 1.0
    assert perturbed.loc[target_idx, "d24h_rolling_pctl"] == 1.0
    assert (
        featured.loc[target_idx + 1, "d6h_rolling_pctl"]
        != perturbed.loc[target_idx + 1, "d6h_rolling_pctl"]
    )


def test_resample_5m_to_1h_uses_last_value_without_forward_fill() -> None:
    metrics = pd.DataFrame(
        {
            "create_time": pd.to_datetime(
                [
                    "2024-01-01T00:00:00Z",
                    "2024-01-01T00:55:00Z",
                    "2024-01-01T02:00:00Z",
                    "2024-01-01T02:55:00Z",
                ],
                utc=True,
            ),
            "sum_open_interest": [10.0, 12.0, 20.0, 24.0],
        }
    )

    hourly = resample_oi_1h(metrics)

    assert hourly["ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").tolist() == [
        "2024-01-01T00:00:00Z",
        "2024-01-01T01:00:00Z",
        "2024-01-01T02:00:00Z",
    ]
    assert hourly.loc[0, "oi"] == 12.0
    assert pd.isna(hourly.loc[1, "oi"])
    assert hourly.loc[2, "oi"] == 24.0
