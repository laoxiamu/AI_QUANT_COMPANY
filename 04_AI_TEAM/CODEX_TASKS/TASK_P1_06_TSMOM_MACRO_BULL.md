# TASK-P1-06 P1-04 + 宏观牛市过滤

**创建：** 2026-06-07 · Claude（CTO）· 执行人：Codex
**预登记：** `06_RESEARCH/HYPOTHESES/v6_tsmom_regime_long_v4.md`（DEC-062）
**遵循：** Research Protocol v1.2（规则式状态门控[非ML,不报精确率/召回率] / 两轴状态 / Purged-Embargo CV / 三屏障=方向性事件策略默认基准,本轮不叠加守单变量）
**状态：** READY_FOR_EXECUTION

> 先按协作规范输出"专业审查七问"。若认为宏观轴定义或归因口径有更优方案，先提异议再落地。

## 1. 目标

在 P1-04 基础上**唯一新增宏观牛熊方向轴**（只在宏观牛市做多），检验能否消除 2022 -23.72% 反证并维持净 Sharpe>1。
从 `p1_04_tsmom_regime_long.py` 复制为 `p1_06_tsmom_macro_bull.py`，只改入场/持仓门控一处。

## 2. 唯一改动

```
macro_bull = (该品种 前一完整UTC日收盘 > 当日 日线SMA200)   # 仅用<=t数据; SMA200预热不足→unknown→不做多
# 入场(仅做多): (close[t]>close[t-540]) AND (4H ADX>25) AND macro_bull → t+1开盘做多
# 持仓: macro 转熊 → 平多
```
冻结：SMA200(日线)、ADX 14/25/20、L=540。其余全部继承 P1-04（信号/仅做多/品种/成本/gross≤1x/Holdout 截断）不变。

## 3. 验收标准（Claude 复核）

1. 判定：净Sharpe>1 AND 原始MaxDD<50% → PASSED/FAILED（DEC-053；Sharpe 为真门槛）。
2. **2022 对照**：净收益/Sharpe vs P1-04 的 -23.72%/-1.67（验证宏观熊市不做多是否消除该亏损）。
3. **vs P1-04 全面对照**：净/毛 Sharpe、MaxDD、WF 三段、交易数、各成本项。
4. **状态门控过滤归因**（v1.2，替代旧 meta-label 精确率/召回率）：报告被"宏观熊市"门控过滤掉的交易的损益分布——验证过滤掉的确为亏损段、未误杀盈利段。
5. **两轴状态归因**：保留交易在 {强度×牛熊} 网格分布与损益。
6. 样本档级（DEC-018，预期约281笔=探索级）。
7. 实现审计：macro 无前视(前一完整日 vs 当日SMA200)、unknown不做多、转熊平多、仅做多、gross≤1x开盘校正。
8. 自动测试通过（沿用 P1-04 + 新增 macro 门控/转熊平多/无前视用例）。
9. 红队自查（预登记§7）+ 七问。
10. 执行报告 `04_AI_TEAM/CODEX_TASKS/REPORT_P1_06_TSMOM_MACRO_BULL.md`。

## 4. 禁止事项

- ❌ 改 §2 继承项或调 SMA200/ADX/L 常数；❌ 加做空/加仓/叠三屏障(守单变量)。
- ❌ 据结果反向调参"抢救"；任何参数优化须 Purged/Embargo CV。
- ❌ 读取/接触 Holdout。❌ 覆盖 Memory Core。
- ❌ 用同周期 DI± 充当牛熊轴（须独立高周期 SMA200，避免复现 P1-04 盲点）。

## 5. 产物

`06_RESEARCH/CODE/p1_06_tsmom_macro_bull.py` + tests、
`06_RESEARCH/RESULTS/20260607_tsmom_macro_bull.md`、
`output/p1_06_*_metrics.json|trades.csv|equity.csv|equity_curve.png`、
`04_AI_TEAM/CODEX_TASKS/REPORT_P1_06_TSMOM_MACRO_BULL.md`

## 6. 后续（Claude 据结果，不在本任务内）

- 通过且2022回正 → 探索级。下一步**扩品种/扩历史**升确认级（仍不进Holdout）。
- 若仍卡 → 据归因再判，不局部修补。

【需要Codex】
