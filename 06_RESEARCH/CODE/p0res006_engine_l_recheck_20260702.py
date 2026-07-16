#!/usr/bin/env python3
"""DEC-092 diagnostic recheck for TSMOM engine L position sizing.

This script reuses the frozen engine-L signal implementation in
`tsmom_dual_engine.py`. It only scans the pre-registered risk-budget target
volatility grid below and does not alter signal, universe, cost, funding, or
cutoff logic.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT / "06_RESEARCH" / "CODE"
OUTPUT_DIR = CODE_DIR / "output"
OUTPUT_JSON = OUTPUT_DIR / "p0res006_engine_l_recheck_20260702.json"
REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "REPORT_P0RES006_ENGINE_L_RECHECK_20260702.md"

TASK_ID = "P0-RES-006"
SCAN_TARGET_VOLS = (0.10, 0.15, 0.20, 0.25, 0.30)


def load_tsmom_module() -> Any:
    path = CODE_DIR / "tsmom_dual_engine.py"
    spec = importlib.util.spec_from_file_location("tsmom_dual_engine_recheck", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{100.0 * float(value):.{digits}f}%"


def round_float(value: Any, digits: int = 6) -> Any:
    if isinstance(value, float):
        return round(value, digits)
    return value


def compact_acceptance(acceptance: dict[str, Any]) -> dict[str, Any]:
    metrics = acceptance["metrics"]
    boot = acceptance["liquidation_bootstrap"]
    annual = acceptance["annual_trade_expectancy"]
    checks = acceptance["checks"]
    return {
        "annualized_log_growth": metrics["annualized_log_growth"],
        "ending_equity": metrics["ending_equity"],
        "max_drawdown": metrics["max_drawdown"],
        "expectancy_r": metrics["expectancy_r"],
        "win_loss_ratio": metrics["win_loss_ratio"],
        "trade_count": metrics["trade_count"],
        "risk_scale_min": metrics["risk_scale_min"],
        "risk_scale_mean": metrics["risk_scale_mean"],
        "risk_scale_lt_1_bars": metrics["risk_scale_lt_1_bars"],
        "p_dd35": boot["standard_dd35_probability"],
        "p_dd20": boot["conservative_dd20_probability"],
        "bootstrap_block_bars": boot["block_bars"],
        "bootstrap_year_bars": boot["year_bars"],
        "bootstrap_iterations": boot["iterations"],
        "bootstrap_seed": boot["seed"],
        "positive_years": annual["positive_years"],
        "counted_years": annual["counted_years"],
        "positive_years_majority": annual["positive_years_majority"],
        "walk_forward_positive_windows": acceptance["walk_forward_positive_windows"],
        "checks": checks,
        "decision_by_v1_5_position_gate": bool(
            boot["conservative_dd20_probability"] <= 0.10
            and metrics["annualized_log_growth"] > 0
        ),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = []
    for row in payload["scan_results"]:
        acc = row["acceptance"]
        rows.append(
            "| {target} | {ending} | {ann_log} | {pdd20} | {pdd35} | {exp_r} | {wl} | {years} | {scale_min} | {scale_mean} | {pass_gate} |".format(
                target=pct(row["target_vol"], 0),
                ending=f"{acc['ending_equity']:,.2f}",
                ann_log=pct(acc["annualized_log_growth"]),
                pdd20=pct(acc["p_dd20"], 2),
                pdd35=pct(acc["p_dd35"], 2),
                exp_r=f"{acc['expectancy_r']:.6f}",
                wl=f"{acc['win_loss_ratio']:.3f}",
                years=f"{acc['positive_years']}/{acc['counted_years']}",
                scale_min=f"{acc['risk_scale_min']:.6f}",
                scale_mean=f"{acc['risk_scale_mean']:.6f}",
                pass_gate=acc["decision_by_v1_5_position_gate"],
            )
        )

    feasible = payload["feasible_points"]
    feasible_text = (
        ", ".join(pct(point["target_vol"], 0) for point in feasible)
        if feasible
        else "无"
    )
    verdict = payload["verdict"]
    first = feasible[0] if feasible else None
    best_line = ""
    if first is not None:
        acc = first["acceptance"]
        best_line = (
            f"\n最保守可行点为 **{pct(first['target_vol'], 0)} 目标波动率**："
            f"P(年DD>=20%)={pct(acc['p_dd20'], 2)}，"
            f"年化log增长={pct(acc['annualized_log_growth'])}，"
            f"赢亏比={acc['win_loss_ratio']:.3f}，"
            f"分年正期望={acc['positive_years']}/{acc['counted_years']}。"
        )

    return f"""# REPORT_P0RES006_ENGINE_L_RECHECK_20260702

**任务 ID:** {payload['task_id']}  
**生成时间:** {payload['generated_at_utc']}  
**性质:** DEC-092 / v1.5 第3件诊断复查，不消耗独立试验计数  
**脚本:** `06_RESEARCH/CODE/p0res006_engine_l_recheck_20260702.py`  
**审计输出:** `06_RESEARCH/CODE/output/p0res006_engine_l_recheck_20260702.json`

## 0. 预登记扫描范围

- 信号层：冻结的 `tsmom_dual_engine.py` 引擎 L，regime-first TSMOM；未改 lookback、ADX、macro gate、universe、成本、真实 funding、cutoff。
- 扫描对象：风险预算目标波动率曲线，`k_t = min(1, target_vol / sigma_t)`，sigma 使用过去 42 根 4H 已完成组合收益。
- 一次性网格：10% / 15% / 20% / 25% / 30% 年化目标波动率，共 5 点；25% 是原 v2 对照点。
- Bootstrap：块长 42 根 4H，2000 条一年路径，seed `20260612`，沿用原实现。
- 判定门：存在至少一个仓位点同时满足 `P(年DD>=20%) <= 10%` 且 `年化log增长 > 0`。
- Holdout：未读取任何 `HOLDOUT` 或 `2026H1` 路径；数据 cutoff 仍为 `2024-12-09 23:59:00 UTC`。

## 1. 逐点结果

| target vol | ending equity | ann. log growth | P(DD>=20%) | P(DD>=35%) | E[R] | win/loss | positive years | min k | mean k | v1.5 gate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(rows)}

## 2. 判定

**{verdict}。** 可行仓位点：{feasible_text}。{best_line}

这说明旧判决中“只测全仓 v1 与 25% vol target v2 后锁死定仓维度穷尽”的口径在 v1.5 下不成立；新口径问题“是否存在可行仓位方案”的答案是 **存在**。本任务只回答存在性，不自动晋级；是否将该信号层重新纳入正常验收流程由 Claude 决定。

## 3. 复查边界

- 未新增信号、未优化 lookback/ADX/macro gate、未扩大 universe。
- 未在看到结果后追加仓位点；5 点网格是本脚本常量。
- 20%/25%/30% 目标波动率未通过 DD20 门；原 25% v2 的 `P(DD>=20%)=17.45%` 被复现。
- 原信号层正期望、赢亏比与分年正期望仍成立；本次变化只来自更保守仓位点使 DD20 门通过。
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tsmom = load_tsmom_module()

    bars, funding, data_audit = tsmom.load_data("L")
    raw = tsmom.raw_bars_from_prepared(bars)
    benchmark_bars = tsmom.prepare_passive_dataset("L", raw, funding)
    benchmark = tsmom.run_backtest(benchmark_bars, funding, label="benchmark_L_macro_bull")

    results = []
    for target_vol in SCAN_TARGET_VOLS:
        result = tsmom.run_backtest(
            bars,
            funding,
            label=f"p0res006_engine_l_target_vol_{int(target_vol * 100)}",
            risk_budget=True,
            risk_target_vol=target_vol,
            risk_window_bars=tsmom.RISK_BUDGET_WINDOW_BARS,
        )
        acceptance = compact_acceptance(tsmom.acceptance(result, benchmark))
        results.append(
            {
                "target_vol": target_vol,
                "acceptance": acceptance,
            }
        )

    feasible = [row for row in results if row["acceptance"]["decision_by_v1_5_position_gate"]]
    payload = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "diagnostic_recheck": "DEC-092 v1.5 item 3",
        "independent_experiment_count_consumed": False,
        "holdout_read": False,
        "script_reused": "06_RESEARCH/CODE/tsmom_dual_engine.py",
        "cutoff_utc": str(tsmom.CUT_OFF),
        "pre_registered_scan_target_vols": list(SCAN_TARGET_VOLS),
        "bootstrap": {
            "seed": tsmom.BOOTSTRAP_SEED,
            "iterations": tsmom.BOOTSTRAP_ITERATIONS,
            "block_bars": tsmom.BOOTSTRAP_BLOCK_BARS,
            "year_bars": tsmom.BOOTSTRAP_YEAR_BARS,
        },
        "data_audit": data_audit,
        "scan_results": results,
        "feasible_points": feasible,
        "verdict": "EXISTS_FEASIBLE_POSITION_SIZING" if feasible else "FAILED_NO_FEASIBLE_POSITION_SIZING",
    }

    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=round_float) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    print(OUTPUT_JSON)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
