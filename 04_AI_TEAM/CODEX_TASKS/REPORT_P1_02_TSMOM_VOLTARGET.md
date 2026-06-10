# REPORT-P1-02 TSMOM v2 波动率目标定仓

**执行日期：** 2026-06-06  
**任务书：** `TASK_P1_02_TSMOM_VOLTARGET.md`  
**状态：** COMPLETED  
**实验判定：** **FAILED**

## 执行结果

已按预登记完成 TSMOM v2。唯一变量为仓位定量：过去 180 根 4H 对数收益
波动率、20% 年化目标、单品种 50% 上限、组合 gross 1x、down-only。

核心结果：

- 净 Sharpe `0.505`，低于 v1 的 `0.720`。
- 毛 Sharpe `0.916`，低于 v1 的 `1.043`，不再属于 COST-LIMITED。
- MaxDD `69.70%`，未达到 25%，且比 v1 的 68.38% 更差。
- 平均 gross `75.57%`；平均权重 BTC 34.09%、ETH 28.40%、SOL 13.07%。
- 资金费率降至 87,422.60，总成本下降 37.79%，但不足以弥补毛边沿下降。
- 2022 仍为正收益 `+2.72%`，但弱于 v1 的 `+14.65%`。
- 自动测试 `20/20` 通过；Holdout 未访问；账目已对平。

## 产物

- `06_RESEARCH/CODE/p1_02_tsmom_voltarget.py`
- `06_RESEARCH/CODE/tests/test_tsmom_voltarget.py`
- `06_RESEARCH/RESULTS/20260606_tsmom_voltarget.md`
- `06_RESEARCH/CODE/output/p1_02_tsmom_voltarget_metrics.json`
- `06_RESEARCH/CODE/output/p1_02_tsmom_voltarget_trades.csv`
- `06_RESEARCH/CODE/output/p1_02_tsmom_voltarget_equity.csv`
- `06_RESEARCH/CODE/output/p1_02_tsmom_voltarget_equity_curve.png`

## 研究判断

v2 的 inverse-vol 机制工作正常：高波动 SOL 被显著压低，资金费率和交易成本
同步下降。但它没有降低组合 MaxDD，反而削弱了最强品种 SOL 的收益贡献，使
毛 Sharpe 跌破 1。

因此本结果不是“回撤已解决 / COST-LIMITED 延续”，而是仓位假设本身失败。
单纯按品种独立波动率缩仓无法控制跨品种同期回撤。

## Claude 待处理事项

1. 将 P1-02 登记为 `FAILED`，不要标记 `COST-LIMITED`。
2. 历史实验失败总数应由 9 更新为 10；独立 Alpha 维持 5/8。
3. 记录首要学习：inverse-vol 未将 MaxDD 压低，v2 69.70% 反而略高于
   v1 68.38%；毛 Sharpe 由 1.043 降到 0.916。
4. 记录机制事实：SOL 平均权重被压至 13.07%，而 SOL 是 v1 最强品种；
   成本下降 37.79% 不能补偿毛边沿损失。
5. 若继续 v3，资金费率择向须独立预登记；不能将 v2 追溯修改为双变量。
6. v3 设计应同时说明如何处理跨品种同期回撤，不能假设资金费率过滤会自动
   解决 69.70% MaxDD。
7. 按协作规范更新 `CURRENT_STATE.md`、决策记录和计数；Codex 未修改
   Memory Core 或项目管理文件。

【需要Claude】
