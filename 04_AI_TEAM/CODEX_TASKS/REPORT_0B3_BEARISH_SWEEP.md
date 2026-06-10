# 执行报告 TASK-0B3 Bearish Sweep

**执行时间：** 2026-06-06  
**执行人：** Codex  
**任务状态：** COMPLETED  
**主假设结论：** FAILED  
**非重叠稳健性：** FAILED

## 产物

- `06_RESEARCH/CODE/bearish_sweep_event_study.py`
- `06_RESEARCH/HYPOTHESES/v5_sweep_regime_bear_v5.md`
- `06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bear_v5_EVAL.md`
- `06_RESEARCH/CODE/output/events_v5_sweep_regime_bear_v5.csv`
- `06_RESEARCH/CODE/output/stats_v5_sweep_regime_bear_v5.json`
- `04_AI_TEAM/CODEX_TASKS/REPORT_0B3_BEARISH_SWEEP.md`

未修改 Memory Core、`00_PROJECT_MANAGEMENT/` 或项目根目录 `CLAUDE.md`。

## 执行摘要

预登记文件先写入并固定规则，之后才运行研究。Bearish Sweep、双层熊市
Regime 和单侧 `less` 检验均按任务镜像实现。三个数据文件均使用固定
`nrows` 读取前 80%，Holdout 未进入解析或计算。

| 指标 | 结果 |
|------|-----:|
| 完整事件 | 344 |
| t+6 | -0.541%，p=0.0083 |
| t+12 | -0.570%，p=0.0196 |
| t+24 | -0.120%，p=0.3901 |
| 非重叠事件 | 152 |
| 非重叠 t+6 / t+12 / t+24 p | 0.1544 / 0.0966 / 0.1054 |

t+24 未通过预登记门槛，因此主假设 FAILED。非重叠校正后三窗口全部不显著。

## 关键解释

- 2022 有 183 个事件，占完整事件 53.2%，t+6 和 t+12 显著为负；
- 2019-2020、2021、2023-2024 不支持稳定做空，后两段多数均值为正；
- Walk-Forward 仅中间段通过，第一、三段失败；
- v4 做多三窗口全部显著，v5 做空并非稳定镜像；
- 不支持以当前证据设计对称的“做多 + 做空”组合。

## 验证

- Python 语法检查通过；
- Bearish Sweep、单侧 `less` 和严格 `>24` 根 K 线非重叠规则的合成测试通过；
- 输出 CSV 为 344 行，无重复 `symbol + datetime`；
- 三个品种事件时间均早于各自 Holdout 起点；
- 注册研究行数和研究截止时间均由程序硬校验；
- 复跑结果与 stats JSON 一致。

## Claude 待处理事项

### 1. 做空信号是否通过

未通过。t+6、t+12 原始合并统计显著为负，但 t+24 失败；非重叠校正后三窗口
全部不显著。结论应记录为“短窗口、2022 依赖的探索性现象”，不是有效做空腿。

### 2. 是否支持设计双向策略

不支持。v4 做多证据明显强于 v5 做空，且 v5 缺少时期稳定性和非重叠稳健性。
不应把做空腿加入当前候选策略。

### 3. CURRENT_STATE 建议更新

请由 Claude 审阅后更新：

- 第五研究闭环：COMPLETED / FAILED；
- 实验版本：`v5_sweep_regime_bear_v5`；
- 完整事件数：344，探索级；
- t+6：-0.541%，单侧 less p=0.0083；
- t+12：-0.570%，单侧 less p=0.0196；
- t+24：-0.120%，单侧 less p=0.3901；
- 非重叠：152 个事件，三个窗口均不显著；
- 稳定性：结果主要由 2022 驱动，Walk-Forward 仅第二段通过；
- Holdout：物理截断，未读取；
- 研究判断：不支持对称双向策略。

### 4. DECISION_LOG 条目建议

本次是预登记实验失败，不必自动新增决策条目，记录到 CURRENT_STATE 和实验档案
即可。若 Claude 认为需要冻结路线，可提交以下草稿等待 Founder 确认：

```text
决策草稿：不将 Bearish Sweep + 双层熊市 Regime 纳入当前双向策略设计。
依据：v5 主假设因 t+24 不显著而失败，非重叠校正后三窗口全部不显著，
且效果集中在 2022，Walk-Forward 第一、三段失败。
边界：保留为失败知识；不读取 Holdout，不围绕本结果继续调参。
状态：需 Claude 审阅；如升级为路线决策，等待 Founder 确认。
```

【需要Claude】
