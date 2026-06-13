# REPORT_B4

**任务：** `BATCH_20260612N` / B4 A-1 MDE 预计算  
**生成时间（UTC）：** 2026-06-12T17:18:08Z  
**结果：** 功效门预判通过  

## 七问自查

1. **验证机制：** 只验证 A-1 OI 骤降事件研究是否有足够 episode 数和方差条件，能否检测 1.5%-3.0% 级别的级联回弹效应。
2. **验收标准量化：** n、24/48/72h 无条件对数收益方差、alpha=0.05 单侧 MDE、与 1.5%-3.0% 对照、通过/不通过。
3. **更便宜等效实现：** 有；直接复用既有 A-1 特征层输出，只做计数和无条件方差，不重建特征、不做事件研究。
4. **禁止项检查：** 不碰 HOLDOUT，不改预登记，不算事件后收益，不使用全样本分位，不读 2024-12-10 后行情参与计算。

## 交付物

- CODE：`06_RESEARCH/CODE/a1_mde_precheck.py`
- RESULTS：`06_RESEARCH/RESULTS/20260612_a1_mde_precheck.md`
- OUTPUT：`06_RESEARCH/CODE/output/a1_mde_precheck_counts.csv`
- OUTPUT：`06_RESEARCH/CODE/output/a1_mde_precheck_unconditional_variance.csv`
- OUTPUT：`06_RESEARCH/CODE/output/a1_mde_precheck_mde.csv`
- OUTPUT：`06_RESEARCH/CODE/output/a1_mde_precheck_summary.json`

## 核心结果

| Item | Value |
|---|---:|
| Pooled episodes before holdout | 203 |
| Precut holdout count | 40 |
| Usable n | 163 |
| 24h MDE | 0.625% |
| 48h MDE | 0.872% |
| 72h MDE | 1.073% |

结论：三个 horizon 的 MDE 均低于 `1.5%-3.0%` 机制合理效应区间下沿，因此 B4 功效门输入件预判为 **通过**。

## 自实现公式

```text
MDE_h = z_(1-alpha) * sqrt(Var[r_h]) / sqrt(n_work)
alpha = 0.05 one-sided
z_(0.95) = 1.6448536269514715
r_h = log(close[t+h] / close[t])
```

任务书未指定 beta/power，因此本次使用 alpha-only 单侧最小可拒绝均值阈值，未加入 80% power 项。

## 复算命令

```bash
python3 06_RESEARCH/CODE/a1_mde_precheck.py
python3 -m py_compile 06_RESEARCH/CODE/a1_mde_precheck.py
```

## 验收自检

- 只做 B4，未执行 B1/B2/B3/B5。
- 使用 `06_RESEARCH/CODE/output/a1_oi_features_*.csv` 统计 6h OI 骤降 P1 rolling percentile episode。
- Episode 合并窗口为 `<=24h`；截止为 `ts < 2024-12-10T00:00:00Z`。
- 扣除 `1/5` Holdout 后得到可用 `n=163`；未写入或读取 HOLDOUT 文件。
- 使用 1H MARK close 的无条件 24/48/72h 对数收益方差；未按事件条件筛选。
- 未计算事件后实际收益。
- 未执行 git commit；批次书头部明确全程禁 commit。
