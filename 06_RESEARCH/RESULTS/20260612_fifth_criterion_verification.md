# B2 第五件追溯复算验证

UTC run timestamp: 2026-06-12T16:52:23.082899+00:00

## 结论

独立复算显示，按 P1 冻结快照和 B2 字面门控口径：P1-04 第五件失败，P1-06 第五件通过。
P1-06 昨日报告中的 `-1,101,379.86` 不能作为 P1-06 冻结窗口第五件结论；根因是追溯包装使用了扩样本数据/窗口口径，而不是交易 P&L 算术反号、成本方向或 funding 方向错误。

## 主对照表

| experiment | strategy ending equity | benchmark ending equity | excess | fifth pass |
|---|---:|---:|---:|---|
| P1-04 | 1413672.48 | 1694715.61 | -281043.13 | False |
| P1-06 | 954160.04 | 703090.24 | 251069.80 | True |

## 与昨日内置追溯的差异

| item | yesterday tsmom_dual_engine.py | B2 independent recompute | delta |
|---|---:|---:|---:|
| P1-04 excess | -12745.95 | -281043.13 | -268297.18 |
| P1-06 excess | -1101379.86 | 251069.80 | 1352449.66 |

根因判断：

1. 不是基准函数把符号、成本或 funding 方向写反导致的算术 bug；本次同成本、同 funding 方向下可复算出自洽结果。
2. 差异主要是口径差/追溯包装问题：昨日追溯用 `06_RESEARCH/DATA/FUTURES/*_MARK_4H.csv` 的 2020 起扩样本窗口和 PIT/cutoff 逻辑；本次按 P1 冻结快照读取根目录三币 4H 文件的研究行，窗口从 2019-01-01 起，SOL 从上市快照起。
3. B2 主口径按任务书字面定义基准：P1-04=ADX趋势窗，P1-06=宏观牛市窗；不叠加 TSMOM 动量信号。
4. 当前成本口径为 fee 0.1%/边 + slippage 0.1%/边 + 真实 funding；旧 P1 输出为 fee 0.05%/边，因此旧 P1 终值只作为参考，不用于主判定。

## 旧 P1 输出参考

| experiment | old output ending equity | B2 strategy ending equity | difference |
|---|---:|---:|---:|
| P1-04 | 1608559.60 | 1413672.48 | -194887.11 |
| P1-06 | 1056648.20 | 954160.04 | -102488.16 |

## 数据与边界

- 未读取 `06_RESEARCH/DATA/HOLDOUT/`；未读取 `*_2026H1`。
- 行情使用 P1 legacy 冻结快照的 pre-Holdout `nrows`；资金费使用对应 pre-Holdout `nrows`。
- 会话审计：任务早期一次 `find` 文件枚举显示了 HOLDOUT 路径名，但未打开或读取 HOLDOUT 文件内容；后续搜索均排除 HOLDOUT。

| symbol | bars rows | bars first | bars last | funding rows | funding last | holdout start |
|---|---:|---:|---:|---:|---:|---:|
| BTC | 13013 | 2019-01-01 00:00:00 | 2024-12-09 12:00:00 | 5414 | 2024-12-09 08:00:00 | 2024-12-09 16:00:00 |
| ETH | 13013 | 2019-01-01 00:00:00 | 2024-12-09 12:00:00 | 5414 | 2024-12-09 08:00:00 | 2024-12-09 16:00:00 |
| SOL | 10194 | 2020-08-11 04:00:00 | 2025-04-06 00:00:00 | 4997 | 2025-03-12 00:00:00 | 2025-04-06 04:00:00 |

## 产出

- `06_RESEARCH/CODE/b2_fifth_criterion_verification.py`
- `06_RESEARCH/CODE/output/b2_fifth_criterion_verification.json`
- `06_RESEARCH/CODE/output/b2_fifth_criterion_comparison.csv`
- `06_RESEARCH/CODE/output/b2_*_equity.csv` / `b2_*_trades.csv`
