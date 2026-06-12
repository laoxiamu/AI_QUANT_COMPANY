"""Build Binance USD-M perpetual point-in-time universe.

This script builds a data asset only. It does not run strategies,
signals, backtests, or statistical tests.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/UNIVERSE_PIT.csv"
EXCHANGE_INFO_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"
ARCHIVE_BASE_URL = "https://data.binance.vision/data/futures/um"
S3_LIST_URL = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
SENTINEL_DELIVERY_MS = 4133404800000
SOURCE_API = "Binance fapi/v1/exchangeInfo"
SOURCE_ARCHIVE_ENUM = "data.binance.vision S3 ListBucket monthly klines"
SOURCE_ARCHIVE_PROBE = "data.binance.vision monthly/daily klines HEAD probe"


def utc_date_from_ms(value: int) -> date:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date()


def month_floor(day: date) -> date:
    return date(day.year, day.month, 1)


def next_month(day: date) -> date:
    if day.month == 12:
        return date(day.year + 1, 1, 1)
    return date(day.year, day.month + 1, 1)


def iter_months(start: date, end: date) -> list[str]:
    months = []
    cursor = month_floor(start)
    end_month = month_floor(end)
    while cursor <= end_month:
        months.append(cursor.strftime("%Y-%m"))
        cursor = next_month(cursor)
    return months


def fetch_json(url: str, retries: int = 3) -> dict:
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (TimeoutError, URLError, OSError) as exc:
            if attempt == retries:
                raise RuntimeError(f"failed to fetch {url}") from exc
            time.sleep(1.5 * attempt)
    raise AssertionError("unreachable")


def fetch_exchange_info() -> list[dict]:
    payload = fetch_json(EXCHANGE_INFO_URL)
    rows = []
    for item in payload["symbols"]:
        if item.get("contractType") != "PERPETUAL":
            continue
        if item.get("quoteAsset") != "USDT" or item.get("marginAsset") != "USDT":
            continue
        if item.get("status") == "PENDING_TRADING":
            continue
        rows.append(item)
    return rows


def s3_list_prefixes(prefix: str, retries: int = 2) -> set[str]:
    """List first-level S3 prefixes under the official Binance archive path.

    The public website's list.js calls this same bucket endpoint. Some proxy
    environments block the S3 TLS path; callers should fall back to direct
    official archive URL probes when this raises.
    """

    prefixes: set[str] = set()
    marker = ""
    while True:
        params = {"delimiter": "/", "prefix": prefix}
        if marker:
            params["marker"] = marker
        url = f"{S3_LIST_URL}?{urlencode(params)}"
        for attempt in range(1, retries + 1):
            try:
                with urlopen(url, timeout=45) as response:
                    body = response.read()
                break
            except (TimeoutError, URLError, OSError) as exc:
                if attempt == retries:
                    raise RuntimeError(f"failed to list archive prefix {prefix}") from exc
                time.sleep(1.5 * attempt)
        root = ET.fromstring(body)
        namespace = ""
        if root.tag.startswith("{"):
            namespace = root.tag.split("}", 1)[0] + "}"
        for node in root.findall(f"{namespace}CommonPrefixes/{namespace}Prefix"):
            if node.text:
                prefixes.add(node.text)
        truncated = root.findtext(f"{namespace}IsTruncated")
        if truncated != "true":
            return prefixes
        next_marker = root.findtext(f"{namespace}NextMarker")
        if not next_marker:
            return prefixes
        marker = next_marker


def archive_url(symbol: str, interval: str, period: str, frequency: str) -> str:
    quoted_symbol = quote(symbol, safe="")
    return (
        f"{ARCHIVE_BASE_URL}/{frequency}/klines/{quoted_symbol}/{interval}/"
        f"{quoted_symbol}-{interval}-{period}.zip"
    )


def url_exists(url: str, retries: int = 2) -> bool:
    request = Request(url, method="HEAD")
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=20) as response:
                return response.status == 200
        except HTTPError as exc:
            if exc.code == 404:
                return False
            if attempt == retries:
                return False
        except (TimeoutError, URLError, OSError):
            if attempt == retries:
                return False
            time.sleep(1.0 * attempt)
    return False


def first_existing_archive(symbol: str, onboard: date, end: date) -> str | None:
    monthly_periods = iter_months(onboard, end)
    for month in monthly_periods:
        url = archive_url(symbol, "1h", month, "monthly")
        if url_exists(url):
            return url

    daily_start = max(onboard, end.replace(day=1))
    daily_days = pd.date_range(daily_start, end, freq="D").date
    for day in daily_days[:14]:
        period = day.strftime("%Y-%m-%d")
        url = archive_url(symbol, "1h", period, "daily")
        if url_exists(url):
            return url
    return None


def archive_presence_by_probe(rows: list[dict], workers: int) -> dict[str, str | None]:
    today = datetime.now(timezone.utc).date()
    last_complete_month = month_floor(today) - pd.Timedelta(days=1)
    capped_today = today

    def check(item: dict) -> tuple[str, str | None]:
        onboard = utc_date_from_ms(int(item["onboardDate"]))
        delivery_ms = int(item.get("deliveryDate") or SENTINEL_DELIVERY_MS)
        if delivery_ms >= SENTINEL_DELIVERY_MS or item.get("status") == "TRADING":
            end = capped_today
        else:
            end = min(utc_date_from_ms(delivery_ms), capped_today)
        monthly_end = min(end, last_complete_month)
        if monthly_end < onboard:
            monthly_end = end
        return item["symbol"], first_existing_archive(item["symbol"], onboard, monthly_end)

    found: dict[str, str | None] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(check, row): row["symbol"] for row in rows}
        for count, future in enumerate(as_completed(futures), start=1):
            symbol, url = future.result()
            found[symbol] = url
            if count % 100 == 0 or count == len(futures):
                print(f"Archive cross-check {count}/{len(futures)}", flush=True)
    return found


def build_frame(rows: list[dict], archive_ok: dict[str, bool], source_mode: str) -> pd.DataFrame:
    output_rows = []
    for item in rows:
        onboard = utc_date_from_ms(int(item["onboardDate"]))
        delivery_ms = int(item.get("deliveryDate") or SENTINEL_DELIVERY_MS)
        if item.get("status") == "TRADING" or delivery_ms >= SENTINEL_DELIVERY_MS:
            delist_text = ""
        else:
            delist_text = utc_date_from_ms(delivery_ms).isoformat()
        source_parts = [SOURCE_API]
        if archive_ok.get(item["symbol"], False):
            source_parts.append(source_mode)
        else:
            source_parts.append(f"{source_mode} missing")
        output_rows.append(
            {
                "symbol": item["symbol"],
                "onboard_date": onboard.isoformat(),
                "delist_date": delist_text,
                "source": "; ".join(source_parts),
            }
        )
    frame = pd.DataFrame(output_rows)
    return frame.sort_values(["onboard_date", "symbol"]).reset_index(drop=True)


def pit_symbols_for_date(universe: pd.DataFrame | str | Path, target_date: str | date) -> list[str]:
    """Return symbols tradable for a UTC calendar date.

    Day-level convention: onboard_date is inclusive, delist_date is exclusive.
    """

    if isinstance(universe, (str, Path)):
        frame = pd.read_csv(universe, dtype=str).fillna("")
    else:
        frame = universe.copy().fillna("")
    if isinstance(target_date, str):
        day = datetime.fromisoformat(target_date).date()
    else:
        day = target_date
    onboard = pd.to_datetime(frame["onboard_date"], utc=True).dt.date
    delist_raw = frame["delist_date"].replace("", pd.NA)
    delist = pd.to_datetime(delist_raw, utc=True, errors="coerce").dt.date
    mask = (onboard <= day) & (delist.isna() | (day < delist))
    return sorted(frame.loc[mask, "symbol"].tolist())


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(
        path,
        index=False,
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument(
        "--skip-s3-enum",
        action="store_true",
        help="Skip S3 XML directory enumeration and use archive URL probes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = fetch_exchange_info()
    archive_ok: dict[str, bool]
    source_mode = SOURCE_ARCHIVE_ENUM
    if args.skip_s3_enum:
        prefixes = set()
    else:
        try:
            prefixes = s3_list_prefixes("data/futures/um/monthly/klines/")
        except RuntimeError as exc:
            print(f"S3 directory enumeration unavailable: {exc}", flush=True)
            prefixes = set()

    if prefixes:
        symbols_in_archive = {
            prefix.rstrip("/").split("/")[-1]
            for prefix in prefixes
            if prefix.rstrip("/").split("/")[-1].endswith("USDT")
        }
        archive_ok = {row["symbol"]: row["symbol"] in symbols_in_archive for row in rows}
    else:
        source_mode = SOURCE_ARCHIVE_PROBE
        found = archive_presence_by_probe(rows, args.workers)
        archive_ok = {symbol: url is not None for symbol, url in found.items()}

    frame = build_frame(rows, archive_ok, source_mode)
    write_csv(frame, args.output)
    delisted = int(frame["delist_date"].ne("").sum())
    verified = int((~frame["source"].str.contains("missing", regex=False)).sum())
    print(f"Wrote {args.output}")
    print(f"rows={len(frame)} delisted={delisted} archive_verified={verified}")


if __name__ == "__main__":
    main()
