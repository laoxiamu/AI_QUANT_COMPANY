#!/usr/bin/env python3
"""Probe TSMOM universe expansion feasibility with archive HEAD checks.

This script only reads PIT metadata and sends HTTP HEAD requests to public
Binance archive URLs. It does not download ZIP payloads, parse prices, compute
returns, generate signals, or run backtests.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = PROJECT_ROOT / "06_RESEARCH/DATA/UNIVERSE_PIT.csv"
OUTPUT_PATH = PROJECT_ROOT / "06_RESEARCH/CODE/output/c1_tsmom_universe_candidates.csv"
SUMMARY_JSON_PATH = PROJECT_ROOT / "06_RESEARCH/CODE/output/c1_tsmom_universe_summary.json"
RESULT_PATH = PROJECT_ROOT / "06_RESEARCH/RESULTS/20260613_tsmom_universe_expansion.md"

ARCHIVE_BASE_URL = "https://data.binance.vision/data/futures/um/monthly/klines"
INTERVAL = "4h"
ONBOARD_CUTOFF = pd.Timestamp("2021-06-30").date()
DELIST_MIN = pd.Timestamp("2024-06-01").date()
DATA_CUTOFF = pd.Timestamp("2024-12-09 23:59:59")
CURRENT_ENGINE_SYMBOLS = {
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LTCUSDT",
}


@dataclass(frozen=True)
class HeadResult:
    ok: bool | None
    status: str
    url: str


def utc_now_text() -> str:
    """Return a UTC timestamp for reports."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_day(value: object) -> date | None:
    """Parse a YYYY-MM-DD value from the PIT universe table."""
    if pd.isna(value) or value == "":
        return None
    return pd.Timestamp(value).date()


def month_floor(day: date) -> date:
    """Return the first day of day's calendar month."""
    return date(day.year, day.month, 1)


def previous_month(day: date) -> date:
    """Return the first day of the calendar month before day."""
    if day.month == 1:
        return date(day.year - 1, 12, 1)
    return date(day.year, day.month - 1, 1)


def month_label(day: date) -> str:
    """Return YYYY-MM for a calendar month date."""
    return day.strftime("%Y-%m")


def monthly_kline_url(symbol: str, month: str) -> str:
    """Build the Binance monthly 4H kline ZIP URL for one symbol/month."""
    quoted = quote(symbol, safe="")
    return f"{ARCHIVE_BASE_URL}/{quoted}/{INTERVAL}/{quoted}-{INTERVAL}-{month}.zip"


def head_url(url: str, retries: int = 2, timeout: int = 15) -> HeadResult:
    """Probe a URL with HEAD and classify 200/404/network failures."""
    request = Request(url, method="HEAD", headers={"User-Agent": "codex-c1-head-probe/1.0"})
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                return HeadResult(ok=response.status == 200, status=str(response.status), url=url)
        except HTTPError as exc:
            if exc.code == 404:
                return HeadResult(ok=False, status="404", url=url)
            if attempt == retries:
                return HeadResult(ok=None, status=f"http_{exc.code}", url=url)
        except (TimeoutError, URLError, OSError) as exc:
            if attempt == retries:
                return HeadResult(ok=None, status=type(exc).__name__, url=url)
        time.sleep(0.5 * attempt)
    return HeadResult(ok=None, status="unknown", url=url)


def load_candidates() -> pd.DataFrame:
    """Load PIT universe metadata and filter non-v1 symbols with enough age."""
    frame = pd.read_csv(UNIVERSE_PATH, dtype=str).fillna("")
    required = {"symbol", "onboard_date", "delist_date"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"UNIVERSE_PIT missing columns: {sorted(missing)}")

    frame["onboard_day"] = frame["onboard_date"].map(parse_day)
    frame["delist_day"] = frame["delist_date"].map(parse_day)
    if frame["onboard_day"].isna().any():
        raise ValueError("UNIVERSE_PIT contains empty onboard_date values")

    mask = (
        (frame["onboard_day"] <= ONBOARD_CUTOFF)
        & ((frame["delist_day"].isna()) | (frame["delist_day"] >= DELIST_MIN))
        & (~frame["symbol"].isin(CURRENT_ENGINE_SYMBOLS))
    )
    return frame.loc[mask, ["symbol", "onboard_date", "delist_date", "onboard_day", "delist_day"]].copy()


def recent_month_for(delist_day: date | None) -> date:
    """Return 2024-11 or the month before delisting when delisted earlier."""
    default_recent = date(2024, 11, 1)
    if delist_day is not None and delist_day <= date(2024, 11, 30):
        return previous_month(delist_day)
    return default_recent


def estimate_bars(onboard_day: date, delist_day: date | None) -> int:
    """Estimate usable 4H bars through the pre-Holdout cutoff or delisting."""
    end_ts = DATA_CUTOFF
    if delist_day is not None:
        delist_ts = pd.Timestamp(delist_day) - pd.Timedelta(seconds=1)
        end_ts = min(end_ts, delist_ts)
    start_ts = pd.Timestamp(onboard_day)
    if end_ts <= start_ts:
        return 0
    return int(((end_ts - start_ts) / pd.Timedelta(hours=4)) * 0.95)


def probe_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Run two HEAD probes per candidate and return CSV rows plus audit rows."""
    rows: list[dict[str, object]] = []
    audit: list[dict[str, object]] = []
    for index, item in enumerate(candidates.itertuples(index=False), start=1):
        onboard_month = month_label(month_floor(item.onboard_day))
        recent_month = month_label(recent_month_for(item.delist_day))
        first_url = monthly_kline_url(item.symbol, onboard_month)
        recent_url = monthly_kline_url(item.symbol, recent_month)
        first = head_url(first_url)
        recent = head_url(recent_url)

        can_build = first.ok is True and recent.ok is True
        rows.append(
            {
                "symbol": item.symbol,
                "onboard": item.onboard_date,
                "delist": item.delist_date,
                "head_first_ok": first.ok,
                "head_recent_ok": recent.ok,
                "est_bars": estimate_bars(item.onboard_day, item.delist_day) if can_build else pd.NA,
            }
        )
        audit.extend(
            [
                {
                    "symbol": item.symbol,
                    "probe": "first_month",
                    "month": onboard_month,
                    "ok": first.ok,
                    "status": first.status,
                    "url": first.url,
                },
                {
                    "symbol": item.symbol,
                    "probe": "recent_month",
                    "month": recent_month,
                    "ok": recent.ok,
                    "status": recent.status,
                    "url": recent.url,
                },
            ]
        )
        if index % 25 == 0 or index == len(candidates):
            print(f"HEAD checked {index}/{len(candidates)} symbols", flush=True)
    return pd.DataFrame(rows), audit


def bool_count(series: pd.Series) -> int | None:
    """Count True values only when no network-indeterminate rows exist."""
    if series.isna().any():
        return None
    return int(series.sum())


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    """Render a small Markdown table."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_outputs(csv_frame: pd.DataFrame, audit: list[dict[str, object]], generated_at: str) -> None:
    """Write the required CSV, JSON summary, and Markdown report."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    csv_frame.to_csv(OUTPUT_PATH, index=False)
    total = len(csv_frame)
    first_ok = bool_count(csv_frame["head_first_ok"])
    recent_ok = bool_count(csv_frame["head_recent_ok"])
    both_ok = None
    if first_ok is not None and recent_ok is not None:
        both_ok = int((csv_frame["head_first_ok"] & csv_frame["head_recent_ok"]).sum())
    indeterminate = int(csv_frame[["head_first_ok", "head_recent_ok"]].isna().any(axis=1).sum())

    can_build = csv_frame[
        (csv_frame["head_first_ok"] == True) & (csv_frame["head_recent_ok"] == True)  # noqa: E712
    ].copy()
    can_build["est_bars"] = pd.to_numeric(can_build["est_bars"], errors="coerce").astype("Int64")
    top_rows = [
        [
            row.symbol,
            row.onboard,
            row.delist if row.delist else "",
            int(row.est_bars) if pd.notna(row.est_bars) else "",
        ]
        for row in can_build.sort_values(["onboard", "symbol"]).itertuples(index=False)
    ]

    summary = {
        "generated_at_utc": generated_at,
        "archive_path": ARCHIVE_BASE_URL,
        "interval": INTERVAL,
        "candidate_count": total,
        "first_month_available": first_ok,
        "recent_month_available": recent_ok,
        "buildable_count": both_ok,
        "indeterminate_symbol_count": indeterminate,
        "head_audit": audit,
    }
    SUMMARY_JSON_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if indeterminate:
        verdict = "FAILED（网络/代理错误导致 HEAD 结果不完整）"
        stats_text = (
            "- 总候选数：`{}`\n"
            "- 首月可得数：`NA`（HEAD 存在网络不确定结果）\n"
            "- 近月可得数：`NA`（HEAD 存在网络不确定结果）\n"
            "- 两端均可得数：`NA`（HEAD 存在网络不确定结果）\n"
            "- 网络不确定 symbol 数：`{}`"
        ).format(total, indeterminate)
        recommendation = (
            "当前不能给出 universe 扩充规模建议；需在 `HTTPS_PROXY=http://127.0.0.1:7897` "
            "可用后复跑脚本。"
        )
    else:
        verdict = "COMPLETED"
        stats_text = (
            f"- 总候选数：`{total}`\n"
            f"- 首月可得数：`{first_ok}`\n"
            f"- 近月可得数：`{recent_ok}`\n"
            f"- 两端均可得数（可建库）：`{both_ok}`"
        )
        if both_ok is not None and both_ok >= 32:
            recommendation = "建议先做 `20/30/40` 三个 universe 规模档次的建库评估，不进入收益或信号计算。"
        elif both_ok is not None and both_ok >= 20:
            recommendation = "建议先做 `20` 币档 universe；若后续逐日完整性检查通过，再评估 `30` 币档。"
        else:
            recommendation = "可建库候选不足以支撑从当前 8 币扩到 ≥20 币；扩 universe 方向暂不充分。"

    rows_text = md_table(["symbol", "onboard", "delist", "est_4h_bars"], top_rows[:50])
    if not top_rows:
        rows_text = "无可建库候选可列示（或 HEAD 结果不完整）。"

    report = f"""# C1 TSMOM Universe 扩充可行性评估

生成时间（UTC）：{generated_at}

## 结论

状态：**{verdict}**。

{recommendation}

## 口径

- 输入：`06_RESEARCH/DATA/UNIVERSE_PIT.csv`
- 候选筛选：`onboard_date <= 2021-06-30`，且未退市或 `delist_date >= 2024-06-01`；排除当前 v1 8 币。
- HEAD 探测：Binance 官方月度 4H K 线 ZIP，`monthly/klines/<symbol>/4h/<symbol>-4h-YYYY-MM.zip`。
- 探测次数：每个 symbol 两次，首月为 onboard 月，近月为 `2024-11` 或退市前月。
- 估算 bars：`(min(2024-12-09 23:59:59, delist前一秒) - onboard) / 4h * 0.95`。
- 网络：必须经 `HTTPS_PROXY=http://127.0.0.1:7897`；不下载 ZIP。

## 汇总统计

{stats_text}

## 可建库候选

{rows_text}

## 产物

- `06_RESEARCH/CODE/c1_tsmom_universe_feasibility.py`
- `06_RESEARCH/CODE/output/c1_tsmom_universe_candidates.csv`
- `06_RESEARCH/CODE/output/c1_tsmom_universe_summary.json`

## 禁止项自检

- 未下载 ZIP。
- 未读取 `HOLDOUT` 路径。
- 未读取 `*_2026H1` 行情文件。
- 未计算收益、信号或回测。
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
    candidates = load_candidates()
    csv_frame, audit = probe_candidates(candidates)
    write_outputs(csv_frame, audit, generated_at)
    if csv_frame[["head_first_ok", "head_recent_ok"]].isna().any(axis=None):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
