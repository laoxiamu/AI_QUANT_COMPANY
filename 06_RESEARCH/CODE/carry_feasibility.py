#!/usr/bin/env python3
"""
Delta-neutral carry feasibility accounting for TASK_CARRY_FEASIBILITY.

Scope:
- Historical accounting only; no trading signal, timing rule, or backtest.
- Reads only 06_RESEARCH/DATA/FUTURES funding and mark files.
- Does not read HOLDOUT, hypotheses, or pre-registration documents.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


SEED = 20260612  # No stochastic step; recorded for project reproducibility convention.
TASK_ID = "CARRY_FEASIBILITY"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
PRIMARY_SYMBOLS = ("BTCUSDT", "ETHUSDT")
REFERENCE_SYMBOLS = ("SOLUSDT",)
FUNDING_EXTREME_ABS_RATE = 0.001  # 0.10% per 8h, fixed threshold; not a sample quantile.
HOLD_DAYS = (30, 90, 365)
PRINCIPAL = 30_000.0
SPOT_CAPITAL_FRACTION = 0.50
MARGIN_RATES = (0.10, 0.20, 0.50)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULTS_DIR = ROOT / "06_RESEARCH" / "RESULTS"
TASKS_DIR = ROOT / "04_AI_TEAM" / "CODEX_TASKS"


@dataclass(frozen=True)
class FeeScenario:
    name: str
    spot_fee_per_side: float
    perp_fee_per_side: float
    slippage_per_side: float
    note: str

    @property
    def round_trip_cost(self) -> float:
        spot_round_trip = 2.0 * (self.spot_fee_per_side + self.slippage_per_side)
        perp_round_trip = 2.0 * (self.perp_fee_per_side + self.slippage_per_side)
        return spot_round_trip + perp_round_trip


FEE_SCENARIOS = (
    FeeScenario(
        name="VIP0_task_conservative",
        spot_fee_per_side=0.0010,
        perp_fee_per_side=0.0010,
        slippage_per_side=0.0010,
        note="Task-mandated conservative fee 0.10%/side on spot and perp; slippage 0.10%/side.",
    ),
    FeeScenario(
        name="BNB_fee_discount_sensitivity",
        spot_fee_per_side=0.00075,
        perp_fee_per_side=0.00090,
        slippage_per_side=0.0010,
        note=(
            "Sensitivity only: spot fee 25% lower and perp fee 10% lower than the task "
            "0.10%/side fee; slippage unchanged."
        ),
    ),
)


def pct(x: float, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "NA"
    return f"{x * 100:.{digits}f}%"


def fnum(x: float, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "NA"
    return f"{x:.{digits}f}"


def md_table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    safe_rows = [["" if v is None else str(v) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in safe_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(row: Iterable[str]) -> str:
        return "| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)) + " |"

    sep = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    return "\n".join([fmt(headers), sep, *[fmt(row) for row in safe_rows]])


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_concat_csv(symbol: str, suffix: str) -> pd.DataFrame:
    paths = [DATA_DIR / f"{symbol}_{suffix}.csv", DATA_DIR / f"{symbol}_{suffix}_2026H1.csv"]
    frames = []
    for path in paths:
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        raise FileNotFoundError(f"No input file found for {symbol} {suffix}")
    df = pd.concat(frames, ignore_index=True)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df = df.drop_duplicates("datetime").sort_values("datetime").reset_index(drop=True)
    return df


def longest_true_run(mask: Iterable[bool]) -> int:
    longest = 0
    current = 0
    for value in mask:
        if value:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def longest_true_run_hours(mask: Iterable[bool], hours: Iterable[float]) -> float:
    longest = 0.0
    current = 0.0
    for value, hour in zip(mask, hours):
        if value:
            current += float(hour)
            longest = max(longest, current)
        else:
            current = 0.0
    return longest


def annualized_from_hours(rates: pd.Series, hours: pd.Series) -> float:
    if rates.empty:
        return float("nan")
    observed_hours = float(hours.sum())
    if observed_hours <= 0:
        return float("nan")
    return float(rates.sum() / observed_hours * 24.0 * 365.25)


def funding_stats(symbol: str, funding: pd.DataFrame) -> tuple[list[dict], dict]:
    df = funding.copy()
    df["year"] = df["datetime"].dt.year
    rows = []
    for year, grp in df.groupby("year", sort=True):
        rates = grp["last_funding_rate"].astype(float)
        hours = grp["funding_interval_hours"].astype(float)
        longest_neg_periods = int(longest_true_run(rates < 0.0))
        longest_neg_hours = longest_true_run_hours(rates < 0.0, hours)
        rows.append(
            {
                "symbol": symbol,
                "year": int(year),
                "periods": int(len(grp)),
                "observed_days": float(hours.sum() / 24.0),
                "sum_funding_return": float(rates.sum()),
                "annualized_funding_return": annualized_from_hours(rates, hours),
                "negative_period_share": float((rates < 0.0).mean()),
                "longest_negative_periods": longest_neg_periods,
                "longest_negative_days": float(longest_neg_hours / 24.0),
            }
        )
    rates_all = df["last_funding_rate"].astype(float)
    hours_all = df["funding_interval_hours"].astype(float)
    longest_neg_periods_all = int(longest_true_run(rates_all < 0.0))
    longest_neg_hours_all = longest_true_run_hours(rates_all < 0.0, hours_all)
    overall = {
        "symbol": symbol,
        "start": df["datetime"].min().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "end": df["datetime"].max().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "periods": int(len(df)),
        "observed_days": float(hours_all.sum() / 24.0),
        "annualized_funding_return": annualized_from_hours(rates_all, hours_all),
        "negative_period_share": float((rates_all < 0.0).mean()),
        "longest_negative_periods": longest_neg_periods_all,
        "longest_negative_days": float(longest_neg_hours_all / 24.0),
        "mean_8h": float(rates_all.mean()),
        "median_8h": float(rates_all.median()),
        "non_8h_periods": int((hours_all != 8.0).sum()),
    }
    return rows, overall


def cost_sensitivity(overall_rows: list[dict]) -> list[dict]:
    rows = []
    for item in overall_rows:
        symbol = item["symbol"]
        gross_ann = item["annualized_funding_return"]
        daily_gross = gross_ann / 365.25
        for scenario in FEE_SCENARIOS:
            cost = scenario.round_trip_cost
            break_even_days = cost / daily_gross if daily_gross > 0 else float("inf")
            for hold_days in HOLD_DAYS:
                amortized_ann_cost = cost * 365.25 / hold_days
                net_ann_notional = gross_ann - amortized_ann_cost
                rows.append(
                    {
                        "symbol": symbol,
                        "scenario": scenario.name,
                        "hold_days": hold_days,
                        "round_trip_cost": cost,
                        "gross_ann_on_notional": gross_ann,
                        "annualized_cost_drag": amortized_ann_cost,
                        "net_ann_on_notional": net_ann_notional,
                        "break_even_days": break_even_days,
                    }
                )
    return rows


def mark_proxy(symbol: str, funding: pd.DataFrame, mark: pd.DataFrame) -> dict:
    extreme = funding[funding["last_funding_rate"].astype(float).abs() >= FUNDING_EXTREME_ABS_RATE].copy()
    if extreme.empty:
        return {
            "symbol": symbol,
            "extreme_threshold_abs": FUNDING_EXTREME_ABS_RATE,
            "extreme_periods": 0,
            "negative_extreme_periods": 0,
            "positive_extreme_periods": 0,
        }

    mark_idx = mark.set_index("datetime").sort_index()
    records = []
    for _, row in extreme.iterrows():
        t = row["datetime"]
        window = mark_idx.loc[(mark_idx.index >= t) & (mark_idx.index <= t + pd.Timedelta(hours=24))]
        if len(window) < 2:
            continue
        start_close = float(window["close"].iloc[0])
        end_close = float(window["close"].iloc[-1])
        high = float(window["high"].max())
        low = float(window["low"].min())
        records.append(
            {
                "funding_time": t,
                "funding_rate": float(row["last_funding_rate"]),
                "return_24h": end_close / start_close - 1.0,
                "high_low_range_24h": high / low - 1.0,
                "max_up_24h": high / start_close - 1.0,
                "max_down_24h": low / start_close - 1.0,
            }
        )

    proxy = pd.DataFrame(records)
    if proxy.empty:
        return {
            "symbol": symbol,
            "extreme_threshold_abs": FUNDING_EXTREME_ABS_RATE,
            "extreme_periods": int(len(extreme)),
            "usable_windows": 0,
        }
    return {
        "symbol": symbol,
        "extreme_threshold_abs": FUNDING_EXTREME_ABS_RATE,
        "extreme_periods": int(len(extreme)),
        "usable_windows": int(len(proxy)),
        "negative_extreme_periods": int((extreme["last_funding_rate"] <= -FUNDING_EXTREME_ABS_RATE).sum()),
        "positive_extreme_periods": int((extreme["last_funding_rate"] >= FUNDING_EXTREME_ABS_RATE).sum()),
        "median_abs_return_24h": float(proxy["return_24h"].abs().median()),
        "p90_abs_return_24h": float(proxy["return_24h"].abs().quantile(0.90)),
        "max_abs_return_24h": float(proxy["return_24h"].abs().max()),
        "median_high_low_range_24h": float(proxy["high_low_range_24h"].median()),
        "p90_high_low_range_24h": float(proxy["high_low_range_24h"].quantile(0.90)),
        "max_high_low_range_24h": float(proxy["high_low_range_24h"].max()),
        "worst_24h_return": float(proxy["return_24h"].min()),
        "best_24h_return": float(proxy["return_24h"].max()),
    }


def capital_efficiency(cost_rows: list[dict]) -> list[dict]:
    rows = []
    notional = PRINCIPAL * SPOT_CAPITAL_FRACTION
    for row in cost_rows:
        if row["hold_days"] != 365:
            continue
        if row["symbol"] not in PRIMARY_SYMBOLS:
            continue
        for margin_rate in MARGIN_RATES:
            margin_required = notional * margin_rate
            free_buffer = PRINCIPAL - notional - margin_required
            net_ann_principal = row["net_ann_on_notional"] * notional / PRINCIPAL
            rows.append(
                {
                    "symbol": row["symbol"],
                    "scenario": row["scenario"],
                    "perp_margin_rate": margin_rate,
                    "spot_notional": notional,
                    "margin_required": margin_required,
                    "free_cash_buffer": free_buffer,
                    "net_ann_on_principal": net_ann_principal,
                    "net_annual_cash": net_ann_principal * PRINCIPAL,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_result_markdown(
    generated_utc: str,
    sources: dict[str, list[dict]],
    overall: list[dict],
    yearly: list[dict],
    costs: list[dict],
    proxies: list[dict],
    cap_eff: list[dict],
) -> str:
    overall_rows = [
        [
            r["symbol"],
            r["start"][:10],
            r["end"][:10],
            f'{r["periods"]} ({r["non_8h_periods"]} non-8h)',
            pct(r["mean_8h"], 4),
            pct(r["annualized_funding_return"]),
            pct(r["negative_period_share"]),
            f'{r["longest_negative_periods"]} ({fnum(r["longest_negative_days"], 1)}d)',
        ]
        for r in overall
    ]
    yearly_rows = [
        [
            r["symbol"],
            r["year"],
            r["periods"],
            fnum(r["observed_days"], 1),
            pct(r["sum_funding_return"]),
            pct(r["annualized_funding_return"]),
            pct(r["negative_period_share"]),
            f'{r["longest_negative_periods"]} ({fnum(r["longest_negative_days"], 1)}d)',
        ]
        for r in yearly
    ]
    cost_rows = [
        [
            r["symbol"],
            r["scenario"],
            r["hold_days"],
            pct(r["round_trip_cost"]),
            pct(r["annualized_cost_drag"]),
            pct(r["net_ann_on_notional"]),
            fnum(r["break_even_days"], 1),
        ]
        for r in costs
    ]
    proxy_rows = [
        [
            r["symbol"],
            r.get("extreme_periods", 0),
            r.get("negative_extreme_periods", 0),
            r.get("positive_extreme_periods", 0),
            pct(r.get("median_abs_return_24h", float("nan"))),
            pct(r.get("p90_abs_return_24h", float("nan"))),
            pct(r.get("max_abs_return_24h", float("nan"))),
            pct(r.get("max_high_low_range_24h", float("nan"))),
        ]
        for r in proxies
    ]
    cap_rows = [
        [
            r["symbol"],
            r["scenario"],
            pct(r["perp_margin_rate"], 0),
            fnum(r["spot_notional"], 0),
            fnum(r["margin_required"], 0),
            fnum(r["free_cash_buffer"], 0),
            pct(r["net_ann_on_principal"]),
            fnum(r["net_annual_cash"], 0),
        ]
        for r in cap_eff
    ]

    primary_365 = [
        r for r in costs if r["symbol"] in PRIMARY_SYMBOLS and r["scenario"] == "VIP0_task_conservative" and r["hold_days"] == 365
    ]
    primary_net_min = min(r["net_ann_on_notional"] for r in primary_365)
    primary_net_max = max(r["net_ann_on_notional"] for r in primary_365)
    cap_primary = [
        r for r in cap_eff if r["scenario"] == "VIP0_task_conservative" and r["perp_margin_rate"] == 0.20
    ]
    cap_min = min(r["net_ann_on_principal"] for r in cap_primary)
    cap_max = max(r["net_ann_on_principal"] for r in cap_primary)

    source_lines = []
    for symbol, items in sources.items():
        joined = "; ".join(f"{item['file']} sha256={item['sha256'][:12]} rows={item['rows']}" for item in items)
        source_lines.append(f"- {symbol}: {joined}")

    return f"""# Delta-neutral carry feasibility accounting

**Generated UTC:** {generated_utc}  
**Task:** TASK_CARRY_FEASIBILITY  
**Nature:** pure historical accounting; not a strategy backtest; no trading signal or timing design.  
**Data boundary:** read only `06_RESEARCH/DATA/FUTURES`; did not read `06_RESEARCH/DATA/HOLDOUT`.

## Executive Summary

- **BTC/ETH still cover conservative double-leg costs on a 365-day hold.** With the task-mandated VIP0 conservative cost of {pct(FEE_SCENARIOS[0].round_trip_cost)} round trip, BTC/ETH net annualized carry on notional is {pct(primary_net_min)} to {pct(primary_net_max)} after amortizing one open/close over 365 days.
- **Short holds are cost-sensitive.** On a 30-day hold, the same {pct(FEE_SCENARIOS[0].round_trip_cost)} cost annualizes to {pct(FEE_SCENARIOS[0].round_trip_cost * 365.25 / 30)}, so BTC/ETH net annualized returns are materially compressed or negative depending on symbol and year.
- **For a 30k account with 50% deployed into the spot leg, BTC/ETH contribute roughly {pct(cap_min)} to {pct(cap_max)} annualized on total principal under a 20% futures-margin reserve.** That is about {fnum(cap_min * PRINCIPAL, 0)} to {fnum(cap_max * PRINCIPAL, 0)} account-currency units per year before tax, financing, borrow, transfer, operational, and liquidation-tail costs.
- **Conclusion: worth entering formal pre-registration only as a low-capacity, operations-heavy carry hypothesis, not as a standalone high-return strategy.** BTC/ETH pass the coarse historical cost screen; SOL remains reference-only because its funding is unstable and extreme-period mark volatility is much larger.

## Overall funding stream

Positive funding rate is treated as income to a 1-unit-notional perpetual short. Annualization uses each row's recorded `funding_interval_hours`.

{md_table(["symbol", "start", "end", "periods", "mean/period", "annualized", "negative share", "longest negative run"], overall_rows)}

## Year-by-year funding accounting

Annualized values use each row's recorded funding interval in each calendar year. 2026 is partial through the available June 5 files.

{md_table(["symbol", "year", "periods", "obs days", "sum funding", "annualized", "negative share", "longest negative run"], yearly_rows)}

## Cost sensitivity and break-even hold

Round-trip cost includes opening and closing both spot and perpetual legs. Slippage is kept at 0.10% per side in both fee scenarios.

{md_table(["symbol", "fee scenario", "hold days", "round-trip cost", "ann cost drag", "net ann notional", "break-even days"], cost_rows)}

## Capital efficiency on 30k principal

Assumption: 50% of capital buys spot with no leverage, matching perpetual short notional is 15k, and the remaining capital funds margin plus cash buffer. Net return uses 365-day cost amortization.

{md_table(["symbol", "fee scenario", "perp margin", "spot notional", "margin req", "cash buffer", "net ann principal", "net annual cash"], cap_rows)}

## Mark-volatility proxy for basis risk

No spot history is available in this task, so this is **not** a basis calculation. It only describes mark-price volatility in the 24h window after fixed-threshold extreme funding periods (`|funding| >= 0.10%/8h`).

{md_table(["symbol", "extreme periods", "neg extremes", "pos extremes", "median abs 24h ret", "p90 abs 24h ret", "max abs 24h ret", "max 24h range"], proxy_rows)}

Interpretation: the proxy says the periods when funding is most attractive or most punitive often coincide with large mark moves, especially SOL. A formal pre-registration needs actual spot-versus-perp basis data and explicit margin/liquidation rules before any live sizing decision.

## Limitations and assumptions

- No spot OHLC data was available or read, so basis, execution mismatch, and spot-perp divergence are not measured directly.
- This is not a strategy backtest: it assumes continuous hold for accounting and does not introduce entry, exit, timing, or selection rules.
- Funding data is treated as the realized cashflow source; exchange outages, settlement errors, borrow constraints, transfer costs, tax, capital controls, and idle-cash yield are outside scope.
- BNB-discount sensitivity applies lower fees only; slippage remains conservative at 0.10% per side.
- Mark-volatility proxy uses a fixed 0.10%/8h extreme threshold, not a sample-derived percentile.

## Recommendation

Enter formal pre-registration for BTC/ETH only if the next task explicitly adds spot history, basis measurement, liquidation/margin stress, execution workflow, and capital-efficiency constraints. Do not pre-register SOL carry as a primary hypothesis from this evidence.

## Source files

{chr(10).join(source_lines)}
"""


def build_task_report(generated_utc: str, result_path: Path, output_paths: list[Path]) -> str:
    outputs = "\n".join(f"- `{p.relative_to(ROOT)}`" for p in output_paths)
    return f"""# REPORT_CARRY_FEASIBILITY

**Generated UTC:** {generated_utc}  
**Task:** `TASK_CARRY_FEASIBILITY`  
**Status:** completed

## Execution Summary

Implemented `06_RESEARCH/CODE/carry_feasibility.py` and generated the historical carry-feasibility accounting report at `{result_path.relative_to(ROOT)}`.

## Required Deliverables

- CODE: `06_RESEARCH/CODE/carry_feasibility.py`
- RESULTS: `{result_path.relative_to(ROOT)}`
- Supporting outputs:
{outputs}

## Scope and Prohibition Self-Check

- Pure historical accounting only: yes.
- Trading signal / timing design: none.
- HOLDOUT read: no; script reads only `06_RESEARCH/DATA/FUTURES`.
- Pre-registration documents modified: no.
- Full-sample percentile threshold: no; extreme funding proxy uses fixed `|funding| >= 0.10%/8h`.
- Cost simplification: no; spot + perp open/close costs include fee and 0.10% per-side slippage.
- Git commit: not performed because the task sheet explicitly prohibits commit.

## Acceptance Checklist

- Historical funding income stream by year: done for BTC/ETH/SOL.
- Negative funding share and longest negative streak: done.
- 30/90/365-day cost amortization and break-even hold: done.
- Funding extreme mark-volatility proxy with limitation: done.
- 30k principal capital-efficiency range: done.
- VIP0 vs BNB fee-discount sensitivity: done.
- Conclusion on formal pre-registration: done.
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    sources: dict[str, list[dict]] = {}
    yearly: list[dict] = []
    overall: list[dict] = []
    proxies: list[dict] = []

    for symbol in SYMBOLS:
        funding_files = [p for p in [DATA_DIR / f"{symbol}_FUNDING_8H.csv", DATA_DIR / f"{symbol}_FUNDING_8H_2026H1.csv"] if p.exists()]
        mark_files = [p for p in [DATA_DIR / f"{symbol}_MARK_4H.csv", DATA_DIR / f"{symbol}_MARK_4H_2026H1.csv"] if p.exists()]
        sources[symbol] = [
            {"file": str(p.relative_to(ROOT)), "sha256": file_sha256(p), "rows": sum(1 for _ in p.open("r", encoding="utf-8")) - 1}
            for p in [*funding_files, *mark_files]
        ]
        funding = read_concat_csv(symbol, "FUNDING_8H")
        mark = read_concat_csv(symbol, "MARK_4H")
        yearly_rows, overall_row = funding_stats(symbol, funding)
        yearly.extend(yearly_rows)
        overall.append(overall_row)
        proxies.append(mark_proxy(symbol, funding, mark))

    costs = cost_sensitivity(overall)
    cap_eff = capital_efficiency(costs)

    yearly_path = OUTPUT_DIR / "carry_feasibility_yearly.csv"
    overall_path = OUTPUT_DIR / "carry_feasibility_overall.csv"
    cost_path = OUTPUT_DIR / "carry_feasibility_cost_sensitivity.csv"
    proxy_path = OUTPUT_DIR / "carry_feasibility_mark_proxy.csv"
    cap_path = OUTPUT_DIR / "carry_feasibility_capital_efficiency.csv"
    summary_path = OUTPUT_DIR / "carry_feasibility_summary.json"
    result_path = RESULTS_DIR / "20260612_carry_feasibility.md"
    task_report_path = TASKS_DIR / "REPORT_CARRY_FEASIBILITY.md"

    write_csv(yearly_path, yearly)
    write_csv(overall_path, overall)
    write_csv(cost_path, costs)
    write_csv(proxy_path, proxies)
    write_csv(cap_path, cap_eff)

    summary = {
        "task_id": TASK_ID,
        "seed": SEED,
        "generated_utc": generated_utc,
        "read_boundary": "06_RESEARCH/DATA/FUTURES only",
        "funding_extreme_abs_rate": FUNDING_EXTREME_ABS_RATE,
        "fee_scenarios": [asdict(s) | {"round_trip_cost": s.round_trip_cost} for s in FEE_SCENARIOS],
        "sources": sources,
        "overall": overall,
        "yearly": yearly,
        "cost_sensitivity": costs,
        "mark_proxy": proxies,
        "capital_efficiency": cap_eff,
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    result_md = build_result_markdown(generated_utc, sources, overall, yearly, costs, proxies, cap_eff)
    result_path.write_text(result_md, encoding="utf-8")

    output_paths = [overall_path, yearly_path, cost_path, proxy_path, cap_path, summary_path]
    task_report_path.write_text(build_task_report(generated_utc, result_path, output_paths), encoding="utf-8")

    print(f"Wrote {result_path.relative_to(ROOT)}")
    print(f"Wrote {task_report_path.relative_to(ROOT)}")
    for path in output_paths:
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
