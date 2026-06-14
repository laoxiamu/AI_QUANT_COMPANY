# Delta 中性 Carry 预登记 v3

**状态：** PREREGISTERED DRAFT v3 — 待独立 Risk Reviewer 盲审；本文不构成自审通过
**起草：** Codex（实现细化，非 thesis owner）｜**日期：** 2026-06-14（Asia/Singapore）
**基线：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v2.md`
**必改依据：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v2.md`
**Protocol v1.4 AI 证据三行：** ①本策略非 LLM 作 alpha 信号，机制=人工经济归纳（杠杆多头需求→正 funding）；知识截止 2025-05，carry 经济链为公开市场常识。②最可能错处：funding 长期转负 / 制度变化（现货 ETF、更多做空工具）使风险溢价消失；短永续腿急涨强平致 delta 暴露。③不以多 agent 共识为证据；本预登记仅作设计冻结。

---

## §0 研究身份与独立性（核心重构不变）

1. **历史工作集（全部输入 `<2024-12-10`）= 锁定可行性复核（FEASIBILITY-LOCK）。** 用途仅为检验“按 v3 完全冻结口径、含全成本与路径级强平账本，历史上 carry 是否仍可行”。设计参数已被历史探索污染，因此历史 PASS 不是独立机制确认、**不耗独立 Alpha 计数、不授权核心资本上线**，最多表述为“历史可行性复核通过”。
2. **真确认 = 前向 SHADOW（paper-trade，未来数据）。** v3 经独立 Reviewer 放行后，按 §9 的固定起点、固定样本量和一次性检验运行；不得回填放行前数据，不得因观察到结果而延长或提前停止。只有前向 net E[R] 显著>0、无强平且跑赢现金零基准，才计入前向确认证据。
3. **证据等级上线 = Founder 治理决定。** 纸面=0；历史复核过=观察级；前向 shadow 过=具备小额真金申请资格；实盘过后才可另议升额。前向 PASS 不自动下单、不自动成为核心资本，也不改变历史段“不耗独立计数”的定性。

盲审副本不得披露待确认的具体收益数值。

---

## §1 机制与策略命题（不变）

- **机制命题（可证伪）：** carry 净收益主要来自 funding 收取，而非 basis 波动、方向价格漂移或再平衡运气。必要条件是 `funding_received > 0`，且 funding 是净收益归因中的最大正贡献项。
- **策略命题：** 按 §2-§6 冻结构造和全成本执行后，净收益通过 §5 全部基础 carry 硬门。
- **非 alpha 声明：** 不以 funding 极端、价格反转或 funding 均值回归择时；正、负 funding 时段均按冻结规则持有。OI 信号只能把双腿同步减至 50%，不能加到 100% 以上。
- **制度依赖：** 逐年和滚动 12 个月报告净 funding；交易所 funding、保证金或合约制度变更按实际生效时点分段，不得结果后挑窗口。

---

## §2 构造、资本恒等式与保证金账本

### §2.1 Venue、合约、价格源与账户模式

| 项目 | 唯一定义 |
|---|---|
| Venue | Binance |
| 现货 | Binance Spot `BTCUSDT`、`ETHUSDT` |
| 永续 | Binance USDⓈ-M、USDT 本位线性永续 `BTCUSDT`、`ETHUSDT` |
| 账户模式 | 标准 USDT-M **cross margin**；关闭 portfolio margin 和 multi-assets mode；BTC/ETH 短仓共用一个 USDT cross wallet |
| 现货信号/估值 | Binance Spot 1H kline close |
| 现货成交 | Binance Spot 次一根 1H kline open |
| 永续信号/损益 | Binance USD-M 合约 1H kline close；成交用次一根合约 1H kline open |
| 保证金/强平 | Binance USD-M mark price 1H OHLC；mark 不作现货成交价或 basis 价 |
| basis | 同一 UTC 1H 的 `spot close - perpetual contract close`；不得用 mark 代替 |
| funding | Binance 实际 funding rate、实际结算时间和结算时短腿名义 |
| OI | Binance USD-M `sumOpenInterestValue`，5M 数据每小时取最后一个有效值；不前填 |
| 维持保证金 | 对应历史时点的 Binance leverage bracket（`mmr`、`cum`）和 liquidation clearance fee |

任一必要价格、funding、OI、历史保证金阶梯或清算费缺失且无法从执行前冻结的输入 manifest 取得，相关必要项记 `N.A. ⇒ FEASIBILITY-LOCK FAIL`；不得用当前费率、mark、插值或另一 venue 代替历史值。

### §2.2 初始资本分配与 `N`

令策略初始 sleeve 资本为 `C0`，统一按 USD 等值记账；`C0` 是所有收益率、MDD、log growth 和年化指标的**唯一固定分母**。初始恒等式为：

```text
C0 = S0 + M0 + B0 + E0

S0 = 现货实际本金
M0 = 永续 cross wallet 初始保证金
B0 = 闲置缓冲现金
E0 = 事件备用现金
```

先冻结现金桶：

```text
B0 = 0.10 * C0
E0 = 0.10 * C0
paired_capital = C0 - B0 - E0 = 0.80 * C0
```

BTC/ETH 权重仍为探索所选并冻结为 `w_BTC=0.70`、`w_ETH=0.30`。对品种 `i`，其现货与永续保证金合计预算：

```text
pair_budget_i = 0.80 * C0 * w_i
```

在初始成交时点取现货 open `S_i,0`、永续合约 open `F_i,0`。为使两腿基础资产数量严格相等且永续初始杠杆为 1.0：

```text
q_i,0 = pair_budget_i / (S_i,0 + F_i,0)
spot_principal_i = q_i,0 * S_i,0
N_i = perp_initial_notional_i = q_i,0 * F_i,0
perp_initial_margin_i = N_i
```

因此 `q_spot_i,0 + q_perp_i,0 = 0`（其中短永续 `q_perp<0`），且
`spot_principal_i + perp_initial_margin_i = pair_budget_i`。`N_i` 是该品种冻结的初始短永续名义及后续 100% 状态的名义基准；它不是额外资本项。

**资本占用表（初始时点）：**

| 资本桶 | 数值化规则 | 是否进入 `C0` | 是否另计为 `N` |
|---|---:|---:|---:|
| BTC 现货本金 | `0.56*C0*S_BTC,0/(S_BTC,0+F_BTC,0)` | 是 | 否 |
| BTC 永续初始保证金 | `N_BTC=0.56*C0*F_BTC,0/(S_BTC,0+F_BTC,0)` | 是 | 否；`N_BTC` 即本行 |
| ETH 现货本金 | `0.24*C0*S_ETH,0/(S_ETH,0+F_ETH,0)` | 是 | 否 |
| ETH 永续初始保证金 | `N_ETH=0.24*C0*F_ETH,0/(S_ETH,0+F_ETH,0)` | 是 | 否；`N_ETH` 即本行 |
| 闲置缓冲现金 `B0` | `0.10*C0` | 是 | 否 |
| 事件备用现金 `E0` | `0.10*C0` | 是 | 否 |
| **合计** | **`C0`** | **唯一一次** | **无额外资本** |

所有现金桶初始均为 USDT，并按 §4 的 USDT/USD 参考价折算 USD。缓冲或事件现金转入 futures wallet 只是 `B/E → M` 的桶间转移，不创造收益、不改变 `C0`、不得在 margin 与现金中重复计数。OI 减仓所得现货现金进入 `B`；cross wallet 中释放的保证金仍留在 `M`，不重复列为现金。

时点 `t` 的 sleeve 权益只用于净值，不替换固定分母：

```text
C_t = spot_market_value_t + futures_margin_balance_t
      + idle_cash_t + event_cash_t - external_liability_t
r_t = (C_t - C_(t-1) - external_flow_t) / C0
```

其中 `futures_margin_balance_t = wallet_balance_t + unrealized_perp_pnl_t`。
研究期间禁止外部注资；`external_flow_t=0`。任何超出 `B/E` 的补款需求均不得从 sleeve 外补入。

### §2.3 持仓、delta 与每日再平衡

- 初始开仓在每段首个可交易日 `00:00 UTC` 信号后的次一根 1H open 完成；两腿数量按 §2.2 相等。
- 共同指数价 `I_i,t` 只用于把基础资产数量差换算为 delta 名义：

```text
delta_drift_i(t) = abs(q_spot_i(t) + q_perp_i(t)) * I_i,t / N_i
```

- 每日 `00:00 UTC` 用当根 1H close 检查。若 `delta_drift_i>5%`，次一根 1H open **只调整现货腿**到 `q_spot_i=-q_perp_i`；永续腿不动。若 `≤5%` 不交易。该规则修正的是数量失配，不把 spot/perp basis 误当方向 delta。
- 若同一时点既有 OI 状态切换又有每日再平衡，先执行 §3 的双腿状态切换，并取消该时点单独的每日再平衡；状态切换后的现货目标已经与永续数量相等。

### §2.4 Cross-margin 逐 1H 账本与强平

对每个 1H `h` 维护：

```text
wallet_balance_h =
    M0 + transfers_in - transfers_out
    + realized_perp_pnl + funding_received
    - futures_fees - liquidation_fees

unrealized_perp_pnl_h = Σ_i q_perp_i * (mark_i,h - entry_price_i)
margin_balance_h = wallet_balance_h + unrealized_perp_pnl_h

position_notional_i,h = abs(q_perp_i) * mark_i,h
maintenance_margin_i,h =
    position_notional_i,h * mmr_i,h - cum_i,h
maintenance_margin_h = Σ_i max(0, maintenance_margin_i,h)
```

`mmr/cum` 取该时点、该名义所在的历史 Binance bracket。账本顺序唯一：

1. **小时 open：** 先执行上小时已排定的现金补款，再执行 OI/再平衡交易；各自按对应市场 open 成交并立即计费。
2. **结算点：** 若本小时含实际 funding timestamp，按结算前实际短腿名义入账。
3. **小时内最坏点：** 对短仓用该小时 mark high 重算 `margin_balance`、bracket 和 `maintenance_margin`。若 `margin_balance <= maintenance_margin`，视为该小时首次触发 account-level liquidation，不允许等到 close 后补款。
4. **小时 close：** 若未强平且 `maintenance_margin < margin_balance < 3*maintenance_margin`，记 `buffer_breach`，并排定次一根 1H open 补款至 `3*maintenance_margin_open`。
5. **补款来源：** 先用 `B`；只有该小时属于 §6 冻结事件窗时，`B` 用尽后才可用 `E`。补款额为可用现金与缺口的较小值。补款后仍 `margin_balance <= maintenance_margin` 则立即强平；不足以回到 3 倍但仍高于维持线则继续持仓并保留 breach 状态。

Account-level liquidation 时，BTC/ETH 所有未平短永续均在首次触发小时按 mark high 加当档滑点买回，并计历史 liquidation clearance fee；这计为一个 liquidation episode，同时记录受影响品种。现货腿保留到次一根 1H open 后全部卖出，期间方向暴露和价格损益完整入账；此后该路径保持现金，不再重开。若清算后 margin balance 为负，`bankruptcy_loss=max(0,-margin_balance_after_liquidation)`，sleeve 权益最低记零，不允许外部追加入金。

ADL 只在 Binance 官方市场/账户执行记录能证明该小时发生时入账：按实际减仓数量和执行价替代普通平仓；缺少执行数量或价格则该事件项 `N.A.⇒FAIL`。提现暂停不改变 mark-to-market，但禁止暂停期内 `B/E` 跨账户转入；已在 futures wallet 的资金仍可用。

---

## §3 A-1×Carry OI 风控触发器

### §3.1 信号

```text
d6h_i(t) = OI_i(t) / OI_i(t-6h) - 1
oi_6h_pctl_i(t) =
    d6h_i(t) 在严格过去固定滚动窗 [t-365d, t) 中的 midrank 分位
```

窗口是**固定 365 日滚动窗，不是扩张窗**；不含当前值。至少覆盖 180 日历日且有 `>=720` 个有效 1H 样本才可出信号，否则状态保持 100% 且记 warm-up，不以缺数触发。OI 不前填。

### §3.2 双腿减仓、成交顺序与恢复

- `oi_6h_pctl_i(t)<=0.01` 且当前为 100%：在次一根 1H open 把该品种**现货和短永续同步降到 50%**，目标短永续名义=`0.5*N_i`，目标数量=`0.5*N_i/F_i,open`，现货目标数量与短永续绝对数量相等。
- 风险优先顺序：减仓时先用 reduce-only 买回短永续，再卖出匹配现货；恢复时先买入现货，再卖出短永续。两腿均用各自次一根 1H open，模拟账本视为同一时间戳；实盘 shadow 要求第二腿在第一腿确认后 60 秒内提交。
- 任一腿不能足额成交时，立即按当时可得价反向撤销已成交第一腿，回到切换前状态；所有成交、撤销、fee 和 slippage 均入账，该次状态切换记 `execution_fail`，24h 内不重试。
- 首次成功减仓启动 24h refractory。期间新触发不延长。24h 到期时若当根仍触发，则续 24h；若不再触发，则次一根 1H open 按上述恢复顺序一次性恢复到 100%。
- BTC/ETH 各自独立运行状态机；无论 50% 或 100% 状态，成功切换后均满足 `q_spot+q_perp=0`，减仓本身不得制造方向暴露。

### §3.3 判决去循环

1. **基础 carry FEASIBILITY-LOCK** 只用不含 OI 触发器的 baseline 按 §5.2 判 PASS/FAIL。
2. 只有 baseline PASS，才评估 OI 模块是否保留。非劣检验为同一路径“有触发器−无触发器”，`H0: ΔnetER<=-0.5%/年`，单侧 `alpha=0.05`，同步 1 周块、`B=2000`、`seed=20260614`。
3. 尾部门唯一化：若 baseline 的事件期 liquidation episodes `L0>0`，要求触发器版 `L1<L0`；若 `L0=0`，要求 `L1=0`。同时要求触发器不得增加 account-level liquidation 总次数。
4. 非劣与尾部门均通过才“保留 OI 模块”。任一不通过则 OI 模块 REJECTED，但不得改写 baseline 的独立 PASS/FAIL，也不得在有/无触发器两版中择优包装 edge。

---

## §4 成本与无重复损益账本

### §4.1 成本

```text
regular_fee_per_side = 0.10%
baseline_slippage_per_side = 0.10%
event_slippage_per_side = 0.30% / 0.50% / 1.00% 三个压力档

trade_cost =
    abs(notional_filled) * (fee_per_side + slippage_per_side)
```

- 现货、永续每一腿分别计费；固定用 0.10%，不根据 VIP、maker/taker 或结果后费率优化。
- 开仓、强制收尾平仓、每日再平衡、OI 减仓/恢复、失败撤销、强平和强平后现货处置均逐笔计费。
- 事件窗内对每一笔交易分别重跑 0.30%/0.50%/1.00% 滑点压力档；fee 仍为 0.10%。清算另加历史 liquidation clearance fee，不以普通手续费代替。
- `financing=0`：全部资金属于 `C0`，无借贷。任何外部借款或补资均为协议违规。

### §4.2 权威损益恒等式

对品种 `i`、小时 `h`，持仓价格损益只计算一次：

```text
spot_pnl_i,h = q_spot_i,h-1 * (spot_close_i,h - spot_close_i,h-1)
perp_pnl_i,h = q_perp_i,h-1 * (perp_contract_close_i,h - perp_contract_close_i,h-1)

net_pnl_h =
    Σ_i (spot_pnl_i,h + perp_pnl_i,h)
    + funding_received_h
    + cash_fx_pnl_h
    - regular_fees_h
    - slippage_h
    - liquidation_fees_h
    - ADL_loss_h
    - bankruptcy_loss_h
```

funding 按实际结算名义计算；负 funding 原样入账。USDT 现金和 futures margin 的 USD 折价统一进入 `cash_fx_pnl`。USDT/USD 参考价冻结为同小时下列两个 Binance index 交叉价的中位数：

```text
u_BTC = BTCUSD_COINM_index / BTCUSDT_USDM_index
u_ETH = ETHUSD_COINM_index / ETHUSDT_USDM_index
USDTUSD = median(u_BTC, u_ETH)
```

两个交叉价均须存在；缺失时不得假定 1.00 或换用结果后挑选的稳定币，记 `N.A.⇒FAIL`。

机制归因表是上述权威 PnL 的**互斥拆分，不是额外加项**：

```text
paired_qty_i,h = min(q_spot_i,h, abs(q_perp_i,h))
basis_pnl_i,h =
    paired_qty_i,h * [(Δspot_close_i,h) - (Δperp_contract_close_i,h)]
rebalance_pnl_i,h =
    (spot_pnl_i,h + perp_pnl_i,h) - basis_pnl_i,h

net_pnl =
    funding_received + basis_pnl + rebalance_pnl + cash_fx_pnl
    - fees - slippage - liquidation_fees - ADL_loss - bankruptcy_loss
```

不得再把 basis MTM、腿级 PnL或“事件损失”重复加到净收益。事件标签只用于切片；事件中的价格、funding、清算、ADL、现金折价已经由上述互斥科目入账。

---

## §5 历史 FEASIBILITY-LOCK 验收与 1H 路径 bootstrap

### §5.1 主收益推断

- 观测单位：8h funding interval 的组合净收益，小时成本归入其发生所在 interval。
- 同步 UTC BTC/ETH 向量 moving-block bootstrap；块长 21 个 8h interval（1 周），`B=2000`，`seed=20260614`。
- 点估计：`annualized_net_ER = mean(r_8h)*1095`。
- 显著性：在 `H0:E[R]=0` 边界下，把组合 8h 净收益减去样本均值后重心化；对重心化序列做上述块重采样。`p=(1+#(T_b>=T_obs))/(B+1)`，单侧 `alpha=0.05`。同时报告未重心化 bootstrap 的 percentile 95% CI。
- 年化 log growth 唯一公式：`mean(log1p(r_8h))*1095`。

### §5.2 基础 carry 二元门

**FEASIBILITY-LOCK PASS 必须全部满足：**

- [ ] `annualized_net_ER>0` 且 §5.1 单侧 `p<=0.05`。
- [ ] 赢亏比 `mean(r|r>0)/abs(mean(r|r<0)) >=1.5`。
- [ ] 完整 UTC 年中净 E[R]>0 的年份占严格多数；不足一个完整年不计入分母。
- [ ] 年化 log growth >0。
- [ ] 相对现金零收益基准的净超额收益通过同一个 `H0:E[R]<=0` 检验。
- [ ] §5.3 分档爆仓概率通过。
- [ ] 组合 MDD `<=15%`，并通过 §6 固定事件直接重演。
- [ ] WF 三段中至少两段净 E[R]>0。
- [ ] 所有必要数据均非 N.A.，且无 Holdout/全样本分位/事后改窗违规。

任一不满足即 **FEASIBILITY-LOCK FAIL**。历史 PASS 只允许使用 §0 的限定表述。

### §5.3 2000 条一年路径：逐 1H 重演保证金账本

**bootstrap 输入不是 8h 收盘收益。** 先构造按同一 UTC 对齐的完整 1H 状态向量：

```text
X_h = {
  spot open/close return,
  perpetual contract open/close return,
  mark open/high/low/close return,
  index return,
  funding rate and settlement flag,
  OI value/change,
  leverage-bracket id and liquidation fee,
  event/withdrawal/ADL flags,
  USDT/USD reference return,
  data-availability flags
}_BTC,ETH
```

路径算法冻结如下：

1. 候选块为从任意 `00:00 UTC` 开始、连续完整 168 小时的同步 `X_h`；跨缺失小时的块不得入池。168 小时是 8 小时结算周期的整数倍。
2. 每条复制独立采样 105 个 168h 块并串接，截取前 17,520h（730 天）。同一块内 BTC/ETH、mark、funding、OI、事件及制度字段始终一起移动，禁止逐列独立抽样。
3. 价格按采样到的 1H return/OHLC 相对量从固定基准连续复原；不直接拼接绝对价格。块边界不插值、不重估 basis。
4. 前 8,760h 只作 OI 365 日滚动窗口 warm-up；在第 8,761 小时以 `C0` 重新初始化资本和持仓，refractory 归零。后 8,760h 是唯一的一年评价期。
5. §5 基础 carry 风险门先在**关闭 OI 模块**的 baseline 上逐小时按 §2.4、§4、§6 重新运行完整交易和保证金状态机，重新产生 funding、补款、强平、delta 暴露、费用和净值；不得从已聚合的 8h 收益或组合 MDD 推断 liquidation。只有 baseline PASS 后，才在同一批路径上另跑开启 §3 的配对版本，用于 OI 模块判决。
6. 每条路径分别运行基准滑点及三个事件压力滑点账本。若路径含 §6 事件小时，只替换事件小时内发生交易的滑点；该路径的风险统计取四个账本中的最坏值。
7. `B=2000` 条路径，统一 `seed=20260614`。报告 account-level liquidation 概率、各品种受影响概率、首次强平小时、补款次数和年 MDD。

硬门：

```text
P(一年 MDD >= 35%) <= 20%
P(一年 MDD >= 20%) <= 10%
```

两者均按 2000 条路径的最坏压力账本频率计算。任一路径无法重建历史 bracket、补款延迟或首次强平状态，则该分档爆仓项 `N.A.⇒FAIL`。

### §5.4 WF

按历史工作集 8h interval 数时间等分三段，余数依次分给前段。每段在首个可交易 open 用同一 `C0` 独立开仓，在段末最后一个 close 强制平仓并计成本；不把持仓或 PnL 跨段传递，不在段内重估参数。这样切点持仓被显式结算而非静默跨界。至少两段净 E[R]>0。

---

## §6 事件清单与规则生成事件

### §6.1 固定命名事件（半开 UTC 窗口）

| 事件 | Venue/策略资产 | UTC 起点（含） | UTC 终点（不含） | 说明 |
|---|---|---|---|---|
| ETH Merge | Binance ETH spot + USDT-M perp | `2022-09-08T06:00:00Z` | `2022-09-22T07:00:00Z` | 围绕 Merge 时点 `2022-09-15T06:42:42Z` 前后各 168h，向外对齐完整 1H |
| Terra/LUNA/UST 崩盘 | Binance BTC、ETH spot + USDT-M perp | `2022-05-09T00:00:00Z` | `2022-05-14T00:00:00Z` | 市场级冲击；不得只保留受益品种 |
| 3AC/借贷连环 | Binance BTC、ETH spot + USDT-M perp | `2022-06-12T00:00:00Z` | `2022-07-01T00:00:00Z` | 从 Celsius 暂停提现起覆盖 3AC/借贷传染至 6 月末 |
| FTX 暴雷 | Binance BTC、ETH spot + USDT-M perp | `2022-11-06T00:00:00Z` | `2022-11-15T00:00:00Z` | 覆盖公开挤兑至冻结窗口终点 |

ETH Merge 已在前序材料披露，不作独立确认样本，只作事件压力诊断。

### §6.2 永续脱锚规则

对每个策略永续逐 1H 计算：

```text
depeg_i,h = abs(mark_close_i,h / index_close_i,h - 1)
```

- 连续两个完整 1H bar 均 `depeg>2%` 才生成事件。
- 起点是该连续 run 的第一个 bar open。
- 起点后首次出现连续六个完整 1H bar 均 `depeg<=0.5%`，事件终点为第六个 bar 的 close；若直到工作集末仍未恢复，终点取工作集 cutoff。
- 相邻事件间隔 `<=6h` 时合并为一个事件。
- mark/index 任一缺失会中断连续计数；若缺失发生在已触发事件内，事件建模 `N.A.⇒FAIL`，不得用插值缩短窗口。
- 第二个确认 bar close 后，次一根 1H open 将该品种双腿降到 0：先买回短永续，再卖出现货；事件期间保持现金。事件终点后再等待 24h，在下一个 `00:00 UTC` 检查点后的 1H open 恢复。baseline 恢复到 100%；开启 OI 模块的配对版本按当时 OI 信号恢复到 50% 或 100%。退出、等待和恢复全部计逐腿成本，脱锚风险规则优先于每日再平衡和 OI 状态切换。

### §6.3 Binance 提现暂停规则

- 只扫描 Binance 官方 announcement archive 及执行前冻结的 BTC、ETH、USDT withdrawal-status 小时快照。
- 仅当官方记录明确显示 BTC、ETH 或 USDT 提现不可用并持续至少两个完整 1H bar，才生成事件。
- 起点取官方生效时间；无生效时间时取公告发布时间向下取整到小时。终点取官方恢复生效时间；无明确时间时取状态快照连续两个小时恢复可用后的第二个小时 close。
- 公告与状态冲突时取更早起点、更晚终点；缺少终点证据则持续到工作集 cutoff。

### §6.4 新事件纳入算法与硬门

固定命名事件之外，**只能**由 §6.2 或 §6.3 的全工作集机械扫描生成事件；禁止凭新闻记忆新增名称、事后移动边界或删除亏损事件。执行前输出按 `(start_utc, end_utc, rule_id, symbol)` 排序的事件 manifest 及 SHA-256；同一规则、同一输入必须生成同一清单。重叠窗口取并集，不能裁短。

每个固定或规则生成事件均按真实 1H 路径直接重演 §2.4 账本，并分别报告 0.10%/0.30%/0.50%/1.00% 滑点。任一压力档发生 account-level liquidation，或事件窗口至恢复后 24h 的 sleeve MDD>15%，则 §5 的事件硬门 FAIL。

---

## §7 Holdout、cutoff 与输入 manifest

- 全部历史输入统一 cutoff `<2024-12-10`：spot、perpetual contract、mark、index、funding、OI、USDT/USD、事件源、保证金阶梯和清算费。
- Holdout 物理封存规范固定引用：`06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v5.md §12`；该文件版本 git commit `5acf2a8aa149f740fc78db78f410841add1a087a`，文件 SHA-256 `a5f5051b9fd4c1365ce08d21a6dd7b3b1213d83148136af968b7eeafa8e3cbfa`。
- 封存使用 AES-256-GCM，格式 `12B nonce || ciphertext || 16B tag`；密钥由执行身份不可读的独立 principal 保管。执行前必须留下 manifest 可读成功、密钥/解密不可用失败的负向权限测试命令、退出码和证据。
- 执行代码拒绝任何路径名含 `HOLDOUT`、`sealed` 的输入。Holdout 对研究执行身份永久不可读；只有 Founder 批准的独立评估身份可一次性解封。
- Holdout 即使未来被独立评估，也只是一轮锁定后的历史稳健性复核，**不耗独立 Alpha 计数、不能救回失败的工作集、不能替代 §9 前向确认**。
- 执行前生成输入 manifest：路径、schema、UTC 起止、行数、缺失率、来源、抓取版本、文件 SHA-256、生成代码 git hash。任一 manifest 后输入变更均视为新版本，须重新盲审。

---

## §8 功效与判读边界

- 历史 8h 序列描述性有效样本量：`n_eff=n/(1+2Σrho_k)`，ACF 截断 30 个 8h lag（10 天）。该数不把被探索污染的历史段升级为独立确认。
- 独立制度周期约 4-5 年，年度样本很少；历史年度正负和显著性仅按冻结门机械报告，不声称充分机制功效。
- v3 不使用 v2 未冻结来源的“年化 5%-12%”外部先验作任何 PASS/FAIL、MDE 或上线判决，也不得执行后补选有利来源。历史身份降级和前向确认的必要性不依赖该数值。
- 不显著点估计必须写“未验证”；负 funding、事件亏损、现金折价和强平不得剔除。

---

## §9 前向 SHADOW 真确认协议

### §9.1 起点、样本与停机

- 起点 `T0`：v3 经独立 Reviewer 书面放行、历史 baseline FEASIBILITY-LOCK PASS、OI 模块去留已经按 §3.3 冻结，且前向数据 manifest/hash 冻结后的**下一个 UTC 月首 `00:00`**。`T0` 前数据一律不得回填。
- shadow 唯一运行版本：baseline 加上“仅当 §3.3 判保留时才启用”的 OI 模块；不得在 shadow 期切换有/无触发器版本。
- “独立月”仅指独立于历史工作集、在 `T0` 后完整采集的 UTC 日历月，不声称月份在统计上相互独立。
- 一个完整月要求 BTC/ETH 所有必要 1H 字段和组合 8h interval 均 `>=99%` 完整、无单次连续缺口超过 8h，且所有缺口原因在结果解盲前留痕；不插值。
- 最少 18 个完整前向月，且组合有效 8h intervals `n>=1620`。最多观察 24 个 UTC 日历月。
- 在第一个达到“18 个完整月且 `n>=1620`”的月末只检验一次；若 24 个月结束仍未达到数据门，直接 SHADOW FAIL。停机只由预定日历和数据完整性决定，不由收益结果决定。
- 期间可做持仓、成交、缺数和风险运维检查，但不得运行确认 p 值、不得以累计收益提前通过或延长观察。

### §9.2 一次性统计确认门

对 `T0` 后组合 8h 全成本净收益：

1. 检验统计量 `T_obs=mean(r_8h)*1095`。
2. `H0:E[R]<=0`，在零边界把序列减去样本均值重心化。
3. 对重心化序列做 90 个 8h interval（30 天）moving-block bootstrap，`B=10000`，`seed=20260614`。
4. `p=(1+#(T_b>=T_obs))/(B+1)`；要求 `T_obs>0` 且单侧 `p<=0.05`。同时报告未重心化 percentile 95% CI。

**SHADOW CONFIRMED 必须同时满足：**

- [ ] 上述前向 net E[R] 显著>0；这同时是对现金零收益基准的超额收益门。
- [ ] 整个 shadow 期 account-level liquidation episodes = 0。
- [ ] 无未解决的 N.A.、外部补资、Holdout 读取、规则变更或执行偏离。

任一不满足即 SHADOW FAIL；不得延长到显著、不得换 seed/块长/alpha、不得把历史 PASS 与前向 FAIL 合并为“部分确认”。重新提出假设必须新版本预登记，并只使用新版本放行后的未来数据。

### §9.3 证据等级与小额真金

SHADOW CONFIRMED 经独立 Reviewer 核对后，只把策略从“历史观察级”提升为“前向确认、可申请小额真金”，不自动进入核心资本。Founder 书面批准后，小额真金 sleeve 上限冻结为：

```text
min(批准日公司可投资 NAV 的 0.5%, 10,000 USDT)
```

真金阶段继续使用同一 venue、1.0 初始杠杆、资本比例、成本和风控，不得升杠杆。任何升额、降级或核心资本上线须另立实盘协议和独立审批；不属于本预登记自动授权范围。

---

## §10 失败后禁止行为

FEASIBILITY-LOCK FAIL 或 SHADOW FAIL 后禁止：改 funding/权重/资本比例/再平衡/OI 阈值/事件窗/seed/块长后在同一数据重测；剔除负 funding 或事件；读取 Holdout“确认”失败；把不显著写成“弱 edge”或“部分成功”；把历史可行性复核冒称独立确认；以 shadow 运行时间代替固定确认门；未经新预登记和独立审批上线或升额。
