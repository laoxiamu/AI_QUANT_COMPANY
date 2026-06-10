# Sweep 双层 Regime 止损位置对照预登记

**实验版本号：** `v5_sweep_regime_bull_v6b`  
**状态：** COMPLETED_FAILED  
**预登记时间：** 2026-06-06  
**执行人：** Codex  
**研究类型：** 策略回测，止损位置对照

## 语义纠错

任务标题及原说明将 `ref_low` 称为“更宽止损”，该说法与 Bullish Sweep
定义矛盾。冻结定义为：

- `ref_low = min(low[t-20:t])`，不含 Sweep K线；
- `sweep_low = low[t]`；
- Bullish Sweep 必须满足 `sweep_low < ref_low` 且 `close[t] > ref_low`。

因此多头交易中，`ref_low` 高于 `sweep_low`，将止损从 `sweep_low` 改到
`ref_low` 会缩短入场价到止损价的距离，是**更紧止损**，不是更宽止损。
本实验仅按任务字面测试 `ref_low + t+12`，不得用“允许更大波动”“仓位因更宽
风险而缩小”等错误逻辑解释结果。

## 研究问题与单变量

在相同 Bullish Sweep、双层 Regime、入场、成本、持仓冲突、1x 敞口上限和
`t+12` 时间退出下，对比：

1. baseline：`sweep_low + t+12`；
2. candidate：`ref_low + t+12`。

唯一变化为止损价。v6 尚无已完成结果，因此 baseline 与 candidate 必须由同一
代码、同一数据快照、同一执行口径现场运行，不得引用未完成的 v6 数字。

## 固定策略口径

- 品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多；
- 信号：冻结事件文件中的 Bullish Liquidity Sweep；
- Regime：各品种前一完整 UTC 日 `close > EMA200`，且前一完整 UTC 日可得的
  BTC 30 日对数收益率 `> 0`；
- 入场：信号 K线下一根 4H K线开盘，买入滑点 `0.05%`；
- baseline 止损：Sweep K线最低价 `sweep_low`；
- candidate 止损：Sweep 前 20 根 K线最低价 `ref_low`；
- 退出：入场后第 12 根 4H K线收盘全仓退出；同根 K线止损优先；
- 仓位：每笔风险预算为入场时账户权益的 `1%`；
- 账户：初始 `100,000 USDT`，总名义敞口上限 `1x`；
- 手续费：每次成交 `0.04%`；
- 资金费率：使用 Binance 历史 8H 真实资金费率；缺失结算点按
  `0.01%/8h` 补齐，禁止按零处理；
- 持仓冲突：同品种已有多仓时拒绝新信号；
- 两个止损版本分别独立运行，共享各自账户，不交叉影响。

## 无效风险拒绝

每个版本均用含入场滑点的实际入场价计算：

`nominal_risk = entry_price - stop_price`

若 `entry_price <= stop_price`，则 `nominal_risk <= 0`，该候选不构成有效多头
风险区间，必须明确拒绝，不得开仓、修正止损或使用绝对值。baseline 与
candidate 的无效风险拒绝数必须分别统计并报告。

## 数据封存

只能以固定 `nrows` 读取已注册快照的前 80%，不得先读取全文件再切片：

| 品种 | 4H总行数 | 研究 `nrows` | Holdout起点 | 资金费率 `nrows` |
|------|----------:|-------------:|-------------|------------------:|
| BTC | 16,267 | 13,013 | 2024-12-09 16:00 | 5,414 |
| ETH | 16,267 | 13,013 | 2024-12-09 16:00 | 5,414 |
| SOL | 12,743 | 10,194 | 2025-04-06 04:00 | 4,997 |

程序须校验实际读取行数、最大时间、时间升序和重复时间戳。禁止读取、统计或
打印 Holdout 内容。

## 必须报告

两个止损版本均须报告：

- BTC+ETH+SOL 三品种组合；
- BTC+ETH 双品种组合；
- 分品种指标；
- 2019-2020、2021、2022、2023-2024 分时期指标；
- 三段 Walk-Forward Sharpe；
- 候选数、成交数、持仓冲突、无效风险、无敞口容量拒绝数；
- 净收益、年化收益、Sharpe、MaxDD、Expectancy R；
- 止损触发率、平均持仓 K线、手续费、资金费率；
- `entry - sweep_low` 与 `entry - ref_low` 的风险距离及二者差异分布。

差异应描述为 candidate 相对 baseline **收紧了多少**。不得将
`ref_low - sweep_low > 0` 称为“额外风险宽度”。

## 预登记判定

候选通过门槛沿用策略标准：Sharpe `> 1.0` 且 MaxDD `< 25%`。

- 若 candidate 达标：仅记录“更紧的结构位止损版本通过样本内门槛”；
- 若未达标：`v6b` 判定 FAILED；
- 不论结果，禁止据此查看 Holdout；
- baseline 是本任务现场对照，不单独增加失败计数；candidate 是 v6b 判定对象。

## 解释限制

`ref_low` 更高会同时改变止损触发概率、单笔名义风险、按 1% 风险计算的期望
仓位，以及 1x 敞口约束下的实际缩放。结果只能按这些真实机制解释，禁止沿用
原任务“止损更宽、仓位自动更小”的错误因果链。

## 执行结果

预登记完成后按冻结口径执行。三品种 candidate 的 Sharpe 为 1.22、MaxDD
为 28.45%；BTC+ETH candidate 的 Sharpe 为 0.92、MaxDD 为 22.57%。
两套组合均未同时满足 Sharpe `> 1.0` 且 MaxDD `< 25%`，因此实验 FAILED。
完整结果见 `06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v6b_BACKTEST.md`。
