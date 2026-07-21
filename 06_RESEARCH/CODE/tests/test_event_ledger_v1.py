import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from event_ledger_v1 import (
    LEDGER_COLUMNS,
    compute_outcome_fields,
    init_ledger,
    upsert_scan_candidates,
    update_decision_fields,
    write_daily_snapshot,
)


def _candidate(symbol: str, *, funding=True, oi=True, price=False) -> dict:
    return {
        "symbol": symbol,
        "source": "funding_oi_squeeze",
        "event_type": "funding_oi_price_anomaly",
        "funding_per_settlement": -0.003 if funding else -0.0001,
        "interval_hours": 8,
        "funding_per_day": -0.009 if funding else -0.0003,
        "funding_8h": -0.003 if funding else -0.0001,
        "funding_est_next": None,
        "funding_seq_n_periods_over_threshold": 2 if funding else 0,
        "oi_usd_now": 300.0 if oi else 120.0,
        "oi_1h_ago": 280.0 if oi else 115.0,
        "oi_4h_ago": 250.0 if oi else 110.0,
        "oi_24h_ago": 100.0,
        "d_oi_1h_pct": 7.142857 if oi else 4.347826,
        "d_oi_4h_pct": 20.0 if oi else 9.090909,
        "d_oi_24h_ratio": 3.0 if oi else 1.2,
        "oi_24h_ratio": 3.0 if oi else 1.2,
        "price_now": 1.0,
        "chg_1h_pct": None,
        "chg_4h_pct": None,
        "chg24h_pct": 5.0 if price else -1.0,
        "dist_from_peak_pct": None,
        "quote_vol_24h_usd": 10_000_000.0,
        "spread_bp": None,
        "price_oi_quadrant": "价↓OI↑",
        "raw": {"fixture": symbol},
    }


def test_ledger_schema_inserts_all_frozen_fields_and_marks_near_miss(tmp_path: Path) -> None:
    db_path = tmp_path / "ledger.db"
    init_ledger(db_path)

    stats = upsert_scan_candidates(
        db_path,
        [_candidate("MISSUSDT", funding=True, oi=True, price=False)],
        scan_utc="20260721_0100",
        scanner_version="P0-RES-017",
        backfilled=False,
        scan_file="unit.json",
    )

    assert stats == {"inserted": 1, "updated": 0, "near_miss": 1, "rejected": 0}
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    columns = {row["name"] for row in con.execute("PRAGMA table_info(events)").fetchall()}
    assert set(LEDGER_COLUMNS).issubset(columns)
    row = con.execute("SELECT * FROM events").fetchone()
    assert row["decision"] == "near_miss"
    assert row["legs_passed"] == "2/3"
    assert row["backfilled"] == 0
    assert row["event_id"]
    assert row["cluster_id"] == row["event_id"]
    assert row["raw_response_sha256"]


def test_ledger_clusters_same_symbol_events_within_48h(tmp_path: Path) -> None:
    db_path = tmp_path / "ledger.db"
    first = upsert_scan_candidates(
        db_path,
        [_candidate("CLUSTERUSDT", funding=True, oi=True, price=True)],
        scan_utc="20260721_0100",
        scanner_version="P0-RES-017",
    )
    second = upsert_scan_candidates(
        db_path,
        [_candidate("CLUSTERUSDT", funding=True, oi=True, price=False)],
        scan_utc="20260722_0000",
        scanner_version="P0-RES-017",
    )

    assert first["inserted"] == 1
    assert second["inserted"] == 1
    con = sqlite3.connect(db_path)
    clusters = [row[0] for row in con.execute("SELECT cluster_id FROM events ORDER BY decision_ts_utc")]
    assert len(set(clusters)) == 1


def test_ledger_merges_duplicate_candidate_rows_under_frozen_event_key(tmp_path: Path) -> None:
    db_path = tmp_path / "ledger.db"
    first = {
        "symbol": "KORUUSDT",
        "source": "binance_announcement",
        "event_type": "futures_contract_size_adjustment",
        "article_code": "completed-code",
        "title": "completed adjustment",
        "raw": {"code": "completed-code"},
    }
    second = {
        "symbol": "KORUUSDT",
        "source": "binance_announcement",
        "event_type": "futures_contract_size_adjustment",
        "article_code": "will-adjust-code",
        "title": "will adjust",
        "raw": {"code": "will-adjust-code"},
    }

    stats = upsert_scan_candidates(
        db_path,
        [first, second],
        scan_utc="20260721_0100",
        scanner_version="P0-RES-017",
    )

    assert stats["inserted"] == 1
    assert stats["updated"] == 1
    con = sqlite3.connect(db_path)
    rows = con.execute("SELECT raw_candidate_json FROM events").fetchall()
    assert len(rows) == 1
    raw_items = json.loads(rows[0][0])
    assert [item["article_code"] for item in raw_items] == ["completed-code", "will-adjust-code"]


def test_update_decision_fields_validates_required_human_decision_fields(tmp_path: Path) -> None:
    db_path = tmp_path / "ledger.db"
    upsert_scan_candidates(
        db_path,
        [_candidate("SELECTUSDT", funding=True, oi=True, price=True)],
        scan_utc="20260721_0100",
        scanner_version="P0-RES-017",
    )
    con = sqlite3.connect(db_path)
    event_id = con.execute("SELECT event_id FROM events").fetchone()[0]

    with pytest.raises(ValueError, match="p_up"):
        update_decision_fields(db_path, event_id, decision="selected", p_up=None)

    update_decision_fields(
        db_path,
        event_id,
        decision="selected",
        p_up=0.61,
        expected_direction="up",
        expected_horizon_h=48,
        entry_rule="first tradable mark after decision_ts",
        exit_rule="exit at horizon",
        invalidation_rule="mechanical no-op for unit test",
        decision_reason="unit test selected row",
        gate0_capacity_pass=True,
        gate1_payer_pass=True,
    )
    row = con.execute("SELECT decision, p_up, expected_direction FROM events WHERE event_id=?", (event_id,)).fetchone()
    assert row == ("selected", 0.61, "up")


def test_resolver_rejects_outcome_timestamps_not_after_decision() -> None:
    fields = compute_outcome_fields(
        decision_ts_utc="2026-07-21T01:00:00Z",
        price_path=[
            {"ts_utc": "2026-07-21T01:00:00Z", "price": 1.0},
            {"ts_utc": "2026-07-21T02:00:00Z", "price": 1.1},
        ],
        oi_path=[],
        funding_path=[],
    )

    assert fields["outcome_status"] == "INVALID_LOOKAHEAD"
    assert fields["ret_1h_pct"] is None


def test_resolver_fills_returns_paths_and_cost_json_without_human_rules() -> None:
    fields = compute_outcome_fields(
        decision_ts_utc="2026-07-21T01:00:00Z",
        price_path=[
            {"ts_utc": "2026-07-21T02:00:00Z", "price": 100.0},
            {"ts_utc": "2026-07-21T03:00:00Z", "price": 102.0},
            {"ts_utc": "2026-07-21T06:00:00Z", "price": 99.0},
        ],
        oi_path=[{"ts_utc": "2026-07-21T02:00:00Z", "oi_usd": 10.0}],
        funding_path=[{"ts_utc": "2026-07-21T02:00:00Z", "fundingRate": -0.003}],
    )

    assert fields["outcome_status"] == "resolved"
    assert fields["ret_1h_pct"] == pytest.approx(2.0)
    assert fields["ret_4h_pct"] == pytest.approx(-1.0)
    assert fields["mae_pct"] == pytest.approx(-1.0)
    assert fields["mfe_pct"] == pytest.approx(2.0)
    assert json.loads(fields["oi_path_json"]) == [{"ts_utc": "2026-07-21T02:00:00Z", "oi_usd": 10.0}]
    assert json.loads(fields["net_r_at_cost"]) == {"0.0015": None, "0.003": None, "0.005": None, "0.01": None}


def test_daily_parquet_snapshot_writes_all_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "ledger.db"
    out_dir = tmp_path / "snapshots"
    upsert_scan_candidates(
        db_path,
        [_candidate("SNAPUSDT", funding=True, oi=False, price=True)],
        scan_utc="20260721_0100",
        scanner_version="P0-RES-017",
    )

    snapshot_path = write_daily_snapshot(db_path, out_dir, snapshot_date="20260721")

    assert snapshot_path.name == "event_ledger_20260721.parquet"
    frame = pd.read_parquet(snapshot_path)
    assert len(frame) == 1
    assert frame.iloc[0]["symbol"] == "SNAPUSDT"
