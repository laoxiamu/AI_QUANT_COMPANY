# REPORT_GOV_TOOLING_EVAL_CODEX_20260621

**任务：** 治理工具链联合评估（独立反审 Claude 草案）  
**日期：** 2026-06-21  
**性质：** 只产报告；不写代码、不建工具、不碰 Holdout、不耗失败计数。  
**被审对象：** `00_PROJECT_MANAGEMENT/STAGE_AUDITS/GOVERNANCE_TOOLING_EVAL_20260621.md`

## 执行前自查

| 问题 | 结论 |
|---|---|
| 任务在验证什么机制？ | 验证“过去失败是否应靠更多工具解决，还是靠轻治理/纪律/状态一致性解决”。 |
| 验收标准是否可量化？ | 是：逐条回答 6 个必答问题，给出总裁决和最高信息增益下一步。 |
| 有无更便宜等效实现？ | 有且已采用：只读指定文档并写反审报告，不建任何治理系统。 |
| 是否触碰禁止项？ | 否：未读 Holdout，未改预登记，未跑回测，未建工具，未改 Claude 独占权威文件。 |

## 1. Claude 对“过去失败根因”的归类是否漏项或错判

**结论：大方向成立，但有两个漏项，需要从“纪律问题”细分为“可机器检查的轻流程缺口”。**

Claude 草案把主要失败归为“方向纪律 + 状态一致性 + 断档”，这一点基本正确。DEC-057 明确项目最严重问题是 AI 把“执行任务书”置于“判断任务是否值得执行”之前，导致局部修补搜索；这不是缺 Backstage/Spec Kit/Discord，而是角色责任和研究顺序铁律缺失。DEC-082 也已把研究重新收敛为 B0-B4 单变量序列，说明方向错的解药是机制门和 WIP=1，不是自动化吞吐。

但 Claude 草案漏了两类真实事故：

1. **DEC 传播/权威正文不一致。** P0-C 报告记录：`state_check.py` 已能抓到 `DECISION_LOG` 中 DEC-080 旧“月化30%目标”正向语境，说明问题不是泛泛“状态不一致”，而是“决策更新后没有硬检查传播到摘要/状态/正文”。这需要小脚本/清单强化，不需要重型控制面。
2. **跨文件规则冲突。** P0-C 报告列出 `AGENTS.md`、`SYSTEM_RULES.md`、`AGENT_REGISTRY.md` 等冲突，例如 Codex 是否可 commit、项目治理状态到底以 DB 还是文件为权威。根因不是缺项目管理 SaaS，而是权威层级没有被机器化校验和裁决传播。

另一个边缘项：定时任务事故不能只写成“Codex nohup 优先”就结束。真实根因是“夜间关键路径放在不可靠 scheduler 上”，当前绕过可接受，但若未来进入生产运行，应该升级为运行承载问题，而不是治理文档问题。

**是否存在“根因其实是缺某个工具/流程”的事故？存在，但都是轻流程/小工具级，不是重型工具级。** 典型就是 `state_check` 真非零、DEC 传播检查、只读任务事件日志。没有证据表明过去失败会被 Spec Kit 全量、Backstage、DevLake、Plane、Web/Discord 控制面直接防住。

## 2. 分层模型 A/B/C/D 是否成立

**结论：模型成立，但 C 层需要拆成“重型系统 DEFER”和“低成本机制可吸收”。Claude 草案有轻微全 DEFER 偏见。**

我认可 A/B/C/D 的主结构：

- A 层 Claude/Memory Core/state_check 治方向、状态、断档，是当前核心。
- B 层 Codex/Superpowers/AGENTS.md 治执行质量，是低成本辅助。
- C 层完整 Orchestrator、Web、Discord、Backstage、DevLake、Plane、Spec Kit 全量等，当前 edge=0、WIP=1，提前上会放大风险B。
- D 层 ADR-001 + C4 L1 是小缺口。

需要修改的是：**C 层里“只读状态/事件日志骨架”不应继续按完整 Orchestrator 一起 DEFER。** DEC-083 已把它裁成 SQLite append-only 事件库、只读展示、零自动派单、零控制面。它直接对应 Founder 关切的“断档/记忆缺失/任务状态无据可查”，成本低，且不会扩大执行权限。这个不是重型工具，是对 TASK_INBOX/RUN_LOG 的可恢复状态补丁。

另一个值得提前的是 **DEC 变更传播强化**。它直接防本轮已发生的 DEC-080 传播遗漏，比任何外部工具更对症。

不建议提前的 C 层工具：

- **Spec Kit 全量/试点：** 当前主要瓶颈是研究机制和权威一致性，不是工程需求规格遗漏。若试点，也应等 B1/B2 后选择非 Alpha、非交易、可删除的小工程功能。
- **Web/Discord 控制面：** 当前没有多人协作规模，也没有 Founder 时间被实测为瓶颈。
- **Backstage/DevLake/Plane/Task Master/BMAD：** 会形成第二任务源、第二生命周期或指标剧场，无法直接防 DEC-057/082 所描述的方向错。

## 3. Claude 推荐中哪些该砍/该降

**结论：保留 A+B，但要明确“工具从属权威文件”，并把若干项降级为按需。**

建议降级/边界化：

1. **Superpowers/Skills 只能作为 Codex 个人执行纪律，不作为项目权威。** 项目权威仍是 DECISION_LOG、CURRENT_STATE、任务书、报告和 TASK_INBOX；skill 输出不得绕过 Claude 验收。
2. **Claude 子代理按需启用，不列为核心治理依赖。** 子代理适合隔离复核，但若上下文包不准，也会制造第二套判断来源。
3. **state_check 不应膨胀成“语义真理机”。** 它应只检查确定性硬冲突、坏串、传播位、路径和退出码；专业判断仍归 Claude/Founder。
4. **Spec Kit 从“保留待初始化”降为“观察/后置试点”。** DEC-082/083 已事实上把它放入 DEFER；不要在当前阶段初始化进主流程。
5. **C4 只做 L1 当前态，不做全套。** C4 L2/Container/Deployment 现在会诱导架构扩写，和 edge=0 阶段不匹配。

Claude 草案里“保留 A+B、C 维持 DEFER、D 择机补”的方向正确，但“D 择机”应改为“D 中 ADR-001 + C4 L1 已按 DEC-083 进入 P0-C+ 封顶包；完整 C4 仍 DEFER”。

## 4. ADR-001 + C4 L1 现在补值不值

**结论：值，且不应再等；但必须封顶为各一页，并且不阻塞 B1。**

理由：

- ADR-001 记录的是技术架构选择：“edge=0 阶段不建完整自动编排/控制面，维持文件式 handoff + 只读状态骨架”。这能防未来再次把“不上工具”的理由遗忘，属于反治理膨胀工具。
- C4 L1 只画当前系统上下文，标明 CURRENT/PLANNED/DEPRECATED，能防“系统在哪、谁负责什么、哪些只是草图”的认知断档。
- 两者成本低，且 DEC-083 已限定在 P0-C+ 一次性包内，不应滚动扩写。

边界：

- 不写业务方向 ADR，业务/研究口径留在 DEC。
- 不画 C4 全套，不画未来态冒充当前态。
- 不因 ADR/C4 暂停 B1；治理包做完即停。

## 5. 总裁决

**ACCEPT-with-MODIFY。**

具体修改建议：

1. Claude 草案 §一新增漏项：DEC 传播/权威正文不一致、跨文件规则冲突、夜间 scheduler 可靠性边界。
2. §二 C 层拆分：
   - C-heavy：完整 Orchestrator、Web、Discord、Backstage、DevLake、Plane、Spec Kit 全量、七维路由、九域记分卡，继续 DEFER。
   - C-light：只读状态/事件日志骨架、DEC 传播强化，进入 P0-C+ 封顶包。
3. §二 D 层改为：ADR-001 + C4 L1 现在补，仍封顶各一页；完整 C4 DEFER。
4. §三推荐裁决改为：保留 A+B；C-heavy DEFER；C-light + D 按 DEC-083 做一次性 P0-C+；完成后停止治理建设，回到 B1。
5. 明确 Spec Kit 状态：不初始化进主流程，除非一条 edge 过 B2 或出现独立工程功能试点需求。

## 6. 最高信息增益的下一步

**治理动作里信息增益最高的是完成 P0-C+ 的 DEC 变更传播强化（`state_check --changelog`/传播位检查）；若问项目总体下一步，则不要再加工具，转去跑 B1-KILLCARD。**

## 边界与完成状态

- 未修改 `00_PROJECT_MANAGEMENT/`、`01_MEMORY_CORE/`、`AGENTS.md`、`CLAUDE.md` 等权威文件。
- 未建 ADR/C4/Orchestrator；本报告只判断是否值得。
- 未读 Holdout、未跑回测、未触碰研究数据。
- 本报告可作为 Claude 收敛 DEC 的反审输入。
