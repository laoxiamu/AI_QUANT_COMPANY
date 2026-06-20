---
name: codex-task-spec
description: 生成标准格式的Codex任务书，写入文件供Codex读取执行。当用户说"派给Codex"、"让Codex做"、"写任务书"、"新建Codex任务"时触发。凡是需要把任务交给Codex的场景都应使用本skill生成规范任务书，不要在对话里直接口述任务。
---

# Codex Task Spec：Codex任务书生成

## 为什么用文件而不是对话传递任务

口述任务 = Founder复制粘贴中间人 = 本项目长期痛点。任务书写进文件，Codex读文件执行，Claude只管写文件。这是DEC-073的协作规则之一。

## 任务书写入位置

```
04_AI_TEAM/CODEX_TASKS/TASK_{ID}_{简短名称}.md
```

文件名示例：`TASK_DATA-001_carry_data_procurement.md`

## 任务书标准格式

```markdown
# Codex任务书：{任务名称}

**任务ID：** {ID}
**优先级：** P1/P2/P3
**创建时间：** {日期}
**预估规模：** {行数/文件数}
**指定Codex Skill：** {从14个已安装Skill中选择，如PlanToDelivery/tdd/diagnose等；无特定=default}

---

## 背景与目的

{1-3段：为什么做这个任务，它解决什么问题，来自哪个研究结论（引用RA-xxx或DEC-xxx）}

## 研究约束（从CLAUDE.md强制继承）

- 机制优先：先验证"谁在付钱/为什么"，不搜因子不搜形态
- 禁止：找信号→回测→失败→改参数→再回测的局部修补搜索
- 借鉴优先：先查RESEARCH_ACTION_REGISTRY有无相关结论再动手
- Holdout绝对禁读：任何情况下不得读取~/.aiquant_sealed/目录

## 具体目标

{可量化的、可验证的任务目标，1-5条}

1. {具体目标1}
2. {具体目标2}

## 输入文件/数据

{列出Codex需要读取的文件，含路径}

- `{路径}` — {用途}

## 输出产物

{Codex需要生成的文件，含路径和格式}

- `04_AI_TEAM/CODEX_TASKS/REPORT_{ID}_{名称}.md` — 任务报告（必须）
- `{其他产物路径}` — {说明}

## 报告模板（输出REPORT_xxx.md时必须按此格式）

```
## 摘要
## 执行步骤
## 关键发现（含对RESEARCH_ACTION_REGISTRY的更新建议）
## 对知识库的贡献（应写入CARRY_KNOWLEDGE.md/TOOLS_KNOWLEDGE.md哪一节）
## 验收结果
## 未解决问题
## 建议下一步
```

## 禁止项

- 禁止读取 `~/.aiquant_sealed/` 下任何文件（Holdout）
- 禁止使用Hyperopt
- 禁止在报告里只给数字不给判断
- {其他任务特定禁止项}

## 验收标准

{用于Claude验收时的检查点，3-5条}

- [ ] {验收条件1}
- [ ] {验收条件2}
- [ ] 报告含"对知识库的贡献"节
- [ ] 报告含"建议下一步"节
```

## 写完任务书后

1. 确认文件已写入正确路径
2. 在 `CURRENT_STATE.md §1b` 注明"已派出TASK_xxx等待Codex执行"
3. 在 `PROJECT_TASK_PLAN.md` 把对应任务标记为"🟡 待Codex执行"
4. 告知Founder任务书路径和需要Codex执行的命令

## 提示Founder的Codex执行命令格式

```
cd /Users/yaomingyu/Documents/AI_QUANT_COMPANY
codex --approval-mode auto-edit "读取并执行 04_AI_TEAM/CODEX_TASKS/TASK_{ID}_{名称}.md 中的任务"
```
