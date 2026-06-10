# TASK-P1-04 regime-first 长偏向 TSMOM

**创建：** 2026-06-06 · Claude（CTO）· 执行人：Codex
**预登记：** `06_RESEARCH/HYPOTHESES/v6_tsmom_regime_long_v3.md`（DEC-055 框架）
**状态：** READY_FOR_EXECUTION
**与 TASK_P1_03（OI数据核查）并行，互不依赖。**

## 1. 目标

实现 regime-first 的第一个实例：**上升趋势规 + 仅做多** 的 TSMOM，检验净 Sharpe 能否>1。
从 `p1_01_tsmom.py` 复制为 `p1_04_tsmom_regime_long.py`，改动见 §2。

## 2. 规则（严格按预登记）

```
# 大环境：ADX(14) on 4H
#   ADX>25 -> 趋势规; ADX<20 -> 震荡; 20~25 维持上一状态(迟滞)
# 入场(仅做多): (close[t] > close[t-540]) AND (regime==趋势) -> t+1开盘做多(×1.001)
# 离场: (close[t] < close[t-540]) OR (ADX<20) -> 平仓
# 仓位: 持仓时名义=portfolio/3; 组合gross<=1x(每4H开盘按比例校正)
# 成本: 手续费0.05%/边 + 滑点0.10%/边 + 真实8H资金费率(做多付正费率)
# 仅做多, 无加仓, 无做空
```
冻结常数：ADX周期=14、进25/出20、趋势L=540。数据三分，最后20% Holdout 物理截断禁读。
ADX 用标准 Wilder 平滑实现，仅用 ≤t 数据（无前视）。

## 3. 验收标准（Claude 复核）

1. 脚本无报错；报告写 `06_RESEARCH/RESULTS/`。
2. 判定：净Sharpe>1 AND 原始MaxDD<50% → PASSED/FAILED（DEC-053口径，Sharpe为真门槛）。
3. **vs TSMOM v1 对照**：净/毛Sharpe、MaxDD、交易数、净收益、各成本项。
4. 趋势规过滤诊断：被过滤掉(震荡/非上升)时段的P&L（验证砍掉的是亏损段）。
5. 2022 表现（预期多数空仓）；WF三段；交易数与样本档级（对照DEC-018）。
6. 资金费率占比。
7. 实现审计：ADX无前视+迟滞正确、仅做多、t+1执行、gross≤1x开盘校正、资金费率方向。
8. 自动测试通过（沿用v1+新增ADX/迟滞/仅做多/regime进出用例）。
9. 红队自查（预登记§7）。
10. 执行报告 `04_AI_TEAM/CODEX_TASKS/REPORT_P1_04_TSMOM_REGIME_LONG.md`。

## 4. 禁止事项

- ❌ 改 ADX/趋势 常数或加做空/加仓；❌ 据结果调阈值"抢救"（新阈值=新预登记）。
- ❌ 读取/接触 Holdout。❌ 漏算资金费率或只当信号。
- ❌ 覆盖 Memory Core；结论写执行报告。
- ❌ 用诊断所用的效率比(ER)替代 ADX（须用独立分类器，防过拟合）。

## 5. 产物（预期）

`06_RESEARCH/CODE/p1_04_tsmom_regime_long.py`、`tests/test_tsmom_regime_long.py`、
`06_RESEARCH/RESULTS/20260606_tsmom_regime_long.md`、
`output/p1_04_*_metrics.json|trades.csv|equity.csv|equity_curve.png`、
`04_AI_TEAM/CODEX_TASKS/REPORT_P1_04_TSMOM_REGIME_LONG.md`

【需要Codex】
