"""A-1 OI percentile carry-risk trigger."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TriggerSchedule:
    scale: pd.Series
    events: pd.DataFrame


def build_refractory_schedule(
    oi_percentile: pd.Series,
    *,
    threshold: float = 0.01,
    reduced_scale: float = 0.5,
    refractory: str | pd.Timedelta = "24h",
) -> TriggerSchedule:
    """Reduce at a trigger timestamp and ignore retriggers until expiry."""
    if not isinstance(oi_percentile.index, pd.DatetimeIndex):
        raise TypeError("oi_percentile must use a DatetimeIndex")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")
    if not 0 < reduced_scale <= 1:
        raise ValueError("reduced_scale must be in (0, 1]")
    duration = pd.Timedelta(refractory)
    if duration <= pd.Timedelta(0):
        raise ValueError("refractory must be positive")

    values = oi_percentile.sort_index().copy()
    if values.index.tz is None:
        values.index = values.index.tz_localize("UTC")
    else:
        values.index = values.index.tz_convert("UTC")

    active_until: pd.Timestamp | None = None
    scales: list[float] = []
    event_rows: list[dict[str, object]] = []
    for timestamp, value in values.items():
        active = active_until is not None and timestamp < active_until
        if not active and pd.notna(value) and float(value) <= threshold:
            active_until = timestamp + duration
            active = True
            event_rows.append(
                {
                    "timestamp": timestamp,
                    "oi_percentile": float(value),
                    "active_until": active_until,
                    "target_scale": reduced_scale,
                }
            )
        scales.append(reduced_scale if active else 1.0)

    events = pd.DataFrame(
        event_rows,
        columns=[
            "timestamp",
            "oi_percentile",
            "active_until",
            "target_scale",
        ],
    )
    return TriggerSchedule(
        scale=pd.Series(scales, index=values.index, name="target_scale"),
        events=events,
    )
