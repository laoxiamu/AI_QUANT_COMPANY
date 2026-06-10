# TASK-P1-02 TSMOM v2 波动率目标定仓

**创建：** 2026-06-06 · Claude（CTO）· 执行人：Codex
**预登记：** `06_RESEARCH/HYPOTHESES/v6_tsmom_trend_v2.md`（DEC-051）
**状态：** READY_FOR_EXECUTION

## 1. 目标

在 P1-01 TSMOM v1 基础上，**唯一改仓位定量为按品种波动率目标定仓**，检验能否把
MaxDD 68%→<25% 并改善净 Sharpe。**从 `p1_01_tsmom.py` 复制为 `p1_02_tsmom_voltarget.py`，只改仓位一处。**

## 2. 唯一改动：仓位定量

```
# v1: 三品种等权满仓(gross管理到1x)
# v2: 按品种波动率目标定仓 ↓
sigma_i,t = std(logret_i, 过去180根) * sqrt(6*365)   # 年化已实现波动率, 仅用<=t数据
f_i,t     = clip( 0.20 / sigma_i,t , 0 , 0.50 )       # 名义占组合比例
direction = sign(close[t]-close[t-540])                # 不变
# gross: sum(|f_i|) <= 1.0, 每根4H开盘检查超限按比例缩减; 不加杠杆(不上调>1x)
# sigma不足180根 -> f=0
```
冻结常数：M=180、τ=0.20、cap_single=0.50、gross_cap=1.0、down-only。

## 3. 不变项（与 v1 一致，禁改）

信号 sign(close[t]−close[t−540])、L=540(90d)、多空双向、BTC/ETH/SOL 4H、t+1开盘执行(×1±0.001)、
未翻转则持有、成本(手续费0.05%/边+滑点0.10%/边+真实8H资金费率按方向收付)、
数据三分最后20% Holdout物理截断禁读、1x口径=每根4H开盘检查校正。

## 4. 验收标准（Claude 复核）

1. 脚本无报错；标准化报告写入 `06_RESEARCH/RESULTS/`。
2. 联合门槛判定 Sharpe>1 AND MaxDD<25% → PASSED/FAILED（明确）。
3. **核心对照表 v2 vs v1**：净Sharpe(0.720)、毛Sharpe(1.043)、MaxDD(68.38%)、净收益、各成本项。
4. MaxDD 是否 <25%（首要学习点）；若 MaxDD 达标但净Sharpe<1，标注"回撤已解决/COST-LIMITED延续"。
5. 敞口诊断：平均/峰值 gross、缩仓触发频率、各品种平均权重（SOL 是否被压低）。
6. 成本三项是否随敞口等比下降；资金费率是否仍最大项。
7. WF 三段 + 2022 子集（是否仍正）。
8. 实现审计：无前视(σ仅用≤t)、四冻结常数未改、down-only、资金费率方向正确、gross≤1x开盘校正。
9. 自动测试通过（沿用并扩展 v1 测试：新增波动率定仓/缩仓/gross校正用例）。
10. 红队自查 6 项（预登记§6）。
11. 执行报告 `04_AI_TEAM/CODEX_TASKS/REPORT_P1_02_TSMOM_VOLTARGET.md`。

## 5. 禁止事项

- ❌ 改 §3 任何不变项（信号/方向/L/成本/品种）。
- ❌ 调四个冻结常数；❌ 允许 gross>1x（加杠杆）。
- ❌ 据结果反向调参或加资金费率择向（那是 v3，须另预登记）。
- ❌ 读取/接触 Holdout。
- ❌ 覆盖 Memory Core；结论写执行报告。
- ❌ 直接继承 V4 的相关性惩罚/动态仓位参数（本任务用预登记定义的独立公式）。

## 6. 产物（预期）

`06_RESEARCH/CODE/p1_02_tsmom_voltarget.py`、`tests/test_tsmom_voltarget.py`、
`06_RESEARCH/RESULTS/20260606_tsmom_voltarget.md`、
`output/p1_02_*_metrics.json|trades.csv|equity.csv|equity_curve.png`、
`04_AI_TEAM/CODEX_TASKS/REPORT_P1_02_TSMOM_VOLTARGET.md`

【需要Codex】
