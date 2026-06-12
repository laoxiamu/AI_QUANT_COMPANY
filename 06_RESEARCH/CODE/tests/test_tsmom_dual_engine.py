"""Synthetic tests for the TSMOM dual-engine expansion."""

from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tsmom_dual_engine import (
    LOOKBACK_BARS,
    desired_position,
    funding_payment,
    prepare_bars,
    read_csv_until_cutoff,
    run_backtest,
)


def _trend_frame(up: bool = True) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=LOOKBACK_BARS + 5, freq="4h")
    if up:
        close = [100.0 + index for index in range(len(dates))]
    else:
        close = [1000.0 - index for index in range(len(dates))]
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close,
            "high": [value + 1 for value in close],
            "low": [value - 1 for value in close],
            "close": close,
            "volume": [0.0] * len(dates),
        }
    )


def test_mirror_desired_position_symmetry() -> None:
    assert desired_position("L", 1, True, True, True) == 1
    assert desired_position("S", 1, True, True, True) == 0
    assert desired_position("L", -1, True, False, True) == 0
    assert desired_position("S", -1, True, False, True) == -1
    assert desired_position("L", 1, True, pd.NA, True) == 0
    assert desired_position("S", -1, True, pd.NA, True) == 0


def test_signal_mirror_on_constructed_price_paths() -> None:
    up = prepare_bars(
        _trend_frame(up=True),
        symbol="BTC",
        onboard_date=pd.Timestamp("2019-01-01"),
        engine="L",
    )
    down = prepare_bars(
        _trend_frame(up=False),
        symbol="BTC",
        onboard_date=pd.Timestamp("2019-01-01"),
        engine="S",
    )
    assert up.loc[LOOKBACK_BARS, "signal"] == 1
    assert down.loc[LOOKBACK_BARS, "signal"] == -1


def test_pit_rule_blocks_until_540_bars_and_onboard_warmup() -> None:
    bars = prepare_bars(
        _trend_frame(up=True),
        symbol="BTC",
        onboard_date=pd.Timestamp("2020-06-01"),
        engine="L",
    )
    assert not bool(bars.loc[LOOKBACK_BARS, "pit_eligible"])
    eligible_rows = bars[bars["pit_eligible"]]
    assert eligible_rows.empty


def test_funding_payment_direction() -> None:
    assert funding_payment(1, 2.0, 100.0, 0.001) == pytest.approx(0.2)
    assert funding_payment(-1, 2.0, 100.0, 0.001) == pytest.approx(-0.2)
    assert funding_payment(-1, 2.0, 100.0, -0.001) == pytest.approx(0.2)


def test_cutoff_reader_does_not_parse_rows_after_expected_snapshot(
    tmp_path: Path,
) -> None:
    path = tmp_path / "BTCUSDT_MARK_4H.csv"
    path.write_text(
        "\n".join(
            [
                "datetime,open,high,low,close,volume",
                "2024-12-09 16:00:00,1,2,1,2,10",
                "2024-12-09 20:00:00,2,3,2,3,11",
                "2024-12-10 00:00:00,NOT_NUMERIC,4,3,4,12",
            ]
        )
        + "\n"
    )
    frame = read_csv_until_cutoff(
        path,
        required_columns=("datetime", "open", "high", "low", "close", "volume"),
        expected_rows=2,
    )
    assert len(frame) == 2
    assert frame["datetime"].max() == pd.Timestamp("2024-12-09 20:00:00")
    assert frame["open"].tolist() == [1, 2]


def test_backtest_short_receives_positive_funding_as_income() -> None:
    dates = pd.date_range("2022-01-01", periods=3, freq="4h")
    bars = pd.DataFrame(
        {
            "datetime": dates,
            "open": [100.0, 100.0, 99.0],
            "high": [101.0, 101.0, 100.0],
            "low": [99.0, 99.0, 98.0],
            "close": [100.0, 99.0, 98.0],
            "execution_target": [0, -1, 0],
            "signal_time": dates - pd.Timedelta(hours=4),
            "execution_signal": [0, -1, -1],
            "execution_adx": [30.0, 30.0, 30.0],
            "execution_macro_bull": [False, False, False],
            "execution_pit_eligible": [True, True, True],
        }
    )
    funding = pd.DataFrame(
        {
            "datetime": [dates[2]],
            "last_funding_rate": [0.001],
        }
    )
    result = run_backtest(
        {"BTC": bars},
        {"BTC": funding},
        label="tsmom_dual_S",
        include_fees=False,
        include_slippage=False,
        include_funding=True,
    )
    assert len(result.trades) == 1
    assert result.trades.iloc[0]["funding_cost"] < 0
