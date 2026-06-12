# Delta-neutral carry feasibility accounting

**Generated UTC:** 2026-06-12 07:14:55 UTC  
**Task:** TASK_CARRY_FEASIBILITY  
**Nature:** pure historical accounting; not a strategy backtest; no trading signal or timing design.  
**Data boundary:** read only `06_RESEARCH/DATA/FUTURES`; did not read `06_RESEARCH/DATA/HOLDOUT`.

## Executive Summary

- **BTC/ETH still cover conservative double-leg costs on a 365-day hold.** With the task-mandated VIP0 conservative cost of 0.80% round trip, BTC/ETH net annualized carry on notional is 11.24% to 13.55% after amortizing one open/close over 365 days.
- **Short holds are cost-sensitive.** On a 30-day hold, the same 0.80% cost annualizes to 9.74%, so BTC/ETH net annualized returns are materially compressed or negative depending on symbol and year.
- **For a 30k account with 50% deployed into the spot leg, BTC/ETH contribute roughly 5.62% to 6.77% annualized on total principal under a 20% futures-margin reserve.** That is about 1686 to 2032 account-currency units per year before tax, financing, borrow, transfer, operational, and liquidation-tail costs.
- **Conclusion: worth entering formal pre-registration only as a low-capacity, operations-heavy carry hypothesis, not as a standalone high-return strategy.** BTC/ETH pass the coarse historical cost screen; SOL remains reference-only because its funding is unstable and extreme-period mark volatility is much larger.

## Overall funding stream

Positive funding rate is treated as income to a 1-unit-notional perpetual short. Annualization uses each row's recorded `funding_interval_hours`.

| symbol  | start      | end        | periods           | mean/period | annualized | negative share | longest negative run |
| ------- | ---------- | ---------- | ----------------- | ----------- | ---------- | -------------- | -------------------- |
| BTCUSDT | 2020-01-01 | 2026-06-05 | 7044 (0 non-8h)   | 0.0110%     | 12.04%     | 14.37%         | 24 (8.0d)            |
| ETHUSDT | 2020-01-01 | 2026-06-05 | 7044 (0 non-8h)   | 0.0131%     | 14.35%     | 13.66%         | 25 (8.3d)            |
| SOLUSDT | 2020-09-13 | 2026-06-05 | 6349 (101 non-8h) | 0.0001%     | 0.13%      | 28.10%         | 53 (15.2d)           |

## Year-by-year funding accounting

Annualized values use each row's recorded funding interval in each calendar year. 2026 is partial through the available June 5 files.

| symbol  | year | periods | obs days | sum funding | annualized | negative share | longest negative run |
| ------- | ---- | ------- | -------- | ----------- | ---------- | -------------- | -------------------- |
| BTCUSDT | 2020 | 1098    | 366.0    | 17.24%      | 17.20%     | 14.30%         | 24 (8.0d)            |
| BTCUSDT | 2021 | 1095    | 365.0    | 30.61%      | 30.63%     | 7.31%          | 9 (3.0d)             |
| BTCUSDT | 2022 | 1095    | 365.0    | 4.16%       | 4.17%      | 22.10%         | 10 (3.3d)            |
| BTCUSDT | 2023 | 1095    | 365.0    | 7.87%       | 7.87%      | 10.14%         | 7 (2.3d)             |
| BTCUSDT | 2024 | 1098    | 366.0    | 11.96%      | 11.93%     | 8.38%          | 18 (6.0d)            |
| BTCUSDT | 2025 | 1095    | 365.0    | 5.13%       | 5.13%      | 12.88%         | 10 (3.3d)            |
| BTCUSDT | 2026 | 468     | 156.0    | 0.42%       | 0.99%      | 40.38%         | 14 (4.7d)            |
| ETHUSDT | 2020 | 1098    | 366.0    | 27.49%      | 27.43%     | 2.64%          | 3 (1.0d)             |
| ETHUSDT | 2021 | 1095    | 365.0    | 37.54%      | 37.56%     | 4.11%          | 6 (2.0d)             |
| ETHUSDT | 2022 | 1095    | 365.0    | 0.79%       | 0.79%      | 34.16%         | 25 (8.3d)            |
| ETHUSDT | 2023 | 1095    | 365.0    | 8.26%       | 8.27%      | 9.13%          | 8 (2.7d)             |
| ETHUSDT | 2024 | 1098    | 366.0    | 13.00%      | 12.97%     | 4.19%          | 12 (4.0d)            |
| ETHUSDT | 2025 | 1095    | 365.0    | 4.93%       | 4.93%      | 16.16%         | 5 (1.7d)             |
| ETHUSDT | 2026 | 468     | 156.0    | 0.24%       | 0.56%      | 40.81%         | 16 (5.3d)            |
| SOLUSDT | 2020 | 328     | 109.3    | -3.75%      | -12.53%    | 25.30%         | 21 (7.0d)            |
| SOLUSDT | 2021 | 1095    | 365.0    | 28.59%      | 28.61%     | 4.75%          | 9 (3.0d)             |
| SOLUSDT | 2022 | 1170    | 364.9    | -38.00%     | -38.03%    | 45.81%         | 53 (15.2d)           |
| SOLUSDT | 2023 | 1095    | 365.0    | 1.30%       | 1.30%      | 28.13%         | 25 (8.3d)            |
| SOLUSDT | 2024 | 1098    | 366.0    | 13.66%      | 13.63%     | 10.29%         | 7 (2.3d)             |
| SOLUSDT | 2025 | 1095    | 365.0    | 0.35%       | 0.35%      | 39.45%         | 12 (4.0d)            |
| SOLUSDT | 2026 | 468     | 156.0    | -1.41%      | -3.30%     | 55.56%         | 21 (7.0d)            |

## Cost sensitivity and break-even hold

Round-trip cost includes opening and closing both spot and perpetual legs. Slippage is kept at 0.10% per side in both fee scenarios.

| symbol  | fee scenario                 | hold days | round-trip cost | ann cost drag | net ann notional | break-even days |
| ------- | ---------------------------- | --------- | --------------- | ------------- | ---------------- | --------------- |
| BTCUSDT | VIP0_task_conservative       | 30        | 0.80%           | 9.74%         | 2.30%            | 24.3            |
| BTCUSDT | VIP0_task_conservative       | 90        | 0.80%           | 3.25%         | 8.79%            | 24.3            |
| BTCUSDT | VIP0_task_conservative       | 365       | 0.80%           | 0.80%         | 11.24%           | 24.3            |
| BTCUSDT | BNB_fee_discount_sensitivity | 30        | 0.73%           | 8.89%         | 3.15%            | 22.1            |
| BTCUSDT | BNB_fee_discount_sensitivity | 90        | 0.73%           | 2.96%         | 9.08%            | 22.1            |
| BTCUSDT | BNB_fee_discount_sensitivity | 365       | 0.73%           | 0.73%         | 11.31%           | 22.1            |
| ETHUSDT | VIP0_task_conservative       | 30        | 0.80%           | 9.74%         | 4.61%            | 20.4            |
| ETHUSDT | VIP0_task_conservative       | 90        | 0.80%           | 3.25%         | 11.10%           | 20.4            |
| ETHUSDT | VIP0_task_conservative       | 365       | 0.80%           | 0.80%         | 13.55%           | 20.4            |
| ETHUSDT | BNB_fee_discount_sensitivity | 30        | 0.73%           | 8.89%         | 5.46%            | 18.6            |
| ETHUSDT | BNB_fee_discount_sensitivity | 90        | 0.73%           | 2.96%         | 11.39%           | 18.6            |
| ETHUSDT | BNB_fee_discount_sensitivity | 365       | 0.73%           | 0.73%         | 13.62%           | 18.6            |
| SOLUSDT | VIP0_task_conservative       | 30        | 0.80%           | 9.74%         | -9.61%           | 2259.2          |
| SOLUSDT | VIP0_task_conservative       | 90        | 0.80%           | 3.25%         | -3.12%           | 2259.2          |
| SOLUSDT | VIP0_task_conservative       | 365       | 0.80%           | 0.80%         | -0.67%           | 2259.2          |
| SOLUSDT | BNB_fee_discount_sensitivity | 30        | 0.73%           | 8.89%         | -8.76%           | 2061.5          |
| SOLUSDT | BNB_fee_discount_sensitivity | 90        | 0.73%           | 2.96%         | -2.83%           | 2061.5          |
| SOLUSDT | BNB_fee_discount_sensitivity | 365       | 0.73%           | 0.73%         | -0.60%           | 2061.5          |

## Capital efficiency on 30k principal

Assumption: 50% of capital buys spot with no leverage, matching perpetual short notional is 15k, and the remaining capital funds margin plus cash buffer. Net return uses 365-day cost amortization.

| symbol  | fee scenario                 | perp margin | spot notional | margin req | cash buffer | net ann principal | net annual cash |
| ------- | ---------------------------- | ----------- | ------------- | ---------- | ----------- | ----------------- | --------------- |
| BTCUSDT | VIP0_task_conservative       | 10%         | 15000         | 1500       | 13500       | 5.62%             | 1686            |
| BTCUSDT | VIP0_task_conservative       | 20%         | 15000         | 3000       | 12000       | 5.62%             | 1686            |
| BTCUSDT | VIP0_task_conservative       | 50%         | 15000         | 7500       | 7500        | 5.62%             | 1686            |
| BTCUSDT | BNB_fee_discount_sensitivity | 10%         | 15000         | 1500       | 13500       | 5.65%             | 1696            |
| BTCUSDT | BNB_fee_discount_sensitivity | 20%         | 15000         | 3000       | 12000       | 5.65%             | 1696            |
| BTCUSDT | BNB_fee_discount_sensitivity | 50%         | 15000         | 7500       | 7500        | 5.65%             | 1696            |
| ETHUSDT | VIP0_task_conservative       | 10%         | 15000         | 1500       | 13500       | 6.77%             | 2032            |
| ETHUSDT | VIP0_task_conservative       | 20%         | 15000         | 3000       | 12000       | 6.77%             | 2032            |
| ETHUSDT | VIP0_task_conservative       | 50%         | 15000         | 7500       | 7500        | 6.77%             | 2032            |
| ETHUSDT | BNB_fee_discount_sensitivity | 10%         | 15000         | 1500       | 13500       | 6.81%             | 2043            |
| ETHUSDT | BNB_fee_discount_sensitivity | 20%         | 15000         | 3000       | 12000       | 6.81%             | 2043            |
| ETHUSDT | BNB_fee_discount_sensitivity | 50%         | 15000         | 7500       | 7500        | 6.81%             | 2043            |

## Mark-volatility proxy for basis risk

No spot history is available in this task, so this is **not** a basis calculation. It only describes mark-price volatility in the 24h window after fixed-threshold extreme funding periods (`|funding| >= 0.10%/8h`).

| symbol  | extreme periods | neg extremes | pos extremes | median abs 24h ret | p90 abs 24h ret | max abs 24h ret | max 24h range |
| ------- | --------------- | ------------ | ------------ | ------------------ | --------------- | --------------- | ------------- |
| BTCUSDT | 92              | 3            | 89           | 2.17%              | 7.89%           | 13.24%          | 26.18%        |
| ETHUSDT | 151             | 7            | 144          | 3.09%              | 8.39%           | 22.22%          | 44.86%        |
| SOLUSDT | 218             | 122          | 96           | 5.50%              | 15.37%          | 51.81%          | 140.17%       |

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

- BTCUSDT: 06_RESEARCH/DATA/FUTURES/BTCUSDT_FUNDING_8H.csv sha256=5803cb5e8ffb rows=7029; 06_RESEARCH/DATA/FUTURES/BTCUSDT_FUNDING_8H_2026H1.csv sha256=d1af8ceff1a5 rows=15; 06_RESEARCH/DATA/FUTURES/BTCUSDT_MARK_4H.csv sha256=7127294528e6 rows=14010; 06_RESEARCH/DATA/FUTURES/BTCUSDT_MARK_4H_2026H1.csv sha256=a20868ae0c91 rows=30
- ETHUSDT: 06_RESEARCH/DATA/FUTURES/ETHUSDT_FUNDING_8H.csv sha256=e3333672e3dd rows=7029; 06_RESEARCH/DATA/FUTURES/ETHUSDT_FUNDING_8H_2026H1.csv sha256=d9455df4c770 rows=15; 06_RESEARCH/DATA/FUTURES/ETHUSDT_MARK_4H.csv sha256=53135ef7aca6 rows=14046; 06_RESEARCH/DATA/FUTURES/ETHUSDT_MARK_4H_2026H1.csv sha256=c36066e1255a rows=30
- SOLUSDT: 06_RESEARCH/DATA/FUTURES/SOLUSDT_FUNDING_8H.csv sha256=24456f2c9e71 rows=6334; 06_RESEARCH/DATA/FUTURES/SOLUSDT_FUNDING_8H_2026H1.csv sha256=78e9975b010c rows=15; 06_RESEARCH/DATA/FUTURES/SOLUSDT_MARK_4H.csv sha256=fc58a2e85afa rows=12478; 06_RESEARCH/DATA/FUTURES/SOLUSDT_MARK_4H_2026H1.csv sha256=5af950d485f3 rows=30
