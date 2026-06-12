# TSMOM 扩样本·多空双引擎 v1

UTC run timestamp: 2026-06-12 11:30:21+0000

## 判定

- 引擎 L：FAILED
- 引擎 S：FAILED

两引擎按预登记独立判定，未合并粉饰；8 币仍是存活至今子集，幸存者偏差未完全消除。

## Holdout 边界审计

- 硬 cutoff：2024-12-09 23:59:00
- 回测脚本未读取 `*_2026H1` 增量文件；行情/资金费以固定 pre-cutoff 行数读取，DataFrame 末条均 <= cutoff。
- 会话审计事故：本次 Codex 会话中一次仓库级 `rg` 范围过宽，命中并显示了 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv` 的若干行；该文件未进入本策略计算，但全局 no-Holdout 自证失败。

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

## 四件套与第五件

| engine | E[R] | win/loss | P(DD>=35%) | P(DD>=20%) | log growth | positive years | WF +/3 | benchmark excess | decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| L | 0.066073 | 3.828 | 0.297 | 0.817 | 0.559 | 4/4 | 2/3 | 168664.44 | FAILED |
| S | -0.004835 | 1.376 | 0.101 | 0.591 | -0.068 | 1/4 | 1/3 | -28532.14 | FAILED |

## 参数对照

| item | P1-06 frozen | dual-engine implementation |
|---|---:|---:|
| lookback_bars | 540 | 540 |
| ADX period/entry/exit | 14 / 25 / 20 | 14 / 25 / 20 |
| macro SMA days | 200 | 200 |
| execution | t+1 open | t+1 open |
| leverage cap | 1.0 | 1.0 |
| target weight | 1/3 for 3 symbols | 1/N current PIT-eligible symbols |
| fee each side | 0.0005 in legacy P1-06 code | 0.001 per Protocol v1.3/AGENTS |
| slippage each side | 0.001 | 0.001 |
| funding | real 8H direction-aware | real 8H direction-aware |

## 组合描述

- L/S daily return correlation: -0.068
- L+S annualized log growth: 0.279
- L-only annualized log growth: 0.559
- Correlation vs existing P1-06 daily equity output: 0.46926547205572167

## P1-04/P1-06 第五件追溯

- P1-04 recomputed excess vs ADX-trend passive benchmark: -12745.95
- P1-06 recomputed excess vs macro-bull passive benchmark: -1101379.86

## 产出

- `06_RESEARCH/CODE/tsmom_dual_engine.py`
- `06_RESEARCH/CODE/output/tsmom_dual_L_trades.csv`
- `06_RESEARCH/CODE/output/tsmom_dual_L_equity.csv`
- `06_RESEARCH/CODE/output/tsmom_dual_L_metrics.json`
- `06_RESEARCH/CODE/output/tsmom_dual_S_trades.csv`
- `06_RESEARCH/CODE/output/tsmom_dual_S_equity.csv`
- `06_RESEARCH/CODE/output/tsmom_dual_S_metrics.json`
