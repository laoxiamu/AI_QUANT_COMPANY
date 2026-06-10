# Opus 独立审计包：Phase 0A

请独立审阅以下阶段跨越判断，不继承Codex结论。

## 项目方向

AI-Native Quant Research Operating System。执行顺序：先验证Alpha，再建系统。

## Phase 0A验收

- Memory恢复：完成
- Research Protocol：完成
- VectorBT/研究回测能力：完成
- 首个假设预登记：完成
- 首个研究闭环：完成，结论FAILED

## 首个实验

版本：`v5_sweep_choch_fvg_bull_v1`

- 品种：BTC/ETH/SOL USD-M永续
- 周期：4H
- Regime：前一完整日收盘 > Daily EMA200
- 信号：Sweep → CHoCH → FVG Retrace
- 成本：手续费0.1%单边、滑点0.1%单边、历史资金费率
- 退出：50% at 1R，50% at 2R
- 实际交易：158
- Sharpe：0.60
- MaxDD：33.14%
- Expectancy：0.129R
- 验证集收益：-0.60%，Sharpe 0.11
- Walk-Forward Sharpe：1.89 / 0.58 / 0.53
- Holdout收益未访问，但信号结构数量曾在可行性阶段接触
- 六组±20%敏感性均失败

## Codex审计结论

P0=0，P1=5。建议进入短周期Phase 0B，优先修复Holdout政策、文档旧快照、回测自动测试、知识提炼，并预登记第二个更简单的假设。

## 请重点审查

1. Phase 0A是否真实满足5项验收？
2. 首个实验失败判断是否过严或过松？
3. Holdout结构性接触应如何处置？
4. 是否存在必须在阶段跨越前解决的P0？
5. 下一假设是否应降维为单一Sweep事件研究？
6. 是否同意进入Phase 0B，而不是直接进入Phase 1或停留0A？

