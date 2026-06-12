# CURRENT_STATE.md

**版本：** 4.0（覆盖式看板制，依据双审计 P0-5 + DEC-069）
**最后更新：** 2026-06-12 ｜ **更新者：** Claude（主理人/CTO）
**历史沿革：** v3.x 滚动记录已归档 `01_MEMORY_CORE/ARCHIVE/STATE_LOG_20260607_0612.md` 及 git 历史
**维护规则：** 本文件为**固定槽位覆盖式看板**——更新=改写槽位内容，不追加滚动条；超过 150 行即违规（state_check 查）。

---

## 1. 状态看板

| 槽位 | 当前值 |
|---|---|
| **阶段** | Phase 1（找真实 edge）。公司 OS **原则层已冻结**（DEC-068②/069②：目标函数/两层资本/机制优先/验收纪律/权威层级）；机会地图与运行层 = v0.x 可迭代，运行层升 v1 条件="连续14天定时任务零卡死+state_check零漂移" |
| **机会地图** | 见 `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md`（DEC-069③）：TSMOM=**Baseline**｜A-1=Conditional（四门）｜A-4=Candidate｜carry=核算中｜funding/OI=状态变量｜A-2=**Dead** |
| **失败计数（DEC-069①）** | 旧范式 5 条封账（历史合计 11 次失败存档）；**新范式独立计数=1**（a2，2026-06-11）；计数=L3触发器（每+2触发复评）。**项目主闸=时间盒（2026-06-07 重置起 6 个月无 edge）+成本盒（5000 元，已用 871.93）+L3 裁量** |
| **Holdout** | 全部封存完好（含 a2 事件级 Holdout 218 条）；任何实验未读取 |
| **验收口径** | v1.3 增补件四件套 + 待补 v1.4：第五件"状态匹配被动基准超额>0" + MDE 功效门 + AI evidence 3 行（起草中） |
| **在途任务** | ①已收：universe PIT✅ / carry核算✅（sleeve候选）/ **双引擎✅：L 仅败于爆仓概率门（信号活、基准超额+168k）→ 下一步=风险预算版变体预登记；S 镜像做空 FAILED 入墓园** ②待 Claude 复核：P1-04/06 第五件追溯负超额数字异常 ③Holdout 事故记录：Codex 会话 rg 范围过宽显示过 a2 events holdout 行（未入计算、a2已Dead、影响=无；任务模板已加排除条款待办）④采集器：节点仍掐WS，**转 VM 方案待 Founder**|
| **等待 Founder** | 云服务器方案确认（见对话说明：~30-60元/月，部署我来）|
| **禁引用措辞** | "极端拥挤=延续"（墓园 2026-06-12 勘误，不显著点估计不得作结论） |

## 2. 工具链

| 工具 | 状态 |
|---|---|
| Claude Cowork + Desktop Commander | ✅ 主工作区 + Mac 执行通道 |
| **Codex CLI 直调** | ✅ **2026-06-11 验证**（配方 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`：代理env + </dev/null + workspace-write；AGENTS.md 已部署项目根）|
| 低模型执行层 | ✅ 两次任务包验收通过；边界收紧（DEC-069 后只做逐字/格式/索引，禁触权威语义）|
| Python 3.13 量化环境 / VectorBT / pytest | ✅ |
| git + GitHub 私库 | ✅ `laoxiamu/AI_QUANT_COMPANY`（deploy key，验收后推送制）|
| 强平采集器 | 🔴 部署完毕但代理节点掐 WebSocket，零数据——**双审计 P0-1** |
| 定时任务 | ⚠️ 周监控/月审 v2 已更新口径；夜间定时不可靠（两次事故），跑批优先 Codex nohup |
| 腾讯云轻量（SG） | ⚠️ 状态未知——查明后要么做采集器迁移要么销户（审计 P2-4）|

## 3. 关键约束（不变）

月预算约 1000 元｜Founder 时间约 1h/天、只批 D 级、无技术背景｜本金上限 30,000（DEC-015 阶梯）｜首要行为风险=风险B/C（治理膨胀/停留讨论层）

## 4. 下一步（执行序）

1. 【Codex 在途】universe 数据资产 + carry 核算（验收后进 TSMOM 扩样本预登记）。
2. 【Claude】Protocol v1.4 增补（MDE门/第五件/AI evidence）→ TSMOM 扩样本预登记（多空两引擎+universe+基准对照）→ A-1 四门评估。
3. 【低模型】治理三件套（AGENT_REGISTRY / RUN_LOG.jsonl / no-holdout lint）。
4. 【Founder】采集器节点/VM；（可选）腾讯云状态查明。
5. 运行层可靠性观察期计时中（升 v1 冻结条件见 §1）。

## 5. 启动协议

见 **CLAUDE.md v2.3「新对话启动协议」**（BOOT_BRIEF → 本文件 → DECISION_LOG索引 → 四蓝图）。本文件不再维护独立清单。
