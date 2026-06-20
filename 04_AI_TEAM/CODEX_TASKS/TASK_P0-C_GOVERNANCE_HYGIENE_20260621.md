# 任务包 P0-C：一次性治理卫生（封顶·做完即停）

**任务号：** P0-C-HYGIENE-20260621
**Owner：** Claude 起草与验收　**执行者：** Codex
**决策来源：** DEC-082（顶层重平衡）；Codex 反审 `CODEX_RESPONSE_CLAUDE_TOPLEVEL_REBALANCE_20260621.md` §1/§4.2
**性质：** edge 发现的前置输入卫生，不是治理轨膨胀。**封顶 = 本一包；做完即停，禁止滚动追加 Orchestrator / C4 / 控制面 / 路由器 / 记分卡。**
**目标：** 保证研究输入（B0–B4 任务定义与验收）不被旧状态/规则冲突/假绿灯污染。

---

## 背景（Claude 已完成的部分，Codex 勿重做）

Claude 已同步全部活动态权威文件至 DEC-082 口径：DECISION_LOG（DEC-082 + DEC-080/081 索引修订）、CURRENT_STATE v4.5、PROJECT_TASK_PLAN（当前焦点 + P1-RES-034 拆 B0–B4）、BOOT_BRIEF（含 8 维表①与最新 DEC 指针）。坏串扫描已 ✓。

**本任务只做 Claude 不该碰的两类技术活：① 修 state_check 代码；② 裁四份规则文件硬冲突。**

---

## T1：修复 state_check.py（消灭假绿灯）

**实证问题：** 当前 `01_MEMORY_CORE/state_check.py` 在结论为「发现 N 项疑似滞后」时**仍返回退出码 0**；且路径解析在非 Mac 环境（如 VM）下把存在的权威文件误报「[缺失]」。

**验收标准（全部硬性）：**
1. **退出码语义正确：** 任何「缺失 / 疑似滞后 / 权威冲突 / 坏串命中」→ 返回**非零退出码**；全绿才返回 0。（这是 DEC-082 P0-C 与 Codex 反审 §1 的核心要求。）
2. **路径鲁棒：** 以脚本自身位置/项目根标记（如 `CLAUDE.md` 所在目录）自动定位项目根，支持任意 cwd 与 Mac/VM 双环境，不再硬编码单一绝对路径。
3. **坏串库更新：** 新增当前必须报警的坏串，至少含：「月化30%」作为研究**验收/门槛**语境、「唯一已验证主线」「新主线=regime-adaptive」（应为 Candidate）、「10-20x 杠杆」作为**实验/Alpha**语境、carry 出现在 active 主线位。允许误报从宽，但不得漏报。
4. **最新 DEC 一致性检查：** 校验 BOOT_BRIEF/CURRENT_STATE 的「最新 DEC」指针与 DECISION_LOG 实际最大 DEC 号一致，不一致即非零退出。
5. 自带最小自测：构造一个含坏串的临时样本→断言返回非零；干净样本→断言返回 0。

**禁止：** 不扩展为通用编排校验器；不接事件库；不改权威文件内容（只读校验）。

---

## T2：裁四份规则文件硬冲突（逐条一个生效规则）

**对象：** `CLAUDE.md`、项目根 `AGENTS.md`、`SYSTEM_RULES`（定位后）、`AGENT_REGISTRY`（定位后）。

**已知必裁冲突（至少这两条，扫描后补全）：**
1. **commit 权限冲突：** AGENTS.md 要求每任务 commit vs AGENT_REGISTRY 禁止 Codex commit。→ 给出唯一生效规则建议（建议：Codex 不直接 commit，由 Claude 验收后推送；以 CODEX_DIRECT_CALL_RUNBOOK 现行实践为准），写明依据。
2. **Memory 写入冲突：** CLAUDE.md 强制建议写入 §1c（DEC-073）vs SYSTEM_RULES 禁止对话分析进入 Memory Core。→ 给出唯一生效规则建议（建议：§1c 属 CURRENT_STATE 运行看板非 Memory Core 长期事实，二者不矛盾；据此澄清 SYSTEM_RULES 措辞）。

**交付物：** `REPORT_P0-C_HYGIENE.md`，含：
- 冲突清单表：`冲突项 | 文件A条款 | 文件B条款 | 建议生效规则 | 依据 | 是否需 Claude/Founder 拍板`。
- **不直接改四份规则文件正文**（规则文件口径变更属权威，Claude 裁决后执行）；Codex 只产出裁决建议清单。

---

## T3：防扩张闭环

`REPORT_P0-C_HYGIENE.md` 末尾必须列 **「未做清单（已冻结）」**，显式声明以下项本任务不做、且按 DEC-082 冻结直至解冻触发：Orchestrator/事件库、Strategy Governor 引擎、Web/Discord、七维路由、九域记分卡、Spec Kit 试点、C4 全套、ADR-业务项。

---

## 完成通知

按 TASK_INBOX 协议写 `04_AI_TEAM/TASK_INBOX/P0-C-HYGIENE-20260621_DONE.json`。
Claude 半天内验收：T1 跑通（含非零退出码自测）+ T2 冲突清单完整 + T3 未做清单齐 → ACCEPT → **治理轨关闭** → 起草 B0 机制卡。

**【需要 Codex】** 执行 T1/T2/T3。
**【Claude 继续】** 验收后起草 B0；不等 Founder（非 D 级）。
