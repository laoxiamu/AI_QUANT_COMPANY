#!/usr/bin/env python3
"""Parse Binance forceOrder JSONL into a normalized UTC DataFrame."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


OUTPUT_COLUMNS = [
    "ts_utc",
    "symbol",
    "side",
    "qty",
    "price",
    "notional_usdt",
]


@dataclass
class ParseReport:
    """Auditable line-level parser counters."""

    path: str
    total_lines: int = 0
    parsed_rows: int = 0
    bad_lines: int = 0
    duplicate_lines: int = 0
    errors_by_reason: Counter[str] = field(default_factory=Counter)

    @property
    def bad_line_ratio(self) -> float:
        return self.bad_lines / self.total_lines if self.total_lines else 0.0

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "total_lines": self.total_lines,
            "parsed_rows": self.parsed_rows,
            "bad_lines": self.bad_lines,
            "duplicate_lines": self.duplicate_lines,
            "bad_line_ratio": self.bad_line_ratio,
            "errors_by_reason": dict(sorted(self.errors_by_reason.items())),
        }


class InvalidForceOrder(ValueError):
    """A JSON value is not a usable Binance forceOrder message."""


def empty_liquidation_frame() -> pd.DataFrame:
    """Return an empty frame with stable output dtypes."""
    return pd.DataFrame(
        {
            "ts_utc": pd.Series([], dtype="datetime64[ms, UTC]"),
            "symbol": pd.Series([], dtype="string"),
            "side": pd.Series([], dtype="string"),
            "qty": pd.Series([], dtype="float64"),
            "price": pd.Series([], dtype="float64"),
            "notional_usdt": pd.Series([], dtype="float64"),
        }
    )


def _positive_float(value: Any, field_name: str) -> float:
    if value is None or value == "":
        raise InvalidForceOrder(f"missing_{field_name}")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise InvalidForceOrder(f"invalid_{field_name}") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise InvalidForceOrder(f"invalid_{field_name}")
    return parsed


def _select_price(order: dict[str, Any]) -> float:
    average_price = order.get("ap")
    if average_price is not None and str(average_price).strip():
        try:
            parsed_average = float(average_price)
        except (TypeError, ValueError) as exc:
            raise InvalidForceOrder("invalid_ap") from exc
        if not math.isfinite(parsed_average) or parsed_average < 0:
            raise InvalidForceOrder("invalid_ap")
        if parsed_average > 0:
            return parsed_average
    return _positive_float(order.get("p"), "p")


def normalize_force_order(payload: Any) -> dict[str, object]:
    """Validate and normalize one decoded forceOrder payload."""
    if not isinstance(payload, dict):
        raise InvalidForceOrder("not_object")
    if payload.get("e") != "forceOrder":
        raise InvalidForceOrder("not_force_order")

    order = payload.get("o")
    if not isinstance(order, dict):
        raise InvalidForceOrder("missing_order")

    symbol_value = order.get("s")
    if not isinstance(symbol_value, str) or not symbol_value.strip():
        raise InvalidForceOrder("missing_symbol")
    symbol = symbol_value.strip().upper()

    side_value = order.get("S")
    if not isinstance(side_value, str):
        raise InvalidForceOrder("missing_side")
    side = side_value.strip().upper()
    if side not in {"SELL", "BUY"}:
        raise InvalidForceOrder("invalid_side")

    qty = _positive_float(order.get("q"), "qty")
    price = _select_price(order)

    trade_ms = order.get("T")
    if trade_ms is None or trade_ms == "":
        raise InvalidForceOrder("missing_trade_time")
    try:
        trade_ms_int = int(trade_ms)
        ts_utc = pd.to_datetime(trade_ms_int, unit="ms", utc=True)
    except (TypeError, ValueError, OverflowError, pd.errors.OutOfBoundsDatetime) as exc:
        raise InvalidForceOrder("invalid_trade_time") from exc
    if pd.isna(ts_utc):
        raise InvalidForceOrder("invalid_trade_time")

    return {
        "ts_utc": ts_utc,
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "price": price,
        "notional_usdt": price * qty,
    }


def parse_jsonl(path: str | Path) -> tuple[pd.DataFrame, ParseReport]:
    """Parse one JSONL file, skipping and counting invalid or duplicate lines."""
    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(f"JSONL file not found: {input_path}")

    report = ParseReport(path=str(input_path))
    rows: list[dict[str, object]] = []
    seen_payload_hashes: set[str] = set()

    with input_path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for raw_line in handle:
            report.total_lines += 1
            stripped = raw_line.strip()
            if not stripped:
                report.bad_lines += 1
                report.errors_by_reason["empty_line"] += 1
                continue

            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                report.bad_lines += 1
                report.errors_by_reason["invalid_json"] += 1
                continue

            try:
                row = normalize_force_order(payload)
            except InvalidForceOrder as exc:
                report.bad_lines += 1
                report.errors_by_reason[str(exc)] += 1
                continue

            canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if payload_hash in seen_payload_hashes:
                report.duplicate_lines += 1
                continue
            seen_payload_hashes.add(payload_hash)
            row["_payload_sha256"] = payload_hash
            rows.append(row)

    if rows:
        frame = pd.DataFrame(rows, columns=[*OUTPUT_COLUMNS, "_payload_sha256"])
        frame["ts_utc"] = pd.to_datetime(frame["ts_utc"], utc=True)
        frame = frame.sort_values(["ts_utc", "symbol", "side"], kind="stable").reset_index(drop=True)
        payload_hashes = frame.pop("_payload_sha256").tolist()
    else:
        frame = empty_liquidation_frame()
        payload_hashes = []

    report.parsed_rows = len(frame)
    frame.attrs["parse_report"] = report.as_dict()
    frame.attrs["payload_sha256"] = payload_hashes
    return frame, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl_path", type=Path)
    parser.add_argument(
        "--output-csv",
        type=Path,
        help="Optional normalized CSV output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    frame, report = parse_jsonl(args.jsonl_path)
    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(args.output_csv, index=False)
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
