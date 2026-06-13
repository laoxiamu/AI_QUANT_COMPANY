# REPORT_E3：执行工作流文档

状态：完成
日期：2026-06-14
执行者：Codex

## 任务范围

- 创建 `05_TECH_DESIGN/03_EXECUTION_WORKFLOW.md`
- 内容覆盖两条核心流程：项目执行流、投研执行流
- 增加流程触发与分工表

## 执行前自查

- 机制验证：本任务为系统蓝图文档创建，不做研究机制验证
- 验收标准：文件存在、两条流程齐全、格式清晰、80 行以内
- 等效实现：直接新增 Markdown 文档是最低成本实现
- 禁止项：未触碰 Holdout、未修改预登记/研究协议、未读取或修改 `01_MEMORY_CORE/`

## 验收自检

- `05_TECH_DESIGN/03_EXECUTION_WORKFLOW.md` 已创建
- 文件头包含标题、ACTIVE 状态、更新日期与说明
- 项目执行流已包含任务分配、Codex 执行、自动验证、Claude Review、归档与 §1b 清空
- 投研执行流已包含机制审查、查墓园、预登记、数据验证、WF 回测、Claude Review、通过/失败分支
- 流程触发与分工表已包含 4 个指定场景
- 流程图使用 ASCII `->` 箭头
- 主文档行数：68 行

## 未执行事项

- 未读取 Holdout 数据
- 未修改 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`
- 未修改 `01_MEMORY_CORE/` 权威文件
- Git 提交未完成：当前环境禁止写入 `.git/index.lock`，无法执行 `git add`
