"""Tests for Binance USD-M point-in-time universe helpers."""

from pathlib import Path
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_universe_pit import pit_symbols_for_date


def test_pit_symbols_exclude_future_and_delisted_contracts() -> None:
    universe = pd.DataFrame(
        [
            {
                "symbol": "OLDUSDT",
                "onboard_date": "2020-01-01",
                "delist_date": "2020-02-01",
                "source": "synthetic",
            },
            {
                "symbol": "LIVEUSDT",
                "onboard_date": "2020-01-15",
                "delist_date": "",
                "source": "synthetic",
            },
            {
                "symbol": "FUTUREUSDT",
                "onboard_date": "2020-03-01",
                "delist_date": "",
                "source": "synthetic",
            },
        ]
    )

    assert pit_symbols_for_date(universe, "2019-12-31") == []
    assert pit_symbols_for_date(universe, "2020-01-01") == ["OLDUSDT"]
    assert pit_symbols_for_date(universe, "2020-01-15") == ["LIVEUSDT", "OLDUSDT"]
    assert pit_symbols_for_date(universe, "2020-02-01") == ["LIVEUSDT"]


def test_pit_symbols_can_read_csv_path(tmp_path: Path) -> None:
    path = tmp_path / "universe.csv"
    path.write_text(
        "symbol,onboard_date,delist_date,source\n"
        "BTCUSDT,2019-09-08,,synthetic\n"
        "DELISTEDUSDT,2020-01-01,2021-01-01,synthetic\n",
        encoding="utf-8",
    )

    assert pit_symbols_for_date(path, "2020-06-01") == ["BTCUSDT", "DELISTEDUSDT"]
    assert pit_symbols_for_date(path, "2021-01-01") == ["BTCUSDT"]
