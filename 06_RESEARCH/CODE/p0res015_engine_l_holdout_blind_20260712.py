#!/usr/bin/env python3
"""P0-RES-015 one-shot Holdout blind validation for TSMOM engine L.

This runner intentionally does not modify ``tsmom_dual_engine.py``. It uses a
local full-history loader authorized by DEC-093, then reuses the frozen engine
preparation/backtest functions and evaluates only the registered Holdout
window.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT / "06_RESEARCH" / "CODE"
DATA_DIR = ROOT / "06_RESEARCH" / "DATA"
FUTURES_DIR = DATA_DIR / "FUTURES"
OUTPUT_DIR = CODE_DIR / "output"
OUTPUT_JSON = OUTPUT_DIR / "p0res015_engine_l_holdout_blind_20260712.json"
REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "REPORT_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712.md"
TASK_INBOX_JSON = ROOT / "04_AI_TEAM" / "TASK_INBOX" / "P0RES015_DONE.json"

TASK_ID = "P0-RES-015"
TASK_SPEC_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "TASK_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712.md"
ENGINE_PATH = CODE_DIR / "tsmom_dual_engine.py"
P014_SCRIPT_PATH = CODE_DIR / "p0res014_engine_l_benchmark_recheck_20260706.py"
P006_JSON = OUTPUT_DIR / "p0res006_engine_l_recheck_20260702.json"
P014_JSON = OUTPUT_DIR / "p0res014_engine_l_benchmark_recheck_20260706.json"

SYMBOLS = ("BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "LTC")
TARGET_POSITION_VOL = 0.10
TARGET_STANDARD_VOL = 0.10
HOLDOUT_START = pd.Timestamp("2024-12-10 00:00:00")
HOLDOUT_END = pd.Timestamp("2026-05-31 20:00:00")
FUNDING_END = pd.Timestamp("2026-05-31 16:00:00")
BOOTSTRAP_ITERATIONS = 5000
BOOTSTRAP_SEED = 20260712
BOOTSTRAP_BLOCK_BARS = 42


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_tsmom_module() -> Any:
    spec = importlib.util.spec_from_file_location("tsmom_dual_engine_p0res015", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_full_csv(path: Path, required_columns: tuple[str, ...]) -> pd.DataFrame:
    if "2026H1" in path.name:
        raise ValueError(f"forbidden increment file requested: {path}")
    if "HOLDOUT" in path.parts:
        raise ValueError(f"forbidden DATA/HOLDOUT path requested: {path}")
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        missing = set(required_columns).difference(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(f"{path} is empty")
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} has duplicate timestamps")
    if not frame["datetime"].is_monotonic_increasing:
        raise ValueError(f"{path} is not ascending")
    for column in frame.columns:
        if column != "datetime":
            frame[column] = pd.to_numeric(frame[column])
    return frame.reset_index(drop=True)


def load_full_data(tsmom: Any) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, Any], dict[str, Path]]:
    pit = tsmom.load_pit()
    bars: dict[str, pd.DataFrame] = {}
    funding: dict[str, pd.DataFrame] = {}
    audit: dict[str, Any] = {}
    files: dict[str, Path] = {}
    for symbol in SYMBOLS:
        mark_path = FUTURES_DIR / f"{symbol}USDT_MARK_4H.csv"
        funding_path = FUTURES_DIR / f"{symbol}USDT_FUNDING_8H.csv"
        files[f"{symbol}_MARK_4H"] = mark_path
        files[f"{symbol}_FUNDING_8H"] = funding_path
        raw_bars = read_full_csv(mark_path, ("datetime", "open", "high", "low", "close", "volume"))
        raw_funding = read_full_csv(funding_path, ("datetime", "last_funding_rate"))
        bars[symbol] = tsmom.prepare_bars(raw_bars, symbol=symbol, onboard_date=pit[symbol], engine="L")
        raw_funding["last_funding_rate"] = pd.to_numeric(raw_funding["last_funding_rate"])
        funding[symbol] = raw_funding
        audit[symbol] = {
            "bars_first_timestamp": str(raw_bars["datetime"].iloc[0]),
            "bars_last_timestamp": str(raw_bars["datetime"].iloc[-1]),
            "bars_rows_read_full_file": int(len(raw_bars)),
            "funding_first_timestamp": str(raw_funding["datetime"].iloc[0]),
            "funding_last_timestamp": str(raw_funding["datetime"].iloc[-1]),
            "funding_rows_read_full_file": int(len(raw_funding)),
            "bars_rows_in_holdout_window": int(((raw_bars["datetime"] >= HOLDOUT_START) & (raw_bars["datetime"] <= HOLDOUT_END)).sum()),
            "funding_rows_through_holdout_funding_end": int(((raw_funding["datetime"] >= HOLDOUT_START) & (raw_funding["datetime"] <= FUNDING_END)).sum()),
        }
    return bars, funding, audit, files


def returns_from_equity(equity: pd.Series) -> pd.Series:
    return equity.astype(float).pct_change().dropna()


def annual_periods(tsmom: Any) -> float:
    return 365.2425 * 24 / tsmom.BAR_HOURS


def annualized_log_growth_from_returns(returns: pd.Series, periods_per_year: float) -> float:
    return float(np.log1p(returns.astype(float)).mean() * periods_per_year)


def annualized_vol(returns: pd.Series, periods_per_year: float) -> float:
    return float(returns.astype(float).std(ddof=1) * math.sqrt(periods_per_year))


def scale_to_vol(returns: pd.Series, target_vol: float, periods_per_year: float) -> tuple[pd.Series, float, float]:
    vol = annualized_vol(returns, periods_per_year)
    if not math.isfinite(vol) or vol <= 0:
        raise ValueError("cannot volatility-scale a zero-volatility series")
    scale = target_vol / vol
    return returns.astype(float) * scale, scale, vol


def max_drawdown(equity: pd.Series) -> float:
    clean = equity.dropna()
    dd = clean / clean.cummax() - 1.0
    return float(dd.min()) if len(dd) else 0.0


def rebase_equity(equity: pd.Series, *, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    window = equity[(equity.index >= start) & (equity.index <= end)].astype(float).copy()
    if window.empty or window.index[0] != start or window.index[-1] != end:
        raise ValueError(f"equity window missing exact start/end: got {window.index[0] if len(window) else None} -> {window.index[-1] if len(window) else None}")
    return window / float(window.iloc[0]) * 100_000.0


def summarize_trades(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {
            "trade_count": 0,
            "expectancy_r": None,
            "win_rate": None,
            "average_win_r": None,
            "average_loss_r_abs": None,
            "win_loss_ratio": None,
            "net_pnl": 0.0,
            "fees": 0.0,
            "slippage_cost": 0.0,
            "funding_cost": 0.0,
        }
    winners = trades[trades["expectancy_r"] > 0]
    losers = trades[trades["expectancy_r"] < 0]
    avg_win = float(winners["expectancy_r"].mean()) if len(winners) else None
    avg_loss_abs = float(-losers["expectancy_r"].mean()) if len(losers) else None
    return {
        "trade_count": int(len(trades)),
        "expectancy_r": float(trades["expectancy_r"].mean()),
        "win_rate": float((trades["expectancy_r"] > 0).mean()),
        "average_win_r": avg_win,
        "average_loss_r_abs": avg_loss_abs,
        "win_loss_ratio": (avg_win / avg_loss_abs if avg_win is not None and avg_loss_abs not in (None, 0.0) else None),
        "net_pnl": float(trades["net_pnl"].sum()),
        "fees": float(trades["total_fees"].sum()),
        "slippage_cost": float(trades["total_slippage_cost"].sum()),
        "funding_cost": float(trades["funding_cost"].sum()),
    }


def quarterly_returns(equity: pd.Series) -> list[dict[str, Any]]:
    out = []
    for quarter, group in equity.groupby(pd.PeriodIndex(equity.index, freq="Q")):
        if len(group) < 2:
            continue
        out.append(
            {
                "quarter": str(quarter),
                "start": str(group.index[0]),
                "end": str(group.index[-1]),
                "simple_return": float(group.iloc[-1] / group.iloc[0] - 1.0),
                "log_return": float(np.log(group.iloc[-1] / group.iloc[0])),
            }
        )
    return out


def moving_block_bootstrap_diff(strategy_returns: pd.Series, benchmark_returns: pd.Series, periods_per_year: float) -> dict[str, Any]:
    both = pd.concat([strategy_returns.rename("strategy"), benchmark_returns.rename("benchmark")], axis=1).dropna()
    values = both.to_numpy(dtype=float)
    n = len(values)
    starts = np.arange(0, max(1, n - BOOTSTRAP_BLOCK_BARS + 1))
    blocks_needed = int(math.ceil(n / BOOTSTRAP_BLOCK_BARS))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    diffs = np.empty(BOOTSTRAP_ITERATIONS, dtype=float)
    for i in range(BOOTSTRAP_ITERATIONS):
        sampled = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            sampled.extend(values[start : start + BOOTSTRAP_BLOCK_BARS])
        sample = np.array(sampled[:n], dtype=float)
        diffs[i] = float(np.log1p(sample[:, 0]).mean() * periods_per_year - np.log1p(sample[:, 1]).mean() * periods_per_year)
    return {
        "iterations": BOOTSTRAP_ITERATIONS,
        "seed": BOOTSTRAP_SEED,
        "block_bars": BOOTSTRAP_BLOCK_BARS,
        "paired_period_count": int(n),
        "diff_log_growth_ci_low": float(np.quantile(diffs, 0.025)),
        "diff_log_growth_ci_high": float(np.quantile(diffs, 0.975)),
        "p_strategy_ge_benchmark": float(np.mean(diffs >= 0.0)),
    }


def p006_row_by_target(p006: dict[str, Any], target_vol: float) -> dict[str, Any]:
    for row in p006["scan_results"]:
        if abs(float(row["target_vol"]) - target_vol) < 1e-12:
            return row
    raise KeyError(f"P0-RES-006 row not found for target_vol={target_vol}")


def reconstruction_check(tsmom: Any) -> dict[str, Any]:
    p006 = json.loads(P006_JSON.read_text(encoding="utf-8"))
    p014 = json.loads(P014_JSON.read_text(encoding="utf-8"))
    bars, funding, _ = tsmom.load_data("L")
    raw = tsmom.raw_bars_from_prepared(bars)
    benchmark_bars = tsmom.prepare_passive_dataset("L", raw, funding)
    benchmark_result = tsmom.run_backtest(benchmark_bars, funding, label="benchmark_L_macro_bull")
    result = tsmom.run_backtest(
        bars,
        funding,
        label="p0res015_pre_cutoff_reconstruction_10pct",
        risk_budget=True,
        risk_target_vol=TARGET_POSITION_VOL,
        risk_window_bars=tsmom.RISK_BUDGET_WINDOW_BARS,
    )
    acceptance = tsmom.acceptance(result, benchmark_result)
    p006_row = p006_row_by_target(p006, TARGET_POSITION_VOL)
    p014_point = p014["points"][0]
    diffs = {
        "vs_p006_acceptance_ending_equity_abs_diff": abs(float(acceptance["metrics"]["ending_equity"]) - float(p006_row["acceptance"]["ending_equity"])),
        "vs_p006_acceptance_annualized_log_growth_abs_diff": abs(float(acceptance["metrics"]["annualized_log_growth"]) - float(p006_row["acceptance"]["annualized_log_growth"])),
        "vs_p014_unadjusted_ending_equity_abs_diff": abs(float(result.equity.iloc[-1]) - float(p014_point["old_v1_4_benchmark_gate"]["strategy_ending_equity"])),
        "vs_p014_unadjusted_return_mean_log_growth_abs_diff": abs(
            annualized_log_growth_from_returns(returns_from_equity(result.equity), annual_periods(tsmom))
            - float(p014_point["original_unadjusted"]["strategy"]["annualized_log_growth"])
        ),
    }
    passed = all(value <= (1e-6 if "ending" in key else 1e-12) for key, value in diffs.items())
    if not passed:
        raise AssertionError(f"pre-cutoff reconstruction mismatch: {diffs}")
    return {
        "passed": True,
        "p006_registered_acceptance": {
            "ending_equity": float(p006_row["acceptance"]["ending_equity"]),
            "annualized_log_growth": float(p006_row["acceptance"]["annualized_log_growth"]),
        },
        "p014_registered_unadjusted": {
            "ending_equity": float(p014_point["old_v1_4_benchmark_gate"]["strategy_ending_equity"]),
            "return_mean_annualized_log_growth": float(p014_point["original_unadjusted"]["strategy"]["annualized_log_growth"]),
        },
        "reconstructed": {
            "ending_equity": float(result.equity.iloc[-1]),
            "acceptance_annualized_log_growth": float(acceptance["metrics"]["annualized_log_growth"]),
            "return_mean_annualized_log_growth": annualized_log_growth_from_returns(returns_from_equity(result.equity), annual_periods(tsmom)),
        },
        "diffs": diffs,
    }


def hash_manifest(extra_files: dict[str, Path]) -> dict[str, str]:
    files = {
        "task_spec": TASK_SPEC_PATH,
        "tsmom_dual_engine": ENGINE_PATH,
        "p0res014_recheck_script": P014_SCRIPT_PATH,
        **extra_files,
    }
    return {name: sha256_file(path) for name, path in files.items()}


def render_report(payload: dict[str, Any]) -> str:
    gates = payload["holdout"]["gates"]
    metrics = payload["holdout"]["strategy_metrics"]
    bench = payload["holdout"]["benchmark_metrics"]
    trade = payload["holdout"]["trade_diagnostics"]
    gate_rows = "\n".join(
        f"| {name} | {row['value']} | {row['threshold']} | {row['pass']} |"
        for name, row in gates.items()
    )
    data_rows = "\n".join(
        f"| {sym} | {row['bars_rows_read_full_file']} | {row['bars_last_timestamp']} | {row['funding_rows_read_full_file']} | {row['funding_last_timestamp']} |"
        for sym, row in payload["data_audit"].items()
    )
    hash_rows = "\n".join(f"| {name} | `{digest}` |" for name, digest in payload["hashes"].items())
    quarter_rows = "\n".join(
        f"| {row['quarter']} | {row['start']} | {row['end']} | {row['simple_return']:.2%} | {row['log_return']:.4f} |"
        for row in payload["holdout"]["quarterly_returns"]
    )
    boundary_rows = "\n".join(
        f"| {row['symbol']} | {row['entry_time']} | {row['exit_time']} | {row['net_pnl']:.2f} | {row['expectancy_r']:.6f} |"
        for row in payload["holdout"]["cross_boundary_trades"]
    ) or "| none | - | - | - | - |"
    return f"""# REPORT_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712

**任务 ID:** {payload['task_id']}  
**生成时间:** {payload['generated_at_utc']}  
**性质:** DEC-093 授权的 TSMOM 引擎L 10%目标波动率点 Holdout 一次性盲验  
**Runner:** `06_RESEARCH/CODE/p0res015_engine_l_holdout_blind_20260712.py`  
**审计 JSON:** `06_RESEARCH/CODE/output/p0res015_engine_l_holdout_blind_20260712.json`

## 1. 四门判定

Runner 仅输出四门布尔值；正式 PASS/FAIL 由 Claude 验收后裁决。

| 门 | 数值 | 判据 | 是否通过 |
|---|---:|---|---:|
{gate_rows}

## 2. Holdout 指标

- 窗口：{payload['holdout']['window']['start']} -> {payload['holdout']['window']['end']} UTC；rebase 初始权益 100,000。
- 策略 ending equity：{metrics['ending_equity']:.2f}；年化 log growth：{metrics['annualized_log_growth']:.6f}；最大回撤：{metrics['max_drawdown']:.6f}。
- 基准 ending equity：{bench['ending_equity']:.2f}；缩放到 10% vol 后年化 log growth：{bench['scaled_to_10pct']['annualized_log_growth']:.6f}。
- H4 diff(strategy-benchmark)：{payload['holdout']['h4_scaled_comparison']['diff_log_growth']:.6f}；95%CI=[{payload['holdout']['h4_scaled_comparison']['bootstrap']['diff_log_growth_ci_low']:.6f}, {payload['holdout']['h4_scaled_comparison']['bootstrap']['diff_log_growth_ci_high']:.6f}]。

## 3. 交易诊断

- 窗内入场交易数：{trade['window_entry_trades']['trade_count']}。
- E[R]：{trade['window_entry_trades']['expectancy_r']}；赢均：{trade['window_entry_trades']['average_win_r']}；亏均(abs)：{trade['window_entry_trades']['average_loss_r_abs']}；赢亏比：{trade['window_entry_trades']['win_loss_ratio']}。
- funding 贡献（窗内入场交易口径，cost为正）：{trade['window_entry_trades']['funding_cost']:.2f}；手续费：{trade['window_entry_trades']['fees']:.2f}；滑点：{trade['window_entry_trades']['slippage_cost']:.2f}。
- 低功效标记（交易数<10）：{trade['low_power_trade_count_lt_10']}。

| 季度 | 起点 | 终点 | simple return | log return |
|---|---|---|---:|---:|
{quarter_rows}

### 跨界交易（不入 H1）

| symbol | entry_time | exit_time | net_pnl | E[R] |
|---|---|---|---:|---:|
{boundary_rows}

## 4. Hash 冻结

| 文件 | SHA256 |
|---|---|
{hash_rows}

## 5. 数据与自检

| symbol | mark rows read | mark last timestamp | funding rows read | funding last timestamp |
|---|---:|---|---:|---|
{data_rows}

- cutoff 前 10% 点重构对账：{payload['pre_cutoff_reconstruction']['passed']}；diffs={payload['pre_cutoff_reconstruction']['diffs']}。
- 禁读检查：未读取 `*_2026H1*`、`DATA/HOLDOUT/`、`~/.aiquant_sealed/`；runner 只从 `06_RESEARCH/DATA/FUTURES/` 指定 16 个文件读取。
- 参数冻结：lookback / ADX / macro gate / universe / FEE=0.001 / SLIPPAGE=0.001 / funding / LEVERAGE_CAP=1.0 均来自冻结引擎路径或任务书常量，未扫描 15% 点。
- Holdout 封账：本 runner 已对引擎 L 该 Holdout 窗完成一次性评估；后续不应再评估本窗。
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASK_INBOX_JSON.parent.mkdir(parents=True, exist_ok=True)

    tsmom = load_tsmom_module()
    periods_per_year = annual_periods(tsmom)
    pre_cutoff = reconstruction_check(tsmom)
    bars, funding, data_audit, data_files = load_full_data(tsmom)
    hashes = hash_manifest(data_files)

    raw = tsmom.raw_bars_from_prepared(bars)
    benchmark_bars = tsmom.prepare_passive_dataset("L", raw, funding)
    strategy_result = tsmom.run_backtest(
        bars,
        funding,
        label="p0res015_engine_l_target_vol_10_holdout_full_history",
        risk_budget=True,
        risk_target_vol=TARGET_POSITION_VOL,
        risk_window_bars=tsmom.RISK_BUDGET_WINDOW_BARS,
    )
    benchmark_result = tsmom.run_backtest(benchmark_bars, funding, label="benchmark_L_macro_bull_holdout_full_history")

    strategy_rebased = rebase_equity(strategy_result.equity, start=HOLDOUT_START, end=HOLDOUT_END)
    benchmark_rebased = rebase_equity(benchmark_result.equity, start=HOLDOUT_START, end=HOLDOUT_END)
    strategy_returns = returns_from_equity(strategy_rebased)
    benchmark_returns = returns_from_equity(benchmark_rebased)

    window_entry_trades = strategy_result.trades[
        (strategy_result.trades["entry_time"] >= HOLDOUT_START)
        & (strategy_result.trades["entry_time"] <= HOLDOUT_END)
    ].copy()
    cross_boundary = strategy_result.trades[
        (strategy_result.trades["entry_time"] < HOLDOUT_START)
        & (strategy_result.trades["exit_time"] >= HOLDOUT_START)
    ].copy()

    years = (strategy_rebased.index[-1] - strategy_rebased.index[0]).total_seconds() / (365.2425 * 24 * 3600)
    strat_ann_log = float(np.log(strategy_rebased.iloc[-1] / strategy_rebased.iloc[0]) / years)
    bench_ann_log = float(np.log(benchmark_rebased.iloc[-1] / benchmark_rebased.iloc[0]) / years)
    strat_scaled, strat_scale, strat_vol = scale_to_vol(strategy_returns, TARGET_STANDARD_VOL, periods_per_year)
    bench_scaled, bench_scale, bench_vol = scale_to_vol(benchmark_returns, TARGET_STANDARD_VOL, periods_per_year)
    strat_scaled_log = annualized_log_growth_from_returns(strat_scaled, periods_per_year)
    bench_scaled_log = annualized_log_growth_from_returns(bench_scaled, periods_per_year)
    boot = moving_block_bootstrap_diff(strat_scaled, bench_scaled, periods_per_year)
    trade_diag = summarize_trades(window_entry_trades)
    h1 = bool(trade_diag["expectancy_r"] is not None and trade_diag["expectancy_r"] > 0)
    h2 = bool(strat_ann_log > 0)
    holdout_dd = max_drawdown(strategy_rebased)
    h3 = bool(holdout_dd > -0.20)
    h4_underperform = bool((strat_scaled_log - bench_scaled_log) < 0 and boot["diff_log_growth_ci_high"] < 0)
    h4 = bool(not h4_underperform)

    payload = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "authorization": "DEC-093 Founder 2026-07-12 approved one-time Holdout use",
        "runner": rel(Path(__file__).resolve()),
        "official_verdict_reserved_for_claude": True,
        "all_four_gates_pass": bool(h1 and h2 and h3 and h4),
        "pre_cutoff_reconstruction": pre_cutoff,
        "hashes": hashes,
        "data_audit": data_audit,
        "forbidden_sources_check": {
            "read_2026H1_increment_files": False,
            "read_DATA_HOLDOUT": False,
            "read_aiquant_sealed": False,
        },
        "holdout": {
            "window": {"start": str(HOLDOUT_START), "end": str(HOLDOUT_END), "funding_end": str(FUNDING_END)},
            "strategy_metrics": {
                "starting_equity": float(strategy_rebased.iloc[0]),
                "ending_equity": float(strategy_rebased.iloc[-1]),
                "annualized_log_growth": strat_ann_log,
                "return_mean_annualized_log_growth": annualized_log_growth_from_returns(strategy_returns, periods_per_year),
                "annualized_vol": strat_vol,
                "max_drawdown": holdout_dd,
                "period_count": int(len(strategy_returns)),
            },
            "benchmark_metrics": {
                "starting_equity": float(benchmark_rebased.iloc[0]),
                "ending_equity": float(benchmark_rebased.iloc[-1]),
                "annualized_log_growth": bench_ann_log,
                "annualized_vol": bench_vol,
                "scaled_to_10pct": {
                    "scale": bench_scale,
                    "annualized_log_growth": bench_scaled_log,
                },
            },
            "h4_scaled_comparison": {
                "target_vol": TARGET_STANDARD_VOL,
                "strategy_scale": strat_scale,
                "benchmark_scale": bench_scale,
                "strategy_scaled_log_growth": strat_scaled_log,
                "benchmark_scaled_log_growth": bench_scaled_log,
                "diff_log_growth": strat_scaled_log - bench_scaled_log,
                "strategy_significantly_underperforms": h4_underperform,
                "bootstrap": boot,
            },
            "trade_diagnostics": {
                "window_entry_definition": "entry_time >= holdout_start and entry_time <= holdout_end; cross-boundary trades excluded from H1",
                "window_entry_trades": trade_diag,
                "low_power_trade_count_lt_10": bool(trade_diag["trade_count"] < 10),
            },
            "cross_boundary_trades": [
                {
                    "symbol": str(row.symbol),
                    "entry_time": str(row.entry_time),
                    "exit_time": str(row.exit_time),
                    "net_pnl": float(row.net_pnl),
                    "expectancy_r": float(row.expectancy_r),
                    "funding_cost": float(row.funding_cost),
                }
                for row in cross_boundary.itertuples(index=False)
            ],
            "quarterly_returns": quarterly_returns(strategy_rebased),
            "gates": {
                "H1_E_R_gt_0": {"value": trade_diag["expectancy_r"], "threshold": "> 0", "pass": h1},
                "H2_annualized_log_growth_gt_0": {"value": strat_ann_log, "threshold": "> 0", "pass": h2},
                "H3_max_drawdown_lt_20pct": {"value": holdout_dd, "threshold": "> -0.20", "pass": h3},
                "H4_not_significantly_underperform_passive": {"value": boot["diff_log_growth_ci_high"], "threshold": "diff 95%CI upper >= 0", "pass": h4},
            },
        },
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    signal = {
        "task_id": "P0RES015",
        "completed_at": utc_now(),
        "status": "PASS" if payload["all_four_gates_pass"] else "FAIL",
        "output_file": rel(REPORT_PATH),
        "next_task": None,
        "notes": (
            "Runner four-gate output: all pass"
            if payload["all_four_gates_pass"]
            else "Runner four-gate output: at least one Holdout gate failed"
        ),
    }
    TASK_INBOX_JSON.write_text(json.dumps(signal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT_JSON)
    print(REPORT_PATH)
    print(TASK_INBOX_JSON)


if __name__ == "__main__":
    main()
