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
| **机会地图** | 见 `OPPORTUNITY_MAP_STATUS.md`：TSMOM=**Baseline**｜**A-1独立回弹=Dead（2026-06-15历史快筛FAILED，48h+1.32% Holm p=0.32不显著；OI信号降级为carry风控触发候选；前向路径休眠免费期权）**｜**carry=最高优先活体方向（升主线，下一步起草正式预登记含A-1×Carry交互）**｜A-4=Candidate｜funding/OI=State｜A-2=Dead |
| **失败计数（DEC-069①）** | 旧范式 5 条封账（历史合计 11 次失败存档）；**新范式独立计数=1**（a2，2026-06-11）；计数=L3触发器（每+2触发复评）。**项目主闸=时间盒（2026-06-07 重置起 6 个月无 edge）+成本盒（5000 元，已用 871.93）+L3 裁量** |
| **Holdout** | 全部封存完好（含 a2 事件级 Holdout 218 条）；任何实验未读取 |
| **验收口径** | **v1.3/v1.4 增补件已完成**（§一~§九：四件套+成本压力档+相关性+事件规则+第五件基准对照+MDE功效门+AI三行+叙事纪律+自动化边界），文件 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` |
| **在途任务** | ✅E2验收通过(02_SYSTEM_ARCHITECTURE,五层架构+TrackA/B)｜✅D2/A1-RR完成但均"需返工"(**正确返工**:独立审查在污染Holdout/浪费算力前抓出问题)：D2=BLOCKED(D1数据不达用途)、A1-RR=NOT APPROVED(10项必改)。**2026-06-14深夜CTO自主完成**：A-1预登记**三轮盲审闭环**(v1→v2→v3全NOT APPROVED,RR3给出不可约性裁定+D级岔路,见§1c⑥)｜DEC070-AUDIT完成(Tier1-clean 20/35,2过滤需外部数据)｜D2/A1-RR验收+专业透镜｜跨对话回收(无孤儿)｜E2验收。**2026-06-15(Founder按推荐继续→DEC-075)**：A-1路径A迭代v4→**v5**(RR4闭2/5+v5闭余4冻结)+Protocol功效门增补件+路径B前向通道设计 已落；**A1-RR5第五轮盲审运行中(Codex PID 43107)**。git已commit(至v5)。|
| **§1b 活动工作区（Claude 对话级在途）** | **2026-06-14深夜(最新)**：Founder睡前委托CTO自主推进。已完成：D2/A1-RR验收+专业透镜、A-1预登记v2主导改写、跨对话回收、E2验收、git锁清。**2026-06-15(最新)**：Founder"按推荐继续"→DEC-075落账(A-1两段式+universe暂缓)。已完成:DEC-075、A-1 v4(路径A)、Protocol功效门增补件、路径B前向通道设计。**运行中**:A1-RR4第四轮盲审(Codex PID 33140)。**恢复点**:RR4出→APPROVED则派发Tier A历史快筛(先过§12加密Holdout封存+负向权限测试),否则按关联快筛合理标尺评估是否修v5。路径B待数据累积(就绪门),低成本并行。|
| **§1c 对话级建议暂存区** | **制度说明（DEC-073）**：本栏捕获对话中Claude提出但尚未落入§4的建议。Founder确认→升入§4/DECISION_LOG；Founder否决→清除；未响应=下次开局必提。**本轮新增（2026-06-14深夜，Founder委托CTO自主推进期间）：**①**[✅Claude执行完毕]** D2/A1-RR验收+专业透镜：两线均"需返工"属**正确返工**；D2 BLOCKED根因=D1"35/35完成"实为**数据不达用途**(下的contract klines非mark-price、缺真实funding、DEC-070四过滤无证据)→**过程教训：完成计数≠达用途，验收门须查数据适用性**(风险E反例修正)。②**[✅Claude执行完毕]** A-1预登记v2亲自主导改写(`A1_CASCADE_REBOUND_PREREG_v2.md`)，逐条闭合Reviewer十项(方向代理过滤/唯一主horizon=48h/cluster块bootstrap/refractory episode/A-2 P95 overlap/80%power MDE/两级门/现金零基准硬门/物理Holdout封存/闭合decision table)；**Codex三轮闭环**：v2盲审NOT APPROVED(仅闭2/10)→CTO据五项必改起草**v3**(`..._v3.md`:纯方向r6h<0/moving-block bootstrap/功效降诊断/A-2原口径单8H读数P95/沙箱外真权限Holdout)→**A1-RR3第三轮盲审运行中(PID 8335)**,特别要求判定剩余阻塞是否=历史样本不可约识别上限。③**[✅已决→DEC-075:暂缓优先A-1]** TSMOM universe扩展(D1v2+D2)**未执行**——CTO判断：扩样本是D级候选(Founder未批)+只解决DD不解决TSMOM核心"无可行定仓"+DEC-070两过滤需外部数据历史不可得，**强行连夜重采=风险D局部修补搜索**。**推荐：A-1优先级高于universe扩展**。DEC070审计(`20260614_dec070_filter_audit.md`)：2可算过滤器下Tier1-clean 20/35、watch 10/35、排除5/35(AXS/FTM/ICX高跳动/低流动);**审计抛专业异议——本地CSV只存base volume非quote volume(ADTV亦不精确)+float市值比/OI市值比需外部历史数据(Binance OI REST仅近1月)**,数据成本叠加,**强化暂缓**:若Founder坚持闭环TSMOM需先投入补quote volume+外部supply/mcap/OI,性价比低于A-1。④**[✅Claude执行完毕]** 跨对话回收(扫23会话)：唯一含在途未存工作的"外部调研(Sweep形态线)"——其做空测试**已在其他会话独立完成并封账**(v4多头"全维度无一可部署"、v5做空已失败,DEC 2026-06-06)，**无孤儿决策丢失**；工作区沙箱故障根因=claude-code-vm 2.1.170下载循环失败,Desktop Commander为正确通道。⑤**[议程·rule8]** A-1历史方向识别结构性局限→**前向强平数据路径**：历史A-1无真实强平名义额(采集器2026-06-13起前向)，v2只能用价格代理；最强验证仍需前向真实强平数据3-6月——把已部署采集器与A-1直接挂钩,是采集器首个明确alpha用途。⑥**[✅已决→DEC-075]** A-1两段式路径+universe暂缓**已经Founder"按推荐继续"确认,升格DEC-075**(③⑥出本栏)。**当前推进(2026-06-15)**：**路径A**=A-1预登记已迭代到**v5**(`..._v5.md`)。盲审进度:RR4判v4闭2/5(功效治理+family CLOSED),余4项判"文字与算法冻结、不要求达机制确证严格度"→v5逐条闭(§7改"A-2非重叠关联硬门"/circular半开网格`[t1,tn+1h)`+offset截断/Spearman改配对bootstrap对ρ居中真检验ρ=0/WF唯一切点中点+按实际足迹purge/AES-256-GCM+密钥独立principal+负向测试留命令退出码)→**A1-RR5第五轮盲审=✅APPROVED(4/4全闭,`A1_RISK_REVIEW_v5.md`)**!五轮收敛(10→2/10→0/5→2/5→4/4)。放行边界:仅关联结论/不耗独立计数/不晋级策略;**执行前须先AES-256-GCM Holdout封存+负向权限测试**。**[⚠️待Founder知会后派发]** 按预登记铁律,跑Tier A事件研究(封Holdout+出A-1生死判决)须Founder知会+主会话人工派发,故CTO停在放行点未自动跑;**路径B**=`A1_FORWARD_LIQUIDATION_PATH.md`已设计(采集器原始forceOrder含side方向字段已核实=首个alpha用途;就绪门=候选n达功效门→另立预登记走硬门耗计数;待数据累积3-6月,低成本并行不阻塞)。**恢复点(2026-06-15最新)**:Founder已GO。**两Codex活并行运行中**:①A1_TIERA=A-1 Tier A历史关联快筛执行(按v5两阶段custodian/executor,已写13单测全过+自审,PID见A1_TIERA_RUN.log)→出关联生死判决;②PB1=路径B强平解析器+就绪门计数器(自包含工具)。**网络根因已查实**:downloads.claude.ai命中`claude.ai,默认组`走双跳商家代理→VM大二进制(claude.app.tar.zst 2.1.170)拉不动→Claude.app 172%CPU热循环挤断DC/MCP。**修复待Founder**:Clash加`DOMAIN,downloads.claude.ai,新加坡跳板`(单跳)置于claude.ai规则前+重启Claude。网络拓扑已记忆([[network-proxy-topology]])。SSH采集器宿主无免密钥(路径B拉真实数据待凭据)。|
| **等待 Founder** | **[一个go·非D级但按预登记铁律需知会]** A-1预登记v5已**APPROVED放行**Tier A历史关联快筛。跑事件研究=封Holdout+出A-1生死判决,预登记要求Founder知会+主会话派发→**等你一句"跑"即派发**(先Holdout加密封存+负向权限测试,再Codex执行,只读work)。其余无阻塞。 |
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
| 强平采集器 | ✅ **VM 直跑，生产运行中（2026-06-13）**：`aiquant-liq-collector.service` active，MainPID=2550847，`/opt/ai_quant_liq_collector/data/LIQUIDATIONS/`；直连 Binance WS 已验证真实数据帧（btcusdt@trade 0.247s 3帧）；双审计 P0-1 **已销项** |
| 定时任务 | ⚠️ 周监控/月审 v2 已更新口径；夜间定时不可靠（两次事故），跑批优先 Codex nohup |
| 腾讯云轻量（SG） | ✅ 活跃——采集器已部署 `/opt/ai_quant_liq_collector/`，现有服务（danted/v4-proxy/v4-strategy-runner/docker/nginx）未受影响；审计 P2-4 **已销项** |

## 3. 关键约束（不变）

月预算约 1000 元｜Founder 时间约 1h/天、只批 D 级、无技术背景｜本金上限 30,000（DEC-015 阶梯）｜首要行为风险=风险B/C（治理膨胀/停留讨论层）

## 4. 下一步（执行序，2026-06-15 更新，DEC-075 后）

1. 【Claude自主闭环·进行中】A1-RR4第四轮盲审(Codex PID 33140)出结果→读：APPROVED→主会话派发Tier A历史关联快筛(先过§12 AES加密Holdout封存+负向权限测试);NOT APPROVED→按"关联快筛合理标尺"判残留是真阻塞还是可接受,必要时修v5(不无限加码)。
2. 【路径B·低成本并行】采集器字段落地核查(取VM LIQUIDATIONS样本验side/price/qty/UTC)+前向事件计数监控(建议并入周监控,维护就绪门倒计时)。就绪门达到前不立路径B预登记。
3. 【等Founder D级】审阅 `OPERATING_MODEL_DESIGN_v2.md`（产研三循环流程+版本标准）。
4. 空头方向：独立机制假设另案研究（非镜像TSMOM），先查墓园；Sweep做空已封账(失败),不复活。

## 5. 启动协议

见 **CLAUDE.md v2.3「新对话启动协议」**（BOOT_BRIEF → 本文件 → DECISION_LOG索引 → 四蓝图）。本文件不再维护独立清单。
