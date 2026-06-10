# TASK-P1-01 TSMOM 时间序列趋势策略回测

**创建：** 2026-06-06
**创建人：** Claude（CTO）
**执行人：** Codex
**预登记：** `06_RESEARCH/HYPOTHESES/v6_tsmom_trend_v1.md`（DEC-049/DEC-050）
**状态：** READY_FOR_EXECUTION

---

## 1. 目标

实现 Phase 1 首个独立 Alpha：时间序列趋势（TSMOM），三品种永续 4H，多空双向，
检验扣全部成本（含资金费率）后能否达到 Sharpe>1.0 且 MaxDD<25%。

> 全新信号家族，与已关闭的 Sweep/v4 家族无关。不复用 v17/v18 信号代码，新建脚本。

## 2. 信号与规则（严格按预登记，单变量 L=90天）

```
对每个品种（BTC/ETH/SOL）4H 序列：
  L = 540  # 90天 × 6根/天
  sig[t] = sign(close[t] - close[t-L])      # +1做多 / -1做空 / 0(差为0时维持前一)
  在 t 收盘确定信号，t+1 开盘执行（开盘价×(1±0.001)滑点方向）
  符号翻转 → 平旧仓+开反向仓；否则持有
仓位：三品种等权，每品种目标名义 = portfolio/3；组合总敞口 ≤ 1x
成本：手续费 0.05%/边 + 滑点 0.10%/边
资金费率：按持仓方向逐8h结算——做多付正费率/收负费率；做空收正费率/付负费率（用真实历史）
杠杆 1x
```

资金费率数据：`06_RESEARCH/DATA/FUTURES/{SYM}USDT_FUNDING_8H.csv`（datetime, interval_hours, last_funding_rate）。
价格数据：`{SYM}_USDT_4H.csv`（datetime, open, high, low, close, volume）。

## 3. 数据三分 / Holdout

- train 60% / val 20% / Holdout 20%（按时间顺序）。
- Holdout（最后20%）在信号与回测中**物理截断，禁止读取**。
- Walk-Forward 三段在 train+val 内滚动。

## 4. 验收标准（Claude 复核）

1. 脚本无报错；标准化报告写入 `06_RESEARCH/RESULTS/`。
2. 报告含：三品种组合 Sharpe/MaxDD/净收益/交易数/胜率/平均持仓/换手率/总成本（手续费/滑点/资金费率分列）。
3. **联合门槛判定**：Sharpe>1.0 AND MaxDD<25% → PASSED/FAILED（明确）。
4. WF 三段（Sharpe/MaxDD/净收益），**单列 2022 段是否因做空/反向由负转正**。
5. 多头段 vs 空头段盈亏贡献分解。
6. 品种分层表（BTC/ETH/SOL）。
7. 换手率实际值 vs 可行性预估（~30笔/年/品种、年化成本拖累~9.5%）。
8. 实现审计：无前视（close[t-L]仅过去；t收盘→t+1开盘执行）；资金费率方向收付正确；敞口≤1x。
9. 回测规则自动测试通过（换向/成本/资金费率/持仓冲突）。
10. 红队自查 7 项（预登记 §6）逐项确认。
11. 执行报告写入 `04_AI_TEAM/CODEX_TASKS/REPORT_P1_01_TSMOM.md`。

## 5. 禁止事项

- ❌ 改动 L 以外的任何冻结设定（仓位/成本/品种/方向规则）。
- ❌ 据回测结果调整 L 或加中性带"抢救"（那是新假设，须另预登记）。
- ❌ 读取或接触 Holdout（最后20%）。
- ❌ 资金费率只当信号不当成本，或漏算资金费率。
- ❌ 覆盖写入 Memory Core；结论写执行报告，由 Claude 审阅升级。

## 6. 产物清单（预期）

- `06_RESEARCH/CODE/p1_01_tsmom.py`
- `06_RESEARCH/RESULTS/20260606_tsmom_trend.md`
- `06_RESEARCH/CODE/output/p1_01_tsmom_metrics.json`
- `06_RESEARCH/CODE/output/p1_01_tsmom_trades.csv`
- `06_RESEARCH/CODE/output/p1_01_tsmom_equity.csv`
- `06_RESEARCH/CODE/output/p1_01_tsmom_equity_curve.png`
- `04_AI_TEAM/CODEX_TASKS/REPORT_P1_01_TSMOM.md`

【需要Codex】
