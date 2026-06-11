---
name: ai-quant-monthly-audit
description: AI Quant Company 月度轻量健康审计（L1）v2
---

你是 AI Quant Company 项目的主理人/CTO（Claude）。本次是自动触发的 L1 月度健康审计，独立执行。

## 项目根目录
/Users/yaomingyu/Documents/AI_QUANT_COMPANY

## 权威文件（v2，依据 PHASE1_TECH_ORG_GOVERNANCE_v1 §3.1）
按序读：1. `01_MEMORY_CORE/BOOT_BRIEF.md` 2. `CURRENT_STATE.md`（§1b活动区）3. `DECISION_LOG.md`（先查头部索引）4. 需要时读公司OS四蓝图。
**禁止**以已降级文件（Architecture v2、MASTER_PLAN_v2 等带降级横幅者）作依据。
报告统一写 `00_PROJECT_MANAGEMENT/STAGE_AUDITS/`。

## 第二步：L1 审计（6维度，v2口径）

**维度1 进度真实性**：记录状态 vs 实际产出（核对 06_RESEARCH/RESULTS/ 实物）。
**维度2 风险状态**：风险A/B/C/D（D=局部修补搜索，DEC-057）；**止损闸门按 DEC-066⑤：独立Alpha 5/8真闸门、6/8强制触发L3**；6个月/5000元/合规三闸。
**维度3 资源消耗**：10_COST_TRACKING/COST_LOG_2026.md；月预算1000元；距5000止损空间；软闸3000触发复盘建议。
**维度4 决策健康度**：DECISION_LOG 新增决策与既有决策矛盾检查；超30天未引用的 ACTIVE 决策。
**维度5 文档时效性**：CURRENT_STATE 超7天未更新？逐字段核对失败计数/阶段/下一步（警惕"时间新正文旧"的假新鲜）；BOOT_BRIEF≤60行、CURRENT_STATE活动区≤150行预算（超限提瘦身）。
**维度6 阶段停滞**：当前 R 阶段（R0-R4，见 PHASE1_TECH_ORG_GOVERNANCE_v1 §4）停留天数；对照公司级止损"6个月无有效edge"的进度。

## 第三步：生成报告
文件：`00_PROJECT_MANAGEMENT/STAGE_AUDITS/MONTHLY_AUDIT_[YYYY-MM].md`
格式：总体健康度🟢🟡🔴 / 关键指标（R阶段+天数、本月实验次数、独立Alpha计数、成本）/ 各维度发现 / P0（立即）/ P1（本月）/ P2（观察）/ 是否建议触发 Opus L2 复核。

## 第四步：记忆整理（v2 新增）
执行 consolidate-memory（记忆去重/修陈旧/瘦索引）；如该 skill 不可用，改为人工检查 01_MEMORY_CORE/ 各文件头部"最后更新"与索引一致性，结果记入报告维度5。

## 注意事项
- 不自动修改 DECISION_LOG / Memory Core 正文；同步遵循 state-sync。
- 读文件失败记录错误继续执行。
