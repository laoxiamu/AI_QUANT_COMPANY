# CURRENT_STATE.md

**版本：** 4.6（2026-06-21 治理分档 DEC-083：Orchestrator=只读骨架/ADR+C4+变更传播现在做(P0-C+)/完整编排+控制面仍DEFER；最新DEC=DEC-083）
**最后更新：** 2026-06-21（Claude独立方案+Codex反审收敛+Founder裁month-30%；权威口径同步进行中）｜ **更新者：** Claude
**历史沿革：** v3.x 滚动记录已归档 `01_MEMORY_CORE/ARCHIVE/STATE_LOG_20260607_0612.md` 及 git 历史
**维护规则：** 本文件为**固定槽位覆盖式看板**——更新=改写槽位内容，不追加滚动条；超过 150 行即违规（state_check 查）。

---

## 1. 状态看板

| 槽位 | 当前值 |
|---|---|
| **阶段** | Phase 1（找真实 edge）。公司 OS **原则层已冻结**（DEC-068②/069②：目标函数/两层资本/机制优先/验收纪律/权威层级）；机会地图与运行层 = v0.x 可迭代，运行层升 v1 条件="连续14天定时任务零卡死+state_check零漂移" |
| **机会地图** | TSMOM=**Baseline（regime-adaptive框架信号基座）**｜A-1独立回弹=**Dead**（OI降级为风控候选；前向强平数据被动积累）｜**carry=Dead（DEC-079）**｜**regime-adaptive方向性策略=Candidate（DEC-082，待过B0机制门+B1数据门；非「已验证主线」）**｜A-4=Candidate（排队）｜funding/OI=State｜A-2=Dead ｜⚠️**month-30%=资本愿望，非研究验收门（DEC-082）；杠杆=过门后风险测试非Alpha来源** |
| **失败计数（DEC-069①）** | 旧范式 5 条封账；**新范式独立计数=1**（a2）；主闸=时间盒（2026-06-07起6个月）+成本盒（5000元，已用871.93）+L3裁量 |
| **Holdout** | 全部封存完好（含 a2 事件级 Holdout 218 条）；任何实验未读取 |
| **验收口径** | v1.3/v1.4 增补件已完成；新方向实验须按同等纪律预登记。文件：`06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` |
| **在途任务** | ⚠️**顶层重平衡（2026-06-21，DEC-082）**：研究=唯一P0轨(WIP=1)；治理=一次性卫生(P0-C，封顶1包)；自动化全DEFER。✅数据就绪(127 parquet)。**唯一研究主线=regime-adaptive，拆为B0机制卡→B1标签审计→B2单变量门控(1x)→B3仓位→B4杠杆风险测试**；P1-RES-034原捆绑描述已冻结。**执行顺序：✅P0-C已验收完成(治理轨关闭)→🟡下一步起草B0机制卡**。**DEFER**：Spec Kit初始化/ADR-业务项/C4全套/Orchestrator/控制面/七维路由/记分卡（解冻=一条edge过B2或Founder时间实测为瓶颈）。强平采集器=收数中。 |
| **§1b 活动工作区（Claude 对话级在途）** | **2026-06-21（本轮=顶层重平衡落盘）**：✅已完成：①Claude独立顶层方案+Codex反审收敛；②month-30%裁决写入DEC-082(Founder D级)；③DEC-080/081索引修订；④CURRENT_STATE机会地图/在途/§1c同步。⑤**P0-C治理卫生已验收**(state_check真绿灯退0+self-test通过;Codex修复+6 pytest;五项规则冲突落地=AGENTS正文2处+SYSTEM_RULES 5项DEC-082裁决指针;DEC-080正文残留month-30%已修订)→**治理轨关闭**;⑥子代理四档路由写入工具链。**🟡下一步(唯一)**：起草B0机制卡(可证伪硬验收,Claude自己写不下放;需机制论证可能查文献)。**恢复点**：P0-C done,治理轨关闭,直接起草B0。 |
| **§1c 对话级建议暂存区** | **制度说明（DEC-073）**：确认→升入§4/DECISION_LOG；否决→清除；未响应=下次开局必提。**已确认写入DECISION_LOG**：DEC-076（系统路线）；DEC-079（carry关闭）；DEC-080（新方向，验收口径被DEC-082修订）；DEC-081（治理工具栈）；**DEC-082（顶层重平衡，Founder D级2026-06-21裁month-30%=资本愿望/研究=唯一P0/治理压一次性卫生/自动化全DEFER/P1-RES-034拆B0-B4）**。**DEC-077/078已废弃**。**当前悬空（待Founder确认）**：④【公司终态D级】P0-STR-005——非紧急。⑤【TASK_INBOX daemon】建议加入P2计划。⑦【团队角色重组】待定义。⑧【治理分档·DEC-083已定】✅Founder采纳Claude折中：Orchestrator=**只读状态/事件日志骨架(G2只读PoC)**,不建自动派单/Web/Discord；并行P0-C+(封顶1包,不挤占B0)=DEC变更传播强化(扩state_check)+ADR-001+C4 L1；完整编排/控制面/Spec Kit全量/七维路由/记分卡仍DEFER(解冻=edge过B2或Founder时间瓶颈)。⑨【skill】grill-me✅(B0用)；codebase-memory⚠️(疑与Memory Core重复,建议改handoff)；headroom❓(来源待补);Cowork会话不能装skill,路径=Codex `npx skills add mattpocock/skills` 或 Settings›Capabilities。⚠️**已否决·禁止复提**：新增定时任务。 |
| **等待 Founder** | ✅month-30%已裁（DEC-082）。当前无阻塞性D级；Claude继续P0-C→B0。D级悬空：④公司终态（非紧急，待B0机制卡后再谈）。 |
| **禁引用措辞** | "极端拥挤=延续"（墓园 2026-06-12 勘误，不显著点估计不得作结论） |

## 2. 工具链

| 工具 | 状态 |
|---|---|
| Claude Cowork + Desktop Commander | ✅ 主工作区 + Mac 执行通道 |
| **Codex CLI 直调** | ✅ **2026-06-11 验证**（配方 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`：代理env + </dev/null + workspace-write；AGENTS.md 已部署项目根）|
| **Codex Skills** | ✅ **2026-06-14 安装扩展**：PlanToDelivery、find-skills、女娲、达尔文、TDD/diagnose/architecture/to-issues、`obra/superpowers`完整14 skill；加密合约专项skill已按perp/funding/OI/强平/微观结构重搜，交易所/API类暂不自动装。记录见 `00_PROJECT_MANAGEMENT/CODEX_SKILLS_INSTALL_LOG_2026-06-14.md`。需重启 Codex 后新会话识别 |
| 低模型执行层 | ✅ 两次任务包验收通过；边界收紧（DEC-069 后只做逐字/格式/索引，禁触权威语义）|
| **子代理/模型路由（DEC-082执行约定，2026-06-21）** | 一句话四档,临场选通道节省主上下文token：①重判断/权威语义/研究裁决/机制卡=**Claude自己**(不下放,DEC-069禁权威语义下放)；②多文件实现/迭代复现=**Codex**；③大批量只读检索/读日志/跑批/提取摘要=**Explore或haiku/sonnet子代理,只回传结构化摘要**；④逐字/格式/索引=**低模型/脚本**。⚠️子代理冷启动不继承项目认知,需深认知的活不下放(喂上下文成本>收益)。**非系统,不升级为七维路由器(DEC-082已DEFER)** |
| Python 3.13 量化环境 / VectorBT / pytest | ✅ |
| git + GitHub 私库 | ✅ `laoxiamu/AI_QUANT_COMPANY`（deploy key，验收后推送制）|
| 强平采集器 | ✅ **已修复并收数（2026-06-15）**：改 WS_URL→`/market/ws/!forceOrder@arr`(根因=Binance 2026-04-23路由迁移,非封IP,v4.6.2线索查实)→重启后**收到92帧**,LIQUIDATIONS 开始增长→路径B免费期权激活。曾误判经历:⚠️先以为零采集/封IP：service active 但 22h `process_messages=0`。根因=**Binance 对腾讯云SG服务器IP的WS行情流限制**（REST fapi HTTP200正常，但 aggTrade/forceOrder WS 握手OPEN后0帧——云IP被限推送）。**非代码bug**（ping+重连正常）。教训=信了"service active"未验真实数据流（风险E/A）。**根因查实（2026-06-15 VERIFY-V462，纠正先前"封IP"误判）**：**非IP封锁，是Binance 2026-04-23 WS路由迁移**。旧URL`wss://fstream.binance.com/ws/!forceOrder@arr`→0帧；**新路由`/market/ws/!forceOrder@arr`→立即收帧**（同机对照+历史v4.6.2 REST直连可用佐证）。**修法极简=改WS_URL路径,无需鉴权/代理**(Codex修复+验证中)。OI/funding改用REST(`/fapi/v1/openInterest`,`/futures/data/openInterestHist`,`/fapi/v1/fundingRate`)。修好后采集器即可正常攒数→路径B免费期权激活 |
| 定时任务 | ⚠️ 周监控/月审 v2 已更新口径；夜间定时不可靠（两次事故），跑批优先 Codex nohup |
| 腾讯云轻量（SG） | ✅ 活跃——采集器已部署 `/opt/ai_quant_liq_collector/`，现有服务（danted/v4-proxy/v4-strategy-runner/docker/nginx）未受影响；审计 P2-4 **已销项** |

## 3. 关键约束（不变）

月预算约 1000 元｜Founder 时间约 1h/天、只批 D 级、无技术背景｜本金上限 30,000（DEC-015 阶梯）｜首要行为风险=风险B/C（治理膨胀/停留讨论层）

## 4. 当前焦点与任务计划指针（2026-06-20）

> **详细任务单一权威：** `00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md`。本节不再复制全量 WBS；对话中的新增、调整、阻塞、完成、废弃和决策，必须当轮写回该计划书。

- **当前唯一执行主线（DEC-082）：** regime-adaptive 研究，拆为 **B0机制卡（可证伪硬验收，不碰Holdout/不调参）→ B1标签审计 → B2单变量门控(1x) → B3仓位 → B4杠杆风险测试**。任一步不过=回墓园/pivot，禁改参数续命（风险D闸）。~~P1-RES-030 carry v4~~=carry已死(DEC-079)，不再为主线。
- **执行顺序：** P0-C 一次性治理卫生（先行，封顶1包：state_check修复+四份规则文件硬冲突裁决）→ 验收后起草 B0。
- **口径（DEC-082）：** month-30%=资本愿望非验收门；杠杆=过门后风险测试非Alpha来源；新方向=Candidate（待过B0/B1门）。
- **被动并行：** 强平采集器收数中；A-1 路径B 继续积累（就绪门=功效门后另立预登记）。A-1 保持 Dead，不得复活/改写「部分成功」。
- **DEFER（解冻=一条edge过B2或Founder时间实测为瓶颈）：** Orchestrator/Strategy Governor引擎/Web/Discord/七维路由/九域记分卡/Spec Kit试点/C4全套。
- **中断恢复：** 未完成步骤写 §1b；恢复后先核对 DEC-082 与 `PROJECT_TASK_PLAN.md` 对应任务 ID。

## 5. 启动协议

见 **CLAUDE.md v2.3「新对话启动协议」**（BOOT_BRIEF → 本文件 → DECISION_LOG索引 → 四蓝图）。本文件不再维护独立清单。
