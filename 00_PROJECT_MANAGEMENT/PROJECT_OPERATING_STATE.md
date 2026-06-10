# PROJECT_OPERATING_STATE.md

**版本：** 2.7  
**更新时间：** 2026-06-07（状态同步:修正§1阶段Phase 0B→Phase 1;P1-01~P1-06已执行,失败计数10/独立Alpha 5/8;本表仅留早期闭环示意,运行实况以CURRENT_STATE为权威。三审计6-07共识:暂停新实验待Founder裁决D级。本文件与CURRENT_STATE重叠,Opus标P2待归并。）  
**上版（2.6）：** 2026-06-06（DEC-053门槛校准:回撤按资金档定规模+保Sharpe>1;TSMOM封存;待选新纯永续方向性信号）  
**阶段：** Phase 1 · 找到有效赚钱规律（2026-06-06 跨越，DEC-049）  
**性质：** 项目运行状态快照，新对话启动时读取以恢复运行认知  
**注意：** 本文件如与 CURRENT_STATE.md 或 DECISION_LOG.md 有冲突，以后两者为准

---

## 1. 当前阶段状态

**阶段：** Phase 1 — 找到有效赚钱规律（2026-06-06 从0B跨越，DEC-049）  
**Phase 0A 验收：** ✅ 全部5项完成；**Phase 0B：** ✅ 研究闭环能力经8闭环证明（L2 CONDITIONAL GO）

> ⚠️ 下表仅保留早期 v1~v5 闭环示意。Phase 0B 后续变体（v6/v6b/0B17/0B18）及 Phase 1（P1-01~P1-06）的运行实况，以 `01_MEMORY_CORE/CURRENT_STATE.md` 为唯一权威。当前最新：P1-06 已完成（PASSED/EXPLORATORY，净Sharpe1.285/309笔探索级）；三审计6-07共识暂停新实验，待Founder裁决4项D级。

**Phase 0B 早期研究进展（示意，非最新）：**

| 实验 | 版本 | 类型 | 结论 | 失败计数 |
|------|------|------|------|---------|
| 第1闭环 | v1（4H三重确认） | 策略回测 | FAILED | 1/8 |
| 第2闭环 | v2（1H三重确认） | 策略回测 | FAILED | 2/8 |
| 第3闭环 | v3（单事件收益） | 事件研究 | FAILED | 3/8 |
| 第4闭环 | v4（双层Regime） | 事件研究 | **PASSED**（三层统计校验） | 不计 |
| v4追加 | v4策略回测 | 策略回测 | FAILED（Sharpe 0.31） | 不另计 |
| 第5闭环 | v5（Bearish Sweep） | 事件研究 | FAILED | 4/8 |
| 基础设施 | Bootstrap校验 | 统计校验 | PASSED（3层） | — |
| 基础设施 | 回测单测 | 自动化测试 | PASSED（9/9） | — |

**失败计数（双轨制，DEC-044/046/047/051/052，三数并列）：** 历史实验失败 **10次**｜独立Alpha假设 **5/8**（管辖项目级止损，距8还有3次）｜v4实现变体 CLOSED；TSMOM家族两连测后建议封存（单因子共同回撤）  
> 注：本表仅列至第5闭环。v6/v6b/0B17/0B18 后续变体明细以 `01_MEMORY_CORE/CURRENT_STATE.md`（权威）为准。L3审计 + Codex复核见 STAGE_AUDITS/L3_EMERGENCY_2026-06-06.md。
**v4：** 样本内统计边沿真实，实现线已关闭，降级"不可部署"归档。  
**Holdout：** 全部实验封存，未读取

---

## 2. 工具链状态

| 工具 | 状态 | 备注 |
|------|------|------|
| Claude Cowork | ✅ 完全可用 | 主工作区 |
| Claude Code v2.1.161 | ✅ 已安装 | Cowork底层 |
| Desktop Commander v0.2.41 | ✅ 完全可用 | Mac本地执行 |
| Python 3.13.5 + 量化环境 | ✅ 完全可用 | pandas/numpy/vectorbt/ccxt/matplotlib/scipy/statsmodels |
| VectorBT 1.0.0 | ✅ 已验证 | 策略回测主引擎 |
| Codex | ✅ 已验证 | 完成0B3/0B4/0B5/0B6四任务 |
| Obsidian + Sync | ✅ 可用 | 被动读取 |
| x-reader + Playwright | ✅ 已安装 | 微信公众号抓取 |
| Context7 | ⚠️ 已安装未使用 | 按需调用 |
| 腾讯云轻量（新加坡） | ⚠️ 状态未知 | Phase 2评估 |

---

## 3. 目录结构实际状态

```
AI_QUANT_COMPANY/
├── CLAUDE.md                                  ✅ v2.0（2026-06-05精简）
├── 00_PROJECT_MANAGEMENT/
│   ├── AI_CAPABILITY_BASELINE.md              ✅ v1.1
│   ├── PROJECT_MASTER_PLAN_v2.md              ✅ v2.2 ACTIVE
│   ├── PROJECT_OPERATING_STATE.md             ✅ 本文件 v2.0
│   ├── AI_QUANT_COMPANY_ARCHITECTURE_v2.md    ✅ FROZEN
│   ├── EXTERNAL_RESEARCH_REPORT_v1.md         ✅ 完成
│   └── STAGE_AUDITS/
│       └── L2_AUDIT_PHASE_0A_2026-06-06.md   ✅ 完成（CONDITIONAL GO）
│
├── 01_MEMORY_CORE/
│   ├── CURRENT_STATE.md                       ✅ v2.7（本次更新）
│   ├── DECISION_LOG.md                        ✅ DEC-001~032
│   ├── PROJECT_CONTEXT.md                     ✅ D10+D34共9条
│   ├── MEMORY_EXTRACTION_PROTOCOL.md          ✅ 完成
│   └── SYSTEM_RULES.md                        ✅ 完成
│
├── 02_KNOWLEDGE_BASE/
│   ├── EXTERNAL_RESEARCH_v2_AI_NATIVE_OPERATING_PATTERNS.md ✅
│   ├── STRUCTURE_SETUP_FAILURE_LESSONS_v1.md  ✅ v1/v2失败经验
│   └── SWEEP_SIGNAL_FAILURE_LESSONS_v2.md     ✅ v3/v4/v5失败经验（2026-06-06新增）
│
├── 03_RAW_INBOX/
│   ├── STATUS_RECORDS/                        ✅ D10/D34等已提炼
│   └── WECHAT_ARTICLES/                       ✅ 20篇微信文章
│
├── 04_AI_TEAM/CODEX_TASKS/
│   ├── COLLABORATION_RULES.md                 ✅
│   ├── SPEC_0A6_SIGNAL_DEFINITIONS.md         ✅
│   ├── TASK_0A6 + REPORT_0A6                  ✅
│   ├── TASK_0B1 + REPORT_0B1（v3）            ✅
│   ├── TASK_0B2 + REPORT_0B2（v4事件）        ✅
│   ├── TASK_0B3 + REPORT_0B3（v5做空）        ✅
│   ├── TASK_0B4 + REPORT_0B4（v4策略）        ✅
│   ├── TASK_0B5 + REPORT_0B5（Bootstrap）     ✅
│   ├── TASK_0B6 + REPORT_0B6（单测）          ✅
│   └── TASK_0B7（v6时间退出）                 ✅ READY_FOR_EXECUTION
│
├── 06_RESEARCH/
│   ├── RESEARCH_PROTOCOL_v1.md               ✅
│   ├── CODE/                                  ✅ 信号检测/事件研究/策略回测/Bootstrap/单测
│   ├── HYPOTHESES/                            ✅ v1~v5预登记文件
│   └── RESULTS/                               ✅ 所有实验评估报告
│
└── 99_TEMP/
    ├── AUDIT_REPORT_HISTORY_CONTAMINATION.md  ✅
    └── RAW_INBOX_EXTRACTION_NOTES.md          ✅
```

---

## 4. 当前任务队列

| 任务 | 状态 | 执行人 |
|------|------|--------|
| Phase 1 P1-01~P1-06 主线 | ✅ 全部执行完毕（最新P1-06 PASSED/EXPLORATORY） | Codex |
| 三审计6-07治理修复（状态同步+台账） | ✅ 本轮完成 | Claude |
| 4项D级裁决（熔断口径/carry/P1-06续/时间盒） | ⏳ 待Founder | Founder |
| P1-04 Deflated Sharpe 补算 | ⏳ 待执行 | Claude |
| —— 以下为历史早期任务（已归档） —— | | |
| CURRENT_STATE v2.7更新 | ✅ 完成 | Claude |
| 失败知识提炼v2（SWEEP_SIGNAL） | ✅ 完成 | Claude |
| P1-4回测单测 | ✅ 完成 | Codex |
| P1-5失败知识 | ✅ 完成（v1/v2+v3/v4/v5均已归档） | Claude |
| PROJECT_OPERATING_STATE更新 | ✅ 本次完成 | Claude |

**P1审计项状态（来自L2 CONDITIONAL GO）：**

| P1项 | 状态 |
|------|------|
| P1-1：替代Holdout污染保护机制 | ⚠️ 待设计（Codex已在执行时自行做物理截断校验） |
| P1-2：旧状态文档过期快照 | ✅ 本次PROJECT_OPERATING_STATE更新至v2.0 |
| P1-3：避免治理文档继续扩张 | ✅ 本次未新增治理文档 |
| P1-4：回测自动测试 | ✅ pytest 9/9通过 |
| P1-5：失败知识系统化提炼 | ✅ v1/v2（v1知识库）+ v3/v4/v5（v2知识库）均已归档 |

---

## 5. 关键约束

- 每月预算：约1000元
- 可用时间：晚9点~2点，约1小时（有帮带孩子时）
- 交易本金上限：30,000元
- Founder角色：纯做最终确认（D级决策节点）
- 首要风险：风险C——连续失败后停留讨论层，失去实验节奏

---

*所有新任务在 Cowork 执行。*
