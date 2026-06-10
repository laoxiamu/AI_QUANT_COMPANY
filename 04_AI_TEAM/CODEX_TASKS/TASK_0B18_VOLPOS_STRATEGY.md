# TASK-0B18 波动率缩仓策略回测

**创建：** 2026-06-06
**创建人：** Claude（CTO）
**执行人：** Codex
**预登记：** `06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_volpos_v1.md`（DEC-045）
**状态：** READY_FOR_EXECUTION

---

## 1. 目标

在 0B17 的 **ATR×3.5** 版本基础上，**唯一新增**一个按市场恐惧度动态缩仓的仓位规则，
检验其能否把三品种组合 Sharpe 抬过 1.0 且 MaxDD < 25%，并修复 WF2/2022 方向失效。

> **定位（DEC-046）：** 这是 v4 实现线**最后一次、预登记完整的机制检验**。
> 通过 → 仅为 Holdout 候选，不得称"可部署策略"；失败 → 立即封存 v4，转全新独立 Alpha。
> 成功率不应高估：高波动也覆盖盈利的 2021，缩仓可能同时削弱 WF1（须诊断）。

**实现方式（强制）：** 从 `06_RESEARCH/CODE/v17_atr_strategy.py` **复制**为
`06_RESEARCH/CODE/v18_volpos_strategy.py`，固定止损倍数为 3.5，**只改仓位定量一处**，
其余逻辑逐行保持不变。这是机械保证单变量的方式。

---

## 2. 唯一改动：波动率缩仓系数

```
# 恐惧度代理（市场级，基于 BTC，无前视）
btc_logret      = log(BTC_close).diff()
sigma_t         = btc_logret.rolling(180).std()        # 30天=180根4H
# 扩张窗口百分位（仅用 t_sweep 及之前）：
p_t = (历史 sigma 中 <= sigma_t 的比例)，历史样本 = 数据起点 .. t_sweep-1
# 预热：历史 sigma 有效样本 < 250 → vol_scalar = 1.0

vol_scalar = 0.5 if p_t >= 0.66 else 1.0

# 仓位（沿用 0B17 代码口径，注意单位 — DEC-046 修正5）
risk_budget   = 0.01 * portfolio                        # 货币单位
risk_distance = ATR(14)[t_sweep] * 3.5                  # 价格单位（不变）
quantity      = risk_budget / risk_distance             # 数量（不是名义！）
notional      = quantity * entry_price * vol_scalar     # ★唯一新增 vol_scalar
# 约束不变：单笔名义 <= 100% * portfolio，组合总敞口 <= 1x（超出按比例缩放）
# ❌ 禁止写成 0.01*portfolio/risk_distance 当名义 —— 该式在价格单位下是数量
```

**冻结常数（禁止调参）：** 滚动窗口 180、百分位阈值 0.66、缩仓乘子 0.5、预热 250。
**BTC 恐惧度 gauge 同时应用于 BTC/ETH/SOL 三品种。**

---

## 3. 约束条件（保持与 0B17 一致，不得改动）

- 信号：v4 Bullish Sweep + 双层 Regime（Daily EMA200 + BTC 30日动量>0）
- 品种：BTC/ETH/SOL，4H，仅做多，1x
- 止损：entry − ATR(14)[t_sweep] × 3.5；K线 low 触发后按该根 close×0.999 退出
- 退出：t+24 时间退出（第 24 根 4H K线）
- 入场价：下一根开盘 × 1.001
- 成本：手续费 0.05%/边 + 滑点 0.1%/边 + 资金费率 0.01%/8h
- ATR(14)[t_sweep]：与 v16/v17 同算法（Sweep K线时刻 14 根 TR 简单均值）
- 去重/持仓冲突/止损优先：与 0B17 一致
- 数据三分，最后 20% Holdout 物理截断，**禁止读取**

---

## 4. 验收标准（Claude 复核）

1. 脚本无报错运行，输出标准化结果报告至 `06_RESEARCH/RESULTS/`
2. 报告含：三品种组合 Sharpe / MaxDD / 交易数 / 止损率 / 胜率 / 净收益 / 平均名义仓位 / 总成本
3. **联合门槛判定**：Sharpe>1.0 AND MaxDD<25% → PASSED/FAILED（明确写出）
4. Walk-Forward 三段（WF1/WF2/WF3）Sharpe/MaxDD/净收益，**单列 WF2 是否改善**；
   **并列 WF1 在 0B17 ATR×3.5 vs 0B18 的对照（DEC-046）** —— 检查缩仓是否同时削弱了 2021 牛市的 WF1
5. 2022 子集：交易/止损率/净盈亏/Sharpe，**与 0B17 ATR×3.5 对照**
6. 高恐惧（p≥0.66）vs 低恐惧分组：笔数/平均仓位/期望/止损率对比
7. 品种分层表（BTC/ETH/SOL）
8. 实现审计：ATR 逐笔误差 < 1e-9；缩仓系数逐笔可复算；敞口/上限验证
9. pytest 回测规则测试 9/9 通过
10. 红队自查 8 项（预登记 §7）逐项确认
11. 执行报告写入 `04_AI_TEAM/CODEX_TASKS/REPORT_0B18_VOLPOS_STRATEGY.md`

---

## 5. 禁止事项

- ❌ 改动第 3 节任何"不变"项（改动即单变量违规，实验作废）
- ❌ 调整四个冻结常数（180/0.66/0.5/250）
- ❌ 读取或以任何方式接触 Holdout（最后 20%）
- ❌ 据回测结果反向修改预登记门槛或失效条件
- ❌ 覆盖写入 Memory Core（DECISION_LOG / CURRENT_STATE / PROJECT_CONTEXT）——
  决策性结论写入执行报告，由 Claude 审阅后决定是否升级

---

## 6. 产物清单（预期）

- `06_RESEARCH/CODE/v18_volpos_strategy.py`
- `06_RESEARCH/RESULTS/20260606_volpos_strategy.md`
- `06_RESEARCH/CODE/output/v18_volpos_metrics.json`
- `06_RESEARCH/CODE/output/v18_volpos_trades.csv`
- `06_RESEARCH/CODE/output/v18_volpos_equity.csv`
- `06_RESEARCH/CODE/output/v18_volpos_equity_curve.png`
- `04_AI_TEAM/CODEX_TASKS/REPORT_0B18_VOLPOS_STRATEGY.md`

【需要Codex】
