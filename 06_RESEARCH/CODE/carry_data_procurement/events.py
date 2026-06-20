"""Event extraction for stablecoin depeg stress windows."""

from __future__ import annotations

import pandas as pd


def detect_depeg_events(
    frame: pd.DataFrame,
    *,
    threshold: float = 0.003,
    min_duration_h: int = 2,
) -> pd.DataFrame:
    """Find contiguous 1H windows where stablecoin pair deviates from 1.0."""
    if "timestamp" not in frame.columns or "close" not in frame.columns:
        raise ValueError("frame must contain timestamp and close")
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if min_duration_h < 1:
        raise ValueError("min_duration_h must be >= 1")

    data = frame.loc[:, ["timestamp", "close"]].copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True, errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data = data.dropna().sort_values("timestamp").reset_index(drop=True)
    data["deviation_pct"] = (data["close"] - 1.0).abs()
    data["active"] = data["deviation_pct"] > threshold

    events: list[dict[str, object]] = []
    start_idx: int | None = None
    for idx, active in enumerate(data["active"].tolist() + [False]):
        if active and start_idx is None:
            start_idx = idx
        elif not active and start_idx is not None:
            window = data.iloc[start_idx:idx]
            duration = len(window)
            if duration >= min_duration_h:
                events.append(
                    {
                        "timestamp": window["timestamp"].iloc[0],
                        "deviation_pct": float(window["deviation_pct"].max()),
                        "duration_h": int(duration),
                    }
                )
            start_idx = None

    return pd.DataFrame(events, columns=["timestamp", "deviation_pct", "duration_h"])
