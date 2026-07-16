#!/usr/bin/env python3
"""
P1-RES-039-B1 Phase A unlock data audit.

Scope:
- Read local FUTURES_EXPANDED 4H price panel only.
- Use a tiny, explicitly registered public-source unlock sample for schema/overlap
  verification, not a backtest or broad event pull.
- Emit machine-readable audit JSON for the Phase A report.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PRICE_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED"
OUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
OUT_PATH = OUT_DIR / "p1res039_phasea_unlock_audit_20260622.json"


@dataclass(frozen=True)
class UnlockSample:
    token: str
    symbol: str
    event_date_utc: str
    amount_tokens: float | None
    value_usd: float | None
    value_to_circulating_supply_pct: float | None
    allocation_summary: dict[str, float]
    source_name: str
    source_url: str
    source_published_utc: str
    source_note: str


AUDITED_FREE_SAMPLES = [
    UnlockSample(
        token="Avalanche",
        symbol="AVAX",
        event_date_utc="2024-08-20T00:00:00Z",
        amount_tokens=9_540_000.0,
        value_usd=251_330_000.0,
        value_to_circulating_supply_pct=2.42,
        allocation_summary={
            "strategic_partners": 2_250_000.0,
            "foundation": 1_670_000.0,
            "team": 4_500_000.0,
            "airdrop": 1_130_000.0,
        },
        source_name="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        source_published_utc="2024-07-31T21:30:00Z",
        source_note=(
            "Public article, not bulk API. Date-only event time; script aligns to "
            "nearest 4H bar and reports this precision limit."
        ),
    ),
    UnlockSample(
        token="Wormhole",
        symbol="W",
        event_date_utc="2024-08-03T00:00:00Z",
        amount_tokens=600_000_000.0,
        value_usd=151_670_000.0,
        value_to_circulating_supply_pct=33.33,
        allocation_summary={"community_and_launch": 600_000_000.0},
        source_name="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        source_published_utc="2024-07-31T21:30:00Z",
        source_note="Public article, not bulk API; token absent from local price panel.",
    ),
    UnlockSample(
        token="Aptos",
        symbol="APT",
        event_date_utc="2024-08-12T00:00:00Z",
        amount_tokens=11_310_000.0,
        value_usd=76_450_000.0,
        value_to_circulating_supply_pct=2.41,
        allocation_summary={
            "foundation": 1_330_000.0,
            "community": 3_210_000.0,
            "core_contributors": 3_960_000.0,
            "investors": 2_810_000.0,
        },
        source_name="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        source_published_utc="2024-07-31T21:30:00Z",
        source_note="Public article, not bulk API; token absent from local price panel.",
    ),
    UnlockSample(
        token="The Sandbox",
        symbol="SAND",
        event_date_utc="2024-08-14T00:00:00Z",
        amount_tokens=205_590_000.0,
        value_usd=66_750_000.0,
        value_to_circulating_supply_pct=9.0,
        allocation_summary={
            "team": 71_250_000.0,
            "advisors": 37_500_000.0,
            "company_reserve": 96_840_000.0,
        },
        source_name="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        source_published_utc="2024-07-31T21:30:00Z",
        source_note="Public article, not bulk API; token absent from local price panel.",
    ),
    UnlockSample(
        token="Arbitrum",
        symbol="ARB",
        event_date_utc="2024-08-16T00:00:00Z",
        amount_tokens=92_650_000.0,
        value_usd=65_170_000.0,
        value_to_circulating_supply_pct=2.77,
        allocation_summary={
            "team_future_team_advisors": 56_130_000.0,
            "investors": 36_520_000.0,
        },
        source_name="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        source_published_utc="2024-07-31T21:30:00Z",
        source_note="Public article, not bulk API; token absent from local price panel.",
    ),
]


TOKENOMIST_BOUNDARIES = {
    "asof_utc": "2026-06-22T00:00:00Z",
    "source_docs": [
        "https://docs.tokenomist.ai/api-documents/introduction",
        "https://docs.tokenomist.ai/api-documents/unlock-events/v5",
        "https://docs.tokenomist.ai/features/csv-download",
    ],
    "api_auth": "x-api-key required for token list, unlock events, upcoming unlock events",
    "free_trial_unlock_events_history": "1 year backward",
    "standard_unlock_events_history": "1 year backward, 2 years forward",
    "elite_unlock_events_history": "2 years backward, 3 years forward",
    "csv_export_boundary": "CSV export only available to Pro users; all release events not free",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_price_panel() -> tuple[dict[str, Any], dict[str, pd.DataFrame]]:
    assets: dict[str, pd.DataFrame] = {}
    rows = []
    required_cols = ["datetime", "open", "high", "low", "close", "volume"]

    for path in sorted(PRICE_DIR.glob("*_4H.csv")):
        symbol = path.name.replace("USDT_4H.csv", "")
        df = pd.read_csv(path, parse_dates=["datetime"])
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        df = df.sort_values("datetime").reset_index(drop=True)
        assets[symbol] = df
        rows.append(
            {
                "file": str(path.relative_to(ROOT)),
                "symbol": symbol,
                "rows": int(len(df)),
                "start": df["datetime"].iloc[0].isoformat(),
                "end": df["datetime"].iloc[-1].isoformat(),
                "columns": required_cols,
            }
        )

    starts = [r["start"] for r in rows]
    ends = [r["end"] for r in rows]
    summary = {
        "price_dir": str(PRICE_DIR.relative_to(ROOT)),
        "asset_count": len(rows),
        "row_count_min": min(r["rows"] for r in rows),
        "row_count_max": max(r["rows"] for r in rows),
        "panel_start_min": min(starts),
        "panel_start_max": max(starts),
        "panel_end_min": min(ends),
        "panel_end_max": max(ends),
        "assets": rows,
    }
    return summary, assets


def compute_event_drifts(sample: UnlockSample, assets: dict[str, pd.DataFrame]) -> dict[str, Any]:
    symbol = sample.symbol
    symbol_present = symbol in assets
    result: dict[str, Any] = {
        "sample": asdict(sample),
        "symbol_present_in_price_panel": symbol_present,
        "price_symbol": f"{symbol}USDT" if symbol_present else None,
        "event_overlap_with_price_panel": False,
        "alignment": None,
        "drifts": [],
    }
    if not symbol_present:
        return result

    df = assets[symbol]
    event_ts = pd.Timestamp(sample.event_date_utc).tz_convert(None)
    if event_ts < df["datetime"].iloc[0] or event_ts > df["datetime"].iloc[-1]:
        return result

    idx = int((df["datetime"] - event_ts).abs().idxmin())
    event_row = df.iloc[idx]
    result["event_overlap_with_price_panel"] = True
    result["alignment"] = {
        "requested_event_time_utc": sample.event_date_utc,
        "nearest_bar_time_utc": event_row["datetime"].isoformat(),
        "nearest_bar_close": float(event_row["close"]),
        "event_time_precision": "date-only public article; 00:00Z convention",
    }

    for bars in (6, 18, 42):
        if idx - bars < 0 or idx + bars >= len(df):
            continue
        pre = float(df.loc[idx, "close"] / df.loc[idx - bars, "close"] - 1.0)
        post = float(df.loc[idx + bars, "close"] / df.loc[idx, "close"] - 1.0)
        result["drifts"].append(
            {
                "horizon_bars_4h": bars,
                "horizon_hours": bars * 4,
                "pre_event_long_return_bp": round(pre * 10_000, 2),
                "post_event_long_return_bp": round(post * 10_000, 2),
                "post_event_short_return_bp": round(-post * 10_000, 2),
                "post_event_abs_gross_drift_bp": round(abs(post) * 10_000, 2),
            }
        )
    return result


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    price_summary, assets = load_price_panel()
    event_results = [compute_event_drifts(sample, assets) for sample in AUDITED_FREE_SAMPLES]

    overlapped = [e for e in event_results if e["event_overlap_with_price_panel"]]
    output = {
        "task_id": "P1-RES-039-B1-PHASEA",
        "generated_at": utc_now_iso(),
        "discipline": {
            "holdout_touched": False,
            "backtest_performed": False,
            "parameter_tuning_performed": False,
            "independent_count_consumed": False,
            "data_reads": ["06_RESEARCH/DATA/FUTURES_EXPANDED"],
        },
        "local_price_panel": price_summary,
        "unlock_source_free_boundary": TOKENOMIST_BOUNDARIES,
        "audited_free_public_article_samples": event_results,
        "event_census_initial": {
            "scope": "Only five events from one public historical article; not a broad census.",
            "recognizable_events_in_sample": len(event_results),
            "events_with_local_price_overlap": len(overlapped),
            "episode_ge_100": len(overlapped) >= 100,
            "eligible_for_60_20_20_split": len(overlapped) >= 300,
            "eligible_for_any_event_census_conclusion": False,
            "reason": (
                "Bulk historical unlock events require Tokenomist API key/paid plan "
                "or heterogeneous on-chain contract reconstruction."
            ),
        },
        "cost_gates_bp": {
            "low": 80,
            "mid": 120,
            "high": 220,
        },
    }
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_PATH)


if __name__ == "__main__":
    main()
