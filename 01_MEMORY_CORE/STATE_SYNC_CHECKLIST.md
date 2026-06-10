# STATE_SYNC —— 状态同步清单（防权威状态失真）

**为什么存在：** Codex L1 标的 P0 = "权威状态失真"（CURRENT_STATE 顶部失败计数/阶段滞后、P1-06 未吸收、四份权威文件不一致）。本清单把"写完就同步"固化成强制流程，治本这个反复出现的坑。

**触发：** 任何一次状态变更后，**同一轮内**执行（不拖延，CLAUDE.md 既有规则）。状态变更包括：决策被 Founder 确认 / 产出新方案文档 / 完成任务 / 阶段或方向变化 / 失败计数变化。

---

## 同步顺序（固定）

1. **CURRENT_STATE.md**（运行权威）：更新"下一步" + 相关小节 + 版本号 + 顶部最后更新摘要。
2. **DECISION_LOG.md**：仅当有 **Founder 确认的** 决策 → 追加 `[DEC-XXX]`（编号续上一条；插在"## 已废弃决策"之前）。建议/推演不写入。
3. **BOOT_BRIEF.md**（派生摘要）：同步一句话现状、目标函数、下一步、parked 清单。**它是摘要不是源**。
4. **被取代的文档**：旧文档顶部标 `DEPRECATED → 指向新版`，防 5 份重叠互相矛盾。
5. **一致性自检**：跑 `python3 01_MEMORY_CORE/state_check.py`，确认无滞后告警。
6. **任务列表**：完成的标 completed，新发现的加任务。

---

## 跨文件必须一致的不变量

| 不变量 | 权威源 | 同时出现于 |
|---|---|---|
| 当前阶段 | CURRENT_STATE | OPERATING_STATE、MASTER_PLAN、BOOT_BRIEF |
| 失败计数（历史/独立Alpha） | CURRENT_STATE 顶部 | OPERATING_STATE、BOOT_BRIEF |
| 下一步/当前任务 | CURRENT_STATE | BOOT_BRIEF、任务列表 |
| 目标函数/资本架构 | DEC-063 | 战略产品定义、Thesis、BOOT_BRIEF |

## 单一权威原则

冲突时优先级：**DECISION_LOG > CURRENT_STATE > 其他方案文档 > 对话**。BOOT_BRIEF 与 OPERATING_STATE 均为派生/快照，永不作为源。

## 红线

- Codex 禁止覆盖写 Memory Core（DECISION_LOG/CURRENT_STATE/PROJECT_CONTEXT），其决策性输出写执行报告由 Claude 升级（DEC-030）。
- 写任何共享文件前先读取确认当前状态。

## 上下文预算与工具注记（2026-06-10，OS_TUNING_PLAN_v1）
- BOOT_BRIEF 预算 ≤60 行；CURRENT_STATE 活动区预算 ≤150 行。超限即触发瘦身（历史内容移 `01_MEMORY_CORE/ARCHIVE/`）。
- 沙盒环境运行自检须传项目根路径参数：`python3 state_check.py <项目根>`。
- DECISION_LOG 新增条目后须同步更新文件头部索引表。
