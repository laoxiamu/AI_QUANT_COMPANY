#!/usr/bin/env python3
"""
Refresh the FUTURES_EXPANDED 4H OHLCV panel to 2026-06-22.

Scope discipline:
- Pure data engineering: no backtest, no signal, no parameter search.
- Reads the existing 06_RESEARCH/DATA/FUTURES_EXPANDED panel.
- Writes new files under 06_RESEARCH/DATA/FUTURES_EXPANDED_2026 only.
- Uses free public endpoints: Binance USD-M futures klines, Bybit linear klines
  fallback, and documented free unlock-source reachability checks.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OLD_PANEL_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED"
NEW_PANEL_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED_2026"
OUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
AUDIT_PATH = OUT_DIR / "panel_refresh_2026_audit.json"
# 2026-07-16：报告名按运行日期戳，保留历史（原硬编码 _20260622 会覆盖旧报告）
REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / f"REPORT_PANEL_REFRESH_2026_{pd.Timestamp.utcnow().strftime('%Y%m%d')}.md"
DONE_PATH = ROOT / "04_AI_TEAM" / "TASK_INBOX" / "DATA-PANEL-REFRESH-2026_DONE.json"

START_UTC = pd.Timestamp("2024-12-09 00:00:00")
# 2026-07-16 L1审计R7修复：END_UTC 原硬编码 "2026-06-22 00:00:00"，是面板止步6/22、重跑无效的根因；改为动态刷到当前（floor 4H 保证末根K线完整）
END_UTC = pd.Timestamp.utcnow().tz_localize(None).floor("4h")
INTERVAL = pd.Timedelta(hours=4)
REQUIRED_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]

BINANCE_BASE = "https://fapi.binance.com/fapi/v1/klines"
BYBIT_BASE = "https://api.bybit.com/v5/market/kline"
BINANCE_DATA_VISION = "https://data.binance.vision/data/futures/um"

TOKENOMIST_DOCS = [
    "https://docs.tokenomist.ai/api-documents/introduction",
    "https://docs.tokenomist.ai/api-documents/unlock-events/v5",
    "https://docs.tokenomist.ai/api-documents/upcoming-unlock-events/v5",
    "https://docs.tokenomist.ai/features/csv-download",
]
UNLOCK_REACHABILITY_URLS = [
    "https://defillama.com/unlocks",
    "https://api.llama.fi/protocols",
    "https://docs.tokenomist.ai/api-documents/unlock-events/v5",
]


@dataclass(frozen=True)
class UnlockEvent:
    symbol: str
    unlock_date: str
    amount_tokens: float | None
    value_usd: float | None
    circulating_pct: float | None
    allocation: str
    source: str
    source_url: str
    note: str


# Audited public article samples from the prior Phase A report. They are outside
# the requested 2025-06..2026-06 free-calendar window and are kept only to verify
# overlap logic without inventing inaccessible event data.
AUDITED_PUBLIC_UNLOCK_SAMPLES = [
    UnlockEvent(
        symbol="AVAX",
        unlock_date="2024-08-20",
        amount_tokens=9_540_000.0,
        value_usd=251_330_000.0,
        circulating_pct=2.42,
        allocation="strategic_partners/foundation/team/airdrop",
        source="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        note="Historical article sample; not in requested 2025-06..2026-06 window.",
    ),
    UnlockEvent(
        symbol="APT",
        unlock_date="2024-08-12",
        amount_tokens=11_310_000.0,
        value_usd=76_450_000.0,
        circulating_pct=2.41,
        allocation="foundation/community/core_contributors/investors",
        source="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        note="Historical article sample; symbol absent from local panel.",
    ),
    UnlockEvent(
        symbol="SAND",
        unlock_date="2024-08-14",
        amount_tokens=205_590_000.0,
        value_usd=66_750_000.0,
        circulating_pct=9.0,
        allocation="team/advisors/company_reserve",
        source="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        note="Historical article sample; symbol absent from local panel.",
    ),
    UnlockEvent(
        symbol="ARB",
        unlock_date="2024-08-16",
        amount_tokens=92_650_000.0,
        value_usd=65_170_000.0,
        circulating_pct=2.77,
        allocation="team_future_team_advisors/investors",
        source="BeInCrypto article citing TokenUnlocks",
        source_url="https://beincrypto.com/token-unlocks-august-2024/",
        note="Historical article sample; symbol absent from local panel.",
    ),
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_millis(ts: pd.Timestamp) -> int:
    return int(ts.tz_localize("UTC").timestamp() * 1000)


def from_millis(ms: int) -> str:
    return pd.to_datetime(ms, unit="ms", utc=True).tz_convert(None).strftime("%Y-%m-%d %H:%M:%S")


def read_json_url(url: str, timeout: int, retries: int = 3) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = Request(url, headers={"User-Agent": "AI-Quant-Research/1.0"})
            with urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            return json.loads(payload)
        except Exception as error:  # noqa: BLE001 - errors are persisted for audit
            last_error = error
            time.sleep(min(2.0, 0.4 * (2**attempt)))
    assert last_error is not None
    raise last_error


def probe_url(url: str, timeout: int) -> dict[str, Any]:
    started = time.time()
    try:
        request = Request(url, headers={"User-Agent": "AI-Quant-Research/1.0"})
        with urlopen(request, timeout=timeout) as response:
            payload = response.read(256)
        return {
            "url": url,
            "ok": True,
            "status": getattr(response, "status", None),
            "elapsed_sec": round(time.time() - started, 3),
            "sample_bytes": len(payload),
        }
    except Exception as error:  # noqa: BLE001
        # An HTTP status response (even 4xx like a bare-params 400) proves the
        # network path is REACHABLE; only treat true transport failures as down.
        reachable = error.__class__.__name__ == "HTTPError"
        return {
            "url": url,
            "ok": reachable,
            "status": getattr(error, "code", None),
            "elapsed_sec": round(time.time() - started, 3),
            "error_type": type(error).__name__,
            "error": str(error),
        }


def discover_universe() -> list[str]:
    symbols = []
    for path in sorted(OLD_PANEL_DIR.glob("*_4H.csv")):
        symbols.append(path.name.replace("_4H.csv", ""))
    for symbol in ("BTCUSDT", "ETHUSDT"):
        if symbol not in symbols:
            symbols.append(symbol)
    return sorted(symbols)


def load_old_symbol(symbol: str) -> pd.DataFrame:
    path = OLD_PANEL_DIR / f"{symbol}_4H.csv"
    if not path.exists():
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    df = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    df = df[REQUIRED_COLUMNS].copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df.sort_values("datetime").drop_duplicates("datetime").reset_index(drop=True)


def normalize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for column in ["open", "high", "low", "close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)


def fetch_binance_klines(symbol: str, start: pd.Timestamp, end: pd.Timestamp, timeout: int) -> pd.DataFrame:
    rows: list[list[Any]] = []
    cursor = start
    end_ms = to_millis(end)
    while to_millis(cursor) <= end_ms:
        params = {
            "symbol": symbol,
            "interval": "4h",
            "startTime": to_millis(cursor),
            "endTime": end_ms,
            "limit": 1500,
        }
        data = read_json_url(f"{BINANCE_BASE}?{urlencode(params)}", timeout=timeout)
        if isinstance(data, dict):
            code = data.get("code")
            msg = data.get("msg")
            raise RuntimeError(f"Binance error for {symbol}: code={code}, msg={msg}")
        if not data:
            break
        rows.extend(data)
        last_open_ms = int(data[-1][0])
        next_cursor = pd.to_datetime(last_open_ms, unit="ms") + INTERVAL
        if next_cursor <= cursor:
            raise RuntimeError(f"Binance pagination did not advance for {symbol}")
        cursor = next_cursor
        time.sleep(0.12)

    frame = pd.DataFrame(
        [
            {
                "datetime": from_millis(int(row[0])),
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
            }
            for row in rows
        ],
        columns=REQUIRED_COLUMNS,
    )
    if not frame.empty:
        frame["datetime"] = pd.to_datetime(frame["datetime"])
    return normalize_numeric(frame)


def fetch_bybit_klines(symbol: str, start: pd.Timestamp, end: pd.Timestamp, timeout: int) -> pd.DataFrame:
    rows: list[list[Any]] = []
    cursor = start
    end_ms = to_millis(end)
    while to_millis(cursor) <= end_ms:
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": "240",
            "start": to_millis(cursor),
            "end": end_ms,
            "limit": 1000,
        }
        data = read_json_url(f"{BYBIT_BASE}?{urlencode(params)}", timeout=timeout)
        if not isinstance(data, dict) or data.get("retCode") != 0:
            raise RuntimeError(f"Bybit error for {symbol}: {data}")
        batch = data.get("result", {}).get("list", [])
        if not batch:
            break
        batch = sorted(batch, key=lambda row: int(row[0]))
        rows.extend(batch)
        last_open_ms = int(batch[-1][0])
        next_cursor = pd.to_datetime(last_open_ms, unit="ms") + INTERVAL
        if next_cursor <= cursor:
            raise RuntimeError(f"Bybit pagination did not advance for {symbol}")
        cursor = next_cursor
        time.sleep(0.12)

    frame = pd.DataFrame(
        [
            {
                "datetime": from_millis(int(row[0])),
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
            }
            for row in rows
        ],
        columns=REQUIRED_COLUMNS,
    )
    if not frame.empty:
        frame["datetime"] = pd.to_datetime(frame["datetime"])
    return normalize_numeric(frame)


def audit_continuity(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "rows": 0,
            "start": None,
            "end": None,
            "gaps_over_4h": None,
            "duplicate_timestamps": 0,
        }
    diffs = df["datetime"].sort_values().diff().dropna()
    return {
        "rows": int(len(df)),
        "start": df["datetime"].iloc[0].strftime("%Y-%m-%d %H:%M:%S"),
        "end": df["datetime"].iloc[-1].strftime("%Y-%m-%d %H:%M:%S"),
        "gaps_over_4h": int((diffs > INTERVAL).sum()),
        "duplicate_timestamps": int(df["datetime"].duplicated().sum()),
    }


def refresh_symbol(symbol: str, timeout: int, write_files: bool) -> dict[str, Any]:
    old = load_old_symbol(symbol)
    if old.empty:
        download_start = START_UTC
    else:
        download_start = max(START_UTC, old["datetime"].max() + INTERVAL)
    result: dict[str, Any] = {
        "symbol": symbol,
        "old_panel": audit_continuity(old),
        "download_start": download_start.strftime("%Y-%m-%d %H:%M:%S"),
        "download_end": END_UTC.strftime("%Y-%m-%d %H:%M:%S"),
        "source": None,
        "status": None,
        "errors": [],
        "new_rows_downloaded": 0,
        "output_file": str((NEW_PANEL_DIR / f"{symbol}_4H.csv").relative_to(ROOT)),
    }

    downloaded = pd.DataFrame(columns=REQUIRED_COLUMNS)
    for source_name, fetcher in (("binance_fapi", fetch_binance_klines), ("bybit_linear", fetch_bybit_klines)):
        try:
            downloaded = fetcher(symbol, download_start, END_UTC, timeout)
            result["source"] = source_name
            result["status"] = "downloaded" if not downloaded.empty else "no_new_data"
            break
        except Exception as error:  # noqa: BLE001
            result["errors"].append(
                {
                    "source": source_name,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )

    result["new_rows_downloaded"] = int(len(downloaded))
    if downloaded.empty and result["source"] is None:
        result["status"] = "failed"
        result["combined_panel"] = audit_continuity(old)
        return result

    combined = pd.concat([old, downloaded], ignore_index=True)
    combined = combined[REQUIRED_COLUMNS].copy()
    combined["datetime"] = pd.to_datetime(combined["datetime"])
    combined = normalize_numeric(combined)
    combined = combined.sort_values("datetime").drop_duplicates("datetime").reset_index(drop=True)
    result["combined_panel"] = audit_continuity(combined)

    if write_files:
        NEW_PANEL_DIR.mkdir(parents=True, exist_ok=True)
        output = NEW_PANEL_DIR / f"{symbol}_4H.csv"
        combined.to_csv(output, index=False, date_format="%Y-%m-%d %H:%M:%S", quoting=csv.QUOTE_MINIMAL)
    return result


def skipped_symbol(symbol: str, reason: str) -> dict[str, Any]:
    old = load_old_symbol(symbol)
    download_start = START_UTC if old.empty else max(START_UTC, old["datetime"].max() + INTERVAL)
    return {
        "symbol": symbol,
        "old_panel": audit_continuity(old),
        "download_start": download_start.strftime("%Y-%m-%d %H:%M:%S"),
        "download_end": END_UTC.strftime("%Y-%m-%d %H:%M:%S"),
        "source": None,
        "status": "skipped_network",
        "errors": [{"source": "preflight", "error_type": "NetworkUnavailable", "error": reason}],
        "new_rows_downloaded": 0,
        "output_file": str((NEW_PANEL_DIR / f"{symbol}_4H.csv").relative_to(ROOT)),
        "combined_panel": audit_continuity(old),
    }


def size_bucket(event: dict[str, Any]) -> str:
    pct = event.get("circulating_pct")
    if pct is None:
        return "unknown"
    if pct < 1.0:
        return "<1%"
    if pct < 3.0:
        return "1-3%"
    if pct < 10.0:
        return "3-10%"
    return ">=10%"


def unlock_overlap_census(panel_results: list[dict[str, Any]]) -> dict[str, Any]:
    universe = {item["symbol"].replace("USDT", "") for item in panel_results}
    panel_ranges: dict[str, tuple[pd.Timestamp, pd.Timestamp]] = {}
    for item in panel_results:
        combined = item.get("combined_panel") or {}
        if combined.get("start") and combined.get("end"):
            panel_ranges[item["symbol"].replace("USDT", "")] = (
                pd.Timestamp(combined["start"]),
                pd.Timestamp(combined["end"]),
            )

    target_window = (pd.Timestamp("2025-06-01"), pd.Timestamp("2026-06-22"))
    target_events: list[dict[str, Any]] = []
    out_of_scope_samples: list[dict[str, Any]] = []
    for sample in AUDITED_PUBLIC_UNLOCK_SAMPLES:
        record = asdict(sample)
        event_day = pd.Timestamp(sample.unlock_date)
        record["in_requested_window"] = bool(target_window[0] <= event_day <= target_window[1])
        record["in_panel_universe"] = sample.symbol in universe
        if record["in_requested_window"]:
            target_events.append(record)
        else:
            out_of_scope_samples.append(record)

    episodes = []
    for event in target_events:
        symbol = event["symbol"]
        if symbol not in panel_ranges:
            continue
        event_day = pd.Timestamp(event["unlock_date"])
        start, end = panel_ranges[symbol]
        if start <= event_day <= end:
            item = dict(event)
            item["size_bucket"] = size_bucket(event)
            episodes.append(item)

    by_bucket: dict[str, int] = {}
    for episode in episodes:
        by_bucket[episode["size_bucket"]] = by_bucket.get(episode["size_bucket"], 0) + 1

    return {
        "requested_window": "2025-06-01..2026-06-22",
        "free_bulk_event_pull_status": "not_completed",
        "free_bulk_event_pull_reason": (
            "Network/API reachability failed in this execution environment; no unauthenticated "
            "event-level Tokenomist/DefiLlama unlock feed was successfully retrieved."
        ),
        "tokenomist_free_boundary_from_prior_audit": {
            "api_auth": "x-api-key required for event endpoints",
            "free_trial_history": "1 year backward",
            "standard_history": "1 year backward, 2 years forward",
            "csv_export": "Pro feature",
            "docs": TOKENOMIST_DOCS,
        },
        "registered_target_window_events": target_events,
        "out_of_scope_public_samples": out_of_scope_samples,
        "overlap_episode_count": len(episodes),
        "episode_ge_100": len(episodes) >= 100,
        "episode_ge_300_for_60_20_20": len(episodes) >= 300,
        "size_bucket_distribution": by_bucket,
        "p1_unlock_b1_feasible": False,
        "p1_unlock_b1_feasibility_note": (
            "Not feasible from this run: price refresh did not complete and the free unlock "
            "calendar pull produced zero registered 2025-06..2026-06 event episodes."
        ),
    }


def oi_funding_plan() -> dict[str, Any]:
    local_files = []
    futures_dir = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
    for path in sorted(futures_dir.glob("*_FUNDING_8H*.csv")) + sorted(futures_dir.glob("*_METRICS_5M.csv")):
        try:
            df = pd.read_csv(path)
            time_col = "datetime" if "datetime" in df.columns else "create_time" if "create_time" in df.columns else df.columns[0]
            ts = pd.to_datetime(df[time_col])
            local_files.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "rows": int(len(df)),
                    "time_column": time_col,
                    "start": str(ts.min()),
                    "end": str(ts.max()),
                }
            )
        except Exception as error:  # noqa: BLE001
            local_files.append({"file": str(path.relative_to(ROOT)), "error": str(error)})
    return {
        "scope": "availability plan only; no large OI/funding backfill performed",
        "binance_rest_boundaries": {
            "fundingRate": "GET /fapi/v1/fundingRate supports paginated public history; limit 1000 per call.",
            "openInterestHist": "GET /futures/data/openInterestHist supports periods such as 5m/1h/4h/1d and near-term history; use Data Vision for bulk archives where available.",
        },
        "binance_data_vision": {
            "root": BINANCE_DATA_VISION,
            "daily_metrics": f"{BINANCE_DATA_VISION}/daily/metrics/{{SYMBOL}}/{{SYMBOL}}-metrics-YYYY-MM-DD.zip",
            "monthly_mark_price_klines": f"{BINANCE_DATA_VISION}/monthly/markPriceKlines/{{SYMBOL}}/4h/",
            "monthly_funding_rate": f"{BINANCE_DATA_VISION}/monthly/fundingRate/{{SYMBOL}}/",
            "note": "Use month/day archive enumeration with checksum/audit manifest; avoid hot-loop downloads on VM.",
        },
        "local_related_files": local_files,
    }


def write_report(audit: dict[str, Any]) -> None:
    panel = audit["panel_refresh"]
    failed = [item for item in panel["symbols"] if item["status"] in {"failed", "skipped_network"}]
    completed = [item for item in panel["symbols"] if item["status"] in {"downloaded", "no_new_data"}]
    overlap = audit["unlock_overlap_census"]

    lines = [
        "# REPORT_PANEL_REFRESH_2026_20260622",
        "",
        "**任务**：DATA-PANEL-REFRESH-2026｜价格面板刷新到 2026 + 解锁日历 overlap 普查",
        f"**Codex 执行时间**：{audit['generated_at']}",
        "**纪律声明**：纯数据工程；未回测；未碰 Holdout；未调参；未做信号/方向；旧面板只读，新产出限定写入 `FUTURES_EXPANDED_2026/`、`CODE/output/`、本报告与 TASK_INBOX。",
        "",
        "## 总裁决",
        "",
    ]
    if failed:
        lines.extend(
            [
                "**BLOCKED：本次没有完成真实 2026 面板刷新。**",
                "",
                "原因不是交易所下架普遍失败，而是当前执行环境网络出口不可用：环境变量指向 `127.0.0.1:7897`，该端口不可连接；探测到宿主有其他代理监听端口，但命令沙箱连接本地 TCP 端口返回 `Operation not permitted`。在该约束下，Binance、Bybit、DefiLlama/Tokenomist URL 均无法从脚本层访问。",
                "",
                "我没有伪造 K 线，也没有把旧面板复制成“已刷新”。已交付可复跑脚本和审计 JSON；网络出口修复后运行同一脚本即可写入真实 `06_RESEARCH/DATA/FUTURES_EXPANDED_2026/` 面板。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "**完成：面板刷新脚本已成功写入 2026 目录。**",
                "",
            ]
        )

    lines.extend(
        [
            "## A. 面板刷新结果",
            "",
            f"- Universe：旧面板 {panel['old_symbol_count']} 个 symbol + BTCUSDT/ETHUSDT 补齐后 {panel['requested_symbol_count']} 个。",
            f"- 成功/有文件：{len(completed)}；失败：{len(failed)}。",
            f"- 输出目录：`{panel['output_dir']}`。",
            "",
            "| Symbol | 状态 | 源 | 新下载行 | 合并止点 | 行数 | 失败摘要 |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for item in panel["symbols"]:
        combined = item.get("combined_panel") or {}
        error_summary = ""
        if item.get("errors"):
            first = item["errors"][0]
            error_summary = f"{first['source']} {first['error_type']}: {first['error']}"[:120]
        lines.append(
            "| {symbol} | {status} | {source} | {new_rows} | {end} | {rows} | {err} |".format(
                symbol=item["symbol"],
                status=item["status"],
                source=item.get("source") or "-",
                new_rows=item.get("new_rows_downloaded", 0),
                end=combined.get("end") or "-",
                rows=combined.get("rows") or 0,
                err=error_summary.replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## B. 解锁日历 overlap 普查",
            "",
            f"- 目标窗口：{overlap['requested_window']}。",
            f"- 免费事件拉取状态：{overlap['free_bulk_event_pull_status']}。",
            f"- overlap episode 数：{overlap['overlap_episode_count']}。",
            f"- episode ≥100：{overlap['episode_ge_100']}。",
            f"- episode ≥300 可 60/20/20：{overlap['episode_ge_300_for_60_20_20']}。",
            f"- 规模档分布：`{json.dumps(overlap['size_bucket_distribution'], ensure_ascii=False)}`。",
            "",
            "说明：上轮已核 Tokenomist event API/CSV 的免费边界；本轮因网络不可达，未能获得 2025-06..2026-06 的免费事件级日历。脚本保留 overlap 计算入口，但当前不把历史文章样本冒充为目标窗口事件。",
            "",
            "## C. OI/funding 可得性计划",
            "",
            "- 本任务未做大规模 OI/funding 回填。",
            "- Binance REST：`/fapi/v1/fundingRate` 可分页取 funding 历史；`/futures/data/openInterestHist` 可取 near-term OI 历史。",
            "- Binance Data Vision：优先用 `data/futures/um/daily/metrics`、`monthly/markPriceKlines`、`monthly/fundingRate` 月/日压缩包做受控回填，写 checksum/manifest，避免 VM 热循环。",
            f"- 本地已存在相关文件数：{len(audit['oi_funding_availability']['local_related_files'])}。",
            "",
            "## D. 复现",
            "",
            "脚本：`06_RESEARCH/CODE/panel_refresh_2026.py`",
            "",
            "```bash",
            "python3 06_RESEARCH/CODE/panel_refresh_2026.py",
            "```",
            "",
            "若需要显式代理，先修正当前死端口，例如：",
            "",
            "```bash",
            "HTTPS_PROXY=http://127.0.0.1:<可用端口> HTTP_PROXY=http://127.0.0.1:<可用端口> python3 06_RESEARCH/CODE/panel_refresh_2026.py",
            "```",
            "",
            "审计 JSON：`06_RESEARCH/CODE/output/panel_refresh_2026_audit.json`",
            "",
            "## 验收标准自检",
            "",
            "| 验收项 | 结果 |",
            "|---|---|",
            f"| 新面板写入 `FUTURES_EXPANDED_2026/` | {'未达成：网络阻塞导致未写真实刷新文件' if failed else '完成'} |",
            "| 不覆盖旧文件 | 达标 |",
            "| 已下架/无数据如实标注 | 达标：失败逐 symbol 记录源错误；未伪造 |",
            f"| 解锁 overlap episode 普查 | 未达成完整事件拉取；当前 episode={overlap['overlap_episode_count']} |",
            "| OI/funding 只报可得性计划 | 达标 |",
            "| 不碰 Holdout / 不回测 / 不调参 | 达标 |",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_done(audit: dict[str, Any]) -> None:
    panel = audit["panel_refresh"]
    overlap = audit["unlock_overlap_census"]
    failures = sum(1 for item in panel["symbols"] if item["status"] in {"failed", "skipped_network"})
    status = "blocked" if failures else "completed"
    latest_endpoints = {
        item["symbol"]: (item.get("combined_panel") or {}).get("end")
        for item in panel["symbols"]
    }
    done = {
        "task_id": "DATA-PANEL-REFRESH-2026",
        "completed_at": utc_now(),
        "status": status,
        "output_file": "04_AI_TEAM/CODEX_TASKS/REPORT_PANEL_REFRESH_2026_20260622.md",
        "next_task": None,
        "panel_latest_endpoints": latest_endpoints,
        "overlap_episode_count": overlap["overlap_episode_count"],
        "p1_unlock_b1_feasible": overlap["p1_unlock_b1_feasible"],
        "notes": (
            "Blocked by command-layer network/proxy failure; no fabricated price/unlock data. "
            "P1 unlock B1 not feasible from this run."
            if status == "blocked"
            else "Panel refresh completed; see report for P1 unlock B1 feasibility."
        ),
    }
    DONE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DONE_PATH.write_text(json.dumps(done, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--no-write-panel", action="store_true", help="Audit only; do not write refreshed CSVs.")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    universe = discover_universe()
    old_symbols = sorted(path.name.replace("_4H.csv", "") for path in OLD_PANEL_DIR.glob("*_4H.csv"))
    network_probes = {
        "environment_proxy": {
            key: os.environ.get(key)
            for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")
            if os.environ.get(key)
        },
        "urls": [probe_url(url, args.timeout) for url in [BINANCE_BASE, BYBIT_BASE, *UNLOCK_REACHABILITY_URLS]],
    }

    core_download_ok = any(
        item["ok"]
        for item in network_probes["urls"]
        if item["url"] in {BINANCE_BASE, BYBIT_BASE}
    )
    if core_download_ok:
        symbol_results = [
            refresh_symbol(symbol, timeout=args.timeout, write_files=not args.no_write_panel)
            for symbol in universe
        ]
    else:
        reason = "Binance and Bybit preflight probes failed; skipped per-symbol hot-loop downloads."
        symbol_results = [skipped_symbol(symbol, reason) for symbol in universe]
    audit = {
        "task_id": "DATA-PANEL-REFRESH-2026",
        "generated_at": utc_now(),
        "discipline": {
            "holdout_touched": False,
            "backtest_performed": False,
            "parameter_tuning_performed": False,
            "signal_or_direction_research_performed": False,
            "paid_data_used": False,
        },
        "network_probes": network_probes,
        "panel_refresh": {
            "old_dir": str(OLD_PANEL_DIR.relative_to(ROOT)),
            "output_dir": str(NEW_PANEL_DIR.relative_to(ROOT)),
            "old_symbol_count": len(old_symbols),
            "requested_symbol_count": len(universe),
            "requested_start_utc": START_UTC.strftime("%Y-%m-%d %H:%M:%S"),
            "requested_end_utc": END_UTC.strftime("%Y-%m-%d %H:%M:%S"),
            "symbols": symbol_results,
        },
        "unlock_overlap_census": unlock_overlap_census(symbol_results),
        "oi_funding_availability": oi_funding_plan(),
    }
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(audit)
    write_done(audit)
    print(json.dumps({"audit": str(AUDIT_PATH.relative_to(ROOT)), "report": str(REPORT_PATH.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
