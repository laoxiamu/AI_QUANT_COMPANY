# 任务书：P0-RES-014 TSMOM引擎L在10%/15%目标波动率点用v1.5风险调整法重算被动基准门

**派发时间：** 2026-07-06　**派发人：** Claude　**执行：** Codex　**验收：** Claude
**性质：** 家族内诊断复查的收尾一步，**不消耗独立试验计数**。

---

## 背景（务必先读，避免重复劳动）

P0-RES-006（`04_AI_TEAM/CODEX_TASKS/REPORT_P0RES006_ENGINE_L_RECHECK_20260702.md` + `06_RESEARCH/CODE/output/p0res006_engine_l_recheck_20260702.json`）已完成TSMOM引擎L的仓位曲线扫描，10%目标波动率点结果：

```
positive_expectancy: true
win_loss_ratio_ge_1_5: true
standard_dd35_prob_le_20pct: true
conservative_dd20_prob_le_10pct: true
annualized_log_growth_positive: true
positive_years_majority: true
walk_forward_majority_positive: true   ← WF已通过，不用重跑
fifth_benchmark_excess_positive: false  ← 唯一未过，但这是旧v1.4原始收益比较口径
```

**七项检查六项已过。** 唯一未过的`fifth_benchmark_excess_positive`用的是修订前的原始收益直接比较（策略收益 vs 基准收益，未做波动率/风险调整）。DEC-092已把这一件（v1.5第5件）改为**风险调整后比较**——这正是P0-RES-007（`04_AI_TEAM/CODEX_TASKS/REPORT_P0RES007_X3_BENCHMARK_RECHECK_20260702.md`）刚验证过的方法，**直接复用同一套方法学**，不要重新设计。

## 任务

1. 读取P0-RES-007的方法（风险调整比较：策略和基准都缩放到同一目标年化波动率后比较年化log growth；主表用10%目标波动率，附带"都缩放到基准实际vol"敏感性；周频/该资产原频率下的paired moving-block bootstrap算显著性）。
2. 对TSMOM引擎L的**10%目标波动率仓位点**（即P0-RES-006已经跑出结果的那个点，不要重新扫描仓位），用同款风险调整法重算被动基准门：
   - 策略序列＝10%目标波动率仓位下的引擎L收益序列（复用P0-RES-006脚本里已生成的该序列，不要重新回测）。
   - 基准序列＝原引擎L验收报告里用的被动基准（`tsmom_dual_engine.py`里的`prepare_passive_dataset`/`benchmark_L_macro_bull`，与P0-RES-006 warm-up时用的同一个基准，保持一致）。
   - 都缩放到10%年化波动率后比较年化log growth，差值+95%CI（block bootstrap，块长与原方法一致）。
3. **同样对15%目标波动率点做一次**（P0-RES-006里另一个通过DD/增长门的点，作为敏感性对照，非必须但强烈建议——如果10%过、15%不过，或反之，这个信息本身有价值）。
4. **判定：** 风险调整后，"策略显著跑输基准"是否仍然成立（即gate是否仍然KILL，还是像#X3一样变成"未确认"/甚至策略反而不输基准）？
5. **禁止事项：** 不得改动仓位扫描范围、不得引入新仓位点、不得改动信号层本身、不得读取Holdout。

## 产出

报告文件 `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES014_ENGINE_L_BENCHMARK_RECHECK_20260706.md`，包含：
- 10%点（及15%点，如做）风险调整前后的基准对照数字对比
- 最终判定：该点位七项检查是否**全部通过**
- 如果全部通过：明确写"TSMOM引擎L·10%目标波动率点＝七项检查全过，构成DEC-092后首个重新达标候选，是否晋级正常验收/paper-forward流程待Claude/Founder决定"——不要自己下"已晋级"的结论，只报告事实状态
- 如果仍有未过项：如实报告，说明具体是哪一项、数字是多少
