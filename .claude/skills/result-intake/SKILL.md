---
name: result-intake
description: 接收并处理Codex任务完成报告，提取研究结论写入知识库，更新项目状态。当用户说"Codex完成了"、"看看这个报告"、"处理任务结果"、"验收"、"intake"时触发。凡是有Codex报告需要处理的场景都应使用本skill，不要手动处理。
---

# Result Intake：Codex报告接收与知识harvest

## 为什么这很重要

项目里60+份Codex报告积累无人harvest，等于白做研究。本skill确保每份报告的结论都被提取、分类、写入正确的知识文件，而不是死在CODEX_TASKS目录里。

## 处理流程

### Step 1：读取报告

读取Codex完成的报告文件（通常在 `04_AI_TEAM/CODEX_TASKS/REPORT_*.md` 或 `TASK_INBOX/*_DONE.json`）。

### Step 2：专业审查（Rule 7，先给判断再汇报数字）

读完报告后，先问自己：**"作为主理人，我从这个结果里看到了什么Founder不会自己看到的？"**

写出你的专业判断，包括：
- 本任务真正回答了什么问题？
- 结果改变了哪些假设（ASSUMPTION_REGISTRY）？
- 发现了什么新风险或新机会？
- 下一步最高价值的行动是什么？

### Step 3：分类处理

根据报告类型写入对应文件：

**研究报告（carry/TSMOM/A-x系列）：**
- 在 `02_KNOWLEDGE_BASE/CARRY_KNOWLEDGE.md`（或对应策略知识库）的§四"教训"节追加新条目
- 格式：`### 教训X-XXX：[简短标题]` + 来源 + 结论 + 对当前研究方向的影响

**系统/工程报告（E系/D系/Fix系）：**
- 在 `02_KNOWLEDGE_BASE/SYSTEM_LESSONS.md` 追加（如文件不存在则创建）
- 格式：`| SYS-XXX | 来源 | 教训 | 日期 |`

**工具/OSS报告：**
- 在 `02_KNOWLEDGE_BASE/TOOLS_KNOWLEDGE.md` 对应节更新

**审计报告：**
- 在 `00_PROJECT_MANAGEMENT/RESEARCH_ACTION_REGISTRY.md` 追加新行动项

### Step 4：更新RESEARCH_ACTION_REGISTRY

凡是报告里有"本项目应该做X"类结论，立刻在 `RESEARCH_ACTION_REGISTRY.md` 追加：

```
| RA-XXX | 来源报告 | 核心结论 | 对应行动 | ❌未执行 | P1/P2/P3 |
```

### Step 5：更新CURRENT_STATE §1c

如果报告产出了需要Founder决策的建议，写入 `CURRENT_STATE.md` 的 §1c 对话级建议暂存区。

### Step 6：更新PROJECT_TASK_PLAN

如果任务完成，在 `PROJECT_TASK_PLAN.md` 把对应任务标记为完成，并根据结果更新下一步任务状态。

### Step 7：输出摘要

给Founder的汇报格式：
```
**[任务ID] 验收结论**
状态：PASS / FAIL / BLOCKED
主理人判断：[你看到了什么Founder不会自己看到的]
关键发现：[1-3条具体结论]
知识库更新：[写入了哪个文件的哪一节]
下一步：[最高价值的后续行动]
```

## 禁止

- 禁止只报数字不给判断（如"任务完成，生成了83个候选"）
- 禁止看完报告不更新知识库
- 禁止跳过RESEARCH_ACTION_REGISTRY更新
