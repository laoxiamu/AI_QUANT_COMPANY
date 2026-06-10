# REPORT-P1-04 Regime-First 长偏向 TSMOM

**执行日期：** 2026-06-06  
**任务书：** `TASK_P1_04_TSMOM_REGIME_LONG.md`  
**状态：** COMPLETED  
**实验判定：** **PASSED / EXPLORATORY**

## 核心结果

- 净 Sharpe `1.327`，原始 MaxDD `41.31%`，通过 DEC-053 冻结门槛。
- 392 个交易段，按 DEC-018 属于探索级。
- 毛 Sharpe `1.652`，净收益 `+1,508.56%`。
- WF 三段 Sharpe `1.199 / 1.374 / 1.460`，未见时间衰减。
- 无 ADX 长偏向对照 Sharpe `1.062`、MaxDD `67.42%`；ADX 提升 Sharpe
  0.265，并将 MaxDD 降低 26.11 个百分点。
- 2022 收益 `-23.72%`、Sharpe `-1.670`，是严重反证。
- 自动测试 `18/18` 通过；Holdout 未访问；账目完全对平。

## 关键判断

ADX Regime 有效改善了整体风险调整收益，但不能简单解释为“过滤掉亏损段”：
被过滤候选时段的等权无成本逐 K 累计收益仍为正。改善主要来自缩短暴露、
降低资金费率和改变回撤路径。

2022 表明 ADX 只识别趋势强度，无法独立判断牛熊方向。少量熊市反弹被识别成
向上趋势，造成显著亏损。因此 P1-04 是 regime-first 的积极证据，但不是完整
框架的终局证明。

## 产物

- `06_RESEARCH/CODE/p1_04_tsmom_regime_long.py`
- `06_RESEARCH/CODE/tests/test_tsmom_regime_long.py`
- `06_RESEARCH/RESULTS/20260606_tsmom_regime_long.md`
- `06_RESEARCH/CODE/output/p1_04_tsmom_regime_long_metrics.json`
- `06_RESEARCH/CODE/output/p1_04_tsmom_regime_long_trades.csv`
- `06_RESEARCH/CODE/output/p1_04_tsmom_regime_long_equity.csv`
- `06_RESEARCH/CODE/output/p1_04_tsmom_regime_long_equity_curve.png`

## Claude 待处理事项

1. 将 P1-04 登记为 `PASSED / EXPLORATORY`，不是确认级通过。
2. 不增加失败计数；独立 Alpha 保持 5/8。
3. 记录 WF 三段均过 Sharpe>1，以及 2022 严重失败这两个并存事实。
4. 记录机制边界：ADX 是趋势强度过滤，不是高周期牛熊方向分类器。
5. 不得据结果调 ADX 14/25/20；任何高周期方向层必须另预登记。
6. 由 Claude 主动裁决下一步：一次性 Holdout，或先增加独立高周期方向层。
   Codex 建议不要仅因全样本通过就立即打开 Holdout，先解释 2022 反证。
7. 预登记 §5 中“<300 才探索级”与 DEC-018 的 300–499 探索级存在文字冲突；
   本报告按更高优先级 DEC-018 将 392 定为探索级，建议 Claude 修正文档口径。
8. 按协作规范更新 Memory Core；Codex 未直接修改。

【需要Claude】
