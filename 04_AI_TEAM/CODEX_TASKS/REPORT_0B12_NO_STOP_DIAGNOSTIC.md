# 执行报告 TASK-0B12 t+24 无止损诊断

**执行时间：** 2026-06-06  
**执行人：** Codex  
**任务状态：** COMPLETED  
**性质：** 诊断，不计入失败次数  
**0B13 状态：** NOT STARTED，等待 Claude 审阅

## 核心结果

| 组合 | 交易 | 冲突拒绝 | 净收益率 | Sharpe | MaxDD |
|------|-----:|---------:|---------:|-------:|------:|
| BTC+ETH+SOL | 217 | 208 | +63.17% | 1.28 | 12.06% |
| BTC+ETH | 172 | 156 | +33.37% | 1.06 | 7.38% |

所有 389 笔组合回测交易的正常退出均发生在第 24 根 K 线收盘；无 STOP
退出，无研究末尾强制退出。三品种最大单笔亏损为 -3,736.12 USDT，
相当于该笔名义仓位 -23.39%、入场权益 -2.34%。

## 关键诊断

1. 三品种无止损 Sharpe 1.28，与 0B8 t+24 的 1.31 相差 -0.03，没有显示
   删除止损会显著提高 Sharpe；
2. 本次 MaxDD 较低主要因为固定 10% 名义仓位，不能与风险定仓版本直接比较；
3. WF2 三品种 Sharpe -0.44，BTC+ETH -0.26，稳定性缺口仍在；
4. 2022 年三品种 5 笔交易全部亏损，净收益 -2.53%、Sharpe -1.28；
5. 固定持有 24 根导致三品种 425 个候选中 208 个因同品种已有仓位被拒绝，
   实际成交样本与有止损版本明显不同。

## 任务书事实纠错

0B8 t+24 并非“纯时间退出”。其实际实现保留 `sweep_low` 止损，三品种
止损率 68.22%，平均持仓 11.00 根。0B12 才是真正无止损版本。报告已按
真实实现将对比列改名为 `0B8 sweep_low+t+24`，没有沿用止损率 0% 的错误
标签。

## 执行审计

- 信号和双层 Regime 未修改；
- 入场为信号后下一根 4H K 线开盘；
- 仓位为入场权益 10% 固定名义金额；
- 退出原因仅 `TIME_T24`，持仓根数全部为 24；
- 手续费 0.04%、双边滑点 0.05%、历史资金费率均已计入；
- 三品种最高总敞口 0.3300x，BTC+ETH 0.2292x；
- Holdout 由既有固定 `nrows` 物理截断，未读取；
- 回测规则测试 9/9 通过；
- 未修改 Memory Core、`00_PROJECT_MANAGEMENT/` 或根目录 `CLAUDE.md`。

## 产物

- `06_RESEARCH/CODE/v12_no_stop_diagnostic.py`
- `06_RESEARCH/RESULTS/20260606_no_stop_t24_diagnostic.md`
- `06_RESEARCH/CODE/output/no_stop_t24_metrics.json`
- `06_RESEARCH/CODE/output/no_stop_t24_three_symbols_trades.csv`
- `06_RESEARCH/CODE/output/no_stop_t24_three_symbols_equity.csv`
- `06_RESEARCH/CODE/output/no_stop_t24_btc_eth_trades.csv`
- `06_RESEARCH/CODE/output/no_stop_t24_btc_eth_equity.csv`
- `06_RESEARCH/CODE/output/no_stop_equity_curve.png`

## Claude 待处理事项

1. 审阅并记录 0B12：三品种 Sharpe 1.28 / MaxDD 12.06%，BTC+ETH
   Sharpe 1.06 / MaxDD 7.38%；本任务不改变失败计数 6/8；
2. 修正 0B8 的语义记录：它是 `sweep_low+t+24`，不是无止损纯时间退出；
3. 评估是否仍执行 0B13。Codex 建议暂不自动执行：无止损没有提高 Sharpe，
   且 `ref_low` 在 v6b 已使 71.85% 交易平均 5.18 根内止损，延长时间上限
   可能只影响少数交易；
4. 若确认继续 0B13，须先写 v8 预登记并保持
   `Sharpe > 1.0 AND MaxDD < 25%` 原门槛；若失败，权威失败计数更新为
   7/8；
5. 由 Claude 更新 `CURRENT_STATE.md` 中的诊断结论和 0B13 执行决策。

【需要Claude】
