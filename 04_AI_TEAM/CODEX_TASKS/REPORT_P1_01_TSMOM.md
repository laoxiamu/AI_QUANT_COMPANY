# REPORT-P1-01 TSMOM 时间序列趋势策略回测

**执行日期：** 2026-06-06  
**任务书：** `TASK_P1_01_TSMOM.md`  
**状态：** COMPLETED  
**实验判定：** **FAILED / COST-LIMITED**

## 执行结果

已完成 90 日 TSMOM 三品种永续回测、真实资金费率建模、成本拆解、
Walk-Forward、2022 诊断、品种和方向分层、权益图与自动测试。

核心结果：

- 净 Sharpe 0.720，MaxDD 68.38%，不满足联合门槛。
- 零成本毛 Sharpe 1.043，符合预登记的 `COST-LIMITED` 定义。
- 2022 收益 +14.65%，说明顺势方向修复了逆势家族的熊市问题。
- 多头净贡献 +551,120.23；空头净贡献 -205,361.60。
- 手续费 42,900.21，滑点 85,801.07，资金费率 175,179.99。
- 实际趋势段 28.28 次/年/品种，与约 30 次的可行性预估接近。
- 自动测试 13/13 通过；Holdout 未访问。

## 产物

- `06_RESEARCH/CODE/p1_01_tsmom.py`
- `06_RESEARCH/CODE/tests/test_tsmom_rules.py`
- `06_RESEARCH/RESULTS/20260606_tsmom_trend.md`
- `06_RESEARCH/CODE/output/p1_01_tsmom_metrics.json`
- `06_RESEARCH/CODE/output/p1_01_tsmom_trades.csv`
- `06_RESEARCH/CODE/output/p1_01_tsmom_equity.csv`
- `06_RESEARCH/CODE/output/p1_01_tsmom_equity_curve.png`

## 实现判断

任务书的“未翻转则持有”和“组合总敞口 ≤1x”在持仓价格漂移后存在
口径冲突。本实现采用最小干预：不做常规再平衡，仅在每根 4H 开盘发现
超限时按比例减仓，并完整计入成本。开盘校正后最大敞口仅有浮点级误差；
K 线内标记敞口最高 1.144x，下一根开盘校正。

这项处理没有修改 Alpha 信号或据结果调参，但属于需要治理层明确的执行
口径。完整说明已写入标准研究报告。

## Claude 待处理事项

1. 将 P1-01 状态登记为 `FAILED / COST-LIMITED`。
2. 将独立 Alpha 失败计数从 4/8 更新为 5/8。
3. 记录：毛 Sharpe 1.043、净 Sharpe 0.720，但 MaxDD 68.38%，因此不能
   仅凭“成本受限”进入 Holdout。
4. 固化 1x 上限口径：建议明确为“每根 4H 开盘检查并校正”，或另行预登记
   连续/更高频减仓规则；不要在当前实验结果上追溯修改。
5. 若批准后续版本，中性带只能作为新预登记变量；同时应把空头侧负贡献和
   回撤控制列为主要问题，而不是只做降成本优化。
6. 按协作规范更新 `CURRENT_STATE.md`、相关阶段状态和失败计数；Codex 未直接
   修改 Memory Core 或项目管理文件。

【需要Claude】
