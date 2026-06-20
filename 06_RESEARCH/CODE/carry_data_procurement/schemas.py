"""Schema normalization and validation for Binance 1H kline datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import pandas as pd


OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
PRICE_COLUMNS = ["timestamp", "close"]


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    rows: int
    start: str | None
    end: str | None
    null_rates: dict[str, float]
    issues: list[str]


def _utc(ts: pd.Timestamp | str) -> pd.Timestamp:
    parsed = pd.Timestamp(ts)
    if parsed.tzinfo is None:
        return parsed.tz_localize("UTC")
    return parsed.tz_convert("UTC")


def normalize_kline_rows(rows: Iterable[Sequence[object]]) -> pd.DataFrame:
    """Convert Binance REST/data.vision kline arrays to canonical OHLCV."""
    frame = pd.DataFrame(list(rows))
    if frame.empty:
        return pd.DataFrame(columns=OHLCV_COLUMNS)
    # Drop header rows if present (data.binance.vision CSVs sometimes include headers)
    if not str(frame.iloc[0, 0]).lstrip("-").isdigit():
        frame = frame.iloc[1:].reset_index(drop=True)
    if frame.empty or frame.shape[1] < 6:
        raise ValueError("Binance kline rows must have at least 6 columns")

    out = pd.DataFrame(
        {
            # pd.to_numeric first: pandas 3.x changed string→datetime parsing under unit="ms"
            "timestamp": pd.to_datetime(pd.to_numeric(frame.iloc[:, 0], errors="coerce"), unit="ms", utc=True),
            "open": pd.to_numeric(frame.iloc[:, 1], errors="coerce"),
            "high": pd.to_numeric(frame.iloc[:, 2], errors="coerce"),
            "low": pd.to_numeric(frame.iloc[:, 3], errors="coerce"),
            "close": pd.to_numeric(frame.iloc[:, 4], errors="coerce"),
            "volume": pd.to_numeric(frame.iloc[:, 5], errors="coerce"),
        }
    )
    return out.sort_values("timestamp").drop_duplicates("timestamp", keep="last")


def normalize_index_rows(rows: Iterable[Sequence[object]]) -> pd.DataFrame:
    """Convert Binance index-price kline arrays to timestamp/close."""
    frame = pd.DataFrame(list(rows))
    if frame.empty:
        return pd.DataFrame(columns=PRICE_COLUMNS)
    if not str(frame.iloc[0, 0]).lstrip("-").isdigit():
        frame = frame.iloc[1:].reset_index(drop=True)
    if frame.empty or frame.shape[1] < 5:
        raise ValueError("Binance index kline rows must have at least 5 columns")
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(pd.to_numeric(frame.iloc[:, 0], errors="coerce"), unit="ms", utc=True),
            "close": pd.to_numeric(frame.iloc[:, 4], errors="coerce"),
        }
    )
    return out.sort_values("timestamp").drop_duplicates("timestamp", keep="last")


def validate_ohlcv_1h(
    frame: pd.DataFrame,
    *,
    start: pd.Timestamp | str,
    end: pd.Timestamp | str,
    max_null_rate: float = 0.0,
) -> ValidationReport:
    return _validate_time_series(
        frame,
        required=OHLCV_COLUMNS,
        start=start,
        end=end,
        max_null_rate=max_null_rate,
        require_hourly=True,
    )


def validate_price_1h(
    frame: pd.DataFrame,
    *,
    start: pd.Timestamp | str,
    end: pd.Timestamp | str,
    max_null_rate: float = 0.0,
) -> ValidationReport:
    return _validate_time_series(
        frame,
        required=PRICE_COLUMNS,
        start=start,
        end=end,
        max_null_rate=max_null_rate,
        require_hourly=True,
    )


def _validate_time_series(
    frame: pd.DataFrame,
    *,
    required: list[str],
    start: pd.Timestamp | str,
    end: pd.Timestamp | str,
    max_null_rate: float,
    require_hourly: bool,
) -> ValidationReport:
    issues: list[str] = []
    missing = [column for column in required if column not in frame.columns]
    if missing:
        issues.append(f"missing_columns={','.join(missing)}")
        return ValidationReport(False, len(frame), None, None, {}, issues)

    data = frame.loc[:, required].copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True, errors="coerce")
    for column in required:
        if column != "timestamp":
            data[column] = pd.to_numeric(data[column], errors="coerce")

    if data["timestamp"].isna().any():
        issues.append(f"invalid_timestamps={int(data['timestamp'].isna().sum())}")
    data = data.dropna(subset=["timestamp"]).sort_values("timestamp")

    start_ts = _utc(start)
    end_ts = _utc(end)
    if data.empty:
        actual_start = None
        actual_end = None
        issues.append("empty")
    else:
        actual_start_ts = data["timestamp"].iloc[0]
        actual_end_ts = data["timestamp"].iloc[-1]
        actual_start = actual_start_ts.isoformat().replace("+00:00", "Z")
        actual_end = actual_end_ts.isoformat().replace("+00:00", "Z")
        if actual_start_ts < start_ts or actual_end_ts > end_ts:
            issues.append("outside_requested_range")
        if actual_start_ts != start_ts:
            issues.append(f"start_mismatch={actual_start}")
        if actual_end_ts != end_ts:
            issues.append(f"end_mismatch={actual_end}")

    null_rates = {
        column: float(data[column].isna().mean()) for column in required if column != "timestamp"
    }
    for column, rate in null_rates.items():
        if rate > max_null_rate:
            issues.append(f"{column}_null_rate={rate:.6f}")

    if data["timestamp"].duplicated().any():
        issues.append(f"duplicate_timestamps={int(data['timestamp'].duplicated().sum())}")

    if require_hourly and not data.empty:
        expected = pd.date_range(start_ts, end_ts, freq="1h")
        observed = pd.DatetimeIndex(data["timestamp"])
        missing_hours = expected.difference(observed)
        extra_hours = observed.difference(expected)
        if len(missing_hours):
            issues.append(f"missing_hours={len(missing_hours)}")
        if len(extra_hours):
            issues.append(f"extra_hours={len(extra_hours)}")

    return ValidationReport(
        ok=not issues,
        rows=len(data),
        start=actual_start,
        end=actual_end,
        null_rates=null_rates,
        issues=issues,
    )
