# Delta 中性 Carry 预登记 v4 第四轮独立风险审查

**任务号：** CARRY-RR4  
**审查者：** Codex（独立 Risk Reviewer，与 v4 起草者分离）  
**审查日期：** 2026-06-15（Asia/Singapore）  
**审查对象：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md`  
**对照：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v3.md`  
**结论：** **APPROVED**  
**v3 剩余条件闭合：** **3/3**

## 审查边界

- 仅审查预登记设计、公式和执行唯一性；未运行回测、收益计算、bootstrap、事件研究或参数搜索。
- 未读取 HOLDOUT、`01_MEMORY_CORE/`、sealed 内容或 carry 实证结果。
- 未修改 `CARRY_DELTA_NEUTRAL_PREREG_v4.md`。
- 裁决标尺仅为“能否放行历史 FEASIBILITY-LOCK 可行性复核”，不把历史段升级为独立确认。

## 逐条裁决

| # | 审查项 | 裁决 | 证据（v4 §/行） | 裁决理由 |
|---:|---|---|---|---|
| 1 | 资本 / USDT 计价账 | **CLOSED** | §2.1 L34-L50；§2.2 L52-L111；§4.2 L251-L288；§4.4 L394-L396；§6.4 L570-L588 | 全程唯一以 USDT 记账；`C0=100,000 USDT`，且 `C0=S0+M0+B0+E0`。80,000 配对资本与两个 10,000 现金桶只计一次，`N_i` 明确不是额外资本。现货本金流、futures wallet、内部转账、费用和滑点的落账桶已冻结。小时、8h、MDD、log growth 和年化指标均以同一个固定 `C0` 为分母。USDT/USD 只生成脱锚事件及非判决购买力附表，不进入或重复叠加权威 USDT PnL。 |
| 2 | 1H 合成强平路径 | **CLOSED** | §2.4 L125-L198；§5.3 L426-L526 | 账户级 cross-margin 状态机逐 1H 处理 funding、维持保证金、延迟补款、open 后检查、同步 mark-high 最坏点、close 检查和首次强平。`buffer_breach` 与 `liquidation` 两级定义及报告口径分离。2000 条路径、`PCG64(seed=20260614)`、抽样顺序、固定价格基准、gap/body/OHLC 递推和块边界接续均冻结。完整历史 bracket rows 随源小时移动，并按每个合成检查点的合成名义重选 `mmr/cum/clearance_fee_rate`；无法重建即 `N.A.⇒FAIL`。 |
| 3 | 交易小时 PnL 计账 | **CLOSED** | §2.4 L157-L195；§4.2 L251-L288；§4.3 L290-L392 | 权威总 PnL 唯一采用相邻 `A_t` 的 NAV 差。open 交易、funding、强平和强平后现货处置分别归属明确小时；8h interval 为固定 UTC 00/08/16 边界，小时 PnL 严格求和。交易小时按 pre-open/post-open 数量拆分价格 PnL，永续腿必须与 `realized_perp_pnl + ΔUPNL` 对账。常规及强平小时归因均须与 NAV 差在 `1e-8*C0` 内一致，否则 `ACCOUNTING_FAIL`，从而禁止漏计、重复计或平衡项修补。 |

## 核心重构与新自由度

**核心重构完整，未发现新的阻塞性自由度。**

- 历史工作集仍只是 FEASIBILITY-LOCK；历史 PASS 不耗独立 Alpha 计数、不构成独立机制确认、不授权核心资本上线（§0 L11-L15）。
- 真正确认仍只能使用 Reviewer 放行后的未来 SHADOW 数据；固定起点、样本量、一次性检验和停机规则禁止回填与 optional stopping（§9.1 L620-L628；§9.2 L630-L645）。
- SHADOW CONFIRMED 只产生“小额真金申请资格”，不会自动下单或进入核心资本；升额和核心资本上线须另立协议和审批（§9.3 L647-L655）。
- Holdout 即使未来由独立身份评估，也不耗独立计数、不能救回失败工作集、不能替代前向确认（§7 L598-L605）。
- 资本计价、小时 PnL、合成路径、随机数、bracket 选择和失败处理均已冻结；未发现可由执行者结果后选择且足以改变历史 FEASIBILITY-LOCK 判决的新参数或账本分支。

## 最小必改

**无。** 就本轮“历史可行性复核可复现性”标尺，v3 遗留三项均已闭合。

执行阶段仍必须机械落实文中已有硬门：必要输入或完整历史制度表缺失即 `N.A.⇒FAIL`；逐小时 NAV 与归因不平即 `ACCOUNTING_FAIL`；不得以实现便利修改 seed、块长、成本、事件窗、计价单位或强平顺序。这些是已冻结的执行条件，不是新的预登记修改要求。

## 最终结论

**APPROVED。** 允许按 v4 冻结规格开展历史 FEASIBILITY-LOCK 可行性复核。

本批准不允许读取 Holdout，不消耗独立 Alpha 计数，不构成策略机制的独立确认，不授权自动下单、小额真金或核心资本上线。后续证据升级仍须满足 §9 前向 SHADOW 协议及独立治理审批。

**审查员签字：** Codex / Independent Risk Reviewer / 2026-06-15
