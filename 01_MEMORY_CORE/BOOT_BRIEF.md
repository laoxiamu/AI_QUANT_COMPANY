# BOOT_BRIEF —— 精简启动简报（新对话先读这一份，省 token）

**性质：** 派生摘要，非权威源（当前焦点=`CURRENT_STATE.md`；详细任务=`PROJECT_TASK_PLAN.md`；决策=`DECISION_LOG.md`）。预算 ≤60 行。
**最后更新：** 2026-07-15（L1深度审计完成，见"一句话现状"末尾增量2；此前2026-07-06：DEC-092触发的诊断复查**全部完成**：TSMOM引擎L七项检查全过后经Holdout盲验**FAIL判死（2026-07-12）**；#X3维持KILL；价格面板37/37已修复。**DEC-093（2026-07-12）：Founder已批消耗Holdout盲验，P0-RES-015当日执行并验收=**FAIL：引擎L判死（H1 E[R]=-0.63%<0生存底线/H2 -6.86%<0，151笔非低功效），TSMOM家族永闭，Holdout消耗封账，量化侧活体候选归零**；死因=样本外premium消失+成本拖累≈11.6%/年；同日失败风险专项评估落盘`STAGE_AUDITS/FAILURE_RISK_REVIEW_20260712.md`（结论：爆炸式失败概率极低；时间盒内未证实edge概率~60-75%；最大失败驱动=执行吞吐）。教训：** Founder追问"codex任务正常吗"发现此前多次"已派Codex"只是写了任务书未实际执行，已核实+补救，今后"已派"必须附真实进程/日志证据。最新DEC=DEC-094）

## 一句话现状

Phase 1，edge=0（唯一P0）。**carry/A-1/A-2/#X2/#X3/TSMOM定仓穷尽=Dead**（免费价格软-payer族已判定耗尽，收窄口径=死的是普通价格形态+低维动量，结构数据+事件交互未试完）。forced-flow v2/P1解锁PARK待数据（2026-07-02核实：价格面板早已刷新至6/22但此前未同步，"无重叠"判断过期，实际有约10天重叠增长中仍不够统计检验；付费数据核实不划算）。**量化主动猎暂停（Founder认可），投研线领跑**（DEC-091四层流水线：投研发现→前向纸面→量化验证→核心资本）。权威路线图见 `OPPORTUNITY_MAP_STATUS.md §🧭`（P0 forced-flow v2/P1事件×资金流/P2山寨痕迹沙盒/P3美股事件/蒸馏支线/三账户分层）。
**当前恢复点（2026-07-06）**：①grill-me/Tokenomist/强平同步/fable两轮审查落地DEC-092等此前工作已归档，见`CURRENT_STATE.md §1b/§1c`；②**DEC-092诊断复查已实际执行**（此前只写了任务书未真正派发，Founder追问后核实并补派）：**P0-RES-006 TSMOM引擎L=EXISTS_FEASIBLE_POSITION_SIZING**（10%目标波动率点6/7项检查通过，DD/growth/WF/赢亏比/正期望全过，唯一未过=旧口径基准比较，P0-RES-014用v1.5风险调整法重算中）——**DEC-092后首个有希望复活的候选，非已晋级**；**P0-RES-007 #X3=KILL_MAINTAINED**（风险调整基准门未确认但主死因独立成立）；③**P0-RES-008价格面板SSL修复已完成**（37/37symbol续到2026-06-22，⚠️新发现BTCUSDT历史仅1.5年远浅于其余~6年，原面板从未含BTCUSDT，另案评估）；④**侦察积压**：P0-RES-009 Hyperliquid已完成（2026-07-06，结论=非数据墙直接解法，留零成本平行验证线）；P0-RES-010~012未派、本周清零（2026-07-15审计R7）、013存档；高频thesis模板(24-72h窗)本周待起草；⑤THESIS #001/#002已结算：方向命中1/2（详见CURRENT_STATE §1b⑦），YZY(T0=7/17)待~7/14冻结。**遗留**：小红书`x-reader login xhs`待Founder配合登录。详细过程见 `CURRENT_STATE.md §1b/§1c`。**2026-07-15增量：THESIS_003/004已结算=均部分命中2/3（003窗末-12.2%方向败/004窗末+8.3%方向中；方向累计2/4=50%与随机无异，样本小且003/004非独立）；YZY弃（真实流动性$1.8k/日不可执行）；拒绝分母累计7条；模板补第7条(字段11禁"期"写绝对时间戳)；取数走通道B(SG)；进度2/10-20剩~22天需新候选；**DEC-094=每日巡检定时任务已建（10:01扫描+登记+结算+watchlist，纸面only），进度脱离人工发起**；DEC-093批Holdout盲验→P0-RES-015当日执行完毕=**FAIL，引擎L判死，TSMOM家族永闭**；失败风险评估已落盘（引擎L死后定义2概率上修至~75-85%，见附录）。最新DEC=DEC-094。**增量2（2026-07-15 L1深度审计）**：路线无偏航；🔴git 24天未提交已补commit+成本盒仪表34天未更新（待Founder补账单）；🟠强平本地同步二次断裂14天已重启rsync（周报加滞后告警R2）、每日巡检待Founder点Run now、权威文件4处过时段+记忆TSMOM变体冲突已修；替代路径=不换路线换执行密度（面板月刷/扫描源拓宽/侦察清零）；处方R1-R7见`STAGE_AUDITS/L1_DEEP_AUDIT_CLAUDE_2026-07-15.md`。**

## 目标函数（DEC-063，原则层冻结）

找真实/可持续/可放大 edge + 安全复利核心资本；月化30%不是验收条件；两层资本（核心受保护 / 围栏**按证据等级解锁**，DEC-069④）；高杠杆=表达工具非Alpha来源（实证：@2x年爆仓61-76%）。

## 止损与计数（DEC-069①）

旧范式 5 败封账；**新范式独立计数=1（a2）**，计数=L3触发器（每+2复评）；**主闸=时间盒（2026-06-07起6个月无edge）+成本盒（5000元，已用871.93）+L3裁量**。"剩N命"倒计时废止。

## 研究范式（原则层冻结）

机制优先七问（含"付的钱经什么路径到我口袋"）；预登记+单变量+WF+Holdout物理封存；事件类按 v1.3 增补件（池化+单调性+成本压力档）；**预登记须含 MDE 功效段、验收含同状态被动基准对照（v1.4 已完成）**；不显著点估计禁作方向结论（墓园禁引用措辞字段）。新假设先查 `06_RESEARCH/GRAVEYARD_INDEX.md`。

## 在途与等待（2026-06-20 方向重置后）

- **🟡P0研究主线（DEC-088）：** 加密合约forced-flow/payer-flow v2 = B0机制卡(单一方向预登记,弃价格动量,funding极端/OI重置/强平簇/taker失衡)→B1-KILLCARD(默认KILL基线,成本/数据/反A-1/反Sweep)→B2(1x)→B3入场优化→B4杠杆风险测试。任一步不过=回墓园/pivot,禁改参数续命。强平清算路径免费阶段A数据预筛(Coinalyze/Tardis/Bybit自采)并入数据层。
- **🟡执行顺序：** ✅三免费价格线连灭(TSMOM/#X2/#X3)→✅DEC-087目标函数修订→✅DEC-088战略复盘三方收敛+路线图→🟡**起草P0 forced-flow v2 B0卡**→B1-KILLCARD→…。P1事件×资金流升一等(P0后或并行)。
- **🧊 DEFER（DEC-082/088,解冻=一条edge过B2或Founder时间实测为瓶颈）：** Spec Kit初始化/ADR-业务项/C4全套/Orchestrator/Strategy Governor引擎/Web/Discord/七维路由/九域记分卡。
- **🔵知识积压：** OSS-001 TOOLS_KNOWLEDGE 6项更新待执行(非阻塞)。
- **⚪等待 Founder D（1项）：** ④公司终态/阶段门（非紧急,待edge后再谈）。
- **详细任务：** `00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md`；权威路线图 `OPPORTUNITY_MAP_STATUS.md §🧭`。

## 公司 OS 全局平衡检查（每次开局强制执行，8维度）

> 主理人职责不只是推进研究，是确保公司8个维度同步健康。开局时必须扫一遍，发现失衡立即提出。

| 维度 | 当前状态 | 警戒 |
|---|---|---|
| ①量化研究 | P0=forced-flow/payer-flow v2(PARK待数据)；carry/A-1/A-2/#X2/#X3 Dead；**TSMOM全家族=Dead（引擎L Holdout盲验FAIL，2026-07-12永闭）；量化侧活体候选=0，投研线领跑** | ⚠️"过回测"≠"edge证实"，勿冒进宣布已找到edge |
| ②生产工程基础设施 | E1-E4 草图已完成，生产平台未建 | ⚠️ 待实现 |
| ③实时风控执行层 | 规则与架构草图已有，代码层未实现 | ⚠️ 待实现 |
| ④运营工作流 | 责任与流程未形成可运行闭环 | ⚠️ 待建设 |
| ⑤公司治理/文档 | DECISION_LOG/OS蓝图相对完整 | 正常 |
| ⑥项目管理/产研工作流 | 总图与 108 项单一 WBS 已建立 | 正常 |
| ⑦监控与告警 | 只有强平采集器，无交易系统监控 | ⚠️ Phase 2前设计 |
| ⑧知识管理/经验沉淀 | CARRY_KNOWLEDGE/TOOLS_KNOWLEDGE/RESEARCH_ACTION_REGISTRY已建；3个Claude Skills（result-intake/codex-task-spec/research-harvest）+Holdout hook已建；60+历史报告harvest待执行 | ⚠️ 改善中 |

**②③④⑦ 已有 DRAFT v0.2（`05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md`）**，包含 Track A（自动执行）+ Track B（AI主动分析）双轨制设计。**Track B 方向待 Founder D 级确认。**

## 团队工作方式（自我提醒）

主理人开局；不做选择题搬运工（D级=修改Founder已拍决策，必带推荐整包上）；两面诚实反迎合；跑批可靠性排序=Codex nohup > 白天定时 > 夜间定时；低模型只做逐字/格式/索引；产出未经 Claude 验收不作依据。**任务产出后强制专业透镜（规则7）；主动设置议程不等Founder发现（规则8）。**

## 细节指针

CURRENT_STATE v5.0（当前焦点；§4 指向任务权威）｜**PROJECT_TASK_PLAN（唯一详细任务权威）**｜**OPPORTUNITY_MAP_STATUS §🧭=权威路线图**｜**§1b=活动工作区/§1c=对话级建议暂存**｜DECISION_LOG（索引→**DEC-094** 为最新）｜直调配方 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`（含DC稳定配方）｜启动协议见 CLAUDE.md v2.4。
**Codex闭环实况（2026-07-15审计更正）**：Codex完成→写04_AI_TEAM/TASK_INBOX/{ID}_DONE.json→**人工/VM轮询验收**；15min自动调度器`codex-task-inbox-checker`已于2026-06-19起disabled，勿再当现行协议引用。

**§1b 制度**：Founder 主动打断对话时，Claude 在结束前必须更新 §1b（已完成什么、剩余什么、恢复点在哪）。新对话开局如 §1b 有内容，优先恢复，不重新分析。
**§1c 制度（DEC-073）**：对话中 Claude 提出的任何建议须当场写入 §1c；Founder 确认→升入§4；否决→清除；未响应=下次开局必提。DEC-073=全周期决策记录规范（§1c制度来源）；**最新=DEC-094**。
