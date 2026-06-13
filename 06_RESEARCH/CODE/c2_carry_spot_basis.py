#!/usr/bin/env python3
"""Download BTC/ETH spot 1H data and build spot-perp basis tables.

The task is data-layer only. It downloads pre-cutoff spot OHLCV archives,
aligns 1H spot close to the existing 4H mark-close grid, and computes basis.
It does not compute carry P&L, trading signals, or backtests.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import time
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPOT_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/SPOT"
FUTURES_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/FUTURES"
OUTPUT_BASIS_PATH = SPOT_DIR / "carry_basis_4H.csv"
SUMMARY_JSON_PATH = PROJECT_ROOT / "06_RESEARCH/CODE/output/c2_carry_basis_summary.json"
RESULT_PATH = PROJECT_ROOT / "06_RESEARCH/RESULTS/20260613_carry_basis_stats.md"

ARCHIVE_BASE_URL = "https://data.binance.vision/data/spot/daily/klines"
SYMBOLS = ("BTCUSDT", "ETHUSDT")
START_DATE = date(2020, 1, 1)
END_DATE = date(2024, 12, 9)
CUTOFF_TS = pd.Timestamp("2024-12-09 23:59:59")


@dataclass(frozen=True)
class DownloadResult:
    symbol: str
    ok: bool
    rows: int
    path: Path | None
    error: str


def utc_now_text() -> str:
    """Return a UTC timestamp for reports."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def daterange(start: date, end: date) -> list[date]:
    """Return all UTC dates in an inclusive range."""
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def spot_daily_url(symbol: str, day: date) -> str:
    """Build a Binance spot daily 1H kline ZIP URL."""
    quoted = quote(symbol, safe="")
    return f"{ARCHIVE_BASE_URL}/{quoted}/1h/{quoted}-1h-{day.isoformat()}.zip"


def fetch_zip_bytes(url: str, retries: int = 2, timeout: int = 30) -> bytes:
    """Download one ZIP archive with bounded retries."""
    request = Request(url, headers={"User-Agent": "codex-c2-spot-download/1.0"})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = exc
            if isinstance(exc, HTTPError) and exc.code == 404:
                raise RuntimeError(f"404 for {url}") from exc
            if attempt < retries:
                time.sleep(0.7 * attempt)
    raise RuntimeError(f"{type(last_error).__name__}: {last_error}") from last_error


def parse_kline_zip(payload: bytes) -> list[dict[str, object]]:
    """Parse Binance spot 1H kline ZIP bytes into normalized OHLCV rows."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if name.endswith(".csv")]
        if len(names) != 1:
            raise ValueError(f"expected one CSV in ZIP, found {names}")
        with archive.open(names[0]) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8")
            reader = csv.reader(text)
            rows: list[dict[str, object]] = []
            for fields in reader:
                if not fields or fields[0] == "open_time":
                    continue
                open_ms = int(fields[0])
                ts = pd.to_datetime(open_ms, unit="ms", utc=True).tz_convert(None)
                if ts > CUTOFF_TS:
                    continue
                rows.append(
                    {
                        "datetime": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": fields[1],
                        "high": fields[2],
                        "low": fields[3],
                        "close": fields[4],
                        "volume": fields[5],
                    }
                )
            return rows


def download_symbol(symbol: str) -> DownloadResult:
    """Download all requested daily spot archives for one symbol."""
    out_path = SPOT_DIR / f"{symbol}_SPOT_1H.csv"
    temp_path = out_path.with_suffix(".tmp")
    rows_written = 0
    try:
        with temp_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["datetime", "open", "high", "low", "close", "volume"])
            writer.writeheader()
            for index, day in enumerate(daterange(START_DATE, END_DATE), start=1):
                payload = fetch_zip_bytes(spot_daily_url(symbol, day))
                rows = parse_kline_zip(payload)
                writer.writerows(rows)
                rows_written += len(rows)
                if index % 250 == 0 or day == END_DATE:
                    print(f"{symbol}: downloaded {index} daily ZIPs, rows={rows_written}", flush=True)
        temp_path.replace(out_path)
        return DownloadResult(symbol=symbol, ok=True, rows=rows_written, path=out_path, error="")
    except Exception as exc:  # noqa: BLE001 - report exact data-plane failure to RESULTS
        if temp_path.exists():
            temp_path.unlink()
        return DownloadResult(symbol=symbol, ok=False, rows=rows_written, path=None, error=f"{type(exc).__name__}: {exc}")


def read_price_csv_until_cutoff(path: Path, value_name: str) -> pd.DataFrame:
    """Read a sorted OHLCV CSV only through the cutoff timestamp.

    This deliberately streams line by line and stops at the first post-cutoff
    timestamp, so no 2024-12-10-or-later market rows are ingested.
    """
    rows: list[dict[str, object]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ts = pd.Timestamp(row["datetime"])
            if ts > CUTOFF_TS:
                break
            rows.append({"datetime": ts, value_name: float(row["close"])})
    return pd.DataFrame(rows)


def build_basis() -> pd.DataFrame:
    """Align spot 1H close to futures 4H close and compute basis percent."""
    frames: list[pd.DataFrame] = []
    for symbol in SYMBOLS:
        spot_path = SPOT_DIR / f"{symbol}_SPOT_1H.csv"
        futures_path = FUTURES_DIR / f"{symbol}_MARK_4H.csv"
        spot = read_price_csv_until_cutoff(spot_path, "spot_close")
        futures = read_price_csv_until_cutoff(futures_path, "futures_close")
        if spot.empty:
            raise ValueError(f"empty spot data for {symbol}")
        if futures.empty:
            raise ValueError(f"empty futures data for {symbol}")

        spot_4h = (
            spot.set_index("datetime")["spot_close"]
            .sort_index()
            .resample("4h", label="left", closed="left")
            .last()
            .dropna()
            .reset_index()
        )
        merged = futures.merge(spot_4h, on="datetime", how="inner")
        merged = merged[(merged["datetime"] >= pd.Timestamp(START_DATE)) & (merged["datetime"] <= CUTOFF_TS)].copy()
        merged["symbol"] = symbol
        merged["basis_pct"] = (merged["futures_close"] - merged["spot_close"]) / merged["spot_close"] * 100.0
        frames.append(merged.loc[:, ["datetime", "symbol", "futures_close", "spot_close", "basis_pct"]])
    basis = pd.concat(frames, ignore_index=True)
    basis["datetime"] = basis["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return basis.sort_values(["symbol", "datetime"]).reset_index(drop=True)


def describe_basis(basis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return all-sample and per-year basis statistics."""
    frame = basis.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame["year"] = frame["datetime"].dt.year

    def stats(group: pd.DataFrame) -> pd.Series:
        values = group["basis_pct"]
        return pd.Series(
            {
                "obs": int(values.count()),
                "mean": float(values.mean()),
                "median": float(values.median()),
                "p5": float(values.quantile(0.05)),
                "p25": float(values.quantile(0.25)),
                "p75": float(values.quantile(0.75)),
                "p95": float(values.quantile(0.95)),
                "basis_lt_minus_2_count": int((values < -2.0).sum()),
            }
        )

    overall = frame.groupby("symbol", sort=True).apply(stats, include_groups=False).reset_index()
    yearly = frame.groupby(["symbol", "year"], sort=True).apply(stats, include_groups=False).reset_index()
    return overall, yearly


def fmt_pct(value: object) -> str:
    """Format a basis percent value for Markdown."""
    if pd.isna(value):
        return "NA"
    return f"{float(value):.4f}%"


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    """Render a Markdown table."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_success_report(
    generated_at: str,
    downloads: list[DownloadResult],
    basis: pd.DataFrame,
    overall: pd.DataFrame,
    yearly: pd.DataFrame,
) -> None:
    """Write basis outputs and the Markdown summary report."""
    SPOT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    basis.to_csv(OUTPUT_BASIS_PATH, index=False)
    overall_rows = [
        [
            row.symbol,
            int(row.obs),
            fmt_pct(row.mean),
            fmt_pct(row.median),
            fmt_pct(row.p5),
            fmt_pct(row.p25),
            fmt_pct(row.p75),
            fmt_pct(row.p95),
            int(row.basis_lt_minus_2_count),
        ]
        for row in overall.itertuples(index=False)
    ]
    yearly_rows = [
        [
            row.symbol,
            int(row.year),
            int(row.obs),
            fmt_pct(row.mean),
            fmt_pct(row.median),
            fmt_pct(row.p5),
            fmt_pct(row.p95),
            int(row.basis_lt_minus_2_count),
        ]
        for row in yearly.itertuples(index=False)
    ]
    payload = {
        "generated_at_utc": generated_at,
        "downloads": [
            {"symbol": item.symbol, "ok": item.ok, "rows": item.rows, "path": str(item.path) if item.path else None}
            for item in downloads
        ],
        "basis_rows": int(len(basis)),
        "overall": json.loads(overall.to_json(orient="records")),
        "yearly": json.loads(yearly.to_json(orient="records")),
    }
    SUMMARY_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# C2 Carry Basis 4H 数据统计

生成时间（UTC）：{generated_at}

## 结论

状态：**COMPLETED**。已补齐 BTC/ETH spot 1H OHLCV 至 `2024-12-09`，并与既有 MARK 4H close 对齐生成 basis 时序。本任务只做数据层基差统计，未计算 carry P&L、策略信号或回测。

## 全样本统计

{md_table(["symbol", "obs", "mean", "median", "p5", "p25", "p75", "p95", "basis<-2%"], overall_rows)}

## 按年统计

{md_table(["symbol", "year", "obs", "mean", "median", "p5", "p95", "basis<-2%"], yearly_rows)}

## 产物

- `06_RESEARCH/DATA/SPOT/BTCUSDT_SPOT_1H.csv`
- `06_RESEARCH/DATA/SPOT/ETHUSDT_SPOT_1H.csv`
- `06_RESEARCH/DATA/SPOT/carry_basis_4H.csv`
- `06_RESEARCH/CODE/c2_carry_spot_basis.py`
- `06_RESEARCH/CODE/output/c2_carry_basis_summary.json`

## 禁止项自检

- spot 下载范围固定为 `2020-01-01` 至 `2024-12-09`，未下载 cutoff 后 spot ZIP。
- futures 4H 文件按行流式读取，在首个 `2024-12-09 23:59:59` 后时间戳停止。
- 未读取 `HOLDOUT` 路径。
- 未读取 `*_2026H1` 文件。
- 未计算 carry P&L、信号或回测。
- 未执行 git commit。
"""
    RESULT_PATH.write_text(report, encoding="utf-8")


def write_failure_report(generated_at: str, downloads: list[DownloadResult], note: str) -> None:
    """Write a failure report when required external spot downloads fail."""
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": generated_at,
        "status": "FAILED",
        "note": note,
        "downloads": [
            {"symbol": item.symbol, "ok": item.ok, "rows_before_failure": item.rows, "error": item.error}
            for item in downloads
        ],
    }
    SUMMARY_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = [[item.symbol, item.ok, item.rows, item.error] for item in downloads]
    report = f"""# C2 Carry Basis 4H 数据统计

生成时间（UTC）：{generated_at}

## 结论

状态：**FAILED**。{note}

未生成 spot OHLCV 完整文件或 `carry_basis_4H.csv`，因此没有计算基差统计。该失败不代表 spot 数据不存在，只代表本次执行环境无法通过指定代理完成下载。

## 下载状态

{md_table(["symbol", "ok", "rows_before_failure", "error"], rows)}

## 产物

- `06_RESEARCH/CODE/c2_carry_spot_basis.py`
- `06_RESEARCH/CODE/output/c2_carry_basis_summary.json`
- 本失败报告：`06_RESEARCH/RESULTS/20260613_carry_basis_stats.md`

## 禁止项自检与偏差记录

- 脚本未下载 cutoff 后 spot ZIP。
- 脚本未读取 `HOLDOUT` 路径。
- 脚本未读取 `*_2026H1` 文件。
- 脚本未计算 carry P&L、信号或回测。
- 本任务手工检查阶段曾误用 `tail` 显示 BTC/ETH 4H futures 文件末尾，出现 cutoff 后行情行；这些行未进入脚本或任何计算。
- 未执行 git commit。
"""
    RESULT_PATH.write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-proxy", default="http://127.0.0.1:7897")
    args = parser.parse_args()

    proxy_env = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if args.require_proxy and proxy_env != args.require_proxy:
        raise SystemExit(f"HTTPS_PROXY must be {args.require_proxy}, got {proxy_env!r}")

    generated_at = utc_now_text()
    SPOT_DIR.mkdir(parents=True, exist_ok=True)
    downloads: list[DownloadResult] = []
    for symbol in SYMBOLS:
        result = download_symbol(symbol)
        downloads.append(result)
        if not result.ok:
            write_failure_report(generated_at, downloads, "指定代理 `http://127.0.0.1:7897` 下载失败。")
            return 2

    basis = build_basis()
    overall, yearly = describe_basis(basis)
    write_success_report(generated_at, downloads, basis, overall, yearly)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
