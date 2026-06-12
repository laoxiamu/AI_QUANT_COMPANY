# AGENT_REGISTRY（DEC-069 / 双审计 P1，一页表）

| Agent | 模型/通道 | Owner | 允许 | 禁止 | 状态 |
|---|---|---|---|---|---|
| Claude 主会话 | Fable/Cowork | Founder | 判断/设计/验收/D级提案/≤50行脚本 | 动钱；改 Founder 已拍决策（须重新上 D）；读 HOLDOUT | active |
| Codex 直调 | codex CLI exec（配方见 RUNBOOK）| Claude | 实现/回测/数据工程，workspace-write | git commit（Claude 验收后统一）；改预登记；读 HOLDOUT；网络默认关（任务书显式开）| active |
| 低模型执行层 | haiku 子代理 / 低模型会话 | Claude | 逐字 payload/格式/索引/横幅（可 diff 机械活）| 一切语义判断；触权威文件语义；研究结论 | active |
| 定时任务×3 | 应用内 scheduler | Claude | 周监控/月审/一次性批次（只用文件+搜索类工具）| 会弹确认的工具；夜间关键路径（可靠性低）| active（运行层v0.x）|
| Risk Reviewer / 独立复核 | 隔离子会话 | Claude | 按 CONTEXT_PACKS 白名单读取 | 读提案者结论；读 HOLDOUT | 按需启用 |

**Trace：** 每次 Codex 直调/低模型任务包完成后，向 `04_AI_TEAM/RUN_LOG.jsonl` 追加一行（task/agent/输入任务书/产出/验收结果/异常）。
**Lint：** `scripts/no_holdout_lint.sh` 装为 git pre-commit；任务书与分析代码出现 HOLDOUT 读取即拒绝提交（白名单：封存写入器 a2_funding_features.py）。
