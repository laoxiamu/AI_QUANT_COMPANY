# 执行报告 TASK-0B4 v4 Strategy Backtest

**执行时间：** 2026-06-06  
**执行人：** Codex  
**任务状态：** COMPLETED  
**策略结论：** FAILED

## 产物

- `06_RESEARCH/CODE/v4_strategy_backtest.py`
- `06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_BACKTEST.md`
- `06_RESEARCH/CODE/output/v4_strategy_metrics.json`
- `06_RESEARCH/CODE/output/v4_strategy_trades.csv`
- `06_RESEARCH/CODE/output/v4_strategy_equity_curve.csv`
- `06_RESEARCH/CODE/output/v4_strategy_equity_curve.png`

未修改 Memory Core、`00_PROJECT_MANAGEMENT/` 或根目录 `CLAUDE.md`。

## 规格澄清

任务描述称事件 CSV 含 `sweep_low`，实际文件只有 `datetime`、`close`、
`ref_low` 等字段。程序没有把 `ref_low` 错当止损，而是用事件时间从物理截断
的 4H OHLCV 中读取 Sweep K线真实 `low`。信号检测未重新运行。

VectorBT 用于标准收益指标计算。分批止盈、止损优先、共享账户、资金费率与
持仓冲突由确定性逐K线执行层处理，因为这些规则无法由简单布尔 entry/exit
矩阵无损表达。

资金费率优先使用仓库已有的 Binance 历史 8H 数据；历史文件开始前和缺失的
标准结算点按任务指定值 `0.01%/8h` 补齐，没有把不可得区间按零处理。

## 核心结果

| 指标 | 结果 |
|------|-----:|
| 候选事件 | 425 |
| 实际交易 | 360 |
| 净收益率 | +20.11% |
| 年化收益率 | +2.97% |
| Sharpe | 0.31 |
| Sortino | 0.42 |
| MaxDD | 19.08% |
| 胜率 | 41.67% |
| 平均盈亏比 | 1.55 |
| Expectancy | +0.032R |
| 资金费率成本 | 6,334.97 USDT |
| 总手续费 | 17,888.37 USDT |

判定规则为 Sharpe>1.0 且 MaxDD<25%。MaxDD 通过，Sharpe 未通过，因此
策略 FAILED。

交易漏斗：425 候选 = 360 成交 + 63 同品种持仓冲突 + 2 已占满 1x
账户敞口；另有 125 笔成交因敞口上限缩小仓位。

## 失败原因

1. 风险调整收益不足：整体 Sharpe 仅 0.31；
2. 时期不稳定：2022 净收益 -6.51%，第三段 WF Sharpe 0.11；
3. 品种不稳定：SOL 净收益 -5.65%，Sharpe -0.14；
4. 成本侵蚀：手续费与资金费率合计约 24,223 USDT，消耗约 54.64% 毛收益；
5. 固定 Sweep-low 止损与 1R/2R 退出无法完整捕获事件研究中的长窗口均值。

## 与 v1/v2 对比

| 实验 | Sharpe | MaxDD |
|------|-------:|------:|
| v1 4H 三重确认 | 0.60 | 33.14% |
| v2 1H 三重确认 | 0.90 | 36.61% |
| v4 完整策略 | 0.31 | 19.08% |

回撤改善，但 Sharpe 下降，不构成整体策略改善。

## Claude 待处理事项

### 1. CURRENT_STATE 建议更新

- v4 完整策略回测：COMPLETED / FAILED；
- 425 候选，360 实际交易；
- 净收益 +20.11%，年化 +2.97%；
- Sharpe 0.31，Sortino 0.42，MaxDD 19.08%；
- Expectancy +0.032R，资金费率 6,334.97 USDT；
- WF Sharpe：0.85 → 0.34 → 0.11；
- 2022 -6.51%，SOL -5.65%；
- Holdout 未读取。

### 2. 结论建议

不建议将 v4 多头策略升级为实盘候选。事件研究通过说明存在条件收益分布，
但当前预登记执行规则没有形成足够高的风险调整收益。

### 3. 是否设计双向策略

应等待 `v5_sweep_regime_bear_v5` 的独立做空事件研究结果。只有做空方向在
多头薄弱时期提供独立且稳定的负向收益证据，才值得预登记双向完整策略；
不得仅因本回测失败直接拼接方向或调整退出参数。

### 4. DECISION_LOG 草稿

```text
决策草稿：v4 Sweep 双层 Regime 事件信号保留为研究证据，但其当前完整多头
策略实现不进入实盘候选。依据：净收益为正且 MaxDD 19.08%，但 Sharpe 0.31，
Walk-Forward 明显衰减，SOL 与 2022 为负。后续是否设计双向策略须以独立
Bearish Sweep 研究结果为前置条件。状态：需 Claude 审阅。
```

【需要Claude】
