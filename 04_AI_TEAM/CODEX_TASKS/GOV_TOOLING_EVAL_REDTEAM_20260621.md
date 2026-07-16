# Codex 任务：治理工具链联合评估（独立反审 Claude 草案）

**类型：** 治理决策反审（不写代码、不建工具、不碰 Holdout、不耗失败计数）。
**触发：** Founder 要 Claude+Codex 联合评估"Claude 治理栈 vs 工具套件，谁优/是否互补，选最优"。Founder 直觉=过去问题大半因治理没做好。
**你的角色：** 独立反审。既要挑 Claude"全 DEFER"的偏见（是否漏掉真正有用的工具），也要守风险B（防治理膨胀）。两边都不许顺。

## 必读
1. `00_PROJECT_MANAGEMENT/STAGE_AUDITS/GOVERNANCE_TOOLING_EVAL_20260621.md`（Claude 草案，被审对象）。
2. `01_MEMORY_CORE/DECISION_LOG.md` → DEC-081/082/083（治理工具栈与分档历史）、DEC-057（被动执行器修复）。
3. `AGENTS.md`、`00_PROJECT_MANAGEMENT/CODEX_SKILLS_INSTALL_LOG_2026-06-14.md`（你这侧实际在用什么）。

## 必答（逐条结论，给依据，不要泛泛）
1. **Claude 对"过去失败根因"的归类（§一）有没有漏项或错判？** 尤其：有没有哪次真实事故，根因其实是"缺某个工具/流程"而不是"纪律/轻治理不足"？
2. **分层模型（§二 A/B/C/D）是否成立？** 有没有哪个被归到 C(DEFER) 的工具，实际是低成本、能直接防我们某条历史失败、值得提前？（防 Claude 全 DEFER 偏见）
3. **反向**：Claude 推荐"保留 A+B、C 维持 DEFER、D 择机补"——其中有没有哪个其实该砍/该降，是冗余或维护负担？
4. **ADR-001 + C4 L1 现在补值不值？** 还是连这个也该等？给你判断。
5. **总裁决**：ACCEPT Claude 草案 / ACCEPT-with-MODIFY（列具体改动）/ REJECT（给替代分层）。
6. **一句话**：站在"防止我们重蹈过去"的目标上，下一步治理动作里**信息增益最高的那一个**是什么（可以是"什么都不加，去跑 B1"）。

## 交付
- 写 `04_AI_TEAM/CODEX_TASKS/REPORT_GOV_TOOLING_EVAL_CODEX_20260621.md`：逐条结论 + 总裁决 + 最高信息增益的下一步。
- 完成写 TASK_INBOX DONE.json。
- **边界**：只产报告，不改 Claude 独占权威文件，不建任何工具，不跑回测。
