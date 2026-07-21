#!/usr/bin/env python3
"""Resolve due EVENT_LEDGER_V1 rows using only post-decision market timestamps."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlencode

from event_ledger_v1 import (
    DEFAULT_LEDGER_DB,
    apply_outcome_fields,
    compute_outcome_fields,
    parse_utc,
    utc_now_iso,
    write_daily_snapshot,
)
from thesis_hf_scan import BASE, make_fetchers, unset_proxy_env


HORIZON_HOURS = 48


def _ms(dt) -> int:
    return int(dt.timestamp() * 1000)


def _price_path(fetch_json, symbol: str, decision_ts_utc: str) -> list[dict]:
    decision_dt = parse_utc(decision_ts_utc)
    params = urlencode(
        {
            "symbol": symbol,
            "interval": "1h",
            "startTime": _ms(decision_dt) + 1,
            "endTime": _ms(decision_dt + timedelta(hours=HORIZON_HOURS + 2)),
            "limit": 60,
        }
    )
    rows = fetch_json(f"{BASE}/fapi/v1/markPriceKlines?{params}")
    path = []
    for row in rows or []:
        path.append({"ts_utc": iso_utc_from_ms(int(row[0])), "price": float(row[4])})
    return path


def _oi_path(fetch_json, symbol: str, decision_ts_utc: str) -> list[dict]:
    decision_dt = parse_utc(decision_ts_utc)
    params = urlencode(
        {
            "symbol": symbol,
            "period": "1h",
            "startTime": _ms(decision_dt) + 1,
            "endTime": _ms(decision_dt + timedelta(hours=HORIZON_HOURS + 2)),
            "limit": 60,
        }
    )
    rows = fetch_json(f"{BASE}/futures/data/openInterestHist?{params}")
    path = []
    for row in rows or []:
        if row.get("timestamp") is None:
            continue
        path.append(
            {
                "ts_utc": iso_utc_from_ms(int(row["timestamp"])),
                "oi_usd": float(row["sumOpenInterestValue"]),
            }
        )
    return path


def _funding_path(fetch_json, symbol: str, decision_ts_utc: str) -> list[dict]:
    decision_dt = parse_utc(decision_ts_utc)
    params = urlencode(
        {
            "symbol": symbol,
            "startTime": _ms(decision_dt) + 1,
            "endTime": _ms(decision_dt + timedelta(hours=HORIZON_HOURS + 2)),
            "limit": 100,
        }
    )
    rows = fetch_json(f"{BASE}/fapi/v1/fundingRate?{params}")
    path = []
    for row in rows or []:
        if row.get("fundingTime") is None:
            continue
        path.append(
            {
                "ts_utc": iso_utc_from_ms(int(row["fundingTime"])),
                "fundingRate": float(row["fundingRate"]),
            }
        )
    return path


def iso_utc_from_ms(ms: int) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def due_rows(db_path: str | Path, *, include_backfilled: bool, limit: int | None) -> list[sqlite3.Row]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    filters = ["source='funding_oi_squeeze'", "outcome_status IS NULL"]
    if not include_backfilled:
        filters.append("backfilled=0")
    sql = "SELECT * FROM events WHERE " + " AND ".join(filters) + " ORDER BY decision_ts_utc"
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    return con.execute(sql).fetchall()


def resolve_due_events(db_path: str | Path, fetch_json, *, include_backfilled: bool = False, limit: int | None = None) -> dict:
    stats = {"resolved": 0, "invalid_lookahead": 0, "no_data": 0, "failed": 0}
    for row in due_rows(db_path, include_backfilled=include_backfilled, limit=limit):
        symbol = row["symbol"]
        try:
            price_path = _price_path(fetch_json, symbol, row["decision_ts_utc"])
            oi_path = _oi_path(fetch_json, symbol, row["decision_ts_utc"])
            funding_path = _funding_path(fetch_json, symbol, row["decision_ts_utc"])
            fields = compute_outcome_fields(
                decision_ts_utc=row["decision_ts_utc"],
                price_path=price_path,
                oi_path=oi_path,
                funding_path=funding_path,
                expected_direction=row["expected_direction"],
                expected_horizon_h=row["expected_horizon_h"],
            )
            apply_outcome_fields(db_path, row["event_id"], fields)
            if fields["outcome_status"] == "INVALID_LOOKAHEAD":
                stats["invalid_lookahead"] += 1
            elif fields["outcome_status"] == "NO_OUTCOME_DATA":
                stats["no_data"] += 1
            else:
                stats["resolved"] += 1
        except Exception as exc:  # noqa: BLE001 - per-event fetch failures are recorded and counted
            apply_outcome_fields(
                db_path,
                row["event_id"],
                {
                    "outcome_status": "RESOLVE_ERROR",
                    "resolver_version": "EVENT_LEDGER_V1_RESOLVER_20260721",
                    "resolved_at_utc": utc_now_iso(),
                    "net_r_at_cost": json.dumps({"error": str(exc)[:180]}, ensure_ascii=False),
                },
            )
            stats["failed"] += 1
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-db", default=str(DEFAULT_LEDGER_DB))
    parser.add_argument("--fetch-via-ssh-sg", action="store_true")
    parser.add_argument("--include-backfilled", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--snapshot-dir", default=str(DEFAULT_LEDGER_DB.parent / "snapshots"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    unset_proxy_env()
    fetch_json, _ = make_fetchers(fetch_via_ssh_sg=args.fetch_via_ssh_sg)
    stats = resolve_due_events(
        args.ledger_db,
        fetch_json,
        include_backfilled=args.include_backfilled,
        limit=args.limit,
    )
    snapshot = write_daily_snapshot(args.ledger_db, args.snapshot_dir)
    print(json.dumps({**stats, "snapshot": str(snapshot)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
