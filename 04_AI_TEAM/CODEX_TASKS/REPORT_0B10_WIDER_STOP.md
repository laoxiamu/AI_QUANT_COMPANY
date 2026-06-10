# 执行报告 TASK-0B10 v6b 止损位置对照

**执行时间：** 2026-06-06  
**执行人：** Codex  
**任务状态：** COMPLETED  
**实验结论：** FAILED

## 关键纠错

任务书将 `ref_low` 称为更宽止损，但冻结的 Bullish Sweep 定义要求
`sweep_low < ref_low`。对多头而言，`ref_low` 更高、更靠近入场价，实际是
更紧止损。预登记已在运行前明确该矛盾，报告与代码均未沿用错误解释。

## 产物

- `06_RESEARCH/CODE/v10_wider_stop_backtest.py`
- `06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v6b.md`
- `06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v6b_BACKTEST.md`
- `06_RESEARCH/CODE/output/v6b_strategy_metrics.json`
- `06_RESEARCH/CODE/output/v6b_strategy_trades.csv`
- `06_RESEARCH/CODE/output/v6b_strategy_equity_curve.csv`
- `06_RESEARCH/CODE/output/v6b_strategy_equity_curve.png`
- `06_RESEARCH/CODE/output/v6b_strategy_baseline_trades.csv`
- `06_RESEARCH/CODE/output/v6b_strategy_baseline_equity_curve.csv`
- `06_RESEARCH/CODE/output/v6b_strategy_baseline_equity_curve.png`
- `06_RESEARCH/CODE/output/v6b_strategy_btc_eth_trades.csv`
- `06_RESEARCH/CODE/output/v6b_strategy_baseline_btc_eth_trades.csv`
- `06_RESEARCH/CODE/output/v6b_strategy_stop_tightening_distribution.png`

未修改 Memory Core、`00_PROJECT_MANAGEMENT/` 或根目录 `CLAUDE.md`。

## 同口径现场双跑

v6 尚未完成，本任务没有引用既有 v6 数字。同一脚本、同一固定数据快照现场
运行：

| 组合 | 版本 | 交易 | 净收益 | Sharpe | MaxDD | Expectancy |
|------|------|-----:|-------:|-------:|------:|-----------:|
| BTC+ETH+SOL | `sweep_low+t+12` | 373 | +132.61% | 0.87 | 36.32% | +0.279R |
| BTC+ETH+SOL | `ref_low+t+12` | 373 | +317.95% | 1.22 | 28.45% | +1.009R |
| BTC+ETH | `sweep_low+t+12` | 297 | +102.14% | 0.86 | 26.65% | +0.286R |
| BTC+ETH | `ref_low+t+12` | 295 | +131.16% | 0.92 | 22.57% | +0.415R |

三品种 candidate 因 MaxDD 超过 25% 失败；BTC+ETH candidate 因 Sharpe
未超过 1.0 失败。

## 执行审计

- 425/425 事件满足 `sweep_low < ref_low`；
- `entry <= stop` 无效风险：baseline 0，candidate 0；
- 三品种止损率：58.71% → 71.85%；
- 平均止损收紧：约价格的 0.95%；
- 平均风险距离：2.33% → 1.37%；
- 平均初始名义仓位：99,365 → 165,972 USDT；
- 1x 上限缩放入场：134 → 246；
- 历史资金费率真实读取，缺口按 `0.01%/8h`；
- Holdout 固定 `nrows` 物理截断，未读取；
- 原有回测规则测试：3/3 通过；
- 正式脚本完成后复跑结果一致。

## SOL

SOL 独立 candidate：净收益 +146.97%，Sharpe 1.34，MaxDD 17.62%。
本次 SOL 不是拖累；三品种组合也优于 BTC+ETH。该结果不自动构成 SOL-only
新假设，禁止据此查看 Holdout。

## Claude 待处理事项

1. 建议记录 v6 baseline：三品种 Sharpe 0.87 / MaxDD 36.32%，BTC+ETH
   Sharpe 0.86 / MaxDD 26.65%，均 FAILED；
2. 建议记录 v6b：三品种 Sharpe 1.22 / MaxDD 28.45%，BTC+ETH Sharpe
   0.92 / MaxDD 22.57%，均 FAILED；
3. 连续失败计数如何归属需 Claude 按任务链审阅：baseline 是 v6 现场结果，
   candidate 是 v6b；本报告不直接修改权威计数；
4. 必须保留语义纠错：`ref_low` 是更紧止损，不得在状态文档中称为更宽；
5. SOL 本次不构成拖累，若提出 SOL-only 研究须另行预登记，不能结果后追认；
6. 当前已接近连续失败止损线，是否触发 L3 审计由 Claude 按权威计数判断。

【需要Claude】
