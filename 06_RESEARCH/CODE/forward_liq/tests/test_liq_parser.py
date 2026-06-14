from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from forward_liq.liq_parser import parse_jsonl  # noqa: E402


def _message(
    *,
    symbol: str,
    side: str,
    qty: str,
    price: str,
    average_price: str,
    trade_ms: int,
) -> dict[str, object]:
    return {
        "e": "forceOrder",
        "E": trade_ms + 1,
        "o": {
            "s": symbol,
            "S": side,
            "o": "LIMIT",
            "f": "IOC",
            "q": qty,
            "p": price,
            "ap": average_price,
            "X": "FILLED",
            "T": trade_ms,
        },
    }


def test_parser_handles_sides_notional_bad_missing_and_duplicate_lines(tmp_path: Path) -> None:
    sell = _message(
        symbol="BTCUSDT",
        side="SELL",
        qty="2",
        price="90",
        average_price="100",
        trade_ms=1_700_000_000_000,
    )
    buy = _message(
        symbol="ETHUSDT",
        side="BUY",
        qty="3",
        price="50",
        average_price="0.000",
        trade_ms=1_700_000_060_000,
    )
    missing_qty = _message(
        symbol="SOLUSDT",
        side="SELL",
        qty="1",
        price="20",
        average_price="20",
        trade_ms=1_700_000_120_000,
    )
    del missing_qty["o"]["q"]  # type: ignore[index]

    path = tmp_path / "liquidations.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(sell),
                "{not-json",
                json.dumps(missing_qty),
                json.dumps(buy),
                json.dumps(sell, sort_keys=True),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    frame, report = parse_jsonl(path)

    assert list(frame.columns) == [
        "ts_utc",
        "symbol",
        "side",
        "qty",
        "price",
        "notional_usdt",
    ]
    assert frame["side"].tolist() == ["SELL", "BUY"]
    assert frame["price"].tolist() == pytest.approx([100.0, 50.0])
    assert frame["notional_usdt"].tolist() == pytest.approx([200.0, 150.0])
    assert isinstance(frame.loc[0, "ts_utc"], pd.Timestamp)
    assert str(frame["ts_utc"].dt.tz) == "UTC"

    assert report.total_lines == 5
    assert report.parsed_rows == 2
    assert report.bad_lines == 2
    assert report.duplicate_lines == 1
    assert report.bad_line_ratio == pytest.approx(0.4)
    assert report.errors_by_reason == {
        "invalid_json": 1,
        "missing_qty": 1,
    }


def test_parser_rejects_empty_required_values(tmp_path: Path) -> None:
    message = _message(
        symbol="",
        side="SELL",
        qty="1",
        price="20",
        average_price="20",
        trade_ms=1_700_000_000_000,
    )
    path = tmp_path / "empty_symbol.jsonl"
    path.write_text(json.dumps(message) + "\n", encoding="utf-8")

    frame, report = parse_jsonl(path)

    assert frame.empty
    assert report.bad_lines == 1
    assert report.errors_by_reason["missing_symbol"] == 1
