# BUILD-PROJECT-PLAN-FULL：建《公司建设总图》+《项目任务计划书》（详细完整版）

**Founder 明确要求：** 当前阶段**放开"轻量"约束，要详细完整**。目标=有了这两份，后续推进只看它们就知道"哪些做了/没做/下一步"，对话中的变更/调整/新增实时记录进去。**不是为了好看的治理文档，是项目的操作骨架，必须可用、准确、反映真实当前状态。**

**依据：** `BPR_TOP_LEVEL_FRAMEWORK_REFERENCE_2026-06-15.md`（方法）+ CTO 调整意见（能力域+L1价值流，微型AI公司适配=责任帽子非组织层级）。

## 第一步（关键，别跳）：吃进项目真实现状
必须先通读并据此填真实状态，**不得生成与现实脱节的空计划**：
- `01_MEMORY_CORE/CURRENT_STATE.md`（看板+§4台账+工具链）、`DECISION_LOG.md`（DEC-001~最新）、`PROJECT_CONTEXT.md`
- `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md`、`06_RESEARCH/GRAVEYARD_INDEX.md`
- `00_PROJECT_MANAGEMENT/` 下 四蓝图/OPERATING_MODEL_DESIGN_v2/PHASE*、`05_TECH_DESIGN/` 系统设计、`06_RESEARCH/PREREGISTRATIONS/`（A-1 v1-v5+评审、carry v1-v4+评审）
- `04_AI_TEAM/CODEX_TASKS/REPORT_*`（已完成工作）
把"已完成/在建/废弃"的真实状态据此标注（例：A-1独立回弹=⛔废弃FAILED；carry=🟢进行中到v4盲审；采集器=✅已修复收数；TSMOM=Baseline定仓穷尽；监控/账务/实时风控=⚪未建）。

## 产出 1：`00_PROJECT_MANAGEMENT/COMPANY_BUILD_MASTERPLAN_v1.md`（总图·详细完整）
- **公司终态**（推荐版，标"待Founder D级确认"）：这家微型量化公司最终是什么、能持续做什么。
- **能力地图**：9 能力域（战略资本边界/Alpha研究/策略产品化/交易平台与数据/实时风控与资本保护/交易运营监控事件响应/资本账务绩效归因/治理知识审计/项目组合交付）。**每个域详写**：职责范围、当前成熟度(空白/草图/部分/成熟)、已有什么、缺什么、关键风险。
- **L1 端到端价值流**（7条：机会到证据/证据到部署/信号到结算/异常到恢复/绩效到配置/决策到交付/结果到知识）。每条：起点、终点、结果、参与能力域、单一Accountable(责任帽子)、关键指标、**当前是否激活**(无实盘→后4条标"未激活·未来阶段")。
- **能力域 × 价值流 缺口矩阵**：标"无人负责/重复建/关键依赖"。
- **阶段划分 Phase 0/1/2/3**（推荐版待Founder确认）：每阶段终态/出口条件/跨域关键路径。
- **各能力域成熟度热力**一览。

## 产出 2：`00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md`（项目任务计划书·详细·单一活来源）
这是 Founder 日常驱动项目看的**唯一详细任务来源**。要求：
- **按 阶段 × 能力域(/价值流) 分组，WBS 拆到具体可执行任务**（粗到能力建设里程碑、细到当前 sprint 的具体活）。
- 每条任务列：`ID | 任务 | 状态 | 负责人 | 依赖 | 下一步 | 产物/证据链接`。
- **状态taxonomy（统一图例）**：✅完成 / 🟢进行中 / ⚪待办 / 🔵新增 / 🟡调整 / ⛔废弃(→墓园/原因) / 🔴阻塞(→阻塞源)。
- 顶部写**维护纪律**：对话中任何变更/调整/新增/决策→当轮写入本表；本表是任务单一权威，`CURRENT_STATE §4` 退化为"当前焦点+指向本表的指针"(不重复维护，防双账本)；废弃任务保留行并标⛔+原因(不删，可追溯)。
- **真实回填**：把已完成的 A-1全线/DEC-075/E2/采集器修复/carry迭代 等标✅或对应态；把未建的 交易平台/实时风控系统/监控/账务/运营工作流 列为⚪待办并挂阶段；当前🟢=carry可行性复核线 + 公司总图建设。

## 产出 3：重定位 `OPERATING_MODEL_DESIGN_v2.md`
头部加重定位声明：状态改为 `ACTIVE-AS-SOP / 不再作公司运营模型`；改称"策略交付生命周期 SOP"；循环E仅"策略接入既有平台"非"从零建系统"；保留原内容+CHANGELOG。

## 第二步：更新 CURRENT_STATE §4 → 改为"当前焦点 + 指向 PROJECT_TASK_PLAN.md"的指针（不再重复全量任务）；更新 BOOT_BRIEF 指针。

## 铁律：不改 DECISION_LOG/预登记/研究结论；不读 HOLDOUT；总图终态/阶段标"待Founder D级"。详细完整优先于简短。完成写 `04_AI_TEAM/TASK_INBOX/BUILD_PROJECT_PLAN_DONE.json`(task_id=BUILD_PROJECT_PLAN,outputs,notes=终态/阶段推荐摘要+待Founder确认点+计划书任务总数)。可 commit。
