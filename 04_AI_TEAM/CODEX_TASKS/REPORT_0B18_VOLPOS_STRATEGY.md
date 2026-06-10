# 执行报告 TASK-0B18 波动率缩仓策略

**执行时间：** 2026-06-06  
**执行人：** Codex  
**状态：** COMPLETED  
**实验结论：** **FAILED / 机制无效**

## 核心结果

- Sharpe：**0.7765**，未达到 `>1.0`
- MaxDD：**14.0347%**，满足 `<25%`
- 净收益率：+32.26%
- 交易数：236
- 止损率：22.46%
- 平均名义仓位：13.39%

相较 0B17 ATR×3.5，Sharpe 从 0.9453 降至 0.7765，MaxDD 从 14.93%
降至 14.03%。回撤小幅改善，但风险调整收益明显恶化。

## 机制结论

冻结的 BTC 波动率百分位没有识别 2022：

- 2022 高恐惧候选：0/12；
- 2022 高恐惧成交：0/7；
- WF2 Sharpe：-0.6127 → -0.6127；
- 2022 Sharpe：-1.8702 → -1.8702；
- 标准化收益率完全不变。

高恐惧成交反而主要来自 2021，且胜率 71.70%、止损率 13.21%、
Expectancy +0.382R。缩仓削弱的是历史高质量交易。WF1 Sharpe
2.84→2.58，收益率 37.79%→25.54%。

## 单变量与数值审计

- 由 `v17_atr_strategy.py` 机械复制；
- 唯一行为改动：基础数量乘冻结 `vol_scalar`；
- 所有 236 笔退出时间、原因与 0B17 ATR×3.5 一致；
- 高恐惧仓位比例逐笔 0.5，低恐惧逐笔 1.0；
- 百分位独立重算误差 `<2e-16`；
- ATR 距离误差 `<2e-11`；
- 时间退出全部为第 24 根；
- 最高敞口 0.8450x，单笔上限未突破；
- 成本三项与 0B17 一致；
- pytest 9/9 通过；
- Holdout 未读取。

## 红队自查

| 检查项 | 状态 |
|--------|------|
| 单变量边界 | PASS |
| 百分位无前视 | PASS |
| ATR 与 v16/v17 一致 | PASS |
| 冻结常数未改 | PASS |
| 成本完整 | PASS |
| Holdout 未读取 | PASS |
| 1x/单笔上限 | PASS |
| 自动测试 | PASS（9/9） |

## 产物

- `06_RESEARCH/CODE/v18_volpos_strategy.py`
- `06_RESEARCH/RESULTS/20260606_volpos_strategy.md`
- `06_RESEARCH/CODE/output/v18_volpos_metrics.json`
- `06_RESEARCH/CODE/output/v18_volpos_trades.csv`
- `06_RESEARCH/CODE/output/v18_volpos_equity.csv`
- `06_RESEARCH/CODE/output/v18_volpos_candidates_audit.csv`
- `06_RESEARCH/CODE/output/v18_volpos_equity_curve.png`

## Claude 待处理事项

1. 将 0B18 记录为 FAILED，并确认机制无效；
2. 按 DEC-044/046 并列更新：
   历史实验失败 **7→8**、独立 Alpha 失败仍 **4/8**、v4 实现线 CLOSED；
3. 记录失败原因：恐惧度 gauge 未识别 2022，反而缩减 2021 优质交易；
4. 永久停止 v4 的止损、退出、仓位和恐惧度变体；
5. Holdout 继续封存，v4 不进入 Holdout；
6. 下一步只能是全新独立 Alpha 假设，需重新预登记；
7. 由 Claude 更新 `CURRENT_STATE.md` 和相关决策状态。

【需要Claude】
