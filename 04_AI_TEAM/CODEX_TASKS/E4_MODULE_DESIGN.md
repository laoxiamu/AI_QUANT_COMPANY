# E4：系统模块设计文档

**任务类型：** 文档创建（中等复杂度）
**输出：** `05_TECH_DESIGN/04_MODULE_DESIGN.md`
**验收：** 文件存在，包含6个模块（A-F）完整说明，每个模块有组件清单和建设状态

---

## 背景

Phase 2 系统蓝图重构第4张图：具体要建设哪些模块。

参考来源（只做对比，不直接复制）：
- Codex V5研究报告 §6 系统模块设计（`04_AI_TEAM/CODEX_TASKS/REPORT_V5_DESIGN_EXTRACTION_POST_0510.md` line 189+）
- 当前Phase 2蓝图（已有内容参考）：`05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md` §五、§六
- 当前DEC记录：`01_MEMORY_CORE/DECISION_LOG.md`（风控规则来源）

重要：以下规格是独立设计，历史文件只作对比。

---

## 输出内容规格

文件路径：`05_TECH_DESIGN/04_MODULE_DESIGN.md`

### 必须包含的内容：

**1. 文件头**
```
# 系统模块设计 v1.0
状态：DRAFT（随Phase 1研究进展更新）
更新：[日期] Claude（主理人/CTO）
原则：模块边界清晰，禁止跨层直接调用；执行模块禁止AI自治
```

**2. 六个模块（A-F）**

每个模块格式：
```
## 模块X：[名称]
职责：[一句话]
组件：[列表]
依赖：[依赖哪个模块]
当前状态：[✅已建设/⚠️设计中/❌未建设]
负责方：[Claude规划/Codex实现/确定性程序]
```

**模块A：PMO / Project OS**（已建设）
- 职责：项目状态管理、决策记录、文档体系、任务追踪
- 组件：`CURRENT_STATE.md`（含§1b活动工作区）、`DECISION_LOG.md`、`BOOT_BRIEF.md`、`OPPORTUNITY_MAP_STATUS.md`、`GRAVEYARD_INDEX.md`（含正向知识库）、`CODEX_TASKS/` 任务规格库、`STATE_SYNC_CHECKLIST.md`
- 依赖：无（基础层）
- 状态：✅ 运行中
- 负责方：Claude 维护内容，Codex 维护文件

**模块B：AI Team 协作层**（运行中）
- 职责：Claude↔Codex 工作协议、任务交接、Review机制
- 组件：`CLAUDE.md v2.4`（主理人规则）、`AGENTS.md`（Codex规则）、Codex 直调配方（`CODEX_DIRECT_CALL_RUNBOOK.md`）、任务规格模板、验收标准模板
- 依赖：A
- 状态：✅ 运行中
- 负责方：Claude 规则设计

**模块C：Knowledge System（知识管理）**（部分建设）
- 职责：原始资料→提炼→知识库→Claude主脑上下文的流水线，防止历史文件直接污染决策
- 组件：`03_RAW_INBOX/`（原始资料隔离区）、`GRAVEYARD_INDEX.md`（失败+正向知识）、研究报告归档（`06_RESEARCH/RESULTS/`）、知识状态标注规则（Active/Deprecated/Superseded）
- 缺口（待建）：半自动提炼流水线（Inbox→去重→冲突检测→Claude主脑可读摘要）
- 依赖：A
- 状态：⚠️ 部分建设
- 负责方：Claude 规则 + Codex 自动化

**模块D：Research Platform（研究平台）**（运行中）
- 职责：数据采集、回测、统计验证、报告生成
- 组件：
  - 数据层：Binance OHLCV历史（`06_RESEARCH/DATA/FUTURES/`）、强平数据（VM）、Funding Rate（FUNDING_8H）、扩展universe（`FUTURES_EXPANDED/`，D1任务中）
  - 回测层：VectorBT引擎、Walk-Forward 3段切分、四件套+第五件验收
  - 验证层：预登记文档（`06_RESEARCH/PREREGISTRATIONS/`）、墓园索引
  - 报告层：`06_RESEARCH/RESULTS/` 研究结果归档
- 当前在途：D1（数据下载）、D2（TSMOM扩展回测，等D1）、D3（A-1预登记，Codex执行）
- 状态：✅ 核心运行中
- 负责方：Claude 研究设计 + Codex 跑批

**模块E：Execution System（交易执行系统）**（未建设）
- 职责：生产级 24小时自动交易执行
- 组件：
  - 信号引擎：TSMOM信号/A-1事件检测/Carry状态（来自模块D的策略代码化）
  - Decision Gateway：唯一下单权；硬风控规则硬编码；AI无法绕过
  - Risk Engine：单日-2%熔断/-20%总回撤/事件窗禁交易/极端波动熔断/OI骤降暂停（DEC-015/063/069）
  - Order Executor：限价单优先/市价单只用于熔断平仓/指数退避重连
  - Position Registry：Position Journal（事件溯源，每笔持仓完整事件日志）、Risk Timestamp（每个持仓的最后风控检查时间）
  - Reconciliation：三方对账（Binance交易所/PostgreSQL/runtime），每1H比对，不一致告警
  - Notification：告警推送（持仓同步失败/亏损预警/A-1事件/服务重启）
- AI Pre-Execution Analyst 接入点：Decision Gateway 执行前可调用 Claude API，输出 approve/caution/no-trade；最终裁决权仍在 Gateway 规则
- 状态：❌ 未建设（Phase 2 主要任务）
- 负责方：Codex 实现 + Claude 架构设计

**模块F：Cost & Governance（成本与治理）**（部分建设）
- 职责：成本监控、AI治理、风险预警
- 组件：
  - 成本追踪：AI token成本（Claude/Codex）、服务器/代理费用、交易成本（手续费/滑点/funding）、ROI看板
  - 治理规则：`CLAUDE.md v2.4`规则7/8/风险E、反迎合规则、研究范式铁律
  - 风险预警：风险A-E（见CLAUDE.md），定期触发检查
- 当前成本盒：5000元，已用871.93元
- 状态：⚠️ 部分建设（成本记录有，自动化未建）
- 负责方：Claude 规则 + Codex 自动化报表

**3. 模块依赖图**
```
A（PMO）←─── 所有模块都依赖
B（AI Team）←─── D/E/F 任务执行依赖
C（Knowledge）←─── A 提炼输出
D（Research）←─── C 知识输入，产出给 E
E（Execution）←─── D 策略代码化，B AI分析接入
F（Governance）←─── 所有模块监控对象
```

**4. Phase 2 建设优先级**
- P0（阻塞后续）：E 模块 Decision Gateway + Risk Engine + Position Registry
- P1（核心功能）：E 模块 Signal Engine + Order Executor + Reconciliation
- P2（质量提升）：E 模块 AI Pre-Execution Analyst 接入 + Track B 日报自动化
- P3（完善）：C 模块知识提炼流水线 + F 模块成本自动化

---

## 格式要求

- 不超过 120 行（6个模块，每个~15行）
- 状态用 ✅/⚠️/❌ 标注
- 不修改任何 `01_MEMORY_CORE/` 权威文件
- 不触碰 Holdout 数据
- 模块E的风控参数必须从 `01_MEMORY_CORE/DECISION_LOG.md`（DEC-015/063/069）读取，不自行发明
