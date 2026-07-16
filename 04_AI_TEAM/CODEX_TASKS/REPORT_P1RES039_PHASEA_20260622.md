# REPORT_P1RES039_PHASEA_20260622

**任务**：P1-RES-039-B1-PHASEA｜解锁数据审计 + 机制红队反审  
**Codex 执行时间**：2026-06-22 UTC  
**纪律声明**：未回测；未碰 Holdout；未调参；未耗独立计数；只读 `06_RESEARCH/DATA/FUTURES_EXPANDED/`；产出写入 `06_RESEARCH/CODE/output/` 与本报告。

## [专业异议] 总裁决

**建议：不应直接进 B1。** 应先补一个可复现的历史解锁事件源，或补 post-2024-12-09 价格面板并只研究当前/未来解锁。理由：

1. B0 对“解锁日历免费且不截断”的表述过强。Tokenomist/TokenUnlocks 的公开网页能看当前/未来表格，API/CSV 才能稳定拿事件级历史数据；Tokenomist 文档显示 API 需要 `x-api-key`，CSV 导出是 Pro 功能，Free trial/Standard 的 Unlock Events 历史回溯为 1 年。按 2026-06-22 倒推，免费/Standard 历史窗约从 2025-06-22 起，**晚于本地价格面板止点 2024-12-09**。
2. 免费网页文章能证明 2024 年历史解锁事件存在，且 AVAX 2024-08-20 与本地价格面板重叠；但这是**人工文章样本**，不是可复现全量事件普查。可识别本地重叠 episode 当前只有 1 个，远低于 100，不能分档单调、不能 60/20/20。
3. 机制上“解锁日期机械”不等于“卖压机械”。VC/团队拿到可转让代币后仍可择时、OTC、对冲或延迟出售；该 payer 硬度强于上币/宏观，但弱于强平这类即时强制流。

**建议落点**：P1 不 KILL，但 **B1 暂停**。下一步二选一：  
① 先补/购买可审计历史 unlock event 数据，且能覆盖 2020-2024 本地 35 资产；或  
② 放弃旧面板，补 2025-06-22 之后 4H 价格面板，研究 Tokenomist 免费/试用可覆盖的近端解锁。若不补数据，不能冻结“代币解锁向下”进入 B1。

## A. 机制红队反审 B0 卡

### A1. payer 硬度排序

**裁决：ACCEPT-with-MODIFY。**

排序大体成立：解锁 > 脱锚 > 上币 > 宏观。解锁确实有硬约束成分：锁仓期、vesting schedule、allocation、cliff date 都是外生日历，不是价格形态筛出来的信号。

修改点：解锁只能称为 **forced availability / scheduled supply**，不能直接称为 **forced sell**。解锁释放的是可转让性，真实卖压取决于接收方现金需求、OTC 安排、对冲、做市承接、归属对象、项目沟通和市场 regime。因此它比宏观/上币硬，但不是强平式机械 payer。B1 必须按 allocation 分组，至少区分 `privateInvestors / founderTeam / publicInvestors / community / reserve`。

### A2. 反“已 price-in”门

**裁决：ACCEPT，且这是最大死亡门。**

我的先验：解锁后仍存在可交易残余漂移的概率偏低，约 25%-35%；大部分可预期影响更可能在事件前或公告/日历传播后完成。公开日历下，真正可能留下残余的情况是：规模特别大、承接薄、团队/投资者 allocation 高、事件前未充分对冲、或实际 claim/transfer 比白皮书 schedule 更突然。

B1 若继续，必须把事件前漂移作为主检验之一：`[-7d,0]` 与 `[0,+1d/+3d/+7d]` 分开报；若前窗已吸收大部分方向性漂移，事件后不可交易，直接 KILL。

### A3. 成本门 80/120/220bp

**裁决：ACCEPT-with-MODIFY。**

小时到日级持仓确实比分钟级 OFI 更可能覆盖成本，因为单次事件毛波动可达数百 bp；但这只改善“幅度空间”，不自动改善“可捕获方向 edge”。解锁事件如果跨 24h/72h/168h，分别暴露约 3/9/21 个 8h funding 结算。按 DEC-089/090，收益必须拆成 ex-funding 与 funding 两账，不能把做空期间收到/支付的 funding 当 alpha。

事件类滑点压力 0.3/0.5/1.0% + 费 0.1%/边对应往返 80/120/220bp 是正确硬门。若方向中位 edge 只有几十 bp，即使绝对波动很大，也与 P0/OI 重置同类死亡。

### A4. 诚实基线

**裁决：ACCEPT-with-MODIFY。**

最可能死亡顺序：

| 死亡门 | 先验死亡概率 | 说明 |
|---|---:|---|
| 免费历史事件数据 × 本地价格重叠 | 70% | 当前已触发主要红旗：免费 API/CSV 历史窗不覆盖本地面板，文章样本不可普查。 |
| 已 price-in / 前窗吸收 | 65% | 公开日历事件，半强式有效下后窗 edge 难留。 |
| 成本门 | 55% | 绝对波动可能过门，但方向 edge 未必过门。 |
| 分档单调性 | 50% | 规模大可能也代表市场早已关注、对冲更充分，单调性不稳。 |
| 全机制阶段 A 失败 | 80% | 数据门 + price-in 双重内生风险。 |

## B. 解锁数据可得性审计

### B1. 本地价格面板覆盖

脚本：`06_RESEARCH/CODE/p1res039_phasea_unlock_audit.py`  
JSON：`06_RESEARCH/CODE/output/p1res039_phasea_unlock_audit_20260622.json`

本地 `FUTURES_EXPANDED` 审计结果：

| 项 | 结果 |
|---|---:|
| 资产数 | 35 |
| 频率 | 4H |
| 字段 | `datetime, open, high, low, close, volume` |
| 最早资产起点 | 2020-01-15 08:00:00 |
| 最晚资产起点 | 2020-11-20 04:00:00 |
| 全资产共同止点 | 2024-12-09 20:00:00 |
| 每资产行数 | 8,885 - 10,738 |

结论：本地价格腿真实存在，但**不能覆盖 2024-12-09 之后事件**。

### B2. 解锁日历源 schema / 免费边界

**Tokenomist / TokenUnlocks**

- 主站公开展示 Token Unlocks Dashboard、upcoming unlock、released percentage、next 7D emission 等字段。
- API 文档显示 `GET /v5/unlock/events/{tokenId}`，需要 `x-api-key`；schema 包含 `unlockDate, tokenName, tokenSymbol, dataSource, cliffAmount, cliffValue, valueToMarketCap, allocationBreakdown, standardAllocationName, referencePrice, unlockPrecision, committedClaim, latestUpdateDate`。
- `GET /v5/unlock/events/upcoming` schema 另含 `marketCap, releasedPercentage, upcomingEvent`。
- API plan 边界：Free trial 的 Unlock Events 回溯 1 年；Standard 1 年历史 + 2 年未来；Elite 2 年历史 + 3 年未来；Enterprise 可定制。按当前 2026-06-22，Free trial/Standard 历史窗从约 2025-06-22 起，**无本地价格面板重叠**；Elite 才可能覆盖 2024-06-22 至 2024-12-09 的一段，但这是付费/API 范围。
- CSV Download 文档显示 CSV export 是 Pro 功能；`All Release Events (each token)` 对 Free 为不可用。

**DefiLlama Unlocks**

- 页面可见 Unlocks/Calendar、Token Unlocks、Prev. Unlock Analysis、7d Post Unlock、Daily Unlocks、Next Event 等栏目。
- 本次没有找到可审计、无需认证的官方 unlock event API schema；页面渲染结果对本任务不足以复现历史事件普查。

**链上归属合约**

- 免费且原则上可审计，但不具备统一 schema。每个项目 vesting 合约、multisig、claim 合约与 tokenomics schedule 差异很大；要从链上还原 35 资产历史 cliff unlock，是单独数据工程任务，不适合作为 B1 快速普查输入。

### B3. 免费历史样本与价格重叠

可审计免费历史样本：BeInCrypto 2024-07-31 文章引用 TokenUnlocks，列出 2024-08 大额解锁：

| Token | 日期 | 规模 | 流通占比 | 本地价格面板 |
|---|---:|---:|---:|---|
| AVAX | 2024-08-20 | 9.54M AVAX / $251.33M | 2.42% | 有，重叠 |
| W | 2024-08-03 | 600M W / $151.67M | 33.33% | 无 |
| APT | 2024-08-12 | 11.31M APT / $76.45M | 2.41% | 无 |
| SAND | 2024-08-14 | 205.59M SAND / $66.75M | 9.00% | 无 |
| ARB | 2024-08-16 | 92.65M ARB / $65.17M | 2.77% | 无 |

这证明“2024 历史解锁事件与本地价格面板可以有重叠”并非逻辑不可能；但当前免费可得形式是文章样本，不是全量事件库，不能支撑普查。

### B4. 描述统计：唯一重叠样本 AVAX

事件时间：公开文章只给日期，脚本按 `2024-08-20T00:00:00Z` 对齐最近 4H bar。该精度不足以做正式事件研究。

| 窗口 | 事件前 long 漂移 | 事件后 long 漂移 | 事件后 short 漂移 | 事件后绝对毛漂移 | 成本门比较 |
|---:|---:|---:|---:|---:|---|
| +24h / 6 根 | +434.82 bp | +634.24 bp | -634.24 bp | 634.24 bp | 绝对毛漂移 > 220bp，但向下先验方向亏损 |
| +72h / 18 根 | +670.91 bp | +2139.97 bp | -2139.97 bp | 2139.97 bp | 绝对毛漂移 > 220bp，但向下先验方向亏损 |
| +168h / 42 根 | +460.37 bp | +2062.41 bp | -2062.41 bp | 2062.41 bp | 绝对毛漂移 > 220bp，但向下先验方向亏损 |

解释：这是单一样本，不能作方向结论；但它足以提醒：**绝对波动过成本门不等于供给冲击向下 edge**。这个样本反而显示事件后上涨，若冻结“解锁=做空”会亏损。必须等全量事件库做分档单调和前/后窗拆分。

### B5. episode 规则裁决

| 项 | 当前结果 |
|---|---:|
| 可识别免费样本事件数 | 5 |
| 本地价格重叠事件数 | 1 |
| episode ≥100 | 否 |
| episode ≥300，可 60/20/20 | 否 |
| 可做分档单调性 | 否 |
| 可冻结方向 | 否 |

事件普查结论：**当前免费/本地组合不能进入 B1**。若 Claude 决定继续，必须先新增事件数据输入，而不是用文章样本补丁继续。

## 文献与来源核实

已核实真实可审计来源：

1. Tokenomist API / 方法文档：真实存在，提供 unlock events schema、cliff/linear 定义、API key 与历史回溯边界。  
   - https://docs.tokenomist.ai/api-documents/introduction  
   - https://docs.tokenomist.ai/api-documents/unlock-events/v5  
   - https://docs.tokenomist.ai/api-documents/upcoming-unlock-events/v5  
   - https://docs.tokenomist.ai/methodology/cliff-and-linear-emission  
   - https://docs.tokenomist.ai/features/csv-download
2. BeInCrypto 2024-07-31 历史文章：真实存在，引用 TokenUnlocks，给出 AVAX/APT/SAND/ARB/W 的 2024-08 解锁日期、规模、流通占比或分配项。  
   - https://beincrypto.com/token-unlocks-august-2024/
3. 事件研究方法：MacKinlay (1997) `Event Studies in Economics and Finance` 是真实 JEL 综述；可作为后续 B1 事件研究方法参考，但本阶段未做正式事件研究。

未核实到足以采用的来源：

- **代币解锁/vesting 抛压价格效应**：本轮未找到可直接依赖的同行评审或一级研究，只有行业数据源和新闻文章；不得在 B1 前写成“文献证明解锁后下跌”。
- **上市首日异常收益**：本轮搜索到“Coinbase effect”等新闻/二级材料，但未锁定可审计 primary paper；上币类不得凭俗称效应进入冻结方向。

## 验收标准自检

| 验收项 | 结果 |
|---|---|
| A. B0 机制红队逐条裁决 | 完成 |
| B1. 核本地价格面板时间覆盖 | 完成，35 资产 4H，全止 2024-12-09 20:00:00 |
| B2. 核免费解锁源 schema / 覆盖 / 历史边界 | 完成，Tokenomist schema 可核，但历史事件 API/CSV 非免费；Free/Standard 历史窗无本地重叠 |
| B3. 若有重叠则做 episode 初判 | 完成，仅文章样本 AVAX 1 个重叠，不足普查 |
| B4. 毛效应 vs 80/120/220bp 并列 | 完成，单样本绝对毛漂移过门但方向先验亏损，不能作方向结论 |
| 不碰 Holdout / 不回测 / 不调参 | 达标 |
| 输出脚本 + JSON | 完成 |

## 最终建议

**不进 B1；先补数据。**  
推荐冻结路径：暂不冻结事件类/方向。若必须保留 P1 主线，下一步应冻结为“代币解锁数据工程 Phase A2”，验收门只有一个：拿到可复现事件级历史表，字段至少含 `symbol, unlockDate, cliffAmount/value, valueToMarketCap 或 released/circulating supply pct, allocationBreakdown, dataSource`，并证明与 35 资产 4H 面板在 2020-2024 期间有 ≥100 个 episode；否则改为补 post-2024-12-09 价格面板研究 2025-2026 近端解锁。
