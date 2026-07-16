# REPORT_P1PIPE_SUMMARY

**任务链**：P1-RES-039-PIPELINE｜P1 解锁数据管线 + B1-KILLCARD 前置数据门  
**执行时间**：2026-06-27 UTC  
**最终状态**：停在 Step 3，未进入 Step 4  
**纪律声明**：未碰 Holdout；未进 B2；未下最终 KILL/PROCEED 裁决；未用付费 API；未把文章样本冒充全量。

## 总结论

**数据管线前两步解锁了价格面板与 OI/funding，但 unlock event 免费源失败，B1-KILLCARD 不可执行。**

关键判断：P1 机制没有被本轮数据直接证伪；被证伪的是“当前免费公开源足以支撑 post-2025 解锁事件普查”的数据假设。在现有免费边界下，overlap episode=0，低于 Step 4 的 ≥50 硬门槛，因此必须停止。

## 四步状态

| Step | 状态 | 结论 |
|---|---|---|
| S1 面板完整性 | completed | `FUTURES_EXPANDED_2026` 有 31 个 4H symbol，全部到 `2026-06-22 00:00:00`；旧新接缝连续；post-2025 事件可用 universe=31 |
| S2 OI/funding 回填 | completed | 输出新目录 `06_RESEARCH/DATA/FUTURES_OI_FUNDING_2026/`；31 个 symbol 均有 OI/funding 文件；近端 OI 可用 29 个，近端 OI+funding 完整可用 25 个 |
| S3 解锁日历 + overlap | blocked | DefiLlama emissions 402；Tokenomist API/CSV/历史全量不在免费边界；免费结构化事件数=0，overlap episode=0 |
| S4 B1-KILLCARD | not executed | S3 episode < 50，按硬护栏不执行 |

## 产出文件

| 类型 | 路径 |
|---|---|
| S1 报告 | `04_AI_TEAM/CODEX_TASKS/REPORT_P1PIPE_S1_PANEL.md` |
| S1 JSON | `06_RESEARCH/CODE/output/p1pipe_s1_panel_audit.json` |
| S1 脚本 | `06_RESEARCH/CODE/p1pipe_s1_panel_audit.py` |
| S2 报告 | `04_AI_TEAM/CODEX_TASKS/REPORT_P1PIPE_S2_OIFUNDING.md` |
| S2 JSON | `06_RESEARCH/CODE/output/p1pipe_s2_oifunding_audit.json` |
| S2 数据 | `06_RESEARCH/DATA/FUTURES_OI_FUNDING_2026/` |
| S2 manifest | `06_RESEARCH/DATA/FUTURES_OI_FUNDING_2026/manifest.json` |
| S2 脚本 | `06_RESEARCH/CODE/p1pipe_s2_oifunding_backfill.py`；`06_RESEARCH/CODE/p1pipe_s2_funding_rest_supplement.py` |
| S3 报告 | `04_AI_TEAM/CODEX_TASKS/REPORT_P1PIPE_S3_UNLOCK.md` |
| S3 JSON | `06_RESEARCH/CODE/output/p1pipe_s3_unlock_source_audit.json` |
| S3 事件 CSV | `06_RESEARCH/CODE/output/p1pipe_s3_free_unlock_events.csv` |
| S3 脚本 | `06_RESEARCH/CODE/p1pipe_s3_unlock_source_audit.py` |
| TASK_INBOX | `P1-RES-039-PIPELINE-S1_DONE.json`；`S2_DONE.json`；`S3_DONE.json`（已被调度器移入 `04_AI_TEAM/TASK_INBOX/PROCESSED/`） |

## 给 Claude 的第一裁决清单

1. **是否允许引入可审计 unlock event 数据源。**  
   当前免费边界不够；若继续 P1 解锁线，需要 Tokenomist/DefiLlama Pro/API trial/CSV 或其他可审计历史事件表，字段至少含 `symbol, unlockDate, amount/value, supply pct, allocation, source/update time`。

2. **是否把 P1 解锁线降级为“数据工程待解锁”。**  
   建议不要把这次写成机制 KILL；应写成“数据门 blocked”。原因是价格/OI/funding 基础腿已就绪，失败点只在事件表。

3. **若拿到事件表，下一次 B1 的过滤口径。**  
   先用 S1/S2 的可用性过滤：post-2025 价格 universe=31；近端 OI 完整=29；近端 OI+funding 完整=25。事件落在 `FTM/REN/LRC/UNI/XMR/XTZ` 缺口后，不能做完整资金流分档或 ex-funding 拆账。

4. **是否扩展替代事件类。**  
   若 unlock 历史数据继续不可得，可考虑上币公告/宏观/脱锚，但必须重新 B0/B1 数据门，不得把本轮 unlock 失败结果迁移成其他事件类证据。

## 专业判断

这次最有价值的结果不是 episode=0，而是把 P1 的瓶颈精确定位了：价格腿和结构资金流腿已经能支撑 post-2025 事件研究，真正卡死的是“免费 unlock event 全量历史表”。因此 Claude 回来后不该让 Codex 继续在网页/文章里挖样本；应先裁决数据源边界。没有事件表，B1 的 price-in、单调性、成本门和 MDE 全都只是形式动作。
