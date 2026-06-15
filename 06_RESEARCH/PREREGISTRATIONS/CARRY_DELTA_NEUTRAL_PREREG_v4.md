# Delta 中性 Carry 预登记 v4

**状态：** PREREGISTERED DRAFT v4 — 待独立 Risk Reviewer 盲审；本文不构成自审通过
**起草：** Codex（实现细化，非 thesis owner）｜**日期：** 2026-06-14（Asia/Singapore）
**基线：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v3.md`
**必改依据：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v3.md`
**Protocol v1.4 AI 证据三行：** ①本策略非 LLM 作 alpha 信号，机制=人工经济归纳（杠杆多头需求→正 funding）；知识截止 2025-05，carry 经济链为公开市场常识。②最可能错处：funding 长期转负 / 制度变化（现货 ETF、更多做空工具）使风险溢价消失；短永续腿急涨强平致 delta 暴露。③不以多 agent 共识为证据；本预登记仅作设计冻结。

---

## §0 研究身份与独立性（核心重构不变）

1. **历史工作集（全部输入 `<2024-12-10`）= 锁定可行性复核（FEASIBILITY-LOCK）。** 用途仅为检验“按 v4 完全冻结口径、含全成本与路径级强平账本，历史上 carry 是否仍可行”。设计参数已被历史探索污染，因此历史 PASS 不是独立机制确认、**不耗独立 Alpha 计数、不授权核心资本上线**，最多表述为“历史可行性复核通过”。
2. **真确认 = 前向 SHADOW（paper-trade，未来数据）。** v4 经独立 Reviewer 放行后，按 §9 的固定起点、固定样本量和一次性检验运行；不得回填放行前数据，不得因观察到结果而延长或提前停止。只有前向 net E[R] 显著>0、无强平且跑赢现金零基准，才计入前向确认证据。
3. **证据等级上线 = Founder 治理决定。** 纸面=0；历史复核过=观察级；前向 shadow 过=具备小额真金申请资格；实盘过后才可另议升额。前向 PASS 不自动下单、不自动成为核心资本，也不改变历史段“不耗独立计数”的定性。

盲审副本不得披露待确认的具体收益数值。

---

## §1 机制与策略命题（不变）

- **机制命题（可证伪）：** carry 净收益主要来自 funding 收取，而非 basis 波动、方向价格漂移或再平衡运气。必要条件是 `funding_received > 0`，且 funding 是净收益归因中的最大正贡献项。
- **策略命题：** 按 §2-§6 冻结构造和全成本执行后，净收益通过 §5 全部基础 carry 硬门。
- **非 alpha 声明：** 不以 funding 极端、价格反转或 funding 均值回归择时；正、负 funding 时段均按冻结规则持有。OI 信号只能把双腿同步减至 50%，不能加到 100% 以上。
- **制度依赖：** 逐年和滚动 12 个月报告净 funding；交易所 funding、保证金或合约制度变更按实际生效时点分段，不得结果后挑窗口。

---

## §2 构造、USDT 资本恒等式与保证金账本

### §2.1 Venue、合约、价格源与账户模式

| 项目 | 唯一定义 |
|---|---|
| Venue | Binance |
| 现货 | Binance Spot `BTCUSDT`、`ETHUSDT` |
| 永续 | Binance USDⓈ-M、USDT 本位线性永续 `BTCUSDT`、`ETHUSDT` |
| 账户模式 | 标准 USDT-M **cross margin**；关闭 portfolio margin 和 multi-assets mode；BTC/ETH 短仓共用一个 USDT cross wallet |
| 现货信号/估值 | Binance Spot 1H kline close |
| 现货成交 | Binance Spot 次一根 1H kline open |
| 永续信号/归因 | Binance USD-M 合约 1H kline close；成交用次一根合约 1H kline open |
| 保证金/权威永续 MTM/强平 | Binance USD-M mark price 1H OHLC；mark 不作现货成交价 |
| basis 归因 | 同一 UTC 1H 的 `spot close - perpetual contract close`；不得用 mark 代替经济 basis，mark 与 contract 的差额按 §4.3 单列 |
| funding | Binance 实际 funding rate、实际结算时间、结算时 mark 和结算前短腿数量 |
| OI | Binance USD-M `sumOpenInterestValue`，5M 数据每小时取最后一个有效值；不前填 |
| 维持保证金 | 对应历史时点的 Binance 完整 leverage bracket 表（floor/cap/mmr/cum）和 liquidation clearance fee rate |
| USDT/USD | 仅按 §6.4 生成 USDT 脱锚事件，不进入 USDT 资本、收益或 PnL 换算 |

任一必要价格、funding、OI、历史完整保证金表、清算费或 §6 事件输入缺失且无法从执行前冻结的输入 manifest 取得，相关必要项记 `N.A. ⇒ FEASIBILITY-LOCK FAIL`；不得用当前费率、插值或另一 venue 代替历史值。

### §2.2 唯一计价单位、绝对资本与初始建仓

全程唯一记账单位为 **USDT**。现货价格、现货现金、USDT-M wallet、funding、手续费、滑点、强平损益、basis MTM、净值和所有收益率分子均用 USDT；不再把 `C0` 称作 USD 等值，也不在策略 PnL 中加入 `cash_fx_pnl`。

```text
C0 = 100,000 USDT
C0 = S0 + M0 + B0 + E0

B0 = 10,000 USDT
E0 = 10,000 USDT
paired_capital = 80,000 USDT
```

`C0` 是 sleeve 的绝对初始资本，也是所有小时收益、8h 收益、MDD、log growth 和年化指标的**唯一固定分母**。BTC/ETH 权重冻结为 `w_BTC=0.70`、`w_ETH=0.30`：

```text
pair_budget_i = 80,000 * w_i USDT
pair_budget_BTC = 56,000 USDT
pair_budget_ETH = 24,000 USDT
```

在初始成交小时 open 取现货参考成交价 `S_i,0` 与永续合约参考成交价 `F_i,0`。为使双腿基础资产数量相等、且永续初始保证金等于其名义：

```text
q_i,0 = pair_budget_i / (S_i,0 + F_i,0)
spot_principal_i = q_i,0 * S_i,0
N_i = perp_initial_notional_i = q_i,0 * F_i,0
perp_initial_margin_i = N_i

q_spot_i,0 = +q_i,0
q_perp_i,0 = -q_i,0
```

因此：

```text
spot_principal_i + perp_initial_margin_i = pair_budget_i
q_spot_i,0 + q_perp_i,0 = 0
```

`N_i` 是该品种初始短永续名义及后续 100% 状态的名义基准，不是额外资本项。

**初始资本占用表（开仓成本前）：**

| 资本桶 | 冻结数值/公式 | 是否进入 `C0` | 是否另计为 `N` |
|---|---:|---:|---:|
| BTC 现货本金 | `q_BTC,0*S_BTC,0` | 是 | 否 |
| BTC 永续初始保证金 | `N_BTC=q_BTC,0*F_BTC,0` | 是 | 否；`N_BTC` 即本行 |
| ETH 现货本金 | `q_ETH,0*S_ETH,0` | 是 | 否 |
| ETH 永续初始保证金 | `N_ETH=q_ETH,0*F_ETH,0` | 是 | 否；`N_ETH` 即本行 |
| 闲置缓冲现金 `B0` | `10,000 USDT` | 是 | 否 |
| 事件备用现金 `E0` | `10,000 USDT` | 是 | 否 |
| **合计** | **`100,000 USDT`** | **唯一一次** | **无额外资本** |

所有交易使用未加滑点的 market open 作为参考成交价，滑点按 §4.1 作为独立 USDT 成本科目只扣一次。初始 open 前，`S0` 先作为 `spot_reserved_cash` 持有，故首个 `A_t` 满足
`spot_reserved_cash + M0 + B0 + E0 = C0`；初始买入后该预留现金一对一转成现货市值，开仓费和滑点另从 `B` 扣。初始永续开仓的 fee/slippage 从 futures wallet `M` 扣。`spot_reserved_cash` 只存在于初始开仓前，完成或撤销开仓后必须为零，不是第五个资本桶。

后续现货买卖的本金流入/流出 `B`，其 fee/slippage 也从 `B` 扣；永续交易不交换名义本金，其 realized PnL、fee/slippage 和 funding 只进入 futures wallet。若所需账户余额不足，按 §3.2 的 `execution_fail` 撤销规则处理，不允许 `B` 或 `M` 隐式为负来完成自愿交易。

`B/E → M` 只是在 sleeve 内部转账，不产生 PnL、不改变 `C0`、不得在现金与 wallet 中重复计数。`E` 只用于 §2.4 规定的事件小时保证金补款，不用于普通开仓、恢复或现货购买。

### §2.3 持仓、delta 与每日再平衡

- 初始开仓在每段首个可交易日 `00:00 UTC` 信号后的次一根 1H open 完成；边界和 PnL 归属按 §4.2。
- 共同指数价 `I_i,t` 只用于把基础资产数量差换算为 delta 名义：

```text
delta_drift_i(t) = abs(q_spot_i(t) + q_perp_i(t)) * I_i,t / N_i
```

- 每日 `00:00 UTC` 用刚闭合 1H bar 的 close 检查。若 `delta_drift_i>5%`，在该 close 后开启的下一根 1H bar open **只调整现货腿**到 `q_spot_i=-q_perp_i`；永续腿不动。若 `≤5%` 不交易。该规则修正数量失配，不把 spot/perp basis 当方向 delta。
- 若同一 open 既有 OI 状态切换又有每日再平衡，先执行 §3 的双腿状态切换，并取消该 open 的单独每日再平衡；状态切换后的两腿目标数量已经相等。

### §2.4 Cross-margin 逐 1H 状态机

对品种 `i` 的短永续持仓维护 `q_perp_i<=0`、加权平均 `entry_i`；对账户维护 USDT wallet `W`：

```text
W =
    M0 + internal_transfers_in - internal_transfers_out
    + cumulative_realized_perp_pnl
    + cumulative_funding_received
    - cumulative_futures_fees
    - cumulative_futures_slippage
    - cumulative_liquidation_clearance_fees
```

在任一估值点、mark 向量 `m_i` 下：

```text
UPNL(m) = Σ_i q_perp_i * (m_i - entry_i)
margin_balance(m) = W + UPNL(m)
notional_i(m) = abs(q_perp_i) * m_i
```

对每个品种，用当时完整历史 bracket 表按
`floor <= notional_i(m) < cap` 重新选唯一档位；最后一档上界为 `+∞`：

```text
maintenance_i(m) = max(0, notional_i(m) * mmr_i - cum_i)
maintenance(m) = Σ_i maintenance_i(m)
```

只携带历史 bracket id 而没有 floor/cap/mmr/cum/clearance fee 完整表不合格。

每根 bar 定义为半开区间 `H_t=[t,t+1h)`，open 为 `t`，close 为 `t+1h`。在两个 bar 共用的边界，先完成前一 bar 的 close 风险检查/可能强平，再处理新边界的 funding；若 close 已清算，则 funding 数量为零。其后才允许补款和新 open 交易。唯一处理顺序如下：

1. **边界 funding：** 若实际 funding timestamp 恰为 `t`，先按边界前持仓 `q_perp_i(t-)` 和结算 mark 入账：

   ```text
   funding_received_i,t =
       -q_perp_i(t-) * mark_i,t * funding_rate_i,t
   ```

   正 funding 对短仓为正收入，负 funding 原样为支出。该现金流属于刚结束的小时和刚结束的 8h interval；不得按边界后的新仓数量计算。
2. **funding 后即时风险检查：** 用 `mark_i,t` 及当前完整 bracket 表重算保证金。若 `margin_balance<=maintenance`，在任何补款或自愿交易前立即进入 account-level liquidation。
3. **延迟补款：** 若上根 bar close 产生 `buffer_breach` 且第 2 步未强平，在 `t` 执行预定补款。按当前 mark/bracket 计算：

   ```text
   topup_gap_t = max(0, 3*maintenance_t - margin_balance_t)
   ```

   先从 `B` 转入；仅当 `H_t` 属于 §6 事件窗时，`B` 用尽后可从 `E` 转入。Binance 官方提现暂停导致跨账户转入不可用时，本步转账为零。转账后若 `margin_balance<=maintenance`，立即强平；若仍低于 `3*maintenance` 但高于维持线，继续持仓并保留风险状态。
4. **小时 open 自愿交易：** 执行已由上一 close 排定的 OI、每日再平衡、脱锚退出/恢复或强平后的现货处置。成交参考价是该 bar 对应市场 open；数量、realized PnL、现金本金流和逐腿成本立即入账。永续部分平仓量
   `q_closed=q_old-q_new`，其 realized PnL 唯一为：

   ```text
   realized_perp_pnl = q_closed * (F_open - entry_old)
   ```

   同方向加仓按绝对数量加权更新 `entry`；本协议禁止主动翻转为净多永续。
5. **open 后即时风险检查：** 用该 bar mark open 和交易后数量重算 bracket、保证金及维持线；若 `margin_balance<=maintenance`，立即强平。
6. **小时内最坏点：** 对两个短仓同时使用各自该小时 mark high，形成保守的同步最坏向量 `m_i=mark_high_i,t`，并按该向量的合成名义重新选档。若 `margin_balance<=maintenance`，首次触发 account-level liquidation；不允许等 close 后补款。
7. **小时 close：** 未强平时用 mark close 重算。若
   `maintenance < margin_balance < 3*maintenance`，本小时记一次 `buffer_breach`，排定下一 bar open 补款；若 `margin_balance>=3*maintenance`，清除 breach 状态。若 close 已满足 `margin_balance<=maintenance`，在该 close 立即强平并归属本小时。

`buffer_breach` 与 `liquidation` 是两级互斥终态：前者表示仍高于维持线、只能触发延迟补款；后者表示首次达到或跌破维持线、立即终止全部短永续。每条路径分别报告“至少一次 buffer breach”和“至少一次 account-level liquidation”，不得把 breach 当作 liquidation，也不得用补款后的结果抹去已发生 breach。

Account-level liquidation 时：

- BTC/ETH 所有未平短永续在首次触发检查点一起按该检查点 mark 参考价买回；滑点作为 §4.1 独立成本，不能既改执行价又重复扣 cost。
- 每腿计 regular fee、对应压力档 slippage，并按触发名义所在完整历史 bracket 的 clearance fee rate 计清算费。
- realized PnL、成本与 wallet 在该检查点立即入账；这计为一个 liquidation episode，并记录受影响品种。
- 现货腿保留到下一根 1H open，再全部卖出并计成本；期间方向暴露和现货 PnL 完整入账。此后路径保持 USDT 现金，不再重开。
- 若清算后 `W_raw<0`，令 `bankruptcy_liability=max(0,-W_raw)`、账面 `W=0`，并在 sleeve NAV 中作为外部负债扣除。该操作只是把负 wallet 重分类为负债；损失已经包含在清算 realized PnL 和费用中，不能再记一笔 bankruptcy PnL。后续用现货卖出所得偿还负债只是资产与负债同时减少，不产生第二次 PnL。若 sleeve 原始权益 `<=0`，净值记零并成为吸收态。

ADL 只在 Binance 官方市场/账户执行记录能证明该小时发生时入账：按实际减仓数量和执行价替代普通平仓；缺少执行数量或价格则该事件项 `N.A.⇒FAIL`。提现暂停不改变 MTM，但按 §6.3 阻止暂停期内 `B/E` 跨账户转入；已在 futures wallet 的资金仍可用。

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
- 风险优先顺序：减仓时先用 reduce-only 买回短永续，再卖出匹配现货；恢复时先买入现货，再卖出永续。两腿均用各自次一根 1H open，模拟账本视为同一时间戳；实盘 shadow 要求第二腿在第一腿确认后 60 秒内提交。
- 任一腿不能足额成交、现金不足或风控检查禁止第二腿时，立即按当时可得价反向撤销已成交第一腿，回到切换前状态；所有成交、撤销、fee 和 slippage 均入账，该次状态切换记 `execution_fail`，24h 内不重试。
- 首次成功减仓启动 24h refractory。期间新触发不延长。24h 到期时若当根仍触发，则续 24h；若不再触发，则次一根 1H open 按上述恢复顺序一次性恢复到 100%。
- BTC/ETH 各自独立运行状态机；无论 50% 或 100% 状态，成功切换后均满足 `q_spot+q_perp=0`，减仓本身不得制造方向暴露。

### §3.3 判决去循环

1. **基础 carry FEASIBILITY-LOCK** 只用不含 OI 触发器的 baseline 按 §5.2 判 PASS/FAIL。
2. 只有 baseline PASS，才评估 OI 模块是否保留。非劣检验为同一路径“有触发器−无触发器”，`H0: ΔnetER<=-0.5%/年`，单侧 `alpha=0.05`，同步 1 周块、`B=2000`、`seed=20260614`。
3. 尾部门唯一化：若 baseline 的事件期 liquidation episodes `L0>0`，要求触发器版 `L1<L0`；若 `L0=0`，要求 `L1=0`。同时要求触发器不得增加 account-level liquidation 总次数。
4. 非劣与尾部门均通过才“保留 OI 模块”。任一不通过则 OI 模块 REJECTED，但不得改写 baseline 的独立 PASS/FAIL，也不得在有/无触发器两版中择优包装 edge。

---

## §4 成本、交易小时与无重复损益账本

### §4.1 成本

```text
regular_fee_per_side = 0.10%
baseline_slippage_per_side = 0.10%
event_slippage_per_side = 0.30% / 0.50% / 1.00% 三个压力档

trade_cost =
    abs(reference_price * quantity_filled)
    * (fee_per_side + slippage_per_side)
```

- 现货、永续每一腿分别计费；fee 固定用 0.10%，不根据 VIP、maker/taker 或结果后费率优化。
- 开仓、强制收尾平仓、每日再平衡、OI 减仓/恢复、失败撤销、脱锚退出/恢复、强平和强平后现货处置均逐笔计费。
- 事件窗内对每一笔交易分别重跑 0.30%/0.50%/1.00% 滑点压力档；fee 仍为 0.10%。清算另加历史 liquidation clearance fee，不能用普通手续费替代。
- 参考成交价始终是规则指定的 raw open 或强平 mark；slippage 只作为上式成本扣一次，不再改成交价。
- `financing=0`：全部资金属于 `C0`，无借贷。任何外部借款或补资均为协议违规。

### §4.2 小时边界、权威 NAV 与交易小时 PnL

对每个 UTC 小时边界 `t` 定义检查点 `A_t`：已完成该边界实际 funding 结算及 funding 后即时强平检查，但**尚未**执行该边界的延迟补款和自愿 open 交易。bar `H_t=[t,t+1h)` 的权威净 PnL 为：

```text
spot_value_A_t = Σ_i q_spot_i(t-) * S_i,t
futures_equity_A_t = W_t + Σ_i q_perp_i(t-) * (mark_i,t - entry_i,t)

NAV_A_t_raw =
    spot_value_A_t + futures_equity_A_t
    + spot_reserved_cash_t + B_t + E_t
    - bankruptcy_liability_t

NAV_A_t = max(0, NAV_A_t_raw)
net_pnl_H_t = NAV_A_(t+1h) - NAV_A_t
r_H_t = net_pnl_H_t / C0
```

内部 `B/E/M` 转账在 NAV 中净额为零。open 交易发生在 `A_t` 之后，因此其 fee、slippage、实现损益与随后持仓 PnL全部归属 `H_t`；`t+1h` 边界的 funding 发生在 `A_(t+1h)` 之前，因此归属 `H_t`。若 `t+1h` 同时有 funding 和新交易，funding 用交易前数量并归属 `H_t`，新交易归属下一小时。强平归属首次触发所在 `H_t`；强平后现货在下一 open 的卖出及成本归属下一小时。

每个固定 UTC 8h 观测 interval 定义为：

```text
I_k = [T_k, T_k+8h)
T_k ∈ {每天 00:00, 08:00, 16:00 UTC}

net_pnl_8h,k = Σ_{H_t subset I_k} net_pnl_H_t
r_8h,k = net_pnl_8h,k / C0
```

因此：

- `T_k` 边界 funding 已归属前一 interval；
- `T_k` 的 open 交易归属 `I_k`；
- `T_k+8h` 边界 funding 归属 `I_k`；
- `T_k+8h` 的 open 交易归属下一 interval。

若交易所临时增加、取消或改变 funding 时点，现金流仍按实际 timestamp 归入包含该 timestamp 的小时，并在该小时右边界入账；结算名义使用实际 timestamp 前最后一个已确认仓位。若同一小时既有非整点 funding 又发生无法排序的 intrahour liquidation/ADL，由于 1H 数据不能证明先后，该小时 `N.A.⇒FAIL`。研究观测单位继续固定为上述 UTC 8h interval，不改年化因子，不按结果重分箱。

### §4.3 腿级对账与机制归因

权威总收益只取 §4.2 的 NAV 差。为审计 open 改仓小时，另计算下列严格求和的腿级价格 PnL。令 `q^-` 为 `t` open 交易前数量、`q^+` 为交易后数量。无小时内强平时：

```text
spot_price_pnl_i,H =
    q_spot_i^- * (S_open_i,t - S_close_i,t-1)
    + q_spot_i^+ * (S_close_i,t - S_open_i,t)

perp_ledger_price_pnl_i,H =
    q_perp_i^- * (F_open_i,t - mark_close_i,t-1)
    + q_perp_i^+ * (mark_close_i,t - F_open_i,t)
```

该 `perp_ledger_price_pnl` 必须等于本小时 `realized_perp_pnl + ΔUPNL`（内部转账、funding 和成本剔除后）。不相等超过 `1e-8*C0` 记账即失败，不得用平衡项静默修补。

经济 basis 归因继续使用 spot 与 perpetual contract 价格。令：

```text
paired_qty^- = min(q_spot^-, abs(q_perp^-))
paired_qty^+ = min(q_spot^+, abs(q_perp^+))

basis_pnl_i,H =
    paired_qty^- *
      [(S_open-S_prev_close) - (F_open-F_prev_close)]
    + paired_qty^+ *
      [(S_close-S_open) - (F_close-F_open)]

contract_leg_pnl_i,H =
    q_spot^-*(S_open-S_prev_close)
    + q_spot^+*(S_close-S_open)
    + q_perp^-*(F_open-F_prev_close)
    + q_perp^+*(F_close-F_open)

rebalance_directional_pnl_i,H =
    contract_leg_pnl_i,H - basis_pnl_i,H

mark_contract_adjustment_i,H =
    q_perp^-*(F_prev_close-mark_prev_close)
    + q_perp^+*(mark_close-F_close)
```

于是每小时必须满足：

```text
net_pnl_H =
    Σ_i basis_pnl_i,H
    + Σ_i rebalance_directional_pnl_i,H
    + Σ_i mark_contract_adjustment_i,H
    + funding_received_H
    - spot_fees_H - futures_fees_H
    - spot_slippage_H - futures_slippage_H
    - liquidation_clearance_fees_H
    - ADL_cash_charge_H
```

`ADL_cash_charge_H` 只允许记录官方账单中独立于执行价的额外现金扣款；ADL 执行数量和执行价本身进入 `perp_ledger_price_pnl`，不得再记为 `ADL_cash_charge`。`bankruptcy_liability` 是负 wallet 重分类，不是额外 PnL 科目。

若在 bar open 或 close 强平，仍使用上式对应边界价格。若在小时内 mark high 触发强平/ADL，由于没有同一触发时刻的可审计 spot 与 perpetual contract 成交价，归因唯一改为：

```text
preopen_basis_pnl =
    paired_qty^- *
    [(S_open-S_prev_close) - (F_open-F_prev_close)]

preopen_contract_residual =
    q_spot^-*(S_open-S_prev_close)
    + q_perp^-*(F_open-F_prev_close)
    - preopen_basis_pnl

forced_segment_pnl =
    本小时实际 spot_price_pnl
    + 本小时实际 perp_ledger_price_pnl
    - preopen_basis_pnl
    - preopen_contract_residual
```

`forced_segment_pnl` 是公开列示的强制执行段价格损益，不再拆成 basis 或方向项；不得用插值构造触发时刻 spot 价格。该小时不用常规整小时 basis 公式，唯一归因为：

```text
net_pnl_forced_H =
    preopen_basis_pnl
    + preopen_contract_residual
    + forced_segment_pnl
    + funding_received_H
    - all_fees_H
    - all_slippage_H
    - liquidation_clearance_fees_H
    - ADL_cash_charge_H
```

分段和仍必须与 NAV 差一致。

逐小时强制检查：

```text
abs(
  net_pnl_H_from_NAV
  - net_pnl_H_from_attribution
) <= 1e-8 * C0
```

不满足即 `ACCOUNTING_FAIL ⇒ FEASIBILITY-LOCK FAIL`。basis、腿级 PnL、wallet realized/unrealized、事件损失均是同一权威 PnL 的互斥解释，不得二次加总。

### §4.4 USDT 脱锚的计价边界

策略收益以 USDT 为 numeraire，故 USDT 相对 USD 的涨跌**不进入** `C0`、NAV、funding、basis 或净收益换算；这样避免把全部 USDT 资产重复乘汇率。USDT 脱锚仍属于 venue/结算资产事件风险，必须按 §6.4 生成事件、应用事件滑点、补款限制和事件硬门，并单独报告 `USDTUSD` 最低值及脱锚幅度。报告可附 USD 购买力敏感性，但只能作为非判决附表，不能替换或叠加 USDT 权威 PnL。

---

## §5 历史 FEASIBILITY-LOCK 验收与 1H 路径 bootstrap

### §5.1 主收益推断

- 观测单位：§4.2 固定 UTC 8h interval 的组合全成本净收益。
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
- [ ] 所有必要数据均非 N.A.，逐小时账本对账通过，且无 Holdout/全样本分位/事后改窗违规。

任一不满足即 **FEASIBILITY-LOCK FAIL**。历史 PASS 只允许使用 §0 的限定表述。

### §5.3 2000 条一年路径：精确 1H 合成与保证金重演

**bootstrap 输入不是 8h 收盘收益。** 对每个历史 1H bar `s=[u,u+1h)` 和每个价格序列
`Y ∈ {spot, perpetual_contract, mark, index}`，保存无量纲模板：

```text
gap_Y,s   = open_Y,s / close_Y,s-1
body_Y,s  = close_Y,s / open_Y,s

mark_high_ratio_s = mark_high_s / mark_open_s
mark_low_ratio_s  = mark_low_s / mark_open_s
oi_ratio_s        = OI_close_s / OI_close_s-1
```

同时保存：

```text
X_s = {
  上述 BTC/ETH 同步价格模板,
  funding rate、实际 settlement flag 及 bar 内 timestamp offset,
  OI 缺失标记,
  每个品种该历史小时生效的完整 bracket rows
    [floor, cap, mmr, cum, clearance_fee_rate],
  由真实历史序列预先按 §6 机械生成的 event membership,
  withdrawal / ADL flags,
  USDTUSD 事件监控值,
  data-availability flags
}
```

候选块须满足：

1. 从历史任意 `00:00 UTC` 开始，连续 168 个完整 1H bar；
2. 候选首 bar 的前一小时 close 完整，使 `gap` 可计算；
3. 块内 BTC/ETH 所有必要字段同步完整；跨缺失小时的块不得入池；
4. 完整 bracket 表按实际生效小时存在，不能只有 bracket id；
5. 168h 是固定 UTC 8h interval 的整数倍。

**随机算法冻结：**

```text
PRNG = NumPy Generator(PCG64(seed=20260614))
paths = 2000
draws_per_path = 105
sampling = 对候选块索引有放回均匀抽样
draw_order = path 0 的 105 次、path 1 的 105 次……依次生成
```

每条路径串接 105 个块共 `17,640h`，只取前 `17,520h`。同一块内 BTC/ETH、价格模板、funding、OI、事件、USDTUSD 和制度表始终一起移动，禁止逐列独立抽样。

**固定合成时钟与数值基准：**

```text
synthetic_start = 2001-01-01T00:00:00Z
BTC prior-close base = 100,000 USDT
ETH prior-close base = 4,000 USDT

在 n=-1：
spot = perpetual_contract = mark = index = 对应品种 base
OI = 1.0（无量纲，仅保留相对变化与滚动分位）
```

对路径第 `n` 个合成 bar、其抽中的历史源 bar `s`，逐序列精确递推：

```text
open_Y,n  = close_Y,n-1 * gap_Y,s
close_Y,n = open_Y,n * body_Y,s

mark_high_n = mark_open_n * mark_high_ratio_s
mark_low_n  = mark_open_n * mark_low_ratio_s
OI_n        = OI_n-1 * oi_ratio_s
```

funding rate、结算 flag/timestamp offset、预先生成的事件 membership、withdrawal/ADL flag 和完整 bracket 表直接从源 bar `s` 复制到合成 bar `n`。合成路径使用复制后的 event membership，不在重建价格上重新扫描 §6，避免块边界制造人工事件；真实历史直接重演仍按 §6 从原始序列机械扫描。块边界使用新块首 bar 自身的 `gap/body` 接续上一合成 close；不插值、不重置、不按源绝对价格重估 basis。若递推后 OHLC 关系不满足
`high>=max(open,close)` 或 `low<=min(open,close)`，该源模板不合格并在抽样前剔除；不得执行后修正。

完整 bracket 表随源 bar 移动，但**档位不随源历史名义复制**。在合成路径每个 funding/open/high/close 检查点，按合成持仓数量乘合成 mark 得到 USDT 名义，再用该检查点携带的完整表按 §2.4 的 floor/cap 重新选 `mmr/cum/clearance_fee_rate`。若合成名义不落入任何档、表有重叠/缺口或制度字段缺失，该路径项 `N.A.⇒FAIL`。

路径运行规则：

1. 前 `8,760h` 只作 OI 365 日滚动窗口 warm-up；不计评价收益。
2. 在合成时钟 `2002-01-01T00:00:00Z`、即零基索引 `n=8,760`（自然数第 `8,761` 个 bar）的 open，以新的 `C0=100,000 USDT` 按当时合成 spot/perpetual open 初始化资本和持仓，所有 PnL、breach、refractory 和负债状态归零；合成价格与 OI 历史不断链。
3. 后 `8,760h` 是唯一一年评价期。§5 基础 carry 风险门先在关闭 OI 模块的 baseline 上，逐小时运行 §2.4、§4 和 §6 的完整状态机；funding、补款、交易、强平、费用和 NAV 必须重新产生，不得从 8h 收益、组合 MDD或源历史强平结果推断。
4. 只有 baseline PASS 后，才在完全相同的 2000 条路径及抽样索引上另跑开启 §3 的配对版本。
5. 每条路径分别运行基准滑点及三个事件压力滑点账本。若路径含 §6 事件小时，只替换事件小时内发生交易的滑点；该路径的风险统计取四个账本中的最坏值。
6. account-level liquidation 后按 §2.4 处置现货并保持现金，不得重开；一年 MDD 按 `NAV_A_t/C0` 逐小时计算。

`B=2000`，统一 `seed=20260614`。报告：

- `P(至少一次 buffer_breach)`、每路径 breach 小时数和补款次数；
- `P(至少一次 account-level liquidation)`、各品种受影响概率及首次强平小时；
- `P(一年 MDD>=20%)`、`P(一年 MDD>=35%)` 和年 MDD 分布。

硬门：

```text
P(一年 MDD >= 35%) <= 20%
P(一年 MDD >= 20%) <= 10%
```

两者均按 2000 条路径的最坏压力账本频率计算。任一路径无法重建完整 bracket、funding 边界、补款延迟或首次强平状态，则该分档爆仓项 `N.A.⇒FAIL`。

### §5.4 WF

按历史工作集 8h interval 数时间等分三段，余数依次分给前段。每段在首个可交易 open 用同一 `C0=100,000 USDT` 独立开仓，在段末最后一个 close 强制平仓并计成本；不把持仓或 PnL 跨段传递，不在段内重估参数。这样切点持仓被显式结算而非静默跨界。至少两段净 E[R]>0。

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
perp_depeg_i,h = abs(mark_close_i,h / index_close_i,h - 1)
```

- 连续两个完整 1H bar 均 `perp_depeg>2%` 才生成事件。
- 起点是该连续 run 的第一个 bar open。
- 起点后首次出现连续六个完整 1H bar 均 `perp_depeg<=0.5%`，事件终点为第六个 bar 的 close；若直到工作集末仍未恢复，终点取工作集 cutoff。
- 相邻事件间隔 `<=6h` 时合并为一个事件。
- mark/index 任一缺失会中断连续计数；若缺失发生在已触发事件内，事件建模 `N.A.⇒FAIL`，不得用插值缩短窗口。
- 第二个确认 bar close 后，次一根 1H open 将该品种双腿降到 0：先买回短永续，再卖出现货；事件期间保持现金。事件终点后再等待 24h，在下一个 `00:00 UTC` 检查点后的 1H open 恢复。baseline 恢复到 100%；开启 OI 模块的配对版本按当时 OI 信号恢复到 50% 或 100%。退出、等待和恢复全部计逐腿成本，脱锚风险规则优先于每日再平衡和 OI 状态切换。

### §6.3 Binance 提现暂停规则

- 只扫描 Binance 官方 announcement archive 及执行前冻结的 BTC、ETH、USDT withdrawal-status 小时快照。
- 仅当官方记录明确显示 BTC、ETH 或 USDT 提现不可用并持续至少两个完整 1H bar，才生成事件。
- 起点取官方生效时间；无生效时间时取公告发布时间向下取整到小时。终点取官方恢复生效时间；无明确时间时取状态快照连续两个小时恢复可用后的第二个小时 close。
- 公告与状态冲突时取更早起点、更晚终点；缺少终点证据则持续到工作集 cutoff。
- 事件期间不允许 `B/E` 向 futures wallet 新转入；已在 futures wallet 的保证金照常使用。该限制在逐 1H 状态机和 bootstrap 中一致执行。

### §6.4 USDT 脱锚规则

USDT/USD 只用于事件识别。逐 1H 计算两个 Binance index 交叉价：

```text
u_BTC,h = BTCUSD_COINM_index_close_h / BTCUSDT_USDM_index_close_h
u_ETH,h = ETHUSD_COINM_index_close_h / ETHUSDT_USDM_index_close_h
USDTUSD_h = median(u_BTC,h, u_ETH,h)
usdt_depeg_h = abs(USDTUSD_h - 1)
```

两个交叉价都必须存在；不得假定 `USDTUSD=1` 或结果后换用另一稳定币。事件生成规则：

- 连续两个完整 1H bar 均 `usdt_depeg>1%` 时触发，起点为该 run 第一个 bar open；
- 触发后首次连续六个完整 1H bar 均 `usdt_depeg<=0.5%`，终点为第六个 bar close；
- 相邻事件间隔 `<=6h` 合并；工作集末未恢复则终点取 cutoff；
- 已触发事件内任一交叉价缺失则 `N.A.⇒FAIL`。

USDT 脱锚事件不主动平掉双腿，因为两腿及保证金均以 USDT 结算；但该窗口适用事件滑点压力、`E` 补款资格和 §6.5 事件硬门，并单列 USDT 相对 USD 的购买力变化。不得把该购买力变化再次加入 USDT PnL。

### §6.5 新事件纳入算法与硬门

固定命名事件之外，**只能**由 §6.2、§6.3 或 §6.4 的全工作集机械扫描生成事件；禁止凭新闻记忆新增名称、事后移动边界或删除亏损事件。执行前输出按 `(start_utc, end_utc, rule_id, symbol)` 排序的事件 manifest 及 SHA-256；同一规则、同一输入必须生成同一清单。重叠窗口取并集，不能裁短。

每个固定或规则生成事件均按真实 1H 路径直接重演 §2.4 账本，并分别报告 0.10%/0.30%/0.50%/1.00% 滑点。任一压力档发生 account-level liquidation，或事件窗口至恢复后 24h 的 sleeve MDD>15%，则 §5 的事件硬门 FAIL。

---

## §7 Holdout、cutoff 与输入 manifest

- 全部历史输入统一 cutoff `<2024-12-10`：spot、perpetual contract、mark、index、funding、OI、USDTUSD 事件源、事件公告/状态、完整保证金阶梯和清算费。
- Holdout 物理封存规范固定引用：`06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v5.md §12`；该文件版本 git commit `5acf2a8aa149f740fc78db78f410841add1a087a`，文件 SHA-256 `a5f5051b9fd4c1365ce08d21a6dd7b3b1213d83148136af968b7eeafa8e3cbfa`。
- 封存使用 AES-256-GCM，格式 `12B nonce || ciphertext || 16B tag`；密钥由执行身份不可读的独立 principal 保管。执行前必须留下 manifest 可读成功、密钥/解密不可用失败的负向权限测试命令、退出码和证据。
- 执行代码拒绝任何路径名含 `HOLDOUT`、`sealed` 的输入。Holdout 对研究执行身份永久不可读；只有 Founder 批准的独立评估身份可一次性解封。
- Holdout 即使未来被独立评估，也只是一轮锁定后的历史稳健性复核，**不耗独立 Alpha 计数、不能救回失败的工作集、不能替代 §9 前向确认**。
- 执行前生成输入 manifest：路径、schema、UTC 起止、行数、缺失率、来源、抓取版本、文件 SHA-256、生成代码 git hash。任一 manifest 后输入变更均视为新版本，须重新盲审。

---

## §8 功效与判读边界

- 历史 8h 序列描述性有效样本量：`n_eff=n/(1+2Σrho_k)`，ACF 截断 30 个 8h lag（10 天）。该数不把被探索污染的历史段升级为独立确认。
- 独立制度周期约 4-5 年，年度样本很少；历史年度正负和显著性仅按冻结门机械报告，不声称充分机制功效。
- v4 不使用 v2 未冻结来源的“年化 5%-12%”外部先验作任何 PASS/FAIL、MDE 或上线判决，也不得执行后补选有利来源。历史身份降级和前向确认的必要性不依赖该数值。
- 不显著点估计必须写“未验证”；负 funding、事件亏损、清算、ADL、USDT 脱锚事件和强平不得剔除。

---

## §9 前向 SHADOW 真确认协议

### §9.1 起点、样本与停机

- 起点 `T0`：v4 经独立 Reviewer 书面放行、历史 baseline FEASIBILITY-LOCK PASS、OI 模块去留已经按 §3.3 冻结，且前向数据 manifest/hash 冻结后的**下一个 UTC 月首 `00:00`**。`T0` 前数据一律不得回填。
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
- [ ] 无未解决的 N.A.、外部补资、Holdout 读取、规则变更、账本不平或执行偏离。

任一不满足即 SHADOW FAIL；不得延长到显著、不得换 seed/块长/alpha、不得把历史 PASS 与前向 FAIL 合并为“部分确认”。重新提出假设必须新版本预登记，并只使用新版本放行后的未来数据。

### §9.3 证据等级与小额真金

SHADOW CONFIRMED 经独立 Reviewer 核对后，只把策略从“历史观察级”提升为“前向确认、可申请小额真金”，不自动进入核心资本。Founder 书面批准后，小额真金 sleeve 上限冻结为：

```text
min(批准日公司可投资 NAV 的 0.5%, 10,000 USDT)
```

真金阶段继续使用同一 venue、1.0 初始杠杆、资本比例、USDT 计价、成本和风控，不得升杠杆。任何升额、降级或核心资本上线须另立实盘协议和独立审批；不属于本预登记自动授权范围。

---

## §10 失败后禁止行为

FEASIBILITY-LOCK FAIL 或 SHADOW FAIL 后禁止：改 funding/权重/资本比例/再平衡/OI 阈值/事件窗/seed/块长后在同一数据重测；剔除负 funding 或事件；读取 Holdout“确认”失败；把不显著写成“弱 edge”或“部分成功”；把历史可行性复核冒称独立确认；以 shadow 运行时间代替固定确认门；未经新预登记和独立审批上线或升额。
