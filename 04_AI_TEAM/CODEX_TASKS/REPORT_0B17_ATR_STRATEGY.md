# 执行报告 TASK-0B17 ATR 动态止损策略

**执行时间：** 2026-06-06  
**执行人：** Codex  
**状态：** COMPLETED  
**实验结论：** **FAILED**

## 预登记判定

ATR×1.9 三品种组合：

- Sharpe：**0.8572**，未达到 `>1.0`
- MaxDD：**24.7994%**，满足 `<25%`
- 联合门槛：**FAILED**
- 权威失败计数应由 Claude 从 **6/8 更新为 7/8**

## 核心结果

| 指标 | ATR×1.9 | ATR×3.5压力测试 |
|------|--------:|----------------:|
| Sharpe | 0.86 | 0.95 |
| MaxDD | 24.80% | 14.93% |
| 交易数 | 287 | 236 |
| 止损率 | 47.74% | 22.46% |
| 平均名义仓位 | 26.53% | 14.52% |
| 净收益率 | +75.08% | +45.87% |

压力测试不计独立失败，但也未达到 Sharpe 门槛。

## 稳定性

ATR×1.9 Walk-Forward Sharpe 为 **2.21 → -0.22 → 0.63**。2022 年 9 笔
交易中 7 笔止损，净亏 9,792.42 USDT，Sharpe -1.77。ATR 止损改善了风险
尺度，却没有修复 WF2 和后段信号质量。

## 品种

| 品种 | Sharpe | MaxDD | 交易 | 止损率 | 平均名义仓位 |
|------|-------:|------:|-----:|-------:|---------------:|
| BTC | 0.25 | 11.67% | 130 | 50.00% | 32.38% |
| ETH | 0.89 | 7.38% | 99 | 43.43% | 25.00% |
| SOL | 0.93 | 11.42% | 58 | 50.00% | 16.99% |

BTC 是最明显拖累，三品种均未独立超过 Sharpe 1。

## 执行审计

- DEC-042 在运行前已由 Claude 写入权威决策日志；
- ATR 算法与 `v16_atr_stop_diagnostic.py` 一致；
- ATR 风险距离逐笔最大数值误差 `<2e-11`；
- 150 笔时间退出全部为第 24 根 K线；
- 最高总敞口 0.9992x，单笔上限 100% 已实现；
- 费用按任务书：0.05%手续费/边、0.1%滑点/边、0.01%/8h资金费率；
- pytest 9/9 通过；
- Holdout 未读取；
- 未修改 Memory Core 或项目管理文件。

## 产物

- `06_RESEARCH/CODE/v17_atr_strategy.py`
- `06_RESEARCH/RESULTS/20260606_atr_strategy.md`
- `06_RESEARCH/CODE/output/v17_atr_metrics.json`
- `06_RESEARCH/CODE/output/v17_atr_trades.csv`
- `06_RESEARCH/CODE/output/v17_atr_1.9_trades.csv`
- `06_RESEARCH/CODE/output/v17_atr_3.5_trades.csv`
- `06_RESEARCH/CODE/output/v17_atr_1.9_equity.csv`
- `06_RESEARCH/CODE/output/v17_atr_3.5_equity.csv`
- `06_RESEARCH/CODE/output/v17_atr_equity_curve.png`

## Claude 待处理事项

1. 将 0B17 记录为 FAILED，并将权威失败计数更新为 **7/8**；
2. 记录主结果：Sharpe 0.86 / MaxDD 24.80% / 止损率 47.74%；
3. 记录压力测试：Sharpe 0.95 / MaxDD 14.93%，仍未通过；
4. 更新 `CURRENT_STATE.md`，标明 ATR 止损解决部分回撤问题，但未解决
   WF2/WF3 稳定性；
5. 建议现在进入 L3 审计准备，不要直接测试第 8 个变体；
6. Holdout 继续封存，不建议因 MaxDD 接近门槛而破例查看。

【需要Claude】
