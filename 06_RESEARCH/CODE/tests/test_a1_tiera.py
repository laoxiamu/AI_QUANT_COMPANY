from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from a1_tiera_core import (  # noqa: E402
    add_mark_direction,
    apply_refractory,
    bootstrap_sample_indices,
    decrypt_aes256_gcm,
    encrypt_aes256_gcm,
    holm_adjust,
    rolling_midrank_percentile,
    split_work_sealed,
    trigger_rows,
)
from a1_tiera_executor import compute_episode_outcomes  # noqa: E402


def test_trigger_requires_p1_nominal_oi_and_negative_same_window_mark() -> None:
    hourly = pd.DataFrame(
        {
            "ts": pd.date_range("2024-01-01", periods=9, freq="1h", tz="UTC"),
            "d6h_rolling_pctl": [np.nan] * 6 + [0.01, 0.009, 0.011],
            "oi_notional": [100.0] * 9,
            "d6h_pct": [0.0] * 9,
        }
    )
    mark = pd.DataFrame(
        {
            "ts": hourly["ts"],
            "mark_close": [100, 100, 100, 100, 100, 100, 99, 101, 98],
        }
    )

    featured = add_mark_direction(hourly, mark)
    triggered = trigger_rows(featured)

    assert triggered["ts"].tolist() == [pd.Timestamp("2024-01-01T06:00:00Z")]
    assert triggered.iloc[0]["r6h_mark"] < 0


def test_refractory_ignores_triggers_through_24h_without_extension() -> None:
    triggers = pd.DataFrame(
        {
            "ts": pd.to_datetime(
                [
                    "2024-01-01T00:00:00Z",
                    "2024-01-01T23:00:00Z",
                    "2024-01-02T00:00:00Z",
                    "2024-01-02T01:00:00Z",
                ],
                utc=True,
            )
        }
    )

    episodes = apply_refractory(triggers)

    assert episodes["ts"].tolist() == [
        pd.Timestamp("2024-01-01T00:00:00Z"),
        pd.Timestamp("2024-01-02T01:00:00Z"),
    ]


class FixedRng:
    def __init__(self, starts: list[int]):
        self.starts = iter(starts)

    def integers(self, low: int, high: int) -> int:
        value = next(self.starts)
        assert low <= value < high
        return value


def test_moving_block_wrap_order_and_last_block_truncation() -> None:
    times = pd.to_datetime(
        [
            "2024-01-01T00:00:00Z",
            "2024-01-01T02:00:00Z",
            "2024-01-01T04:00:00Z",
        ],
        utc=True,
    )

    sampled = bootstrap_sample_indices(
        times,
        FixedRng([4, 0]),
        width_hours=2,
    )

    assert sampled.tolist() == [2, 0, 0]
    assert len(sampled) == len(times)


def test_holm_uses_fixed_family_and_is_monotone() -> None:
    adjusted = holm_adjust(
        {
            "a": 0.01,
            "b": 0.03,
            "c": 0.04,
            "d": None,
        }
    )

    assert adjusted["a"] == pytest.approx(0.04)
    assert adjusted["b"] == pytest.approx(0.09)
    assert adjusted["c"] == pytest.approx(0.09)
    assert adjusted["d"] is None


def test_aes256_gcm_round_trip_and_tag_authentication() -> None:
    key = bytes(range(32))
    nonce = bytes(range(12))
    plaintext = b"sealed episode csv"

    encrypted = encrypt_aes256_gcm(plaintext, key, nonce)

    assert encrypted[:12] == nonce
    assert decrypt_aes256_gcm(encrypted, key) == plaintext
    tampered = encrypted[:-1] + bytes([encrypted[-1] ^ 1])
    with pytest.raises(Exception):
        decrypt_aes256_gcm(tampered, key)


def test_executor_alignment_waits_for_close_after_signal_bucket() -> None:
    work = pd.DataFrame(
        {
            "event_time": pd.to_datetime(["2024-01-04T00:00:00Z"], utc=True),
            "event_time_utc": ["2024-01-04T00:00:00Z"],
            "symbol": ["BTCUSDT"],
            "severity_code": [2],
            "a2_overlap": [0],
            "regime": ["bull"],
        }
    )
    bar_opens = pd.date_range(
        "2023-12-31T00:00:00Z", periods=200, freq="1h", tz="UTC"
    )
    marks = {
        "BTCUSDT": pd.DataFrame(
            {
                "bar_open_time": bar_opens,
                "close_time": bar_opens + pd.Timedelta(hours=1),
                "mark_close": np.exp(np.arange(len(bar_opens)) * 0.001),
            }
        )
    }
    funding = {
        "BTCUSDT": pd.DataFrame(
            {
                "funding_time": pd.to_datetime([], utc=True),
                "funding_rate": pd.Series(dtype=float),
            }
        )
    }

    result = compute_episode_outcomes(work, marks, funding)

    assert result.iloc[0]["signal_available_time"] == pd.Timestamp(
        "2024-01-04T01:00:00Z"
    )
    assert result.iloc[0]["align_time"] == pd.Timestamp("2024-01-04T02:00:00Z")


def test_rolling_percentile_requires_180_days_and_720_prior_samples() -> None:
    times = pd.DatetimeIndex(
        [
            pd.Timestamp("2023-01-01T00:00:00Z")
            + pd.Timedelta(days=day, hours=hour)
            for day in range(180)
            for hour in (0, 6, 12, 18)
        ]
        + [pd.Timestamp("2023-06-30T00:00:00Z")]
    )
    values = pd.Series(np.zeros(len(times)))
    values.iloc[-1] = 1.0

    result = rolling_midrank_percentile(pd.Series(times), values)

    assert pd.isna(result.iloc[719])
    assert result.iloc[-1] == pytest.approx(1.0)


def test_split_reserves_every_fifth_after_deterministic_sort() -> None:
    episodes = pd.DataFrame(
        {
            "event_time_utc": pd.to_datetime(
                [
                    "2024-01-02T00:00:00Z",
                    "2024-01-01T00:00:00Z",
                    "2024-01-03T00:00:00Z",
                    "2024-01-01T00:00:00Z",
                    "2024-01-04T00:00:00Z",
                ],
                utc=True,
            ),
            "symbol": ["BTC", "SOL", "BTC", "BTC", "ETH"],
            "row": [3, 2, 4, 1, 5],
        }
    )

    work, sealed = split_work_sealed(episodes)

    assert work["row"].tolist() == [1, 2, 3, 4]
    assert sealed["row"].tolist() == [5]
