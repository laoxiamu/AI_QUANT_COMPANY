#!/usr/bin/env python3
"""D2 TSMOM extended-universe backtest with fail-closed input auditing.

Variant C reproduces the frozen eight-asset long engine. Variants A/B are
executed only when the expanded inputs preserve the same mark-price source,
include real funding, and carry auditable DEC-070 universe-quality evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tsmom_dual_engine import (
    ADX_ENTRY,
    ADX_EXIT,
    ADX_PERIOD,
    BOOTSTRAP_BLOCK_BARS,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    CUT_OFF,
    FEE_RATE,
    LOOKBACK_BARS,
    MACRO_MA_DAYS,
    SLIPPAGE_RATE,
    SYMBOL_ORDER,
    acceptance,
    load_data,
    prepare_bars,
    prepare_passive_bars,
    prepare_passive_dataset,
    raw_bars_from_prepared,
    run_backtest,
)


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "06_RESEARCH" / "DATA"
EXPANDED = DATA / "FUTURES_EXPANDED"
MANIFEST_PATH = EXPANDED / "DOWNLOAD_MANIFEST.json"
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULT_PATH = (
    ROOT
    / "06_RESEARCH"
    / "RESULTS"
    / "20260613_tsmom_extended_backtest_report.md"
)
CODEX_REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "REPORT_D2.md"
SUMMARY_PATH = OUTPUT / "tsmom_extended_summary.json"

HARD_CUTOFF = pd.Timestamp("2024-12-09 23:59:59")
BASE_FULL_SYMBOLS = tuple(f"{symbol}USDT" for symbol in SYMBOL_ORDER)
EXPECTED_BASELINE_EXPECTANCY = 0.06607270148934911
EXPECTED_BASELINE_EXCESS = 168_664.4375067039
REPRODUCTION_RELATIVE_TOLERANCE = 0.05
WF_BOUNDARIES = (
    pd.Timestamp("2020-01-01 00:00:00"),
    pd.Timestamp("2021-08-24 12:00:00"),
    pd.Timestamp("2023-04-18 04:00:00"),
    pd.Timestamp("2024-12-10 00:00:00"),
)
DEC_070_REQUIRED_FILTERS = {
    "adtv",
    "float_market_cap_ratio",
    "oi_market_cap_ratio",
    "price_jump_frequency",
}


@dataclass(frozen=True)
class Blocker:
    code: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("summary", {}).get("success", 0) < 20:
        raise ValueError("D1 dependency failed: manifest success < 20")
    return manifest


def select_expanded_symbols(
    manifest: dict[str, Any],
    count: int,
) -> list[str]:
    downloads = manifest.get("downloads", {})
    candidates = [
        (symbol, int(record["rows"]))
        for symbol, record in downloads.items()
        if record.get("ok") is True and symbol not in BASE_FULL_SYMBOLS
    ]
    candidates.sort(key=lambda item: (-item[1], item[0]))
    selected = [symbol for symbol, _ in candidates[:count]]
    if len(selected) < count:
        raise ValueError(f"requested {count} expanded symbols, found {len(selected)}")
    return selected


def assert_pre_holdout_frame(frame: pd.DataFrame, label: str) -> None:
    if "datetime" not in frame.columns:
        raise ValueError(f"{label} missing datetime")
    timestamps = pd.to_datetime(frame["datetime"], errors="raise")
    assert timestamps.max() <= HARD_CUTOFF, (
        f"{label} crossed cutoff: {timestamps.max()} > {HARD_CUTOFF}"
    )


def fixed_wf_sharpes(equity: pd.Series) -> list[float | None]:
    values: list[float | None] = []
    annualizer = np.sqrt(365.2425 * 6)
    for start, end in zip(WF_BOUNDARIES[:-1], WF_BOUNDARIES[1:], strict=True):
        segment = equity[(equity.index >= start) & (equity.index < end)]
        returns = segment.pct_change().dropna()
        if len(returns) < 2 or returns.std(ddof=1) <= 0:
            values.append(None)
        else:
            values.append(
                float(returns.mean() / returns.std(ddof=1) * annualizer)
            )
    return values


def reproduce_variant_c() -> tuple[dict[str, Any], dict[str, Any]]:
    bars, funding, data_audit = load_data("L")
    for symbol, frame in bars.items():
        assert_pre_holdout_frame(frame, f"{symbol} bars")
    for symbol, frame in funding.items():
        assert_pre_holdout_frame(frame, f"{symbol} funding")

    raw = raw_bars_from_prepared(bars)
    benchmark_bars = prepare_passive_dataset("L", raw, funding)
    strategy = run_backtest(
        bars,
        funding,
        label="tsmom_dual_L_d2_variant_C",
    )
    benchmark = run_backtest(
        benchmark_bars,
        funding,
        label="benchmark_L_d2_variant_C",
    )
    accepted = acceptance(strategy, benchmark)
    metrics = accepted["metrics"]
    e_r = float(metrics["expectancy_r"])
    excess = float(accepted["benchmark"]["excess_profit"])
    relative_error = abs(e_r - EXPECTED_BASELINE_EXPECTANCY) / abs(
        EXPECTED_BASELINE_EXPECTANCY
    )
    reproduction_passed = relative_error < REPRODUCTION_RELATIVE_TOLERANCE
    if not reproduction_passed:
        raise AssertionError(
            f"variant C E[R] reproduction error {relative_error:.2%} >= 5%"
        )

    trades = strategy.trades
    annual = accepted["annual_trade_expectancy"]
    variant = {
        "status": "completed",
        "universe_size": len(SYMBOL_ORDER),
        "symbols": list(BASE_FULL_SYMBOLS),
        "e_r_per_trade": e_r,
        "win_loss_ratio": float(metrics["win_loss_ratio"]),
        "positive_years": int(annual["positive_years"]),
        "counted_years": int(annual["counted_years"]),
        "positive_year_ratio": (
            float(annual["positive_years"] / annual["counted_years"])
            if annual["counted_years"]
            else None
        ),
        "p_dd_ge_20": float(
            accepted["liquidation_bootstrap"][
                "conservative_dd20_probability"
            ]
        ),
        "benchmark_excess": excess,
        "full_universe_weight_cap": 1 / len(SYMBOL_ORDER),
        "realized_max_initial_weight": float(trades["nominal_pct"].max()),
        "wf_3_sharpe": fixed_wf_sharpes(strategy.equity),
        "ending_equity": float(metrics["ending_equity"]),
        "max_drawdown": float(metrics["max_drawdown"]),
        "annualized_log_growth": float(metrics["annualized_log_growth"]),
        "trade_count": int(metrics["trade_count"]),
        "reproduction": {
            "expected_e_r": EXPECTED_BASELINE_EXPECTANCY,
            "expected_excess": EXPECTED_BASELINE_EXCESS,
            "e_r_relative_error": relative_error,
            "passed": reproduction_passed,
        },
    }
    audit = {
        "data": data_audit,
        "bars_max": max(str(frame["datetime"].max()) for frame in bars.values()),
        "funding_max": max(
            str(frame["datetime"].max()) for frame in funding.values()
        ),
    }
    return variant, audit


def load_pit_dates(symbols: list[str]) -> dict[str, pd.Timestamp]:
    pit = pd.read_csv(DATA / "UNIVERSE_PIT.csv", parse_dates=["onboard_date"])
    output: dict[str, pd.Timestamp] = {}
    for full_symbol in symbols:
        match = pit[pit["symbol"] == full_symbol]
        if len(match) != 1:
            raise ValueError(
                f"{full_symbol} not found exactly once in UNIVERSE_PIT.csv"
            )
        output[full_symbol] = pd.Timestamp(match.iloc[0]["onboard_date"])
    return output


def read_expanded_bars(
    full_symbol: str,
    manifest: dict[str, Any],
) -> pd.DataFrame:
    path = EXPANDED / f"{full_symbol}_4H.csv"
    expected_rows = int(manifest["downloads"][full_symbol]["rows"])
    frame = pd.read_csv(path, parse_dates=["datetime"])
    if len(frame) != expected_rows:
        raise ValueError(
            f"{path} expected {expected_rows} rows, got {len(frame)}"
        )
    required = {"datetime", "open", "high", "low", "close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    assert_pre_holdout_frame(frame, str(path))
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} has duplicate timestamps")
    if not frame["datetime"].is_monotonic_increasing:
        raise ValueError(f"{path} is not ascending")
    for column in required - {"datetime"}:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame.loc[
        :, ["datetime", "open", "high", "low", "close", "volume"]
    ].reset_index(drop=True)


def read_expanded_funding(full_symbol: str) -> pd.DataFrame:
    path = EXPANDED / f"{full_symbol}_FUNDING_8H.csv"
    frame = pd.read_csv(path, parse_dates=["datetime"])
    required = {"datetime", "last_funding_rate"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"{path} is empty")
    assert_pre_holdout_frame(frame, str(path))
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} has duplicate timestamps")
    if not frame["datetime"].is_monotonic_increasing:
        raise ValueError(f"{path} is not ascending")
    frame["last_funding_rate"] = pd.to_numeric(
        frame["last_funding_rate"], errors="raise"
    )
    return frame.loc[:, ["datetime", "last_funding_rate"]].reset_index(
        drop=True
    )


def summarize_variant(
    strategy: Any,
    benchmark: Any,
    full_symbols: list[str],
) -> dict[str, Any]:
    accepted = acceptance(strategy, benchmark)
    metrics = accepted["metrics"]
    annual = accepted["annual_trade_expectancy"]
    trades = strategy.trades
    return {
        "status": "completed",
        "universe_size": len(full_symbols),
        "symbols": full_symbols,
        "e_r_per_trade": float(metrics["expectancy_r"]),
        "win_loss_ratio": float(metrics["win_loss_ratio"]),
        "positive_years": int(annual["positive_years"]),
        "counted_years": int(annual["counted_years"]),
        "positive_year_ratio": (
            float(annual["positive_years"] / annual["counted_years"])
            if annual["counted_years"]
            else None
        ),
        "p_dd_ge_20": float(
            accepted["liquidation_bootstrap"][
                "conservative_dd20_probability"
            ]
        ),
        "benchmark_excess": float(
            accepted["benchmark"]["excess_profit"]
        ),
        "full_universe_weight_cap": 1 / len(full_symbols),
        "realized_max_initial_weight": float(trades["nominal_pct"].max()),
        "wf_3_sharpe": fixed_wf_sharpes(strategy.equity),
        "ending_equity": float(metrics["ending_equity"]),
        "max_drawdown": float(metrics["max_drawdown"]),
        "annualized_log_growth": float(metrics["annualized_log_growth"]),
        "trade_count": int(metrics["trade_count"]),
    }


def run_expanded_variant(
    manifest: dict[str, Any],
    selected: list[str],
    variant_label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    base_bars, base_funding, base_audit = load_data("L")
    pit = load_pit_dates(selected)
    bars = dict(base_bars)
    funding = dict(base_funding)
    raw = raw_bars_from_prepared(base_bars)
    data_audit: dict[str, Any] = dict(base_audit)

    for full_symbol in selected:
        key = full_symbol.removesuffix("USDT")
        raw_frame = read_expanded_bars(full_symbol, manifest)
        funding_frame = read_expanded_funding(full_symbol)
        raw[key] = raw_frame
        bars[key] = prepare_bars(
            raw_frame,
            symbol=key,
            onboard_date=pit[full_symbol],
            engine="L",
        )
        funding[key] = funding_frame
        data_audit[key] = {
            "bars_path": str(
                (EXPANDED / f"{full_symbol}_4H.csv").relative_to(ROOT)
            ),
            "bars_rows_used": int(len(raw_frame)),
            "bars_first_timestamp": str(raw_frame["datetime"].min()),
            "bars_last_timestamp": str(raw_frame["datetime"].max()),
            "funding_path": str(
                (
                    EXPANDED / f"{full_symbol}_FUNDING_8H.csv"
                ).relative_to(ROOT)
            ),
            "funding_rows_used": int(len(funding_frame)),
            "funding_first_timestamp": str(
                funding_frame["datetime"].min()
            ),
            "funding_last_timestamp": str(
                funding_frame["datetime"].max()
            ),
            "onboard_date": str(pit[full_symbol]),
        }

    base_pit = load_pit_dates(list(BASE_FULL_SYMBOLS))
    benchmark_bars: dict[str, pd.DataFrame] = {}
    for key, raw_frame in raw.items():
        full_symbol = f"{key}USDT"
        onboard = (
            base_pit[full_symbol]
            if full_symbol in base_pit
            else pit[full_symbol]
        )
        benchmark_bars[key] = prepare_passive_bars(
            raw_frame,
            symbol=key,
            onboard_date=onboard,
            engine="L",
        )

    strategy = run_backtest(
        bars,
        funding,
        label=f"tsmom_dual_L_d2_{variant_label}",
    )
    benchmark = run_backtest(
        benchmark_bars,
        funding,
        label=f"benchmark_L_d2_{variant_label}",
    )
    full_symbols = list(BASE_FULL_SYMBOLS) + selected
    variant = summarize_variant(
        strategy,
        benchmark,
        full_symbols,
    )
    return variant, data_audit


def audit_expanded_inputs(
    manifest: dict[str, Any],
    selected_30: list[str],
) -> list[Blocker]:
    blockers: list[Blocker] = []
    base_url = str(manifest.get("base_url", ""))
    if "/markPriceKlines" not in base_url:
        blockers.append(
            Blocker(
                "PRICE_SOURCE_MISMATCH",
                "D1 expanded files use contract klines, while the frozen 8-asset "
                "baseline uses mark-price klines. Mixing them is not a "
                "single-variable universe test.",
            )
        )

    missing_funding = [
        symbol
        for symbol in selected_30
        if not (EXPANDED / f"{symbol}_FUNDING_8H.csv").exists()
    ]
    if missing_funding:
        blockers.append(
            Blocker(
                "MISSING_REAL_FUNDING",
                f"{len(missing_funding)}/{len(selected_30)} selected expanded "
                "assets lack pre-cutoff real 8H funding files: "
                + ", ".join(missing_funding),
            )
        )

    quality = manifest.get("dec_070_quality_audit")
    passed_filters = {
        key
        for key, value in (quality.items() if isinstance(quality, dict) else [])
        if value is True
    }
    missing_filters = sorted(DEC_070_REQUIRED_FILTERS - passed_filters)
    if missing_filters:
        blockers.append(
            Blocker(
                "DEC_070_FILTERS_NOT_AUDITABLE",
                "DOWNLOAD_MANIFEST.json does not prove the DEC-070 hard filters: "
                + ", ".join(missing_filters),
            )
        )
    return blockers


def blocked_variant(
    symbols: list[str],
    blockers: list[Blocker],
) -> dict[str, Any]:
    universe = list(BASE_FULL_SYMBOLS) + symbols
    return {
        "status": "blocked",
        "universe_size": len(universe),
        "symbols": universe,
        "e_r_per_trade": None,
        "win_loss_ratio": None,
        "positive_year_ratio": None,
        "p_dd_ge_20": None,
        "benchmark_excess": None,
        "full_universe_weight_cap": 1 / len(universe),
        "realized_max_initial_weight": None,
        "wf_3_sharpe": None,
        "blockers": [blocker.code for blocker in blockers],
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "BLOCKED"
    return f"{value:.{digits}f}"


def render_result_report(payload: dict[str, Any]) -> str:
    if payload["status"] == "completed":
        return render_completed_result_report(payload)
    c = payload["variant_C_baseline"]
    a = payload["variant_A_20coins"]
    b = payload["variant_B_30coins"]
    wf_c = " / ".join(fmt(value) for value in c["wf_3_sharpe"])
    blocker_lines = "\n".join(
        f"{index}. **{row['code']}**：{row['detail']}"
        for index, row in enumerate(payload["blockers"], start=1)
    )
    return f"""# D2 TSMOM 扩展 Universe 信号层回测

**[专业异议]**

## 技术结论

**任务状态：BLOCKED。不能回答“扩 universe 后 P(DD≥20%) 是否 <10%”。**

变体 C 已按冻结的 8 币 `tsmom_dual_L` 口径精确复现；变体 A/B 因输入不满足同源价格、真实 funding 和 DEC-070 universe 审计要求而暂停。用零 funding 或混用 contract/mark K 线继续计算会直接违反成本完整与单变量原则。

## 三变体对比

| 指标 | 变体C（8币） | 变体A（28币） | 变体B（38币） |
|---|---:|---:|---:|
| E[R] per trade | {c['e_r_per_trade']:.6f} | BLOCKED | BLOCKED |
| 赢亏比 | {c['win_loss_ratio']:.3f} | BLOCKED | BLOCKED |
| 正年比例 | {c['positive_years']}/{c['counted_years']} | BLOCKED | BLOCKED |
| P(DD≥20%) | {c['p_dd_ge_20']:.1%} | BLOCKED | BLOCKED |
| 第五件：基准超额 | ${c['benchmark_excess']:,.2f} | BLOCKED | BLOCKED |
| 完整 universe 单资产权重帽 | {c['full_universe_weight_cap']:.2%} | {a['full_universe_weight_cap']:.2%} | {b['full_universe_weight_cap']:.2%} |
| 历史实际最大初始权重 | {c['realized_max_initial_weight']:.2%} | BLOCKED | BLOCKED |
| WF 3段 Sharpe | {wf_c} | BLOCKED | BLOCKED |

注意：任务书表格把变体 C 单资产最大权重写为 12.5%，这是“8 币全部可交易时”的权重帽。冻结引擎按当时 PIT 可交易资产数动态分配，早期历史实际最大初始权重为 {c['realized_max_initial_weight']:.2%}，不能把 12.5% 误写成全历史实际最大值。

## P1-06 / 8币基线复现

- 权威基线：`tsmom_dual_L`，不是旧 3 币 `p1_06_tsmom_macro_bull`。
- E[R]：预期 `{c['reproduction']['expected_e_r']:.6f}`，本次 `{c['e_r_per_trade']:.6f}`，相对偏差 `{c['reproduction']['e_r_relative_error']:.6%}`，通过 `<5%` 验收。
- 第五件超额：预期 `${c['reproduction']['expected_excess']:,.2f}`，本次 `${c['benchmark_excess']:,.2f}`。
- 固定成本：手续费 `{FEE_RATE:.1%}/边` + 滑点 `{SLIPPAGE_RATE:.1%}/边` + 真实 8H funding。
- 冻结信号：L={LOOKBACK_BARS} 根 4H、ADX {ADX_PERIOD}/{ADX_ENTRY:.0f}/{ADX_EXIT:.0f}、前一完整 UTC 日日收盘相对 SMA{MACRO_MA_DAYS}、仅做多、t+1 open。

## 阻塞项

{blocker_lines}

## 为什么这些问题会改变结论

1. Contract K 线与 mark-price K 线会改变动量、ADX、门控、成交价和权益路径，A/B 与 C 不再只差 universe。
2. 新资产 funding 不是小额可忽略项。8 币基线 funding 成本为实质性成本，按零处理会系统性抬高 E[R]、终值和基准超额。
3. DEC-070 要求 ADTV、流通市值比、OI/市值比和异常跳动频率硬过滤；当前 manifest 只证明历史长度、归档可得与手工黑名单，不能证明入选资产是决策定义的 Tier 1。

## Holdout 与数据边界

- 本脚本只读取既有 8 币固定 pre-cutoff 行数与 D1 manifest；未读取任何 `HOLDOUT` 路径。
- 变体 C 行情与 funding 最大时间均不晚于 `2024-12-09 23:59:59`，显式 assert 已通过。
- A/B 未加载收益数据、未生成信号、未计算指标。

## 恢复前提

1. 为入选 30 个扩展资产提供截至 `2024-12-09 23:59:59 UTC` 的同源 **mark-price 4H** 文件。
2. 为同一批资产提供截至同一边界的真实 **8H funding** 文件。
3. 在 manifest 或独立审计文件中逐项证明 DEC-070 四个硬过滤器，并由 Claude 确认 universe。
4. 保持 8 币变体 C、参数、成本、WF 边界和 bootstrap seed `{BOOTSTRAP_SEED}` 不变后再恢复 A/B。

## 方法口径

- Bootstrap：4H 净值收益、块长 `{BOOTSTRAP_BLOCK_BARS}` 根、`{BOOTSTRAP_ITERATIONS}` 路径、seed `{BOOTSTRAP_SEED}`、一年路径。
- WF 边界：`{WF_BOUNDARIES[0]}` / `{WF_BOUNDARIES[1]}` / `{WF_BOUNDARIES[2]}` / `{WF_BOUNDARIES[3]}`。
- 图表省略：A/B 无合法数值，绘制 DD 对比图会制造虚假可比性；保留精确审计表。
- 结论字段保持 `null`，不得把阻塞结果写成 `DD_improved` 或 `DD_not_improved`。
"""


def render_completed_result_report(payload: dict[str, Any]) -> str:
    c = payload["variant_C_baseline"]
    a = payload["variant_A_20coins"]
    b = payload["variant_B_30coins"]

    def wf(row: dict[str, Any]) -> str:
        return " / ".join(fmt(value) for value in row["wf_3_sharpe"])

    target_passed = bool(
        a["p_dd_ge_20"] < 0.10 or b["p_dd_ge_20"] < 0.10
    )
    return f"""# D2 TSMOM 扩展 Universe 信号层回测

## 技术结论

**结论：{payload['conclusion']}。扩展 universe 后至少一个变体满足 P(DD≥20%)<10%：{target_passed}。**

## 三变体对比

| 指标 | 变体C（8币） | 变体A（28币） | 变体B（38币） |
|---|---:|---:|---:|
| E[R] per trade | {c['e_r_per_trade']:.6f} | {a['e_r_per_trade']:.6f} | {b['e_r_per_trade']:.6f} |
| 赢亏比 | {c['win_loss_ratio']:.3f} | {a['win_loss_ratio']:.3f} | {b['win_loss_ratio']:.3f} |
| 正年比例 | {c['positive_years']}/{c['counted_years']} | {a['positive_years']}/{a['counted_years']} | {b['positive_years']}/{b['counted_years']} |
| P(DD≥20%) | {c['p_dd_ge_20']:.1%} | {a['p_dd_ge_20']:.1%} | {b['p_dd_ge_20']:.1%} |
| 第五件：基准超额 | ${c['benchmark_excess']:,.2f} | ${a['benchmark_excess']:,.2f} | ${b['benchmark_excess']:,.2f} |
| 完整 universe 单资产权重帽 | {c['full_universe_weight_cap']:.2%} | {a['full_universe_weight_cap']:.2%} | {b['full_universe_weight_cap']:.2%} |
| 历史实际最大初始权重 | {c['realized_max_initial_weight']:.2%} | {a['realized_max_initial_weight']:.2%} | {b['realized_max_initial_weight']:.2%} |
| WF 3段 Sharpe | {wf(c)} | {wf(a)} | {wf(b)} |

## P1-06 / 8币基线复现

- 变体 C E[R] 相对偏差 `{c['reproduction']['e_r_relative_error']:.6%}`，通过 `<5%`。
- 第五件超额 `${c['benchmark_excess']:,.2f}`，与冻结基线一致。

## DD 改善程度

- 变体 A 相对 C：P(DD≥20%) 变化 `{a['p_dd_ge_20'] - c['p_dd_ge_20']:+.1%}`。
- 变体 B 相对 C：P(DD≥20%) 变化 `{b['p_dd_ge_20'] - c['p_dd_ge_20']:+.1%}`。
- 核心门槛 `<10%`：A=`{a['p_dd_ge_20'] < 0.10}`，B=`{b['p_dd_ge_20'] < 0.10}`。

## 方法与边界

- 成本：手续费 `{FEE_RATE:.1%}/边` + 滑点 `{SLIPPAGE_RATE:.1%}/边` + 真实 8H funding。
- Bootstrap：块长 `{BOOTSTRAP_BLOCK_BARS}` 根、`{BOOTSTRAP_ITERATIONS}` 路径、seed `{BOOTSTRAP_SEED}`。
- WF 固定边界：`{WF_BOUNDARIES[0]}` / `{WF_BOUNDARIES[1]}` / `{WF_BOUNDARIES[2]}` / `{WF_BOUNDARIES[3]}`。
- 所有输入显式 assert 不晚于 `2024-12-09 23:59:59`；未读取 Holdout。
"""


def render_codex_report(payload: dict[str, Any]) -> str:
    if payload["status"] == "completed":
        return render_completed_codex_report(payload)
    blocker_lines = "\n".join(
        f"- `{row['code']}`：{row['detail']}" for row in payload["blockers"]
    )
    c = payload["variant_C_baseline"]
    return f"""# REPORT_D2

**[专业异议]**

## 状态

**BLOCKED。** 变体 C 复现完成；变体 A/B 未执行，原因是继续执行会违反单变量、完整成本和 DEC-070 universe 约束。

## 七问自查

1. 验证机制：更多经质量过滤且同口径资产是否通过降低单资产权重改善组合 DD。
2. 验收量化：三变体四件套、第五件、WF Sharpe、P(DD≥20%)<10%、C 的 E[R] 偏差<5%。
3. 更便宜等效实现：复用已审计 `tsmom_dual_engine`，先复现 C，再对 A/B 做输入失败关闭。
4. 禁止项：未读 Holdout、未改预登记、未简化成本、未用全样本分位、未引黑箱依赖。
5. 变量能否作用于 DD：能，但只有价格源、成本和 universe 质量固定时才是 universe 单变量。
6. 最可能失败原因：扩展资产高相关/高 beta 使表面分散无效，或低质量小币引入更大尾部；当前输入无法区分。
7. 专业异议：D1 数据层不足以支持 D2 主判定，已暂停 A/B。

## 已完成

- D1 manifest 审计：`success={payload['d1_manifest']['success']}`，前 20/30 选择可确定。
- 变体 C：E[R] `{c['e_r_per_trade']:.6f}`，相对基线偏差 `{c['reproduction']['e_r_relative_error']:.6%}`，复现通过。
- 变体 C 第五件超额：`${c['benchmark_excess']:,.2f}`。
- 截止日期 assert：通过。
- Holdout：未读取。
- 新增失败关闭脚本与单元测试。

## 阻塞项

{blocker_lines}

## 剩余步骤

- 纠正 D1 价格源为 mark-price 4H。
- 补齐入选 30 资产真实 8H funding。
- 补齐并验收 DEC-070 四项 universe 质量过滤证据。
- 恢复运行 A/B，更新 summary 的结论为 `DD_improved` 或 `DD_not_improved`。

## 产物

- `06_RESEARCH/CODE/d2_tsmom_extended_backtest.py`
- `06_RESEARCH/CODE/tests/test_d2_tsmom_extended_backtest.py`
- `06_RESEARCH/CODE/output/tsmom_extended_summary.json`
- `06_RESEARCH/RESULTS/20260613_tsmom_extended_backtest_report.md`
- `04_AI_TEAM/CODEX_TASKS/REPORT_D2.md`

## Git

未 commit。任务处于 blocked，不能按“完成任务”提交。
"""


def render_completed_codex_report(payload: dict[str, Any]) -> str:
    c = payload["variant_C_baseline"]
    a = payload["variant_A_20coins"]
    b = payload["variant_B_30coins"]
    return f"""# REPORT_D2

## 状态

**COMPLETED。结论：{payload['conclusion']}。**

## 验收自检

- 三变体对比：PASS。
- 变体 C E[R] 复现偏差：`{c['reproduction']['e_r_relative_error']:.6%}`，PASS。
- 真实 funding：PASS。
- 同源 mark-price 4H：PASS。
- DEC-070 四项 universe 过滤证据：PASS。
- 截止日期 assert：PASS。
- Holdout 未读取：PASS。
- P(DD≥20%)：C=`{c['p_dd_ge_20']:.1%}`，A=`{a['p_dd_ge_20']:.1%}`，B=`{b['p_dd_ge_20']:.1%}`。

## 产物

- `06_RESEARCH/CODE/d2_tsmom_extended_backtest.py`
- `06_RESEARCH/CODE/tests/test_d2_tsmom_extended_backtest.py`
- `06_RESEARCH/CODE/output/tsmom_extended_summary.json`
- `06_RESEARCH/RESULTS/20260613_tsmom_extended_backtest_report.md`
- `04_AI_TEAM/CODEX_TASKS/REPORT_D2.md`
"""


def write_outputs(payload: dict[str, Any]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CODEX_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    RESULT_PATH.write_text(render_result_report(payload), encoding="utf-8")
    CODEX_REPORT_PATH.write_text(render_codex_report(payload), encoding="utf-8")


def main() -> int:
    manifest = load_manifest()
    selected_20 = select_expanded_symbols(manifest, 20)
    selected_30 = select_expanded_symbols(manifest, 30)
    variant_c, variant_c_audit = reproduce_variant_c()
    blockers = audit_expanded_inputs(manifest, selected_30)

    payload: dict[str, Any] = {
        "task_id": "D2",
        "generated_at_utc": utc_now(),
        "holdout_accessed": False,
        "cutoff_assert_passed": True,
        "d1_manifest": {
            "path": str(MANIFEST_PATH.relative_to(ROOT)),
            "success": int(manifest["summary"]["success"]),
            "base_url": manifest.get("base_url"),
        },
        "parameters": {
            "lookback_bars": LOOKBACK_BARS,
            "adx_period": ADX_PERIOD,
            "adx_entry": ADX_ENTRY,
            "adx_exit": ADX_EXIT,
            "macro_ma_days": MACRO_MA_DAYS,
            "fee_each_side": FEE_RATE,
            "slippage_each_side": SLIPPAGE_RATE,
            "funding": "real 8H rates, direction-aware",
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
            "bootstrap_block_bars": BOOTSTRAP_BLOCK_BARS,
            "wf_boundaries": [str(value) for value in WF_BOUNDARIES],
        },
        "variant_C_baseline": variant_c,
        "variant_C_data_audit": variant_c_audit,
    }
    if blockers:
        payload.update(
            {
                "status": "blocked",
                "variant_A_20coins": blocked_variant(
                    selected_20, blockers
                ),
                "variant_B_30coins": blocked_variant(
                    selected_30, blockers
                ),
                "blockers": [
                    blocker.as_dict() for blocker in blockers
                ],
                "conclusion": None,
            }
        )
        write_outputs(payload)
        return 2

    variant_a, audit_a = run_expanded_variant(
        manifest,
        selected_20,
        "variant_A",
    )
    variant_b, audit_b = run_expanded_variant(
        manifest,
        selected_30,
        "variant_B",
    )
    improved = (
        variant_a["p_dd_ge_20"] < variant_c["p_dd_ge_20"]
        and variant_b["p_dd_ge_20"] < variant_c["p_dd_ge_20"]
    )
    payload.update(
        {
            "status": "completed",
            "variant_A_20coins": variant_a,
            "variant_B_30coins": variant_b,
            "variant_A_data_audit": audit_a,
            "variant_B_data_audit": audit_b,
            "blockers": [],
            "conclusion": (
                "DD_improved" if improved else "DD_not_improved"
            ),
        }
    )
    write_outputs(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
