# A-1 MDE Precheck（B4）

生成时间（UTC）：2026-06-12T17:18:08Z  
任务：`BATCH_20260612N` / B4  
代码：`06_RESEARCH/CODE/a1_mde_precheck.py`

## 结论

**功效门预判：通过。**  
滚动 P1 的 6h OI 骤降在 2024-12-10 之前合并为 `203` 个 episode；按预切 `1/5` Holdout 扣除 `40` 个后，可用 `n=163`。alpha=0.05 单侧、仅按无条件 MARK 24/48/72h 对数收益方差估算的 MDE 分别为 `0.625% / 0.872% / 1.073%`，均低于机制合理效应区间 `1.5%-3.0%` 的下沿。

该结论仅是功效门输入件，不是事件研究结果；本次没有计算任何事件后的实际收益。

## 口径

- 事件候选：`a1_oi_features_*.csv` 中 `warmup == False` 且 `d6h_rolling_pctl <= 0.01`。
- 分位：继承 A-1 特征层的 365 天滚动、最少 180 天、midrank、仅用 t 之前历史样本口径。
- Episode 合并：同品种 P1 触发行按时间排序，距离上一触发 `<=24h` 归为同一 episode，事件时间不落盘。
- 截止：`ts < 2024-12-10T00:00:00Z`，不使用 2024-12-10 及之后行情。
- Holdout 预扣：池化 episode 计数按 A-2 预切习惯估算，每第 5 个预留；本任务只扣数量，不写入也不读取 HOLDOUT 文件。
- 方差：BTC/ETH/SOL 的 1H MARK close，计算无条件 `log(close[t+h] / close[t])`，仅使用两端均在截止前的样本；不按事件条件筛选。

## Episode 计数

| Symbol | P1 trigger rows | Episodes merged <=24h |
|---|---:|---:|
| BTCUSDT | 290 | 75 |
| ETHUSDT | 218 | 76 |
| SOLUSDT | 208 | 52 |
| **Pooled** | **716** | **203** |

Holdout 预扣：`floor(203 / 5) = 40`；工作集可用 `n = 163`。

## 无条件方差与 MDE

公式：

```text
MDE_h = z_(1-alpha) * sqrt(Var[r_h]) / sqrt(n_work)
alpha = 0.05 one-sided, z_(0.95) = 1.6448536269514715
r_h = log(close[t+h] / close[t])
```

说明：任务书只指定 alpha，未指定 beta/power；因此这里使用 alpha-only 的单侧最小可拒绝均值阈值，不加入 80% power 的 beta 项。

| Horizon | Return obs | Var[r_h] | Stdev | n | MDE | 功效门 |
|---:|---:|---:|---:|---:|---:|---|
| 24h | 123061 | 0.002355 | 0.048529 | 163 | 0.625% | 通过 |
| 48h | 122941 | 0.004580 | 0.067676 | 163 | 0.872% | 通过 |
| 72h | 122821 | 0.006935 | 0.083279 | 163 | 1.073% | 通过 |

## 对照区间

- 批次书给定机制合理效应上限区间：`1.5%-3.0%`（级联回弹幅度的文献与常识区间）。
- `06_RESEARCH/RESULTS/20260611_event_census.md` 的普查结论显示，A-1 代理核心 `6h OI 骤降 P1` 是 OI 类事件中样本最厚的一档；本次改用滚动分位且截断 2024-12-09 后，仍有 `n=163` 可用于工作集。
- `06_RESEARCH/RESULTS/20260611_data_inventory.md` 确认 A-1 价格侧最细为 1H MARK，因此本次 24/48/72h 方差使用 1H MARK close。

## 输出文件

- `06_RESEARCH/CODE/output/a1_mde_precheck_counts.csv`
- `06_RESEARCH/CODE/output/a1_mde_precheck_unconditional_variance.csv`
- `06_RESEARCH/CODE/output/a1_mde_precheck_mde.csv`
- `06_RESEARCH/CODE/output/a1_mde_precheck_summary.json`

## 禁止项自检

- 未读取或写入 `HOLDOUT` 目录。
- 未计算事件后实际收益。
- 未使用全样本分位；事件触发使用既有滚动分位字段。
- 未读取 2024-12-10 及之后行情参与计算。
- 未修改预登记文档。
