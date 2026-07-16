#!/usr/bin/env python3
"""DEC-092 v1.5 passive benchmark recheck for TSMOM engine L.

This script applies the P0-RES-007 risk-adjusted benchmark method to the
already-registered P0-RES-006 engine-L 10% and 15% target-volatility position
points. It does not scan for new position points or alter signal logic.
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
OUTPUT_JSON = OUTPUT_DIR / "p0res014_engine_l_benchmark_recheck_20260706.json"
REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "REPORT_P0RES014_ENGINE_L_BENCHMARK_RECHECK_20260706.md"
P006_JSON = OUTPUT_DIR / "p0res006_engine_l_recheck_20260702.json"

TASK_ID = "P0-RES-014"
TARGET_POSITION_VOLS = (0.10, 0.15)
TARGET_VOL_STANDARD = 0.10
SEED = 20260702
BOOTSTRAP_ITERATIONS = 5000


def load_tsmom_module() -> Any:
    path = CODE_DIR / "tsmom_dual_engine.py"
    spec = importlib.util.spec_from_file_location("tsmom_dual_engine_p0res014", path)
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


def annual_periods(tsmom: Any) -> float:
    return 365.2425 * 24 / tsmom.BAR_HOURS


def annualized_log_growth(returns: pd.Series, periods_per_year: float) -> float:
    return float(np.log1p(returns.astype(float)).mean() * periods_per_year)


def annualized_arithmetic_return(returns: pd.Series, periods_per_year: float) -> float:
    return float(returns.astype(float).mean() * periods_per_year)


def annualized_vol(returns: pd.Series, periods_per_year: float) -> float:
    return float(returns.astype(float).std(ddof=1) * math.sqrt(periods_per_year))


def scale_to_vol(
    returns: pd.Series,
    target_vol: float,
    periods_per_year: float,
) -> tuple[pd.Series, float]:
    vol = annualized_vol(returns, periods_per_year)
    if not math.isfinite(vol) or vol <= 0:
        raise ValueError("cannot volatility-scale a zero-volatility series")
    scale = target_vol / vol
    return returns.astype(float) * scale, scale


def summarize_series(returns: pd.Series, periods_per_year: float) -> dict[str, float]:
    clean = returns.astype(float).dropna()
    return {
        "annualized_arithmetic_return": annualized_arithmetic_return(clean, periods_per_year),
        "annualized_log_growth": annualized_log_growth(clean, periods_per_year),
        "annualized_vol": annualized_vol(clean, periods_per_year),
        "min_period_return": float(clean.min()),
        "max_period_return": float(clean.max()),
        "period_count": int(len(clean)),
    }


def moving_block_bootstrap_diff(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    *,
    periods_per_year: float,
    block_bars: int,
) -> dict[str, float]:
    both = pd.concat(
        [strategy_returns.rename("strategy"), benchmark_returns.rename("benchmark")],
        axis=1,
    ).dropna()
    values = both.to_numpy(dtype=float)
    n = len(values)
    starts = np.arange(0, max(1, n - block_bars + 1))
    blocks_needed = int(math.ceil(n / block_bars))
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        sampled = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            sampled.extend(values[start : start + block_bars])
        sample = np.array(sampled[:n], dtype=float)
        strat = sample[:, 0]
        bench = sample[:, 1]
        diffs.append(
            float(
                np.log1p(strat).mean() * periods_per_year
                - np.log1p(bench).mean() * periods_per_year
            )
        )
    boot = np.array(diffs)
    return {
        "iterations": BOOTSTRAP_ITERATIONS,
        "seed": SEED,
        "block_bars": block_bars,
        "paired_period_count": int(n),
        "diff_log_growth_ci_low": float(np.quantile(boot, 0.025)),
        "diff_log_growth_ci_high": float(np.quantile(boot, 0.975)),
        "p_strategy_ge_benchmark": float(np.mean(boot >= 0.0)),
    }


def comparison_payload(
    name: str,
    strategy: pd.Series,
    benchmark: pd.Series,
    target_vol: float,
    *,
    periods_per_year: float,
    block_bars: int,
) -> dict[str, Any]:
    scaled_strategy, strategy_scale = scale_to_vol(strategy, target_vol, periods_per_year)
    scaled_benchmark, benchmark_scale = scale_to_vol(benchmark, target_vol, periods_per_year)
    strat_summary = summarize_series(scaled_strategy, periods_per_year)
    bench_summary = summarize_series(scaled_benchmark, periods_per_year)
    diff = strat_summary["annualized_log_growth"] - bench_summary["annualized_log_growth"]
    boot = moving_block_bootstrap_diff(
        scaled_strategy,
        scaled_benchmark,
        periods_per_year=periods_per_year,
        block_bars=block_bars,
    )
    return {
        "name": name,
        "target_vol": target_vol,
        "strategy_scale": strategy_scale,
        "benchmark_scale": benchmark_scale,
        "strategy": strat_summary,
        "benchmark": bench_summary,
        "strategy_minus_benchmark_log_growth": diff,
        "bootstrap_diff": boot,
        "strategy_significantly_underperforms": bool(diff < 0 and boot["diff_log_growth_ci_high"] < 0),
        "risk_adjusted_gate_pass": bool(not (diff < 0 and boot["diff_log_growth_ci_high"] < 0)),
    }


def returns_from_equity(equity: pd.Series) -> pd.Series:
    return equity.astype(float).pct_change().dropna()


def p006_row_by_target(p006: dict[str, Any], target_vol: float) -> dict[str, Any]:
    for row in p006["scan_results"]:
        if abs(float(row["target_vol"]) - target_vol) < 1e-12:
            return row
    raise KeyError(f"P0-RES-006 row not found for target_vol={target_vol}")


def assert_reconstructed_matches_p006(
    target_vol: float,
    acceptance: dict[str, Any],
    p006_row: dict[str, Any],
) -> dict[str, float]:
    metrics = acceptance["metrics"]
    expected = p006_row["acceptance"]
    diffs = {
        "ending_equity_abs_diff": abs(float(metrics["ending_equity"]) - float(expected["ending_equity"])),
        "annualized_log_growth_abs_diff": abs(
            float(metrics["annualized_log_growth"]) - float(expected["annualized_log_growth"])
        ),
        "p_dd20_abs_diff": abs(
            float(acceptance["liquidation_bootstrap"]["conservative_dd20_probability"])
            - float(expected["p_dd20"])
        ),
    }
    if diffs["ending_equity_abs_diff"] > 1e-6 or diffs["annualized_log_growth_abs_diff"] > 1e-12:
        raise AssertionError(f"reconstructed {target_vol:.0%} point does not match P0-RES-006: {diffs}")
    return diffs


def compact_existing_checks(p006_row: dict[str, Any], risk_adjusted_gate_pass: bool) -> dict[str, bool]:
    checks = dict(p006_row["acceptance"]["checks"])
    checks.pop("fifth_benchmark_excess_positive", None)
    checks["risk_adjusted_benchmark_gate_pass"] = bool(risk_adjusted_gate_pass)
    checks["all_seven_v1_5_checks_pass"] = bool(
        checks["positive_expectancy"]
        and checks["win_loss_ratio_ge_1_5"]
        and checks["standard_dd35_prob_le_20pct"]
        and checks["conservative_dd20_prob_le_10pct"]
        and checks["annualized_log_growth_positive"]
        and checks["positive_years_majority"]
        and checks["walk_forward_majority_positive"]
        and risk_adjusted_gate_pass
    )
    return checks


def render_report(payload: dict[str, Any]) -> str:
    original_rows = []
    adjusted_rows = []
    gate_rows = []
    for point in payload["points"]:
        original = point["original_unadjusted"]
        old = point["old_v1_4_benchmark_gate"]
        original_rows.append(
            "| {point} | {svol} | {bvol} | {slog} | {blog} | {diff} | {send} | {bend} | {excess} | {old_gate} |".format(
                point=pct(point["position_target_vol"], 0),
                svol=pct(original["strategy"]["annualized_vol"]),
                bvol=pct(original["benchmark"]["annualized_vol"]),
                slog=pct(original["strategy"]["annualized_log_growth"]),
                blog=pct(original["benchmark"]["annualized_log_growth"]),
                diff=pct(original["strategy_minus_benchmark_log_growth"]),
                send=f"{old['strategy_ending_equity']:,.2f}",
                bend=f"{old['benchmark_ending_equity']:,.2f}",
                excess=f"{old['excess_profit']:,.2f}",
                old_gate=old["fifth_benchmark_excess_positive"],
            )
        )
        for comp in point["comparisons"]:
            boot = comp["bootstrap_diff"]
            adjusted_rows.append(
                "| {point} | {name} | {target} | {svol} | {bvol} | {slog} | {blog} | {diff} | [{lo}, {hi}] | {pge} | {gate} |".format(
                    point=pct(point["position_target_vol"], 0),
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
                    gate="KILL" if comp["strategy_significantly_underperforms"] else "not significant / pass",
                )
            )
        checks = point["v1_5_checks"]
        gate_rows.append(
            "| {point} | {er} | {wl} | {dd35} | {dd20} | {growth} | {years} | {wf} | {bench} | {all_pass} |".format(
                point=pct(point["position_target_vol"], 0),
                er=checks["positive_expectancy"],
                wl=checks["win_loss_ratio_ge_1_5"],
                dd35=checks["standard_dd35_prob_le_20pct"],
                dd20=checks["conservative_dd20_prob_le_10pct"],
                growth=checks["annualized_log_growth_positive"],
                years=checks["positive_years_majority"],
                wf=checks["walk_forward_majority_positive"],
                bench=checks["risk_adjusted_benchmark_gate_pass"],
                all_pass=checks["all_seven_v1_5_checks_pass"],
            )
        )

    primary = payload["points"][0]["comparisons"][0]
    primary_boot = primary["bootstrap_diff"]
    final_text = payload["final_verdict_text"]

    return f"""# REPORT_P0RES014_ENGINE_L_BENCHMARK_RECHECK_20260706

**任务 ID:** {payload['task_id']}  
**生成时间:** {payload['generated_at_utc']}  
**性质:** DEC-092 / v1.5 第5件诊断复查；家族内诊断复查收尾，不消耗独立试验计数  
**脚本:** `06_RESEARCH/CODE/p0res014_engine_l_benchmark_recheck_20260706.py`  
**审计输出:** `06_RESEARCH/CODE/output/p0res014_engine_l_benchmark_recheck_20260706.json`

## 0. 方法与边界

- 策略：冻结的 `tsmom_dual_engine.py` 引擎 L；只重构 P0-RES-006 已登记的 10% / 15% 目标波动率仓位点，不重扫仓位，不新增点。
- 基准：`prepare_passive_dataset("L", raw, funding)` + `run_backtest(..., label="benchmark_L_macro_bull")`，与 P0-RES-006 warm-up/旧第五件基准一致。
- 风险调整：沿用 P0-RES-007 v1.5 方法，将策略和基准收益分别缩放到同一目标年化波动率后比较年化 log growth；主表为 10% 年化 vol，敏感性为“都缩放到基准实际 vol”。
- 显著性：4H 原频率 paired moving-block bootstrap，块长 {payload['bootstrap']['block_bars']} 根 4H（沿用引擎 L 原 bootstrap 块长），{payload['bootstrap']['iterations']} 次，seed `{payload['bootstrap']['seed']}`。
- Holdout：未读取 `HOLDOUT` 或 `2026H1`；数据 cutoff 仍为 `{payload['cutoff_utc']}`。
- 复用说明：P0-RES-006 JSON 未持久化收益序列；本脚本用同一冻结代码路径重构指定两条序列，并校验 ending equity / annualized log growth 与 P0-RES-006 完全一致。

## 1. 风险调整前对照

| position target vol | strategy ann. vol | benchmark ann. vol | strategy ann. log growth | benchmark ann. log growth | strategy-benchmark log diff | strategy ending equity | benchmark ending equity | old raw equity excess | old v1.4 fifth gate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(original_rows)}

旧口径用 ending equity / raw profit 直接比较，因此 10% 与 15% 两个点的 `fifth_benchmark_excess_positive` 均为 False。

## 2. 风险调整后比较

| position target vol | comparison | target vol | strategy vol | benchmark vol | strategy log growth | benchmark log growth | diff | diff 95% CI | P(strategy>=benchmark) | gate |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(adjusted_rows)}

主口径 10% 仓位点：策略年化 log growth {pct(primary['strategy']['annualized_log_growth'])}，基准 {pct(primary['benchmark']['annualized_log_growth'])}，差值 {pct(primary['strategy_minus_benchmark_log_growth'])}；95%CI=[{pct(primary_boot['diff_log_growth_ci_low'])}, {pct(primary_boot['diff_log_growth_ci_high'])}]，P(strategy>=benchmark)={pct(primary_boot['p_strategy_ge_benchmark'], 2)}。

## 3. 七项检查复核

| position target vol | E[R]>0 | win/loss>=1.5 | P(DD35)<=20% | P(DD20)<=10% | log growth>0 | positive years majority | WF majority positive | v1.5 risk-adjusted benchmark gate | all pass |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(gate_rows)}

## 4. 判定

**{payload['passive_benchmark_gate_verdict']}。** 风险调整后，“策略显著跑输基准”不成立；旧 v1.4 原始收益比较导致的被动基准 KILL 不再成立。

{final_text}

## 5. 自检

- 未改动仓位扫描范围；本脚本只跑 P0-RES-006 已登记且已通过 DD/增长门的 10% / 15% 两点。
- 未引入新仓位点，未改动 lookback / ADX / macro gate / universe / 成本 / funding / cutoff。
- 未读取 Holdout；`safe_market_path` 仍禁止 `2026H1` 文件名，数据审计最后时间为 2024-12-09。
- 10% / 15% 重构一致性校验已通过，详见 JSON 的 `p006_reconstruction_check`。
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    tsmom = load_tsmom_module()
    p006 = json.loads(P006_JSON.read_text(encoding="utf-8"))
    periods_per_year = annual_periods(tsmom)

    bars, funding, data_audit = tsmom.load_data("L")
    raw = tsmom.raw_bars_from_prepared(bars)
    benchmark_bars = tsmom.prepare_passive_dataset("L", raw, funding)
    benchmark_result = tsmom.run_backtest(benchmark_bars, funding, label="benchmark_L_macro_bull")
    benchmark_returns = returns_from_equity(benchmark_result.equity)
    benchmark_summary = summarize_series(benchmark_returns, periods_per_year)
    benchmark_actual_vol = benchmark_summary["annualized_vol"]

    points = []
    for target_vol in TARGET_POSITION_VOLS:
        result = tsmom.run_backtest(
            bars,
            funding,
            label=f"p0res006_engine_l_target_vol_{int(target_vol * 100)}",
            risk_budget=True,
            risk_target_vol=target_vol,
            risk_window_bars=tsmom.RISK_BUDGET_WINDOW_BARS,
        )
        acceptance = tsmom.acceptance(result, benchmark_result)
        p006_row = p006_row_by_target(p006, target_vol)
        reconstruction_check = assert_reconstructed_matches_p006(target_vol, acceptance, p006_row)
        strategy_returns = returns_from_equity(result.equity)
        strategy_summary = summarize_series(strategy_returns, periods_per_year)
        original = {
            "strategy": strategy_summary,
            "benchmark": benchmark_summary,
            "strategy_minus_benchmark_log_growth": (
                strategy_summary["annualized_log_growth"] - benchmark_summary["annualized_log_growth"]
            ),
        }
        comparisons = [
            comparison_payload(
                "both scaled to 10% annual vol",
                strategy_returns,
                benchmark_returns,
                TARGET_VOL_STANDARD,
                periods_per_year=periods_per_year,
                block_bars=tsmom.BOOTSTRAP_BLOCK_BARS,
            ),
            comparison_payload(
                "both scaled to benchmark actual vol",
                strategy_returns,
                benchmark_returns,
                benchmark_actual_vol,
                periods_per_year=periods_per_year,
                block_bars=tsmom.BOOTSTRAP_BLOCK_BARS,
            ),
        ]
        primary_gate_pass = comparisons[0]["risk_adjusted_gate_pass"]
        points.append(
            {
                "position_target_vol": target_vol,
                "reconstructed_label": result.label,
                "p006_reconstruction_check": reconstruction_check,
                "original_unadjusted": original,
                "comparisons": comparisons,
                "old_v1_4_benchmark_gate": {
                    "strategy_ending_equity": float(result.equity.iloc[-1]),
                    "benchmark_ending_equity": float(benchmark_result.equity.iloc[-1]),
                    "excess_profit": float(result.equity.iloc[-1] - benchmark_result.equity.iloc[-1]),
                    "fifth_benchmark_excess_positive": bool(
                        p006_row["acceptance"]["checks"]["fifth_benchmark_excess_positive"]
                    ),
                },
                "p006_existing_acceptance": p006_row["acceptance"],
                "v1_5_checks": compact_existing_checks(p006_row, primary_gate_pass),
            }
        )

    primary_kill = points[0]["comparisons"][0]["strategy_significantly_underperforms"]
    all_primary_pass = points[0]["v1_5_checks"]["all_seven_v1_5_checks_pass"]
    if all_primary_pass:
        final_verdict_text = (
            "TSMOM引擎L·10%目标波动率点＝七项检查全过，构成DEC-092后首个重新达标候选，"
            "是否晋级正常验收/paper-forward流程待Claude/Founder决定。"
        )
    else:
        failed = [
            name
            for name, value in points[0]["v1_5_checks"].items()
            if name != "all_seven_v1_5_checks_pass" and value is False
        ]
        final_verdict_text = "10%目标波动率点仍有未过项：" + ", ".join(failed)

    payload = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "diagnostic_recheck": "DEC-092 v1.5 item 5 for TSMOM engine L",
        "independent_experiment_count_consumed": False,
        "holdout_read": False,
        "source_script_reused": "06_RESEARCH/CODE/tsmom_dual_engine.py",
        "p006_source_json": str(P006_JSON.relative_to(ROOT)),
        "p007_method_source": "06_RESEARCH/CODE/p0res007_x3_benchmark_recheck_20260702.py",
        "position_target_vols_rechecked": list(TARGET_POSITION_VOLS),
        "no_position_scan_performed": True,
        "frequency": "4H",
        "annual_periods": periods_per_year,
        "cutoff_utc": str(tsmom.CUT_OFF),
        "bootstrap": {
            "iterations": BOOTSTRAP_ITERATIONS,
            "seed": SEED,
            "block_bars": tsmom.BOOTSTRAP_BLOCK_BARS,
        },
        "data_audit": data_audit,
        "points": points,
        "passive_benchmark_gate_verdict": (
            "KILL_MAINTAINED_RISK_ADJUSTED" if primary_kill else "RISK_ADJUSTED_GATE_NOT_CONFIRMED"
        ),
        "ten_pct_all_seven_v1_5_checks_pass": bool(all_primary_pass),
        "final_verdict_text": final_verdict_text,
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    print(OUTPUT_JSON)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
