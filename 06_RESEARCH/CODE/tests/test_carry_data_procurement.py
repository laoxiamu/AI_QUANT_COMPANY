from pathlib import Path

import pandas as pd
import pytest

from carry_data_procurement.events import detect_depeg_events
from carry_data_procurement.manifest import build_file_record
from carry_data_procurement.schemas import (
    normalize_kline_rows,
    validate_ohlcv_1h,
)


def test_binance_kline_rows_normalize_to_auditable_ohlcv_schema() -> None:
    rows = [
        [
            1577836800000,
            "100.0",
            "110.0",
            "90.0",
            "105.0",
            "12.5",
            1577840399999,
            "0",
            1,
            "0",
            "0",
            "0",
        ]
    ]

    frame = normalize_kline_rows(rows)

    assert frame.columns.tolist() == [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    assert frame["timestamp"].tolist() == [pd.Timestamp("2020-01-01T00:00:00Z")]
    assert frame["open"].tolist() == [100.0]


def test_validate_ohlcv_rejects_missing_hours_and_out_of_range_rows() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2020-01-01T00:00:00Z", "2020-01-01T02:00:00Z"],
                utc=True,
            ),
            "open": [1.0, 1.0],
            "high": [1.0, 1.0],
            "low": [1.0, 1.0],
            "close": [1.0, 1.0],
            "volume": [1.0, 1.0],
        }
    )

    report = validate_ohlcv_1h(
        frame,
        start=pd.Timestamp("2020-01-01T00:00:00Z"),
        end=pd.Timestamp("2020-01-01T02:00:00Z"),
    )

    assert not report.ok
    assert "missing_hours=1" in report.issues


def test_depeg_detector_requires_threshold_and_duration() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2020-01-01T00:00:00Z",
                    "2020-01-01T01:00:00Z",
                    "2020-01-01T02:00:00Z",
                    "2020-01-01T03:00:00Z",
                ],
                utc=True,
            ),
            "close": [1.0000, 1.0040, 1.0045, 1.0000],
        }
    )

    events = detect_depeg_events(frame, threshold=0.003, min_duration_h=2)

    assert events.to_dict("records") == [
        {
            "timestamp": pd.Timestamp("2020-01-01T01:00:00Z"),
            "deviation_pct": pytest.approx(0.0045),
            "duration_h": 2,
        }
    ]


def test_manifest_record_reports_rows_sha_and_time_range(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("timestamp,open\n2020-01-01T00:00:00Z,1.0\n", encoding="utf-8")
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2020-01-01T00:00:00Z"], utc=True),
            "open": [1.0],
        }
    )

    record = build_file_record(path, frame, source="unit-test")

    assert record["path"].endswith("sample.csv")
    assert record["rows"] == 1
    assert record["sha256"]
    assert record["start"] == "2020-01-01T00:00:00Z"
    assert record["end"] == "2020-01-01T00:00:00Z"
    assert record["source"] == "unit-test"
