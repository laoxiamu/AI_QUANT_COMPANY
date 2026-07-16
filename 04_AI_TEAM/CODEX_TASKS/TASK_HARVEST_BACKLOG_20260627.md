# Codex 任务：历史报告积压 harvest 提取（P1-GOV-009 提取段）

**任务 ID：** P1-GOV-009-EXTRACT｜**派发：** Claude（主理人）｜**日期：** 2026-06-27
**分工边界（重要）：** 你只做**批量提取 + 草拟**，产出到**暂存文件**；**绝不写入正式知识库文件**（CARRY_KNOWLEDGE/TOOLS_KNOWLEDGE/TSMOM/GRAVEYARD/RESEARCH_ACTION_REGISTRY 等）——权威条目由 Claude 审后写（DEC-069 权威语义不下放）。
**纪律：** 不碰 Holdout、不回测、不调参、不耗计数；只读报告、只写一个暂存 md。

## 范围
- `04_AI_TEAM/CODEX_TASKS/REPORT_*.md`（约 84 份）
- `06_RESEARCH/RESULTS/*.md`（约 55 份）

## 处理（参照 `.claude/skills/research-harvest/SKILL.md` 格式）
1. 逐份读（优先第一节摘要/结论；FAILED/KILL/NOT APPROVED 类读全文）。
2. 按类别分组（skill 表）：Carry / 系统工程 / 工具OSS / TSMOM-Alpha / 治理审计 / 其他。
3. 每份抽一行结构化：`文件名 | 日期 | 主题 | 结论或状态(标注FAILED/KILL/PASS) | 核心发现(1-2句) | 根因(如失败) | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复?(Y/N+哪条)`。
4. 对每类，按 skill 格式**草拟**待写条目（教训 C-XXX / 行动 RA-XXX），标 **[草稿待Claude审]**，不写进正式文件。
5. 优先序：失败类(FAILED/KILL/NOT APPROVED)最优先 → carry/forced-flow/TSMOM 相关 → 近6月 → 其余倒序。
6. 交叉现有知识库（只读 `02_KNOWLEDGE_BASE/*.md`）标重复，避免重复草拟。

## 输出（只写这一个文件）
`02_KNOWLEDGE_BASE/HARVEST_STAGING_20260627.md`：分类清单(全部~139行) + 各类草拟条目[草稿待Claude审] + 末尾"给Claude的判断线索"(你观察到的模式/反复出现的失败根因，供 Claude 下主理人判断，但**不替 Claude 下最终判断**)。
回写 `04_AI_TEAM/TASK_INBOX/P1-GOV-009-EXTRACT_DONE.json`(status/暂存文件路径/扫描份数/各类计数)。

## 禁止
- 禁写任何 `02_KNOWLEDGE_BASE/` 下的现有正式文件（只新建 HARVEST_STAGING）。
- 禁把"不推荐做X"当无价值忽略(负面结论有价值)。禁写通用废话教训。
