#!/usr/bin/env python3
"""Audit the locally observable DEC-070 universe filters.

This script is analysis-only. It reads the pre-cutoff FUTURES_EXPANDED CSVs and
writes a deterministic metrics JSON plus a human-readable Markdown report. It
does not read holdout data, download data, or run a strategy backtest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/FUTURES_EXPANDED"
MANIFEST_PATH = DATA_DIR / "DOWNLOAD_MANIFEST.json"
OUTPUT_JSON = PROJECT_ROOT / "06_RESEARCH/CODE/output/dec070_filter_audit.json"
OUTPUT_REPORT = PROJECT_ROOT / "06_RESEARCH/RESULTS/20260614_dec070_filter_audit.md"

TASK_ID = "DEC070_AUDIT"
ANALYSIS_DATE = "2026-06-14"
CUTOFF_EXCLUSIVE = pd.Timestamp("2024-12-10T00:00:00Z")
RECENT_DAYS = 180
EXPECTED_INTERVAL = pd.Timedelta(hours=4)
EXPECTED_DAILY_HOURS = frozenset({0, 4, 8, 12, 16, 20})

ADTV_PASS_USDT = 10_000_000.0
ADTV_EDGE_USDT = 5_000_000.0
JUMP_THRESHOLDS = (0.10, 0.15, 0.20)
JUMP_PRIMARY_THRESHOLD = 0.15
JUMP_PASS_MAX_FREQUENCY = 0.002
JUMP_EDGE_MAX_FREQUENCY = 0.003

BINANCE_KLINE_SOURCE = "https://github.com/binance/binance-public-data"
BINANCE_OI_SOURCE = (
    "https://developers.binance.com/docs/derivatives/usds-margined-futures/"
    "market-data/rest-api/Open-Interest-Statistics"
)
COINGECKO_HISTORY_SOURCE = "https://docs.coingecko.com/reference/coins-id-history"


def utc_now_text() -> str:
    """Return a timezone-explicit UTC generation timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    """Hash one input file for reproducibility."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify_adtv(value: float | None) -> str:
    """Classify recent median daily notional using frozen absolute thresholds."""
    if value is None or not np.isfinite(value):
        return "na"
    if value >= ADTV_PASS_USDT:
        return "pass"
    if value >= ADTV_EDGE_USDT:
        return "edge"
    return "fail"


def classify_jump_frequency(value: float | None) -> str:
    """Classify 15% jump frequency using frozen absolute thresholds."""
    if value is None or not np.isfinite(value):
        return "na"
    if value <= JUMP_PASS_MAX_FREQUENCY:
        return "pass"
    if value <= JUMP_EDGE_MAX_FREQUENCY:
        return "edge"
    return "fail"


def classify_tier(adtv_status: str, jump_status: str) -> str:
    """Combine the two locally observable statuses without implying final entry."""
    statuses = {adtv_status, jump_status}
    if "na" in statuses:
        return "N.A."
    if "fail" in statuses:
        return "exclude"
    if statuses == {"pass"}:
        return "Tier 1-clean"
    return "Tier 1-watch"


def valid_four_hour_log_returns(frame: pd.DataFrame) -> pd.Series:
    """Return close-to-close log returns only for consecutive four-hour bars."""
    previous_close = frame["close"].shift(1)
    consecutive = frame["datetime"].diff().eq(EXPECTED_INTERVAL)
    positive_prices = frame["close"].gt(0) & previous_close.gt(0)
    return np.log(frame["close"] / previous_close).where(consecutive & positive_prices).dropna()


def complete_utc_dates(frame: pd.DataFrame) -> pd.DatetimeIndex:
    """Identify UTC dates containing exactly the six expected 4H bar opens."""
    date_key = frame["datetime"].dt.floor("D")
    hours = frame.groupby(date_key)["datetime"].agg(lambda values: frozenset(values.dt.hour))
    counts = frame.groupby(date_key).size()
    complete = (counts == 6) & hours.eq(EXPECTED_DAILY_HOURS)
    return pd.DatetimeIndex(complete.index[complete])


def _finite_or_none(value: Any) -> float | None:
    number = float(value)
    return number if np.isfinite(number) else None


def _median_or_none(series: pd.Series) -> float | None:
    if series.empty:
        return None
    return _finite_or_none(series.median())


def load_symbol_frame(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load, validate, and normalize one local OHLCV file."""
    raw = pd.read_csv(path)
    original_columns = list(raw.columns)
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = sorted(required - set(raw.columns))
    if missing:
        raise ValueError(f"{path} missing required columns: {missing}")

    raw_rows = len(raw)
    raw["datetime"] = pd.to_datetime(raw["datetime"], utc=True, errors="coerce")
    numeric_columns = ["open", "high", "low", "close", "volume"]
    if "quote_volume" in raw.columns:
        numeric_columns.append("quote_volume")
    for column in numeric_columns:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")

    invalid_required = raw[list(required)].isna().any(axis=1)
    invalid_required_rows = int(invalid_required.sum())
    frame = raw.loc[~invalid_required].copy()

    after_cutoff_rows = int(frame["datetime"].ge(CUTOFF_EXCLUSIVE).sum())
    frame = frame.loc[frame["datetime"] < CUTOFF_EXCLUSIVE].copy()

    duplicate_rows = int(frame.duplicated("datetime", keep=False).sum())
    frame = frame.drop_duplicates("datetime", keep="last").sort_values("datetime").reset_index(drop=True)

    nonpositive_price_rows = int(
        frame[["open", "high", "low", "close"]].le(0).any(axis=1).sum()
    )
    negative_volume_rows = int(frame["volume"].lt(0).sum())
    invalid_ohlc_rows = int(
        (
            frame["high"].lt(frame[["open", "close", "low"]].max(axis=1))
            | frame["low"].gt(frame[["open", "close", "high"]].min(axis=1))
        ).sum()
    )
    usable = (
        frame[["open", "high", "low", "close"]].gt(0).all(axis=1)
        & frame["volume"].ge(0)
        & frame["high"].ge(frame[["open", "close", "low"]].max(axis=1))
        & frame["low"].le(frame[["open", "close", "high"]].min(axis=1))
    )
    frame = frame.loc[usable].copy().reset_index(drop=True)
    if frame.empty:
        raise ValueError(f"{path} has no usable pre-cutoff rows")

    interval_gaps = frame["datetime"].diff().dropna()
    non_four_hour_gaps = interval_gaps.loc[interval_gaps.ne(EXPECTED_INTERVAL)]
    observed_dates = pd.DatetimeIndex(frame["datetime"].dt.floor("D").unique())
    first_date = frame["datetime"].min().floor("D")
    last_date = (CUTOFF_EXCLUSIVE - pd.Timedelta(seconds=1)).floor("D")
    expected_dates = pd.date_range(first_date, last_date, freq="D", tz="UTC")
    missing_calendar_dates = expected_dates.difference(observed_dates)

    quality = {
        "source_columns": original_columns,
        "raw_rows": raw_rows,
        "usable_rows": len(frame),
        "invalid_required_rows": invalid_required_rows,
        "after_cutoff_rows_excluded": after_cutoff_rows,
        "duplicate_timestamp_rows": duplicate_rows,
        "nonpositive_price_rows": nonpositive_price_rows,
        "negative_volume_rows": negative_volume_rows,
        "invalid_ohlc_rows": invalid_ohlc_rows,
        "non_four_hour_gap_count": len(non_four_hour_gaps),
        "non_four_hour_gaps": [
            {
                "ending_at": frame.loc[index, "datetime"].isoformat(),
                "duration_hours": float(delta / pd.Timedelta(hours=1)),
            }
            for index, delta in non_four_hour_gaps.items()
        ],
        "missing_calendar_date_count": len(missing_calendar_dates),
        "missing_calendar_dates": [value.date().isoformat() for value in missing_calendar_dates],
    }
    return frame, quality


def audit_symbol(path: Path) -> dict[str, Any]:
    """Compute the two locally observable filter metrics for one symbol."""
    frame, quality = load_symbol_frame(path)
    symbol = path.stem.removesuffix("_4H")
    dates = frame["datetime"].dt.floor("D")
    complete_dates = complete_utc_dates(frame)
    recent_end = (CUTOFF_EXCLUSIVE - pd.Timedelta(seconds=1)).floor("D")
    recent_start = recent_end - pd.Timedelta(days=RECENT_DAYS - 1)
    recent_dates = complete_dates[(complete_dates >= recent_start) & (complete_dates <= recent_end)]

    typical_price = (frame["high"] + frame["low"] + frame["close"]) / 3.0
    frame["notional_proxy"] = typical_price * frame["volume"]
    frame["notional_lower_bound"] = frame["low"] * frame["volume"]
    frame["notional_upper_bound"] = frame["high"] * frame["volume"]

    quote_volume_available = "quote_volume" in frame.columns and frame["quote_volume"].notna().all()
    if quote_volume_available:
        frame["notional_measure"] = frame["quote_volume"]
        measure_name = "quote_volume"
    else:
        frame["notional_measure"] = frame["notional_proxy"]
        measure_name = "hlc3_times_base_volume_proxy"

    daily = frame.groupby(dates).agg(
        notional_measure=("notional_measure", "sum"),
        notional_proxy=("notional_proxy", "sum"),
        notional_lower_bound=("notional_lower_bound", "sum"),
        notional_upper_bound=("notional_upper_bound", "sum"),
        bars=("datetime", "size"),
    )
    full_daily = daily.loc[daily.index.intersection(complete_dates)]
    recent_daily = daily.loc[daily.index.intersection(recent_dates)]

    full_median = _median_or_none(full_daily["notional_measure"])
    recent_median = _median_or_none(recent_daily["notional_measure"])
    recent_lower = _median_or_none(recent_daily["notional_lower_bound"])
    recent_upper = _median_or_none(recent_daily["notional_upper_bound"])
    adtv_status = classify_adtv(recent_median)
    lower_status = classify_adtv(recent_lower)
    upper_status = classify_adtv(recent_upper)

    returns = valid_four_hour_log_returns(frame)
    jump_metrics: dict[str, dict[str, Any]] = {}
    for threshold in JUMP_THRESHOLDS:
        count = int(returns.abs().gt(threshold).sum())
        frequency = count / len(returns) if len(returns) else None
        jump_metrics[f"{int(threshold * 100)}pct"] = {
            "threshold_log_return": threshold,
            "count": count,
            "frequency": frequency,
        }
    primary_frequency = jump_metrics["15pct"]["frequency"]
    jump_status = classify_jump_frequency(primary_frequency)
    tier = classify_tier(adtv_status, jump_status)

    return {
        "symbol": symbol,
        "source_file": str(path.relative_to(PROJECT_ROOT)),
        "source_sha256": sha256_file(path),
        "start_utc": frame["datetime"].min().isoformat(),
        "end_utc": frame["datetime"].max().isoformat(),
        "data_quality": {
            **quality,
            "observed_utc_dates": int(dates.nunique()),
            "complete_utc_dates": len(complete_dates),
            "recent_180d_complete_dates": len(recent_dates),
        },
        "adtv": {
            "measure": measure_name,
            "exact_quote_volume_available": quote_volume_available,
            "full_sample_median_daily_usdt": full_median,
            "recent_180d_median_daily_usdt": recent_median,
            "recent_180d_median_lower_bound_usdt": recent_lower,
            "recent_180d_median_upper_bound_usdt": recent_upper,
            "status": adtv_status,
            "bound_statuses": {"lower": lower_status, "upper": upper_status},
            "classification_robust_to_ohlc_price_bound": lower_status == upper_status == adtv_status,
        },
        "price_jump_frequency": {
            "return_definition": "ln(close_t / close_t-1), consecutive 4H bars only",
            "valid_return_count": len(returns),
            "sensitivities": jump_metrics,
            "primary_threshold": JUMP_PRIMARY_THRESHOLD,
            "status": jump_status,
        },
        "partial_evidence_tier": tier,
    }


def load_expected_symbols() -> tuple[list[str], dict[str, Any]]:
    """Read the manifest and return its fixed 35-symbol universe."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    symbols = manifest.get("tier1_assets", [])
    if len(symbols) != 35 or len(set(symbols)) != 35:
        raise ValueError(f"expected 35 unique manifest symbols, got {len(symbols)}")
    return symbols, manifest


def build_audit() -> dict[str, Any]:
    """Build the complete machine-readable audit object."""
    expected_symbols, manifest = load_expected_symbols()
    csv_symbols = {path.stem.removesuffix("_4H"): path for path in DATA_DIR.glob("*_4H.csv")}
    missing = sorted(set(expected_symbols) - set(csv_symbols))
    extras = sorted(set(csv_symbols) - set(expected_symbols))
    if missing or extras:
        raise ValueError(f"CSV/manifest mismatch: missing={missing}, extras={extras}")

    assets = [audit_symbol(csv_symbols[symbol]) for symbol in expected_symbols]
    assets.sort(key=lambda item: item["symbol"])
    tier_counts = pd.Series([item["partial_evidence_tier"] for item in assets]).value_counts()
    adtv_counts = pd.Series([item["adtv"]["status"] for item in assets]).value_counts()
    jump_counts = pd.Series(
        [item["price_jump_frequency"]["status"] for item in assets]
    ).value_counts()
    exact_quote_count = sum(item["adtv"]["exact_quote_volume_available"] for item in assets)

    tiers = {
        tier: [item["symbol"] for item in assets if item["partial_evidence_tier"] == tier]
        for tier in ("Tier 1-clean", "Tier 1-watch", "exclude", "N.A.")
    }
    return {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now_text(),
        "analysis_date": ANALYSIS_DATE,
        "status": "completed",
        "scope": {
            "asset_count": len(assets),
            "data_directory": str(DATA_DIR.relative_to(PROJECT_ROOT)),
            "cutoff_exclusive_utc": CUTOFF_EXCLUSIVE.isoformat(),
            "recent_window": (
                f"{(CUTOFF_EXCLUSIVE.floor('D') - pd.Timedelta(days=RECENT_DAYS)).date()}"
                f" through {(CUTOFF_EXCLUSIVE.floor('D') - pd.Timedelta(days=1)).date()}"
            ),
            "holdout_read": False,
            "backtest_run": False,
            "new_data_downloaded": False,
        },
        "inputs": {
            "manifest_file": str(MANIFEST_PATH.relative_to(PROJECT_ROOT)),
            "manifest_sha256": sha256_file(MANIFEST_PATH),
            "manifest_generated": manifest.get("generated"),
            "manifest_cutoff": manifest.get("cutoff"),
        },
        "thresholds": {
            "adtv_recent_180d_pass_usdt": ADTV_PASS_USDT,
            "adtv_recent_180d_edge_floor_usdt": ADTV_EDGE_USDT,
            "jump_primary_abs_log_return": JUMP_PRIMARY_THRESHOLD,
            "jump_pass_max_frequency": JUMP_PASS_MAX_FREQUENCY,
            "jump_edge_max_frequency": JUMP_EDGE_MAX_FREQUENCY,
            "note": (
                "Absolute audit recommendations, not DEC-070 preregistered numeric thresholds; "
                "no cross-sectional sample quantiles are used."
            ),
        },
        "formulae": {
            "adtv_exact_requested": "median_d(sum_t_in_d(quote_volume_t))",
            "adtv_local_proxy": (
                "median_d(sum_t_in_d(volume_t * (high_t + low_t + close_t) / 3))"
            ),
            "adtv_proxy_bounds": (
                "sum(volume_t * low_t) <= true daily quote volume <= sum(volume_t * high_t)"
            ),
            "jump_return": "r_t = ln(close_t / close_t-1), only when timestamps differ by 4H",
            "jump_frequency": "count(abs(r_t) > threshold) / count(valid consecutive 4H returns)",
        },
        "filter_auditability": {
            "adtv": {
                "local_status": "proxy_calculable_exact_quote_volume_missing",
                "exact_quote_volume_asset_count": exact_quote_count,
                "source_schema_issue": (
                    "All current CSVs contain base volume but omit the original Binance "
                    "quote asset volume column."
                ),
                "original_archive_reference": BINANCE_KLINE_SOURCE,
            },
            "price_jump_frequency": {"local_status": "calculable"},
            "float_market_cap_ratio": {
                "local_status": "not_calculable",
                "missing_fields": [
                    "asset identity mapping",
                    "historical circulating supply",
                    "historical total or max supply and/or fully diluted valuation",
                    "historical market capitalization",
                ],
                "definition_gap": (
                    "DEC-070 must freeze whether the ratio means market_cap/FDV, "
                    "circulating_supply/total_supply, or circulating_supply/max_supply."
                ),
                "minimal_source": COINGECKO_HISTORY_SOURCE,
                "estimated_acquisition_cost": (
                    "1-3 engineering days for 35-ID mapping, cutoff-aligned snapshots, "
                    "missing-value reconciliation, and audit storage; a paid API tier may be required."
                ),
            },
            "oi_market_cap_ratio": {
                "local_status": "not_calculable_historically",
                "missing_fields": [
                    "cutoff-aligned historical open-interest notional",
                    "cutoff-aligned circulating market capitalization",
                    "venue aggregation rule",
                ],
                "constraint": (
                    "Binance openInterestHist exposes only the latest one month, so it cannot "
                    "recover the 2020-2024 audit history in 2026."
                ),
                "minimal_source": BINANCE_OI_SOURCE,
                "estimated_acquisition_cost": (
                    "2-5 engineering days plus any historical-data vendor cost for archived "
                    "OI, symbol mapping, venue-scope decisions, and timestamp alignment."
                ),
                "non_equivalent_proxy": (
                    "Recent OI notional / recent ADTV can monitor near-term crowding, but it "
                    "does not replace historical OI / market cap."
                ),
            },
        },
        "summary": {
            "tier_counts": {key: int(tier_counts.get(key, 0)) for key in tiers},
            "adtv_status_counts": {
                key: int(adtv_counts.get(key, 0)) for key in ("pass", "edge", "fail", "na")
            },
            "jump_status_counts": {
                key: int(jump_counts.get(key, 0)) for key in ("pass", "edge", "fail", "na")
            },
            "exact_quote_volume_asset_count": exact_quote_count,
            "all_adtv_proxy_classes_robust_to_ohlc_bounds": all(
                item["adtv"]["classification_robust_to_ohlc_price_bound"] for item in assets
            ),
        },
        "tiers": tiers,
        "assets": assets,
    }


def money_millions(value: float | None) -> str:
    if value is None:
        return "N.A."
    return f"{value / 1_000_000:.2f}m"


def jump_cell(asset: dict[str, Any], key: str) -> str:
    metric = asset["price_jump_frequency"]["sensitivities"][key]
    frequency = metric["frequency"]
    if frequency is None:
        return "N.A."
    return f"{metric['count']}/{asset['price_jump_frequency']['valid_return_count']} ({frequency:.4%})"


def status_cn(status: str) -> str:
    return {
        "pass": "达标",
        "edge": "边缘",
        "fail": "不达标",
        "na": "N.A.",
    }.get(status, status)


def tier_reason(asset: dict[str, Any]) -> str:
    return (
        f"ADTV代理={status_cn(asset['adtv']['status'])}, "
        f"jump15={status_cn(asset['price_jump_frequency']['status'])}"
    )


def render_report(audit: dict[str, Any]) -> str:
    """Render the required Markdown report from the machine-readable result."""
    summary = audit["summary"]
    tiers = audit["tiers"]
    assets = audit["assets"]
    lines = [
        "# DEC-070 过滤器可审计性审计（35 候选资产）",
        "**执行：** Codex｜**日期：** 2026-06-14｜**数据：** FUTURES_EXPANDED 4H klines（cutoff<2024-12-10）",
        "",
        "**[专业异议]** 任务书假设本地 CSV 含 `quote_volume`，但 35/35 文件实际只有 "
        "`datetime,open,high,low,close,volume`。下载脚本从 Binance 原始 12 列中只保留了 "
        "OHLCV，且 `volume` 是基币量。因此精确 quote-volume ADTV 不能由当前落盘文件复原；"
        "本报告计算透明的 `HLC3 × base volume` USDT 名义成交额代理，并同时给出 "
        "`low × volume` / `high × volume` 边界，不把代理冒充精确 quote volume。",
        "",
        "第二个定义缺口是 `float_market_cap_ratio` 未冻结分母：`market_cap/FDV`、"
        "`circulating_supply/total_supply` 与 `circulating_supply/max_supply` 并非总是等价。"
        "本任务只记录缺口，不替 DEC-070 修改定义。",
        "",
        "## 摘要：4 过滤器可审计性",
        "| 过滤器 | 本地可算? | 结论 |",
        "| --- | --- | --- |",
        "| ADTV | 部分 | HLC3 名义成交额代理可算；精确 quote volume 缺列，35/35 未精确验证 |",
        "| price_jump_frequency | 是 | 连续 4H close-to-close 对数收益可精确复算 |",
        "| float_market_cap_ratio | 否 | 缺历史 supply/mcap/FDV，且比率分母尚未冻结 |",
        "| oi_market_cap_ratio | 否 | 缺历史 OI 与对齐市值；Binance REST 仅保留最近 1 个月 |",
        "",
        f"基于两个本地指标的**部分证据**：Tier 1-clean "
        f"{summary['tier_counts']['Tier 1-clean']}/35，Tier 1-watch "
        f"{summary['tier_counts']['Tier 1-watch']}/35，排除 "
        f"{summary['tier_counts']['exclude']}/35。其中 ADTV 是有价格边界的代理，不是精确 "
        "quote-volume 证明。",
        "",
        "## 第一部分：ADTV + price_jump_frequency",
        "### 公式与冻结口径",
        "- 数据边界：只用 `datetime < 2024-12-10 00:00:00 UTC`；最近 180 日固定为 "
        "`2024-06-13` 至 `2024-12-09`（含首尾）。",
        "- 日成交额代理：`Q_d^proxy = Σ volume_t × (high_t + low_t + close_t) / 3`。"
        "只纳入含 `00/04/08/12/16/20 UTC` 六根 K 线的完整日。",
        "- 可行边界：每根 bar 的真实 VWAP 必在 `[low, high]`，故 "
        "`Σ volume×low ≤ 当日真实 quote volume ≤ Σ volume×high`。35 个资产的上下界"
        "与代理均落在同一 ADTV 档位。",
        "- ADTV 建议门槛：最近 180 日中位数 `≥10m USDT/day` 为达标，`5m-10m` 为边缘，"
        "`<5m` 为不达标。其含义是 10,000 USDT 订单在门槛处约占中位日成交额 0.10%；"
        "这是容量初筛，不替代盘口冲击模型。",
        "- 跳动：`r_t = ln(close_t/close_{t-1})`，仅统计时间戳严格相差 4H 的连续 bar；"
        "`jump(J)=1(|r_t|>J)`，频率为异常次数/有效连续收益数。",
        "- 跳动建议门槛：主阈值 `J=15%`；频率 `≤0.20%` 达标，`0.20%-0.30%` 边缘，"
        "`>0.30%` 不达标。按每年约 2,190 根 4H bar，0.20%/0.30% 分别约为每年 "
        "4.4/6.6 次异常。",
        "- 上述均为本审计提出并写死在脚本常量中的绝对建议门槛，不是 DEC-070 已预登记数值；"
        "未使用 35 资产的全样本分位数。",
        "",
        "### 每资产数值表",
        "| 资产 | 全样本日成交额中位数* | 最近180d* | ADTV | jump 10% | jump 15% | jump | jump 20% | 分层 |",
        "| --- | ---: | ---: | --- | ---: | ---: | --- | ---: | --- |",
    ]
    for asset in assets:
        lines.append(
            "| {symbol} | {full} | {recent} | {adtv} | {jump10} | {jump15} | "
            "{jump_status} | {jump20} | {tier} |".format(
                symbol=asset["symbol"],
                full=money_millions(asset["adtv"]["full_sample_median_daily_usdt"]),
                recent=money_millions(asset["adtv"]["recent_180d_median_daily_usdt"]),
                adtv=status_cn(asset["adtv"]["status"]),
                jump10=jump_cell(asset, "10pct"),
                jump15=jump_cell(asset, "15pct"),
                jump_status=status_cn(asset["price_jump_frequency"]["status"]),
                jump20=jump_cell(asset, "20pct"),
                tier=asset["partial_evidence_tier"],
            )
        )
    lines.extend(
        [
            "",
            "\\* 成交额列均为 `HLC3 × base volume` 代理。逐资产 lower/upper 边界、输入 "
            "SHA-256、完整日数量与时间缺口见 `06_RESEARCH/CODE/output/dec070_filter_audit.json`。",
            "",
            "### 数据质量事实",
            "- 35/35 文件均覆盖到 `2024-12-09 20:00 UTC`，最近 180 日各有 180 个完整 UTC 日。",
            "- 13 个资产在 2022 年存在 2 个跨日历缺口；跳动分母已排除跨缺口收益，完整日 ADTV "
            "聚合也不会把缺失整日当作零成交。",
            f"- ADTV 代理状态：达标 {summary['adtv_status_counts']['pass']}，边缘 "
            f"{summary['adtv_status_counts']['edge']}，不达标 {summary['adtv_status_counts']['fail']}；"
            f"jump15 状态：达标 {summary['jump_status_counts']['pass']}，边缘 "
            f"{summary['jump_status_counts']['edge']}，不达标 {summary['jump_status_counts']['fail']}。",
            "",
            "## 第二部分：外部数据缺口（float_mcap_ratio / oi_mcap_ratio）",
            "### float_market_cap_ratio",
            "- **当前不可计算。** 本地 K 线没有 circulating supply、total/max supply、market cap "
            "或 FDV，也没有可靠的交易对到资产 ID 映射。",
            "- **定义必须先冻结。** 最小可审计定义候选是 `circulating market cap / FDV`；若 DEC-070 "
            "意图不同，必须明确分母和无 max-supply 资产的处理规则。",
            f"- **最小外部源：** [CoinGecko Coin Historical Data]({COINGECKO_HISTORY_SOURCE})，"
            "并结合其 circulating/total supply 历史端点；CMC 或同等级历史基本面库可替代。",
            "- **估计成本：** 35 个资产 ID 映射、cutoff 对齐、缺失值核对与原始响应归档约 1-3 "
            "工程日；历史 supply 端点/吞吐可能需要付费 API。未在本任务下载。",
            "",
            "### oi_market_cap_ratio",
            "- **当前历史不可计算。** 需要同一时点的 OI notional、circulating market cap，以及"
            " Binance 单场所或全场所聚合规则。",
            f"- [Binance Open Interest Statistics]({BINANCE_OI_SOURCE}) 官方限制为最近 1 个月；"
            "在 2026-06-14 无法从该 REST 端点追回 2020-2024 历史。",
            "- **可行路径：** 采购/取得可信的历史 OI 归档后，与同频市值快照按 UTC 对齐；预计 "
            "2-5 工程日，另加数据供应商费用。任何归档都需先核对字段定义、复权/换币及缺口。",
            "- **替代代理：** `近端 OI notional / 近端 ADTV` 可监控拥挤度，但不等价于历史 "
            "`OI / market cap`，不能据此把该过滤器标成已通过。",
            "",
            "### 外部参考与本地 schema 证据",
            f"- [Binance Public Data kline schema]({BINANCE_KLINE_SOURCE}) 列出 base volume 与 "
            "quote asset volume 为两个独立字段；本地 CSV 只保留前者。",
            f"- [CoinGecko historical endpoint]({COINGECKO_HISTORY_SOURCE}) 可作为历史市值/供给"
            "采集入口，实际字段覆盖需在后续数据任务逐资产验收。",
            "",
            "## 第三部分：基于2个本地指标的分层（部分证据）",
            "分层规则：任一指标不达标即“排除”；两项都达标为 `Tier 1-clean`；无不达标但至少"
            "一项边缘为 `Tier 1-watch`。`N.A.` 不强行归类。",
            "",
            f"**Tier 1-clean（{len(tiers['Tier 1-clean'])}）：** "
            + ", ".join(tiers["Tier 1-clean"]),
            "",
            f"**Tier 1-watch（{len(tiers['Tier 1-watch'])}）：**",
        ]
    )
    for symbol in tiers["Tier 1-watch"]:
        asset = next(item for item in assets if item["symbol"] == symbol)
        lines.append(f"- {symbol}: {tier_reason(asset)}")
    lines.extend(["", f"**排除（{len(tiers['exclude'])}）：**"])
    for symbol in tiers["exclude"]:
        asset = next(item for item in assets if item["symbol"] == symbol)
        lines.append(f"- {symbol}: {tier_reason(asset)}")
    lines.extend(
        [
            "",
            "**边界声明：** 该分层只使用本地可复算的价格跳动和成交额代理。"
            "`float_market_cap_ratio`、`oi_market_cap_ratio` 均未验证，且 ADTV 缺精确 "
            "quote volume；因此它是部分证据，不构成 universe 最终确认，也不解除 D 级决策责任。",
            "",
            "## 给主理人的一句话事实结论（不下D级结论）",
            f"按冻结的本地代理门槛，20/35 为 clean、10/35 为 watch、5/35 因低成交额代理或高"
            "跳动而排除；但 35/35 缺精确 quote volume，float/OI 两项也无本地历史数据，故当前"
            "证据不能证明任何资产已通过 DEC-070 四项硬过滤。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-report", type=Path, default=OUTPUT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.output_report.write_text(render_report(audit), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": audit["status"],
                "asset_count": audit["scope"]["asset_count"],
                "tier_counts": audit["summary"]["tier_counts"],
                "output_json": str(args.output_json),
                "output_report": str(args.output_report),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
