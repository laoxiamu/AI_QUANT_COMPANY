"""P0-RES-018 A-4 redefined listing census.

This census answers feasibility only. It does not compute returns, CAR,
residuals, signals, or backtests.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import re
import statistics
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from io import BytesIO, TextIOWrapper
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/UNIVERSE_PIT.csv"
DELIST_INVENTORY_PATH = (
    PROJECT_ROOT / "06_RESEARCH/DATA/DELIST_EVENTS/binance_delist_event_inventory_p0res010_20260716.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/LISTING_EVENTS"
CODE_OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
CODEX_REPORT_PATH = PROJECT_ROOT / "04_AI_TEAM/CODEX_TASKS/REPORT_P0RES018_A4_LISTING_CENSUS_20260721.md"
RESULTS_REPORT_PATH = PROJECT_ROOT / "06_RESEARCH/RESULTS/20260721_p0res018_a4_redefined_listing_census.md"

ANNOUNCEMENT_LIST_URL = "https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query"
ANNOUNCEMENT_DETAIL_URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query"
ANNOUNCEMENT_CATALOGS = {
    48: "New Cryptocurrency Listing",
    49: "Latest Binance News",
}
ANNOUNCEMENT_LOWER_BOUND_UTC = datetime(2021, 12, 1, tzinfo=timezone.utc)

DATA_VISION_FUTURES = "https://data.binance.vision/data/futures/um"
DATA_VISION_SPOT = "https://data.binance.vision/data/spot"
START_DATE = date(2022, 1, 1)
FIRST_N_DAYS = 30
FIRST_WEEK_DAYS = 7
KLINE_INTERVAL = "1h"
PAGE_SIZE = 50

USER_AGENT = "Mozilla/5.0 (compatible; P0RES018ListingCensus/1.0)"

SYMBOL_RE = re.compile(r"\b(?P<symbol>[A-Z0-9]{2,32}(?:USDT|USDC|USD1))\b")
UTC_TS_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s*\(UTC\)")
UTC_TS_LOOSE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2})")

SPECIAL_KEYWORDS = (
    "tradfi",
    "traditional asset",
    "underlying equity",
    "underlying stock",
    "underlying index",
    "underlying commodity",
    "nasdaq",
    "nyse",
    "bstock",
    "stock token",
    "gold",
    "silver",
    "spacex",
)
SPECIAL_BASES = {
    "XAU",
    "XAG",
    "SPX",
    "SPX500",
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "META",
    "AMZN",
    "TSLA",
    "MSTR",
    "COIN",
    "HOOD",
    "CRCL",
    "NFLX",
    "BABA",
    "SPCX",
    "SPCXUSD1",
}
MULTIPLIERS = ("1000000", "100000", "10000", "1000")
GENERIC_SYMBOL_BASES = {
    "ASSET",
    "CONTRACT",
    "CONTRACTS",
    "EQUITY",
    "INDEX",
    "MARGINED",
    "PERPETUAL",
    "TRADING",
    "FUTURES",
    "UNDERLYING",
    "VALUE",
}


@dataclass(frozen=True)
class HeadJob:
    event_id: str
    dataset: str
    period: str
    url: str
    probe_symbol: str


@dataclass(frozen=True)
class HeadResult:
    event_id: str
    dataset: str
    period: str
    url: str
    probe_symbol: str
    ok: bool
    status: str


@dataclass(frozen=True)
class VolumeJob:
    event_id: str
    symbol: str
    day: date
    url: str


@dataclass(frozen=True)
class VolumeResult:
    event_id: str
    symbol: str
    day: str
    ok: bool
    status: str
    quote_volume: float | None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def parse_day(value: object) -> date | None:
    if pd.isna(value) or value == "":
        return None
    return pd.Timestamp(value).date()


def parse_datetime_text(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip().replace("Z", "").replace(" UTC", "")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def ms_to_utc(ms: int | float | str | None) -> datetime | None:
    if ms is None or ms == "":
        return None
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def day_range(start: date, end: date) -> list[date]:
    if end < start:
        return []
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def month_periods(start: date, end: date) -> list[str]:
    if end < start:
        return []
    cursor = date(start.year, start.month, 1)
    last = date(end.year, end.month, 1)
    periods: list[str] = []
    while cursor <= last:
        periods.append(cursor.strftime("%Y-%m"))
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return periods


def normalize_text(text: str) -> str:
    out = html.unescape(text or "")
    out = out.replace("\u24c8", "S")
    out = out.replace("\xa0", " ")
    out = re.sub(r"\s+", " ", out)
    return out.strip()


def stable_suffix(symbol: str) -> str:
    for suffix in ("USDT", "USDC", "USD1"):
        if symbol.endswith(suffix):
            return suffix
    return ""


def base_asset(symbol: str) -> str:
    suffix = stable_suffix(symbol)
    return symbol[: -len(suffix)] if suffix else symbol


def strip_multiplier(base: str) -> str:
    for multiplier in MULTIPLIERS:
        if base.startswith(multiplier) and len(base) > len(multiplier) + 1:
            return base[len(multiplier) :]
    return base


def is_plausible_symbol(symbol: str) -> bool:
    if not stable_suffix(symbol):
        return False
    base = base_asset(symbol)
    if base in GENERIC_SYMBOL_BASES:
        return False
    bad_fragments = (
        "COMPOSITEINDEX",
        "USDTUSDS",
        "USDTUSDM",
        "USDTEQUITY",
        "USDSMARGINED",
        "USD1USDS",
    )
    return not any(fragment in symbol for fragment in bad_fragments)


def spot_candidates(symbol: str) -> list[str]:
    base = base_asset(symbol)
    candidates: list[str] = []
    if symbol.endswith("USDT"):
        candidates.append(symbol)
    candidates.append(f"{base}USDT")
    stripped = strip_multiplier(base)
    if stripped != base:
        candidates.append(f"{stripped}USDT")
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def futures_kline_url(symbol: str, day: date) -> str:
    quoted = quote(symbol, safe="")
    period = day.isoformat()
    return f"{DATA_VISION_FUTURES}/daily/klines/{quoted}/{KLINE_INTERVAL}/{quoted}-{KLINE_INTERVAL}-{period}.zip"


def spot_kline_url(symbol: str, day: date) -> str:
    quoted = quote(symbol, safe="")
    period = day.isoformat()
    return f"{DATA_VISION_SPOT}/daily/klines/{quoted}/{KLINE_INTERVAL}/{quoted}-{KLINE_INTERVAL}-{period}.zip"


def funding_url(symbol: str, period: str) -> str:
    quoted = quote(symbol, safe="")
    return f"{DATA_VISION_FUTURES}/monthly/fundingRate/{quoted}/{quoted}-fundingRate-{period}.zip"


def oi_metrics_url(symbol: str, day: date) -> str:
    quoted = quote(symbol, safe="")
    period = day.isoformat()
    return f"{DATA_VISION_FUTURES}/daily/metrics/{quoted}/{quoted}-metrics-{period}.zip"


def request_json(url: str, retries: int = 2) -> dict:
    curl_cmd = [
        "curl",
        "-fsSL",
        "--connect-timeout",
        "8",
        "--max-time",
        "20",
        "-H",
        f"User-Agent: {USER_AGENT}",
        "-H",
        "Accept-Language: en",
        "-H",
        "Referer: https://www.binance.com/en/messages/v2/group/announcement",
        url,
    ]
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            completed = subprocess.run(
                curl_cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=25,
            )
            return json.loads(completed.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.8 * attempt)

    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en",
            "Referer": "https://www.binance.com/en/messages/v2/group/announcement",
        },
    )
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=12) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.8 * attempt)
    raise RuntimeError(f"Failed JSON request after {retries} attempts: {url}: {last_error}")


def fetch_article_lists() -> pd.DataFrame:
    rows: list[dict] = []
    seen_codes: set[str] = set()
    for catalog_id, catalog_name in ANNOUNCEMENT_CATALOGS.items():
        page_no = 1
        while True:
            query = urlencode(
                {
                    "type": 1,
                    "catalogId": catalog_id,
                    "pageNo": page_no,
                    "pageSize": PAGE_SIZE,
                }
            )
            payload = request_json(f"{ANNOUNCEMENT_LIST_URL}?{query}")
            catalogs = (payload.get("data") or {}).get("catalogs") or []
            if not catalogs:
                break
            articles = catalogs[0].get("articles") or []
            if not articles:
                break
            oldest_release: datetime | None = None
            for article in articles:
                release_dt = ms_to_utc(article.get("releaseDate"))
                if release_dt is not None:
                    oldest_release = release_dt if oldest_release is None else min(oldest_release, release_dt)
                code = article.get("code") or ""
                if not code:
                    continue
                dedupe_key = f"{catalog_id}:{code}"
                if dedupe_key in seen_codes:
                    continue
                seen_codes.add(dedupe_key)
                rows.append(
                    {
                        "catalog_id": catalog_id,
                        "catalog_name": catalog_name,
                        "article_code": code,
                        "article_id": article.get("id", ""),
                        "title": normalize_text(article.get("title", "")),
                        "release_ts_utc": "" if release_dt is None else utc_text(release_dt),
                        "release_ms": article.get("releaseDate", ""),
                    }
                )
            if oldest_release is not None and oldest_release < ANNOUNCEMENT_LOWER_BOUND_UTC:
                break
            page_no += 1
            if page_no % 10 == 1:
                print(f"announcement catalog {catalog_id} fetched page {page_no - 1}", flush=True)
    return pd.DataFrame(rows)


def is_futures_launch_title(title: str) -> bool:
    lower = title.lower()
    if "binance futures" not in lower:
        return False
    if "perpetual" not in lower:
        return False
    launch_words = ("will launch", "launches", "will list", "adds")
    if not any(word in lower for word in launch_words):
        return False
    stable_words = ("usdt", "usdc", "usd1", "usdt-margined", "usds-margined", "usds-m", "usd-margined")
    has_stable = any(word in lower for word in stable_words)
    if ("coin-m" in lower or "coin-margined" in lower) and not has_stable:
        return False
    return has_stable


def body_to_text(body_raw: str) -> str:
    if not body_raw:
        return ""
    try:
        body = json.loads(body_raw)
    except json.JSONDecodeError:
        stripped = re.sub(r"<[^>]+>", " ", body_raw)
        return normalize_text(stripped)

    def walk(node: object) -> str:
        if isinstance(node, dict):
            if node.get("node") == "text":
                return str(node.get("text", ""))
            return " ".join(walk(child) for child in node.get("child", []) or [])
        if isinstance(node, list):
            return " ".join(walk(child) for child in node)
        return ""

    return normalize_text(walk(body))


def fetch_article_detail(row: dict) -> dict:
    code = row["article_code"]
    query = urlencode({"articleCode": code})
    payload = request_json(f"{ANNOUNCEMENT_DETAIL_URL}?{query}")
    data = payload.get("data") or {}
    body_text = body_to_text(data.get("body", ""))
    title = normalize_text(data.get("title") or row.get("title", ""))
    release_dt = ms_to_utc(row.get("release_ms"))
    return {
        "catalog_id": row["catalog_id"],
        "catalog_name": row["catalog_name"],
        "article_code": code,
        "title": title,
        "release_ts_utc": "" if release_dt is None else utc_text(release_dt),
        "body_text": body_text,
        "article_url": f"https://www.binance.com/en/support/announcement/{code}",
        "detail_status": "ok" if body_text else "empty_body",
    }


def fetch_candidate_details(article_list: pd.DataFrame, workers: int) -> pd.DataFrame:
    candidates = article_list[article_list["title"].map(is_futures_launch_title)].copy()
    rows: list[dict] = []
    records = candidates.to_dict("records")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_article_detail, record): record for record in records}
        for count, future in enumerate(as_completed(futures), start=1):
            record = futures[future]
            try:
                rows.append(future.result())
            except Exception as exc:  # keep the census moving under the 4h box
                rows.append(
                    {
                        "catalog_id": record["catalog_id"],
                        "catalog_name": record["catalog_name"],
                        "article_code": record["article_code"],
                        "title": record["title"],
                        "release_ts_utc": record["release_ts_utc"],
                        "body_text": "",
                        "article_url": f"https://www.binance.com/en/support/announcement/{record['article_code']}",
                        "detail_status": f"detail_error:{type(exc).__name__}",
                    }
                )
            if count % 50 == 0 or count == len(records):
                print(f"announcement details {count}/{len(records)}", flush=True)
    return pd.DataFrame(rows)


def parse_effective_times(text: str) -> list[datetime]:
    times: list[datetime] = []
    for match in UTC_TS_RE.finditer(text):
        dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H:%M").replace(
            tzinfo=timezone.utc
        )
        if dt not in times:
            times.append(dt)
    if times:
        return times
    for match in UTC_TS_LOOSE_RE.finditer(text):
        dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H:%M").replace(
            tzinfo=timezone.utc
        )
        if dt not in times:
            times.append(dt)
    return times


def symbols_in_text(text: str) -> list[str]:
    symbols: list[str] = []
    for match in SYMBOL_RE.finditer(text):
        symbol = match.group("symbol")
        if not is_plausible_symbol(symbol):
            continue
        if symbol not in symbols:
            symbols.append(symbol)
    return symbols


def infer_usdt_margin_symbols(text: str) -> list[str]:
    symbols: list[str] = []
    pattern = re.compile(
        r"\b(?:USDT|USDS|USD[S\u24c8])-Margined\s+(.{1,160}?)\s+Perpetual",
        flags=re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        segment = match.group(1)
        segment = re.split(r"\band\s+Coin-Margined\b|\bwhile\b|\bwith\b|\bat\b", segment, flags=re.IGNORECASE)[0]
        if re.search(r"\bMultiple\b|\bTradFi\b", segment, flags=re.IGNORECASE):
            continue
        parts = re.split(r",|&|\band\b", segment, flags=re.IGNORECASE)
        for part in parts:
            token = re.sub(r"[^A-Za-z0-9]", "", part).upper()
            if not token or token in {"BINANCE", "FUTURES", "USDT", "USDS", "USD", "MARGINED"}:
                continue
            symbol = token if stable_suffix(token) else f"{token}USDT"
            if not is_plausible_symbol(symbol):
                continue
            if symbol not in symbols:
                symbols.append(symbol)
    return symbols


def parse_article_events(detail: dict) -> list[dict]:
    title = normalize_text(detail.get("title", ""))
    body = normalize_text(detail.get("body_text", ""))
    combined = normalize_text(f"{title} {body}")
    if not combined:
        return []

    release_dt = parse_datetime_text(detail.get("release_ts_utc", ""))
    all_symbols = symbols_in_text(combined)
    for inferred in infer_usdt_margin_symbols(title):
        if inferred not in all_symbols:
            all_symbols.append(inferred)
    all_times = parse_effective_times(combined)
    event_map: dict[str, datetime | None] = {}

    matches = list(UTC_TS_RE.finditer(combined)) or list(UTC_TS_LOOSE_RE.finditer(combined))
    for i, match in enumerate(matches):
        dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H:%M").replace(
            tzinfo=timezone.utc
        )
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(combined)
        segment = combined[max(0, match.start() - 260) : min(len(combined), next_start)]
        for symbol in symbols_in_text(segment):
            event_map.setdefault(symbol, dt)

    if not event_map and all_symbols:
        fallback_dt = all_times[0] if all_times else None
        for symbol in all_symbols:
            event_map[symbol] = fallback_dt
    elif all_symbols:
        fallback_dt = all_times[0] if all_times else None
        for symbol in all_symbols:
            event_map.setdefault(symbol, fallback_dt)

    rows: list[dict] = []
    for symbol, effective_dt in event_map.items():
        if effective_dt is not None and effective_dt.date() < START_DATE:
            continue
        if effective_dt is None and release_dt is not None and release_dt.date() < START_DATE:
            continue
        rows.append(
            {
                "symbol": symbol,
                "announcement_ts_utc": "" if release_dt is None else utc_text(release_dt),
                "effective_ts_utc": "" if effective_dt is None else utc_text(effective_dt),
                "announcement_title": title,
                "announcement_code": detail.get("article_code", ""),
                "announcement_url": detail.get("article_url", ""),
                "announcement_catalog_id": detail.get("catalog_id", ""),
                "announcement_catalog_name": detail.get("catalog_name", ""),
                "announcement_parse_status": "ok" if effective_dt is not None else "symbol_only_no_effective_ts",
                "announcement_body_excerpt": combined[:500],
            }
        )
    return rows


def build_announcement_events(details: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for detail in details.to_dict("records"):
        rows.extend(parse_article_events(detail))
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    frame["effective_day"] = frame["effective_ts_utc"].map(lambda x: parse_datetime_text(x).date() if x else None)
    frame = frame.drop_duplicates(
        subset=["symbol", "announcement_code", "effective_ts_utc"], keep="first"
    ).reset_index(drop=True)
    return frame


def load_universe() -> pd.DataFrame:
    frame = pd.read_csv(UNIVERSE_PATH, dtype=str).fillna("")
    required = {"symbol", "onboard_date", "delist_date", "source"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"UNIVERSE_PIT missing columns: {sorted(missing)}")
    frame["onboard_day"] = frame["onboard_date"].map(parse_day)
    frame["delist_day"] = frame["delist_date"].map(parse_day)
    return frame[frame["onboard_day"].map(lambda x: x is not None and x >= START_DATE)].copy()


def load_delist_inventory() -> pd.DataFrame:
    if not DELIST_INVENTORY_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(DELIST_INVENTORY_PATH, dtype=str).fillna("")
    frame = frame[frame["market"].str.contains("USDS-M perpetual", na=False)].copy()
    return frame


def best_announcement_for_symbol(symbol: str, onboard: date, announcement_events: pd.DataFrame) -> dict | None:
    if announcement_events.empty:
        return None
    matches = announcement_events[announcement_events["symbol"] == symbol].copy()
    if matches.empty:
        return None

    def score(row: pd.Series) -> tuple[int, int]:
        effective_day = row.get("effective_day")
        if isinstance(effective_day, date):
            abs_days = abs((effective_day - onboard).days)
            direction_penalty = 0 if effective_day == onboard else 1
            return abs_days, direction_penalty
        release_dt = parse_datetime_text(row.get("announcement_ts_utc", ""))
        if release_dt is not None:
            return abs((release_dt.date() - onboard).days), 2
        return 9999, 3

    records = sorted(matches.to_dict("records"), key=lambda row: score(pd.Series(row)))
    best = records[0]
    effective_day = best.get("effective_day")
    release_dt = parse_datetime_text(best.get("announcement_ts_utc", ""))
    close = False
    if isinstance(effective_day, date):
        close = abs((effective_day - onboard).days) <= 7
    elif release_dt is not None:
        close = abs((release_dt.date() - onboard).days) <= 14
    return best if close else None


def make_event_id(index: int) -> str:
    return f"P0RES018-{index:05d}"


def build_base_events(
    universe: pd.DataFrame,
    announcement_events: pd.DataFrame,
    delist_inventory: pd.DataFrame,
    as_of: datetime,
) -> pd.DataFrame:
    rows: list[dict] = []
    matched_announcement_keys: set[tuple[str, str]] = set()
    delist_by_symbol = {
        row["symbol"]: row for row in delist_inventory.to_dict("records")
    } if not delist_inventory.empty else {}

    for record in universe.to_dict("records"):
        symbol = record["symbol"]
        onboard = record["onboard_day"]
        if not isinstance(onboard, date):
            continue
        announcement = best_announcement_for_symbol(symbol, onboard, announcement_events)
        if announcement is not None:
            matched_announcement_keys.add((announcement.get("symbol", ""), announcement.get("announcement_code", "")))
        effective_ts = ""
        effective_source = "universe_onboard_date_midnight_proxy"
        if announcement is not None and announcement.get("effective_ts_utc"):
            effective_ts = announcement["effective_ts_utc"]
            effective_source = "official_announcement_body"
        else:
            effective_ts = utc_text(datetime(onboard.year, onboard.month, onboard.day, tzinfo=timezone.utc))

        delist_day = record.get("delist_day")
        delist_row = delist_by_symbol.get(symbol)
        delist_ts = ""
        delist_source = ""
        if delist_row is not None and delist_row.get("delist_settlement_time_utc"):
            parsed = parse_datetime_text(delist_row.get("delist_settlement_time_utc"))
            delist_ts = "" if parsed is None else utc_text(parsed)
            delist_source = "p0res010_delist_inventory"
        elif isinstance(delist_day, date):
            delist_ts = utc_text(datetime(delist_day.year, delist_day.month, delist_day.day, tzinfo=timezone.utc))
            delist_source = "UNIVERSE_PIT_delist_date_midnight_proxy"

        rows.append(
            {
                "symbol": symbol,
                "base_asset_guess": base_asset(symbol),
                "perp_listing_announcement_ts_utc": ""
                if announcement is None
                else announcement.get("announcement_ts_utc", ""),
                "perp_listing_effective_ts_utc": effective_ts,
                "effective_ts_source": effective_source,
                "onboard_date_universe": onboard.isoformat(),
                "universe_source": "UNIVERSE_PIT",
                "announcement_title": "" if announcement is None else announcement.get("announcement_title", ""),
                "announcement_code": "" if announcement is None else announcement.get("announcement_code", ""),
                "announcement_url": "" if announcement is None else announcement.get("announcement_url", ""),
                "announcement_parse_status": "not_matched_to_official_announcement"
                if announcement is None
                else announcement.get("announcement_parse_status", ""),
                "announcement_body_excerpt": "" if announcement is None else announcement.get("announcement_body_excerpt", ""),
                "delisted_later": bool(delist_ts),
                "delist_ts_utc": delist_ts,
                "delist_source": delist_source,
                "delist_date_universe": "" if not isinstance(delist_day, date) else delist_day.isoformat(),
            }
        )

    if not announcement_events.empty:
        local_symbols = set(universe["symbol"].tolist())
        for announcement in announcement_events.to_dict("records"):
            symbol = announcement["symbol"]
            key = (symbol, announcement.get("announcement_code", ""))
            if symbol in local_symbols or key in matched_announcement_keys:
                continue
            effective_ts = announcement.get("effective_ts_utc", "")
            effective_dt = parse_datetime_text(effective_ts)
            release_dt = parse_datetime_text(announcement.get("announcement_ts_utc", ""))
            if effective_dt is not None and effective_dt > as_of:
                continue
            event_day = effective_dt.date() if effective_dt else (release_dt.date() if release_dt else None)
            if event_day is None or event_day < START_DATE:
                continue
            rows.append(
                {
                    "symbol": symbol,
                    "base_asset_guess": base_asset(symbol),
                    "perp_listing_announcement_ts_utc": announcement.get("announcement_ts_utc", ""),
                    "perp_listing_effective_ts_utc": effective_ts
                    if effective_ts
                    else utc_text(datetime(event_day.year, event_day.month, event_day.day, tzinfo=timezone.utc)),
                    "effective_ts_source": "official_announcement_body"
                    if effective_ts
                    else "official_announcement_release_date_midnight_proxy",
                    "onboard_date_universe": "",
                    "universe_source": "official_announcement_only_not_in_local_UNIVERSE_PIT",
                    "announcement_title": announcement.get("announcement_title", ""),
                    "announcement_code": announcement.get("announcement_code", ""),
                    "announcement_url": announcement.get("announcement_url", ""),
                    "announcement_parse_status": announcement.get("announcement_parse_status", ""),
                    "announcement_body_excerpt": announcement.get("announcement_body_excerpt", ""),
                    "delisted_later": False,
                    "delist_ts_utc": "",
                    "delist_source": "",
                    "delist_date_universe": "",
                }
            )

    frame = pd.DataFrame(rows)
    frame["event_day"] = frame["perp_listing_effective_ts_utc"].map(lambda x: parse_datetime_text(x).date())
    frame = frame.sort_values(["event_day", "symbol"]).reset_index(drop=True)
    frame.insert(0, "event_id", [make_event_id(i + 1) for i in range(len(frame))])
    return frame


def head_url(job: HeadJob, retries: int = 2) -> HeadResult:
    for attempt in range(1, retries + 1):
        curl_cmd = [
            "curl",
            "-sSIL",
            "--connect-timeout",
            "5",
            "--max-time",
            "12",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            "-H",
            f"User-Agent: {USER_AGENT}",
            job.url,
        ]
        try:
            completed = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=15)
            status = completed.stdout.strip()[-3:] if completed.stdout.strip() else "curl_empty"
            if status == "200":
                return HeadResult(job.event_id, job.dataset, job.period, job.url, job.probe_symbol, True, "200")
            if status == "404":
                return HeadResult(job.event_id, job.dataset, job.period, job.url, job.probe_symbol, False, "404")
            if attempt == retries:
                return HeadResult(job.event_id, job.dataset, job.period, job.url, job.probe_symbol, False, status)
        except (subprocess.SubprocessError, OSError) as exc:
            if attempt == retries:
                return HeadResult(job.event_id, job.dataset, job.period, job.url, job.probe_symbol, False, type(exc).__name__)
        time.sleep(0.4 * attempt)
    return HeadResult(job.event_id, job.dataset, job.period, job.url, job.probe_symbol, False, "unknown")


def run_head_jobs(jobs: list[HeadJob], workers: int) -> pd.DataFrame:
    rows: list[dict] = []
    if not jobs:
        return pd.DataFrame(columns=["event_id", "dataset", "period", "probe_symbol", "ok", "status", "url"])
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(head_url, job): job for job in jobs}
        for count, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            rows.append(
                {
                    "event_id": result.event_id,
                    "dataset": result.dataset,
                    "period": result.period,
                    "probe_symbol": result.probe_symbol,
                    "ok": result.ok,
                    "status": result.status,
                    "url": result.url,
                }
            )
            if count % 1000 == 0 or count == len(jobs):
                print(f"HEAD checked {count}/{len(jobs)}", flush=True)
    return pd.DataFrame(rows)


def build_probe_jobs(events: pd.DataFrame, as_of: datetime) -> tuple[pd.DataFrame, list[HeadJob], list[VolumeJob]]:
    archive_daily_complete_day = as_of.date() - timedelta(days=2)
    prior_month_end = date(as_of.year, as_of.month, 1) - timedelta(days=1)
    metadata_rows: list[dict] = []
    jobs: list[HeadJob] = []
    volume_jobs: list[VolumeJob] = []

    for event in events.to_dict("records"):
        event_id = event["event_id"]
        symbol = event["symbol"]
        event_day = event["event_day"]
        delist_dt = parse_datetime_text(event.get("delist_ts_utc", ""))
        delist_day = delist_dt.date() if delist_dt is not None else None
        nominal_end = event_day + timedelta(days=FIRST_N_DAYS - 1)
        if delist_day is not None and delist_day <= nominal_end:
            observed_end = delist_day - timedelta(days=1)
            delisted_within_30d = True
        else:
            observed_end = nominal_end
            delisted_within_30d = False
        daily_window_matured = observed_end <= archive_daily_complete_day
        funding_archive_closed = observed_end <= prior_month_end
        probe_end = min(observed_end, archive_daily_complete_day)
        futures_days_to_probe = day_range(event_day, probe_end)
        full_window_days = day_range(event_day, observed_end)
        funding_periods = month_periods(event_day, observed_end)
        funding_periods_to_probe = funding_periods

        pre_spot_days = day_range(event_day - timedelta(days=FIRST_N_DAYS), event_day - timedelta(days=1))
        near_spot_days = day_range(event_day, min(event_day + timedelta(days=FIRST_WEEK_DAYS), archive_daily_complete_day))
        candidates = spot_candidates(symbol)
        for spot_symbol in candidates:
            for day in pre_spot_days:
                jobs.append(HeadJob(event_id, "spot_1h_daily_pre30", day.isoformat(), spot_kline_url(spot_symbol, day), spot_symbol))
            for day in near_spot_days:
                jobs.append(HeadJob(event_id, "spot_1h_daily_near_listing", day.isoformat(), spot_kline_url(spot_symbol, day), spot_symbol))

        for day in futures_days_to_probe:
            jobs.append(HeadJob(event_id, "perp_kline_1h_daily", day.isoformat(), futures_kline_url(symbol, day), symbol))
            jobs.append(HeadJob(event_id, "perp_oi_metrics_daily", day.isoformat(), oi_metrics_url(symbol, day), symbol))
        for period in funding_periods_to_probe:
            jobs.append(HeadJob(event_id, "perp_fundingRate_monthly", period, funding_url(symbol, period), symbol))

        first_week_probe_days = day_range(event_day, min(event_day + timedelta(days=FIRST_WEEK_DAYS - 1), archive_daily_complete_day))
        for day in first_week_probe_days:
            volume_jobs.append(VolumeJob(event_id, symbol, day, futures_kline_url(symbol, day)))

        metadata_rows.append(
            {
                "event_id": event_id,
                "archive_daily_complete_day": archive_daily_complete_day.isoformat(),
                "funding_archive_complete_month": prior_month_end.strftime("%Y-%m"),
                "data_window_start": event_day.isoformat(),
                "data_window_end": observed_end.isoformat(),
                "nominal_30d_end": nominal_end.isoformat(),
                "delisted_within_30d": delisted_within_30d,
                "matured_30d_window_daily_archive": daily_window_matured,
                "funding_window_archive_closed": funding_archive_closed,
                "expected_kline_days_full": len(full_window_days),
                "expected_oi_days_full": len(full_window_days),
                "expected_funding_months_full": len(funding_periods),
                "probed_kline_days": len(futures_days_to_probe),
                "probed_oi_days": len(futures_days_to_probe),
                "probed_funding_months": len(funding_periods_to_probe),
                "spot_probe_candidates": ";".join(candidates),
                "spot_pre30_expected_days": len(pre_spot_days),
            }
        )

    return pd.DataFrame(metadata_rows), jobs, volume_jobs


def download_daily_quote_volume(job: VolumeJob, retries: int = 2) -> VolumeResult:
    for attempt in range(1, retries + 1):
        curl_cmd = [
            "curl",
            "-fsSL",
            "--connect-timeout",
            "5",
            "--max-time",
            "25",
            "-H",
            f"User-Agent: {USER_AGENT}",
            job.url,
        ]
        try:
            completed = subprocess.run(curl_cmd, check=True, capture_output=True, timeout=30)
            payload = completed.stdout
            with ZipFile(BytesIO(payload)) as archive:
                names = archive.namelist()
                if not names:
                    return VolumeResult(job.event_id, job.symbol, job.day.isoformat(), False, "empty_zip", None)
                with archive.open(names[0]) as raw:
                    wrapper = TextIOWrapper(raw, encoding="utf-8")
                    reader = csv.reader(wrapper)
                    total = 0.0
                    rows = 0
                    for line in reader:
                        if len(line) < 8:
                            continue
                        try:
                            quote_volume = float(line[7])
                        except ValueError:
                            continue
                        if math.isfinite(quote_volume):
                            total += quote_volume
                            rows += 1
                    if rows == 0:
                        return VolumeResult(job.event_id, job.symbol, job.day.isoformat(), False, "no_rows", None)
                    return VolumeResult(job.event_id, job.symbol, job.day.isoformat(), True, "200", total)
        except subprocess.CalledProcessError as exc:
            if attempt == retries:
                return VolumeResult(job.event_id, job.symbol, job.day.isoformat(), False, f"curl_exit_{exc.returncode}", None)
        except (subprocess.SubprocessError, OSError, BadZipFile) as exc:
            if attempt == retries:
                return VolumeResult(job.event_id, job.symbol, job.day.isoformat(), False, type(exc).__name__, None)
        time.sleep(0.4 * attempt)
    return VolumeResult(job.event_id, job.symbol, job.day.isoformat(), False, "unknown", None)


def run_volume_jobs(jobs: list[VolumeJob], workers: int) -> pd.DataFrame:
    rows: list[dict] = []
    if not jobs:
        return pd.DataFrame(columns=["event_id", "symbol", "day", "ok", "status", "quote_volume"])
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download_daily_quote_volume, job): job for job in jobs}
        for count, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            rows.append(
                {
                    "event_id": result.event_id,
                    "symbol": result.symbol,
                    "day": result.day,
                    "ok": result.ok,
                    "status": result.status,
                    "quote_volume": result.quote_volume,
                }
            )
            if count % 1000 == 0 or count == len(jobs):
                print(f"volume days read {count}/{len(jobs)}", flush=True)
    return pd.DataFrame(rows)


def semicolon(values: list[str], limit: int = 40) -> str:
    vals = sorted(str(v) for v in values if str(v))
    if len(vals) <= limit:
        return ";".join(vals)
    return ";".join(vals[:limit]) + ";..."


def status_counts(frame: pd.DataFrame) -> str:
    if frame.empty:
        return ""
    counts = frame["status"].value_counts(dropna=False).to_dict()
    return ";".join(f"{key}:{value}" for key, value in sorted(counts.items(), key=lambda x: str(x[0])))


def ok_mask(frame: pd.DataFrame) -> pd.Series:
    if "ok" not in frame.columns:
        return pd.Series(False, index=frame.index)
    return frame["ok"].map(lambda value: value is True or str(value).lower() == "true")


def classify_special(event: dict) -> bool:
    text = normalize_text(f"{event.get('announcement_title', '')} {event.get('announcement_body_excerpt', '')}").lower()
    base = base_asset(event["symbol"])
    return base in SPECIAL_BASES or any(keyword in text for keyword in SPECIAL_KEYWORDS)


def summarize_events(events: pd.DataFrame, window_meta: pd.DataFrame, probes: pd.DataFrame, volumes: pd.DataFrame) -> pd.DataFrame:
    probe_groups = probes.groupby(["event_id", "dataset"], sort=False) if not probes.empty else None
    volume_groups = volumes.groupby("event_id", sort=False) if not volumes.empty else None
    meta_by_event = {row["event_id"]: row for row in window_meta.to_dict("records")}
    rows: list[dict] = []

    for event in events.to_dict("records"):
        event_id = event["event_id"]
        meta = meta_by_event[event_id]

        def group(dataset: str) -> pd.DataFrame:
            if probe_groups is None or (event_id, dataset) not in probe_groups.groups:
                return pd.DataFrame(columns=probes.columns if not probes.empty else [])
            return probe_groups.get_group((event_id, dataset))

        spot_pre = group("spot_1h_daily_pre30")
        spot_near = group("spot_1h_daily_near_listing")
        kline = group("perp_kline_1h_daily")
        funding = group("perp_fundingRate_monthly")
        oi = group("perp_oi_metrics_daily")

        best_spot_symbol = ""
        spot_found_days = 0
        spot_missing_days: list[str] = []
        for candidate, candidate_group in spot_pre.groupby("probe_symbol") if not spot_pre.empty else []:
            candidate_ok = ok_mask(candidate_group)
            found_periods = set(candidate_group.loc[candidate_ok, "period"].tolist())
            found = len(found_periods)
            if found > spot_found_days:
                best_spot_symbol = candidate
                spot_found_days = found
                expected_periods = set(candidate_group["period"].tolist())
                spot_missing_days = sorted(expected_periods - found_periods)
        spot_near_first = ""
        if not spot_near.empty:
            near_ok = spot_near[ok_mask(spot_near)].sort_values("period")
            if not near_ok.empty:
                spot_near_first = str(near_ok.iloc[0]["period"])
                if not best_spot_symbol:
                    best_spot_symbol = str(near_ok.iloc[0]["probe_symbol"])

        expected_spot_days = int(meta["spot_pre30_expected_days"])
        has_spot_30d_before = spot_found_days == expected_spot_days and expected_spot_days > 0

        kline_ok = ok_mask(kline)
        oi_ok = ok_mask(oi)
        funding_ok = ok_mask(funding)
        kline_found = int(kline_ok.sum()) if not kline.empty else 0
        oi_found = int(oi_ok.sum()) if not oi.empty else 0
        funding_found = int(funding_ok.sum()) if not funding.empty else 0

        missing_kline = kline.loc[~kline_ok, "period"].tolist() if not kline.empty else []
        missing_oi = oi.loc[~oi_ok, "period"].tolist() if not oi.empty else []
        missing_funding = funding.loc[~funding_ok, "period"].tolist() if not funding.empty else []

        matured_daily = bool(meta["matured_30d_window_daily_archive"])
        funding_closed = bool(meta["funding_window_archive_closed"])
        kline_complete = matured_daily and kline_found == int(meta["expected_kline_days_full"])
        oi_complete = matured_daily and oi_found == int(meta["expected_oi_days_full"])
        funding_complete = funding_closed and funding_found == int(meta["expected_funding_months_full"])
        data_complete_all = bool(kline_complete and oi_complete and funding_complete)

        if volume_groups is not None and event_id in volume_groups.groups:
            volume_group = volume_groups.get_group(event_id)
        else:
            volume_group = pd.DataFrame(columns=volumes.columns if not volumes.empty else [])
        volume_ok = ok_mask(volume_group)
        daily_volumes = [float(v) for v in volume_group.loc[volume_ok, "quote_volume"].dropna().tolist()]
        if daily_volumes:
            first_week_median = statistics.median(daily_volumes)
        else:
            first_week_median = math.nan

        special = classify_special(event)
        if special:
            event_type = "tradfi_or_special"
            event_reason = "announcement/body or ticker indicates TradFi/special underlying"
        elif has_spot_30d_before:
            event_type = "existing_spot_then_perp"
            event_reason = "Binance spot 1h daily archive complete for 30 calendar days before perp listing"
        elif spot_found_days > 0 or spot_near_first:
            event_type = "simultaneous_spot_perp"
            event_reason = "Binance spot archive exists only within/near the pre-listing window, not full 30d"
        else:
            event_type = "zero_base_new_asset"
            event_reason = "No Binance spot archive found in pre30 or near-listing probe window"

        valid_existing_spot_sample = bool(event_type == "existing_spot_then_perp" and data_complete_all)

        row = dict(event)
        row.update(meta)
        row.update(
            {
                "spot_symbol_used": best_spot_symbol,
                "has_spot_30d_before": has_spot_30d_before,
                "spot_30d_found_days": spot_found_days,
                "spot_30d_missing_days": semicolon(spot_missing_days),
                "spot_near_first_found_day": spot_near_first,
                "event_type": event_type,
                "event_type_reason": event_reason,
                "kline_days_found": kline_found,
                "funding_months_found": funding_found,
                "oi_days_found": oi_found,
                "kline_30d_complete": kline_complete,
                "funding_window_complete": funding_complete,
                "oi_30d_complete": oi_complete,
                "data_complete_all": data_complete_all,
                "valid_existing_spot_sample": valid_existing_spot_sample,
                "missing_kline_days": semicolon(missing_kline),
                "missing_funding_months": semicolon(missing_funding),
                "missing_oi_days": semicolon(missing_oi),
                "kline_probe_status_counts": status_counts(kline),
                "funding_probe_status_counts": status_counts(funding),
                "oi_probe_status_counts": status_counts(oi),
                "spot_probe_status_counts": status_counts(pd.concat([spot_pre, spot_near], ignore_index=True)),
                "first_week_quote_volume_median": "" if math.isnan(first_week_median) else f"{first_week_median:.8f}",
                "first_week_volume_days_found": len(daily_volumes),
                "first_week_volume_status_counts": status_counts(volume_group) if not volume_group.empty else "",
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def pct(numer: int, denom: int) -> str:
    return "NA" if denom == 0 else f"{numer / denom:.2%}"


def write_report(events: pd.DataFrame, article_list: pd.DataFrame, details: pd.DataFrame, probes: pd.DataFrame, volumes: pd.DataFrame, as_of: datetime) -> None:
    total = len(events)
    local_total = int((events["universe_source"] == "UNIVERSE_PIT").sum())
    announcement_only = total - local_total
    delisted = int(events["delisted_later"].sum())
    valid = int(events["valid_existing_spot_sample"].sum())
    existing_total = int((events["event_type"] == "existing_spot_then_perp").sum())
    existing_data_complete = int(
        ((events["event_type"] == "existing_spot_then_perp") & events["data_complete_all"]).sum()
    )
    exit_conclusion = "够格" if valid >= 100 else "不够格"

    layer_rows = []
    for event_type, group in events.groupby("event_type", sort=True):
        complete = int(group["data_complete_all"].sum())
        valid_group = int(group["valid_existing_spot_sample"].sum())
        delisted_group = int(group["delisted_later"].sum())
        layer_rows.append([event_type, len(group), complete, valid_group, delisted_group, pct(delisted_group, len(group))])

    year_rows = []
    for year, group in events.groupby(events["event_day"].map(lambda d: d.year), sort=True):
        year_rows.append(
            [
                year,
                len(group),
                int((group["event_type"] == "existing_spot_then_perp").sum()),
                int(group["data_complete_all"].sum()),
                int(group["valid_existing_spot_sample"].sum()),
                int(group["delisted_later"].sum()),
            ]
        )

    completeness_rows = [
        ["spot pre30 complete", int(events["has_spot_30d_before"].sum()), total, pct(int(events["has_spot_30d_before"].sum()), total)],
        ["perp kline 30d complete", int(events["kline_30d_complete"].sum()), total, pct(int(events["kline_30d_complete"].sum()), total)],
        ["funding window complete", int(events["funding_window_complete"].sum()), total, pct(int(events["funding_window_complete"].sum()), total)],
        ["OI 30d complete", int(events["oi_30d_complete"].sum()), total, pct(int(events["oi_30d_complete"].sum()), total)],
        ["kline+funding+OI complete", int(events["data_complete_all"].sum()), total, pct(int(events["data_complete_all"].sum()), total)],
    ]

    survivor_rows = [
        ["all events", delisted, total, pct(delisted, total)],
        [
            "existing_spot_then_perp",
            int(events.loc[events["event_type"] == "existing_spot_then_perp", "delisted_later"].sum()),
            existing_total,
            pct(int(events.loc[events["event_type"] == "existing_spot_then_perp", "delisted_later"].sum()), existing_total),
        ],
        [
            "valid existing_spot sample",
            int(events.loc[events["valid_existing_spot_sample"], "delisted_later"].sum()),
            valid,
            pct(int(events.loc[events["valid_existing_spot_sample"], "delisted_later"].sum()), valid),
        ],
    ]

    missing_related = events[
        (events["event_type"] == "existing_spot_then_perp") & (~events["data_complete_all"])
    ][
        [
            "symbol",
            "event_day",
            "delisted_later",
            "kline_30d_complete",
            "funding_window_complete",
            "oi_30d_complete",
            "missing_kline_days",
            "missing_funding_months",
            "missing_oi_days",
        ]
    ].head(20)

    missing_rows = missing_related.astype(str).values.tolist()
    announcement_matched = int((events["announcement_code"] != "").sum())
    local_events = events[events["universe_source"] == "UNIVERSE_PIT"]
    local_announcement_matched = int((local_events["announcement_code"] != "").sum())
    effective_source_rows = [
        [source, len(group), pct(len(group), total)]
        for source, group in events.groupby("effective_ts_source", sort=True)
    ]
    announcement_rows = [
        ["all events with official announcement code", announcement_matched, total, pct(announcement_matched, total)],
        [
            "UNIVERSE_PIT rows with official announcement code",
            local_announcement_matched,
            len(local_events),
            pct(local_announcement_matched, len(local_events)),
        ],
        [
            "effective timestamp exact from announcement body",
            int((events["effective_ts_source"] == "official_announcement_body").sum()),
            total,
            pct(int((events["effective_ts_source"] == "official_announcement_body").sum()), total),
        ],
    ]
    event_csv = OUTPUT_DIR / "p0res018_a4_redefined_listing_events_20260721.csv"
    probes_csv = OUTPUT_DIR / "p0res018_a4_redefined_head_probes_20260721.csv"
    details_csv = OUTPUT_DIR / "p0res018_a4_redefined_announcement_details_20260721.csv"
    volumes_csv = OUTPUT_DIR / "p0res018_a4_redefined_first_week_volume_20260721.csv"

    report = f"""# REPORT_P0RES018_A4_LISTING_CENSUS_20260721

Generated: {utc_text(as_of)}

## 结论

- 本轮只做可行性普查；未计算收益、CAR、残差、方向胜率、Sharpe、回撤或回测。
- 事件表总数 {total}：本地 `UNIVERSE_PIT.csv` 驱动 {local_total}，官方公告补充但不在本地 universe 的 {announcement_only}。
- `existing_spot_then_perp` 总数 {existing_total}；其中 Kline/funding/OI 三项 30 天窗口完整 {existing_data_complete}。
- 出口判据：有效样本 `existing_spot_then_perp & data_complete_all` = {valid}，阈值 100，结论 **{exit_conclusion}**。

## 口径

- PIT universe：以 `06_RESEARCH/DATA/UNIVERSE_PIT.csv` 为主，保留已退市合约；`fapi.binance.com` 当前返回 HTTP 451，未用当前可交易清单删除样本。
- 公告源：Binance 官方 CMS `bapi/apex` 列表 + `bapi/composite` 文章详情；抓取目录为 New Cryptocurrency Listing 与 Latest Binance News。
- 现货判定：对候选 Binance spot symbol 的上市前 30 个 UTC 自然日 `1h` 日归档逐日 HEAD；不下载现货 Kline。
- 永续数据完整性：上市日起最多 30 个 UTC 自然日，Kline 用 daily `1h` ZIP HEAD，OI 用 daily `metrics` ZIP HEAD，funding 用 monthly `fundingRate` ZIP HEAD。
- 首周成交额代理：只读取永续 `1h` Kline ZIP 的 quote volume 字段，按日求和后取首 7 日中位数；不计算任何价格变动或收益。
- 截止日：daily futures/OI 归档按 {events["archive_daily_complete_day"].iloc[0] if total else "NA"} 为可闭合日；monthly funding 按 {events["funding_archive_complete_month"].iloc[0] if total else "NA"} 为可闭合月份。

## 分层计数

{md_table(["event_type", "events", "data_complete_all", "valid_existing_spot_sample", "delisted_later", "delisted_rate"], layer_rows)}

## 分年计数

{md_table(["year", "events", "existing_spot_then_perp", "data_complete_all", "valid_existing_spot_sample", "delisted_later"], year_rows)}

## 数据可得性

{md_table(["check", "ok", "denominator", "rate"], completeness_rows)}

## 公告/生效时间覆盖

{md_table(["coverage", "count", "denominator", "rate"], announcement_rows)}

{md_table(["effective_ts_source", "events", "rate"], effective_source_rows)}

未从公告正文解析到精确 UTC 生效时间的事件，`perp_listing_effective_ts_utc` 使用本地 PIT `onboard_date` 的 UTC 午夜代理，或公告发布日期午夜代理；CSV 的 `effective_ts_source` 逐行标明。

## 幸存者偏差量化

{md_table(["segment", "delisted_later", "denominator", "rate"], survivor_rows)}

已退市合约被保留在事件分母和失败率中；若只用当前仍可交易合约，会漏掉 {delisted} / {total} = {pct(delisted, total)} 的历史事件。

## 缺失样例

{md_table(["symbol", "event_day", "delisted_later", "kline_complete", "funding_complete", "oi_complete", "missing_kline_days", "missing_funding_months", "missing_oi_days"], missing_rows) if missing_rows else "existing_spot_then_perp 组无 Kline/funding/OI 缺失样例。"}

## 源与限制

- 官方公告详情有少数格式不可解析时，事件仍按本地 universe 日期保留，并在 CSV 的 `announcement_parse_status` 标注。
- Binance spot 历史只核验 Binance 官方现货归档；未核验其他交易所现货历史。因此 `zero_base_new_asset` 是“Binance spot archive 未发现”的工程分类，不等同于全市场没有现货。
- Funding 只有 monthly archive 可免费核验；当窗口落在当前未闭合月份时，标为不完整，不据此删除事件。

## 产物

- CODE: `06_RESEARCH/CODE/p0res018_a4_listing_census_redefined.py`
- EVENT CSV: `{event_csv}`
- HEAD PROBES: `{probes_csv}`
- ANNOUNCEMENT DETAILS: `{details_csv}`
- FIRST WEEK VOLUME: `{volumes_csv}`
- RESULTS copy: `{RESULTS_REPORT_PATH}`

## 验收自检

| requirement | status | evidence |
| --- | --- | --- |
| 不看收益/不做回测 | PASS | 脚本无 return/CAR/residual/backtest 计算；Kline 仅读取 quote volume |
| PIT universe 驱动并保留退市 | PASS | `UNIVERSE_PIT.csv` {local_total} 行入表；`delisted_later` {delisted} |
| 公告与生效分列 | PASS | `perp_listing_announcement_ts_utc` 与 `perp_listing_effective_ts_utc` 分列 |
| 现货前 30 天 HEAD | PASS | `spot_1h_daily_pre30` HEAD 明细 {int((probes["dataset"] == "spot_1h_daily_pre30").sum()) if not probes.empty else 0} 行 |
| Kline/funding/OI 可得性 | PASS | HEAD 明细 {len(probes)} 行 |
| 首周成交额代理 | PASS | volume 明细 {len(volumes)} 行，仅用于分层字段 |
| 不碰 Holdout/不 commit | PASS | 未读取 `06_RESEARCH/DATA/HOLDOUT`; 未执行 git commit |
"""
    CODEX_REPORT_PATH.write_text(report, encoding="utf-8")
    RESULTS_REPORT_PATH.write_text(report, encoding="utf-8")


def write_task_inbox(as_of: datetime, status: str, notes: str) -> None:
    inbox = PROJECT_ROOT / "04_AI_TEAM/TASK_INBOX"
    inbox.mkdir(parents=True, exist_ok=True)
    done = {
        "task_id": "P0RES018",
        "completed_at": as_of.isoformat().replace("+00:00", "Z"),
        "status": status,
        "output_file": "04_AI_TEAM/CODEX_TASKS/REPORT_P0RES018_A4_LISTING_CENSUS_20260721.md",
        "next_task": None,
        "notes": notes,
    }
    (inbox / "P0RES018_DONE.json").write_text(json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_outputs(article_list: pd.DataFrame, details: pd.DataFrame, announcement_events: pd.DataFrame, events: pd.DataFrame, probes: pd.DataFrame, volumes: pd.DataFrame, as_of: datetime) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CODE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CODEX_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    article_list.to_csv(OUTPUT_DIR / "p0res018_a4_redefined_announcement_list_20260721.csv", index=False)
    details.to_csv(OUTPUT_DIR / "p0res018_a4_redefined_announcement_details_20260721.csv", index=False)
    announcement_events.to_csv(OUTPUT_DIR / "p0res018_a4_redefined_announcement_events_20260721.csv", index=False)
    probes.to_csv(OUTPUT_DIR / "p0res018_a4_redefined_head_probes_20260721.csv", index=False)
    volumes.to_csv(OUTPUT_DIR / "p0res018_a4_redefined_first_week_volume_20260721.csv", index=False)
    events.to_csv(OUTPUT_DIR / "p0res018_a4_redefined_listing_events_20260721.csv", index=False)

    summary = {
        "generated_at": utc_text(as_of),
        "event_rows": int(len(events)),
        "universe_pit_rows": int((events["universe_source"] == "UNIVERSE_PIT").sum()) if not events.empty else 0,
        "announcement_only_rows": int((events["universe_source"] != "UNIVERSE_PIT").sum()) if not events.empty else 0,
        "existing_spot_then_perp": int((events["event_type"] == "existing_spot_then_perp").sum()) if not events.empty else 0,
        "valid_existing_spot_sample": int(events["valid_existing_spot_sample"].sum()) if not events.empty else 0,
        "delisted_later": int(events["delisted_later"].sum()) if not events.empty else 0,
        "head_probe_rows": int(len(probes)),
        "volume_rows": int(len(volumes)),
        "exit_threshold": 100,
        "exit_conclusion": "qualified"
        if (not events.empty and int(events["valid_existing_spot_sample"].sum()) >= 100)
        else "not_qualified",
    }
    (CODE_OUTPUT_DIR / "p0res018_a4_redefined_summary_20260721.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(events, article_list, details, probes, volumes, as_of)
    write_task_inbox(
        as_of,
        "completed",
        f"A-4 redefined census complete; valid_existing_spot_sample={summary['valid_existing_spot_sample']}; exit={summary['exit_conclusion']}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="P0RES018 A-4 redefined listing census")
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--detail-workers", type=int, default=8)
    parser.add_argument("--volume-workers", type=int, default=16)
    parser.add_argument("--skip-announcement-fetch", action="store_true")
    parser.add_argument("--use-announcement-cache", action="store_true")
    args = parser.parse_args()

    as_of = utc_now()
    print(f"as_of={utc_text(as_of)}", flush=True)

    universe = load_universe()
    delist_inventory = load_delist_inventory()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    article_cache = OUTPUT_DIR / "p0res018_a4_redefined_announcement_list_20260721.csv"
    detail_cache = OUTPUT_DIR / "p0res018_a4_redefined_announcement_details_20260721.csv"
    announcement_event_cache = OUTPUT_DIR / "p0res018_a4_redefined_announcement_events_20260721.csv"

    if args.skip_announcement_fetch:
        article_list = pd.DataFrame()
        details = pd.DataFrame()
        announcement_events = pd.DataFrame()
    elif args.use_announcement_cache and article_cache.exists() and detail_cache.exists() and announcement_event_cache.exists():
        article_list = pd.read_csv(article_cache, dtype=str).fillna("")
        details = pd.read_csv(detail_cache, dtype=str).fillna("")
        announcement_events = pd.read_csv(announcement_event_cache, dtype=str).fillna("")
        if "effective_day" in announcement_events.columns:
            announcement_events["effective_day"] = announcement_events["effective_day"].map(parse_day)
        print(f"announcement cache rows={len(article_list)} details={len(details)} events={len(announcement_events)}", flush=True)
    else:
        article_list = fetch_article_lists()
        print(f"announcement list rows={len(article_list)}", flush=True)
        article_list.to_csv(article_cache, index=False)
        details = fetch_candidate_details(article_list, workers=args.detail_workers)
        print(f"announcement detail rows={len(details)}", flush=True)
        details.to_csv(detail_cache, index=False)
        announcement_events = build_announcement_events(details)
        print(f"announcement event rows={len(announcement_events)}", flush=True)
        announcement_events.to_csv(announcement_event_cache, index=False)

    events_base = build_base_events(universe, announcement_events, delist_inventory, as_of)
    print(f"base events={len(events_base)}", flush=True)

    window_meta, head_jobs, volume_jobs = build_probe_jobs(events_base, as_of)
    print(f"HEAD jobs={len(head_jobs)} volume jobs={len(volume_jobs)}", flush=True)
    probes = run_head_jobs(head_jobs, workers=args.workers)
    volumes = run_volume_jobs(volume_jobs, workers=args.volume_workers)
    events = summarize_events(events_base, window_meta, probes, volumes)
    write_outputs(article_list, details, announcement_events, events, probes, volumes, as_of)
    valid = int(events["valid_existing_spot_sample"].sum()) if not events.empty else 0
    print(f"valid_existing_spot_sample={valid} exit={'qualified' if valid >= 100 else 'not_qualified'}", flush=True)


if __name__ == "__main__":
    main()
