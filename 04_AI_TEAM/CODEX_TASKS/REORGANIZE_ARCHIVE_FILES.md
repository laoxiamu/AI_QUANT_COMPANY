# Codex 任务：全项目归档整理

**任务 ID：** REORGANIZE-ARCHIVE-001  
**状态：** 待派发（Founder 核实后在新会话派 Codex）  
**负责人：** Codex（`--sandbox workspace-write`，纯文件操作，不需要网络）  
**预估时间：** 15-30 分钟  
**优先级：** P2（不阻塞研究主线，但每次新对话都会因文件过多浪费 token）

---

## 任务目标

将 00_PROJECT_MANAGEMENT/ 中的过期/重型文件归档到统一 reference/ 目录，将活跃权威文件数量压缩到 ≤8，减少每次新对话的认知负载和 token 消耗。

---

## 归档规则

1. 归档 = `git mv` 到 `00_PROJECT_MANAGEMENT/reference/` 下的对应子目录（不删除，git 历史保留）
2. 凡文件有更新版本（v2覆盖v1、v2.md覆盖v1.md）的旧版本，归档
3. 凡"快照/调研/批次报告"类文件（不是权威规格），归档
4. 凡已被上位文件引用并降级为"参考输入"的文件，归档
5. 归档后在该子目录创建 `README.md` 说明这里放的是什么、为什么归档

---

## 明确归档列表（00_PROJECT_MANAGEMENT/）

归档到 `00_PROJECT_MANAGEMENT/reference/plans/`：
- `PROJECT_MASTER_PLAN_v1.md`（被 v2 覆盖）
- `PROJECT_MASTER_PLAN_v2.md`（被 PROJECT_TASK_PLAN 覆盖）
- `ADJUSTMENT_LIST_v1.md`（历史调整记录，已入 DECISION_LOG）
- `REVISION_WORKORDER_v2_FREEZE.md`（已冻结执行完毕）
- `EXECUTION_SPEC_v2_FREEZE.md`（已冻结执行完毕）
- `COMPANY_BUILD_MASTERPLAN_v1.md`（上位总图，仍有参考价值，归档但保留指针）

归档到 `00_PROJECT_MANAGEMENT/reference/operating_models/`：
- `OPERATING_MODEL_DESIGN_v0.md`（被v1覆盖）
- `OPERATING_MODEL_DESIGN_v1.md`（被v2覆盖）

归档到 `00_PROJECT_MANAGEMENT/reference/research_snapshots/`：
- `AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12.md`
- `AI_CAPABILITY_TOOLING_AUDIT_v1.md`
- `AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12.md`
- `EXTERNAL_RESEARCH_REPORT_v1.md`
- `EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md`
- `FRONTIER_AI_OPC_AGENT_GOVERNANCE_RESEARCH_2026-06-12.md`
- `INDEPENDENT_REVIEW_v1.md`
- `PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12.md`
- `XHS_NOTE_SUBSTITUTE_ALPHA_ILLUSION_2026-06-12.md`
- `PHASE1_RESEARCH_THESIS_v1.md`（被当前机会地图覆盖）
- `RESEARCH_SNAPSHOT_0B.md`
- `PHASE_TRANSITION_ANALYSIS_0B_TO_1.md`

归档到 `00_PROJECT_MANAGEMENT/reference/tool_plans/`：
- `V5_TOOL_INTEGRATION_PLAN_v1.md`（被v2覆盖）
- `V5_TOOL_INTEGRATION_PLAN_v2.md`（被 OSS_BUILD_VS_BUY 覆盖，作参考保留）
- `TOOL_RESEARCH_BRIEF_v1.md`
- `CLAUDE_CODEX_DISCORD_COLLABORATION_PROPOSAL_2026-06-14.md`
- `OS_TUNING_PLAN_v1.md`
- `CLAUDE_MD_AMENDMENT_PROPOSAL_v2.3.md`（已执行入 CLAUDE.md）
- `CODEX_SKILLS_INSTALL_LOG_2026-06-14.md`

归档到 `00_PROJECT_MANAGEMENT/reference/architecture/`：
- `AI_QUANT_COMPANY_ARCHITECTURE_v1.md`（被v2覆盖）
- `AI_QUANT_COMPANY_ARCHITECTURE_v2.md`（被 COMPANY_BUILD_MASTERPLAN 覆盖）

---

## 00_PROJECT_MANAGEMENT/ 保留活跃文件（不归档）

| 文件 | 保留原因 |
|---|---|
| `PROJECT_TASK_PLAN.md` | 任务单一权威 |
| `OPPORTUNITY_MAP_STATUS.md` | 机会地图活跃看板 |
| `CONSTITUTION.md` | 原则层冻结文件 |
| `COMPANY_STRATEGY_PRODUCT_v1.md` | 战略基础文件 |
| `OPERATING_MODEL_DESIGN_v2.md` | 策略SOP（已降级定位，仍活跃） |
| `PHASE1_TECH_ORG_GOVERNANCE_v1.md` | 治理蓝图（四蓝图之一） |
| `PHASE1_RESEARCH_RISK_BLUEPRINT_v1.md` | 风险蓝图（四蓝图之一） |
| `CAPABILITY_ENV_REGISTRY.md` | 新建，保留 |
| `ASSUMPTION_REGISTRY.md` | 新建，保留 |
| `DEGRADED_MODE_PLAYBOOK.md` | 降级运行手册，仍有用 |
| `CODEX_RESULT_INTAKE_TEMPLATES.md` | Codex任务验收模板 |
| `TOOL_ROUTING.md` | 工具路由规则 |
| `BPR_TOP_LEVEL_FRAMEWORK_REFERENCE_2026-06-15.md` | 最新BPR参考，仍有价值 |
| `AI_CAPABILITY_BASELINE.md` | 能力基线（与CAPABILITY_ENV_REGISTRY互补） |
| `STAGE_AUDITS/`（整个目录） | 所有审计报告保留 |

---

## 05_TECH_DESIGN/ 处理

归档到 `05_TECH_DESIGN/reference/`：
- `01_COMPANY_ORG.md`（E1，作为 E 系列草图，归档）
- `02_SYSTEM_ARCHITECTURE.md`（E2，草图，归档，PHASE2_SYSTEM_BLUEPRINT 为更新版）
- `03_EXECUTION_WORKFLOW.md`（E3，草图，归档）
- `04_MODULE_DESIGN.md`（E4，草图，归档）

保留：`PHASE2_SYSTEM_BLUEPRINT.md`（Track A/B 双轨设计，仍活跃参考）

---

## 99_TEMP/ 处理

全部归档到 `99_TEMP/reference/`（或可直接移入 git 历史，不保留在活跃目录）：
- `ARCHITECTURE_V2_REVIEW.md`
- `BATCH_20260613_SUMMARY.md`
- `CHANGE_REPORT_20260610.md`
- `CHANGE_REPORT_20260611.md`
- `NIGHT_RUN_20260611_REPORT.md`
- `PROTOCOL_GAP_ANALYSIS.md`
- `RAW_INBOX_EXTRACTION_NOTES.md`
- `BACKUP_20260610/`（整个目录，git 已有备份，可删）

---

## 验收标准

1. `00_PROJECT_MANAGEMENT/` 根目录 `.md` 文件数量 ≤ 18（现在 ~42）
2. 所有归档文件有对应 `reference/README.md` 说明
3. `git status` 显示所有移动均为 rename（不是 add+delete）
4. 运行 `python3 01_MEMORY_CORE/state_check.py` 零报错（文件路径引用未断裂）

---

## 执行命令（参考）

```bash
cd /Users/yaomingyu/Documents/AI_QUANT_COMPANY

# 建目录
mkdir -p 00_PROJECT_MANAGEMENT/reference/plans
mkdir -p 00_PROJECT_MANAGEMENT/reference/operating_models
mkdir -p 00_PROJECT_MANAGEMENT/reference/research_snapshots
mkdir -p 00_PROJECT_MANAGEMENT/reference/tool_plans
mkdir -p 00_PROJECT_MANAGEMENT/reference/architecture
mkdir -p 05_TECH_DESIGN/reference
mkdir -p 99_TEMP/reference

# 移动（示例，按实际列表执行）
git mv 00_PROJECT_MANAGEMENT/PROJECT_MASTER_PLAN_v1.md 00_PROJECT_MANAGEMENT/reference/plans/
# ... 其余文件同理

git commit -m "归档过期文件(REORGANIZE-ARCHIVE-001)：活跃文件压缩到≤18"
```

---

**派发前确认：** Founder 核实保留列表无误后，在新会话发送本文件路径给 Codex 执行。  
**不要自动派发** — 归档操作不可逆（虽然 git 可恢复），需 Founder 确认一次。
