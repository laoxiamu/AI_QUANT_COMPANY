# 执行报告 TASK-0B15 波动率压缩分组

**执行时间：** 2026-06-06  
**执行人：** Codex  
**状态：** COMPLETED  
**性质：** 诊断，不计失败次数

## 核心结果

| 方案 | 压缩N | 扩张N | t+24压缩 | t+24扩张 | 差值 | 单侧p |
|------|------:|------:|----------:|----------:|-----:|-------:|
| ATR14 < ATR50 | 247 | 178 | 2.31% | 2.37% | -0.06pp | 0.5320 |
| BBW < 历史中位数 | 289 | 136 | 1.94% | 3.17% | -1.23pp | 0.9134 |

两种方案均未达到“压缩组领先 >0.5pp 且 p<0.05”。1,000 次 Bootstrap
置信区间也都跨越 0。

## 止损与 2022

- 方案 A 前 6 根 `sweep_low` 触发率：压缩 57.49%，扩张 46.07%；
- 方案 B：压缩 55.71%，扩张 46.32%；
- 2022 的 12 个事件：方案 A 为 6/6；方案 B 为压缩 10、扩张 2。

压缩过滤不能解释或排除 2022，且会提高早期结构止损触发率。

## 审计

- 425/425 冻结事件均完成分组；
- 所有指标使用信号前一根 K 线；
- BBW 阈值使用当时可见的扩展历史中位数，无全样本前视；
- t+6/12/24 收益直接读取冻结事件文件；
- Holdout 未读取；
- 未修改 Memory Core 或项目管理文件。

## 产物

- `06_RESEARCH/CODE/v15_vol_compression.py`
- `06_RESEARCH/RESULTS/20260606_vol_compression_analysis.md`
- `06_RESEARCH/CODE/output/vol_compression_metrics.json`
- `06_RESEARCH/CODE/output/vol_compression_event_groups.csv`
- `06_RESEARCH/CODE/output/vol_compression_charts.png`

## Claude 待处理事项

1. 记录 V4 历史波动压缩 IC 因子在当前 v4 双层 Regime 下未复现；
2. 不建议增加波动率压缩过滤层，压缩样本也低于 300；
3. 不得将方案 B 的扩张组较高均值追认为新假设，差异未显著且属事后观察；
4. 2022 不能由该因子过滤；
5. 由 Claude 更新 `CURRENT_STATE.md`，失败计数保持 6/8。

【需要Claude】
