# 低模型执行任务包 2026-06-10（OS 调优机械任务）
**发包人：** Claude（主理人/CTO）｜ **执行者：** 低成本模型新会话 ｜ **验收人：** Claude
**依据：** `00_PROJECT_MANAGEMENT/OS_TUNING_PLAN_v1.md` + `STAGE_AUDITS/L2_AUDIT_OS_FREEZE_2026-06-10.md`

## ⛔ 执行铁律（违反任何一条=任务失败）

1. 你是机械执行者，**不做任何判断、不改写语义、不发明内容、不优化措辞**。payload 标注"逐字"的，一字不改地用。
2. **禁止**修改 DECISION_LOG 既有条目正文、禁止改任何研究结论、禁止删除任何文件、禁止超出本包范围的任何"顺手优化"。
3. 动 `01_MEMORY_CORE/` 任何文件前，先复制备份到 `99_TEMP/BACKUP_20260610/`。
4. 每完成一个任务，在 `99_TEMP/CHANGE_REPORT_20260610.md` 追加一行：任务号/动了哪些文件/做了什么。
5. 遇到锚点找不到、内容与本包描述不符的情况：**跳过该任务并在报告中记录**，不要自行变通。
6. 全部完成后执行 T-13 终检。所有任务完成≠生效，**Claude 验收后才算数**。

---

## T-01 创建低模型会话章程

新建 `04_AI_TEAM/LOW_TIER_TASKS/LOW_TIER_CHARTER.md`，逐字写入：

> # 低模型执行会话章程 v1（2026-06-10，依据 OS_TUNING_PLAN_v1 §④）
> **定位：** 公司第三执行层。判断→Claude；复杂实现→Codex；机械批量→低模型（本层）。
> **可做：** 逐字payload搬运、加横幅、生成索引表、按精确spec移动文本块、跑给定命令、格式化。
> **不可做：** 任何判断/语义改写/内容发明/触碰DECISION_LOG条目语义/修改研究结论/扩大任务范围。
> **护栏：** 动权威文件先备份99_TEMP；每任务记录diff摘要；终检跑state_check；Claude验收后才算完成。
> **任务包格式：** 见 TASK_PACKAGE_*.md；铁律6条随包重申。

## T-02 已降级文档加警示横幅

对下列 7 个文件（均在 `00_PROJECT_MANAGEMENT/`），在标题行（第一个 `#` 行）之后插入一个空行 + 下面这段逐字横幅：

> ⚠️ **本文件已降级（2026-06-10，依据 PHASE1_TECH_ORG_GOVERNANCE_v1 §3.1 文档权威层级）**：仅作历史参考，禁止作为当前架构、计划或决策依据。现行权威：`01_MEMORY_CORE/BOOT_BRIEF.md` + 公司OS四蓝图。

文件清单：`AI_QUANT_COMPANY_ARCHITECTURE_v1.md`、`AI_QUANT_COMPANY_ARCHITECTURE_v2.md`、`PROJECT_MASTER_PLAN_v1.md`、`PROJECT_MASTER_PLAN_v2.md`、`PHASE1_RESEARCH_THESIS_v1.md`、`OPERATING_MODEL_DESIGN_v0.md`、`V5_TOOL_INTEGRATION_PLAN_v1.md`。
（注意：`PROJECT_OPERATING_STATE.md` **不在**清单内，不要动它。）

## T-03 CURRENT_STATE 瘦身（高危任务，严格按步骤）

1. 备份 `01_MEMORY_CORE/CURRENT_STATE.md` → `99_TEMP/BACKUP_20260610/`。
2. 新建 `01_MEMORY_CORE/ARCHIVE/RESEARCH_LOG_PHASE0_1_2026H1.md`，头部写一行："# 研究与状态历史归档（2026-06-10 自 CURRENT_STATE v3.18 剥离，内容原样未改）"。
3. 把 CURRENT_STATE 中 `## 3. Memory Core 文件状态`、`## 4. RAW_INBOX 提炼状态`、`## 5. 当前任务队列` 三个章节的**全部内容原样剪切**到归档文件——**例外：§5 中以下列开头的段落保留在 CURRENT_STATE**（剪切前先把它们移到 §2 之前，新建小节 `## 1b. 最近进展（活动区）` 存放，保持原顺序）：
   - `**下一步（三份2026-06-07审计共识）`
   - `**2026-06-08 进展：`
   - `**2026-06-10 进展` 开头的全部段落（共3段）
4. 不动头部、§1、§2、§6、§7、§8 的任何内容。
5. 完成后文件应明显短于 200 行；若结构与上述描述不符，按铁律 5 跳过并报告。

## T-04 DECISION_LOG 加索引

1. 备份 `01_MEMORY_CORE/DECISION_LOG.md`。
2. 在 `## 本项目自身决策` 标题**之前**插入新章节 `## 索引（2026-06-10 机械生成，以正文为准）`，内容为表格：列=编号｜决策一句话｜状态。逐条读取正文每个 `**[DEC-XXX]**` 块，"决策一句话"取该块"决策内容："后的第一行并截断到30字以内（纯截断，不改写）；"状态"取该块的状态行。含 DEC-DEPRECATED-001。
3. **禁止改动任何条目正文。**

## T-05 STATE_SYNC_CHECKLIST 补维护规则

在 `01_MEMORY_CORE/STATE_SYNC_CHECKLIST.md` 文件末尾追加（逐字）：

> ## 上下文预算与工具注记（2026-06-10，OS_TUNING_PLAN_v1）
> - BOOT_BRIEF 预算 ≤60 行；CURRENT_STATE 活动区预算 ≤150 行。超限即触发瘦身（历史内容移 `01_MEMORY_CORE/ARCHIVE/`）。
> - 沙盒环境运行自检须传项目根路径参数：`python3 state_check.py <项目根>`。
> - DECISION_LOG 新增条目后须同步更新文件头部索引表。

## T-06 创建工具路由表

新建 `00_PROJECT_MANAGEMENT/TOOL_ROUTING.md`，逐字写入：

> # 工具路由表 v1（2026-06-10）
> | 活的类型 | 走哪 | 理由/禁区 |
> |---|---|---|
> | 判断/设计/研究主张/验收 | Claude 主会话 | 唯一判断层；禁被动执行 |
> | 复杂实现（>100行/多文件/长迭代）| Codex | 文件式handoff+任务规格；R1起经直调通道 |
> | 机械批量（索引/横幅/搬运/格式化）| 低模型会话 | 按 LOW_TIER_CHARTER；Claude验收 |
> | ≤50行分析脚本 | Claude 沙盒 bash | 一次性、可丢弃 |
> | 常驻进程（采集器等）| Mac launchd / 云VM | **沙盒禁**（会话结束即死）|
> | 定时巡检/月审/周监控 | scheduled task | SKILL与现行口径同步是Claude责任 |
> | 独立复核/红队 | 隔离子会话 | 只给Context Pack（见04_AI_TEAM/CONTEXT_PACKS）|
> | 外部知识摄取 | WebSearch/x-reader | 按可信源清单；交易所博客=最低档证据 |

## T-07 采集器运行手册

新建 `06_RESEARCH/CODE/LIQUIDATION_COLLECTOR_RUNBOOK.md`，逐字写入：

> # 强平采集器运行手册（2026-06-10）
> **脚本：** `06_RESEARCH/CODE/liquidation_collector.py` ｜ **数据：** `06_RESEARCH/DATA/LIQUIDATIONS/liq_YYYYMMDD.jsonl`
> **依赖安装（Mac）：** `pip3 install websocket-client --break-system-packages`
> **启动（Mac 前台测试）：** `python3 liquidation_collector.py`（看到 heartbeat 行即正常）
> **启动（Mac 常驻）：** `cd 06_RESEARCH/CODE && nohup python3 liquidation_collector.py >> collector.log 2>&1 &`
> **健康检查：** 每周看 `DATA/LIQUIDATIONS/` 最新文件行数>0；collector.log 每小时一条 heartbeat。
> **注意：** Mac 休眠会断流（数据缺口可接受，按"尽力采集"定位）；长期方案=腾讯云VM（Phase 2 评估）。时间戳统一 UTC。
> **待办（Claude）：** 周监控任务加"昨日行数>0"检查；评估顺手加收 Bybit/OKX 强平流。

## T-08 创建子会话 Context Pack（两份）

新建 `04_AI_TEAM/CONTEXT_PACKS/RISK_REVIEWER_PACK.md`，逐字：

> # Risk Reviewer 上下文包 v1
> **必读：** BOOT_BRIEF / 被审对象的预登记文档（HYPOTHESES/）/ Protocol v1.3 验收口径 / 风控七层（蓝图③ Part C）
> **禁读：** 提案者的结果报告、结论、equity曲线——**先独立形成风险判断，再看结果**。
> **职责：** 爆仓概率/相关性/生存性审查，有否决权。输出：通过/否决+理由，落 06_RESEARCH/RESULTS/ 同名 _RISK_REVIEW.md。

新建 `04_AI_TEAM/CONTEXT_PACKS/INDEPENDENT_REVIEW_PACK.md`，逐字：

> # Independent Review 上下文包 v1
> **必读：** 被审对象的预登记文档 + 原始数据路径 + Protocol v1.3。
> **禁读：** 提案者的结果/结论/中间CSV——**必须从原始数据独立复算**，不继承任何中间产物。
> **职责：** 独立复算 + Deflated Sharpe（按试验次数贴现）+ 红队清单（单变量?前视?窥探?多重检验?）。输出落 _INDEP_REVIEW.md。

## T-09 创建假设墓园索引

新建 `06_RESEARCH/GRAVEYARD_INDEX.md`，逐字写入（任何新假设预登记前必查本表）：

> # 假设墓园索引 v1（2026-06-10）｜新假设预登记前必查，防换皮重测
> | 实验 | 猎的是什么 | 结论 | 根因 | 复活条件 |
> |---|---|---|---|---|
> | v1/v2 (4H/1H三重确认) | 形态组合 | FAILED | WF衰减/无机制 | 不复活 |
> | v3 (Sweep事件分布) | 形态 | FAILED | 效应集中2021 | 不复活 |
> | v4 (Sweep+双层Regime) | 形态+状态 | 样本内边沿真实/不可部署，线CLOSED | WF2方向失效非实现层可解 | 永不（DEC-047）|
> | v5 (Bearish Sweep做空) | 形态 | FAILED | 依赖2022单一时期 | 不复活 |
> | v6/v6b/0B17/0B18 (止损/仓位变体) | 实现层修补 | 全FAILED | 瓶颈在信号稳定性非实现层 | 禁止再开变体 |
> | Sweep形态家族整体 | 看图下单 | 封存（DEC-066④）| 图形是机制的影子 | 机制版已并入A-1，形态版不复活 |
> | P1-01/02 TSMOM v1/v2 | 趋势因子 | FAILED/COST-LIMITED | 净Sharpe<1+69%共同回撤 | 被P1-04取代 |
> | P1-04/06 regime-first TSMOM | 机制化趋势 | **活体候选**：新口径四件套全过（20260610复读）| — | R2后扩样本，P1-06优先 |
> | delta中性carry | 资金费率稳态 | 排除（蓝图A-5）| 容量无限=大资金游戏 | 资金规模质变时重评 |
> | 裸卖波动率/VRP | 卖保险 | 排除 | 左尾在级联中爆炸 | 不复活；VRP只作择时输入 |

## T-10 创建 Claude 不可用降级预案

新建 `00_PROJECT_MANAGEMENT/DEGRADED_MODE_PLAYBOOK.md`，逐字：

> # Claude 不可用降级预案（2026-06-10）
> **场景：** 周额度耗尽/服务中断，任务做到一半。
> **原则：** state-sync 保证每轮结束权威文件已同步（2026-06-09 额度截断实测零丢失）。
> **Founder 该做的：** ①什么都不用改——禁止手工编辑 01_MEMORY_CORE/ 任何文件；②等额度恢复后开新会话，说"更新当前进度"即可，启动协议会自动恢复断点；③紧急情况只允许动钱的操作走交易所App人工处理。
> **Founder 不该做的：** 手工改状态文件、让其他AI代写权威文件、凭记忆口述状态（以文件为准）。

## T-11 创建 Protocol v1.3 增补件（逐字，不改 v1.2 原文）

新建 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`，逐字写入：

> # Research Protocol v1.3 增补件（2026-06-10，依据 DEC-066③ + L2_AUDIT_OS_FREEZE P0-1/2）
> **效力：** 本件与 v1.2 冲突处以本件为准。v1.2 中 Expectancy>1.0、MaxDD<25%、净Sharpe>1 等旧门槛**全部作废**。
> ## 一、验收口径四件套（量化冻结）
> 1. **正期望：** 单笔 E[R]>0（R=净盈亏/名义仓位，扣手续费+滑点+funding）。
> 2. **盈亏不对称：** 赢均/亏均 ≥1.5。
> 3. **爆仓概率（块bootstrap：块长1周等效bar数、2000路径×1年、seed预登记）：** 标准档 P(年DD≥35%)≤20%；保守档 P(年DD≥20%)≤10%；围栏激进档不适用本条（可归零），仅验1/2/4。
> 4. **几何增长：** 年化对数增长率>0，且分年E[R]为正的年份占多数（仅计≥10笔的年份）。
> 样本量分档沿用 DEC-018；WF、Holdout 封存纪律不变。
> ## 二、事件类策略成本压力档（A-1/A-2 类强制）
> 基准滑点0.1%外，必须报 0.3%/0.5%/1.0% 三档敏感性。**通过线：** 事件类策略在0.3%档四件套仍全部成立；清算级联类（A-1）额外要求1.0%档 E[R]>0。级联时刻按市价单+部分成交假设建模，禁用限价理想成交。
> ## 三、组合相关性门槛（新策略晋级追加条件）
> 新策略日PnL与既有已晋级策略相关性 |corr|<0.5，或证明加入后组合年化对数增长率提升。
> ## 四、事件研究样本规则（R2 适用）
> 预登记前先做事件普查（各极端阈值下独立episode计数）；episode<100时禁用60/20/20三分，改用跨品种池化+阈值单调性检验，Holdout按事件级（而非时间比例）预先切分并封存；预登记中写明检验总次数上限，结论经多重检验贴现。

## T-12 版本控制初始化（P0-5）

在项目根目录依次执行（如 git 已存在 `.git` 目录则跳过 init，只做后三步）：
1. `git init`
2. 创建 `.gitignore`，逐字内容：`__pycache__/`、`*.pyc`、`.DS_Store`、`99_TEMP/BACKUP_*/`、`collector.log`、`.obsidian/workspace.json`（每行一条）
3. `pip3 freeze > 00_PROJECT_MANAGEMENT/requirements_lock_20260610.txt`（失败则记录跳过）
4. 生成数据哈希清单：对 `06_RESEARCH/DATA/` 下所有 .csv 执行 sha256，输出到 `06_RESEARCH/DATA/DATA_HASHES_20260610.txt`（格式：哈希两空格相对路径）
5. `git add -A && git commit -m "baseline: company OS v1 + DEC-066 (2026-06-10)"`

## T-13 终检（最后执行）

1. `python3 01_MEMORY_CORE/state_check.py <项目根路径>` —— 必须输出"无已知滞后"。
2. 确认 `99_TEMP/CHANGE_REPORT_20260610.md` 覆盖了 T-01~T-12 每一项（含跳过项及原因）。
3. 在报告末尾写："全部完成，等待 Claude 验收"。**不要更新 CURRENT_STATE/BOOT_BRIEF**（那是 Claude 验收后的事）。
