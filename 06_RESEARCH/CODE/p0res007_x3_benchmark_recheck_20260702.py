#!/usr/bin/env python3
"""DEC-092 diagnostic recheck for X3 passive benchmark gate.

The original X3 B1 verdict remains governed by monotonicity and survivorship
gates. This script only recomputes the passive benchmark comparison after
volatility matching, using the frozen B1 strategy and benchmark return series.
"""

from __future__ import annotations

import datetime as dt
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
OUTPUT_DIR = CODE_DIR / "output"
OUTPUT_JSON = OUTPUT_DIR / "p0res007_x3_benchmark_recheck_20260702.json"
REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "REPORT_P0RES007_X3_BENCHMARK_RECHECK_20260702.md"

TASK_ID = "P0-RES-007"
SEED = 20260702
BOOTSTRAP_ITERATIONS = 5000
BOOTSTRAP_BLOCK_WEEKS = 4
ANNUAL_WEEKS = 52
TARGET_VOL_STANDARD = 0.10


def load_x3_module() -> Any:
    path = CODE_DIR / "x3_momentum_redteam_b1_audit.py"
    spec = importlib.util.spec_from_file_location("x3_momentum_recheck", path)
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


def annualized_log_growth(returns: pd.Series) -> float:
    return float(np.log1p(returns.astype(float)).mean() * ANNUAL_WEEKS)


def annualized_arithmetic_return(returns: pd.Series) -> float:
    return float(returns.astype(float).mean() * ANNUAL_WEEKS)


def annualized_vol(returns: pd.Series) -> float:
    return float(returns.astype(float).std(ddof=1) * math.sqrt(ANNUAL_WEEKS))


def scale_to_vol(returns: pd.Series, target_vol: float) -> tuple[pd.Series, float]:
    vol = annualized_vol(returns)
    if not math.isfinite(vol) or vol <= 0:
        raise ValueError("cannot volatility-scale a zero-volatility series")
    scale = target_vol / vol
    return returns.astype(float) * scale, scale


def summarize_series(returns: pd.Series) -> dict[str, float]:
    return {
        "annualized_arithmetic_return": annualized_arithmetic_return(returns),
        "annualized_log_growth": annualized_log_growth(returns),
        "annualized_vol": annualized_vol(returns),
        "min_period_return": float(returns.min()),
        "max_period_return": float(returns.max()),
    }


def moving_block_bootstrap_diff(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> dict[str, float]:
    both = pd.concat(
        [strategy_returns.rename("strategy"), benchmark_returns.rename("benchmark")],
        axis=1,
    ).dropna()
    values = both.to_numpy(dtype=float)
    n = len(values)
    starts = np.arange(0, max(1, n - BOOTSTRAP_BLOCK_WEEKS + 1))
    blocks_needed = int(math.ceil(n / BOOTSTRAP_BLOCK_WEEKS))
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        sampled = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            sampled.extend(values[start : start + BOOTSTRAP_BLOCK_WEEKS])
        sample = np.array(sampled[:n], dtype=float)
        strat = sample[:, 0]
        bench = sample[:, 1]
        diffs.append(float(np.log1p(strat).mean() * ANNUAL_WEEKS - np.log1p(bench).mean() * ANNUAL_WEEKS))
    boot = np.array(diffs)
    return {
        "iterations": BOOTSTRAP_ITERATIONS,
        "seed": SEED,
        "block_weeks": BOOTSTRAP_BLOCK_WEEKS,
        "diff_log_growth_ci_low": float(np.quantile(boot, 0.025)),
        "diff_log_growth_ci_high": float(np.quantile(boot, 0.975)),
        "p_strategy_ge_benchmark": float(np.mean(boot >= 0.0)),
    }


def comparison_payload(name: str, strategy: pd.Series, benchmark: pd.Series, target_vol: float) -> dict[str, Any]:
    scaled_strategy, strategy_scale = scale_to_vol(strategy, target_vol)
    scaled_benchmark, benchmark_scale = scale_to_vol(benchmark, target_vol)
    strat_summary = summarize_series(scaled_strategy)
    bench_summary = summarize_series(scaled_benchmark)
    diff = strat_summary["annualized_log_growth"] - bench_summary["annualized_log_growth"]
    boot = moving_block_bootstrap_diff(scaled_strategy, scaled_benchmark)
    return {
        "name": name,
        "target_vol": target_vol,
        "strategy_scale": strategy_scale,
        "benchmark_scale": benchmark_scale,
        "strategy": strat_summary,
        "benchmark": bench_summary,
        "strategy_minus_benchmark_log_growth": diff,
        "bootstrap_diff": boot,
        "strategy_still_underperforms": bool(diff < 0 and boot["diff_log_growth_ci_high"] < 0),
    }


def render_report(payload: dict[str, Any]) -> str:
    rows = []
    for comp in payload["comparisons"]:
        boot = comp["bootstrap_diff"]
        rows.append(
            "| {name} | {target} | {svol} | {bvol} | {slog} | {blog} | {diff} | [{lo}, {hi}] | {pge} | {verdict} |".format(
                name=comp["name"],
                target=pct(comp["target_vol"]),
                svol=pct(comp["strategy"]["annualized_vol"]),
                bvol=pct(comp["benchmark"]["annualized_vol"]),
                slog=pct(comp["strategy"]["annualized_log_growth"]),
                blog=pct(comp["benchmark"]["annualized_log_growth"]),
                diff=pct(comp["strategy_minus_benchmark_log_growth"]),
                lo=pct(boot["diff_log_growth_ci_low"]),
                hi=pct(boot["diff_log_growth_ci_high"]),
                pge=pct(boot["p_strategy_ge_benchmark"], 2),
                verdict="KILL" if comp["strategy_still_underperforms"] else "not significant",
            )
        )

    original = payload["original_unadjusted"]
    primary = payload["comparisons"][0]
    primary_boot = primary["bootstrap_diff"]
    if payload["passive_benchmark_gate_verdict"] == "KILL_MAINTAINED_RISK_ADJUSTED":
        passive_text = (
            "风险调整后仍显著跑输，被动基准门维持 KILL。"
            f"在主口径 10% 年化波动率匹配后，#X3 策略年化 log growth 为 {pct(primary['strategy']['annualized_log_growth'])}，"
            f"等权 alt 基准为 {pct(primary['benchmark']['annualized_log_growth'])}，"
            f"差值 {pct(primary['strategy_minus_benchmark_log_growth'])}；"
            f"bootstrap 95%CI=[{pct(primary_boot['diff_log_growth_ci_low'])}, {pct(primary_boot['diff_log_growth_ci_high'])}]，"
            f"P(strategy>=benchmark)={pct(primary_boot['p_strategy_ge_benchmark'], 2)}。"
        )
        impact_text = "被动基准门本身仍成立；整体判决维持 **KILL**。"
    else:
        passive_text = (
            "风险调整后点估计仍跑输，但“显著跑输”未确认；被动基准门不再作为独立 KILL 死因成立。"
            f"在主口径 10% 年化波动率匹配后，#X3 策略年化 log growth 为 {pct(primary['strategy']['annualized_log_growth'])}，"
            f"等权 alt 基准为 {pct(primary['benchmark']['annualized_log_growth'])}，"
            f"差值 {pct(primary['strategy_minus_benchmark_log_growth'])}；"
            f"bootstrap 95%CI=[{pct(primary_boot['diff_log_growth_ci_low'])}, {pct(primary_boot['diff_log_growth_ci_high'])}]，"
            f"P(strategy>=benchmark)={pct(primary_boot['p_strategy_ge_benchmark'], 2)}。"
        )
        impact_text = (
            "整体判决仍维持 **KILL**，因为原主死因“截面单调 CI 穿 0 + 删除前20%赢家后 edge 翻负”独立成立。"
        )
    return f"""# REPORT_P0RES007_X3_BENCHMARK_RECHECK_20260702

**任务 ID:** {payload['task_id']}  
**生成时间:** {payload['generated_at_utc']}  
**性质:** DEC-092 / v1.5 第5件诊断复查，不消耗独立试验计数  
**脚本:** `06_RESEARCH/CODE/p0res007_x3_benchmark_recheck_20260702.py`  
**审计输出:** `06_RESEARCH/CODE/output/p0res007_x3_benchmark_recheck_20260702.json`

## 0. 方法

- 策略：沿用 `REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md` 的周频低换手 CS 动量，base 成本 0.20%/fill 后净收益。
- 基准：同一周频表中的等权持有 alt 基准 `ew_alt_return`。
- 风险调整：分别将策略和基准周收益缩放到同一目标年化波动率后比较年化 log growth；主表使用 10% vol，附带“都缩放到基准实际 vol”敏感性。
- 显著性：周频 paired moving-block bootstrap，块长 4 周，5000 次，seed `20260702`，比较 `strategy - benchmark` 的年化 log growth 差。
- Holdout：未读取 Holdout；只复用原 B1 脚本从 `06_RESEARCH/DATA/FUTURES_EXPANDED` 构造原口径周频序列。

## 1. 原始未调波动结果

| series | ann. vol | ann. arithmetic return | ann. log growth |
|---|---:|---:|---:|
| CS strategy, base cost | {pct(original['strategy']['annualized_vol'])} | {pct(original['strategy']['annualized_arithmetic_return'])} | {pct(original['strategy']['annualized_log_growth'])} |
| EW alt benchmark | {pct(original['benchmark']['annualized_vol'])} | {pct(original['benchmark']['annualized_arithmetic_return'])} | {pct(original['benchmark']['annualized_log_growth'])} |

原报告附加死因的原始口径为 CS 年化 log growth {pct(original['strategy']['annualized_log_growth'])} vs 等权 alt {pct(original['benchmark']['annualized_log_growth'])}。

## 2. 风险调整后比较

| comparison | target vol | strategy vol | benchmark vol | strategy log growth | benchmark log growth | diff | diff 95% CI | P(strategy>=benchmark) | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(rows)}

## 3. 判定

**{payload['passive_benchmark_gate_verdict']}。** {passive_text}

{impact_text}
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    x3 = load_x3_module()

    closes, inventory = x3.load_daily_close()
    weekly = x3.run_strategy(closes, "weekly")
    if weekly.empty:
        raise RuntimeError("weekly X3 strategy returned no rows")

    strategy = weekly["raw_return"].astype(float) - weekly["total_turnover"].astype(float) * x3.COST_CASES["protocol_base_0_20pct"]
    benchmark = weekly["ew_alt_return"].astype(float)
    original = {
        "strategy": summarize_series(strategy),
        "benchmark": summarize_series(benchmark),
    }
    benchmark_vol = original["benchmark"]["annualized_vol"]
    comparisons = [
        comparison_payload("both scaled to 10% annual vol", strategy, benchmark, TARGET_VOL_STANDARD),
        comparison_payload("both scaled to benchmark actual vol", strategy, benchmark, benchmark_vol),
    ]
    gate_kill = comparisons[0]["strategy_still_underperforms"]

    payload = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "diagnostic_recheck": "DEC-092 v1.5 item 5",
        "independent_experiment_count_consumed": False,
        "holdout_read": False,
        "source_script_reused": "06_RESEARCH/CODE/x3_momentum_redteam_b1_audit.py",
        "frequency": "weekly",
        "cost_case": "protocol_base_0_20pct",
        "data_inventory": {
            "data_path": str(x3.DATA_DIR.relative_to(ROOT)),
            "csv_files": len(inventory),
            "symbols": [row["symbol"] for row in inventory],
        },
        "original_unadjusted": original,
        "comparisons": comparisons,
        "passive_benchmark_gate_verdict": "KILL_MAINTAINED_RISK_ADJUSTED" if gate_kill else "RISK_ADJUSTED_GATE_NOT_CONFIRMED",
        "overall_verdict": "KILL_MAINTAINED",
        "overall_verdict_reason": "Primary kill reasons remain monotonicity CI crossing zero and in-panel survivorship stress; passive benchmark gate is not confirmed as a significant independent KILL reason after volatility matching.",
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    print(OUTPUT_JSON)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
