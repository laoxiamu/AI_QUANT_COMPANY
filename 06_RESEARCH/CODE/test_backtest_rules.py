"""Regression tests for pre-registered backtest execution rules."""

import importlib.util
from pathlib import Path
import unittest

import pandas as pd


MODULE_PATH = Path(__file__).with_name(
    "backtest_v5_sweep_choch_fvg_bull_v1.py"
)
SPEC = importlib.util.spec_from_file_location("backtest", MODULE_PATH)
BACKTEST = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BACKTEST)


def bars(rows: list[tuple[str, float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows, columns=["datetime", "open", "high", "low", "close"]
    ).assign(
        datetime=lambda frame: pd.to_datetime(frame["datetime"]),
        volume=0.0,
    )


def candidates(rows: list[tuple[str, str, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=["signal_time", "sweep_time", "entry_price", "stop_loss"],
    ).assign(
        signal_time=lambda frame: pd.to_datetime(frame["signal_time"]),
        sweep_time=lambda frame: pd.to_datetime(frame["sweep_time"]),
    )


class BacktestRuleTests(unittest.TestCase):
    def test_stop_wins_when_same_bar_hits_stop_and_targets(self) -> None:
        data = bars(
            [
                ("2026-01-01 00:00", 100, 101, 99, 100),
                ("2026-01-01 01:00", 100, 130, 80, 105),
            ]
        )
        signals = candidates(
            [("2026-01-01 00:00", "2025-12-31 23:00", 100, 90)]
        )
        result = BACKTEST.simulate(
            data,
            pd.DataFrame(
                columns=[
                    "datetime",
                    "funding_interval_hours",
                    "last_funding_rate",
                ]
            ),
            signals,
            data.datetime.iloc[0],
            data.datetime.iloc[-1],
            "TEST",
        )
        self.assertEqual(result.trades.iloc[0].exit_reason, "STOP")
        self.assertFalse(bool(result.trades.iloc[0].tp1_hit))

    def test_open_position_rejects_same_direction_signal(self) -> None:
        data = bars(
            [
                ("2026-01-01 00:00", 100, 101, 99, 100),
                ("2026-01-01 01:00", 100, 105, 95, 101),
                ("2026-01-01 02:00", 101, 106, 96, 102),
            ]
        )
        signals = candidates(
            [
                ("2026-01-01 00:00", "2025-12-31 23:00", 100, 80),
                ("2026-01-01 01:00", "2026-01-01 00:00", 101, 81),
            ]
        )
        result = BACKTEST.simulate(
            data,
            pd.DataFrame(
                columns=[
                    "datetime",
                    "funding_interval_hours",
                    "last_funding_rate",
                ]
            ),
            signals,
            data.datetime.iloc[0],
            data.datetime.iloc[-1],
            "TEST",
        )
        self.assertEqual(result.rejected_conflicts, 1)
        self.assertEqual(len(result.trades), 1)
        self.assertEqual(result.trades.iloc[0].exit_reason, "WINDOW_END")

    def test_positive_funding_rate_is_paid_by_long(self) -> None:
        data = bars(
            [
                ("2026-01-01 00:00", 100, 101, 99, 100),
                ("2026-01-01 01:00", 100, 105, 95, 100),
                ("2026-01-01 02:00", 100, 105, 95, 100),
            ]
        )
        funding = pd.DataFrame(
            {
                "datetime": pd.to_datetime(["2026-01-01 01:00"]),
                "funding_interval_hours": [8],
                "last_funding_rate": [0.001],
            }
        )
        signals = candidates(
            [("2026-01-01 00:00", "2025-12-31 23:00", 100, 80)]
        )
        result = BACKTEST.simulate(
            data,
            funding,
            signals,
            data.datetime.iloc[0],
            data.datetime.iloc[-1],
            "TEST",
        )
        self.assertGreater(result.trades.iloc[0].funding_paid, 0)


if __name__ == "__main__":
    unittest.main()
