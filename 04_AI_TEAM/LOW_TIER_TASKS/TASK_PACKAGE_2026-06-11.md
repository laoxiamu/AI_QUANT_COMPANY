# 低模型执行任务包 2026-06-11（文档一致性修复，4 项）
**发包/验收：** Claude ｜ **执行铁律：** 同 TASK_PACKAGE_2026-06-10 六条（不判断/不发明/动 01_MEMORY_CORE 先备份 99_TEMP/BACKUP_20260611/；锚点找不到就跳过并报告；完成记录追加 99_TEMP/CHANGE_REPORT_20260611.md；终检跑 state_check）

## U-01 运营模型 KPI 残留修复
文件 `00_PROJECT_MANAGEMENT/OPERATING_MODEL_DESIGN_v1.md`，§1.1 第6条：
把 `6. 成功指标（月化、分档存活率、自动化率、停机时长、人工介入次数）`
逐字替换为 `6. 成功指标（核心资本几何增长率、分档存活率、自动化率、停机时长、人工介入次数——DEC-063：月化30%已废除）`

## U-02 战略文围栏表述统一
文件 `00_PROJECT_MANAGEMENT/COMPANY_STRATEGY_PRODUCT_v1.md`：
把 `└── 围栏高风险子账户（小额，如 1000 一档，物理隔离）`
逐字替换为 `└── 围栏高风险子账户（25%本金，DEC-066②；低资金档另设绝对值下限，物理隔离）`

## U-03 Protocol v1.2 头部加增补件注记
文件 `06_RESEARCH/RESEARCH_PROTOCOL_v1.2` ——注意实际文件名是 `06_RESEARCH/RESEARCH_PROTOCOL_v1.md`。在其标题行之后插入空行 + 逐字横幅：
`> ⚠️ **增补件优先（2026-06-11）**：本文件与 RESEARCH_PROTOCOL_v1.3_ADDENDUM.md 冲突处，以增补件为准。本文旧门槛（Expectancy>1.0 / MaxDD<25% / 净Sharpe>1）已废，验收按增补件四件套。`

## U-04 PROJECT_OPERATING_STATE 降级横幅
文件 `00_PROJECT_MANAGEMENT/PROJECT_OPERATING_STATE.md` 标题行后插入空行 + 与其他降级文件相同的逐字横幅：
`> ⚠️ **本文件已降级（2026-06-11，依据 CLAUDE.md v2.3 / DEC-067）**：仅作历史参考，禁止作为当前架构、计划或决策依据。现行权威：\`01_MEMORY_CORE/BOOT_BRIEF.md\` + 公司OS四蓝图。`

## 终检
`python3 01_MEMORY_CORE/state_check.py <项目根>` 须输出"无已知滞后"；报告末尾写"全部完成，等待 Claude 验收"。
