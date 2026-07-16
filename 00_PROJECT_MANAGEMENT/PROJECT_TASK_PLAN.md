# 项目任务计划书

**状态：** ACTIVE / 项目详细任务单一权威  
**版本：** v1.0  
**基线日期：** 2026-06-15  
**覆盖范围：** Phase 0-3 × 9 能力域 × 7 条 L1 价值流  
**上位总图：** `00_PROJECT_MANAGEMENT/COMPANY_BUILD_MASTERPLAN_v1.md`

## 维护纪律

1. **本表是项目任务的唯一详细权威。** `CURRENT_STATE.md §4` 只保留当前焦点、阻塞和本表指针，不再复制全量任务。
2. 对话中任何任务新增、范围调整、优先级变化、阻塞、恢复、完成、废弃或 Founder/Claude 决策，必须在当轮更新本表。
3. 完成必须有产物或可复核证据链接；“文件已写”不自动等于能力已建成。
4. 废弃任务不删除，保留原行并标 `⛔废弃`，在“下一步”写墓园/原因/复活条件。
5. 阻塞任务标 `🔴阻塞`，必须写明阻塞源和解除条件；解除后改为实际状态，不保留假阻塞。
6. `🔵新增` 表示本轮识别、尚未进入执行队列的新任务；`🟡调整` 表示范围/优先级/方法已改变，需按“下一步”重新排程或确认。
7. Founder D 级确认、资金动作、阶段跨越和重大架构变更不能由任务完成状态代替。
8. 任务 ID 永不复用；拆分任务时保留父任务并新增子 ID。

## 状态图例

| 状态 | 含义 |
|---|---|
| ✅完成 | 验收已通过且证据已落盘 |
| 🟢进行中 | 当前有执行者和明确下一动作 |
| ⚪待办 | 已进入计划，等待依赖或排期 |
| 🔵新增 | 新识别任务，待 Claude 排优先级 |
| 🟡调整 | 已有任务发生范围、顺序或方法调整 |
| ⛔废弃 | 任务/方向已终止，保留原因与墓园指针 |
| 🔴阻塞 | 无法继续，已写阻塞源与解除条件 |

## 当前焦点（2026-07-12 state-sync 更正，DEC-092执行结果；此前 2026-07-01 state-sync DEC-087~091；2026-06-22 战略复盘 DEC-087/088）

- **权威路线图＝`OPPORTUNITY_MAP_STATUS.md §🧭`**（本段为指针，不复制全量）。
- **⚫终局（2026-07-15审计更正，取代本行2026-07-06旧文）：TSMOM引擎L已于2026-07-12经Holdout一次性盲验FAIL判死（DEC-093，P0-RES-015），全家族永闭、禁开任何变体。** 2026-07-06"七项检查全过"最终成为"回测全门+WF全过仍样本外死"的协议价值实证。"TSMOM定仓穷尽"历史口径经历"推翻→复活候选→Holdout判死"全周期，终局=Dead。详见`GRAVEYARD_INDEX.md`、下方P0-RES-015行。**当前领跑=投研线高频thesis冲刺（DEC-091/094，进度2/10-20），任务追踪见P0-RES-016行与`CURRENT_STATE.md §1b`。
- **⚠️ 战略拐点（DEC-087/088，历史记录，TSMOM一项已被2026-07-06进展更正）：** 三免费价格软-payer线连灭（~~TSMOM定仓穷尽~~已复活见上/`P1-RES-037`#X2跨链RV 阶段0 KILL/`P1-RES-038`#X3横截面动量 B1 KILL，后两者仍维持墓园判决）。**口径更正：死的是普通价格形态+低维横截面动量，不是整个免费价格族——免费结构数据(funding/OI/basis/强平/taker失衡)+事件交互未试完。** 机制优先扩7类。三方(Claude/零认知子代理/Codex红队)独立印证方法没跑偏。
- **目标函数修订（DEC-087 Founder D级）：** 猎场过滤器(多空对称/24x7/杠杆可得/低准入)松绑为可选；保命纪律硬(先edge再投核心资本/杠杆=已验证edge乘数非利润源/月化30%只是资本愿望不约束研究)。
- **🟡唯一研究主线（DEC-088）＝P0 加密合约 forced-flow/payer-flow v2**（funding极端/OI重置/强平簇/taker失衡，**弃普通价格动量**）。序列=**B0机制卡(单一方向预登记,成本门前置)→B1-KILLCARD(默认KILL)→B2(1x)→B3入场优化→B4杠杆风险**（任一步不过即 pivot，禁改参数续命）。免费阶段A强平数据预筛(Coinalyze/Tardis/Bybit自采)并入数据层。**状态更新（2026-07-01，state-sync 修正原"下一步=起草B0"过期指针）：B0机制卡已起草完成**（`06_RESEARCH/PREREGISTRATIONS/FORCED_FLOW_PAYER_FLOW_V2_B0_MECHANISM_CARD.md`，任务ID P0-RES-038-B0，REVISE_ONCE）**，阶段A数据审计发现强平簇缺重叠数据/taker缺L2/funding易退化carry→机制未否，转被动攒数/PARK**，量化主动猎暂停（Founder认可），当前唯一P0轨=投研线（DEC-091四层管道）。解冻条件=强平数据积累到位（采集器持续收数中）或Founder时间判定为瓶颈。
- **P1（升一等，P0后或并行）：** 事件×结构资金流（FOMC/上币/解锁/脱锚，与OI/funding合并）。**P2：** 山寨操盘痕迹沙盒。**P3观察：** 美股事件/散户期权/ETF流。**支线：** 实战者方法论蒸馏(只蒸馏机制/付钱方喂P2)。**三账户分层：** Research/Paper-forward/Discretionary sandbox。
- **DEFER（DEC-082/088）：** Spec Kit/ADR-业务项/C4全套/Orchestrator/Web/Discord/七维路由/九域记分卡。
- **被动并行：** `P1-RES-014` 强平采集器持续攒数(245k条已同步本地，VM→本地同步待常态化，不新建定时任务)，不占研究 WIP。
- **明确暂缓：** `P1-RES-008` TSMOM universe 扩展；`P0-STR-005`（公司终态）待 edge 后再谈。

## Phase 0：原则与证据基础

### 战略、目标函数与资本边界

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P0-STR-001 | 明确公司 North Star、自有资本客户和自动化终态 | ✅完成 | Founder D；Claude | 无 | 仅在公司范围改变时重开 | `00_PROJECT_MANAGEMENT/COMPANY_STRATEGY_PRODUCT_v1.md`；DEC-004/007 |
| P0-STR-002 | 冻结真实/可持续/可放大 edge + 核心资本安全复利目标函数 | ✅完成 | Founder D；Claude | P0-STR-001 | 按 DEC-063 执行 | DEC-063；`00_PROJECT_MANAGEMENT/CONSTITUTION.md` |
| P0-STR-003 | 建立核心资本/围栏资本两层架构与证据等级解锁 | ✅完成 | Founder D；Claude | P0-STR-002 | 实盘前另立资本运行协议 | DEC-063/066/069 |
| P0-STR-004 | 建立项目时间盒、成本盒和 L3 裁量主闸 | ✅完成 | Founder D；Claude | P0-STR-002 | 持续维护成本与时间证据 | DEC-069；`01_MEMORY_CORE/CURRENT_STATE.md` |
| P0-STR-005 | 确认公司推荐终态与 Phase 0-3 新阶段边界 | ⚪待办 | Founder D | P1-PMO-010 | 审阅总图 §2/§6/§9，确认或退回修改 | `00_PROJECT_MANAGEMENT/COMPANY_BUILD_MASTERPLAN_v1.md` |

### Alpha 研究与证据管理

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P0-RES-001 | 建立 Research Protocol、预登记、WF、成本、Holdout 和红队纪律 | ✅完成 | Claude；Founder确认 | 无 | 仅按正式增补件升级 | `06_RESEARCH/RESEARCH_PROTOCOL_v1.md`；`06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` |
| P0-RES-002 | 用 v1.3/v1.4 四件套、事件压力档、第五件和 MDE 门替换旧 Sharpe/MaxDD 尺子 | ✅完成 | Claude；Founder确认 | P0-RES-001 | 新实验按最新协议执行 | DEC-063/066/069；Protocol 增补件 |
| P0-RES-003 | 建立可审计小函数库纪律，禁止 MLFinPy 等黑箱硬依赖 | ✅完成 | Claude；Codex | P0-RES-001 | 新统计方法先自实现并测试 | DEC-061 |
| P0-RES-004 | 建立机会地图状态机和墓园/禁引用措辞 | ✅完成 | Claude | P0-RES-001 | 每个二元结果当轮更新 | `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md`；`06_RESEARCH/GRAVEYARD_INDEX.md` |
| P0-RES-005 | 验收协议v1.3/v1.4增补件第3/5件测量对象修正（升级v1.5，DEC-092） | ✅完成 | fable审查；Claude裁决；Founder确认 | 无 | **2026-07-02完成**：第3件(爆仓概率)改判"是否存在可行仓位方案"而非已测方案是否达标；第5件(被动基准对照)改风险调整后比较。触发引擎L/#X3两条墓园记录一次性诊断复查（见P0-RES-006/007） | `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`（v1.5）；DEC-092 |
| P0-RES-006 | 诊断复查：TSMOM引擎L是否存在可行仓位方案（新3件口径） | ✅完成（2026-07-06） | Codex执行；Claude验收 | DEC-092；P0-RES-005 | **结果=EXISTS_FEASIBLE_POSITION_SIZING**（10%/15%目标波动率两点通过，10%点年化log增长18.40%/P(DD≥20%)=2.60%）——原"定仓维度穷尽"判决推翻，原FAILED解除，见GRAVEYARD_INDEX.md。**未完待续：** 需在10%仓位点补测WF+风险调整基准两项（见P0-RES-014）才能真正判定晋级 | `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES006_ENGINE_L_RECHECK_20260702.md` |
| P0-RES-007 | 诊断复查：#X3横截面动量被动基准门风险调整后重算 | ✅完成（2026-07-06） | Codex执行；Claude验收 | DEC-092；P0-RES-005 | 结果符合预期：风险调整后被动基准门`RISK_ADJUSTED_GATE_NOT_CONFIRMED`（CI穿0），但主死因（截面单调CI穿0+幸存者偏差）不受影响，**整体KILL_MAINTAINED，不复活** | `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES007_X3_BENCHMARK_RECHECK_20260702.md` |
| P0-RES-014 | TSMOM引擎L在10%/15%目标波动率点用v1.5风险调整法重算被动基准门 | ✅完成（2026-07-06） | Codex执行；Claude验收 | P0-RES-006、P0-RES-007（同款方法） | **结果：10%/15%两点七项检查全过**（10%点：策略年化log增长12.98% vs 基准11.78%，diff+1.20%，95%CI[-4.21%,6.24%]，"显著跑输"不成立）。**这是DEC-092落地以来、也是本项目至今唯一走完当前量化验收协议全流程的候选。** 未消耗Holdout，未产生前向证据——是否晋级待Claude/Founder决策，见CURRENT_STATE §1c | `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES014_ENGINE_L_BENCHMARK_RECHECK_20260706.md` |
| P0-RES-008 | 修复价格面板6个刷新失败symbol（含BTCUSDT，SSL错误） | ✅完成（2026-07-06，Claude直接执行） | Claude | `06_RESEARCH/CODE/panel_refresh_2026.py` | 根因=瞬时连接问题（非代码/symbol错误），直连重试后37/37全部续到2026-06-22。**新发现待评估**：BTCUSDT历史深度远低于其他symbol（仅2024-12-09起，其余多为2020年起）——原始面板从未含BTCUSDT，非本次引入 | `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES008_PANEL_SSL_FIX_20260706.md` |
| P0-RES-009 | 备胎侦察R1：Hyperliquid链上完整清算数据可行性 | ✅完成（2026-07-06，Claude WebSearch/Fetch直接调研） | Claude | fable备胎扫描2026-07-02 | **结论：不是forced-flow v2数据墙的直接解法**——免费第三方归档(Hydromancer Reservoir)对Hyperliquid永续合约历史只从2025年8月起(~11个月)，深度接近我们已修复的BTCUSDT(~1.5年)，远不及其余symbol(~6年)；且清算机制(链上CLOB+ADL)与Binance(保险基金)结构不同，不能直接当同一机制的证据外推。**建议列为几乎零成本的独立平行验证线**，留待P0重启时顺手验证，不单独立项 | `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES009_HYPERLIQUID_SCOUT_20260706.md` |
| P0-RES-010 | 备胎侦察R3：Binance退市强制平仓事件库存 | ✅完成（2026-07-16，Claude验收裁决=**历史库存不立项**：124行库存中与面板可对齐仅8行、永续强制结算仅1行(OMG)<<30门槛；Mac→Binance now 451，官方全量爬取不可稳定） | Codex执行✅；Claude验收✅ | fable备胎扫描2026-07-02 | **价值转移**：退市事件改由新扫描器`binance_announcement`源前向捕获（futures_delist类，2026-07-16实测4条），活体样本随巡检自动积累，优于挖历史；库存CSV归档`06_RESEARCH/DATA/DELIST_EVENTS/` | `REPORT_P0RES010_BINANCE_DELIST_EVENTS.md` |
| P0-RES-011 | 备胎侦察R4：期权对冲流(#6/#7)DEFER前提复核 | ✅完成（2026-07-16，Claude验收裁决=**"需付费"前提推翻**：Deribit/Bybit/Binance公开API足够免费初筛；Laevitas免费档仅1周历史不作核心源） | Codex执行✅；Claude验收✅ | fable备胎扫描2026-07-02 | 机会地图Tier3行口径已修正为FREE-SCREENABLE（DEFER维持，WIP纪律不变，解冻时零成本先初筛） | `REPORT_P0RES011_OPTIONS_HEDGE_FLOW_DATA.md` |
| P0-RES-012 | 备胎侦察R5：美股事件×bStocks容量核实 | ✅完成（2026-07-16，Claude验收裁决=**容量优势不成立，P3观察维持不升级**：无借贷=空头不可表达、collateral要VIP3+、451地理限制实测、名义量$272M/日但刷量不可剔且非Binance独占口径；fable原判方向对、Founder的量数据也真——名义量大≠可执行容量） | Codex执行✅；Claude验收✅ | Founder 2026-07-02指出bStocks成交量数据 | 无后续动作；bStocks快照归档`06_RESEARCH/CODE/output/p0res012_*.csv`；若未来开通借贷/杠杆再重评 | `REPORT_P0RES012_BSTOCKS_CAPACITY.md` |
| P0-RES-013 | 备胎侦察R6：境内合规黄金渠道（上期所黄金期货/银行黄金T+D） | ⚪存档待排期 | Claude/Codex | Founder 2026-07-02提出 | 初步资料研究是否有可测微观机制，**明确排除MT4/MT5境外黄金CFD（合规风险，见已否决清单）** | `OPPORTUNITY_MAP_STATUS.md`备胎清单R6 |
| P0-RES-016 | L1深度审计R7执行包（2026-07-15）：①面板月刷制度化②投研扫描源拓宽③侦察批010/011/012 | ✅**全部完成并验收（2026-07-16当日）** | Claude起草✅；Codex/脚本执行✅；Claude验收✅ | L1审计2026-07-15处方R7 | ①**面板37/37刷至2026-07-16，0失败**——两个根因修复：END_UTC硬编码6/22（改动态）+Mac直连Binance退化为HTTP 451 geo封锁（6/22还通），刷新改走通道B一键脚本`06_RESEARCH/CODE/panel_refresh_via_sg.sh`；重叠窗=6/15起约31天被动增长，9/15复评forced-flow阶段A解冻；月刷挂月审维度8。②扫描器扩四源验收PASS（回归精确一致+6测试过+SG实测88候选/四源0错误，`REPORT_P0RES016_SCAN_SOURCES_20260716.md`）；巡检提示词已同步四源判定规则。③侦察批三报告验收完毕（裁决见各行）。R2/R4/R5治理小修同日落 | `L1_DEEP_AUDIT_CLAUDE_2026-07-15.md`；`REPORT_PANEL_REFRESH_2026_20260716.md` |
| P0-RES-015 | TSMOM引擎L（10%目标波动率点）Holdout一次性最终盲验（DEC-093，Founder 2026-07-12批准） | ✅**完成（2026-07-12，Claude验收裁决=FAIL，引擎L判死）**：H1 E[R]=-0.63%<0（生存底线）、H2年化log增长-6.86%<0两门不过；H3 DD17.0%过/H4基准门过；151笔非低功效；验收核查=hash全对+重构对账0差异+禁读边界干净+算术自检一致。死因=样本外趋势premium消失+成本拖累≈11.6%/年。TSMOM家族永闭，Holdout消耗封账，墓园/机会地图已写回。（派发过程留痕：首派CLI/模型不匹配失败[p0res015_run.log]→`-m gpt-5.5`重派成功[PID 11815, session 019f54e9, p0res015_run2.log]） | Claude起草预登记任务书✅；Codex执行中；Claude验收 | DEC-093；P0-RES-006/014 | 判据已冻结（四门H1-H4：窗内E[R]>0/年化log增长>0/实现DD<20%/风险调整基准门seed=20260712；Holdout窗=2024-12-10→2026-05-31；一次执行禁重跑；任务书SHA256=07ac51bb…5862cf）。VM轮询`p0res015_run.log`+`TASK_INBOX/P0RES015_DONE.json`；完成后Claude验收裁决PASS/FAIL并写回墓园/机会地图 | `04_AI_TEAM/CODEX_TASKS/TASK_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712.md`；待产出REPORT_P0RES015 |

### 治理、知识与审计

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P0-GOV-001 | 建立 CLAUDE/AGENTS 角色、专业异议和七问机制 | ✅完成 | Founder；Claude | 无 | 持续执行，不新增重复规则 | `CLAUDE.md`；`AGENTS.md`；DEC-057/065 |
| P0-GOV-002 | 建立 DECISION_LOG、Memory Core、BOOT_BRIEF 与 state-sync | ✅完成 | Claude | P0-GOV-001 | 保持派生摘要与权威源一致 | `01_MEMORY_CORE/DECISION_LOG.md`；`01_MEMORY_CORE/CURRENT_STATE.md` |
| P0-GOV-003 | 建立 L1/L2/L3 审计体系 | ✅完成 | Claude；Founder | P0-GOV-001 | 运行层连续稳定后评估精简 | DEC-022；`00_PROJECT_MANAGEMENT/STAGE_AUDITS/` |
| P0-GOV-004 | 建立 Holdout 加密、独立密钥和负向权限测试范式 | ✅完成 | Claude custodian；Codex executor | P0-RES-001 | 未来研究复用，不得降低权限边界 | A-1 v5 §12；`04_AI_TEAM/CODEX_TASKS/REPORT_A1_TIERA_EXEC.md` |
| P0-GOV-005 | 历史文件降级并禁止未经分析直接继承 | ✅完成 | Claude | P0-GOV-002 | 新设计引用历史时写独立评估 | `PROJECT_CONTEXT.md`；各旧主文档降级声明 |
| P0-GOV-006 | 建立 §1b 中断恢复和 TASK_INBOX 完成通知 | ✅完成 | Claude；Codex | P0-GOV-002 | 每个中断/完成任务按协议写入 | DEC-071；`04_AI_TEAM/TASK_INBOX/README.md` |

### 项目组合与交付管理

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P0-PMO-001 | 建立 Claude→Codex 任务规格、报告三件套和验收链 | ✅完成 | Claude；Codex | P0-GOV-001 | 持续使用任务/报告/完成事件 | `04_AI_TEAM/CODEX_TASKS/` |
| P0-PMO-002 | 接通 Codex CLI 直调与文件式 handoff | ✅完成 | Claude；Codex | P0-PMO-001 | 继续以真实退出码和报告验收 | DEC-061；`04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md` |
| P0-PMO-003 | 建立设计评审 DR 链和独立 Risk Reviewer | ✅完成 | Claude；Codex | P0-PMO-001 | 重大架构和独立 Alpha 继续使用 | DEC-071；A-1/carry RR 系列 |

## Phase 1：Edge 与最小可运行平台

### Alpha 研究与证据管理：已完成、废弃与当前主线

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-RES-001 | 完成 Sweep/SMC 形态家族研究与实现变体 | ⛔废弃 | Claude；Codex | P0-RES-001 | 永不复活形态版；查墓园防换皮 | `06_RESEARCH/GRAVEYARD_INDEX.md`；REPORT_0B1~0B18 |
| P1-RES-002 | 完成 A-2 funding 极端反转事件研究 | ⛔废弃 | Claude；Codex | P0-RES-001 | 反转版不复活；禁写“极端拥挤=延续” | `04_AI_TEAM/CODEX_TASKS/REPORT_R2_A2_EVENT_STUDY.md`；墓园 |
| P1-RES-003 | 完成 TSMOM v1/v2、regime 归因和宏观牛市门控 | ✅完成 | Claude；Codex | P0-RES-001 | Baseline 仅作相关性卡尺 | REPORT_P1_01~P1_06；DEC-060/062 |
| P1-RES-004 | 完成 TSMOM 双引擎 S 和风险预算 L 验证 | ⛔废弃 | Claude；Codex | P1-RES-003 | 镜像做空和第三定仓变体禁止重开 | `04_AI_TEAM/CODEX_TASKS/REPORT_TSMOM_DUAL_ENGINE.md`；`REPORT_B1.md` |
| P1-RES-005 | 新口径复读并确认 TSMOM=Baseline、定仓维度穷尽 | ✅完成 | Claude；Codex | P1-RES-003 | 仅保留为新 edge 相关性卡尺 | `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md`；`REPORT_B1.md`/`REPORT_B2.md` |
| P1-RES-006 | 构建 TSMOM 扩展 universe 数据探针 | ✅完成 | Codex | P1-RES-005 | 结果只证明数据层候选，不证明可用于 D2 | `04_AI_TEAM/CODEX_TASKS/REPORT_UNIVERSE_PIT.md`；`REPORT_D1.md` |
| P1-RES-007 | 审计 DEC-070 ADTV/跳动/float/OI 四过滤器 | ✅完成 | Codex；Claude验收 | P1-RES-006 | 保留“仅部分证据”结论 | `04_AI_TEAM/CODEX_TASKS/REPORT_DEC070_AUDIT.md` |
| P1-RES-008 | 执行 TSMOM universe 扩展 A/B 变体 | 🟡调整 | Claude；Founder D | P1-RES-006/007 | DEC-075 暂缓；若重启先补 mark-price、真实 funding、float/OI 数据，不沿用已阻塞输入 | `04_AI_TEAM/CODEX_TASKS/REPORT_D2.md`；DEC-075 |
| P1-RES-009 | A-4 新上市数据普查 | ✅完成 | Codex | P0-RES-004 | 保持 Candidate，等待主线空档再立机制卡 | `04_AI_TEAM/CODEX_TASKS/REPORT_B3.md` |
| P1-RES-010 | A-4 机制卡、功效和正式预登记 | ⚪待办 | Claude；Risk Reviewer | P1-RES-009、carry 结论 | carry 线闭环后再排；先查墓园与数据边界 | `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md` |
| P1-RES-011 | 设计并部署强平原始流采集器 | ✅完成 | Codex；Claude | A-1 数据缺口 | 保持被动收数与健康监控 | `04_AI_TEAM/CODEX_TASKS/REPORT_DEPLOY_COLLECTOR_VM.md` |
| P1-RES-012 | 核实 V4.6.2 数据源并定位 Binance WS 路由迁移 | ✅完成 | Codex | P1-RES-011 零帧 | 经验写入数据健康标准 | `04_AI_TEAM/CODEX_TASKS/REPORT_VERIFY_V462.md` |
| P1-RES-013 | 修复强平采集器 WS URL 并验证持续收帧 | ✅完成 | Codex | P1-RES-012 | 按帧数、last_message 和 JSONL 增量监控 | `04_AI_TEAM/CODEX_TASKS/REPORT_FIX_COLLECTOR_URL.md` |
| P1-RES-014 | 被动积累 A-1 路径 B 真实强平数据 | ⚪待办 | 自动采集器；Claude监控 | P1-RES-013 | 持续 3-6 月；仅到 readiness gate 才重启研究 | `06_RESEARCH/PREREGISTRATIONS/A1_FORWARD_LIQUIDATION_PATH.md` |
| P1-RES-015 | A-1 v1-v5 预登记与五轮独立盲审 | ✅完成 | Claude；Codex Reviewer | P0-RES-001 | 不再修改冻结 v5 | A1 prereg/review v1-v5；`REPORT_A1_RR5.md` |
| P1-RES-016 | A-1 Holdout custodian、权限负测与 Tier A 执行 | ✅完成 | Claude custodian；Codex executor | P1-RES-015 | 保持 sealed 38 条原封不动 | `04_AI_TEAM/CODEX_TASKS/REPORT_A1_TIERA_EXEC.md` |
| P1-RES-017 | A-1 独立回弹结论 | ⛔废弃 | Claude | P1-RES-016 | FAILED；不复活，不用 +1.32% 作 edge；OI 信号仅可作 carry 风控候选 | `06_RESEARCH/GRAVEYARD_INDEX.md`；`OPPORTUNITY_MAP_STATUS.md` |
| P1-RES-018 | carry 历史粗可行性核算 | ✅完成 | Codex；Claude | DEC-069 重开 carry | 仅作探索输入，不当确认 | `04_AI_TEAM/CODEX_TASKS/REPORT_CARRY_FEASIBILITY.md` |
| P1-RES-019 | carry 回测脚手架与 25 项合成测试 | ✅完成 | Codex | P1-RES-018 | 作为 v4 实现起点，差异必须逐条补齐 | `04_AI_TEAM/CODEX_TASKS/REPORT_CARRY_SCAFFOLD.md` |
| P1-RES-020 | carry v1 预登记和 RR1 | ✅完成 | Claude；Codex Reviewer | P1-RES-018 | v1 NOT APPROVED，保留审计链 | `CARRY_DELTA_NEUTRAL_PREREG_v1.md`；`CARRY_RISK_REVIEW_v1.md` |
| P1-RES-021 | carry v2 重构为历史 FEASIBILITY-LOCK + 前向确认 | ✅完成 | Claude | P1-RES-020 | v2 NOT APPROVED，保留重构成果 | `CARRY_DELTA_NEUTRAL_PREREG_v2.md`；`CARRY_RISK_REVIEW_v2.md` |
| P1-RES-022 | carry v3 闭合资本、OI、事件、shadow 和路径账本 | ✅完成 | Codex；Claude | P1-RES-021 | v3 NOT APPROVED，三项账本阻塞转 v4 | `CARRY_DELTA_NEUTRAL_PREREG_v3.md`；`CARRY_RISK_REVIEW_v3.md` |
| P1-RES-028 | carry v4 冻结 USDT 资本、1H 强平路径和交易小时 PnL | ✅完成 | Codex | P1-RES-022 | 不再修改，除非新预登记 | `CARRY_DELTA_NEUTRAL_PREREG_v4.md`；`REPORT_CARRY_V4_DRAFT.md` |
| P1-RES-029 | carry v4 第四轮独立盲审 | ✅完成 | Codex Reviewer | P1-RES-028 | APPROVED，仅放行历史可行性复核 | `CARRY_RISK_REVIEW_v4.md`；`REPORT_CARRY_RR4.md` |
| P1-RES-030 | 按 carry v4 冻结规格执行历史 FEASIBILITY-LOCK | ⛔废弃 | — | — | **DEC-079（2026-06-20）**：carry方向全线关闭，本任务永不执行。 | — |
| P1-RES-030A | carry数据采购 | ✅完成 | Claude（Mac直连Binance） | P1-RES-028/029 | **2026-06-20完成**：127个parquet落盘。数据用途已转为Regime-TSMOM输入（DEC-080）。 | `08_DATA/carry/`（127个parquet） |
| P1-RES-031 | carry 结果独立验收 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |
| P1-RES-032 | carry 前向 SHADOW 启动准备 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |
| P1-RES-033 | carry 18-24 月前向 SHADOW 一次性确认 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |
| P1-RES-034 | regime-adaptive 研究（原捆绑描述已冻结，DEC-082拆为B0-B4） | 🔵拆分中 | Claude起草；Codex执行/反审 | DEC-082；P1-RES-030A数据；P0-C先行 | **DEC-082冻结原「Regime×TSMOM×10-20x单实验+月均>20%/夏普>0.5验收」**（违反单变量+机制后置+杠杆前置+收益反推）。改单变量序列，验收口径=机制成立+成本后E[R]>0+爆仓概率/log growth/分年正期望+同状态被动基准对照（v1.4） | 见 B0-B4 子任务 |
| P1-RES-034-B0 | B0 机制卡（regime-adaptive 方向性） | 🟡Tier2持有（领跑被扫描推翻） | Claude起草 | DEC-082；P0-C验收 | **2026-06-21**：B0 v1 收窄为「强制流状态门控趋势」(REVISE_ONCE)。**随后机制扫描(14候选)推翻其领跑**：强制流门控仍=TSMOM+门控(同P1-04/06)+强平免费数据抽样截断(A-1旧伤)→**降Tier2持有**(待强平数据攒够+前档全灭再重启)。卡含 §6 扫描后再裁决。**未碰Holdout/未调参/不耗计数** | `06_RESEARCH/PREREGISTRATIONS/REGIME_ADAPTIVE_B0_MECHANISM_CARD.md` |
| P1-RES-035 | 机制候选扫描（14候选）+ Claude 排序裁决 | ✅完成 | Claude（子代理搜集，自己裁决） | B0 v1 | **2026-06-21 完成**：Founder挑战"先调研防烂尾"→general-purpose子代理扫14候选→Claude换皮裁决(不下放)。产出排序backlog(Tier1领跑=#X1横截面funding carry,Tier1备选=#X2跨链RV配对,其余Tier2/3/Defer)，落OPPORTUNITY_MAP_STATUS作pivot菜单。消费合约=研究主线选择依据+kill后抽下一档+晋级路径B0→B1→B2 | `06_RESEARCH/MECHANISM_SURVEY/CRYPTO_PERP_MECHANISM_SCAN_20260621.md`；`OPPORTUNITY_MAP_STATUS.md`机制候选段 |
| P1-RES-036-B0 | B0 机制卡：~~#X1 carry~~~~/#X2 RV~~ → **强制流/订单流机制**（形态=触发器，**新领跑 DEC-085**） | ✅完成（Codex红队通过，已推进至B1，见P1-RES-036-B1；**状态标签2026-07-12核实后更正**，此前长期滞留"🟢草成待Codex红队"，实际红队与B1均已完成） | Claude起草；Codex红队 | DEC-085；P1-RES-035 | **DEC-085（Founder D级2026-06-21）定向**：Founder要自动化但嫌市场中性利润低→看图法量化卡入场=风险D死循环,但形态背后有真机制→**猎强制流/订单流(流动性掠夺→清算流;量价→订单流),形态=触发器,入场优化后置B3,杠杆放大已验证edge取收益B4**。B0已起草=**PROCEED到B1**,带子机制选定门(建议OFI先行数据齐;清算流并行攒数)+数据功效门;防换皮vs A-1硬约束(A-1清算回弹FAILED,新线须选distinct子机制)。**✅Codex红队完成+Claude接受MODIFY→B0降REVISE_ONCE(默认KILL基线)**。**B1-KILLCARD已完成=不进B2**（见P1-RES-036-B1，OFI/清算流/lead-lag三子机制均未通过数据-功效门），此线已终结，不再有下一步 | `FORCED_FLOW_ORDERFLOW_B0_MECHANISM_CARD.md`(§5修订)；`REPORT_REDTEAM_FORCED_FLOW_20260621.md` |
| P1-RES-036-B1 | B1-KILLCARD：强制/激进流数据-功效门（四道非收益筛查） | ✅完成=不进B2 | Codex；Claude验收 | B0 REVISE_ONCE | **2026-06-21完成=不进B2**：OFI KILL_AS_TRADABLE(成本门:maker最乐观signal-level 14bp>分钟级信号~10bp+本地无可审计aggTrades/L2);免费清算流SLEEP(forceOrder缺失不可界定=A-1换皮);lead-lag KILL_NOW(无成对spot/perp数据)。Founder maker变量已入账(成交率+逆选折扣)。⚠️审计发现本地强平/SPOT数据0行+采集器零帧→需核VM。下一步=Founder三选一(回#X2/付费数据/修采集器攒数) | `REPORT_B1_KILLCARD_FORCED_FLOW_20260621.md`；`06_RESEARCH/CODE/b1_killcard_forced_flow_audit.py` |
| P1-RES-037 | 研究范围约束登记：禁资金费型策略（DEC-084） | ✅完成 | Founder D；Claude | 无 | **2026-06-21**：Founder口头"不要做资金费策略"→落DEC-084。严格读法=禁funding-harvest为edge(delta-carry/横截面carry/任何变体)；funding可否作非edge状态输入=待Founder边界确认(从严)。 | DEC-084；OPPORTUNITY_MAP_STATUS |
| P1-RES-037-B0 | B0 机制卡：#X2 跨链/跨品种相对价值配对（强制流死后回取，新领跑） | ⛔KILL（阶段0，DEC-088） | Claude起草；Codex红队 | 强制流B1全灭；DEC-084合规 | **2026-06-22（DEC-088战略复盘）**：三方独立扫描印证后于阶段0 KILL，入墓园，不再是研究主线；领跑权转 forced-flow/payer-flow v2（见 P0-RES-038-B0）。原 2026-06-21 起草记录保留存档。 | `06_RESEARCH/PREREGISTRATIONS/CROSS_ASSET_RV_B0_MECHANISM_CARD.md`；`06_RESEARCH/GRAVEYARD_INDEX.md` |
| P0-RES-038-B0 | B0 机制卡：forced-flow/payer-flow v2（funding极端/OI重置/强平簇/taker失衡，弃普通价格动量，DEC-088新领跑） | 🟡PARK·数据饿死 | Claude起草 | DEC-088；强平采集器数据层 | **2026-06-22起草=REVISE_ONCE**。**2026-06-22阶段A数据审计**：OI重置成本门fail入墓园/强平簇缺重叠数据/taker缺L2/funding易退化carry→**机制未否，仅免费当前数据不可测**，转被动攒数/PARK（非放弃）。强平采集器持续健康收数（本地已续到`liq_20260701.jsonl`，245k+条）。**下一步=数据积累到可测阈值后重启B1-KILLCARD，或Founder时间判定为瓶颈时改用付费数据源**。量化主动猎暂停期间不占WIP，投研线（DEC-091）领跑。 | `06_RESEARCH/PREREGISTRATIONS/FORCED_FLOW_PAYER_FLOW_V2_B0_MECHANISM_CARD.md` |
| P1-RES-014B | 核实强平采集器（风险E排查→误报更正） | ✅完成=采集器健康 | Claude直连VM | B1审计报本地0行 | **2026-06-21**：Claude直连VM(`id_ed25519_aiquant`)核实=**采集器健康**(service active 6/15起,VM上245,614条真实记录,今日19,842行在线)。B1"0行"=**VM→本地同步断**,非采集器死(上轮风险E误报已更正)。已rsync 7文件到本地`06_RESEARCH/DATA/LIQUIDATIONS/`。遗留:同步常态化(不新建定时任务,手动/Codex periodic)。Codex任务因429+沙箱挡SSH失败,Claude直连完成 | `06_RESEARCH/DATA/LIQUIDATIONS/`(245k行) |
| P1-RES-034-B1 | B1 数据与标签审计 | ⚪B0后 | Codex；Claude验收 | B0=PROCEED | 验regime标签可滚动计算/无前视/切换延迟/样本量MDE/数据质量；**不得按收益选标签**；结束冻结标签规则或KILL | 待建 |
| P1-RES-034-B2 | B2 实验A：单变量Regime门控 | ⚪B1后 | Codex；Claude验收 | B1冻结标签 | 冻结TSMOM+1x，只测单一regime门控是否改善预登记指标且优于同状态被动基准；**禁同时调lookback/阈值/出场/费用/仓位/杠杆；禁多regime并行试到最好；禁把失败写「部分有效」** | 待建（预登记+功效段） |
| P1-RES-034-B3 | B3 实验B：仓位/波动目标 | ⚪B2过门后 | Codex；Claude验收 | B2 ACCEPT | 在冻结信号上测仓位/波动目标 | 待建 |
| P1-RES-034-B4 | B4 杠杆风险敏感性 | ⚪B3过门后 | Codex；Claude验收 | B3 ACCEPT | 仅过门后做，作风险测试（爆仓概率），**不作Alpha来源** | 待建 |

### 策略产品化

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-PROD-001 | 将 `OPERATING_MODEL_DESIGN_v2` 重定位为策略交付生命周期 SOP | ✅完成 | Codex；Claude验收 | P1-PMO-010 | 后续只管 R-S-E，不承担公司总模型 | `00_PROJECT_MANAGEMENT/OPERATING_MODEL_DESIGN_v2.md` |
| P1-PROD-002 | 建立策略 SPEC 模板 | 🔵新增 | Claude；Codex DR | P1-PROD-001 | 以 carry 为首个真实实例，不先造空模板体系 | SOP 循环 S |
| P1-PROD-003 | 建立策略 ATD 验收测试定义模板 | 🔵新增 | Claude；Codex DR | P1-PROD-002 | 明确已知输入、期望持仓/PnL/风控输出 | SOP S3 |
| P1-PROD-004 | carry 策略 SPEC v1 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |
| P1-PROD-005 | carry 成本/仓位/账务模型规格 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |
| P1-PROD-006 | carry ATD v1 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |
| P1-PROD-007 | carry 接入最小平台接口契约 | ⛔废弃 | — | — | carry关闭连带废弃（DEC-079）。 | — |

### 工程借力与最小闭环（OSS集成，优先于自建）

> **来源：** OSS调研 `STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md` + 四棱镜A2审计。  
> **原则：** 不自建能借力替代的组件；自己只写薄风控/决策门/数据校验层。

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-OSS-001 | 建 DATA_CONTRACT.yaml + 数据校验层 | 🔵新增 | Codex；Claude DR | P1-RES-030（数据适用性证据） | 对价格源、funding、OI、时间、volume类型、缺失、cutoff、schema、hash逐项定义验收标准 | `05_TECH_DESIGN/DATA_CONTRACT.yaml`（待建） |
| P1-OSS-002 | Freqtrade 集成评估与配置 | 🔵新增 | Codex；Claude DR | P1-OSS-001 | 验证 Freqtrade futures 支持、DB持久化、dry-run/live切换；写配置骨架 | `05_TECH_DESIGN/FREQTRADE_INTEGRATION.md`（待建） |
| P1-OSS-003 | CCXT 薄封装适配层 | 🔵新增 | Codex | P1-OSS-002 | 覆盖 Binance perp REST/WS；统一 ticker/kline/funding/OI/account/order 接口；保留官方字段校验 | `07_INFRA/ccxt_adapter.py`（待建） |
| P1-OSS-004 | 数据历史取法标准化 | 🔵新增 | Codex；Claude DR | P1-OSS-001 | 对 contract/mark/funding/OI/continuous kline 分别定义正确来源+坑点；历史用 data.binance.vision；REST 补洞 | `05_TECH_DESIGN/DATA_SOURCES.md`（待建） |
| P1-OSS-005 | 强平数据策略决策（**升为OSS最高优先**） | ✅完成 | Claude | 无（成本盒内，不需Founder D） | **2026-06-20决策：跳过CoinGlass订阅**。三项数据（提币状态/USDT脱锚/ADL）均有免费替代（Binance spot/公告历史/ADL模型假设），性价比不成立（CoinGlass Pro ~$300/月，超月预算1000元CNY）。替代方案已写入TASK_DATA-001。 | `TASK_DATA-001_carry_data_procurement.md §第二批` |
| P1-OSS-006 | kill/pivot 条件显式化 | 🔵新增 | Claude；Founder D | P1-OSS-002 | 写明：何时判定"edge不值得继续"并pivot；carry失败后备选机制列表；时间/成本盒检查点 | `00_PROJECT_MANAGEMENT/KILL_PIVOT_CONDITIONS.md`（待建） |

### 交易平台与数据基础设施

> **2026-06-20调整：** 以下 PLAT 任务在 P1-OSS-002 完成后重新审视范围——部分自建功能可由 Freqtrade 直接覆盖（dry-run/live/DB/UI）；自建只保留 Freqtrade 不提供的薄层（风控守门、对账审计、研究验收）。

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-PLAT-001 | Phase 2 公司组织、系统架构、执行流和模块设计 E1-E4 | ✅完成 | Codex；Claude验收 | DEC-071/072 | 作为草图输入；OSS评估后部分自建计划可能废弃 | `05_TECH_DESIGN/01_COMPANY_ORG.md`~`04_MODULE_DESIGN.md` |
| P1-PLAT-002 | 冻结最小 paper 平台范围与非目标 | 🟡调整 | Claude；Founder D 如涉及重大架构 | P0-STR-005、P1-RES-031、**P1-OSS-002** | 范围须折入 Freqtrade 能力边界，不重建它已覆盖的部分 | `05_TECH_DESIGN/02_SYSTEM_ARCHITECTURE.md` |
| P1-PLAT-003 | 定义生产数据合同和数据适用性验收门 | 🔵新增 | Claude；Codex | P1-PLAT-002 | 对价格源、funding、OI、时间、缺失、cutoff、schema、hash 逐项验收 | D2/采集器事故证据 |
| P1-PLAT-004 | 建 PostgreSQL 最小 schema（订单/成交/持仓/风险/账务/决策请求） | ⚪待办 | Codex；Claude DR | P1-PLAT-002/003 | 先写 `05_DB_SCHEMA.md`，再迁移与测试 | DEC-008~011；`05_TECH_DESIGN/05_DB_SCHEMA.md`（待建） |
| P1-PLAT-005 | 建唯一 trade_id、订单幂等键和生命周期状态机 | ⚪待办 | Codex | P1-PLAT-004 | 覆盖拒绝同向覆盖、部分成交、撤单、重启 | DEC-009/010 |
| P1-PLAT-006 | 建实时数据增量采集和新鲜度监控 | ⚪待办 | Codex | P1-PLAT-003/004 | 先覆盖 carry 的 spot/perp/mark/index/funding/OI | 强平采集器经验 |
| P1-PLAT-007 | 建历史回放与 paper exchange 模拟器 | ⚪待办 | Codex | P1-PLAT-003/004 | 同一策略适配器支持回放和实时 paper | `02_SYSTEM_ARCHITECTURE.md` |
| P1-PLAT-008 | 建策略适配器接口和 Decision Gateway 输入协议 | ⚪待办 | Claude；Codex DR | P1-PLAT-004/005 | 输出不可变 decision_request snapshot | DEC-071；E2 |
| P1-PLAT-009 | 建订单执行器 paper 版与幂等重试 | ⚪待办 | Codex | P1-PLAT-005/007/008 | 限价/市价语义、指数退避、重复请求测试 | `04_MODULE_DESIGN.md` |
| P1-PLAT-010 | 建重启恢复、状态重建和备份恢复 | ⚪待办 | Codex | P1-PLAT-004/005/009 | 启动先读 DB 并与 paper exchange 对账 | DEC-008/011 |

### 实时风控与资本保护

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-RISK-001 | 冻结 Phase 2 具体风控参数 DEC | ⚪待办 | Founder D；Claude | P0-STR-005、DEC-072 | 代码化前确认单日熔断、总回撤、事件窗、极端波动、OI 暂停 | DEC-072 |
| P1-RISK-002 | 实现 Decision Gateway 唯一下单权 | ⚪待办 | Codex；Claude DR | P1-PLAT-008、P1-RISK-001 | 策略和 AI 均不能绕过 | `02_SYSTEM_ARCHITECTURE.md` |
| P1-RISK-003 | 实现 Position Registry 与 DB 权威状态 | ⚪待办 | Codex | P1-PLAT-004/005 | 禁止内存字典作为风控输入 | DEC-008~010 |
| P1-RISK-004 | 实现 Reconciliation Loop 和 Orphan Detection | ⚪待办 | Codex | P1-RISK-003、P1-PLAT-009 | 每轮风险检查前对账；未检查持仓告警 | DEC-011 |
| P1-RISK-005 | 实现账户/策略/资产/单笔硬限制与急停 | ⚪待办 | Codex | P1-RISK-001/002/003 | 全部错误路径有测试和结构化日志 | DEC-015/019/063/072 |
| P1-RISK-006 | 建风险规则回放测试与故障注入 | ⚪待办 | Codex | P1-RISK-002~005 | 覆盖重复单、DB 延迟、交易所不一致、强平、断网、重启 | Ghost Position 事故 |

### 交易运营、监控与事件响应

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-OPS-001 | 定义 paper 平台 SLI/SLO 与健康标准 | 🔵新增 | Claude；Codex | P1-PLAT-002 | 至少含数据新鲜度、消息量、订单成功、对账差异、风险扫描覆盖 | 采集器零帧事故 |
| P1-OPS-002 | 建结构化日志、指标与告警路由 | ⚪待办 | Codex | P1-OPS-001、P1-PLAT-006/009 | 告警必须有 owner、严重级别和 Runbook 链接 | `02_SYSTEM_ARCHITECTURE.md` |
| P1-OPS-003 | 编写数据停更/订单失败/对账异常/风险熔断/服务重启 Runbook | ⚪待办 | Claude；Codex复核 | P1-OPS-001 | 每类定义检测、止损、恢复、验证、升级 | `09_OPERATIONS/`（待建） |
| P1-OPS-004 | 建事件分级、接管责任帽子和事故模板 | 🔵新增 | Claude | P1-OPS-003 | 区分技术、数据、交易、风险和账务事故 | D10 Ghost Position 经验 |
| P1-OPS-005 | 执行 paper 环境故障恢复演练 | ⚪待办 | Codex；Claude验收 | P1-OPS-002/003、P1-RISK-006 | 留 MTTD/MTTR、状态一致性和复发防护证据 | 待产出 |

### 资本、账务与绩效归因

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-ACC-001 | 定义 paper 权威账本与会计恒等式 | ⚪待办 | Claude；Codex DR | P1-PLAT-004、carry v4 | 复用 NAV 差原则，明确订单/成交/funding/fee/transfer 落账 | carry v4 §4 |
| P1-ACC-002 | 实现订单、成交、持仓、现金、funding 与 NAV 日结 | ⚪待办 | Codex | P1-ACC-001、P1-PLAT-009 | 每日生成可复核 ledger snapshot | 待产出 |
| P1-ACC-003 | 实现交易所/DB/runtime 三方对账 | ⚪待办 | Codex | P1-ACC-002、P1-RISK-004 | 差异非零即阻断并告警 | DEC-011；E2 |
| P1-ACC-004 | 实现策略/机制/成本/事件绩效归因 | ⚪待办 | Codex；Claude验收 | P1-ACC-002 | 归因项严格求和到权威 NAV 差 | carry v4 §4.3 |
| P1-ACC-005 | 建资金划转审批与审计记录 | ⚪待办 | Founder D；Claude；Codex | P1-ACC-001/002 | paper 先模拟；实盘前冻结权限 | 两层资本架构 |

### 治理、知识与审计

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-GOV-001 | 将 `PROJECT_TASK_PLAN.md` 设为任务单一权威 | ✅完成 | Codex；Claude验收 | P1-PMO-010 | 对话变化当轮维护 | 本文件；`CURRENT_STATE.md §4` |
| P1-GOV-002 | 自动检查 CURRENT_STATE §4 不复制全量 WBS | 🔵新增 | Codex | P1-GOV-001 | 扩展 state_check，检测指针和重复表 | `01_MEMORY_CORE/state_check.py` |
| P1-GOV-003 | 建任务链接、状态、废弃原因和阻塞源完整性检查 | 🔵新增 | Codex | P1-GOV-001 | 校验每行 ID 唯一、证据链接非空、废弃/阻塞有原因 | 本文件 |
| P1-GOV-004 | 运行层达到连续 14 天零卡死 + state_check 零漂移 | ⚪待办 | Claude；自动化 | P1-GOV-002/003 | 达标后提出运行层 v1 冻结 | DEC-069 |
| P1-GOV-005 | 建知识结果到任务的反向引用检查 | 🔵新增 | Codex | P1-GOV-003 | 墓园/机会地图变更必须有对应任务状态更新 | `GRAVEYARD_INDEX.md` |
| P1-GOV-006 | 建3个Claude项目级Skill + Holdout硬门控 | ✅完成 | Claude | 无 | result-intake/codex-task-spec/research-harvest已建；protect-holdout.py已建 | `.claude/skills/`；`.claude/hooks/protect-holdout.py`（2026-06-20） |
| P1-GOV-007 | 建state-sync Skill + hypothesis-preregister Skill | 🟡进行中 | Claude | P1-GOV-006 | state-sync Skill ✅已建（2026-06-20）；hypothesis-preregister ⚪待建（新方向spec起草后补） | `.claude/skills/state-sync/SKILL.md` |
| P1-GOV-008 | TASK_INBOX文件监听daemon | 🔵新增 | Codex | 无 | 任务书已备好`04_AI_TEAM/CODEX_TASKS/BUILD_TASK_INBOX_DAEMON.md`；消除Codex→Claude复制粘贴传话 | `04_AI_TEAM/CODEX_TASKS/BUILD_TASK_INBOX_DAEMON.md` |
| P1-GOV-009 | 执行历史Codex报告积压harvest（实际~139份：84 CODEX_TASKS+55 RESULTS） | ✅完成 | Codex提取段+Claude判断段(DEC-069) | P1-GOV-006 | 2026-06-27完成。Codex扫139份→暂存`HARVEST_STAGING_20260627.md`(未碰正式库);Claude判断段→权威摘要`HARVEST_DIGEST_20260627.md`。**主理人判断=积压无埋藏edge/机制,全是已吸收负面知识;5个反复流程病(数据不全/口径漂移/机制先验弱/成本门/scaffold当证据)项目纪律已内化**。新增5道流程门(H1 BLOCKED≠FAILED/H2 scaffold≠证据/H3验证前置/H4工具治理登记/H5工具不替裁决)+4行动项(RA-H1~H4)。大类(Sweep/TSMOM/Carry/X2/X3/forced-flow)确认已在各KB/墓园,不重复。 | `02_KNOWLEDGE_BASE/HARVEST_DIGEST_20260627.md` |
| P1-GOV-010 | 文件归档：REORGANIZE-ARCHIVE-001 | 🔵新增 | Codex | Founder确认保留列表 | 任务书已备好；清理历史散落文件；待Founder确认不删除的文件列表后立即派Codex | `04_AI_TEAM/CODEX_TASKS/REORGANIZE-ARCHIVE-001.md` |
| P1-GOV-011 | 精简CLAUDE.md至≤200行，流程规则移入Skill | 🔵新增 | Claude | P1-GOV-007 | RA-013要求；当前CLAUDE.md内联所有规则=每次对话全量加载=token浪费；流程类规则→Skill；原则类保留；参考触发条件"阶段切换/持续输出偏差" | `CLAUDE.md`；RA-013 |
| P1-GOV-012 | harvest 外部历史项目 v4.6.2/openclaw（SG服务器） | ✅完成 | Claude（只读SSH） | 无 | **2026-06-27 Founder临时指派**。⚠️流程教训=Claude执行前未查计划(违规则4)。**裁决=策略/架构/因子一条不借**:v4.6.2自诊断22分制IC≈50%噪声+执行层修补=墓园标准死法;candidate-factors 8因子全墓园同族(F4=OFI已KILL/F6=funding carry+a2已死)。唯一收获=负面确认范式耗尽。SG只读未碰服务。≠P1-GOV-009(那是harvest我方60+Codex报告,仍待办)。 | CURRENT_STATE §1b ㊱ |
| P1-GOV-012 | 部署Claude subagents处理重量级上下文任务 | 🔵新增 | Claude | P1-GOV-006 | RA-012；超长对话漂移问题的机制解法：把"会淹没主上下文的60+报告扫描/日志分析/多文件读取"放独立subagent窗口；主对话保持干净 | `.claude/agents/`（目录已建） |
| P1-GOV-013 | 写Founder使用协议（对话管理+D级批处理+token节省） | 🔵新增 | Claude | P1-GOV-011 | 本次对话诊断出的Founder侧使用问题系统化；产物=`00_PROJECT_MANAGEMENT/FOUNDER_USAGE_PROTOCOL.md` | 本次对话诊断 |

### 项目组合与交付管理

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-PMO-010 | 建立公司建设总图与单一任务计划 | ✅完成 | Codex；Claude验收 | BPR 评审、全量取证 | Founder 审阅 D 级项；后续维护本表 | 总图；本文件 |
| P1-PMO-011 | Founder 确认总图终态与阶段边界 | ⚪待办 | Founder D | P1-PMO-010 | 审阅总图 §9 | 总图 |
| P1-PMO-012 | 为 Phase 1 关键路径设置月度里程碑和 WIP 上限 | 🔵新增 | Claude | P1-PMO-011 | 当前 WIP 限 carry 复核 + 必要平台前置，避免多线扩散 | 本文件 |
| P1-PMO-013 | 建 Phase 1→2 阶段审计包 | ⚪待办 | Claude；Independent Review | P1-RES-031、平台/风控/监控/账务 paper 门 | 按总图出口条件逐项给证据 | `STAGE_AUDITS/` |

## Phase 2：受控 paper 与小额实盘

### 阶段与资本门

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P2-STR-001 | Phase 1→2 阶段确认 | ⚪待办 | Founder D | P1-PMO-013 | 只有阶段审计通过后批准 | 总图 §6 |
| P2-STR-002 | 冻结小额真金上限、亏损阈值和降级规则 | ⚪待办 | Founder D；Claude | P2-STR-001、策略 shadow 资格 | 形成实盘资本协议和 DEC | DEC-015/069；carry v4 §9.3 |

### 证据到部署 / 信号到结算

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P2-DEP-001 | carry paper 集成测试 | ⚪待办 | Codex；Claude验收 | P1-PROD-004~007、P1-PLAT、P1-RISK、P1-ACC | 历史回放逐笔对照策略 ATD | 待产出 |
| P2-DEP-002 | carry 前向 shadow 运行 | ⚪待办 | 自动系统；Claude运营 | P2-DEP-001、P1-RES-032 | 按冻结 T0 和 18-24 月协议运行 | carry v4 §9 |
| P2-DEP-003 | 小额真金上线审批与部署 | ⚪待办 | Founder D；Claude；Codex | P2-DEP-002=CONFIRMED、P2-STR-002 | 仅启用批准额度，不升杠杆 | 待产出 |
| P2-DEP-004 | 真实订单、成交、funding、持仓和 NAV 日结 | ⚪待办 | 自动系统；Codex维护 | P2-DEP-003 | 每日零差异对账 | P1-ACC 系列 |

### 异常到恢复

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P2-OPS-001 | 生产告警与人工接管值守 | ⚪待办 | Claude / Risk & Operations Lead | P1-OPS-005、P2-DEP-003 | 按严重级别自动升级 Founder | Runbook |
| P2-OPS-002 | 真实急停、重启恢复和三方对账演练 | ⚪待办 | Codex；Claude验收 | P2-DEP-003 | 在不损坏账务前提下完成演练 | 待产出 |
| P2-OPS-003 | 首次真实事故闭环 | ⚪待办 | Claude；Codex | 实际事故触发 | 记录检测、处置、恢复、根因、预防；无事故不虚构完成 | 事故报告模板 |

### 绩效到配置

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P2-CAP-001 | 建真实绩效/风险/容量月度决策包 | ⚪待办 | Claude；Codex数据 | P2-DEP-004 | 给出继续/缩减/暂停/增配单一建议 | 待产出 |
| P2-CAP-002 | 首次资本配置复审 | ⚪待办 | Founder D | P2-CAP-001、观察窗完成 | 记录决定与证据，不自动升额 | 待 DEC |

### Track B AI 分析

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P2-AI-001 | 实现 AI Pre-Execution Analyst 异步 advisory worker | ⚪待办 | Codex；Claude DR | P1-PLAT-008、P1-ACC-004、Founder确认 Track B | 冻结 snapshot、schema、timeout、cap、circuit breaker | `05_TECH_DESIGN/02_SYSTEM_ARCHITECTURE.md` |
| P2-AI-002 | 实现日报/周报/异常分析 | ⚪待办 | Codex；Claude | P2-AI-001、监控与账务数据 | AI 不得伪装 unavailable 为 approve | E2 |
| P2-AI-003 | 验证 Track B 故障不影响 Track A | ⚪待办 | Codex | P2-AI-001/002 | 断 API、超时、schema 错误故障注入 | E2 fallback 语义 |

## Phase 3：稳态复利与有限扩展

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P3-STR-001 | Phase 2→3 资本规模与公司范围确认 | ⚪待办 | Founder D | Phase 2 稳态证据 | 确认资本上限、策略数、多所边界 | 总图 §9 |
| P3-PORT-001 | 建多策略组合相关性与资本分配 | ⚪待办 | Claude；Codex | 至少两个前向确认策略 | 以边际贡献和尾部相关性配置，不按单策略收益排序 | 待产出 |
| P3-PLAT-001 | 验证新增策略只接入平台、不复制底座 | ⚪待办 | Claude；Codex DR | 第二个部署候选 | 接入评审必须证明无私有订单/状态/风控/账务 | SOP 循环 E |
| P3-OPS-001 | 建稳定运营 SLO、容量和变更管理 | ⚪待办 | Claude；Codex | Phase 2 运营数据 | 冻结事故率、MTTR、对账差异和发布门 | 待产出 |
| P3-CAP-001 | 建资本扩张、降级和退出制度 | ⚪待办 | Founder D；Claude | P3-STR-001 | 任何升额有观察窗和回滚门 | 待 DEC |
| P3-GOV-001 | 评估是否需要多交易所/外部业务新总图 | ⚪待办 | Founder D；Claude | 稳态后出现真实需求 | 另立 v2，不在 v1 偷渡范围 | 待产出 |

## 关键路径与等待规则

1. **当前主路径（借力路线，2026-06-20修正）：** `[P1-OSS-005(CoinGlass决策) + P1-RES-030A(数据采购)] 并行 [custodian封存] → P1-RES-030(carry可行性) → P1-RES-031(验收) → P1-OSS-001(DATA_CONTRACT) + P1-OSS-002(Freqtrade) → P1-OSS-003/004 → P1-PLAT(精简范围) → P2-DEP-001`。**关键修正：DATA_CONTRACT和Freqtrade在carry可行性之后，不是之前**——carry数据决策(P1-OSS-005)是当前OSS第一优先。
2. **build-vs-buy 硬关卡：** P1-PLAT任何自建子任务开工前，必须先核对 P1-OSS-002 结论——Freqtrade 已覆盖的能力不自建。
3. carry 历史复核 FAIL 时，停止 carry 产品化与 shadow 路径；先更新墓园和机会地图，再按 P1-OSS-006(kill/pivot条件) 重排。
4. carry 历史复核 PASS 也不能跳过 DATA_CONTRACT、策略规格、风控守门和对账审计。
5. **实盘硬门（A3审计）：** 实时风控+账本+对账+对手方合规全部建成验收之前，不得用真实资金，不论 carry 结论如何。
6. A-1 路径 B 只被动积累数据，不与当前主线争夺 WIP；到 readiness gate 前不重启实验。
7. TSMOM universe 扩展保持 🟡调整/暂缓；不进入当前 sprint。
8. Phase 2/3 的所有真实资金、阶段跨越和重大架构任务均等待 Founder D 级，不因前置任务完成自动启动。

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 | 触发原因 |
|---|---|---|---|---|
| v1.0 | 2026-06-15 | Codex | 建立 Phase 0-3 × 9 能力域的详细 WBS；真实回填已完成、进行中、待办、调整、废弃与阻塞历史；确立单一任务权威和维护纪律 | Founder 要求后续日常推进只看本表即可知道已做/未做/下一步 |
| v1.1 | 2026-06-20 | Claude | 折入四棱镜审计+OSS调研结论：新增工程借力层(P1-OSS-001~006)；P1-PLAT-002 调整为折入 Freqtrade 范围；关键路径加 build-vs-buy 硬关卡和实盘硬门；当前焦点更新；删除 2026-06-19 实时变更记录段落（已正式转为任务行）；§1c 历史叙事已清空（无悬空建议只留4个D级项） | 四棱镜审计后方向重校准 |
| v1.2 | 2026-06-20 | Claude | P1-RES-030状态修正🟢→🔴阻塞（双重阻塞）；新增P1-RES-030A(8个carry数据采购任务)；P1-OSS-005升为OSS最高优先并去掉不必要的"Founder D"标注（成本盒内可自决）；关键路径修正（DATA_CONTRACT在carry可行性之后不是之前）；新增P1-GOV-006/007/008（Claude Skills/hook/daemon）；修正循环依赖问题 | 全计划主理人盘点 |

