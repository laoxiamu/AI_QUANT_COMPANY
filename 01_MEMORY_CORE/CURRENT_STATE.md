# CURRENT_STATE.md

**版本：** 4.2（覆盖式看板制，依据双审计 P0-5 + DEC-069）
**最后更新：** 2026-06-15（A-1独立回弹Tier A FAILED→Dead;carry升主线迭代至v3;采集器纠正;Codex网络认知更正;§1b/§4/§1c/§等待Founder全量回写对齐）｜ **更新者：** Claude（CTO）
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
| **在途任务** | **A-1 路径A 已完结（2026-06-15）：** 五轮盲审 v1→v5 收敛 APPROVED → custodian 封 Holdout(work156/sealed38,AES-GCM,密钥项目外) → executor 跑 → **Tier A FAILED**(48h CAR +1.32% 但 Holm p=0.32 不显著,功效充分非欠功效) → **A-1 独立回弹判 Dead**(墓园+机会地图;不耗计数;OI信号降级为carry风控触发候选;前向路径休眠免费期权)。**carry 升主线（2026-06-15）：** v1→RR1(NOT APPROVED 8项,核心=用已探索工作集倒推设计HARKing)→v2(重构:历史=可行性复核不耗计数/前向shadow=真确认/证据等级上线)→RR2(NOT APPROVED 2/8,**重构获认**,余6项实现细节)→**v3起草中(Codex)**;carry回测脚手架25单测就绪。**采集器**:查实零采集(Binance限腾讯云IP的WS行情流,非代码bug)→修复(Codex danger-full-access,经住宅代理绕IP)跑中。**运行中Codex**:carry v3起草 + 采集器修复。git 已commit。|
| **§1b 活动工作区（Claude 对话级在途）** | **2026-06-15(最新)**：A-1路径A全程完结(v5 APPROVED→custodian封Holdout→executor跑→Tier A **FAILED**→A-1独立回弹**Dead**);carry升主线迭代中(v1→v2→RR2 2/8重构获认→**v3起草**);采集器查实零采集(Binance限云IP)修复中;Codex网络认知更正(网络/SSH活用`--sandbox danger-full-access`,workspace-write关shell网络)。**运行中Codex**:carry v3起草 + 采集器修复(danger-full-access)。**恢复点**:①carry v3出→CTO验收→派独立盲审CARRY-RR3→收敛APPROVED→custodian封Holdout→脚手架跑历史可行性复核(不耗计数/不上线);②采集器修复结果(成→路径B免费期权激活);③前向shadow确认协议待carry过审后设计。**勿再信旧"A1-RR/Tier A"恢复点(已完结)。**|
| **§1c 对话级建议暂存区** | **制度说明（DEC-073）**：本栏捕获对话中Claude提出但尚未落入§4的建议。Founder确认→升入§4/DECISION_LOG；Founder否决→清除；未响应=下次开局必提。**本轮新增（2026-06-14深夜，Founder委托CTO自主推进期间）：**①**[✅Claude执行完毕]** D2/A1-RR验收+专业透镜：两线均"需返工"属**正确返工**；D2 BLOCKED根因=D1"35/35完成"实为**数据不达用途**(下的contract klines非mark-price、缺真实funding、DEC-070四过滤无证据)→**过程教训：完成计数≠达用途，验收门须查数据适用性**(风险E反例修正)。②**[✅Claude执行完毕]** A-1预登记v2亲自主导改写(`A1_CASCADE_REBOUND_PREREG_v2.md`)，逐条闭合Reviewer十项(方向代理过滤/唯一主horizon=48h/cluster块bootstrap/refractory episode/A-2 P95 overlap/80%power MDE/两级门/现金零基准硬门/物理Holdout封存/闭合decision table)；**Codex三轮闭环**：v2盲审NOT APPROVED(仅闭2/10)→CTO据五项必改起草**v3**(`..._v3.md`:纯方向r6h<0/moving-block bootstrap/功效降诊断/A-2原口径单8H读数P95/沙箱外真权限Holdout)→**A1-RR3第三轮盲审运行中(PID 8335)**,特别要求判定剩余阻塞是否=历史样本不可约识别上限。③**[✅已决→DEC-075:暂缓优先A-1]** TSMOM universe扩展(D1v2+D2)**未执行**——CTO判断：扩样本是D级候选(Founder未批)+只解决DD不解决TSMOM核心"无可行定仓"+DEC-070两过滤需外部数据历史不可得，**强行连夜重采=风险D局部修补搜索**。**推荐：A-1优先级高于universe扩展**。DEC070审计(`20260614_dec070_filter_audit.md`)：2可算过滤器下Tier1-clean 20/35、watch 10/35、排除5/35(AXS/FTM/ICX高跳动/低流动);**审计抛专业异议——本地CSV只存base volume非quote volume(ADTV亦不精确)+float市值比/OI市值比需外部历史数据(Binance OI REST仅近1月)**,数据成本叠加,**强化暂缓**:若Founder坚持闭环TSMOM需先投入补quote volume+外部supply/mcap/OI,性价比低于A-1。④**[✅Claude执行完毕]** 跨对话回收(扫23会话)：唯一含在途未存工作的"外部调研(Sweep形态线)"——其做空测试**已在其他会话独立完成并封账**(v4多头"全维度无一可部署"、v5做空已失败,DEC 2026-06-06)，**无孤儿决策丢失**；工作区沙箱故障根因=claude-code-vm 2.1.170下载循环失败,Desktop Commander为正确通道。⑤**[议程·rule8]** A-1历史方向识别结构性局限→**前向强平数据路径**：历史A-1无真实强平名义额(采集器2026-06-13起前向)，v2只能用价格代理；最强验证仍需前向真实强平数据3-6月——把已部署采集器与A-1直接挂钩,是采集器首个明确alpha用途。⑥**[✅已决→DEC-075]** A-1两段式路径+universe暂缓**已经Founder"按推荐继续"确认,升格DEC-075**(③⑥出本栏)。**当前推进(2026-06-15)**：**路径A**=A-1预登记已迭代到**v5**(`..._v5.md`)。盲审进度:RR4判v4闭2/5(功效治理+family CLOSED),余4项判"文字与算法冻结、不要求达机制确证严格度"→v5逐条闭(§7改"A-2非重叠关联硬门"/circular半开网格`[t1,tn+1h)`+offset截断/Spearman改配对bootstrap对ρ居中真检验ρ=0/WF唯一切点中点+按实际足迹purge/AES-256-GCM+密钥独立principal+负向测试留命令退出码)→**A1-RR5第五轮盲审=✅APPROVED(4/4全闭,`A1_RISK_REVIEW_v5.md`)**!五轮收敛(10→2/10→0/5→2/5→4/4)。放行边界:仅关联结论/不耗独立计数/不晋级策略;**执行前须先AES-256-GCM Holdout封存+负向权限测试**。**[⚠️待Founder知会后派发]** 按预登记铁律,跑Tier A事件研究(封Holdout+出A-1生死判决)须Founder知会+主会话人工派发,故CTO停在放行点未自动跑;**路径B**=`A1_FORWARD_LIQUIDATION_PATH.md`已设计(采集器原始forceOrder含side方向字段已核实=首个alpha用途;就绪门=候选n达功效门→另立预登记走硬门耗计数;待数据累积3-6月,低成本并行不阻塞)。**⑥已闭（2026-06-15）**：A-1 Tier A 已跑 → **FAILED**(48h Holm p=0.32) → A-1独立回弹 **Dead**(墓园+机会地图);PB1脚手架完成。**⑦[已升格→§4]** carry升主线:v1→RR1→v2→RR2(2/8重构获认)→v3起草中;已入§4执行序与机会地图,非悬空建议。**⑧[已记]** 采集器查实零采集(Binance限云IP)→工具链已纠正;Codex网络认知更正(网络活用danger-full-access)。**⑨[环境·待Founder]** VM下载/DC断联:downloads.claude.ai走双跳拉不动53MB二进制,Founder已加Clash单跳规则但下载仍truncate(2核跳板带宽不足),Founder选C忍着(不阻塞research,A-1/carry均nohup扛断)。网络拓扑已记忆([[network-proxy-topology]])。**⑩[核实项·已派Codex]** Founder线索:服务器有历史v4.6.2(数据源也是币安,疑v4-strategy-runner)。**若v4.6.2能正常取币安数据→可能推翻"Binance封本IP"结论**(我只测了futures公共WS forceOrder,v4.6.2或用REST/现货/不同端点/鉴权)。已派`VERIFY_V462`(Codex danger-full-access)核实其数据源+对照,出修采集器正路。**本栏其余无悬空建议（carry在§4,A-1在墓园,采集器在工具链）。**|
| **等待 Founder** | **无阻塞项。** A-1已完结(Tier A FAILED→Dead,无需Founder)。carry处于可行性研究阶段(历史复核+前向shadow),**通过后核心资本上线才是D级**(未来,DEC-019范围,按DEC-069证据等级解锁)。 |
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
| 强平采集器 | ⚠️ **实为零采集（2026-06-14 查实，纠正旧"生产运行中"假状态）**：service active 但 22h `process_messages=0`。根因=**Binance 对腾讯云SG服务器IP的WS行情流限制**（REST fapi HTTP200正常，但 aggTrade/forceOrder WS 握手OPEN后0帧——云IP被限推送）。**非代码bug**（ping+重连正常）。教训=信了"service active"未验真实数据流（风险E/A）。**根因查实（2026-06-15 VERIFY-V462，纠正先前"封IP"误判）**：**非IP封锁，是Binance 2026-04-23 WS路由迁移**。旧URL`wss://fstream.binance.com/ws/!forceOrder@arr`→0帧；**新路由`/market/ws/!forceOrder@arr`→立即收帧**（同机对照+历史v4.6.2 REST直连可用佐证）。**修法极简=改WS_URL路径,无需鉴权/代理**(Codex修复+验证中)。OI/funding改用REST(`/fapi/v1/openInterest`,`/futures/data/openInterestHist`,`/fapi/v1/fundingRate`)。修好后采集器即可正常攒数→路径B免费期权激活 |
| 定时任务 | ⚠️ 周监控/月审 v2 已更新口径；夜间定时不可靠（两次事故），跑批优先 Codex nohup |
| 腾讯云轻量（SG） | ✅ 活跃——采集器已部署 `/opt/ai_quant_liq_collector/`，现有服务（danted/v4-proxy/v4-strategy-runner/docker/nginx）未受影响；审计 P2-4 **已销项** |

## 3. 关键约束（不变）

月预算约 1000 元｜Founder 时间约 1h/天、只批 D 级、无技术背景｜本金上限 30,000（DEC-015 阶梯）｜首要行为风险=风险B/C（治理膨胀/停留讨论层）

## 4. 任务计划台账（单一持久来源·四态齐全，2026-06-15）

> 本节=项目持久任务计划（Cowork任务widget仅会话级辅助、不持久、无废弃态，不作准）。状态：🟢进行中/⚪待执行/✅已完成里程碑/⛔已废弃(→墓园)。

**🟢 进行中（Codex nohup）**
1. carry v4 起草（闭 RR3 剩余:资本USDT计价账/1H强平路径/交易小时PnL）→ 完成派 CARRY-RR4。
2. 采集器一行修复（WS_URL→`/market/ws/`,根因=Binance 2026-04-23路由迁移非封IP）+ 验证收帧。

**⚪ 待执行（链路）**
3. carry v4→RR4→收敛APPROVED→custodian封Holdout→脚手架(25单测)跑**历史可行性复核**(不耗计数/不上线)。
4. carry过历史复核→设计**前向shadow确认协议**(纸面攒独立月)→达门→DEC-069证据等级解锁小额真金(**D级·Founder**)。
5. 采集器修好→路径B免费期权激活被动攒强平数据(就绪门倒计时)。
6. 【等Founder D级】审阅 `OPERATING_MODEL_DESIGN_v2.md`。
7. A-4=Candidate第8命排队；空头独立机制另案(先查墓园)。

**✅ 已完成里程碑（本阶段）**
- A-1路径A五轮盲审APPROVED→Tier A执行→FAILED→判Dead（见⛔）。DEC-075落账。E2验收。DEC070审计。跨对话回收。state-sync全量对齐(§1b/§4/§1c/§等待Founder)。采集器根因查实纠正。

**⛔ 已废弃（→GRAVEYARD_INDEX + OPPORTUNITY_MAP，不复活）**
- A-1独立回弹(2026-06-15 FAILED,Holm p=0.32)｜A-2 funding反转｜Sweep形态(多头无可部署/做空失败)｜TSMOM引擎S镜像做空/v2风险预算｜裸卖VRP｜TSMOM universe扩展(DEC-075暂缓,非废弃但不推进)。
- **A-1前向真实强平=休眠免费期权（非废弃,待采集器攒数据+无更优方向才重启）。**

## 5. 启动协议

见 **CLAUDE.md v2.3「新对话启动协议」**（BOOT_BRIEF → 本文件 → DECISION_LOG索引 → 四蓝图）。本文件不再维护独立清单。
