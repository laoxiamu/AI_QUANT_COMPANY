# BOOT_BRIEF —— 精简启动简报（新对话先读这一份，省 token）

> ⚠️ 2026-06-21 顶层重平衡（DEC-082）：研究=唯一P0/治理压一次性卫生/自动化全DEFER；month-30%出研究验收(=资本愿望)；P1-RES-034拆B0-B4单变量序列；杠杆=过门后风险测试非Alpha来源。carry仍Dead(DEC-079)。本文件已同步。

**性质：** 派生摘要，非权威源（当前焦点=`CURRENT_STATE.md`；详细任务=`PROJECT_TASK_PLAN.md`；决策=`DECISION_LOG.md`）。预算 ≤60 行。
**最后更新：** 2026-06-21（治理分档DEC-083；最新DEC=DEC-083）

## 一句话现状

Phase 1。**carry=Dead（DEC-079）**。regime-adaptive=**Candidate（待过B0机制门/B1数据门，非已验证主线）**。**DEC-082顶层重平衡：研究=唯一P0轨/治理压一次性卫生(P0-C封顶1包)/自动化全DEFER；month-30%=资本愿望非验收门；杠杆=过门后风险测试非Alpha来源**。数据✅就绪(127 parquet)。🟡下一步=**P0-C治理卫生(先行,state_check+四份规则文件冲突)→起草B0机制卡**。P1-RES-034原捆绑描述已冻结,拆B0→B1→B2(1x)→B3→B4。A-1 Dead。强平采集器收数中。

## 目标函数（DEC-063，原则层冻结）

找真实/可持续/可放大 edge + 安全复利核心资本；月化30%不是验收条件；两层资本（核心受保护 / 围栏**按证据等级解锁**，DEC-069④）；高杠杆=表达工具非Alpha来源（实证：@2x年爆仓61-76%）。

## 止损与计数（DEC-069①）

旧范式 5 败封账；**新范式独立计数=1（a2）**，计数=L3触发器（每+2复评）；**主闸=时间盒（2026-06-07起6个月无edge）+成本盒（5000元，已用871.93）+L3裁量**。"剩N命"倒计时废止。

## 研究范式（原则层冻结）

机制优先七问（含"付的钱经什么路径到我口袋"）；预登记+单变量+WF+Holdout物理封存；事件类按 v1.3 增补件（池化+单调性+成本压力档）；**预登记须含 MDE 功效段、验收含同状态被动基准对照（v1.4 已完成）**；不显著点估计禁作方向结论（墓园禁引用措辞字段）。新假设先查 `06_RESEARCH/GRAVEYARD_INDEX.md`。

## 在途与等待（2026-06-20 方向重置后）

- **🟡唯一研究主线（DEC-082拆分）：** regime-adaptive = B0机制卡(可证伪硬验收,不碰Holdout/不调参)→B1标签审计→B2单变量门控(1x)→B3仓位→B4杠杆风险测试。任一步不过=回墓园/pivot,禁改参数续命。
- **🟡执行顺序：** P0-C一次性治理卫生(先行,封顶1包:state_check修复+AGENTS/CLAUDE/SYSTEM_RULES/AGENT_REGISTRY硬冲突裁决)→验收后起草B0。
- **🧊 DEFER（DEC-082,解冻=一条edge过B2或Founder时间实测为瓶颈）：** Spec Kit初始化/ADR-业务项/C4全套/Orchestrator/Strategy Governor引擎/Web/Discord/七维路由/九域记分卡。
- **🔵知识积压：** OSS-001 TOOLS_KNOWLEDGE 6项更新待执行(非阻塞)。
- **⚪等待 Founder D（1项）：** ④公司终态/阶段门（非紧急,待B0后再谈）。
- **详细任务：** `00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md`。

## 公司 OS 全局平衡检查（每次开局强制执行，8维度）

> 主理人职责不只是推进研究，是确保公司8个维度同步健康。开局时必须扫一遍，发现失衡立即提出。

| 维度 | 当前状态 | 警戒 |
|---|---|---|
| ①量化研究 | regime-adaptive=Candidate(待过B0机制门)；carry Dead；A-1 Dead；TSMOM Baseline | ⚠️edge=0，唯一P0 |
| ②生产工程基础设施 | E1-E4 草图已完成，生产平台未建 | ⚠️ 待实现 |
| ③实时风控执行层 | 规则与架构草图已有，代码层未实现 | ⚠️ 待实现 |
| ④运营工作流 | 责任与流程未形成可运行闭环 | ⚠️ 待建设 |
| ⑤公司治理/文档 | DECISION_LOG/OS蓝图相对完整 | 正常 |
| ⑥项目管理/产研工作流 | 总图与 108 项单一 WBS 已建立 | 正常 |
| ⑦监控与告警 | 只有强平采集器，无交易系统监控 | ⚠️ Phase 2前设计 |
| ⑧知识管理/经验沉淀 | CARRY_KNOWLEDGE/TOOLS_KNOWLEDGE/RESEARCH_ACTION_REGISTRY已建；3个Claude Skills（result-intake/codex-task-spec/research-harvest）+Holdout hook已建；60+历史报告harvest待执行 | ⚠️ 改善中 |

**②③④⑦ 已有 DRAFT v0.2（`05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md`）**，包含 Track A（自动执行）+ Track B（AI主动分析）双轨制设计。**Track B 方向待 Founder D 级确认。**

## 团队工作方式（自我提醒）

主理人开局；不做选择题搬运工（D级=修改Founder已拍决策，必带推荐整包上）；两面诚实反迎合；跑批可靠性排序=Codex nohup > 白天定时 > 夜间定时；低模型只做逐字/格式/索引；产出未经 Claude 验收不作依据。**任务产出后强制专业透镜（规则7）；主动设置议程不等Founder发现（规则8）。**

## 细节指针

CURRENT_STATE v4.3（当前焦点；§4 指向任务权威）｜**PROJECT_TASK_PLAN（唯一详细任务权威）**｜**§1b=活动工作区（Claude 对话级在途）**｜DECISION_LOG（索引→DEC-083 为最新）｜OPPORTUNITY_MAP_STATUS｜直调配方 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`｜启动协议见 CLAUDE.md v2.4。
**新协议**：Codex完成任务→写04_AI_TEAM/TASK_INBOX/{ID}_DONE.json→15min调度器自动拾取→派发下一步（见TASK_INBOX/README.md）。

**§1b 制度**：Founder 主动打断对话时，Claude 在结束前必须更新 §1b（已完成什么、剩余什么、恢复点在哪）。新对话开局如 §1b 有内容，优先恢复，不重新分析。
**§1c 制度（DEC-073）**：对话中 Claude 提出的任何建议须当场写入 §1c；Founder 确认→升入§4；否决→清除；未响应=下次开局必提。DEC-073=全周期决策记录规范（§1c制度来源）；**最新=DEC-083**。
