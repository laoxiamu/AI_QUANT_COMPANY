# 执行报告 TASK-0B1 Sweep Event Study

**执行时间：** 2026-06-06  
**执行人：** Codex  
**任务状态：** COMPLETED  
**实验结论：** FAILED

## 产物

- `06_RESEARCH/CODE/sweep_event_study.py`
- `06_RESEARCH/HYPOTHESES/v5_sweep_only_bull_v3.md`
- `06_RESEARCH/RESULTS/20260606_v5_sweep_only_bull_v3_EVAL.md`
- `06_RESEARCH/CODE/output/events_v5_sweep_only_bull_v3.csv`
- `06_RESEARCH/CODE/output/stats_v5_sweep_only_bull_v3.json`

未修改：

- `01_MEMORY_CORE/`全部文件
- `00_PROJECT_MANAGEMENT/`全部文件
- 项目根目录`CLAUDE.md`

## 执行摘要

### Sweep事件数

| 品种 | Regime前 | Regime后 | 完整事件 |
|------|---------:|---------:|---------:|
| BTC | 564 | 299 | 298 |
| ETH | 486 | 240 | 240 |
| SOL | 477 | 210 | 210 |
| 合计 | 1,527 | 749 | 748 |

### 主检验

| 窗口 | 均值 | 单侧p | 结论 |
|------|-----:|------:|------|
| t+6 | +0.489% | 0.0022 | 显著为正 |
| t+12 | +0.513% | 0.0122 | 显著为正 |
| t+24 | +0.465% | 0.0918 | 不显著 |

预登记要求三个窗口全部通过，因此整体结论为FAILED。

### 稳定性

- BTC三个窗口均不显著；
- ETH仅t+6/t+12显著；
- SOL三个窗口均不显著；
- 2021三个窗口均显著为正；
- 2019-2020与2022均值为负；
- 2023-2024三个窗口均不显著；
- t+12 Walk-Forward均值：+1.441% → +0.262% → +0.089%，后两段不显著。

## 规格执行确认

- Sweep定义：按SPEC §一实现 ✅
- `sweep_lookback=20`：未修改 ✅
- Daily EMA200 Regime：前一完整日、`shift(1)` ✅
- t+6/12/24对数收益：完整输出 ✅
- 单品种及合并统计：完整输出 ✅
- 市场时期分层：完整输出 ✅
- Walk-Forward三段：完整输出 ✅
- Holdout物理截断：使用`nrows`，未读取Holdout行 ✅
- 未计算手续费/滑点：符合事件研究规范 ✅

## 发现的规格问题或模糊点

1. 任务写“t-test，p<0.05”，但未明确单侧还是双侧。因假设方向明确为`mean > 0`，主检验使用单侧`alternative="greater"`，同时输出双侧p值。
2. 普通t检验没有处理重叠事件和跨品种相关性，p值可能偏乐观。该问题不改变失败结论。
3. “按DEC-025去重”对Sweep单事件没有实际冲突：同一品种每根K线最多一个Sweep事件，因此无需额外去重。
4. 2025-2026层在预-Holdout数据中只有12个完整事件，结论不稳定。

## Claude 待处理事项

### 1. DECISION_LOG建议

本实验结果是FACT，不建议直接新增“决策”条目。

若Founder确认停止当前结构信号方向，可由Claude整理以下决策草稿：

```text
决策草稿：暂停 Liquidity Sweep / CHoCH / FVG 结构信号路线的参数化扩展。
依据：4H完整策略、1H完整策略、Sweep单事件三个连续假设均失败；
Sweep短期合并显著性主要由2021和ETH贡献，缺乏跨时期、跨品种稳定性。
后续Alpha来源须经L3审计后重新选择，不继续围绕现有窗口调参。
状态：等待Founder确认。
```

### 2. CURRENT_STATE需要更新

建议Claude更新：

- 第三研究闭环：COMPLETED / FAILED；
- 实验版本：`v5_sweep_only_bull_v3`；
- 事件数：748个完整事件；
- t+6：均值+0.489%，单侧p=0.0022；
- t+12：均值+0.513%，单侧p=0.0122；
- t+24：均值+0.465%，单侧p=0.0918；
- 结论：主假设失败，存在短期但时期依赖的弱证据；
- 连续失败假设计数：从2/8更新为3/8；
- 风险状态：触发DEC-022 L3紧急审计；
- Holdout：未读取、未分析。

### 3. 需要Claude执行

1. 根据DEC-022创建L3紧急审计；
2. 审阅是否需要Founder确认暂停当前结构信号路线；
3. 决定下一Alpha来源，不建议Codex自行启动第四个相近假设；
4. 如阶段状态已正式进入Phase 0B，请同步修正Memory Core和主计划旧快照。

