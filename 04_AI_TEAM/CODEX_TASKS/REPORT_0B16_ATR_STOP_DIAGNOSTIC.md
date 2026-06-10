# 执行报告 TASK-0B16 ATR 止损诊断

**执行时间：** 2026-06-06  
**执行人：** Codex  
**状态：** COMPLETED  
**性质：** 诊断，不计失败次数

## 核心结果

- ATR×3.5 平均距离：**8.69%**
- `sweep_low` 平均距离：2.30%
- `ref_low` 平均距离：1.35%
- ATR×3.5 在 425/425 事件中宽于两种结构止损
- `max(ref_low, ATR×3.5)` 在 425/425 中等同纯 ATR×3.5
- ATR×3.5 覆盖盈利 MAE：96.77%
- ATR×1.9 覆盖盈利 MAE：81.45%

## 原止损理论避免率

| 止损 | 210笔原STOP | 118笔首根STOP |
|------|------------:|--------------:|
| ATR×1.9 | 61.43% 可避免 | 61.86% 可避免 |
| ATR×3.5 | 94.76% 可避免 | 95.76% 可避免 |

避免止损不等于最终盈利，仅证明当前结构止损处于更窄的价格区域。

## 2022 纠错

2022 ATR×3.5 平均距离 7.80%，是全局的 0.90 倍，并非绝对波动最高时期；
但结构止损仅 1.35% / 0.57%，使 ATR 距离分别达到其 5.76 倍 / 13.70 倍。
真正问题是结构止损没有随波动尺度调整。

## 推荐

建议下一策略假设以 **ATR×1.9** 为主参数，3.5x 作为压力测试。任务书建议的
`max(ref_low, ATR×3.5)` 没有复合效果，因为它在全部事件中都退化为纯
ATR×3.5。

## 审计

- 425/425 冻结事件完成四类止损距离计算；
- ATR 使用 Sweep K 线可见的标准 TR 14 根简单均值；
- 210 笔 v4 STOP 与 118 笔首根 STOP 完成路径重放；
- 引用 0B14 的 124 笔盈利交易 MAE；
- Holdout 未读取；
- pytest 9/9 通过；
- 未修改 Memory Core 或项目管理文件。

## 产物

- `06_RESEARCH/CODE/v16_atr_stop_diagnostic.py`
- `06_RESEARCH/RESULTS/20260606_atr_stop_diagnostic.md`
- `06_RESEARCH/CODE/output/atr_stop_metrics.json`
- `06_RESEARCH/CODE/output/atr_stop_event_distances.csv`
- `06_RESEARCH/CODE/output/atr_vs_structure_stop_charts.png`

## Claude 待处理事项

1. 记录 ATR×3.5 平均距离 8.69%，理论可避免 95.76% 首根止损；
2. 同时记录 3.5x 明显宽于 MAE 推导值，不能只凭避免率认定最优；
3. 建议下一假设主测 ATR×1.9，并按 ATR 风险距离重新定仓；
4. 不建议使用 `max(ref_low, ATR×3.5)`，其在全部事件中等同纯 ATR；
5. 2022 应记录为结构止损相对波动过紧，同时存在独立的方向失效；
6. 是否消耗第 7 次失败机会进行 ATR 策略回测，由 Claude 审阅后决定；
7. 由 Claude 更新 `CURRENT_STATE.md`，当前失败计数仍为 6/8。

【需要Claude】
