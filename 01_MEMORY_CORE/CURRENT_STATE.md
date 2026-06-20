# CURRENT_STATE.md

**版本：** 4.4（2026-06-20 审计后全项目重组；§1c 清空历史叙事，写入真正悬空 D 级项）
**最后更新：** 2026-06-20（四棱镜审计+OSS调研已完成；方向重校准=借力最小闭环/实盘NO-GO/6月目标重定；全项目重组进行中）｜ **更新者：** Claude
**历史沿革：** v3.x 滚动记录已归档 `01_MEMORY_CORE/ARCHIVE/STATE_LOG_20260607_0612.md` 及 git 历史
**维护规则：** 本文件为**固定槽位覆盖式看板**——更新=改写槽位内容，不追加滚动条；超过 150 行即违规（state_check 查）。

---

## 1. 状态看板

| 槽位 | 当前值 |
|---|---|
| **阶段** | Phase 1（找真实 edge）。公司 OS **原则层已冻结**（DEC-068②/069②：目标函数/两层资本/机制优先/验收纪律/权威层级）；机会地图与运行层 = v0.x 可迭代，运行层升 v1 条件="连续14天定时任务零卡死+state_check零漂移" |
| **机会地图** | 见 `OPPORTUNITY_MAP_STATUS.md`：TSMOM=**Baseline**｜**A-1独立回弹=Dead（2026-06-15历史快筛FAILED，48h+1.32% Holm p=0.32不显著；OI信号降级为carry风控触发候选；前向路径休眠免费期权）**｜**carry=最高优先活体方向（升主线，下一步起草正式预登记含A-1×Carry交互）**｜A-4=Candidate｜funding/OI=State｜A-2=Dead |
| **失败计数（DEC-069①）** | 旧范式 5 条封账（历史合计 11 次失败存档）；**新范式独立计数=1**（a2，2026-06-11）；计数=L3触发器（每+2触发复评）。**项目主闸=时间盒（2026-06-07 重置起 6 个月无 edge）+成本盒（5000 元，已用 871.93）+L3 裁量** |
| **Holdout** | 全部封存完好（含 a2 事件级 Holdout 218 条）；任何实验未读取 |
| **验收口径** | **v1.3/v1.4 增补件已完成**（§一~§九：四件套+成本压力档+相关性+事件规则+第五件基准对照+MDE功效门+AI三行+叙事纪律+自动化边界），文件 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` |
| **在途任务** | **carry=唯一执行主线（P1-RES-030）**：carry v4预登记APPROVED(五轮盲审v1→v5收敛)，历史FEASIBILITY-LOCK **🔴阻塞**（custodian封存需主会话写项目外密钥，Codex沙箱做不了→需主会话人工操作chmod-000法，参A1_RISK_REVIEW_v5 §12）。**A-1独立回弹=Dead**（历史快筛FAILED Holm p=0.32，OI信号降级为carry风控触发候选，前向路径B=免费期权积累中）。**强平采集器=已修复收数**（2026-06-15，Binance WS路由迁移`/market/ws/`，已收92帧，路径B激活）。**TSMOM=Baseline**（定仓维度穷尽，universe扩展按DEC-075暂缓）。 |
| **§1b 活动工作区（Claude 对话级在途）** | **2026-06-20（重组进行中）**：四棱镜独立审计完成（A1-A4+OSS调研）；方向重校准=借力最小闭环/实盘NO-GO/6月目标重定；全项目重组当前执行：①§1c清空✅ ②PROJECT_TASK_PLAN更新（借力路线+kill/pivot）⬜ ③能力/假设登记表⬜ ④Codex归档任务书⬜ ⑤BOOT_BRIEF同步⬜。**恢复点**：重组完成后首要任务=解决carry FEASIBILITY-LOCK阻塞（主会话做custodian封存）→然后派Codex跑历史可行性复核。 |
| **§1c 对话级建议暂存区** | **制度说明（DEC-073）**：本栏捕获Claude提出但Founder尚未响应的建议。确认→升入§4/DECISION_LOG；否决→清除；未响应=下次开局必提。**当前悬空（2026-06-20，审计后，待Founder一次确认）：** ①【系统路线D级】砍成最小借力闭环（Freqtrade+CCXT+官方数据+CoinGlass）替代自建重型五层？OSS调研结论强烈推荐=是，见`STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md`。 ②【carry严谨度D级】将carry验证严谨度从”18-24月学术级shadow”下调为”几月纸面+小额真钱+硬风控”？审计推荐=是（与3万在险资金体量对齐）。 ③【6月目标D级】将6月目标从”找到可部署edge”重定为”验证edge是否值得继续”并设kill/pivot条件？审计推荐=是（最没被质疑的假设=公开数据AI在6月内找到可交易edge）。 ④【公司终态D级】确认推荐终态与Phase 0-3阶段门（P0-STR-005，见总图§2/§6/§9）？此项2026-06-15已挂起，仍未响应。 |
| **等待 Founder** | **4项D级待一次确认**（见§1c ①②③④）。当前无研究阻塞——carry FEASIBILITY-LOCK阻塞=Claude操作项（custodian封存），不需Founder。 |
| **禁引用措辞** | "极端拥挤=延续"（墓园 2026-06-12 勘误，不显著点估计不得作结论） |

## 2. 工具链

| 工具 | 状态 |
|---|---|
| Claude Cowork + Desktop Commander | ✅ 主工作区 + Mac 执行通道 |
| **Codex CLI 直调** | ✅ **2026-06-11 验证**（配方 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`：代理env + </dev/null + workspace-write；AGENTS.md 已部署项目根）|
| **Codex Skills** | ✅ **2026-06-14 安装扩展**：PlanToDelivery、find-skills、女娲、达尔文、TDD/diagnose/architecture/to-issues、`obra/superpowers`完整14 skill；加密合约专项skill已按perp/funding/OI/强平/微观结构重搜，交易所/API类暂不自动装。记录见 `00_PROJECT_MANAGEMENT/CODEX_SKILLS_INSTALL_LOG_2026-06-14.md`。需重启 Codex 后新会话识别 |
| 低模型执行层 | ✅ 两次任务包验收通过；边界收紧（DEC-069 后只做逐字/格式/索引，禁触权威语义）|
| Python 3.13 量化环境 / VectorBT / pytest | ✅ |
| git + GitHub 私库 | ✅ `laoxiamu/AI_QUANT_COMPANY`（deploy key，验收后推送制）|
| 强平采集器 | ✅ **已修复并收数（2026-06-15）**：改 WS_URL→`/market/ws/!forceOrder@arr`(根因=Binance 2026-04-23路由迁移,非封IP,v4.6.2线索查实)→重启后**收到92帧**,LIQUIDATIONS 开始增长→路径B免费期权激活。曾误判经历:⚠️先以为零采集/封IP：service active 但 22h `process_messages=0`。根因=**Binance 对腾讯云SG服务器IP的WS行情流限制**（REST fapi HTTP200正常，但 aggTrade/forceOrder WS 握手OPEN后0帧——云IP被限推送）。**非代码bug**（ping+重连正常）。教训=信了"service active"未验真实数据流（风险E/A）。**根因查实（2026-06-15 VERIFY-V462，纠正先前"封IP"误判）**：**非IP封锁，是Binance 2026-04-23 WS路由迁移**。旧URL`wss://fstream.binance.com/ws/!forceOrder@arr`→0帧；**新路由`/market/ws/!forceOrder@arr`→立即收帧**（同机对照+历史v4.6.2 REST直连可用佐证）。**修法极简=改WS_URL路径,无需鉴权/代理**(Codex修复+验证中)。OI/funding改用REST(`/fapi/v1/openInterest`,`/futures/data/openInterestHist`,`/fapi/v1/fundingRate`)。修好后采集器即可正常攒数→路径B免费期权激活 |
| 定时任务 | ⚠️ 周监控/月审 v2 已更新口径；夜间定时不可靠（两次事故），跑批优先 Codex nohup |
| 腾讯云轻量（SG） | ✅ 活跃——采集器已部署 `/opt/ai_quant_liq_collector/`，现有服务（danted/v4-proxy/v4-strategy-runner/docker/nginx）未受影响；审计 P2-4 **已销项** |

## 3. 关键约束（不变）

月预算约 1000 元｜Founder 时间约 1h/天、只批 D 级、无技术背景｜本金上限 30,000（DEC-015 阶梯）｜首要行为风险=风险B/C（治理膨胀/停留讨论层）

## 4. 当前焦点与任务计划指针（2026-06-20）

> **详细任务单一权威：** `00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md`。本节不再复制全量 WBS；对话中的新增、调整、阻塞、完成、废弃和决策，必须当轮写回该计划书。

- **当前唯一执行主线：** `P1-RES-030`，carry v4 历史 FEASIBILITY-LOCK；🔴阻塞=custodian封存待主会话操作。解除后派 Codex 跑历史复核（不耗计数/不读Holdout/不授权上线）。
- **方向重校准（2026-06-20 审计后）：** 系统路线=借力最小闭环（Freqtrade+CCXT+官方数据）；实盘=有条件NO-GO（实时风控/账本/对账全没建）；6月目标=验证edge是否值得继续+设kill/pivot条件。
- **被动并行：** 强平采集器已修复并收数；A-1 路径 B 继续积累真实强平数据（就绪门=功效门后另立预登记）。
- **明确暂缓：** TSMOM universe 扩展按 DEC-075 保持调整态；A-1 独立回弹保持 Dead，不得复活或改写为”部分成功”。
- **中断恢复：** 对话级未完成步骤仍写 §1b；恢复后先核对 `PROJECT_TASK_PLAN.md` 对应任务 ID，再继续执行。

## 5. 启动协议

见 **CLAUDE.md v2.3「新对话启动协议」**（BOOT_BRIEF → 本文件 → DECISION_LOG索引 → 四蓝图）。本文件不再维护独立清单。
