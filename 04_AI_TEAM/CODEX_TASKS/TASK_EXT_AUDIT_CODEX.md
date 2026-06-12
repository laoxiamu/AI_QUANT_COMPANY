# TASK_EXT_AUDIT_CODEX —— 外部多专家深度审计（Codex 独立版）

**发包：** Claude 2026-06-11 ｜ **要求：** 以最高推理强度执行。你是**外部独立审计委员会**（项目管理/量化产品/系统架构/AI治理/工作流组织/加密量化投研买方/数据工程/风控/决策科学 九专家逐一切换视角），**不隶属本项目，结论不得迎合项目现有叙事**。与另一份 Claude 侧审计互为独立对照——不要试图猜测或对齐对方结论。

## 方法论（防锚定，严格按序）
1. 先只读 CLAUDE.md + 00_PROJECT_MANAGEMENT/COMPANY_STRATEGY_PRODUCT_v1.md，在读其他材料前写下"零锚定预期"（若从零设计这家公司你会怎么做），存入报告附录A。
2. 再读：01_MEMORY_CORE/BOOT_BRIEF.md、CURRENT_STATE.md、DECISION_LOG.md（先索引，重点DEC-063~068）、四蓝图（OPERATING_MODEL_DESIGN_v1/PHASE1_RESEARCH_RISK_BLUEPRINT_v1/PHASE1_TECH_ORG_GOVERNANCE_v1）、06_RESEARCH/RESEARCH_PROTOCOL_v1.md+v1.3_ADDENDUM、GRAVEYARD_INDEX、RESULTS下（20260611_a2_event_study/20260610_tsmom_recheck/20260611_event_census/20260611_data_inventory）、STAGE_AUDITS下（L2_AUDIT_OS_FREEZE_2026-06-10/L3_EMERGENCY_2026-06-11）、TOOL_ROUTING.md、04_AI_TEAM/（AGENTS.md/CODEX_DIRECT_CALL_RUNBOOK/LOW_TIER_TASKS/）。
3. 对比预期vs现实，差异逐条判定"项目错 or 外部预期不适用本约束"，给理由。

## 必答核心题（DEC-068①）
A-2"拥挤反转"首测即死且方向整体相反（极端拥挤=延续）——这是否暴露**方向/方法本身的错误**？机制优先范式执行对不对？两主线（A-1清算级联/A-2）选择该不该修？动量vs反转证据如何重塑机会地图？**剩2条独立实验命该怎么花**？

## 覆盖维度
整体方向｜研究方法｜方案设计｜R0-R4路线与执行手册｜技术方案与数据流｜组织（Founder+Claude+Codex+低模型四层）｜系统架构｜文件/文档治理｜工具与配置｜记忆工程｜上下文工程｜agent编排（直调/子代理/定时任务）｜工作流｜功能模块｜风控两层资本｜成本runway（10_COST_TRACKING/COST_LOG_2026.md）｜自选盲区。

## 硬性要求
≥5处指名道姓挑战现有共识（哪个DEC/哪份蓝图哪个论断）并给替代方案；P0/P1/P2分级且每条给可执行改法；禁"总体良好"式开头；引用外部知识标注证据等级。

## 输出与边界
唯一输出：`00_PROJECT_MANAGEMENT/STAGE_AUDITS/EXTERNAL_DEEP_AUDIT_CODEX_2026-06-12.md`（执行摘要≤15行→九专家发现→P0/P1/P2→五处共识挑战→剩2命花法→建议工具清单→附录A）。
**禁止**：修改任何既有文件；运行实验/回测；读 06_RESEARCH/DATA/HOLDOUT/；git commit（由 Claude 验收后统一提交）。
