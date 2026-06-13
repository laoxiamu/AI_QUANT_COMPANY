# CURRENT_STATE.md

**版本：** 4.2（覆盖式看板制，依据双审计 P0-5 + DEC-069）
**最后更新：** 2026-06-14 深夜（Founder委托CTO自主推进：A-1预登记v2→v3三轮盲审闭环、D2/A1-RR验收+专业透镜、跨对话回收、universe扩展D级推荐、E2验收）｜ **更新者：** Claude（CTO）
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
| **验收口径** | **v1.3/v1.4 增补件已完成**（§一~§九：四件套+成本压力档+相关性+事件规则+第五件基准对照+MDE功效门+AI三行+叙事纪律+自动化边界），文件 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` |
| **在途任务** | ✅E2验收通过(02_SYSTEM_ARCHITECTURE,五层架构+TrackA/B)｜✅D2/A1-RR完成但均"需返工"(**正确返工**:独立审查在污染Holdout/浪费算力前抓出问题)：D2=BLOCKED(D1数据不达用途)、A1-RR=NOT APPROVED(10项必改)。**进行中(2026-06-14深夜,Founder委托CTO自主推进)**：A1-RR2=A-1预登记v2第二轮独立盲审(Codex gpt-5.5,PID 2081,收敛NOT APPROVED)｜DEC070-AUDIT=universe过滤器可审计性审计(Codex gpt-5.5,PID 4142)。**Claude已执行**：A-1 v2亲自改写、跨对话回收(无孤儿)、E2验收、git锁清。|
| **§1b 活动工作区（Claude 对话级在途）** | **2026-06-14深夜(最新)**：Founder睡前委托CTO自主推进。已完成：D2/A1-RR验收+专业透镜、A-1预登记v2主导改写、跨对话回收、E2验收、git锁清。**运行中**：A1-RR2盲审(PID 2081)+DEC070审计(PID 4142)。**恢复点**：①A1-RR2出结果→读→若NOT APPROVED且修改在CTO权限内→起草A-1 v3再盲审(自主闭环,不等Founder)；②DEC070审计出→并入universe D级决策包(§1c③)。|
| **§1c 对话级建议暂存区** | **制度说明（DEC-073）**：本栏捕获对话中Claude提出但尚未落入§4的建议。Founder确认→升入§4/DECISION_LOG；Founder否决→清除；未响应=下次开局必提。**本轮新增（2026-06-14深夜，Founder委托CTO自主推进期间）：**①**[✅Claude执行完毕]** D2/A1-RR验收+专业透镜：两线均"需返工"属**正确返工**；D2 BLOCKED根因=D1"35/35完成"实为**数据不达用途**(下的contract klines非mark-price、缺真实funding、DEC-070四过滤无证据)→**过程教训：完成计数≠达用途，验收门须查数据适用性**(风险E反例修正)。②**[✅Claude执行完毕]** A-1预登记v2亲自主导改写(`A1_CASCADE_REBOUND_PREREG_v2.md`)，逐条闭合Reviewer十项(方向代理过滤/唯一主horizon=48h/cluster块bootstrap/refractory episode/A-2 P95 overlap/80%power MDE/两级门/现金零基准硬门/物理Holdout封存/闭合decision table)；Codex第二轮盲审运行中。③**[⚠️待Founder D级·CTO推荐]** TSMOM universe扩展(D1v2+D2)**今晚未执行**——CTO判断：扩样本是D级候选(Founder未批)+只解决DD不解决TSMOM核心"无可行定仓"+DEC-070两过滤需外部数据历史不可得，**强行连夜重采=风险D局部修补搜索**。**推荐：A-1优先级高于universe扩展；若Founder要闭环TSMOM，先看DEC070部分审计再D级决定是否值得补外部数据**。④**[✅Claude执行完毕]** 跨对话回收(扫23会话)：唯一含在途未存工作的"外部调研(Sweep形态线)"——其做空测试**已在其他会话独立完成并封账**(v4多头"全维度无一可部署"、v5做空已失败,DEC 2026-06-06)，**无孤儿决策丢失**；工作区沙箱故障根因=claude-code-vm 2.1.170下载循环失败,Desktop Commander为正确通道。⑤**[议程·rule8]** A-1历史方向识别结构性局限→**前向强平数据路径**：历史A-1无真实强平名义额(采集器2026-06-13起前向)，v2只能用价格代理；最强验证仍需前向真实强平数据3-6月——把已部署采集器与A-1直接挂钩,是采集器首个明确alpha用途。|
| **等待 Founder** | **[D级·CTO推荐待批]** TSMOM universe扩展是否值得投入(补mark-price+funding重采+外部市值/OI数据)——CTO推荐**暂缓,优先A-1**(理由见§1c③)。无其他阻塞项。 |
| **禁引用措辞** | "极端拥挤=延续"（墓园 2026-06-12 勘误，不显著点估计不得作结论） |

## 2. 工具链

| 工具 | 状态 |
|---|---|
| Claude Cowork + Desktop Commander | ✅ 主工作区 + Mac 执行通道 |
| **Codex CLI 直调** | ✅ **2026-06-11 验证**（配方 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`：代理env + </dev/null + workspace-write；AGENTS.md 已部署项目根）|
| 低模型执行层 | ✅ 两次任务包验收通过；边界收紧（DEC-069 后只做逐字/格式/索引，禁触权威语义）|
| Python 3.13 量化环境 / VectorBT / pytest | ✅ |
| git + GitHub 私库 | ✅ `laoxiamu/AI_QUANT_COMPANY`（deploy key，验收后推送制）|
| 强平采集器 | ✅ **VM 直跑，生产运行中（2026-06-13）**：`aiquant-liq-collector.service` active，MainPID=2550847，`/opt/ai_quant_liq_collector/data/LIQUIDATIONS/`；直连 Binance WS 已验证真实数据帧（btcusdt@trade 0.247s 3帧）；双审计 P0-1 **已销项** |
| 定时任务 | ⚠️ 周监控/月审 v2 已更新口径；夜间定时不可靠（两次事故），跑批优先 Codex nohup |
| 腾讯云轻量（SG） | ✅ 活跃——采集器已部署 `/opt/ai_quant_liq_collector/`，现有服务（danted/v4-proxy/v4-strategy-runner/docker/nginx）未受影响；审计 P2-4 **已销项** |

## 3. 关键约束（不变）

月预算约 1000 元｜Founder 时间约 1h/天、只批 D 级、无技术背景｜本金上限 30,000（DEC-015 阶梯）｜首要行为风险=风险B/C（治理膨胀/停留讨论层）

## 4. 下一步（执行序，2026-06-14 深夜更新）

1. 【Claude自主闭环·进行中】A1-RR2第二轮盲审(Codex PID 2081)出结果→读→若NOT APPROVED且修改在CTO权限内→起草A-1 v3再盲审,直到APPROVED或判定停机;不等Founder唤醒。
2. 【Claude·进行中】DEC070-AUDIT(Codex PID 4142)出结果→并入universe D级决策包,精确量化Tier1-clean资产数+外部数据缺口。
3. 【等Founder D级】TSMOM universe扩展是否投入(CTO推荐暂缓,优先A-1,见§1c③)。
4. 【等Founder D级】审阅 `OPERATING_MODEL_DESIGN_v2.md`（产研三循环流程+版本标准）。
5. 【Claude】A-1 v2(或最终APPROVED版)通过盲审后→Founder知会→主会话人工派发事件研究(Tier A),先过§12物理Holdout封存。
6. 【议程·rule8】前向强平采集器→A-1前向验证路径设计(采集器首个明确alpha用途,见§1c⑤)。
7. 空头方向：独立机制假设另案研究（非镜像TSMOM），先查墓园；Sweep做空已封账(失败),不复活。

## 5. 启动协议

见 **CLAUDE.md v2.3「新对话启动协议」**（BOOT_BRIEF → 本文件 → DECISION_LOG索引 → 四蓝图）。本文件不再维护独立清单。
