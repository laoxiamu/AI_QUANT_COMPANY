from pathlib import Path

import pandas as pd
import pytest

from carry.data import load_symbol_data


def test_loader_normalizes_utc_skips_bad_rows_and_applies_strict_cutoff(
    tmp_path: Path,
) -> None:
    (tmp_path / "BTCUSDT_FUNDING_8H.csv").write_text(
        "datetime,last_funding_rate\n"
        "2024-12-09T08:00:00Z,0.0001\n"
        "malformed,row,with,extra,fields\n"
        "2024-12-09T16:00:00Z,not-a-number\n"
        "2024-12-10T00:00:00Z,0.0002\n",
        encoding="utf-8",
    )
    (tmp_path / "BTCUSDT_MARK_1H.csv").write_text(
        "datetime,close\n"
        "2024-12-09T08:00:00+00:00,100\n"
        "bad-time,101\n"
        "2024-12-09T09:00:00+00:00,102\n"
        "2024-12-10T00:00:00+00:00,103\n",
        encoding="utf-8",
    )

    loaded = load_symbol_data(tmp_path, "BTCUSDT")

    assert loaded.funding["timestamp"].tolist() == [
        pd.Timestamp("2024-12-09T08:00:00Z")
    ]
    assert loaded.mark["timestamp"].tolist() == [
        pd.Timestamp("2024-12-09T08:00:00Z"),
        pd.Timestamp("2024-12-09T09:00:00Z"),
    ]
    assert str(loaded.funding["timestamp"].dt.tz) == "UTC"
    assert loaded.audit["funding"]["invalid_rows"] == 2
    assert loaded.audit["funding"]["cutoff_rows"] == 1
    assert loaded.audit["mark"]["invalid_rows"] == 1
    assert loaded.audit["mark"]["cutoff_rows"] == 1


def test_loader_rejects_holdout_paths(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="Holdout"):
        load_symbol_data(tmp_path / "HOLDOUT", "BTCUSDT")


def test_loader_rejects_cutoffs_after_frozen_date(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="later than frozen"):
        load_symbol_data(
            tmp_path,
            "BTCUSDT",
            cutoff="2024-12-11T00:00:00Z",
        )
