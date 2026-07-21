#!/usr/bin/env python3
"""EVENT_LEDGER_V1 storage, writer, and resolver helpers."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd


RESEARCH_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_DIR = RESEARCH_DIR / "DATA" / "EVENT_LEDGER"
DEFAULT_LEDGER_DB = DEFAULT_LEDGER_DIR / "ledger.db"
DEFAULT_SNAPSHOT_DIR = DEFAULT_LEDGER_DIR / "snapshots"
RESOLVER_VERSION = "EVENT_LEDGER_V1_RESOLVER_20260721"
FUNDING_LEG_DAILY_THRESHOLD = -0.009
OI_LEG_RATIO_THRESHOLD = 2.0
COST_RATES = (0.0015, 0.003, 0.005, 0.01)

SCHEMA_COLUMNS = [
    "event_id",
    "decision_ts_utc",
    "data_asof_utc",
    "scanner_version",
    "raw_response_sha256",
    "source",
    "funding_per_settlement",
    "interval_hours",
    "funding_per_day",
    "funding_est_next",
    "funding_seq_n_periods_over_threshold",
    "oi_usd_now",
    "oi_1h_ago",
    "oi_4h_ago",
    "oi_24h_ago",
    "d_oi_1h_pct",
    "d_oi_4h_pct",
    "d_oi_24h_ratio",
    "price_now",
    "chg_1h_pct",
    "chg_4h_pct",
    "chg_24h_pct",
    "dist_from_peak_pct",
    "quote_vol_24h_usd",
    "spread_bp",
    "price_oi_quadrant",
    "decision",
    "decision_reason",
    "gate0_capacity_pass",
    "gate1_payer_pass",
    "legs_passed",
    "p_up",
    "expected_direction",
    "expected_horizon_h",
    "entry_rule",
    "exit_rule",
    "invalidation_rule",
    "ret_1h_pct",
    "ret_2h_pct",
    "ret_4h_pct",
    "ret_8h_pct",
    "ret_24h_pct",
    "ret_48h_pct",
    "mae_pct",
    "mfe_pct",
    "oi_path_json",
    "funding_path_json",
    "net_r_at_cost",
    "invalidation_hit_ts",
    "resolver_version",
    "resolved_at_utc",
]

OPERATIONAL_COLUMNS = [
    "symbol",
    "event_type",
    "cluster_id",
    "backfilled",
    "outcome_status",
    "scan_file",
    "raw_candidate_json",
    "created_at_utc",
    "updated_at_utc",
]

LEDGER_COLUMNS = SCHEMA_COLUMNS + OPERATIONAL_COLUMNS

COLUMN_TYPES = {
    "event_id": "TEXT PRIMARY KEY",
    "decision_ts_utc": "TEXT NOT NULL",
    "data_asof_utc": "TEXT",
    "scanner_version": "TEXT NOT NULL",
    "raw_response_sha256": "TEXT NOT NULL",
    "source": "TEXT NOT NULL",
    "symbol": "TEXT NOT NULL",
    "event_type": "TEXT",
    "cluster_id": "TEXT NOT NULL",
    "backfilled": "INTEGER NOT NULL DEFAULT 0",
    "gate0_capacity_pass": "INTEGER",
    "gate1_payer_pass": "INTEGER",
    "raw_candidate_json": "TEXT",
    "created_at_utc": "TEXT NOT NULL",
    "updated_at_utc": "TEXT NOT NULL",
}

REAL_COLUMNS = {
    "funding_per_settlement",
    "interval_hours",
    "funding_per_day",
    "funding_est_next",
    "oi_usd_now",
    "oi_1h_ago",
    "oi_4h_ago",
    "oi_24h_ago",
    "d_oi_1h_pct",
    "d_oi_4h_pct",
    "d_oi_24h_ratio",
    "price_now",
    "chg_1h_pct",
    "chg_4h_pct",
    "chg_24h_pct",
    "dist_from_peak_pct",
    "quote_vol_24h_usd",
    "spread_bp",
    "p_up",
    "expected_horizon_h",
    "ret_1h_pct",
    "ret_2h_pct",
    "ret_4h_pct",
    "ret_8h_pct",
    "ret_24h_pct",
    "ret_48h_pct",
    "mae_pct",
    "mfe_pct",
}

INTEGER_COLUMNS = {"funding_seq_n_periods_over_threshold", "backfilled"}

SOURCE_MAP = {
    "funding_oi_squeeze": "funding_oi_squeeze",
    "binance_announcement": "binance_announcement",
    "token_unlock_cryptorank": "token_unlock",
    "token_unlock": "token_unlock",
    "depeg_coingecko": "depeg",
    "depeg": "depeg",
    None: "funding_oi_squeeze",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def sha256_hex16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def parse_utc(value: str) -> datetime:
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if len(value) == 13 and value[8] == "_":
        return datetime.strptime(value, "%Y%m%d_%H%M").replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def iso_utc(value: str | datetime) -> str:
    dt = parse_utc(value) if isinstance(value, str) else value.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def init_ledger(db_path: str | Path = DEFAULT_LEDGER_DB) -> Path:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    column_defs = []
    for column in LEDGER_COLUMNS:
        if column in COLUMN_TYPES:
            sql_type = COLUMN_TYPES[column]
        elif column in REAL_COLUMNS:
            sql_type = "REAL"
        elif column in INTEGER_COLUMNS:
            sql_type = "INTEGER"
        else:
            sql_type = "TEXT"
        column_defs.append(f"{column} {sql_type}")
    with sqlite3.connect(db_path) as con:
        con.execute(f"CREATE TABLE IF NOT EXISTS events ({', '.join(column_defs)})")
        existing = {row[1] for row in con.execute("PRAGMA table_info(events)").fetchall()}
        for column in LEDGER_COLUMNS:
            if column not in existing:
                sql_type = COLUMN_TYPES.get(column, "REAL" if column in REAL_COLUMNS else "TEXT")
                con.execute(f"ALTER TABLE events ADD COLUMN {column} {sql_type}")
        con.execute("CREATE INDEX IF NOT EXISTS idx_events_symbol_ts ON events(symbol, decision_ts_utc)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_events_source_decision ON events(source, decision)")
    return db_path


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _bool_int(value: Any) -> int | None:
    if value is None:
        return None
    return 1 if bool(value) else 0


def normalized_source(candidate: dict[str, Any]) -> str:
    source = SOURCE_MAP.get(candidate.get("source"), candidate.get("source"))
    if not source:
        source = "funding_oi_squeeze"
    return source


def ledger_symbol(candidate: dict[str, Any]) -> str:
    symbol = candidate.get("symbol")
    if symbol:
        return str(symbol)
    symbols = candidate.get("symbols")
    if symbols:
        return ",".join(str(item) for item in symbols)
    for key in ("article_code", "key", "coingecko_id", "name"):
        if candidate.get(key):
            return str(candidate[key])
    return "UNKNOWN"


def classify_decision(candidate: dict[str, Any]) -> dict[str, Any]:
    if normalized_source(candidate) != "funding_oi_squeeze":
        return {
            "decision": "rejected",
            "decision_reason": "machine placeholder: non-funding candidate pending human review",
            "gate1_payer_pass": None,
            "legs_passed": None,
        }

    funding_per_day = _safe_float(candidate.get("funding_per_day"))
    oi_ratio = _safe_float(candidate.get("d_oi_24h_ratio") or candidate.get("oi_24h_ratio"))
    chg_24h = _safe_float(candidate.get("chg24h_pct") or candidate.get("chg_24h_pct"))
    funding_pass = funding_per_day is not None and funding_per_day <= FUNDING_LEG_DAILY_THRESHOLD
    oi_pass = oi_ratio is not None and oi_ratio >= OI_LEG_RATIO_THRESHOLD
    price_pass = chg_24h is not None and chg_24h >= 0
    passed = sum((funding_pass, oi_pass, price_pass))
    decision = "near_miss" if passed == 2 else "rejected"
    return {
        "decision": decision,
        "decision_reason": f"machine placeholder: funding/OI/price legs {passed}/3",
        "gate1_payer_pass": funding_pass,
        "legs_passed": f"{passed}/3",
    }


def _candidate_record(
    candidate: dict[str, Any],
    *,
    scan_utc: str,
    scanner_version: str,
    backfilled: bool,
    scan_file: str | None,
    cluster_id: str | None = None,
) -> dict[str, Any]:
    decision_ts = iso_utc(scan_utc)
    source = normalized_source(candidate)
    symbol = ledger_symbol(candidate)
    raw_json = canonical_json(candidate)
    raw_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
    event_id = sha256_hex16(f"{symbol}|{source}|{decision_ts}|{scanner_version}")
    decision_fields = classify_decision(candidate)
    now = utc_now_iso()
    record = {column: None for column in LEDGER_COLUMNS}
    record.update(
        {
            "event_id": event_id,
            "decision_ts_utc": decision_ts,
            "data_asof_utc": decision_ts,
            "scanner_version": scanner_version,
            "raw_response_sha256": raw_hash,
            "source": source,
            "symbol": symbol,
            "event_type": candidate.get("event_type") or "funding_oi_price_anomaly",
            "cluster_id": cluster_id or event_id,
            "backfilled": 1 if backfilled else 0,
            "outcome_status": None,
            "scan_file": scan_file,
            "raw_candidate_json": raw_json,
            "created_at_utc": now,
            "updated_at_utc": now,
            "funding_per_settlement": _safe_float(
                candidate.get("funding_per_settlement", candidate.get("funding_8h"))
            ),
            "interval_hours": _safe_float(candidate.get("interval_hours")),
            "funding_per_day": _safe_float(candidate.get("funding_per_day")),
            "funding_est_next": _safe_float(candidate.get("funding_est_next")),
            "funding_seq_n_periods_over_threshold": _safe_int(
                candidate.get("funding_seq_n_periods_over_threshold")
            ),
            "oi_usd_now": _safe_float(candidate.get("oi_usd_now", candidate.get("oi_now_usdt"))),
            "oi_1h_ago": _safe_float(candidate.get("oi_1h_ago")),
            "oi_4h_ago": _safe_float(candidate.get("oi_4h_ago")),
            "oi_24h_ago": _safe_float(candidate.get("oi_24h_ago", candidate.get("oi_24h_ago_usdt"))),
            "d_oi_1h_pct": _safe_float(candidate.get("d_oi_1h_pct")),
            "d_oi_4h_pct": _safe_float(candidate.get("d_oi_4h_pct")),
            "d_oi_24h_ratio": _safe_float(candidate.get("d_oi_24h_ratio", candidate.get("oi_24h_ratio"))),
            "price_now": _safe_float(candidate.get("price_now", candidate.get("price_usd"))),
            "chg_1h_pct": _safe_float(candidate.get("chg_1h_pct")),
            "chg_4h_pct": _safe_float(candidate.get("chg_4h_pct")),
            "chg_24h_pct": _safe_float(candidate.get("chg_24h_pct", candidate.get("chg24h_pct"))),
            "dist_from_peak_pct": _safe_float(candidate.get("dist_from_peak_pct")),
            "quote_vol_24h_usd": _safe_float(
                candidate.get("quote_vol_24h_usd", candidate.get("quote_vol_usdt"))
            ),
            "spread_bp": _safe_float(candidate.get("spread_bp")),
            "price_oi_quadrant": candidate.get("price_oi_quadrant"),
            "decision": decision_fields["decision"],
            "decision_reason": decision_fields["decision_reason"],
            "gate0_capacity_pass": None,
            "gate1_payer_pass": _bool_int(decision_fields["gate1_payer_pass"]),
            "legs_passed": decision_fields["legs_passed"],
            "net_r_at_cost": canonical_json({str(cost): None for cost in COST_RATES}),
        }
    )
    return record


def _find_cluster_id(con: sqlite3.Connection, symbol: str, decision_ts_utc: str) -> str | None:
    decision_dt = parse_utc(decision_ts_utc)
    for row_ts, cluster_id in con.execute(
        "SELECT decision_ts_utc, cluster_id FROM events WHERE symbol=? ORDER BY decision_ts_utc",
        (symbol,),
    ).fetchall():
        if abs(parse_utc(row_ts) - decision_dt) <= timedelta(hours=48):
            return cluster_id
    return None


def _merge_raw_candidate_json(existing_text: str | None, new_text: str) -> str:
    def as_items(text: str | None) -> list[Any]:
        if not text:
            return []
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else [parsed]

    items = as_items(existing_text)
    new_item = json.loads(new_text)
    new_key = canonical_json(new_item)
    existing_keys = {canonical_json(item) for item in items}
    if new_key not in existing_keys:
        items.append(new_item)
    if len(items) == 1:
        return canonical_json(items[0])
    return canonical_json(items)


def _insert_or_update(con: sqlite3.Connection, record: dict[str, Any]) -> str:
    exists = con.execute(
        "SELECT raw_candidate_json FROM events WHERE event_id=?",
        (record["event_id"],),
    ).fetchone()
    if exists:
        merged_raw_json = _merge_raw_candidate_json(exists[0], record["raw_candidate_json"])
        merged_raw_hash = hashlib.sha256(merged_raw_json.encode("utf-8")).hexdigest()
        update_columns = [
            column
            for column in (
                "data_asof_utc",
                "raw_response_sha256",
                "event_type",
                "funding_per_settlement",
                "interval_hours",
                "funding_per_day",
                "funding_est_next",
                "funding_seq_n_periods_over_threshold",
                "oi_usd_now",
                "oi_1h_ago",
                "oi_4h_ago",
                "oi_24h_ago",
                "d_oi_1h_pct",
                "d_oi_4h_pct",
                "d_oi_24h_ratio",
                "price_now",
                "chg_1h_pct",
                "chg_4h_pct",
                "chg_24h_pct",
                "dist_from_peak_pct",
                "quote_vol_24h_usd",
                "spread_bp",
                "price_oi_quadrant",
                "scan_file",
                "raw_candidate_json",
                "updated_at_utc",
            )
        ]
        record["raw_candidate_json"] = merged_raw_json
        record["raw_response_sha256"] = merged_raw_hash
        assignments = ", ".join(f"{column}=?" for column in update_columns)
        con.execute(
            f"UPDATE events SET {assignments} WHERE event_id=?",
            [record[column] for column in update_columns] + [record["event_id"]],
        )
        return "updated"
    placeholders = ",".join("?" for _ in LEDGER_COLUMNS)
    con.execute(
        f"INSERT INTO events ({', '.join(LEDGER_COLUMNS)}) VALUES ({placeholders})",
        [record[column] for column in LEDGER_COLUMNS],
    )
    return "inserted"


def upsert_scan_candidates(
    db_path: str | Path = DEFAULT_LEDGER_DB,
    candidates: list[dict[str, Any]] | None = None,
    *,
    scan_utc: str,
    scanner_version: str,
    backfilled: bool = False,
    scan_file: str | None = None,
) -> dict[str, int]:
    db_path = init_ledger(db_path)
    stats = {"inserted": 0, "updated": 0, "near_miss": 0, "rejected": 0}
    with sqlite3.connect(db_path) as con:
        for candidate in candidates or []:
            provisional = _candidate_record(
                candidate,
                scan_utc=scan_utc,
                scanner_version=scanner_version,
                backfilled=backfilled,
                scan_file=scan_file,
            )
            cluster_id = _find_cluster_id(con, provisional["symbol"], provisional["decision_ts_utc"])
            record = _candidate_record(
                candidate,
                scan_utc=scan_utc,
                scanner_version=scanner_version,
                backfilled=backfilled,
                scan_file=scan_file,
                cluster_id=cluster_id,
            )
            action = _insert_or_update(con, record)
            stats[action] += 1
            if record["decision"] in ("near_miss", "rejected"):
                stats[record["decision"]] += 1
    return stats


def update_decision_fields(
    db_path: str | Path,
    event_id: str,
    *,
    decision: str,
    p_up: float | None,
    expected_direction: str | None = None,
    expected_horizon_h: int | None = None,
    entry_rule: str | None = None,
    exit_rule: str | None = None,
    invalidation_rule: str | None = None,
    decision_reason: str | None = None,
    gate0_capacity_pass: bool | None = None,
    gate1_payer_pass: bool | None = None,
) -> None:
    if decision not in {"selected", "watch", "near_miss", "rejected"}:
        raise ValueError(f"invalid decision: {decision}")
    if p_up is None:
        raise ValueError("p_up is required for human decision updates")
    if not 0 <= float(p_up) <= 1:
        raise ValueError("p_up must be between 0 and 1")
    if decision in {"selected", "watch"}:
        required = {
            "expected_direction": expected_direction,
            "expected_horizon_h": expected_horizon_h,
            "entry_rule": entry_rule,
            "exit_rule": exit_rule,
            "invalidation_rule": invalidation_rule,
        }
        missing = [key for key, value in required.items() if value in (None, "")]
        if missing:
            raise ValueError("missing required decision fields: " + ", ".join(missing))

    db_path = init_ledger(db_path)
    with sqlite3.connect(db_path) as con:
        cur = con.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,))
        if cur.fetchone() is None:
            raise KeyError(event_id)
        con.execute(
            """
            UPDATE events
            SET decision=?, p_up=?, expected_direction=?, expected_horizon_h=?,
                entry_rule=?, exit_rule=?, invalidation_rule=?, decision_reason=?,
                gate0_capacity_pass=?, gate1_payer_pass=?, updated_at_utc=?
            WHERE event_id=?
            """,
            (
                decision,
                float(p_up),
                expected_direction,
                expected_horizon_h,
                entry_rule,
                exit_rule,
                invalidation_rule,
                decision_reason,
                _bool_int(gate0_capacity_pass),
                _bool_int(gate1_payer_pass),
                utc_now_iso(),
                event_id,
            ),
        )


def _sorted_path(path: list[dict[str, Any]], value_key: str) -> list[dict[str, Any]]:
    clean = []
    for row in path:
        if row.get("ts_utc") is None or row.get(value_key) is None:
            continue
        clean.append({"ts_utc": iso_utc(str(row["ts_utc"])), value_key: _safe_float(row[value_key])})
    return sorted(clean, key=lambda row: parse_utc(row["ts_utc"]))


def _return_at_horizon(price_path: list[dict[str, Any]], base_dt: datetime, base_price: float, hours: int) -> float | None:
    target = base_dt + timedelta(hours=hours)
    for row in price_path:
        if parse_utc(row["ts_utc"]) >= target:
            return (row["price"] / base_price - 1) * 100
    return None


def compute_outcome_fields(
    *,
    decision_ts_utc: str,
    price_path: list[dict[str, Any]],
    oi_path: list[dict[str, Any]],
    funding_path: list[dict[str, Any]],
    expected_direction: str | None = None,
    expected_horizon_h: int | None = None,
) -> dict[str, Any]:
    decision_dt = parse_utc(decision_ts_utc)
    prices = _sorted_path(price_path, "price")
    oi_clean = _sorted_path(oi_path, "oi_usd")
    funding_clean = _sorted_path(funding_path, "fundingRate")
    net_costs = canonical_json({str(cost): None for cost in COST_RATES})
    base_fields = {
        "ret_1h_pct": None,
        "ret_2h_pct": None,
        "ret_4h_pct": None,
        "ret_8h_pct": None,
        "ret_24h_pct": None,
        "ret_48h_pct": None,
        "mae_pct": None,
        "mfe_pct": None,
        "oi_path_json": canonical_json(oi_clean),
        "funding_path_json": canonical_json(funding_clean),
        "net_r_at_cost": net_costs,
        "invalidation_hit_ts": None,
        "resolver_version": RESOLVER_VERSION,
        "resolved_at_utc": utc_now_iso(),
    }
    if not prices:
        return {**base_fields, "outcome_status": "NO_OUTCOME_DATA"}
    if parse_utc(prices[0]["ts_utc"]) <= decision_dt:
        return {**base_fields, "outcome_status": "INVALID_LOOKAHEAD"}

    base_dt = parse_utc(prices[0]["ts_utc"])
    base_price = prices[0]["price"]
    if not base_price or base_price <= 0:
        return {**base_fields, "outcome_status": "NO_OUTCOME_DATA"}

    fields = {**base_fields, "outcome_status": "resolved"}
    for hours in (1, 2, 4, 8, 24, 48):
        fields[f"ret_{hours}h_pct"] = _return_at_horizon(prices, base_dt, base_price, hours)
    returns = [(row["price"] / base_price - 1) * 100 for row in prices if row["price"] is not None]
    fields["mae_pct"] = min(returns) if returns else None
    fields["mfe_pct"] = max(returns) if returns else None

    if expected_direction in {"up", "down"} and expected_horizon_h in (1, 2, 4, 8, 24, 48):
        ret = fields.get(f"ret_{expected_horizon_h}h_pct")
        if ret is not None:
            signed_ret = ret if expected_direction == "up" else -ret
            fields["net_r_at_cost"] = canonical_json({str(cost): signed_ret - cost * 100 for cost in COST_RATES})
    return fields


def apply_outcome_fields(db_path: str | Path, event_id: str, fields: dict[str, Any]) -> None:
    db_path = init_ledger(db_path)
    allowed = [
        "ret_1h_pct",
        "ret_2h_pct",
        "ret_4h_pct",
        "ret_8h_pct",
        "ret_24h_pct",
        "ret_48h_pct",
        "mae_pct",
        "mfe_pct",
        "oi_path_json",
        "funding_path_json",
        "net_r_at_cost",
        "invalidation_hit_ts",
        "resolver_version",
        "resolved_at_utc",
        "outcome_status",
    ]
    assignments = ", ".join(f"{column}=?" for column in allowed) + ", updated_at_utc=?"
    values = [fields.get(column) for column in allowed] + [utc_now_iso(), event_id]
    with sqlite3.connect(db_path) as con:
        con.execute(f"UPDATE events SET {assignments} WHERE event_id=?", values)


def write_daily_snapshot(
    db_path: str | Path = DEFAULT_LEDGER_DB,
    out_dir: str | Path = DEFAULT_SNAPSHOT_DIR,
    *,
    snapshot_date: str | None = None,
) -> Path:
    db_path = init_ledger(db_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot_date = snapshot_date or datetime.now(timezone.utc).strftime("%Y%m%d")
    snapshot_path = out_dir / f"event_ledger_{snapshot_date}.parquet"
    with sqlite3.connect(db_path) as con:
        frame = pd.read_sql_query("SELECT * FROM events ORDER BY decision_ts_utc, source, symbol", con)
    frame.to_parquet(snapshot_path, index=False)
    return snapshot_path
