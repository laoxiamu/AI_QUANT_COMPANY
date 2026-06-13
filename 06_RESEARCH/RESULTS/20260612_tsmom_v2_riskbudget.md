# TSMOM dual engine v2 risk budget

UTC run timestamp: 2026-06-12 16:44:37+0000

## 判定

- B1 二值判定：FAILED
- 解释：四件套、第五件与 WF 三段必须全过；任一失败即 FAILED。

## 机制与边界

- 机制：继承 v1 引擎 L，唯一新增变量为 25% 年化组合波动率目标缩放。
- 缩放：每根 4H 开盘用过去 42 根 4H 已完成组合收益计算 σ_t，k_t = min(1, 25%/σ_t)。
- 硬 cutoff：2024-12-09 23:59:00；未读取 `*_2026H1`，未读取 HOLDOUT。
- 成本：手续费 0.1%/边 + 滑点 0.1%/边 + 真实 8H funding。
- 基准：同门控 8 币等权买入持有，不缩放。

## 四件套与第五件

| criterion | value | pass |
|---|---:|---:|
| E[R] > 0 | 0.016321 | True |
| win/loss >= 1.5 | 2.074 | True |
| P(annual DD>=35%) <= 20% | 0.003 | True |
| P(annual DD>=20%) <= 10% | 0.174 | False |
| annualized log growth > 0 | 0.293 | True |
| positive years majority | 4/4 | True |
| WF positive windows >= 2/3 | 2/3 | True |
| benchmark excess > 0 | -992784.95 | False |

## v1 L 对比

| item | v1 L | v2 risk budget | delta |
|---|---:|---:|---:|
| ending_equity | 1587259.39 | 425810.00 | -1161449.39 |
| annualized_log_growth | 0.559 | 0.293 | -0.266 |
| max_drawdown | -0.412 | -0.236 | 0.176 |
| expectancy_r | 0.066073 | 0.016321 | -0.049752 |
| win_loss_ratio | 3.828 | 2.074 | -1.755 |
| P(DD>=35%) | 0.297 | 0.003 | -0.294 |
| P(DD>=20%) | 0.817 | 0.174 | -0.642 |

## 缩放审计

- min(k_t): 0.327937
- mean(k_t): 0.922358
- k_t < 1 bars: 2519
- k_t <= 1 invariant: True
- σ_t uses only `<t` equity history: True

## WF 三段

| window | start | end | trades | log growth | positive |
|---|---|---|---:|---:|---:|
| 1 | 2020-01-01 00:00:00 | 2021-08-24 12:00:00 | 198 | 0.606 | True |
| 2 | 2021-08-24 12:00:00 | 2023-04-18 04:00:00 | 29 | -0.019 | False |
| 3 | 2023-04-18 04:00:00 | 2024-12-10 00:00:00 | 214 | 0.297 | True |

## 数据审计

| symbol | bars last | funding last | bars rows | funding rows |
|---|---:|---:|---:|---:|
| BTC | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 10782 | 5415 |
| ETH | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 10818 | 5415 |
| SOL | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 9250 | 4720 |
| BNB | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 10596 | 5294 |
| XRP | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 10758 | 5399 |
| DOGE | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 9672 | 4841 |
| ADA | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 10708 | 5359 |
| LTC | 2024-12-09 20:00:00 | 2024-12-09 16:00:00 | 10769 | 5390 |

## 产出

- `06_RESEARCH/CODE/tsmom_dual_engine.py --riskbudget-v2`
- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_trades.csv`
- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_equity.csv`
- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_metrics.json`
- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_scales.csv`
