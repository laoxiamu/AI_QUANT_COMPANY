# Delta 中性 Carry 预登记 v3 第三轮独立风险审查

**任务号：** CARRY-RR3
**审查者：** Codex（独立 Risk Reviewer，与 v3 起草上下文分离）
**审查日期：** 2026-06-14（Asia/Singapore）
**审查对象：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v3.md`
**对照：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v2.md`
**结论：** **NOT APPROVED**
**RR2 剩余条件完全闭合：** **4/6**

## 关键发现

1. **资本恒等式的结构已修复，但 USD/USDT 计价不自洽，绝对 `C0` 仍未冻结。** v3 把 `C0` 定义为 USD 等值，却直接用 USDT 报价计算 `q_i`、`S0`、`M0` 和 `C_t`，未乘当时 `USDTUSD`。当 USDT 不等于 1 USD 时，所列 USD 恒等式不成立。绝对 `C0` 未指定也使历史 leverage bracket、`cum` 和 liquidation fee 档位无法唯一选择。
2. **逐 1H 强平重演框架已经建立，但合成路径仍不能唯一复原。** “固定基准”和 open/close/OHLC 相对量没有数值及精确递推方程；重采样后的合成名义如何映射到采样小时的完整历史 bracket schedule 也未冻结。不同实现会产生不同 mark high、维持保证金和首次强平时点。
3. **v3 新增的权威 PnL 恒等式在交易发生小时会漏计或错计。** §4.2 用单一 `q_(h-1) * (close_h-close_(h-1))`，但 OI、再平衡、脱锚退出和恢复均在小时 open 改变数量。该公式未拆分“前收盘至本 open 的旧仓 PnL”和“本 open 至本收盘的新仓 PnL”，也未说明成交实现损益与 futures wallet 账本如何对账。

以上均会直接改变净 E[R]、MDD 或 liquidation，属于历史可行性复核本身的可复现性阻塞，不是要求历史段达到独立确认级。

## 审查边界

- 仅做预登记设计、公式和执行唯一性审查；未运行回测、收益计算、bootstrap、事件研究或参数搜索。
- 未读取 HOLDOUT、`01_MEMORY_CORE/`、sealed 内容或 carry 实证结果。
- 未修改 `CARRY_DELTA_NEUTRAL_PREREG_v3.md`。
- 裁决标尺是“能否放行历史 FEASIBILITY-LOCK 复核”，不要求历史段达到独立确认级。

## RR2 剩余六项闭合裁决

| # | RR2 剩余项 | 裁决 | 证据（v3 §/行） | 仍缺 |
|---:|---|---|---|---|
| 1 | 资本 / `N` 恒等式 | **PARTIAL** | §2.2 L53-L113；§4.2 L226-L250 | `C0=S0+M0+B0+E0`、80/10/10 分配、等数量双腿、固定收益率分母和资本占用表均已写明，且 `N` 不再重复计作资本。但 `C0` 被定义为 USD 等值（L53），仓位公式却直接除以 USDT 报价（L78-L85），`C_t` 也直接相加 USDT 资产（L104-L112）；初始及逐时 `USDTUSD` 换算未进入恒等式。另未冻结绝对 `C0`，无法唯一确定名义对应的历史保证金档。 |
| 2 | OI 双腿减仓 | **CLOSED** | §3.2 L172-L178；§3.3 L180-L185 | 减仓和恢复均把现货、短永续目标数量配平；减仓先 reduce-only 回补永续再卖现货，恢复顺序相反；次一根 1H open、60 秒 shadow 提交约束、部分成交撤销、24h refractory 和 baseline/OI 判决顺序均唯一。未发现减仓制造净方向暴露的残留规则。 |
| 3 | 逐 1H 强平路径 bootstrap | **PARTIAL** | §2.4 L127-L156；§5.3 L280-L316 | 已明确以同步 1H 完整状态向量生成 2000 条路径，在一年评价期逐小时重跑 cross-wallet、funding、补款延迟、维持保证金、事件和首次强平，而非从 8H 收益或组合 MDD 推断。仍缺：固定价格基准的数值/来源；open、close、high、low 相对量的精确递推式；合成名义按哪套完整历史 bracket schedule 重新选档。绝对 `C0` 未冻结进一步使 bracket/clearance fee 不唯一。 |
| 4 | 事件清单 | **CLOSED** | §6.1 L324-L335；§6.2-§6.4 L337-L363 | 四个命名事件均有 venue/资产及半开 UTC 精确起止。新事件只能由永续脱锚或 Binance 提现暂停规则机械扫描生成；触发、恢复、缺数、合并、冲突和 manifest SHA 均冻结，禁止凭新闻记忆增删或移动边界。 |
| 5 | 前向 shadow 确认门 | **CLOSED** | §9.1 L387-L397；§9.2 L399-L414；§9.3 L416-L424 | `T0`、不得回填、最少 18 个完整月、`n>=1620`、最长 24 月、一次性检验、30 日块、`B=10000`、`seed=20260614`、单侧 `alpha=0.05`、零强平和失败停机均可执行。通过只解锁“小额真金申请资格”，上限为 NAV 0.5% 与 10,000 USDT 较小者，不自动下单或进入核心资本。 |
| 6 | 其余 RR2 执行歧义 | **CLOSED** | 页首 L3-L7；§2.1 L32-L49；§2.3 L115-L125；§4.1 L191-L205 | 日期和 AI 证据三行完整；venue、现货、USDT-M 合约、账户模式、现货/永续/mark/basis/funding/OI 来源均唯一；日再平衡只调现货腿且与 OI 同时发生时有优先级；手续费、基准滑点和事件 0.3/0.5/1.0% 压力档逐腿逐成交冻结。新发现的 PnL 交易时点缺陷另列下节，不否定本项所指定字段已经闭合。 |

## 新缺陷与新自由度

### 1. USD/USDT 单位混用会破坏资本恒等式

§2.2 L53 把 `C0` 定义为 USD 等值，L102 又规定资本桶实际持有 USDT。若初始 `u_0=USDTUSD_0`，单位一致的建仓数量至少应包含 `u_0`：

```text
q_i,0 = pair_budget_i_USD / ((S_i,0 + F_i,0) * u_0)
```

或者全文统一以 USDT 为资本记账单位，另设 USD 报告净值。当前 §2.2 L81、L107-L112 和 §4.2 L226-L250 没有冻结哪一种做法，也没有说明 `cash_fx_pnl` 是仅作用于闲置现金，还是作用于全部 USDT 计价的现货市值、futures wallet、funding、费用和已实现损益。该缺口会导致 FX 漏计或重复计入。

### 2. 交易小时的 PnL 与 wallet 对账不唯一

§2.4 L148 规定在小时 open 交易，§3.2 和 §6.2 会在 open 改变持仓；但 §4.2 L212-L214 对整小时只使用一个数量。至少需要冻结以下等价账本之一：

```text
price_pnl_h =
    q_preopen_h * (open_h - close_h-1)
    + q_postopen_h * (close_h - open_h)
```

并单列成交实现损益、fee、slippage；或直接以逐时 NAV 差作为权威总 PnL，再把归因项约束为严格求和一致。现有公式不能保证与 `wallet_balance + unrealized_perp_pnl` 对账。

### 3. 合成 1H 路径存在实现选择

§5.3 L282-L307 已选对重采样层级，但“固定基准连续复原”仍允许执行者自行选择基准价格、open gap 定义、high/low 相对 open 或前 close 的定义，以及块边界后的第一根 open。bracket 字段只列 `id`，未明确携带当时完整 `notional floor/cap, mmr, cum, clearance fee` 表并按合成名义重新选档。上述选择会改变强平首达事件。

## 核心重构完整性

核心重构**未被稀释**：

- 历史段仍明确只是 FEASIBILITY-LOCK，可行性 PASS 不耗独立 Alpha 计数、不授权核心资本上线（§0 L13）。
- 真确认仍限定为放行后的未来 shadow 数据，禁止回填和按收益 optional stopping（§0 L14；§9.1 L391-L397）。
- 前向 PASS 只形成小额真金申请资格，不自动下单、不自动成为核心资本；升额和核心上线须另立协议审批（§0 L15；§9.3 L418-L424）。
- Holdout 未来即使由独立身份评估，也不耗计数、不能救回失败工作集、不能替代前向确认（§7 L367-L374）。
- 失败后禁止把历史或 shadow 失败包装为弱 edge/部分成功（§10 L428-L430）。

因此本轮否决只针对执行与账本唯一性，不否定 v3 的研究身份重构。

## 最小必改

1. **统一资本计价并冻结绝对规模。** 明确 `C0` 的唯一记账币种和绝对数值；若以 USD 记账，在 `q_i`、资本占用、`C_t` 和所有 USDT 现金流中显式使用 `USDTUSD`，并规定 FX 只计一次。冻结 spot/futures 开仓 fee 与 slippage 从哪个资本桶扣除。由合成名义按完整历史 bracket 表选择 `mmr/cum/clearance fee`。
2. **修正交易小时权威 PnL。** 用 pre-open/post-open 数量和实际 open 成交价拆分价格损益，或改用逐时 NAV 差作权威总 PnL；明确 realized/unrealized、funding、fee、slippage 与 futures wallet 的逐项对账，保证 OI、再平衡、事件退出/恢复小时无漏计和重复。
3. **冻结 1H 合成路径递推。** 给出固定价格基准、各 return/OHLC 相对量定义、块边界第一根 bar 的递推方程，以及完整历史 bracket schedule 随块移动并按合成名义选档的算法。完成后再做文档盲审；本轮仍不得运行历史复核或读取 Holdout。

## 最终结论

**NOT APPROVED。** RR2 剩余六项中 **4/6 CLOSED**。在上述三项最小必改闭合前，不得放行历史 FEASIBILITY-LOCK 复核。即使后续放行，历史结果仍不耗独立 Alpha 计数、不授权自动下单或核心资本上线。

**审查员签字：** Codex / Independent Risk Reviewer / 2026-06-14
