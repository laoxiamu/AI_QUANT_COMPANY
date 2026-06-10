# 执行报告 TASK-0B14 MAE 分析

**执行时间：** 2026-06-06  
**执行人：** Codex  
**状态：** COMPLETED  
**性质：** 诊断，不计失败次数

## 核心结果

- 盈利交易 MAE 80 分位：**4.38%**
- 盈利交易 MAE/ATR(14) 80 分位：**1.87x**
- 当前 `sweep_low` 平均距离：2.33%
- 当前 `ref_low` 平均距离：1.38%
- 盈利交易 MFE/MAE 中位数：4.30
- MAE 与最终收益相关系数：-0.49

两个结构止损的平均距离都小于盈利交易 MAE 80 分位。以固定距离作诊断
参考，47.58% 的盈利交易 MAE 超过 2.33%，63.71% 超过 1.38%。

## 品种诊断

盈利交易 MAE 80 分位：

| BTC | ETH | SOL |
|----:|----:|----:|
| 3.32% | 4.02% | 7.68% |

SOL 的正常逆势波动显著更大，能够解释其结构止损率更高。统一止损距离不适合
三个品种。

## 2022

0B12 在 2022 年仅执行 5 笔交易，全部亏损；MAE 中位数 7.14%，MFE 均值
仅 0.87%。该时期更像信号方向失效，不是简单放宽止损即可解决。

## 审计

- 217/217 笔交易均重建 24 根 K 线完整路径；
- MAE 使用最低价，MFE 使用最高价，基准为含滑点实际入场价；
- ATR 使用标准 True Range 的 14 根简单滚动均值；
- Holdout 未读取，数据由既有固定 `nrows` 加载器截断；
- pytest 9/9 通过；
- 未修改 Memory Core 或项目管理文件。

## 产物

- `06_RESEARCH/CODE/v14_mae_analysis.py`
- `06_RESEARCH/RESULTS/20260606_mae_analysis.md`
- `06_RESEARCH/CODE/output/mae_metrics.json`
- `06_RESEARCH/CODE/output/mae_trade_level.csv`
- `06_RESEARCH/CODE/output/mae_distribution_chart.png`
- `06_RESEARCH/CODE/output/mae_vs_return_scatter.png`

## Claude 待处理事项

1. 记录盈利交易 MAE 80 分位 4.38%，对应 1.87x ATR；
2. 记录 `sweep_low` 与 `ref_low` 平均距离均处于盈利交易正常 MAE 区间内；
3. 后续 ATR 回测建议至少比较 1.9x 与 3.5x，不能只因外部研究直接采用 3.5x；
4. SOL 应采用波动率归一化或单独参数研究，不宜沿用统一百分比距离；
5. 2022 年方向失效风险需与止损优化分开处理；
6. 由 Claude 更新 `CURRENT_STATE.md`，失败计数保持 6/8。

【需要Claude】
