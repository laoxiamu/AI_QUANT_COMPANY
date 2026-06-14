from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from forward_liq.forward_event_counter import (  # noqa: E402
    CounterConfig,
    compute_candidate_events,
    parse_files,
    run_counter,
)
from forward_liq.liq_parser import parse_jsonl  # noqa: E402


def _message(
    timestamp: str,
    notional: float,
    *,
    symbol: str = "BTCUSDT",
    side: str = "SELL",
) -> dict[str, object]:
    import pandas as pd

    trade_ms = int(pd.Timestamp(timestamp).timestamp() * 1000)
    return {
        "e": "forceOrder",
        "E": trade_ms,
        "o": {
            "s": symbol,
            "S": side,
            "q": str(notional),
            "p": "1",
            "ap": "1",
            "T": trade_ms,
        },
    }


def _write_jsonl(path: Path, messages: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(message) + "\n" for message in messages),
        encoding="utf-8",
    )


def test_known_jsonl_yields_two_distinct_pulse_candidates(tmp_path: Path) -> None:
    messages = [
        _message("2026-01-01T00:00:00Z", 10),
        _message("2026-01-01T02:00:00Z", 10),
        _message("2026-01-01T04:00:00Z", 30),
        _message("2026-01-01T04:10:00Z", 5),
        _message("2026-01-01T05:00:00Z", 1, side="BUY"),
        _message("2026-01-01T06:00:00Z", 5),
        _message("2026-01-01T08:00:00Z", 40),
        _message("2026-01-01T08:05:00Z", 1_000, symbol="XRPUSDT"),
    ]
    path = tmp_path / "known.jsonl"
    _write_jsonl(path, messages)
    frame, _ = parse_jsonl(path)

    result = run_counter(
        frame,
        CounterConfig(
            window="1h",
            quantile=0.5,
            min_history=2,
            n_min=3,
            count_mode="episode_start",
        ),
    )

    assert result.events["ts_utc"].dt.strftime("%H:%M").tolist() == ["04:00", "08:00"]
    assert result.overall_summary["cumulative_n"] == 2
    assert result.overall_summary["remaining_n"] == 1
    assert result.overall_summary["event_rate_per_elapsed_day"] == pytest.approx(6.0)
    assert result.overall_summary["projected_target_date"] == "2026-01-02"
    btc_month = result.monthly_counts.query(
        "symbol == 'BTCUSDT' and month_utc == '2026-01'"
    )
    assert btc_month["candidate_events"].item() == 2


def test_quantile_boundary_is_inclusive_and_has_no_current_value_lookahead(tmp_path: Path) -> None:
    messages = [
        _message("2026-01-01T00:00:00Z", 10),
        _message("2026-01-01T02:00:00Z", 20),
        _message("2026-01-01T04:00:00Z", 20),
    ]
    path = tmp_path / "boundary.jsonl"
    _write_jsonl(path, messages)
    frame, _ = parse_jsonl(path)

    signals, events = compute_candidate_events(
        frame,
        CounterConfig(
            window="1h",
            quantile=1.0,
            min_history=2,
            count_mode="all_hits",
        ),
    )

    third = signals.iloc[2]
    assert third["historical_quantile"] == pytest.approx(20.0)
    assert third["rolling_sell_notional"] == pytest.approx(20.0)
    assert bool(third["qualifies"]) is True
    assert len(events) == 1


def test_invalid_placeholder_parameters_are_rejected() -> None:
    with pytest.raises(ValueError, match="quantile"):
        CounterConfig(quantile=1.01).validate()
    with pytest.raises(ValueError, match="min_history"):
        CounterConfig(min_history=0).validate()


def test_cross_file_dedup_uses_full_payload_not_only_normalized_columns(tmp_path: Path) -> None:
    original = _message("2026-01-01T00:00:00Z", 10)
    distinct_same_output = json.loads(json.dumps(original))
    distinct_same_output["E"] = int(distinct_same_output["E"]) + 1

    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    _write_jsonl(first, [original])
    _write_jsonl(second, [original, distinct_same_output])

    frame, reports, cross_file_duplicates = parse_files([first, second])

    assert len(reports) == 2
    assert cross_file_duplicates == 1
    assert len(frame) == 2
