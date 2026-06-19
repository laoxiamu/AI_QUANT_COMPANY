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

## 当前焦点

- **唯一执行主线：** `P1-RES-030`，按 carry v4 冻结规格执行历史 `FEASIBILITY-LOCK`；Claude 验收后由 `P1-RES-031` 给二元结论。
- **本轮建设任务：** `P1-PMO-010` 已完成，等待 `P0-STR-005` / `P1-PMO-011` 的 Founder D 级确认。
- **被动并行：** `P1-RES-014` 持续积累真实强平数据，不占当前研究 WIP。
- **明确暂缓：** `P1-RES-008` TSMOM universe 扩展按 DEC-075 保持调整态，不进入当前 sprint。

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
| P1-RES-030 | 按 carry v4 冻结规格执行历史 `FEASIBILITY-LOCK` | 🟢进行中 | Codex；Claude验收 | P1-RES-019/028/029 | 先完成 v4 差异矩阵、输入 manifest、历史 bracket/事件数据可得性检查；再运行二元判决 | carry v4；脚手架报告 |
| P1-RES-031 | carry 结果独立验收并更新机会地图/墓园 | ⚪待办 | Claude；独立 Reviewer | P1-RES-030 | PASS→观察级并冻结 OI 模块去留；FAIL→墓园且不得包装弱 edge | `OPPORTUNITY_MAP_STATUS.md`；`GRAVEYARD_INDEX.md` |
| P1-RES-032 | carry 前向 SHADOW 启动准备 | ⚪待办 | Claude；Codex | P1-RES-031=PASS | 冻结 T0、manifest、运行版本和数据完整性监控；不得回填 | carry v4 §9 |
| P1-RES-033 | carry 18-24 月前向 SHADOW 一次性确认 | ⚪待办 | 自动系统；Claude/Reviewer | P1-RES-032、最小 paper 平台 | 按月只做运维检查，不看确认 p 值；到预定门一次检验 | carry v4 §9 |

### 策略产品化

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-PROD-001 | 将 `OPERATING_MODEL_DESIGN_v2` 重定位为策略交付生命周期 SOP | ✅完成 | Codex；Claude验收 | P1-PMO-010 | 后续只管 R-S-E，不承担公司总模型 | `00_PROJECT_MANAGEMENT/OPERATING_MODEL_DESIGN_v2.md` |
| P1-PROD-002 | 建立策略 SPEC 模板 | 🔵新增 | Claude；Codex DR | P1-PROD-001 | 以 carry 为首个真实实例，不先造空模板体系 | SOP 循环 S |
| P1-PROD-003 | 建立策略 ATD 验收测试定义模板 | 🔵新增 | Claude；Codex DR | P1-PROD-002 | 明确已知输入、期望持仓/PnL/风控输出 | SOP S3 |
| P1-PROD-004 | carry 策略 SPEC v1 | ⚪待办 | Claude；Codex DR | P1-RES-031=PASS | 逐条翻译 v4，不允许改变机制、成本、资本和事件规则 | `06_RESEARCH/STRATEGY_SPECS/`（待建） |
| P1-PROD-005 | carry 成本/仓位/账务模型规格 | ⚪待办 | Claude；Codex | P1-PROD-004 | 与历史引擎逐项对账，手算样例 | carry v4 §2-§6 |
| P1-PROD-006 | carry ATD v1 | ⚪待办 | Claude；Codex | P1-PROD-004/005 | 至少覆盖 funding、负 funding、再平衡、OI 减仓、buffer breach、liquidation、事件退出、对账 | SOP S3 |
| P1-PROD-007 | carry 接入最小平台接口契约 | ⚪待办 | Claude；Codex DR | P1-PROD-004、P1-PLAT-008 | 不建立策略私有订单/状态/账务旁路 | `05_TECH_DESIGN/06_MODULE_INTERFACE.md`（待建） |

### 交易平台与数据基础设施

| ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接 |
|---|---|---|---|---|---|---|
| P1-PLAT-001 | Phase 2 公司组织、系统架构、执行流和模块设计 E1-E4 | ✅完成 | Codex；Claude验收 | DEC-071/072 | 作为草图输入，不等于平台已建 | `05_TECH_DESIGN/01_COMPANY_ORG.md`~`04_MODULE_DESIGN.md` |
| P1-PLAT-002 | 冻结最小 paper 平台范围与非目标 | ⚪待办 | Claude；Founder D 如涉及重大架构 | P0-STR-005、P1-RES-031 | 只建 carry shadow 必需能力；无 UI、多所、RL | `05_TECH_DESIGN/02_SYSTEM_ARCHITECTURE.md` |
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

1. **当前主路径：** `P1-RES-030 -> P1-RES-031 -> P1-PROD-004~007 -> P1-PLAT/RISK/OPS/ACC -> P2-DEP-001 -> P2-DEP-002`。
2. carry 历史复核 FAIL 时，停止 carry 产品化与 shadow 路径；先更新墓园和机会地图，再由 Claude 重排 A-4/其他机制。
3. carry 历史复核 PASS 也不能跳过策略规格、paper 平台、风控、监控和账务。
4. A-1 路径 B 只被动积累数据，不与当前 carry 主线争夺 WIP；到 readiness gate 前不重启实验。
5. TSMOM universe 扩展保持 🟡调整/暂缓；除非 Founder 重新确认优先级且补齐数据适用性，不进入当前 sprint。
6. Phase 2/3 的所有真实资金、阶段跨越和重大架构任务均等待 Founder D 级，不因前置任务完成自动启动。

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 | 触发原因 |
|---|---|---|---|---|
| v1.0 | 2026-06-15 | Codex | 建立 Phase 0-3 × 9 能力域的详细 WBS；真实回填已完成、进行中、待办、调整、废弃与阻塞历史；确立单一任务权威和维护纪律 | Founder 要求后续日常推进只看本表即可知道已做/未做/下一步 |

---
## 实时变更记录 — 2026-06-19（审计与根因后，CTO 当轮回写）

**⛔ 已停止（止额度血）**
- `codex-task-inbox-checker`（每15分钟全天候跑=每天~96次Claude运行烧Founder额度，6/11起）→ **2026-06-19 DISABLED**。
- `ai-quant-weekly-monitor`（每周一）→ DISABLED（项目重构期暂停）。月度审计保留待Founder定。

**🟡 调整（待Founder D级确认）**
- 系统范围：从"自建重型五层"→ **借力(CCXT/Freqtrade/数据商)的最小纸面→小额实盘闭环**（A2审计）。
- 研究严谨度：carry 从"18-24月前向shadow"→ **几月纸面+小额真钱+硬风控**，严谨度对齐3万在险资金（A1/A4审计）。
- 目标重定：6个月=**止损时间盒(找edge)**，非系统工期；近1-2月成功标准=借力跑通最小真钱闭环+低成本验证≥1个可部署edge，否则pivot（A4审计）。

**🔵 新增任务（审计产出，待排期）**
- 采用 CCXT/Freqtrade build-vs-buy（RESEARCH-OSS 调研中）；强平/funding/OI 改用数据商(Coinglass/CoinAPI)替代自建采集器。
- 建 `DATA_CONTRACT.yaml`+校验（实盘前数据质量硬门，A2）。
- 实盘前硬门：实时风控/账本/对账/对手方合规必须先建（A3 判"有条件不可实盘"）。
- 建《能力/环境登记表》+《假设登记表》；红队审计制度化、周期化（根因修复）。

**🟢 进行中**：RESEARCH-OSS(工具调研)、AUDIT-A1重派(前次4h前网络死)。**🔴 阻塞**：carry历史可行性复核(custodian需主会话写项目外密钥,Codex沙箱做不了)。

**根因（半个月误投）**：埋头执行不质疑框架 + 无build-vs-buy/退步检查点 + 拿Founder当唯一退步机制；超长线程与"只记执行不记假设"的文件架构放大之。5条结构修复见上"🔵/根因"。
