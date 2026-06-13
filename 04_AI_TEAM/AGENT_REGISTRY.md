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

## Script Registry Addendum（2026-06-13）

| Batch | Task | Path / Entry | Purpose | Status |
|---|---|---|---|---|
| BATCH_20260612N | B1 | `06_RESEARCH/CODE/tsmom_dual_engine.py --riskbudget-v2` | TSMOM v2 风险预算版回测入口 | registered |
| BATCH_20260612N | B2 | `06_RESEARCH/CODE/b2_fifth_criterion_verification.py` | P1-04/P1-06 第五件追溯复算 | registered |
| BATCH_20260612N | B3 | `06_RESEARCH/CODE/a4_listing_census.py` | A-4 新上市归档可得性普查 | registered |
| BATCH_20260612N | B4 | `06_RESEARCH/CODE/a1_mde_precheck.py` | A-1 MDE 功效门预检 | registered |
| BATCH_20260612N | B5 | `06_RESEARCH/CODE/collector_dataplane_diag.py` | Binance WebSocket 数据面诊断 | registered |
| BATCH_20260613 | C1 | `06_RESEARCH/CODE/c1_tsmom_universe_feasibility.py` | TSMOM 扩 universe 月度 4H 归档 HEAD 探测 | registered |
| BATCH_20260613 | C2 | `06_RESEARCH/CODE/c2_carry_spot_basis.py` | BTC/ETH spot 1H 下载与 basis 数据层统计 | registered |
| BATCH_20260613 | C3 | `06_RESEARCH/CODE/a1_event_study_framework.py` | A-1 事件研究执行框架 | registered |
| BATCH_20260613 | C3 | `06_RESEARCH/CODE/tests/test_a1_event_study.py` | A-1 框架合成数据 pytest | registered |
| BATCH_20260613 | C4 | `06_RESEARCH/HYPOTHESES/a4_new_listing_v1.md` | A-4 新上市错位预登记草案（非脚本） | registered |
