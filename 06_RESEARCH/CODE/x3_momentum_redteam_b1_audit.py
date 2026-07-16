#!/usr/bin/env python3
"""Reproducible red-team and B1 kill-card audit for P1-RES-038-B1.

Protocol choices are frozen in-code before looking at results:
- Data: 06_RESEARCH/DATA/FUTURES_EXPANDED/*_4H.csv only.
- Signal: trailing 30 calendar-day close-to-close return.
- Portfolio: top/bottom terciles, equal weighted, dollar neutral.
- Frequencies: daily and weekly are evaluated as pre-specified cost gates, not
  as a parameter search. No lookback/window/quantile optimization is performed.
- Costs: per-fill all-in alt execution costs of 0.15%, 0.20%, and 0.30%.

The script does not read Holdout paths and does not write under DATA.
"""

from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
OUTPUT_JSON = OUTPUT_DIR / "x3_momentum_redteam_b1_audit.json"
REPORT_PATH = ROOT / "04_AI_TEAM" / "CODEX_TASKS" / "REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md"
RESULT_PATH = ROOT / "06_RESEARCH" / "RESULTS" / "X3_MOMENTUM_REDTEAM_B1_20260622.md"

TASK_ID = "P1-RES-038-B1"
SEED = 20260622
LOOKBACK_DAYS = 30
MIN_UNIVERSE = 12
COST_CASES = {
    "maker_low_with_adverse_0_15pct": 0.0015,
    "protocol_base_0_20pct": 0.0020,
    "alt_taker_high_0_30pct": 0.0030,
}


def utc_now() -> str:
    return (
        dt.datetime.now(dt.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def pct(x: float | None, digits: int = 4) -> float | None:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return None
    return round(100.0 * float(x), digits)


def annual_factor(freq: str) -> int:
    return 365 if freq == "daily" else 52


def normal_two_sided_p(z: float) -> float:
    if not math.isfinite(z):
        return float("nan")
    return math.erfc(abs(z) / math.sqrt(2.0))


def load_daily_close() -> tuple[pd.DataFrame, list[dict[str, object]]]:
    frames = []
    inventory: list[dict[str, object]] = []
    for path in sorted(DATA_DIR.glob("*_4H.csv")):
        symbol = path.name.replace("_4H.csv", "")
        df = pd.read_csv(path, parse_dates=["datetime"])
        required = ["datetime", "open", "high", "low", "close", "volume"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{path} missing columns: {missing}")
        df = df.sort_values("datetime")
        series = df.set_index("datetime")["close"].astype(float)
        inventory.append(
            {
                "symbol": symbol,
                "rows": int(len(df)),
                "start": str(df["datetime"].iloc[0]),
                "end": str(df["datetime"].iloc[-1]),
                "close_na": int(df["close"].isna().sum()),
            }
        )
        daily = series.resample("1D").last().rename(symbol)
        frames.append(daily)
    if not frames:
        raise FileNotFoundError(f"No *_4H.csv files found in {DATA_DIR}")
    closes = pd.concat(frames, axis=1, sort=True).sort_index()
    closes = closes.ffill(limit=1)
    return closes, inventory


def rebalance_index(closes: pd.DataFrame, freq: str) -> pd.DatetimeIndex:
    valid_counts = closes.notna().sum(axis=1)
    dates = closes.index[valid_counts >= MIN_UNIVERSE]
    if freq == "daily":
        return dates
    if freq == "weekly":
        weekly = closes.loc[dates].resample("W-MON").last().index
        return weekly.intersection(closes.index)
    raise ValueError(freq)


def group_weights(signal: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    signal = signal.dropna()
    if len(signal) < MIN_UNIVERSE:
        empty = pd.Series(dtype=float)
        return empty, empty, empty
    k = len(signal) // 3
    ordered = signal.sort_values(kind="mergesort")
    bottom = ordered.index[:k]
    top = ordered.index[-k:]
    middle = ordered.index[k:-k]
    long_w = pd.Series(1.0 / k, index=top)
    short_w = pd.Series(-1.0 / k, index=bottom)
    middle_w = pd.Series(1.0 / len(middle), index=middle) if len(middle) else pd.Series(dtype=float)
    return long_w, short_w, middle_w


def align_weights(weights: pd.Series, columns: Iterable[str]) -> pd.Series:
    out = pd.Series(0.0, index=list(columns))
    if len(weights):
        out.loc[weights.index] = weights
    return out


def run_strategy(closes: pd.DataFrame, freq: str, symbols: list[str] | None = None) -> pd.DataFrame:
    if symbols is not None:
        closes = closes[symbols]
    idx = rebalance_index(closes, freq)
    step = 1 if freq == "daily" else 7
    rows = []
    prev_long = pd.Series(0.0, index=closes.columns)
    prev_short = pd.Series(0.0, index=closes.columns)
    for date in idx:
        loc = closes.index.get_loc(date)
        lookback_loc = loc - LOOKBACK_DAYS
        future_loc = loc + step
        if lookback_loc < 0 or future_loc >= len(closes.index):
            continue
        current = closes.iloc[loc]
        past = closes.iloc[lookback_loc]
        future = closes.iloc[future_loc]
        signal = (current / past - 1.0).replace([np.inf, -np.inf], np.nan).dropna()
        future_ret = (future / current - 1.0).replace([np.inf, -np.inf], np.nan)
        signal = signal[future_ret.reindex(signal.index).notna()]
        long_w, short_w, middle_w = group_weights(signal)
        if len(long_w) == 0:
            continue
        cols = list(closes.columns)
        long_vec = align_weights(long_w, cols)
        short_vec = align_weights(short_w, cols)
        gross_vec = long_vec + short_vec
        future_ret = future_ret.reindex(cols).fillna(0.0)
        long_ret = float((long_vec * future_ret).sum())
        short_leg_ret = float((-short_vec * future_ret).sum())
        raw = long_ret - short_leg_ret
        middle_ret = float((align_weights(middle_w, cols) * future_ret).sum()) if len(middle_w) else float("nan")
        ew_ret = float(future_ret[signal.index].mean())
        long_turnover = float((long_vec - prev_long).abs().sum())
        short_turnover = float((short_vec - prev_short).abs().sum())
        total_turnover = long_turnover + short_turnover
        rows.append(
            {
                "date": date,
                "raw_return": raw,
                "top_return": long_ret,
                "middle_return": middle_ret,
                "bottom_return": short_leg_ret,
                "ew_alt_return": ew_ret,
                "long_turnover": long_turnover,
                "short_turnover": short_turnover,
                "total_turnover": total_turnover,
                "universe_n": int(len(signal)),
                "top_n": int(len(long_w)),
                "bottom_n": int(len(short_w)),
                "top_symbols": ",".join(long_w.index),
                "bottom_symbols": ",".join(short_w.index),
            }
        )
        prev_long = long_vec
        prev_short = short_vec
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.set_index("date")
    return out


def moving_block_bootstrap_mean(values: np.ndarray, block_len: int, samples: int = 5000) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    n = len(values)
    if n == 0:
        return {"ci_low": float("nan"), "ci_high": float("nan"), "p_mean_le_0": float("nan")}
    rng = np.random.default_rng(SEED + block_len + n)
    starts = np.arange(0, max(1, n - block_len + 1))
    means = []
    blocks_needed = int(math.ceil(n / block_len))
    for _ in range(samples):
        sample = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            sample.extend(values[start : start + block_len])
        means.append(float(np.mean(sample[:n])))
    boot = np.array(means)
    return {
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
        "p_mean_le_0": float(np.mean(boot <= 0.0)),
    }


def bootstrap_drawdown_probabilities(
    returns: pd.Series,
    freq: str,
    block_len: int,
    samples: int = 5000,
) -> dict[str, object]:
    """Estimate one-year path drawdown probabilities via moving-block bootstrap."""

    values = returns.dropna().to_numpy(dtype=float)
    n = len(values)
    if n == 0:
        return {
            "seed": SEED,
            "iterations": samples,
            "block_periods": block_len,
            "year_periods": annual_factor(freq),
            "standard_dd35_probability": None,
            "conservative_dd20_probability": None,
            "ruin_dd100_probability": None,
        }
    rng = np.random.default_rng(SEED + 1000 + n + block_len)
    starts = np.arange(0, max(1, n - block_len + 1))
    year_periods = annual_factor(freq)
    blocks_needed = int(math.ceil(year_periods / block_len))
    dd35 = 0
    dd20 = 0
    ruin = 0
    for _ in range(samples):
        sampled = []
        for start in rng.choice(starts, size=blocks_needed, replace=True):
            sampled.extend(values[start : start + block_len])
        path = np.array(sampled[:year_periods], dtype=float)
        equity = np.cumprod(1.0 + path)
        drawdown = equity / np.maximum.accumulate(equity) - 1.0
        worst = float(drawdown.min())
        dd35 += int(worst <= -0.35)
        dd20 += int(worst <= -0.20)
        ruin += int(np.any(equity <= 0.0) or worst <= -1.0)
    return {
        "seed": SEED,
        "iterations": samples,
        "block_periods": block_len,
        "year_periods": year_periods,
        "standard_dd35_probability": dd35 / samples,
        "conservative_dd20_probability": dd20 / samples,
        "ruin_dd100_probability": ruin / samples,
    }


def protocol_metrics(returns: pd.Series, freq: str, block_len: int) -> dict[str, object]:
    values = returns.dropna().astype(float)
    wins = values[values > 0.0]
    losses = values[values < 0.0]
    average_win = float(wins.mean()) if len(wins) else None
    average_loss_abs = float(-losses.mean()) if len(losses) else None
    win_loss = (
        average_win / average_loss_abs
        if average_win is not None and average_loss_abs not in (None, 0.0)
        else None
    )
    yearly = []
    for year, group in values.groupby(values.index.year):
        mean = float(group.mean())
        yearly.append(
            {
                "year": int(year),
                "periods": int(len(group)),
                "mean_pct": pct(mean),
                "positive_expectancy": bool(mean > 0.0),
            }
        )
    positive_years = sum(1 for row in yearly if row["positive_expectancy"])
    ann_log = float(np.log1p(values).mean() * annual_factor(freq)) if len(values) else float("nan")
    return {
        "period_mean_pct": pct(float(values.mean())) if len(values) else None,
        "expectancy_positive": bool(len(values) and float(values.mean()) > 0.0),
        "average_win_pct": pct(average_win),
        "average_loss_abs_pct": pct(average_loss_abs),
        "win_loss_ratio": win_loss,
        "win_loss_ratio_ge_1_5": bool(win_loss is not None and win_loss >= 1.5),
        "drawdown_bootstrap": bootstrap_drawdown_probabilities(values, freq, block_len),
        "annualized_log_growth_pct": pct(ann_log),
        "annualized_log_growth_positive": bool(math.isfinite(ann_log) and ann_log > 0.0),
        "yearly": yearly,
        "positive_years": int(positive_years),
        "majority_years_positive": bool(len(yearly) and positive_years > len(yearly) / 2.0),
    }


def summarize_returns(df: pd.DataFrame, freq: str) -> dict[str, object]:
    af = annual_factor(freq)
    raw = df["raw_return"].astype(float)
    n = int(raw.count())
    mean = float(raw.mean())
    std = float(raw.std(ddof=1))
    se = std / math.sqrt(n) if n > 1 else float("nan")
    z = mean / se if se and math.isfinite(se) and se > 0 else float("nan")
    base_cost = COST_CASES["protocol_base_0_20pct"]
    block = 5 if freq == "daily" else 4
    boot = moving_block_bootstrap_mean(raw.to_numpy(), block)
    top = float(df["top_return"].mean())
    middle = float(df["middle_return"].mean())
    bottom = float(df["bottom_return"].mean())
    monotonic = bool(bottom < middle < top)
    out: dict[str, object] = {
        "periods": n,
        "start": str(df.index.min().date()) if n else None,
        "end": str(df.index.max().date()) if n else None,
        "mean_raw": mean,
        "mean_raw_pct": pct(mean),
        "std_raw": std,
        "t_stat_normal": z,
        "p_value_normal_approx": normal_two_sided_p(z),
        "bootstrap": boot,
        "bootstrap_ci_pct": [pct(boot["ci_low"]), pct(boot["ci_high"])],
        "mde_95_period_pct": pct(1.96 * se if math.isfinite(se) else float("nan")),
        "top_mean_pct": pct(top),
        "middle_mean_pct": pct(middle),
        "bottom_mean_pct": pct(bottom),
        "monotonic_bottom_middle_top": monotonic,
        "avg_total_turnover": float(df["total_turnover"].mean()),
        "avg_total_turnover_pct": pct(float(df["total_turnover"].mean())),
        "break_even_cost_per_fill": float(mean / df["total_turnover"].mean()) if df["total_turnover"].mean() > 0 else float("nan"),
        "break_even_cost_per_fill_pct": pct(float(mean / df["total_turnover"].mean())) if df["total_turnover"].mean() > 0 else None,
        "annualized_raw_log_growth": float(np.log1p(raw).mean() * af),
        "annualized_raw_log_growth_pct": pct(float(np.log1p(raw).mean() * af)),
        "ew_alt_period_mean_pct": pct(float(df["ew_alt_return"].mean())),
        "ew_alt_annualized_log_growth": float(np.log1p(df["ew_alt_return"]).mean() * af),
        "ew_alt_annualized_log_growth_pct": pct(float(np.log1p(df["ew_alt_return"]).mean() * af)),
    }
    costs = {}
    for name, per_fill in COST_CASES.items():
        net = raw - df["total_turnover"] * per_fill
        costs[name] = {
            "per_fill_cost_pct": pct(per_fill),
            "mean_cost_period_pct": pct(float((df["total_turnover"] * per_fill).mean())),
            "mean_net_period_pct": pct(float(net.mean())),
            "annualized_net_log_growth_pct": pct(float(np.log1p(net).mean() * af)),
            "positive_net_mean": bool(float(net.mean()) > 0.0),
        }
    out["cost_cases"] = costs
    yearly = []
    for year, g in df.groupby(df.index.year):
        net = g["raw_return"] - g["total_turnover"] * base_cost
        yearly.append(
            {
                "year": int(year),
                "periods": int(len(g)),
                "raw_mean_pct": pct(float(g["raw_return"].mean())),
                "base_net_mean_pct": pct(float(net.mean())),
                "base_net_positive": bool(float(net.mean()) > 0.0),
            }
        )
    out["yearly_base_cost"] = yearly
    out["positive_years_base_cost"] = int(sum(1 for r in yearly if r["base_net_positive"]))
    out["majority_years_positive_base_cost"] = bool(out["positive_years_base_cost"] > len(yearly) / 2.0)
    base_net = raw - df["total_turnover"] * base_cost
    out["protocol_v1_3_base_cost"] = protocol_metrics(base_net, freq, block)
    return out


def tsmom_series(closes: pd.DataFrame, freq: str) -> pd.Series:
    idx = rebalance_index(closes, freq)
    step = 1 if freq == "daily" else 7
    rows = []
    for date in idx:
        loc = closes.index.get_loc(date)
        lookback_loc = loc - LOOKBACK_DAYS
        future_loc = loc + step
        if lookback_loc < 0 or future_loc >= len(closes.index):
            continue
        current = closes.iloc[loc]
        past = closes.iloc[lookback_loc]
        future = closes.iloc[future_loc]
        signal = (current / past - 1.0).replace([np.inf, -np.inf], np.nan)
        future_ret = (future / current - 1.0).replace([np.inf, -np.inf], np.nan)
        valid = signal.notna() & future_ret.notna()
        if valid.sum() < MIN_UNIVERSE:
            continue
        signs = np.sign(signal[valid])
        if signs.abs().sum() == 0:
            val = 0.0
        else:
            val = float((signs * future_ret[valid]).sum() / signs.abs().sum())
        rows.append((date, val))
    return pd.Series(dict(rows)).sort_index()


def orthogonality(df: pd.DataFrame, closes: pd.DataFrame, freq: str) -> dict[str, object]:
    ts = tsmom_series(closes, freq)
    both = pd.concat([df["raw_return"].rename("cs"), ts.rename("tsmom")], axis=1).dropna()
    if len(both) < 3:
        return {"periods": int(len(both)), "correlation": None}
    corr = float(both["cs"].corr(both["tsmom"]))
    beta = float(np.cov(both["cs"], both["tsmom"], ddof=1)[0, 1] / np.var(both["tsmom"], ddof=1))
    residual = both["cs"] - beta * both["tsmom"]
    return {
        "periods": int(len(both)),
        "correlation": corr,
        "beta_to_tsmom": beta,
        "cs_mean_pct": pct(float(both["cs"].mean())),
        "tsmom_mean_pct": pct(float(both["tsmom"].mean())),
        "residual_mean_pct": pct(float(residual.mean())),
        "abs_corr_gt_0_70": bool(abs(corr) > 0.70),
    }


def terminal_returns(closes: pd.DataFrame) -> pd.Series:
    vals = {}
    for col in closes.columns:
        s = closes[col].dropna()
        vals[col] = float(s.iloc[-1] / s.iloc[0] - 1.0) if len(s) else float("nan")
    return pd.Series(vals).sort_values()


def survivorship_stress(closes: pd.DataFrame, freq: str, baseline_mean: float) -> dict[str, object]:
    terminal = terminal_returns(closes)
    n_remove = max(1, int(round(len(terminal) * 0.20)))
    top_winners = terminal.tail(n_remove).index.tolist()
    bottom_losers = terminal.head(n_remove).index.tolist()
    common_start = max(closes[c].first_valid_index() for c in closes.columns)
    common_closes = closes.loc[common_start:]

    stresses = {}
    for name, symbols in {
        "drop_top_20pct_terminal_winners": [c for c in closes.columns if c not in top_winners],
        "drop_bottom_20pct_terminal_losers": [c for c in closes.columns if c not in bottom_losers],
        "common_sample_after_all_symbols_listed": list(common_closes.columns),
    }.items():
        src = common_closes if name == "common_sample_after_all_symbols_listed" else closes
        res = run_strategy(src, freq, symbols=symbols)
        mean = float(res["raw_return"].mean()) if not res.empty else float("nan")
        stresses[name] = {
            "periods": int(len(res)),
            "mean_raw_pct": pct(mean),
            "mean_change_vs_baseline_pct": pct(mean - baseline_mean),
            "edge_disappears": bool(math.isfinite(mean) and mean <= 0.0),
        }
    return {
        "terminal_return_bottom_20pct": {k: pct(v) for k, v in terminal.head(n_remove).items()},
        "terminal_return_top_20pct": {k: pct(v) for k, v in terminal.tail(n_remove).items()},
        "stress": stresses,
        "caveat": "The 35-file panel cannot add exchange listings that died before 2024-12; this is an in-panel stress proxy, not a full point-in-time delisting correction.",
    }


def asset_contribution(df: pd.DataFrame) -> list[dict[str, object]]:
    contrib = {sym: 0.0 for sym in sorted({s for row in df["top_symbols"] for s in row.split(",") if s})}
    for sym in sorted({s for row in df["bottom_symbols"] for s in row.split(",") if s}):
        contrib.setdefault(sym, 0.0)
    for date, row in df.iterrows():
        top = row["top_symbols"].split(",")
        bottom = row["bottom_symbols"].split(",")
        # Contribution accounting is sign exposure frequency, not exact PnL, because
        # exact per-asset returns are not retained in the compact period table.
        for sym in top:
            if sym:
                contrib[sym] += 1.0
        for sym in bottom:
            if sym:
                contrib[sym] -= 1.0
    ranked = sorted(contrib.items(), key=lambda kv: abs(kv[1]), reverse=True)
    return [{"symbol": k, "net_top_minus_bottom_selections": int(v)} for k, v in ranked[:10]]


def gate_verdicts(summary: dict[str, object], freq: str) -> dict[str, object]:
    base = summary["cost_cases"]["protocol_base_0_20pct"]  # type: ignore[index]
    high = summary["cost_cases"]["alt_taker_high_0_30pct"]  # type: ignore[index]
    cost_pass = bool(base["positive_net_mean"] and high["positive_net_mean"])  # type: ignore[index]
    mono_pass = bool(
        summary["monotonic_bottom_middle_top"]
        and summary["mean_raw"] > 0.0
        and summary["bootstrap"]["ci_low"] > 0.0  # type: ignore[index]
    )
    passive_pass = bool(
        base["annualized_net_log_growth_pct"] is not None  # type: ignore[index]
        and summary["ew_alt_annualized_log_growth_pct"] is not None
        and base["annualized_net_log_growth_pct"] > summary["ew_alt_annualized_log_growth_pct"]  # type: ignore[index]
    )
    return {
        "freq": freq,
        "gate1_cost_pass": cost_pass,
        "gate2_monotonic_significance_pass": mono_pass,
        "passive_benchmark_pass": passive_pass,
    }


def render_report(audit: dict[str, object]) -> str:
    daily = audit["frequencies"]["daily"]  # type: ignore[index]
    weekly = audit["frequencies"]["weekly"]  # type: ignore[index]
    chosen = weekly
    gates = chosen["gates"]  # type: ignore[index]
    surv = chosen["survivorship"]  # type: ignore[index]
    ortho = chosen["orthogonality"]  # type: ignore[index]
    base = chosen["summary"]["cost_cases"]["protocol_base_0_20pct"]  # type: ignore[index]
    high = chosen["summary"]["cost_cases"]["alt_taker_high_0_30pct"]  # type: ignore[index]
    protocol = chosen["summary"]["protocol_v1_3_base_cost"]  # type: ignore[index]
    dd = protocol["drawdown_bootstrap"]  # type: ignore[index]
    final = audit["final_verdict"]

    return f"""# REPORT_X3_MOMENTUM_REDTEAM_B1_20260622

**任务 ID:** {TASK_ID}  
**生成时间:** {audit['generated_at_utc']}  
**最终裁决:** **{final}**  
**脚本:** `06_RESEARCH/CODE/x3_momentum_redteam_b1_audit.py`  
**审计输出:** `06_RESEARCH/CODE/output/x3_momentum_redteam_b1_audit.json`

## 0. 执行前自查

- 机制验证对象：alt 横截面动量 top 三分位减 bottom 三分位是否在低频再平衡、完整换手成本和幸存者偏差压力下仍可交易。
- 验收标准是否可量化：阶段 0 三选一；B1 门1/门2/门3/被动基准任一不过即 KILL。
- 更便宜等效实现：固定 30 日 lookback + 三分位 + 日/周频率审计，不做 L/分位/频率网格搜索。
- 禁止项检查：未读取 Holdout；未改预登记；未使用全样本分位阈值；未引入黑箱依赖；失败按 KILL 写入。

## 1. 阶段 0 方向红队

**裁决：PROCEED。** 不是因为我认同 B0 的乐观版本，而是阶段 0 的三个反驳都可以被现有 panel 用固定方案量化，尚不足以在跑 B1 前直接 KILL。

1. 成本量级最危险：若每次周频组合接近全换，4 腿成本约为 `turnover * per_fill_cost`。本审计实际周频平均总换手为 **{chosen['summary']['avg_total_turnover_pct']}%**，base 0.20%/fill 的周期成本为 **{base['mean_cost_period_pct']}%**，高成本 0.30%/fill 为 **{high['mean_cost_period_pct']}%**。因此周频 raw top-bottom 必须至少达到这个量级。
2. 幸存者偏差不能被现有 35 文件完全消除：脚本只可做上市后可交易宇宙、共同样本和删除终值赢家/输家压力。缺失的“2024-12 前已死亡且不在文件中”的资产无法从当前数据复原。
3. 与 TSMOM 的正交性必须实测：周频 CS 与同 lookback TSMOM 相关为 **{pct(ortho['correlation'])}%**，不能口头判定独立。

## 2. B1 三门

### 门1 成本门

**结论：{'PASS' if gates['gate1_cost_pass'] else 'KILL'}。** 周频是低换手方案；日频仅作对照。

| 频率 | 周期数 | raw top-bottom | 平均总换手 | base 成本 | base 净收益 | high 净收益 | break-even / fill |
|---|---:|---:|---:|---:|---:|---:|---:|
| 日频 | {daily['summary']['periods']} | {daily['summary']['mean_raw_pct']}% | {daily['summary']['avg_total_turnover_pct']}% | {daily['summary']['cost_cases']['protocol_base_0_20pct']['mean_cost_period_pct']}% | {daily['summary']['cost_cases']['protocol_base_0_20pct']['mean_net_period_pct']}% | {daily['summary']['cost_cases']['alt_taker_high_0_30pct']['mean_net_period_pct']}% | {daily['summary']['break_even_cost_per_fill_pct']}% |
| 周频 | {weekly['summary']['periods']} | {weekly['summary']['mean_raw_pct']}% | {weekly['summary']['avg_total_turnover_pct']}% | {base['mean_cost_period_pct']}% | {base['mean_net_period_pct']}% | {high['mean_net_period_pct']}% | {chosen['summary']['break_even_cost_per_fill_pct']}% |

门1按 base 与 high 两档都为正才算过。若 high 档为负，说明 alt taker/逆选环境下 top-bottom 幅度没有硬证据压住成本。

### 门2 截面单调门

**结论：{'PASS' if gates['gate2_monotonic_significance_pass'] else 'KILL'}。**

周频分组未来收益：bottom **{chosen['summary']['bottom_mean_pct']}%** / middle **{chosen['summary']['middle_mean_pct']}%** / top **{chosen['summary']['top_mean_pct']}%**；单调性 `bottom < middle < top` = **{chosen['summary']['monotonic_bottom_middle_top']}**。top-bottom bootstrap 95% CI = **{chosen['summary']['bootstrap_ci_pct'][0]}% 到 {chosen['summary']['bootstrap_ci_pct'][1]}%**，MDE(95%, normal approx) = **{chosen['summary']['mde_95_period_pct']}%**。

### 门3 幸存者偏差门

**结论：{'PASS' if chosen['survivorship_gate_pass'] else 'KILL'}。**

现有 panel 的去偏压力结果：

| 压力 | 周期数 | raw top-bottom | 相对基线变化 | edge 是否消失 |
|---|---:|---:|---:|---:|
| 删除终值前 20% 赢家 | {surv['stress']['drop_top_20pct_terminal_winners']['periods']} | {surv['stress']['drop_top_20pct_terminal_winners']['mean_raw_pct']}% | {surv['stress']['drop_top_20pct_terminal_winners']['mean_change_vs_baseline_pct']}% | {surv['stress']['drop_top_20pct_terminal_winners']['edge_disappears']} |
| 删除终值后 20% 输家 | {surv['stress']['drop_bottom_20pct_terminal_losers']['periods']} | {surv['stress']['drop_bottom_20pct_terminal_losers']['mean_raw_pct']}% | {surv['stress']['drop_bottom_20pct_terminal_losers']['mean_change_vs_baseline_pct']}% | {surv['stress']['drop_bottom_20pct_terminal_losers']['edge_disappears']} |
| 全 35 币共同样本起点后 | {surv['stress']['common_sample_after_all_symbols_listed']['periods']} | {surv['stress']['common_sample_after_all_symbols_listed']['mean_raw_pct']}% | {surv['stress']['common_sample_after_all_symbols_listed']['mean_change_vs_baseline_pct']}% | {surv['stress']['common_sample_after_all_symbols_listed']['edge_disappears']} |

限制：当前文件不能补回不在 35 个文件中的死币，因此门3不能证明“去偏后仍成立”；只能证明 in-panel 压力下是否脆弱。

## 3. TSMOM 正交性与被动基准

- 周频 CS vs TSMOM period-return correlation：**{pct(ortho['correlation'])}%**；beta：**{round(float(ortho['beta_to_tsmom']), 4)}**；TSMOM 残差均值：**{ortho['residual_mean_pct']}%**。
- 周频 base-cost CS 年化 log growth：**{base['annualized_net_log_growth_pct']}%**。
- 等权 alt 被动基准年化 log growth：**{chosen['summary']['ew_alt_annualized_log_growth_pct']}%**。
- 被动基准门：**{'PASS' if gates['passive_benchmark_pass'] else 'KILL'}**。

## 4. Protocol v1.3 四件套自检

口径：周频低换手版本、base 0.20%/fill 成本后的周期净收益。

| 验收项 | 数字 | 结论 |
|---|---:|---|
| E[R] > 0 | {protocol['period_mean_pct']}% / period | {protocol['expectancy_positive']} |
| 赢亏比 >= 1.5 | {round(float(protocol['win_loss_ratio']), 4) if protocol['win_loss_ratio'] is not None else None} | {protocol['win_loss_ratio_ge_1_5']} |
| 分档爆仓/回撤概率 | DD35={pct(dd['standard_dd35_probability'])}% / DD20={pct(dd['conservative_dd20_probability'])}% / DD100={pct(dd['ruin_dd100_probability'])}% | reported |
| 年化 log growth > 0 | {protocol['annualized_log_growth_pct']}% | {protocol['annualized_log_growth_positive']} |
| 分年正期望占多数 | {protocol['positive_years']} / {len(protocol['yearly'])} | {protocol['majority_years_positive']} |

说明：本策略未给保证金/杠杆账本，分档爆仓按既有 TSMOM 风控口径用 1 年块 bootstrap 的 DD20/DD35/DD100 路径代理，不把它写成真实逐仓强平概率。

## 5. 最终裁决

**{final}。** 任一门不过即 KILL；本次议程升级条款 **{audit['agenda_escalation']}**。

关键理由：{audit['final_reason']}
"""


def render_result(audit: dict[str, object]) -> str:
    weekly = audit["frequencies"]["weekly"]  # type: ignore[index]
    base = weekly["summary"]["cost_cases"]["protocol_base_0_20pct"]  # type: ignore[index]
    high = weekly["summary"]["cost_cases"]["alt_taker_high_0_30pct"]  # type: ignore[index]
    gates = weekly["gates"]  # type: ignore[index]
    protocol = weekly["summary"]["protocol_v1_3_base_cost"]  # type: ignore[index]
    return f"""# X3 Momentum Redteam B1 Result - 2026-06-22

**Task:** {TASK_ID}  
**Verdict:** {audit['final_verdict']}  
**Stage 0:** PROCEED to fixed-parameter B1 audit.

Frozen audit design: 30-day trailing return, top/bottom terciles, daily and weekly rebalance as pre-specified cost-frequency checks, no L/quantile/frequency search.

Weekly key numbers from `06_RESEARCH/CODE/output/x3_momentum_redteam_b1_audit.json`:

| Metric | Value |
|---|---:|
| raw top-bottom / period | {weekly['summary']['mean_raw_pct']}% |
| average total turnover / period | {weekly['summary']['avg_total_turnover_pct']}% |
| base 0.20%/fill net / period | {base['mean_net_period_pct']}% |
| high 0.30%/fill net / period | {high['mean_net_period_pct']}% |
| bootstrap 95% CI | {weekly['summary']['bootstrap_ci_pct'][0]}% to {weekly['summary']['bootstrap_ci_pct'][1]}% |
| bottom / middle / top future return | {weekly['summary']['bottom_mean_pct']}% / {weekly['summary']['middle_mean_pct']}% / {weekly['summary']['top_mean_pct']}% |
| CS vs TSMOM correlation | {pct(weekly['orthogonality']['correlation'])}% |
| base-cost CS annualized log growth | {base['annualized_net_log_growth_pct']}% |
| EW alt annualized log growth | {weekly['summary']['ew_alt_annualized_log_growth_pct']}% |
| v1.3 win/loss ratio | {round(float(protocol['win_loss_ratio']), 4) if protocol['win_loss_ratio'] is not None else None} |
| v1.3 positive years | {protocol['positive_years']} / {len(protocol['yearly'])} |

Gate status: cost={gates['gate1_cost_pass']}, monotonic/significant={gates['gate2_monotonic_significance_pass']}, survivorship={weekly['survivorship_gate_pass']}, passive benchmark={gates['passive_benchmark_pass']}, v1.3_log_growth={protocol['annualized_log_growth_positive']}.

Final reason: {audit['final_reason']}
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    closes, inventory = load_daily_close()
    audit: dict[str, object] = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "seed": SEED,
        "protocol": {
            "lookback_days": LOOKBACK_DAYS,
            "groups": "top/bottom terciles",
            "frequencies": ["daily", "weekly"],
            "cost_cases_per_fill": {k: pct(v) for k, v in COST_CASES.items()},
            "holdout_read": False,
            "parameter_search": False,
        },
        "data_inventory": {
            "data_path": str(DATA_DIR.relative_to(ROOT)),
            "csv_files": len(inventory),
            "symbols": [r["symbol"] for r in inventory],
            "min_rows": min(int(r["rows"]) for r in inventory),
            "max_rows": max(int(r["rows"]) for r in inventory),
            "min_start": min(str(r["start"]) for r in inventory),
            "max_start": max(str(r["start"]) for r in inventory),
            "common_end": max(str(r["end"]) for r in inventory),
            "rows": inventory,
        },
        "stage0_verdict": "PROCEED",
        "stage0_reason": "The red-team objections are material, but the available 35-asset panel can quantify cost, monotonicity, in-panel survivorship stress, and TSMOM correlation under frozen assumptions.",
        "frequencies": {},
    }

    for freq in ["daily", "weekly"]:
        df = run_strategy(closes, freq)
        if df.empty:
            raise RuntimeError(f"No strategy rows for {freq}")
        summary = summarize_returns(df, freq)
        ortho = orthogonality(df, closes, freq)
        surv = survivorship_stress(closes, freq, float(summary["mean_raw"]))
        stress = surv["stress"]
        surv_pass = bool(
            not stress["drop_top_20pct_terminal_winners"]["edge_disappears"]
            and not stress["common_sample_after_all_symbols_listed"]["edge_disappears"]
        )
        gates = gate_verdicts(summary, freq)
        audit["frequencies"][freq] = {  # type: ignore[index]
            "summary": summary,
            "gates": gates,
            "orthogonality": ortho,
            "survivorship": surv,
            "survivorship_gate_pass": surv_pass,
            "selection_concentration_top10": asset_contribution(df),
        }

    weekly = audit["frequencies"]["weekly"]  # type: ignore[index]
    weekly_gates = weekly["gates"]
    all_pass = bool(
        weekly_gates["gate1_cost_pass"]
        and weekly_gates["gate2_monotonic_significance_pass"]
        and weekly["survivorship_gate_pass"]
        and weekly_gates["passive_benchmark_pass"]
    )
    audit["final_verdict"] = "PROCEED-to-B2" if all_pass else "KILL"
    failed = []
    if not weekly_gates["gate1_cost_pass"]:
        failed.append("成本门")
    if not weekly_gates["gate2_monotonic_significance_pass"]:
        failed.append("截面单调/显著门")
    if not weekly["survivorship_gate_pass"]:
        failed.append("幸存者偏差门")
    if not weekly_gates["passive_benchmark_pass"]:
        failed.append("被动基准门")
    if not weekly["summary"]["protocol_v1_3_base_cost"]["annualized_log_growth_positive"]:  # type: ignore[index]
        failed.append("v1.3 年化log增长")
    if not weekly["summary"]["protocol_v1_3_base_cost"]["win_loss_ratio_ge_1_5"]:  # type: ignore[index]
        failed.append("v1.3 赢亏比")
    if not weekly["summary"]["protocol_v1_3_base_cost"]["majority_years_positive"]:  # type: ignore[index]
        failed.append("v1.3 分年正期望")
    audit["final_reason"] = (
        "B1 four gates all passed under the frozen weekly low-turnover design."
        if all_pass
        else "未通过：" + "、".join(failed) + "；默认 KILL 基线下不得靠改 L/分位/频率续命。"
    )
    audit["agenda_escalation"] = "触发" if not all_pass else "未触发"

    OUTPUT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    REPORT_PATH.write_text(render_report(audit), encoding="utf-8")
    RESULT_PATH.write_text(render_result(audit), encoding="utf-8")
    print(OUTPUT_JSON)
    print(REPORT_PATH)
    print(RESULT_PATH)


if __name__ == "__main__":
    main()
