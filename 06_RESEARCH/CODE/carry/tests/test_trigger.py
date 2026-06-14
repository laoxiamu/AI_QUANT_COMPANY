import pandas as pd

from carry.trigger import build_refractory_schedule


def test_low_oi_percentile_reduces_position_for_24h_without_extension() -> None:
    index = pd.date_range("2024-01-01", periods=6, freq="6h", tz="UTC")
    percentile = pd.Series(
        [0.50, 0.01, 0.005, 0.50, 0.50, 0.50],
        index=index,
    )

    schedule = build_refractory_schedule(percentile)

    assert schedule.scale.tolist() == [1.0, 0.5, 0.5, 0.5, 0.5, 1.0]
    assert schedule.events["timestamp"].tolist() == [index[1]]
    assert schedule.events["active_until"].tolist() == [
        index[1] + pd.Timedelta(hours=24)
    ]
