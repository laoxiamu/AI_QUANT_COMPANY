"""A-4 listing archive census.

This script only counts listings and probes public archive availability with
HTTP HEAD. It does not download archive payloads or compute returns,
volatility, signals, or backtests.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/UNIVERSE_PIT.csv"
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/CODE/output"
RESULT_PATH = PROJECT_ROOT / "06_RESEARCH/RESULTS/20260612_a4_listing_census.md"

ARCHIVE_BASE_URL = "https://data.binance.vision/data/futures/um"
DEFAULT_PROXY = "http://127.0.0.1:7897"
START_YEAR = 2022
FIRST_N_DAYS = 30
KLINE_INTERVAL = "1h"


@dataclass(frozen=True)
class HeadResult:
    url: str
    ok: bool
    status: str


@dataclass(frozen=True)
class ProbeJob:
    symbol: str
    dataset: str
    period: str
    url: str


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def parse_day(value: object) -> date | None:
    if pd.isna(value) or value == "":
        return None
    return pd.Timestamp(value).date()


def day_range(start: date, end: date) -> list[date]:
    if end < start:
        return []
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


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


def kline_daily_url(symbol: str, day: date) -> str:
    quoted = quote(symbol, safe="")
    period = day.isoformat()
    return (
        f"{ARCHIVE_BASE_URL}/daily/klines/{quoted}/{KLINE_INTERVAL}/"
        f"{quoted}-{KLINE_INTERVAL}-{period}.zip"
    )


def funding_monthly_url(symbol: str, period: str) -> str:
    quoted = quote(symbol, safe="")
    return (
        f"{ARCHIVE_BASE_URL}/monthly/fundingRate/{quoted}/"
        f"{quoted}-fundingRate-{period}.zip"
    )


def head_url(url: str, retries: int = 2) -> HeadResult:
    request = Request(url, method="HEAD")
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=20) as response:
                return HeadResult(url=url, ok=response.status == 200, status=str(response.status))
        except HTTPError as exc:
            if exc.code == 404:
                return HeadResult(url=url, ok=False, status="404")
            if attempt == retries:
                return HeadResult(url=url, ok=False, status=str(exc.code))
        except (TimeoutError, URLError, OSError) as exc:
            if attempt == retries:
                return HeadResult(url=url, ok=False, status=type(exc).__name__)
        time.sleep(0.7 * attempt)
    return HeadResult(url=url, ok=False, status="unknown")


def load_universe() -> pd.DataFrame:
    frame = pd.read_csv(UNIVERSE_PATH, dtype=str).fillna("")
    required = {"symbol", "onboard_date", "delist_date", "source"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"UNIVERSE_PIT missing columns: {sorted(missing)}")
    frame["onboard_day"] = frame["onboard_date"].map(parse_day)
    frame["delist_day"] = frame["delist_date"].map(parse_day)
    if frame["onboard_day"].isna().any():
        raise ValueError("UNIVERSE_PIT has empty onboard_date values")
    return frame


def build_probe_jobs(frame: pd.DataFrame, today: date) -> tuple[pd.DataFrame, list[ProbeJob]]:
    rows: list[dict] = []
    jobs: list[ProbeJob] = []
    for item in frame.itertuples(index=False):
        symbol = item.symbol
        onboard = item.onboard_day
        delist = item.delist_day
        nominal_end = onboard + timedelta(days=FIRST_N_DAYS - 1)
        if delist is not None and delist <= nominal_end:
            observed_end = delist - timedelta(days=1)
            delisted_within_window = True
        else:
            observed_end = nominal_end
            delisted_within_window = False
        matured = observed_end < today
        expected_days = day_range(onboard, observed_end) if matured else []
        funding_periods = month_periods(onboard, observed_end) if matured else []
        rows.append(
            {
                "symbol": symbol,
                "onboard_date": onboard.isoformat(),
                "onboard_year": onboard.year,
                "delist_date": "" if delist is None else delist.isoformat(),
                "window_start": onboard.isoformat(),
                "window_end": observed_end.isoformat(),
                "matured_30d_window": matured,
                "delisted_within_30d": delisted_within_window,
                "expected_kline_days": len(expected_days),
                "expected_funding_months": len(funding_periods),
            }
        )
        for day in expected_days:
            jobs.append(ProbeJob(symbol, "kline_1h_daily", day.isoformat(), kline_daily_url(symbol, day)))
        for period in funding_periods:
            jobs.append(ProbeJob(symbol, "fundingRate_monthly", period, funding_monthly_url(symbol, period)))
    return pd.DataFrame(rows), jobs


def run_head_jobs(jobs: list[ProbeJob], workers: int) -> pd.DataFrame:
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(head_url, job.url): job for job in jobs}
        for count, future in enumerate(as_completed(futures), start=1):
            job = futures[future]
            result = future.result()
            rows.append(
                {
                    "symbol": job.symbol,
                    "dataset": job.dataset,
                    "period": job.period,
                    "ok": result.ok,
                    "status": result.status,
                    "url": result.url,
                }
            )
            if count % 1000 == 0 or count == len(jobs):
                print(f"HEAD checked {count}/{len(jobs)}", flush=True)
    return pd.DataFrame(rows)


def summarize_probes(listings: pd.DataFrame, probes: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    grouped = probes.groupby(["symbol", "dataset"], sort=False) if not probes.empty else {}
    for item in listings.itertuples(index=False):
        symbol = item.symbol
        out = item._asdict()
        kline = (
            grouped.get_group((symbol, "kline_1h_daily"))
            if not probes.empty and (symbol, "kline_1h_daily") in grouped.groups
            else pd.DataFrame(columns=probes.columns)
        )
        funding = (
            grouped.get_group((symbol, "fundingRate_monthly"))
            if not probes.empty and (symbol, "fundingRate_monthly") in grouped.groups
            else pd.DataFrame(columns=probes.columns)
        )
        kline_found = int(kline["ok"].sum()) if not kline.empty else 0
        funding_found = int(funding["ok"].sum()) if not funding.empty else 0
        missing_kline = sorted(kline.loc[~kline["ok"], "period"].tolist()) if not kline.empty else []
        missing_funding = sorted(funding.loc[~funding["ok"], "period"].tolist()) if not funding.empty else []
        out.update(
            {
                "kline_days_found": kline_found,
                "funding_months_found": funding_found,
                "kline_30d_complete": bool(item.matured_30d_window and kline_found == item.expected_kline_days),
                "funding_window_complete": bool(
                    item.matured_30d_window and funding_found == item.expected_funding_months
                ),
                "archive_window_available": bool(
                    item.matured_30d_window
                    and kline_found == item.expected_kline_days
                    and funding_found == item.expected_funding_months
                ),
                "missing_kline_days": ";".join(missing_kline[:12])
                + (";..." if len(missing_kline) > 12 else ""),
                "missing_funding_months": ";".join(missing_funding),
            }
        )
        rows.append(out)
    return pd.DataFrame(rows)


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def pct(numer: int, denom: int) -> str:
    if denom == 0:
        return "NA"
    return f"{numer / denom:.2%}"


def write_outputs(
    universe: pd.DataFrame,
    listings_2022: pd.DataFrame,
    probes: pd.DataFrame,
    summary: pd.DataFrame,
    generated_at: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    annual = (
        universe.groupby(universe["onboard_day"].map(lambda d: d.year))
        .size()
        .reset_index(name="new_listings")
        .rename(columns={"onboard_day": "year"})
    )
    annual.to_csv(OUTPUT_DIR / "a4_listing_census_by_year.csv", index=False)
    probes.to_csv(OUTPUT_DIR / "a4_listing_archive_head_probes.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "a4_listing_archive_summary.csv", index=False)

    matured = summary[summary["matured_30d_window"]].copy()
    by_year_rows: list[list[object]] = []
    for year, group in summary.groupby("onboard_year", sort=True):
        matured_group = group[group["matured_30d_window"]]
        available = int(matured_group["archive_window_available"].sum())
        kline_ok = int(matured_group["kline_30d_complete"].sum())
        funding_ok = int(matured_group["funding_window_complete"].sum())
        by_year_rows.append(
            [
                year,
                len(group),
                len(matured_group),
                kline_ok,
                funding_ok,
                available,
                pct(available, len(matured_group)),
            ]
        )

    overall = {
        "generated_at": generated_at,
        "universe_rows": int(len(universe)),
        "new_listings_2022_plus": int(len(summary)),
        "matured_30d_windows": int(len(matured)),
        "immature_30d_windows": int((~summary["matured_30d_window"]).sum()),
        "kline_complete": int(matured["kline_30d_complete"].sum()),
        "funding_complete": int(matured["funding_window_complete"].sum()),
        "archive_window_available": int(matured["archive_window_available"].sum()),
        "archive_window_available_rate": None
        if len(matured) == 0
        else float(matured["archive_window_available"].mean()),
        "head_probe_rows": int(len(probes)),
        "proxy": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "",
    }
    (OUTPUT_DIR / "a4_listing_census_summary.json").write_text(
        json.dumps(overall, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    annual_rows = annual.values.tolist()
    missing = summary[
        summary["matured_30d_window"] & ~summary["archive_window_available"]
    ].copy()
    missing_rows = missing[
        [
            "symbol",
            "onboard_date",
            "window_end",
            "expected_kline_days",
            "kline_days_found",
            "expected_funding_months",
            "funding_months_found",
            "missing_kline_days",
            "missing_funding_months",
        ]
    ].head(20).values.tolist()

    result_md = f"""# A-4 新上市数据普查

Generated: {generated_at}

## 结论

- `UNIVERSE_PIT.csv` 共 {len(universe)} 个 Binance USDT-M 永续合约；2022 起新上市 {len(summary)} 个。
- 已成熟的“上市后 30 天”窗口 {len(matured)} 个，K 线与 funding 归档均可得 {overall["archive_window_available"]} 个，可得率 {pct(overall["archive_window_available"], len(matured))}。
- 未成熟窗口 {overall["immature_30d_windows"]} 个，未纳入可得率分母。
- 本任务只做计数与 HEAD 可得性探测；未下载 zip、未读取行情内容、未计算收益/波动/信号。

## 口径

- 数据源：`06_RESEARCH/DATA/UNIVERSE_PIT.csv`
- 范围：按 `onboard_date` 统计全部年份上市数；对 `onboard_date >= 2022-01-01` 的合约做归档探测。
- K 线：`data.binance.vision/data/futures/um/daily/klines/<symbol>/1h/`，上市日起最多 30 个 UTC 自然日逐日 `HEAD`。
- Funding：官方归档实际为 monthly `fundingRate` ZIP；对覆盖上市后 30 天窗口的月份做 `HEAD`。
- 退市边界：若合约上市 30 天内退市，期望窗口截到 `delist_date` 前一日。
- 当前 UTC 日尚未走完或 30 天窗口未结束的合约标为未成熟，不纳入可得率分母。
- 网络：`HTTPS_PROXY={overall["proxy"]}`。

## 分年新上市数量

{md_table(["year", "new_listings"], annual_rows)}

## 2022 起前 30 天归档可得率

{md_table(["year", "listed", "matured", "kline complete", "funding complete", "both available", "both rate"], by_year_rows)}

## 缺口样例

{md_table(["symbol", "onboard", "window_end", "kline expected", "kline found", "funding months expected", "funding months found", "missing kline days", "missing funding months"], missing_rows) if missing_rows else "无成熟窗口缺口。"}

## 产物

- `06_RESEARCH/CODE/a4_listing_census.py`
- `06_RESEARCH/CODE/output/a4_listing_census_by_year.csv`
- `06_RESEARCH/CODE/output/a4_listing_archive_head_probes.csv`
- `06_RESEARCH/CODE/output/a4_listing_archive_summary.csv`
- `06_RESEARCH/CODE/output/a4_listing_census_summary.json`
"""
    RESULT_PATH.write_text(result_md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="A-4 listing archive census")
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--proxy", default=DEFAULT_PROXY)
    args = parser.parse_args()

    os.environ.setdefault("HTTPS_PROXY", args.proxy)
    os.environ.setdefault("https_proxy", args.proxy)

    generated_at = utc_now_text()
    today = datetime.now(timezone.utc).date()
    universe = load_universe()
    listings_2022 = universe[universe["onboard_day"].map(lambda d: d.year >= START_YEAR)].copy()
    listings, jobs = build_probe_jobs(listings_2022, today)
    print(
        f"Loaded {len(universe)} universe rows; {len(listings)} listings since {START_YEAR}; "
        f"{len(jobs)} HEAD probes",
        flush=True,
    )
    probes = run_head_jobs(jobs, workers=args.workers)
    summary = summarize_probes(listings, probes)
    write_outputs(universe, listings_2022, probes, summary, generated_at)
    matured = summary[summary["matured_30d_window"]]
    available = int(matured["archive_window_available"].sum())
    print(
        f"matured={len(matured)} available={available} rate={pct(available, len(matured))}",
        flush=True,
    )


if __name__ == "__main__":
    main()
