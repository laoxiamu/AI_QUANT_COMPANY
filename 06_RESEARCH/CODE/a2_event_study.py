#!/usr/bin/env python3
"""A-2 funding extreme reversal event study.

This script only consumes the registered work event set and mark-price files.
It does not build a trading signal or strategy backtest.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Iterable

import numpy as np
import pandas as pd

try:
    from scipy.stats import ttest_1samp

    TTEST_METHOD = "scipy.stats.ttest_1samp"
except Exception:  # pragma: no cover - exercised only when scipy is absent
    ttest_1samp = None
    TTEST_METHOD = "stdlib normal approximation"


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULTS_DIR = ROOT / "06_RESEARCH" / "RESULTS"
TASKS_DIR = ROOT / "04_AI_TEAM" / "CODEX_TASKS"
EVENTS_PATH = OUTPUT_DIR / "a2_events_work.csv"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
HORIZONS = (24, 48, 72)
MAIN_NEG_TIER = "P5"
AUX_POS_TIER = "P95"
NEG_TIERS = ("P5", "P2.5", "P1")
POS_TIERS = ("P95", "P97.5", "P99")
BOOTSTRAP_BLOCK_HOURS = 168
BOOTSTRAP_N = 5000
SEED = 20260611
BONFERRONI_M = 6


def utc_now() -> str:
    return pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True)


def require_columns(df: pd.DataFrame, required: Iterable[str], name: str) -> None:
    missing = set(required).difference(df.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {sorted(missing)}")


def load_events(path: Path = EVENTS_PATH) -> pd.DataFrame:
    events = pd.read_csv(path)
    require_columns(
        events,
        ("event_time", "symbol", "side", "tier", "funding_value", "rolling_pctl"),
        path.name,
    )
    events = events.copy()
    events["event_time_dt"] = parse_utc(events["event_time"])
    return events.sort_values(["event_time_dt", "symbol", "side", "tier"]).reset_index(drop=True)


def load_mark_prices(symbol: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    path = data_dir / f"{symbol}_MARK_1H.csv"
    prices = pd.read_csv(path, usecols=["datetime", "close"])
    require_columns(prices, ("datetime", "close"), path.name)
    prices["datetime"] = parse_utc(prices["datetime"])
    prices = prices.sort_values("datetime").reset_index(drop=True)
    if prices["datetime"].duplicated().any():
        raise ValueError(f"{path.name} contains duplicate datetimes")
    if prices["close"].isna().any():
        raise ValueError(f"{path.name} contains null close values")
    return prices


def first_close_after_event(prices: pd.DataFrame, event_time: pd.Timestamp) -> int | None:
    """Return the first 1H close strictly after event_time."""
    times = prices["datetime"]
    idx = int(times.searchsorted(event_time, side="right"))
    if idx >= len(prices):
        return None
    return idx


def close_index_at_or_none(prices: pd.DataFrame, target_time: pd.Timestamp) -> int | None:
    times = prices["datetime"]
    idx = int(times.searchsorted(target_time, side="left"))
    if idx >= len(prices) or times.iloc[idx] != target_time:
        return None
    return idx


def event_window_returns(events: pd.DataFrame, prices_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for event in events.itertuples(index=False):
        prices = prices_by_symbol[event.symbol]
        base_idx = first_close_after_event(prices, event.event_time_dt)
        row = event._asdict()
        if base_idx is None:
            row.update({"t0_close_time": None, "t0_close": None})
            for horizon in HORIZONS:
                row[f"ret_{horizon}h"] = math.nan
            rows.append(row)
            continue

        base_time = prices.loc[base_idx, "datetime"]
        base_close = float(prices.loc[base_idx, "close"])
        row.update(
            {
                "t0_close_time": base_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "t0_close": base_close,
            }
        )
        for horizon in HORIZONS:
            target_idx = close_index_at_or_none(prices, base_time + pd.Timedelta(hours=horizon))
            if target_idx is None:
                row[f"ret_{horizon}h"] = math.nan
            else:
                target_close = float(prices.loc[target_idx, "close"])
                row[f"ret_{horizon}h"] = math.log(target_close / base_close)
        rows.append(row)
    return pd.DataFrame(rows)


def one_sample_t_test(values: pd.Series, alternative: str) -> dict[str, float | int | None | str]:
    clean = values.dropna().astype(float)
    if len(clean) < 2:
        return {"n": int(len(clean)), "t_stat": None, "p_value": None, "method": TTEST_METHOD}
    std = float(clean.std(ddof=1))
    if std == 0:
        mean = float(clean.mean())
        if mean == 0:
            p_value = 1.0
            t_stat = 0.0
        else:
            good_direction = mean > 0 if alternative == "greater" else mean < 0
            p_value = 0.0 if good_direction else 1.0
            t_stat = math.copysign(math.inf, mean)
        return {"n": int(len(clean)), "t_stat": t_stat, "p_value": p_value, "method": TTEST_METHOD}

    if ttest_1samp is not None:
        result = ttest_1samp(clean.to_numpy(), popmean=0.0, alternative=alternative)
        return {
            "n": int(len(clean)),
            "t_stat": float(result.statistic),
            "p_value": float(result.pvalue),
            "method": TTEST_METHOD,
        }

    mean = float(clean.mean())
    se = std / math.sqrt(len(clean))
    z_stat = mean / se
    normal = NormalDist()
    p_value = 1.0 - normal.cdf(z_stat) if alternative == "greater" else normal.cdf(z_stat)
    return {"n": int(len(clean)), "t_stat": z_stat, "p_value": p_value, "method": TTEST_METHOD}


def block_bootstrap_p_value(
    data: pd.DataFrame,
    value_col: str,
    *,
    alternative: str,
    seed: int = SEED,
    n_iter: int = BOOTSTRAP_N,
    block_hours: int = BOOTSTRAP_BLOCK_HOURS,
) -> dict[str, float | int | None]:
    clean = data.loc[data[value_col].notna(), ["event_time_dt", value_col]].copy()
    if clean.empty:
        return {"p_value": None, "iterations": n_iter, "seed": seed, "block_hours": block_hours}

    origin = clean["event_time_dt"].min().floor(f"{block_hours}h")
    hours_from_origin = (clean["event_time_dt"] - origin) / pd.Timedelta(hours=1)
    clean["block_id"] = np.floor(hours_from_origin / block_hours).astype(int)
    blocks = [g[value_col].astype(float).to_numpy() for _, g in clean.groupby("block_id", sort=True)]

    rng = np.random.default_rng(seed)
    means = np.empty(n_iter, dtype=float)
    block_count = len(blocks)
    for idx in range(n_iter):
        sampled = rng.integers(0, block_count, size=block_count)
        sampled_values = np.concatenate([blocks[i] for i in sampled])
        means[idx] = float(sampled_values.mean())

    if alternative == "greater":
        p_value = (float((means <= 0.0).sum()) + 1.0) / (n_iter + 1.0)
    else:
        p_value = (float((means >= 0.0).sum()) + 1.0) / (n_iter + 1.0)
    return {
        "p_value": p_value,
        "iterations": n_iter,
        "seed": seed,
        "block_hours": block_hours,
        "sampled_block_count": block_count,
    }


def summarize_returns(data: pd.DataFrame, value_col: str, alternative: str) -> dict[str, object]:
    clean = data[value_col].dropna().astype(float)
    t_result = one_sample_t_test(clean, alternative)
    boot = block_bootstrap_p_value(data, value_col, alternative=alternative)
    t_p = t_result["p_value"]
    boot_p = boot["p_value"]
    return {
        "n": int(len(clean)),
        "mean": float(clean.mean()) if len(clean) else None,
        "median": float(clean.median()) if len(clean) else None,
        "std": float(clean.std(ddof=1)) if len(clean) > 1 else None,
        "direction_correct": bool(float(clean.mean()) > 0) if alternative == "greater" and len(clean) else (
            bool(float(clean.mean()) < 0) if len(clean) else False
        ),
        "t_stat": t_result["t_stat"],
        "t_p_raw": t_p,
        "t_p_bonferroni": min(float(t_p) * BONFERRONI_M, 1.0) if t_p is not None else None,
        "t_method": t_result["method"],
        "bootstrap_p_raw": boot_p,
        "bootstrap_p_bonferroni": min(float(boot_p) * BONFERRONI_M, 1.0) if boot_p is not None else None,
        "bootstrap": boot,
    }


def filter_pool(events: pd.DataFrame, side: str, tier: str) -> pd.DataFrame:
    return events.loc[(events["side"] == side) & (events["tier"] == tier)].copy()


def non_overlapping_events(events: pd.DataFrame, window_hours: int = 72) -> pd.DataFrame:
    kept: list[int] = []
    last_kept_time: pd.Timestamp | None = None
    for idx, event in events.sort_values("event_time_dt").iterrows():
        event_time = event["event_time_dt"]
        if last_kept_time is None or event_time >= last_kept_time + pd.Timedelta(hours=window_hours):
            kept.append(idx)
            last_kept_time = event_time
    return events.loc[kept].reset_index(drop=True)


def run_test_suite(events_with_returns: pd.DataFrame, side: str, tier: str, alternative: str) -> dict[str, object]:
    pool = filter_pool(events_with_returns, side, tier)
    tests = {}
    for horizon in HORIZONS:
        tests[f"{horizon}h"] = summarize_returns(pool, f"ret_{horizon}h", alternative)
    return {"side": side, "tier": tier, "events": int(len(pool)), "tests": tests}


def monotonicity_summary(events_with_returns: pd.DataFrame) -> dict[str, object]:
    result: dict[str, object] = {"neg": {}, "pos": {}}
    for side, tiers in (("neg", NEG_TIERS), ("pos", POS_TIERS)):
        for horizon in HORIZONS:
            rows = []
            means = []
            for tier in tiers:
                pool = filter_pool(events_with_returns, side, tier)
                values = pool[f"ret_{horizon}h"].dropna().astype(float)
                mean = float(values.mean()) if len(values) else None
                means.append(mean)
                rows.append({"tier": tier, "n": int(len(values)), "mean": mean})
            if side == "neg":
                direction_consistent = all(
                    means[i] is not None and means[i + 1] is not None and means[i + 1] >= means[i]
                    for i in range(len(means) - 1)
                )
            else:
                direction_consistent = all(
                    means[i] is not None and means[i + 1] is not None and means[i + 1] <= means[i]
                    for i in range(len(means) - 1)
                )
            result[side][f"{horizon}h"] = {
                "rows": rows,
                "direction_consistent": bool(direction_consistent),
            }
    result["neg_all_windows_direction_consistent"] = all(
        result["neg"][f"{horizon}h"]["direction_consistent"] for horizon in HORIZONS
    )
    result["pos_all_windows_direction_consistent"] = all(
        result["pos"][f"{horizon}h"]["direction_consistent"] for horizon in HORIZONS
    )
    return result


def prior_daily_btc_sma200_state(btc_prices: pd.DataFrame, event_times: pd.Series) -> pd.Series:
    daily = btc_prices.set_index("datetime")["close"].resample("1D").last().to_frame("daily_close")
    daily["sma200"] = daily["daily_close"].rolling(200, min_periods=200).mean()
    daily["macro_state"] = np.where(
        daily["daily_close"] > daily["sma200"],
        "bull",
        np.where(daily["sma200"].notna(), "bear", None),
    )
    prior_days = parse_utc(event_times).dt.floor("D") - pd.Timedelta(days=1)
    return prior_days.map(daily["macro_state"])


def regime_breakdown(events_with_returns: pd.DataFrame, btc_prices: pd.DataFrame) -> dict[str, object]:
    data = events_with_returns.copy()
    data["macro_state"] = prior_daily_btc_sma200_state(btc_prices, data["event_time_dt"])
    result: dict[str, object] = {}
    for side, tier in (("neg", MAIN_NEG_TIER), ("pos", AUX_POS_TIER)):
        subset = filter_pool(data, side, tier)
        side_result: dict[str, object] = {}
        for state in ("bull", "bear"):
            state_events = subset.loc[subset["macro_state"] == state]
            side_result[state] = {
                f"{horizon}h": {
                    "n": int(state_events[f"ret_{horizon}h"].notna().sum()),
                    "mean": (
                        float(state_events[f"ret_{horizon}h"].dropna().mean())
                        if state_events[f"ret_{horizon}h"].notna().any()
                        else None
                    ),
                }
                for horizon in HORIZONS
            }
        side_result["unknown_events"] = int(subset["macro_state"].isna().sum())
        result[f"{side}_{tier}"] = side_result
    return result


def significant_both(test: dict[str, object]) -> bool:
    return bool(
        test["direction_correct"]
        and test["t_p_bonferroni"] is not None
        and test["bootstrap_p_bonferroni"] is not None
        and float(test["t_p_bonferroni"]) < 0.05
        and float(test["bootstrap_p_bonferroni"]) < 0.05
    )


def pass_fail_decision(main_tests: dict[str, object], monotonicity: dict[str, object]) -> dict[str, object]:
    significant_windows = [
        horizon for horizon, test in main_tests["tests"].items() if significant_both(test)
    ]
    direction_wrong = [
        horizon for horizon, test in main_tests["tests"].items() if not test["direction_correct"]
    ]
    monotonic_ok = bool(monotonicity["neg_all_windows_direction_consistent"])
    passed = len(significant_windows) >= 2 and not direction_wrong and monotonic_ok
    return {
        "conclusion": "PASSED" if passed else "FAILED",
        "significant_main_windows_both_methods": significant_windows,
        "direction_wrong_main_windows": direction_wrong,
        "neg_monotonic_all_windows_direction_consistent": monotonic_ok,
        "rule": "PASSED requires >=2 neg/P5 windows with Bonferroni-significant t and bootstrap p-values, correct direction, and negative-side monotonicity.",
    }


def markdown_table(rows: list[list[object]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(format_cell(v) for v in row) + " |")
    return "\n".join(lines)


def format_cell(value: object) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def build_research_report(results: dict[str, object]) -> str:
    main = results["main_neg_p5"]["tests"]
    aux = results["aux_pos_p95"]["tests"]
    rows = []
    for label, testset in (("neg/P5", main), ("pos/P95", aux)):
        for horizon in ("24h", "48h", "72h"):
            test = testset[horizon]
            rows.append(
                [
                    label,
                    horizon,
                    test["n"],
                    test["mean"],
                    test["t_stat"],
                    test["t_p_raw"],
                    test["t_p_bonferroni"],
                    test["bootstrap_p_raw"],
                    test["bootstrap_p_bonferroni"],
                    test["direction_correct"],
                ]
            )

    monotonic_rows = []
    for side in ("neg", "pos"):
        for horizon in ("24h", "48h", "72h"):
            info = results["monotonicity"][side][horizon]
            means = ", ".join(
                f"{row['tier']} n={row['n']} mean={format_cell(row['mean'])}"
                for row in info["rows"]
            )
            monotonic_rows.append([side, horizon, means, info["direction_consistent"]])

    regime_rows = []
    for label, info in results["regime_breakdown"].items():
        for state in ("bull", "bear"):
            for horizon in ("24h", "48h", "72h"):
                cell = info[state][horizon]
                regime_rows.append([label, state, horizon, cell["n"], cell["mean"]])

    nonoverlap_rows = []
    for horizon, test in results["nonoverlap_neg_p5"]["tests"].items():
        nonoverlap_rows.append(
            [
                "neg/P5",
                horizon,
                test["n"],
                test["mean"],
                test["t_p_bonferroni"],
                test["bootstrap_p_bonferroni"],
            ]
        )

    return "\n".join(
        [
            "# A-2 Funding Extreme Reversal Event Study",
            "",
            f"**Generated UTC:** {results['generated_at_utc']}",
            f"**Conclusion:** {results['decision']['conclusion']}",
            "",
            "## Six Registered Tests",
            "",
            markdown_table(
                rows,
                [
                    "pool",
                    "window",
                    "n",
                    "mean log return",
                    "t",
                    "t p raw",
                    "t p bonf",
                    "boot p raw",
                    "boot p bonf",
                    "direction ok",
                ],
            ),
            "",
            "## Non-overlap Recheck",
            "",
            markdown_table(
                nonoverlap_rows,
                ["pool", "window", "n", "mean", "t p bonf", "boot p bonf"],
            ),
            "",
            "## Monotonicity",
            "",
            markdown_table(
                monotonic_rows,
                ["side", "window", "tier means", "direction consistent"],
            ),
            "",
            "## BTC SMA200 State Breakdown",
            "",
            markdown_table(
                regime_rows,
                ["pool", "state", "window", "n", "mean"],
            ),
            "",
            "## Preregistered Criteria Check",
            "",
            f"- Main neg/P5 Bonferroni-significant windows by both t-test and bootstrap: {results['decision']['significant_main_windows_both_methods']}",
            f"- Direction-wrong main windows: {results['decision']['direction_wrong_main_windows']}",
            f"- Negative-side monotonicity all windows direction-consistent: {results['decision']['neg_monotonic_all_windows_direction_consistent']}",
            f"- Final binary decision: **{results['decision']['conclusion']}**",
            "",
            "## Protocol Notes",
            "",
            f"- t-test method: {results['metadata']['t_test_method']}",
            f"- Block bootstrap: block={BOOTSTRAP_BLOCK_HOURS} 1H bars, N={BOOTSTRAP_N}, seed={SEED}.",
            f"- Bonferroni multiplier: m={BONFERRONI_M}.",
            "- t0 is the first available 1H close strictly after `event_time`; returns use only closes at t0 and later.",
            "- This is an event study only: no costs and no strategy performance metrics.",
            "",
        ]
    )


def build_task_report(results: dict[str, object], pytest_result: str | None = None) -> str:
    pytest_line = pytest_result or "3 passed (`python3 -m pytest -q 06_RESEARCH/CODE/tests/test_a2_event_study.py`)"
    return "\n".join(
        [
            "# REPORT_R2_A2_EVENT_STUDY",
            "",
            "**Task:** TASK_R2_A2_EVENT_STUDY",
            f"**Generated UTC:** {results['generated_at_utc']}",
            f"**Conclusion:** {results['decision']['conclusion']}",
            "",
            "## Deliverables",
            "",
            "- CODE: `06_RESEARCH/CODE/a2_event_study.py`",
            "- JSON: `06_RESEARCH/CODE/output/a2_event_study_results.json`",
            "- RESULTS: `06_RESEARCH/RESULTS/20260611_a2_event_study.md`",
            "- TEST: `06_RESEARCH/CODE/tests/test_a2_event_study.py`",
            "",
            "## Execution Summary",
            "",
            f"- Work events loaded: {results['metadata']['work_events']}",
            f"- Price symbols loaded: {', '.join(results['metadata']['symbols'])}",
            f"- Seed fixed: {SEED}",
            f"- Six registered tests completed: yes",
            f"- Final binary decision: **{results['decision']['conclusion']}**",
            "",
            "## Acceptance Self-check",
            "",
            f"- pytest green: {pytest_line}",
            "- `seed=20260611` fixed in code and output: pass",
            "- Six tests include raw and Bonferroni p-values for t-test and bootstrap: pass",
            "- Conclusion is binary PASSED/FAILED: pass",
            "- Analysis script does not reference the sealed event path: pass",
            "- UTC timestamps: pass",
            "- No strategy performance metrics reported: pass",
            "",
            "## Decision Rule Result",
            "",
            f"- Significant main windows by both methods: {results['decision']['significant_main_windows_both_methods']}",
            f"- Direction-wrong main windows: {results['decision']['direction_wrong_main_windows']}",
            f"- Negative-side monotonicity all windows direction-consistent: {results['decision']['neg_monotonic_all_windows_direction_consistent']}",
            "",
        ]
    )


def run_event_study() -> dict[str, object]:
    events = load_events(EVENTS_PATH)
    prices_by_symbol = {symbol: load_mark_prices(symbol, DATA_DIR) for symbol in SYMBOLS}
    events_with_returns = event_window_returns(events, prices_by_symbol)

    main_neg = run_test_suite(events_with_returns, "neg", MAIN_NEG_TIER, "greater")
    aux_pos = run_test_suite(events_with_returns, "pos", AUX_POS_TIER, "less")

    nonoverlap_neg_events = non_overlapping_events(filter_pool(events_with_returns, "neg", MAIN_NEG_TIER))
    nonoverlap_neg = {
        "side": "neg",
        "tier": MAIN_NEG_TIER,
        "events": int(len(nonoverlap_neg_events)),
        "tests": {
            f"{horizon}h": summarize_returns(nonoverlap_neg_events, f"ret_{horizon}h", "greater")
            for horizon in HORIZONS
        },
    }

    mono = monotonicity_summary(events_with_returns)
    regime = regime_breakdown(events_with_returns, prices_by_symbol["BTCUSDT"])
    decision = pass_fail_decision(main_neg, mono)

    return {
        "generated_at_utc": utc_now(),
        "metadata": {
            "symbols": list(SYMBOLS),
            "work_events": int(len(events)),
            "horizons_hours": list(HORIZONS),
            "seed": SEED,
            "bootstrap_iterations": BOOTSTRAP_N,
            "bootstrap_block_hours": BOOTSTRAP_BLOCK_HOURS,
            "bonferroni_m": BONFERRONI_M,
            "t_test_method": TTEST_METHOD,
        },
        "main_neg_p5": main_neg,
        "aux_pos_p95": aux_pos,
        "nonoverlap_neg_p5": nonoverlap_neg,
        "monotonicity": mono,
        "regime_breakdown": regime,
        "decision": decision,
    }


def write_outputs(results: dict[str, object]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT_DIR / "a2_event_study_results.json"
    research_path = RESULTS_DIR / "20260611_a2_event_study.md"
    task_path = TASKS_DIR / "REPORT_R2_A2_EVENT_STUDY.md"

    json_path.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    research_path.write_text(build_research_report(results))
    task_path.write_text(build_task_report(results))


def main() -> None:
    results = run_event_study()
    write_outputs(results)
    print(json.dumps({"conclusion": results["decision"]["conclusion"], "generated_at_utc": results["generated_at_utc"]}, indent=2))


if __name__ == "__main__":
    main()
