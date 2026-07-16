# REPORT_B1_KILLCARD_FORCED_FLOW_20260621

**任务 ID：** P1-RES-036-B1  
**任务类型：** 数据/功效 Kill Card（不耗失败计数；不碰 Holdout；不调参做 alpha）  
**执行时间：** 2026-06-21 UTC  
**执行者：** Codex  

## 0. 边界确认

- 已读必读文件：
  - `06_RESEARCH/PREREGISTRATIONS/FORCED_FLOW_ORDERFLOW_B0_MECHANISM_CARD.md`
  - `04_AI_TEAM/CODEX_TASKS/REPORT_REDTEAM_FORCED_FLOW_20260621.md`
  - `06_RESEARCH/RESEARCH_PROTOCOL_v1.4_A1SCREEN_ADDENDUM.md`
  - `06_RESEARCH/GRAVEYARD_INDEX.md`
- 新增可复跑审计脚本：`06_RESEARCH/CODE/b1_killcard_forced_flow_audit.py`
- 审计输出：`06_RESEARCH/CODE/output/b1_killcard_forced_flow_audit.json`
- Holdout：未读取 `06_RESEARCH/DATA/HOLDOUT/`、`sealed_holdout.enc` 或 A1 holdout 文件；脚本内置拒读 Holdout/sealed 路径。
- 未下单、未回测收益、未调参、未改预登记/治理权威文件。

## 1. 总裁决

**总建议：不进 B2。**

| 子机制 | 总裁决 | 依据 |
|---|---:|---|
| OFI / MLOFI（分钟级、非共置） | **KILL_AS_TRADABLE** | 成本门不过；订单流数据门不过 |
| 免费 Binance 清算流 | **SLEEP_DATA_ACCUMULATION_ONLY** | forceOrder 缺失不可界定；无单一方向命题；继承 A-1 风险 |
| 现货-永续 aggressive-flow lead-lag | **KILL_NOW_NOT_B2** | 当前无成对 aggTrades/book 数据与连续性审计；成本门未证明可过 |

若 Claude 不另立新的 lead-lag 数据审计任务并提供成对 spot/perp trade+book 数据，本方向应回墓园/休眠，机会地图回取 `#X2` 或其他候选。

## 2. 门1：成本可交易门

**结论：OFI KILL；清算流休眠；lead-lag 当前 KILL。**

成本带（round-trip drift hurdle，来自审计脚本）：

| 执行方式 | 有效成本 / hurdle |
|---|---:|
| Founder taker 进 + taker 出，基础滑点 10bp/边 | **30bp = 0.30%** |
| Protocol 保守 taker/taker 地板，费 10bp/边 + 滑点 10bp/边 | **40bp = 0.40%** |
| 事件压力 taker/taker，滑点 30/50/100bp/边 | **70 / 110 / 210bp** |
| maker/maker 名义费 | **4bp** |
| maker/maker 乐观：70% 成交、逆选 3bp/边 | filled-trade **10bp**；signal-level **14.29bp** |
| maker/maker 基准：50% 成交、逆选 5bp/边 | filled-trade **14bp**；signal-level **28bp** |
| maker/maker 压力：25% 成交、逆选 8bp/边 | filled-trade **20bp**；signal-level **80bp** |

Founder 的 maker 变量不能按“名义 4bp”入账。挂单在本机制中倾向于“错时成交”：真正成交时往往是流冲过来，必须扣逆向选择；未成交时则降低有效样本和功效。审计脚本用 `filled_trade_effective_cost = maker_fee_rt + adverse_selection_rt`，并用 `signal_level_hurdle = filled_trade_effective_cost / fill_rate` 给出 signal-level 折扣。

逐子机制：

- **OFI：KILL_AS_TRADABLE。** 分钟级公开 OFI 的合理毛效应上限按红队口径只能视作单 digit 至约 10bp 级。在最乐观 maker 折扣后，signal-level hurdle 仍为 14.29bp；taker 基础成本 30bp，Protocol 保守地板 40bp。`合理毛效应上限 > 有效全成本` 不成立。
- **清算流：SLEEP。** 级联/事件窗必须报告 0.3/0.5/1.0% 滑点压力档；对应 taker/taker hurdle 为 70/110/210bp。免费清算数据无法给出可靠毛效应上限，不允许进入 B2。
- **lead-lag：KILL_NOW_NOT_B2。** 跨市场 aggressive-flow lead-lag 仍接近延迟套利边界；在非共置秒-分钟窗口，未有数据证明合理毛效应上限能超过最乐观 maker signal-level 14.29bp 或 taker 30bp。

## 3. 门2：数据完整门

**结论：清算流 KILL_TO_SLEEP；订单流 KILL。**

审计事实：

- `06_RESEARCH/DATA/LIQUIDATIONS/`：存在但 0 文件。
- `06_RESEARCH/DATA/LIQ_SAMPLE/`：存在但 0 文件。
- `06_RESEARCH/DATA/SPOT/`：存在但 0 文件。
- `06_RESEARCH/DATA/FUTURES/`：仅有 mark/funding/metrics 低频或非订单流文件，不能替代 aggTrades + L2 book。
- `collector.log`：155 次 heartbeat，非零 heartbeat 为 0；最大 rows=0；出现 `ping/pong timed out` 22 次、`UNEXPECTED_EOF_WHILE_READING` 170 次、`Connection to remote host was lost` 51 次。
- `collector_dataplane_diag.json`：6 个 handshake-capable/测试路径均为 0 aggTrade frames；诊断结论为 Mac 侧路径全 60 秒零数据帧，需 VM 直跑，Mac 侧继续 patch 无意义。

逐项判定：

- **清算流：不能界定 Binance 免费 forceOrder 缺失。** 当前本地采集没有任何有效 liquidation rows，且免费 `forceOrder` 本身可能是抽样/截断广播；不能证明极端窗缺失是随机还是系统性。因此清算路径只能数据积累，不可确证。
- **订单流：不能证明 aggTrades taker 方向字段一致性。** Binance `buyer-is-maker` 字段理论上可转换主动买/卖方向，但仓库内没有 aggTrades 样本可复核；现有 dataplane 诊断还显示 aggTrade 采集零帧。
- **L2 book：不能证明连续重建。** 仓库内没有 depth snapshot/updateId 连续性、gap repair、撮合时间/本地到达时间分离记录，也没有可审计 L2 rebuilder。MLOFI 数据门不过。
- **lead-lag：不能证明成对 spot/perp 连续数据。** `SPOT/` 为空，没有 paired spot/perp aggressive-flow + book continuity audit。

## 4. 门3：反 A-1 门（清算路径）

**结论：清算路径 KILL_TO_SLEEP。**

本次没有看收益，也没有选择“延续”或“耗尽”。但当前 B1 任务和既有文件没有冻结一个可执行的单一方向命题。若后续清算流要复活，必须在任何收益检查前由 Claude 在新预登记中二选一：

- 清算方向延续；或
- 清算后耗尽反转。

禁止两头测后择优。当前免费数据状态下，“用真实强平流直接观测”这一点也没有成立，因此不能与墓园 A-1 的 `OI proxy 48h 回弹 FAILED` 做真实区分。清算路径继续推进会成为 A-1 换皮。

## 5. 门4：反 Sweep 白名单门

**结论：仅条件 PASS；不产生 B2 放行。**

允许变量白名单：

- 清算 notional
- signed taker volume
- OFI / MLOFI
- 深度不平衡
- spread
- RV / OI 控制

禁止变量：

- 支撑阻力、突破回踩、插针、sweep、结构位、局部高低点、K 线/影线/均线形态
- “在某个图上价位挂单赌反转”

Founder 的 maker 挂单变量只有一种合规方式：挂单价位由流变量定位，例如盘口深度不平衡、spread、流冲击后的可审计 book level；不得由图上支撑阻力、前高前低、突破回踩点位定位。

OFI 和 lead-lag 在概念上可以只用流变量，因此本门是 **PASS_CONDITIONAL**。但它们已死在成本/数据门，本条件通过不构成 B2 放行。

## 6. 子机制逐项结论

### 6.1 OFI / MLOFI

- 门1：**KILL_AS_TRADABLE**
- 门2：**KILL**
- 门3：N/A
- 门4：PASS_CONDITIONAL
- 总结：**KILL_AS_TRADABLE，不进 B2。**

原因不是“OFI 没有统计相关性”，而是当前任务问的是交易路径：非共置、分钟级、全成本、含 maker 成交率和逆选折扣后，合理毛效应上限不能超过有效成本；同时本地没有可审计 aggTrades/L2 连续重建数据。

### 6.2 免费清算流

- 门1：**KILL_TO_SLEEP**
- 门2：**KILL_TO_SLEEP**
- 门3：**KILL_TO_SLEEP**
- 门4：PASS_CONDITIONAL
- 总结：**只可数据积累，不得进入 B2。**

复活前提：付费全量强平源，或 VM 侧 3-6 个月前向完整采集，并在看收益前冻结单一方向命题。

### 6.3 Spot-perp / venue aggressive-flow lead-lag

- 门1：**KILL_NOW**
- 门2：**KILL_NOW**
- 门3：N/A
- 门4：PASS_CONDITIONAL
- 总结：**不能直接取 lead-lag 进 B2。**

它可作为未来独立数据审计候选，但前提是先取得 paired spot/perp aggTrades + L2 books、记录交易所撮合时间和本地到达时间、证明 updateId 连续/gap repair，并以非共置秒-分钟窗口和全成本为硬边界。

## 7. 验收标准逐条自检

| 验收项 | 状态 | 说明 |
|---|---:|---|
| 四门逐门 PASS/KILL | PASS | 第 2-5 节逐门给出 |
| 每个子机制 PASS/KILL | PASS | 第 6 节给出 |
| Founder maker 挂单变量 | PASS | 成交率、逆选、signal-level hurdle 已入账 |
| 不碰 Holdout | PASS | 脚本拒读 Holdout/sealed；未读取相关路径 |
| 不改 Claude 独占权威文件 | PASS | 未改 DECISION_LOG/CURRENT_STATE/预登记 |
| 不下单、不调参、不耗失败计数 | PASS | 仅做数据/成本审计 |
| 输出 CODE/RESULTS/报告 | PASS | 脚本 + JSON 输出 + 本报告 |
| TASK_INBOX 完成事件 | PASS | 已写入根目录并被调度器归档到 `04_AI_TEAM/TASK_INBOX/PROCESSED/P1-RES-036-B1_DONE.json` |

## 8. 最终建议

**不进 B2。**

执行建议：

1. **OFI：回墓园或标记 `KILL_AS_TRADABLE`。**
2. **清算流：休眠/数据积累。** 付费全量源或 3-6 月 VM 前向采集前，不允许做机制确证。
3. **lead-lag：不直接取。** 若 Claude 认为值得保留，只能另立 B1 数据审计任务；否则强制/激进流方向休眠，回机会地图取 `#X2`。
