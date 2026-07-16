# 治理工具链联合评估（Claude 方案 + Codex 反审）

**触发：** Founder（2026-06-21）"你那套(Memory Core/Claude Skills/state_check/子代理) vs 工具(Superpowers/Spec Kit/...)哪个好？还是互补？选最优。我一直觉得过去问题很大部分是治理没做好。"
**定时盒：** 一次评估 pass，产决策，不建任何东西；评完回到 maker+B1。**反风险B守卫：** 任何"现在多建治理"的结论必须先回答"它能防我们哪一条具体的历史失败"。
**性质：** 决策草案，待 Codex 反审收敛后升 DEC。

---

## 一、先对齐"过去真正的失败"（不是泛泛的治理不足）

| 历史失败 | 根因 | 实际解药 | 状态 |
|---|---|---|---|
| state_check 假绿灯→状态不一致 | 校验脚本漏洞 | P0-C 修 state_check（小脚本+纪律） | ✅已修 |
| 方向错（追形态/局部修补搜索） | 无机制门、被任务书牵走 | DEC-057/064/082 机制优先 + Codex红队 | ✅纪律已立 |
| 跨对话断档失忆→推倒重来 | 无持久权威+恢复点 | Memory Core（BOOT_BRIEF/CURRENT_STATE §1b/DECISION_LOG）+ 启动协议 | ✅在用且有效 |
| 被动执行器、Founder 被迫做抽象 | 角色定义缺失 | CLAUDE.md 规则7/8（专业透镜/主动议程） | ✅纪律已立 |
| 定时任务事故（跑批不可靠） | 夜间定时不稳 | Codex nohup 优先 | ✅绕过 |

**诊断结论：我们过去的失败，90% 是"方向纪律 + 状态一致性 + 断档"，解药全是轻治理+纪律，已基本到位。没有一条历史失败的根因是"缺重型工具(Spec Kit/Orchestrator/Backstage)"。**

## 二、两套东西不是竞品，是不同层（Claude 主张）

| 层 | 内容 | 治什么 | 现状/裁决 |
|---|---|---|---|
| A. 我（Claude）侧 | CLAUDE.md + Memory Core + 项目Claude Skills + state_check + 子代理 | 方向纪律/状态一致/断档恢复/研究治理 | ✅核心，保留；我可更勤用自己的 Skill |
| B. Codex 侧 | Superpowers(14 skill) + AGENTS.md | Codex 执行质量(计划/TDD/红队/收尾) | ✅已在用（红队就用了），低成本，保留 |
| C. 重型工具 | Spec Kit / Orchestrator / Web / Discord / Backstage / DevLake / Plane / 七维路由 / 记分卡 | 规模化/多人协作/自动派单吞吐/生产工程 | 🧊 DEFER（DEC-082/083）：edge=0、单人、WIP=1 用不上；上了=风险B + 放大漂移 |
| D. 小缺口 | ADR-001 + C4 L1（DEC-083 P0-C+ 说做，未落盘） | 架构决策/系统图断档 | ⚠️未做；轻(各半页)，但不得抢 B1 |

## 三、Claude 推荐裁决（待 Codex 反审）

1. **不是二选一，是互补分层**：A（我侧）治研究/状态/方向，B（Codex侧）治执行，C 是生产期才需要的，D 是小补丁。最优=保留 A+B 现状，C 维持 DEFER，D 择机一次性补。
2. **过去问题的最大杠杆不是"再加工具"，是"守研究纪律"**：先证 B1/B2 再 B3、机制优先、状态保持绿。再加治理对"防重蹈"边际收益≈0，且有膨胀风险。
3. **唯一值得现在补**：ADR-001（半页：为何 edge=0 不建编排）+ C4 L1（半页系统现状图）——防"系统在哪/为何这么定"断档。**但排在 B1 之后**，不抢研究 P0。
4. **解冻条件不变**：一条 edge 过 B2 或 Founder 时间被实测为瓶颈 → 重评 C 层。

## 四、待 Codex 独立反审的问题
- 我是否低估了某个工具对"防断档/防方向错"的真实作用？（防我"全DEFER"偏见）
- ADR/C4 之外，是否有哪个 C 层工具其实低成本高回报、值得提前？
- 我对"过去失败根因"的归类有没有漏项？

---
*（Claude 侧草案；Codex 反审意见见 `REPORT_GOV_TOOLING_EVAL_CODEX_20260621.md`；收敛后升 DEC。）*

---

## 五、收敛裁决（Codex 反审 ACCEPT-with-MODIFY → 升 DEC-086，2026-06-21）

Codex 独立反审（`REPORT_GOV_TOOLING_EVAL_CODEX_20260621.md`）认同主结构，抓 Claude 全 DEFER 偏见，收敛如下（已升 DEC-086）：

1. **§一补漏**：过去失败补两类"可机器检查的轻流程缺口"——①DEC 传播/权威正文不一致（DEC-080 month-30% 泄漏型）②跨文件规则冲突；夜间 scheduler 可靠性=未来生产承载问题（非治理文档问题）。
2. **C 层拆分**：C-heavy（完整 Orchestrator/Web/Discord/Backstage/DevLake/Plane/Spec Kit 全量/七维路由/记分卡）续 DEFER；**C-light（只读状态/事件日志骨架 + DEC 变更传播强化）纳 P0-C+ 现在做**——直接对症 Founder 的断档关切，低成本、不扩执行权限。
3. **D**：ADR-001 + C4 L1 现在补，各封顶一页，不写业务 ADR、不画 C4 全套、不阻塞 B1。
4. **边界**：工具从属权威文件；Superpowers/Skill 只作 Codex 执行纪律非项目权威；子代理按需非核心依赖；state_check 只检确定性硬冲突不做语义真理机；Spec Kit 不进主流程。
5. **最高信息增益**：治理侧=DEC 传播强化；项目总体=不再加工具，去跑 B1-KILLCARD。

**对 Founder 之问的最终答复：不是"我的栈 vs 工具"二选一，是互补分层；最优=保留 A+B + 一次性封顶 P0-C+（C-light+D），重工具续 DEFER，做完即停回 B1。过去问题的最大杠杆是纪律+轻传播检查，不是多加工具。**
