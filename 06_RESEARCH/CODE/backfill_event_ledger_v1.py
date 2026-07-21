#!/usr/bin/env python3
"""Backfill EVENT_LEDGER_V1 from historical thesis_hf_scan JSON snapshots."""

from __future__ import annotations

import argparse
import glob
import json
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlencode

from event_ledger_v1 import DEFAULT_LEDGER_DB, DEFAULT_SNAPSHOT_DIR, parse_utc, upsert_scan_candidates, write_daily_snapshot
from thesis_hf_scan import (
    BASE,
    count_funding_sequence_over_threshold,
    infer_funding_interval_hours,
    make_fetchers,
    normalize_funding_per_day,
    unset_proxy_env,
)


DEFAULT_SCAN_GLOB = str(Path(__file__).resolve().parent / "output" / "thesis_hf_scan_*.json")


def _ms(dt) -> int:
    return int(dt.timestamp() * 1000)


def enrich_legacy_funding_candidate(candidate: dict, scan_utc: str, fetch_json) -> dict:
    item = dict(candidate)
    if item.get("source", "funding_oi_squeeze") != "funding_oi_squeeze":
        return item
    if item.get("interval_hours") is not None and item.get("funding_per_day") is not None:
        return item
    symbol = item.get("symbol")
    rate = item.get("funding_per_settlement", item.get("funding_8h"))
    if not symbol or rate is None:
        return item
    decision_dt = parse_utc(scan_utc)
    params = urlencode(
        {
            "symbol": symbol,
            "startTime": _ms(decision_dt - timedelta(hours=72)),
            "endTime": _ms(decision_dt) + 1,
            "limit": 20,
        }
    )
    history = fetch_json(f"{BASE}/fapi/v1/fundingRate?{params}")
    interval_hours = infer_funding_interval_hours(history)
    item["funding_per_settlement"] = float(rate)
    item["interval_hours"] = interval_hours
    item["funding_per_day"] = normalize_funding_per_day(float(rate), interval_hours)
    item["funding_seq_n_periods_over_threshold"] = count_funding_sequence_over_threshold(
        history,
        interval_hours,
    )
    return item


def load_scan(path: Path, fetch_json=None) -> tuple[str, str, list[dict]]:
    payload = json.loads(path.read_text())
    scan_utc = payload["scan_utc"]
    scanner_version = payload.get("schema_version") or "legacy_pre_p0res016"
    candidates = payload.get("candidates") or []
    normalized = []
    for candidate in candidates:
        item = dict(candidate)
        if "source" not in item:
            item["source"] = "funding_oi_squeeze"
            item["event_type"] = "funding_oi_price_anomaly"
        if fetch_json is not None:
            item = enrich_legacy_funding_candidate(item, scan_utc, fetch_json)
        normalized.append(item)
    return scan_utc, scanner_version, normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-glob", default=DEFAULT_SCAN_GLOB)
    parser.add_argument("--ledger-db", default=str(DEFAULT_LEDGER_DB))
    parser.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))
    parser.add_argument("--fetch-via-ssh-sg", action="store_true", help="用SG通道补旧快照funding周期字段")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    unset_proxy_env()
    fetch_json = None
    if args.fetch_via_ssh_sg:
        fetch_json, _ = make_fetchers(fetch_via_ssh_sg=True)
    totals = {"inserted": 0, "updated": 0, "near_miss": 0, "rejected": 0, "files": 0, "candidates": 0}
    snapshot_dates = set()
    for scan_path in sorted(Path(path) for path in glob.glob(args.scan_glob)):
        scan_utc, scanner_version, candidates = load_scan(scan_path, fetch_json=fetch_json)
        stats = upsert_scan_candidates(
            args.ledger_db,
            candidates,
            scan_utc=scan_utc,
            scanner_version=scanner_version,
            backfilled=True,
            scan_file=str(scan_path),
        )
        totals["files"] += 1
        totals["candidates"] += len(candidates)
        snapshot_dates.add(scan_utc[:8])
        for key in ("inserted", "updated", "near_miss", "rejected"):
            totals[key] += stats[key]
    snapshots = []
    for snapshot_date in sorted(snapshot_dates):
        snapshots.append(str(write_daily_snapshot(args.ledger_db, args.snapshot_dir, snapshot_date=snapshot_date)))
    print(json.dumps({**totals, "snapshots": snapshots}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
