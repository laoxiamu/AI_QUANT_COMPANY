# 系统模块设计 v1.0
状态：DRAFT（随Phase 1研究进展更新）
更新：2026-06-14 Claude（主理人/CTO）
原则：模块边界清晰，禁止跨层直接调用；执行模块禁止AI自治

---

## 模块A：PMO / Project OS
职责：项目状态管理、决策记录、文档体系、任务追踪。
组件：
- `CURRENT_STATE.md`（含§1b活动工作区）
- `DECISION_LOG.md`、`BOOT_BRIEF.md`、`STATE_SYNC_CHECKLIST.md`
- `OPPORTUNITY_MAP_STATUS.md`
- `GRAVEYARD_INDEX.md`（含正向知识库）
- `CODEX_TASKS/` 任务规格库
依赖：无（基础层）
当前状态：✅ 运行中
负责方：Claude 维护内容，Codex 维护文件

## 模块B：AI Team 协作层
职责：Claude↔Codex 工作协议、任务交接、Review机制。
组件：
- `CLAUDE.md v2.4`（主理人规则）
- `AGENTS.md`（Codex规则）
- `CODEX_DIRECT_CALL_RUNBOOK.md`（Codex直调配方）
- 任务规格模板、验收标准模板
依赖：A
当前状态：✅ 运行中
负责方：Claude 规则设计

## 模块C：Knowledge System（知识管理）
职责：原始资料→提炼→知识库→Claude主脑上下文的流水线，防止历史文件直接污染决策。
组件：
- `03_RAW_INBOX/`（原始资料隔离区）
- `GRAVEYARD_INDEX.md`（失败+正向知识）
- `06_RESEARCH/RESULTS/` 研究报告归档
- 知识状态标注规则（Active / Deprecated / Superseded）
缺口（待建）：半自动提炼流水线（Inbox→去重→冲突检测→Claude主脑可读摘要）
依赖：A
当前状态：⚠️ 部分建设
负责方：Claude 规则 + Codex 自动化

## 模块D：Research Platform（研究平台）
职责：数据采集、回测、统计验证、报告生成。
组件：
- 数据层：Binance OHLCV历史（`06_RESEARCH/DATA/FUTURES/`）、强平数据（VM）、Funding Rate（`FUNDING_8H`）、扩展universe（`FUTURES_EXPANDED/`，D1任务中）
- 回测层：VectorBT引擎、Walk-Forward 3段切分、四件套+第五件验收
- 验证层：预登记文档（`06_RESEARCH/PREREGISTRATIONS/`）、墓园索引
- 报告层：`06_RESEARCH/RESULTS/` 研究结果归档
当前在途：D1（数据下载）、D2（TSMOM扩展回测，等D1）、D3（A-1预登记，Codex执行）
依赖：A、C
当前状态：✅ 核心运行中
负责方：Claude 研究设计 + Codex 跑批

## 模块E：Execution System（交易执行系统）
职责：生产级 24小时自动交易执行。
组件：
- 信号引擎：TSMOM信号、A-1事件检测、Carry状态（来自模块D的策略代码化）
- Decision Gateway：唯一下单权；硬风控规则硬编码；AI无法绕过
- Risk Engine：单日-2%熔断、-20%总回撤人工介入、事件窗禁交易、极端波动熔断、OI骤降暂停
- Order Executor：限价单优先；市价单只用于熔断平仓；指数退避重连
- Position Registry：Position Journal（事件溯源）、Risk Timestamp（每个持仓最后风控检查时间）
- Reconciliation：三方对账（Binance交易所 / PostgreSQL / runtime），每1H比对，不一致告警
- Notification：告警推送（持仓同步失败、亏损预警、A-1事件、服务重启）
风控来源说明：DEC-015确认分档亏损上限，DEC-063确认核心/围栏资本架构，DEC-069确认围栏与治理约束；具体执行参数按 `PHASE2_SYSTEM_BLUEPRINT.md` §五现行蓝图，待DEC补记后冻结。
AI Pre-Execution Analyst 接入点：Decision Gateway 执行前可调用 Claude API，输出 approve / caution / no-trade；最终裁决权仍在 Gateway 规则。
依赖：A、B、D、F
当前状态：❌ 未建设（Phase 2 主要任务）
负责方：Codex 实现 + Claude 架构设计 + 确定性程序执行

## 模块F：Cost & Governance（成本与治理）
职责：成本监控、AI治理、风险预警。
组件：
- 成本追踪：AI token成本（Claude/Codex）、服务器/代理费用、交易成本（手续费/滑点/funding）、ROI看板
- 治理规则：`CLAUDE.md v2.4` 规则7/8/风险E、反迎合规则、研究范式铁律
- 风险预警：风险A-E（见 `CLAUDE.md`），定期触发检查
当前成本盒：5000元，已用871.93元
依赖：A、B、D、E
当前状态：⚠️ 部分建设（成本记录有，自动化未建）
负责方：Claude 规则 + Codex 自动化报表

---

## 模块依赖图
```text
A（PMO）←─── 所有模块都依赖
B（AI Team）←─── D/E/F 任务执行依赖
C（Knowledge）←─── A 提炼输出
D（Research）←─── C 知识输入，产出给 E
E（Execution）←─── D 策略代码化，B AI分析接入
F（Governance）←─── 所有模块监控对象
```

## Phase 2 建设优先级
- P0（阻塞后续）：E 模块 Decision Gateway + Risk Engine + Position Registry
- P1（核心功能）：E 模块 Signal Engine + Order Executor + Reconciliation
- P2（质量提升）：E 模块 AI Pre-Execution Analyst 接入 + Track B 日报自动化
- P3（完善）：C 模块知识提炼流水线 + F 模块成本自动化
