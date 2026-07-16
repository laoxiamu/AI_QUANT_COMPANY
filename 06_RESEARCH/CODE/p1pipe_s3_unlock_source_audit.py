#!/usr/bin/env python3
"""
P1-RES-039-PIPELINE Step 3: free unlock-calendar source audit + overlap census.

This script does not use paid APIs and does not use article/news samples as an
event census. It records source reachability and whether a reproducible
structured event table is available under the free boundary.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[2]
S1_JSON = ROOT / "06_RESEARCH" / "CODE" / "output" / "p1pipe_s1_panel_audit.json"
S2_JSON = ROOT / "06_RESEARCH" / "CODE" / "output" / "p1pipe_s2_oifunding_audit.json"
PRICE_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED_2026"
OUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
OUT_JSON = OUT_DIR / "p1pipe_s3_unlock_source_audit.json"
EVENT_CSV = OUT_DIR / "p1pipe_s3_free_unlock_events.csv"


URLS = [
    {
        "name": "DefiLlama protocols API control",
        "url": "https://api.llama.fi/protocols",
        "expected": "reachable free API, not unlock events",
    },
    {
        "name": "DefiLlama emissions API",
        "url": "https://api.llama.fi/emissions",
        "expected": "structured unlock/emissions API if free",
    },
    {
        "name": "DefiLlama unlocks API guess",
        "url": "https://api.llama.fi/unlocks",
        "expected": "structured unlock API if exposed",
    },
    {
        "name": "DefiLlama unlocks page",
        "url": "https://defillama.com/unlocks",
        "expected": "public dashboard page",
    },
    {
        "name": "Tokenomist overview page",
        "url": "https://tokenomist.ai/?sort-key=upcomingEvent.dateUnix&sort-direction=asc&page-size=25&watchlist=false",
        "expected": "guest dashboard / upcoming events only if embedded",
    },
    {
        "name": "Tokenomist AAVE token unlock page",
        "url": "https://tokenomist.ai/aave/unlock-events",
        "expected": "single-token guest visible page, not full universe",
    },
    {
        "name": "Tokenomist API docs path",
        "url": "https://tokenomist.ai/api-documents/unlock-events/v5",
        "expected": "docs path if public",
    },
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def fetch(url: str) -> dict[str, Any]:
    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "AI-Quant-Research/1.0"})
        text = response.text
        return {
            "url": url,
            "ok": response.status_code < 500,
            "status": response.status_code,
            "size_bytes": len(response.content),
            "sha256": sha256_text(text),
            "sample": text[:300],
            "text": text,
            "error_type": None,
            "error": None,
        }
    except requests.RequestException as error:
        return {
            "url": url,
            "ok": False,
            "status": None,
            "size_bytes": 0,
            "sha256": None,
            "sample": "",
            "text": "",
            "error_type": type(error).__name__,
            "error": str(error),
        }


def classify_source(record: dict[str, Any]) -> dict[str, Any]:
    text = record.pop("text")
    lower = text.lower()
    signals = {
        "payment_required": record["status"] == 402 or "upgrade to the paid api plan" in lower,
        "not_found": record["status"] == 404 or "404 not found" in lower,
        "tokenomist_api_banner": "get free trial api" in lower or "build and backtest tokenomist api" in lower,
        "has_unlock_keywords": bool(re.search(r"unlockEvents|unlockDate|cliffAmount|upcomingEvent|dateUnix", text)),
        "has_probable_event_json": bool(re.search(r'"unlockDate"\s*:|"cliffAmount"\s*:|"allocationBreakdown"\s*:', text)),
        "has_article_cards": "weekly unlock digest" in lower or "tokenomist research" in lower,
    }
    record["signals"] = signals
    if signals["payment_required"]:
        record["free_event_table_status"] = "blocked_paid_api"
    elif signals["not_found"]:
        record["free_event_table_status"] = "not_found"
    elif signals["has_probable_event_json"]:
        record["free_event_table_status"] = "candidate_embedded_data"
    elif signals["has_unlock_keywords"]:
        record["free_event_table_status"] = "keywords_only_or_limited_ui"
    else:
        record["free_event_table_status"] = "no_structured_events_detected"
    return record


def load_price_ranges() -> dict[str, dict[str, Any]]:
    ranges = {}
    for path in PRICE_DIR.glob("*USDT_4H.csv"):
        symbol = path.name.replace("USDT_4H.csv", "")
        df = pd.read_csv(path, usecols=["datetime"], parse_dates=["datetime"])
        ranges[symbol] = {
            "start": df["datetime"].min(),
            "end": df["datetime"].max(),
            "file": str(path.relative_to(ROOT)),
        }
    return ranges


def overlap_census(events: list[dict[str, Any]], price_ranges: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    s2 = json.loads(S2_JSON.read_text(encoding="utf-8"))
    oi_complete = {
        item["symbol"]
        for item in s2["metrics"]
        if item["coverage"]["coverage_status"] == "covers_requested_window"
    }
    funding_complete = {
        item["symbol"]
        for item in s2["funding"]
        if item["coverage"]["coverage_status"] == "covers_requested_window"
    }
    for event in events:
        symbol = event["symbol"]
        ts = pd.Timestamp(event["unlockDate"]).tz_localize(None)
        price = price_ranges.get(symbol)
        price_overlap = bool(price and price["start"] <= ts <= price["end"])
        out.append(
            {
                **event,
                "price_overlap": price_overlap,
                "oi_near_term_complete": symbol in oi_complete,
                "funding_near_term_complete": symbol in funding_complete,
            }
        )
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_records = []
    for item in URLS:
        record = fetch(item["url"])
        record["name"] = item["name"]
        record["expected"] = item["expected"]
        source_records.append(classify_source(record))

    # Free-boundary rule: do not convert article cards or limited guest UI into
    # census events. This stays empty unless a broad structured event endpoint is
    # discovered and parsed.
    free_events: list[dict[str, Any]] = []
    price_ranges = load_price_ranges()
    overlap = overlap_census(free_events, price_ranges)
    pd.DataFrame(overlap).to_csv(EVENT_CSV, index=False)

    s1 = json.loads(S1_JSON.read_text(encoding="utf-8"))
    output = {
        "task_id": "P1-RES-039-PIPELINE-S3",
        "generated_at": utc_now_iso(),
        "discipline": {
            "holdout_touched": False,
            "paid_api_used": False,
            "article_samples_used_as_census": False,
            "parameter_tuning_performed": False,
        },
        "universe": s1["post_2025_event_eligible_universe"],
        "source_audit": source_records,
        "free_structured_events": {
            "event_file": str(EVENT_CSV.relative_to(ROOT)),
            "events": free_events,
            "event_count": len(free_events),
            "reason_empty": (
                "No reproducible free full-history unlock event table was available. "
                "DefiLlama emissions returned 402, Tokenomist public pages are limited/guest UI or 404 for API docs, "
                "and article/research cards were excluded by task instruction."
            ),
        },
        "overlap_census": {
            "price_overlap_episodes": sum(1 for row in overlap if row["price_overlap"]),
            "price_oi_funding_overlap_episodes": sum(
                1
                for row in overlap
                if row["price_overlap"] and row["oi_near_term_complete"] and row["funding_near_term_complete"]
            ),
            "episode_ge_50": len(overlap) >= 50,
            "episode_ge_100": len(overlap) >= 100,
            "episode_ge_300": len(overlap) >= 300,
            "eligible_for_60_20_20": len(overlap) >= 300,
            "scale_bucket_distribution": {},
        },
    }
    OUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_JSON)


if __name__ == "__main__":
    main()
