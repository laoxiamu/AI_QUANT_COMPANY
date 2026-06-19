# 全项目独立审计·共用章程（AUDIT_CHARTER）

**性质：** 多棱镜独立审计 panel 的共用规则。每个棱镜（A1-A4）是一个独立 Codex 审计员，**互不参考彼此结论**，从指定专业视角独立审全项目。
**审计哲学（铁律）：**
1. **质疑根本，不限于现有内容**：可挑战公司方向/方法/架构/计划本身；发现现有方案有更优替代，必须提出并论证。
2. **独立批判，不护短不迎合**：这是红队审计，找问题和盲点，不是确认现状。对 Claude(CTO) 已做的决策/设计同样开炮。
3. **每条发现给：问题 + 严重度(致命/重大/一般) + 证据(指文件/决策) + 更优方案建议 + 谁该决策(Founder D级/CTO/可自动)**。
4. **专门找盲点**：明说"这个项目/CTO 没在看什么、哪些假设没被质疑过"。
5. 结论分"立即改/下阶段改/记录待议"。不堆砌，按信息增益排序。

**先读（建立真实认知，勿凭空评）：** `01_MEMORY_CORE/CURRENT_STATE.md`、`DECISION_LOG.md`(扫索引+近期)、`PROJECT_CONTEXT.md`、`00_PROJECT_MANAGEMENT/COMPANY_BUILD_MASTERPLAN_v1.md`、`PROJECT_TASK_PLAN.md`、`OPPORTUNITY_MAP_STATUS.md`、`06_RESEARCH/GRAVEYARD_INDEX.md`、`OPERATING_MODEL_DESIGN_v2.md`、`05_TECH_DESIGN/`、`06_RESEARCH/PREREGISTRATIONS/`、`04_AI_TEAM/CODEX_TASKS/REPORT_*`。**禁读 HOLDOUT。不改任何文件**（只产出自己的审计报告）。

**约束背景（审计须据此现实，不要假设大团队大预算）：** 1 Founder(非技术,1h/天,只批D级) + Claude(CTO,额度紧) + Codex(额度足) + 本金上限3万 + 月预算~1000元 + 6个月时间盒。当前:A-1独立回弹已死,carry在历史可行性复核,TSMOM仅Baseline,交易系统/实时风控/监控/账务=未建。

**输出：** 各棱镜写独立报告到 `00_PROJECT_MANAGEMENT/STAGE_AUDITS/AUDIT_2026-06-15_[棱镜号].md`，并写 `04_AI_TEAM/TASK_INBOX/AUDIT_[棱镜号]_DONE.json`(task_id,verdict_summary,top_findings,better_alternatives,notes)。
