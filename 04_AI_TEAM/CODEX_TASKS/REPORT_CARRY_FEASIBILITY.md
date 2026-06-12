# REPORT_CARRY_FEASIBILITY

**Generated UTC:** 2026-06-12 07:14:55 UTC  
**Task:** `TASK_CARRY_FEASIBILITY`  
**Status:** completed

## Execution Summary

Implemented `06_RESEARCH/CODE/carry_feasibility.py` and generated the historical carry-feasibility accounting report at `06_RESEARCH/RESULTS/20260612_carry_feasibility.md`.

## Required Deliverables

- CODE: `06_RESEARCH/CODE/carry_feasibility.py`
- RESULTS: `06_RESEARCH/RESULTS/20260612_carry_feasibility.md`
- Supporting outputs:
- `06_RESEARCH/CODE/output/carry_feasibility_overall.csv`
- `06_RESEARCH/CODE/output/carry_feasibility_yearly.csv`
- `06_RESEARCH/CODE/output/carry_feasibility_cost_sensitivity.csv`
- `06_RESEARCH/CODE/output/carry_feasibility_mark_proxy.csv`
- `06_RESEARCH/CODE/output/carry_feasibility_capital_efficiency.csv`
- `06_RESEARCH/CODE/output/carry_feasibility_summary.json`

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
