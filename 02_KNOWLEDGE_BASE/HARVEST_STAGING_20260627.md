# HARVEST_STAGING_20260627

> [草稿待Claude审] P1-GOV-009-EXTRACT 暂存提取文件。只读历史报告与现有知识库；不得视为正式知识库条目。

## 0. 扫描摘要

- 扫描时间：2026-06-28T16:05:34+00:00
- 范围：`04_AI_TEAM/CODEX_TASKS/REPORT_*.md` 84 份；`06_RESEARCH/RESULTS/*.md` 55 份；合计 139 份。
- 只读交叉知识库：`02_KNOWLEDGE_BASE/CARRY_KNOWLEDGE.md`、`TOOLS_KNOWLEDGE.md`、`TREND_TSMOM_LESSONS_v1.md`、`SWEEP_SIGNAL_FAILURE_LESSONS_v2.md`、`STRUCTURE_SETUP_FAILURE_LESSONS_v1.md`、`V4_REUSABLE_ASSETS_v1.md`、`EXTERNAL_RESEARCH_v2_AI_NATIVE_OPERATING_PATTERNS.md`。
- 写入边界：本文件为唯一知识库目录产出；未写入正式知识库文件。
- 类别计数：Carry 15；系统工程 18；工具OSS 6；TSMOM-Alpha 29；治理审计 15；其他 56；合计 139。
- 状态计数：PASS 38；FAILED 34；COMPLETED 16；DIAGNOSTIC 13；UNKNOWN 12；BLOCKED 9；KILL 8；NOT APPROVED 7；MIXED 2。

## 1. 分类清单（139行）

字段：文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似重复

### Carry（15）

| 文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复? |
|---|---:|---|---|---|---|---|---|---|
| 20260613_carry_basis_stats.md | 2026-06-13 | C2 Carry Basis 4H 数据统计 | FAILED | 结论；状态：FAILED。指定代理 http://127.0.0.1:7897 下载失败。 | - | 禁止项自检与偏差记录；- 脚本未下载 cutoff 后 spot ZIP。；- 脚本未读取 HOLDOUT 路径。 | Carry | Y CARRY_KNOWLEDGE |
| REPORT_CARRY_RR1.md | 2026-06-14 | CARRY-RR1 执行报告 | NOT APPROVED | 状态： completed；审查结论： NOT APPROVED | 审查结论： NOT APPROVED；交付；3. 更便宜等效实现： 先做文本盲审和解析功效计算即可识别阻塞，无需运行回测或读取任何结果数据。 | 2. 量化验收： 任务要求 A/B/C/D、二元结论、最小必改；审查发现原 §5 本身尚未量化闭合。；3. 更便宜等效实现： 先做文本盲审和解析功效计算即可识别阻塞，无需运行回测或读取任何结果数据。；4. 禁止项： 未读取 Holdout/01MEMORYCORE/，未改预登记，未运行回测，未简化成本或引入黑箱依赖。 | Carry | Y CARRY_KNOWLEDGE |
| REPORT_CARRY_RR2.md | 2026-06-14 | CARRY-RR2 执行报告 | NOT APPROVED | 状态： completed；审查结论： NOT APPROVED | 审查结论： NOT APPROVED；RR1 条件完全闭合： 2/8；交付 | 2. 量化验收： RR1 八项逐条给出 CLOSED/PARTIAL/NOTCLOSED、证据行、剩余缺口，并输出二元结论和最小必改。；3. 更便宜等效实现： 文本与公式一致性审查即可识别阻塞，不需要运行回测或读取任何 Holdout。；4. 禁止项： 未读取 Holdout/01MEMORYCORE/，未修改预登记，未运行回测，未改假设或成本模型。 | Carry | Y CARRY_KNOWLEDGE,SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_CARRY_RR3.md | 2026-06-14 | CARRY-RR3 执行报告 | NOT APPROVED | 状态： completed；审查结论： NOT APPROVED | 审查结论： NOT APPROVED；RR2 剩余条件完全闭合： 4/6；交付 | 4. 禁止项： 未读取 HOLDOUT/01MEMORYCORE/，未修改预登记，未运行回测，未改成本模型或研究假设。；裁决摘要；- [x] 输出二元结论 NOT APPROVED、4/6 CLOSED 和最小必改。 | Carry | Y CARRY_KNOWLEDGE |
| REPORT_CARRY_V3_DRAFT.md | 2026-06-14 | CARRY-V3-DRAFT 执行报告 | NOT APPROVED | 状态： completed（起草完成，待独立 Reviewer 盲审）；审查结论： 本轮不作 APPROVED/NOT APPROVED 自审裁决 | 审查结论： 本轮不作 APPROVED/NOT APPROVED 自审裁决；交付 | 4. 禁止项： 未读取 Holdout/01MEMORYCORE/，未运行回测，未修改 v2，未改变 §0 核心重构或机制命题。；六项闭合 | Carry | Y CARRY_KNOWLEDGE |
| REPORT_CARRY_V4_DRAFT.md | 2026-06-14 | CARRY-V4-DRAFT 执行报告 | NOT APPROVED | 状态： completed（草案完成，待独立 Risk Reviewer 盲审）；审查结论： 本轮不作 APPROVED/NOT APPROVED 自审裁决 | 审查结论： 本轮不作 APPROVED/NOT APPROVED 自审裁决；交付 | 4. 禁止项： 未读取 Holdout/01MEMORYCORE/，未改历史预登记或 RR3 审查，未改 §0 核心重构，未简化成本模型。；四项闭合映射；- [x] buffer breach 与 liquidation 分级、次小时补款和禁止外部补资明确。 | Carry | Y CARRY_KNOWLEDGE,SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260615_carry_feasibility.md | 2026-06-15 | 20260615 Carry Feasibility v4 Historical Review | BLOCKED | Verdict: FAILED；Scope: Historical feasibility review only. This does not consume an independent alpha count and does not authorize core capital deployment. | Negative permission test FAIL 06RESEARCH/DATA/CARRYWORK/CARRYHOLDOUTPERMTEST.log records the blocked key-path test; decrypt-without-key was not runnable because no sealed artifact exists.；3. Input Audit Summary；Historic… | - | Carry | Y CARRY_KNOWLEDGE,SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_CARRY_FEASIBILITY.md | 2026-06-19 | REPORTCARRYFEASIBILITY | BLOCKED | Verdict: FAILED；[专业异议] | Blocked / Failed Steps；- Stage 1 sealed holdout creation failed before encryption because the required external key directory is not writable in this execution sandbox: | - | Carry | Y CARRY_KNOWLEDGE,SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_DATA-001_carry_data_procurement.md | 2026-06-20 | REPORT DATA-001 — carry v4 缺失数据采购 | BLOCKED | 状态： blocked；执行时间： 2026-06-20 UTC | 状态： blocked；执行时间： 2026-06-20 UTC；执行命令： python3 06RESEARCH/CODE/procurecarrydata.py --output 08DATA/carry --timeout 5 | 对CARRYKNOWLEDGE.md的更新建议；建议更新 02KNOWLEDGEBASE/CARRYKNOWLEDGE.md §三 当前阻塞状态：；- 将阻塞2细分为三个外部前置条件：网络可达 Binance 官方域名、安装 parquet engine（pyarrow 或 fastparquet）、提供只读 Binance futures API key/secret 用于 signed endpoints。 | Carry | Y CARRY_KNOWLEDGE,SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_CARRY_SCAFFOLD.md | 未知 | REPORTCARRYSCAFFOLD | PASS | - 未生成真实数据验收数值、验收判决或 edge 结论。；- 未引入 MLFinPy 等不可审计依赖。 | - | 已按任务号准备提交，但当前沙箱禁止写入 .git/index.lock，git add 返回；Operation not permitted，因此本会话无法创建 commit。交付文件保持在工作树，；未暂存或回退任何并行任务改动。 | Carry | Y CARRY_KNOWLEDGE |
| 20260612_carry_feasibility.md | 2026-06-12 | Delta-neutral carry feasibility accounting | PASS | - Conclusion: worth entering formal pre-registration only as a low-capacity, operations-heavy carry hypothesis, not as a standalone high-return strategy. BTC/ETH pass the coarse historical cost screen; SOL remains reference-only … | - | Recommendation；Enter formal pre-registration for BTC/ETH only if the next task explicitly adds spot history, basis measurement, liquidation/margin stress, execution workflow, and capital-efficiency constraints. Do not pre-register SOL carr… | Carry | Y CARRY_KNOWLEDGE |
| 20260615_carry_scaffold_selftest.md | 2026-06-15 | Carry Delta-Neutral Scaffold Self-Test | PASS | decision, or edge conclusion. It did not read Holdout or 01MEMORYCORE/. | - | - | Carry | Y CARRY_KNOWLEDGE |
| REPORT_CARRY_RR4.md | 2026-06-15 | CARRY-RR4 执行报告 | PASS | 状态： completed；评审结论： APPROVED | - | 任务已完成，无中断恢复项。下一步由 Claude 按评审结论验收和调度。 | Carry | Y CARRY_KNOWLEDGE,SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_funding_feasibility.md | 2026-06-06 | 资金费率可行性前置（Phase 1 首个方向） | UNKNOWN | 4. 结论与路线判断；1. BTC/ETH 资金费率长期为正（~88%），年化 carry 14~17% → delta 中性 carry（现货多+永续空）是真实、高胜率、价格中性的边，是迄今最像"可部署"的方向。 | - | - | Carry | Y CARRY_KNOWLEDGE |
| 20260613_carry_empirical_analysis.md | 2026-06-13 | Delta-Neutral Carry 实证分析 | UNKNOWN | Delta-Neutral Carry 实证分析；日期： 2026-06-13 | - | carry sleeve 是真实可行的 edge，建议进入正式预登记流程。；BTC carry（11.5-13.9% 净年化）对于 30k 本金贡献约 3,450-4,170 元/年，这是低风险的基础底仓收益。意义不在于"让项目赚大钱"，而在于：① 为核心资本提供低相关性的复利基础；② 与 A-1 研究形成协同（carry 退出信号 = A-1 触发 = 研究利用同一数据）。；ETH carry 收益更高但风险更大，建议初期以 BTC 为主（70%）、ETH 为辅（30%）… | Carry | Y CARRY_KNOWLEDGE |

### 系统工程（18）

| 文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复? |
|---|---:|---|---|---|---|---|---|---|
| REPORT_UNIVERSE_PIT.md | 2026-06-12 | REPORTUNIVERSEPIT | FAILED | 结论；已生成 Binance USDT-M 永续 PIT universe 数据资产： | 数据缺口与可信度；- exchangeInfo 当前返回 646 个已上市 USDT-M perpetual 合约，包含 119 个 SETTLING 退市/下架合约；这是本资产的 PIT 日期主来源。；- data.binance.vision 官方网页的 list.js 声明其目录表来自 https://s3-ap-northeast-1.amazonaws.com/data.binance.vision。当前代理 HTTPSPR… | - 排除了 PENDINGTRADING symbol，因为其尚非历史可交易合约，不应进入 PIT 可交易集合。；复算命令 | 系统工程 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_VERIFY_LIQ_COLLECTOR_20260621.md | 2026-06-21 | REPORTVERIFYLIQCOLLECTOR20260621 | BLOCKED | 任务状态： blocked；执行时间： 2026-06-21T16:43:20Z | 任务状态： blocked；执行时间： 2026-06-21T16:43:20Z；目标： 核实并修复 Tencent SG VM root@43.160.200.224:/opt/aiquantliqcollector/ 强平采集器真实数据流 | 本会话可用的指定入口存在，但当前执行沙箱禁止出站 TCP 连接，SSH 在认证前被本地策略拒绝。；已验证：；需要在允许本地命令出站连接 43.160.200.224:22 的 Codex/终端环境中恢复执行。继续使用指定 sshpass SSH 入口，不需要也不应切换到浏览器/WebShell。 | 系统工程 | N |
| REPORT_PANEL_REFRESH_2026_20260622.md | 2026-06-22 | REPORTPANELREFRESH202620260622 | BLOCKED | Symbol 状态 源 新下载行 合并止点 行数 失败摘要；AAVEUSDT downloaded binancefapi 3355 2026-06-22 00:00:00 12450 | BLOCKED：本次没有完成真实 2026 面板刷新。；原因不是交易所下架普遍失败，而是当前执行环境网络出口不可用：环境变量指向 127.0.0.1:7897，该端口不可连接；探测到宿主有其他代理监听端口，但命令沙箱连接本地 TCP 端口返回 Operation not permitted。在该约束下，Binance、Bybit、DefiLlama/Tokenomist URL 均无法从脚本层访问。；我没有伪造 K 线，也没有把旧面板… | - | 系统工程 | N |
| REPORT_P1PIPE_SUMMARY.md | 2026-06-27 | REPORTP1PIPESUMMARY | KILL | 最终状态：停在 Step 3，未进入 Step 4；纪律声明：未碰 Holdout；未进 B2；未下最终 KILL/PROCEED 裁决；未用付费 API；未把文章样本冒充全量。 | S3 解锁日历 + overlap blocked DefiLlama emissions 402；Tokenomist API/CSV/历史全量不在免费边界；免费结构化事件数=0，overlap episode=0；S4 B1-KILLCARD not executed S3 episode < 50，按硬护栏不执行；产出文件 | 建议不要把这次写成机制 KILL；应写成“数据门 blocked”。原因是价格/OI/funding 基础腿已就绪，失败点只在事件表。；3. 若拿到事件表，下一次 B1 的过滤口径。；先用 S1/S2 的可用性过滤：post-2025 价格 universe=31；近端 OI 完整=29；近端 OI+funding 完整=25。事件落在 FTM/REN/LRC/UNI/XMR/XTZ 缺口后，不能做完整资金流分档或 ex-funding 拆账。 | 系统工程 | N |
| REPORT_LIQUIDATION_DATA_OPTIONS.md | 2026-06-22 | [专业异议] 强平数据是否必须立即付费 | PASS | 结论；“连续、历史、跨交易所、事件级全量强平数据通常需要付费”基本成立。 | - | 因此建议暂停“立即订阅 1-2 个月全量强平数据”，先执行一个低成本可证伪门。只有免费组合显示方向性和单调性后，再购买连续事件级历史数据。；官方证据；建议的两阶段门 | 系统工程 | N |
| REPORT_A1_OI_FEATURES.md | 2026-06-12 | REPORTA1OIFEATURES | PASS | REPORTA1OIFEATURES；生成时间（UTC）：2026-06-12T00:49:32Z | - | - 禁止项：未新增事件、阈值、Holdout、收益代码路径；未修改 A-2 既有模块；未执行 git commit。 | 系统工程 | N |
| REPORT_FIX_COLLECTOR.md | 2026-06-14 | REPORTFIXCOLLECTOR | PASS | 结论；- 任务状态：completed | - | 4. 禁止项：未触碰 Holdout、研究数据、成本模型或其他业务服务；未使用浏览器/WebShell；未记录或提交代理凭据。；证据；建议 | 系统工程 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_PB1.md | 2026-06-14 | REPORTPB1 | PASS | No event-forward return or edge conclusion PASS；No HOLDOUT or A1WORK/sealed content read PASS | - | - | 系统工程 | N |
| 20260615_pb1_harness_selftest.md | 2026-06-15 | PB1 强平解析与就绪门计数器自测 | PASS | 任务性质： 离线工具/监控，不耗 Alpha 计数，不计算事件后收益，不下 edge 结论。；模块用途 | - | 阈值在时点 t 只使用 t 之前的滚动名义额，禁止当前值进入自身阈值。；episodestart 将连续超阈值区间只计为一个 pulse；相邻消息间隔达到一个；短窗时重置 pulse。allhits 仅作为参数化审计模式。 | 系统工程 | N |
| REPORT_P1PIPE_S1_PANEL.md | 2026-06-27 | REPORTP1PIPES1PANEL | PASS | 结论；Step 1 通过，允许进入 Step 2。 新面板 FUTURESEXPANDED2026 有 31 个 4H 合约，全部止于 2026-06-22 00:00:00，满足“到 2026-06”的止点要求；与旧 FUTURESEXPANDED 的共同 symbol 接缝连续：旧面板最后一根 2024-12-09 20:00:00 在新面板中存在，下一根为 2024-12-10 00:00:00，无接缝跳空。 | - | 下一步闸门：通过，进入 Step 2 OI/funding 回填。 | 系统工程 | N |
| REPORT_P1PIPE_S2_OIFUNDING.md | 2026-06-27 | REPORTP1PIPES2OIFUNDING | PASS | 结论；Step 2 通过，允许进入 Step 3，但后续结构资金流分档必须带数据可用性过滤。 | - | 下一步闸门：通过，进入 Step 3。Step 3 overlap 统计要同时给“价格 overlap”和“结构资金流 overlap”两种口径。 | 系统工程 | N |
| REPORT_P1PIPE_S3_UNLOCK.md | 2026-06-27 | REPORTP1PIPES3UNLOCK | PASS | 结论；Step 3 闸门不通过，任务链停在 Step 3；不得进入 Step 4 B1-KILLCARD。 | - | Step 3 闸门不通过，任务链停在 Step 3；不得进入 Step 4 B1-KILLCARD。；免费边界下没有拿到可复现的 post-2025 全量/准全量结构化 unlock event 表。最终可用于普查的事件数为 0：；按任务硬护栏，Step 3 overlap episode < 50，停止，不进入 Step 4。下一步需要 Claude 回来裁决：是否购买/申请可审计 unlock event 数据，或改任务方向为“只研究 Tokenomist 免费/试用可… | 系统工程 | N |
| REPORT_FIX_COLLECTOR_URL.md | 2026-06-13 | REPORTFIXCOLLECTORURL | COMPLETED | 结论；- 任务状态：completed | - | heartbeat 输出 processmessages= 字面量，因此在不得修改其余逻辑的约束下，；2-3 分钟验收使用同一 messagecount 的 [message] count0 证据。；首次检查时文件从 10 行增至 11 行；持续性复验： | 系统工程 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260611_data_inventory.md | 2026-06-11 | 数据盘点（N4） | UNKNOWN | 数据盘点（N4）；日期： 2026-06-11 ｜ 执行： Claude（接管夜跑批次） | - | 3. 🔴 缺口一：无 5m/15m 价格K线。METRICS 有 5M 粒度但不含价格；价格最细 1H。影响：A-1 抢级联回弹的入场时机研究在 1H 粒度下偏粗（级联多在分钟级展开）。建议：R2 的 A-1 事件研究先用 1H 价格验证"事件后24-72h回弹是否存在"（机制层够用）；确认机制存在后再补 5m K线（Binance API 可得）做执行层研究——不要现在就补（先证机制，避免建无用数据）。；4. 缺口二：ETH/SOL METRICS 始于 2021-12（… | 系统工程 | Y TREND_TSMOM_LESSONS_v1 |
| 20260611_event_census.md | 2026-06-11 | R2 前置：极端事件普查（N3，审计 P0-3） | UNKNOWN | 对 R2 预登记的结论（按 Protocol v1.3 增补件 §四）；1. 任何单品种×单阈值都不够 300 探索级 → R2 全部走跨品种池化 + 阈值单调性检验（P95→P97.5→P99 效应应单调增强），禁用 60/20/20 时间三分，Holdout 按事件级预切。 | - | 4. 检验次数预算建议：A-2 主检验 ≤6 次（2方向×3窗口），A-1 ≤4 次；超出即须多重检验贴现说明。；5. ⚠️ 本普查用全样本算分位数（含未来信息）——仅用于设计检验方案，正式 R2 的阈值必须用滚动/扩张窗口分位（无前视）。 | 系统工程 | N |
| 20260612_a4_listing_census.md | 2026-06-12 | A-4 新上市数据普查 | UNKNOWN | 结论；- UNIVERSEPIT.csv 共 646 个 Binance USDT-M 永续合约；2022 起新上市 530 个。 | - | - | 系统工程 | N |
| 20260612_collector_dataplane.md | 2026-06-12 | 20260612 Collector Data-Plane Diagnostic | UNKNOWN | 判定矩阵；Path Client Proxy URL Handshake Frames First frame s Elapsed s Verdict Error | - | Collector Patch Recommendation；全部测试路径 60s 零数据帧；按任务书口径，结论为 "Mac 侧无解，须 VM 直跑"。不建议在 Mac 采集器上继续打补丁。；Reproducibility | 系统工程 | N |
| REPORT_DEPLOY_COLLECTOR_VM.md | 2026-06-13 | REPORTDEPLOYCOLLECTORVM | UNKNOWN | 结论；强平采集器已部署到新加坡腾讯云服务器，并以独立 systemd 服务常驻运行。 | - | - | 系统工程 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,V4_REUSABLE_ASSETS_v1 |

### 工具OSS（6）

| 文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复? |
|---|---:|---|---|---|---|---|---|---|
| REPORT_RESEARCH-AI-NATIVE-20260621.md | 2026-06-21 | RESEARCH-AI-NATIVE-20260621 公司级综合分析 | PASS | 一、结论先行；1. 这些文章真正共同指向什么 | - | 任务性质： 外部资料综合、项目事实核验、行动设计；日期： 2026-06-21；输入： Founder 提供 31 个链接；项目现有顶层治理、Agent 协作、任务路由、Discord、OSS 和研究行动文件 | 工具OSS | Y TOOLS_KNOWLEDGE |
| REPORT_VERIFY_V462.md | 2026-04-23 | REPORTVERIFYV462 | COMPLETED | 结论；- 任务状态：completed | - | 建议在独立修复任务中执行部署和重启，验收顺序：；1. 先用 /market/ws/btcusdt@aggTrade 确认 10 秒内有帧。；2. 改为 /market/ws/!forceOrder@arr 后重启采集器。 | 工具OSS | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,TOOLS_KNOWLEDGE,V4_REUSABLE_ASSETS_v1 |
| REPORT_RESEARCH_OSS.md | 2026-06-19 | REPORTRESEARCHOSS | COMPLETED | 要求 状态；调研 CCXT 能力/成熟度/成本/接入难度/推荐结论 完成 | - | 调研 Freqtrade / NautilusTrader / vectorbt 生态并给地基建议 完成；调研 Binance 官方 SDK + data.binance.vision + mark/contract/funding/OI 正确取法 完成；调研 Coinglass / CoinAPI / Kaiko / Amberdata 强平、funding、OI 覆盖与成本 完成 | 工具OSS | Y TOOLS_KNOWLEDGE |
| REPORT_OSS-001_oss_tool_synthesis.md | 2026-06-20 | REPORTOSS-001osstoolsynthesis | COMPLETED | 执行摘要；1. DEC-076 的主线未被推翻：1个月 carry 实盘路线仍应围绕 Freqtrade + CCXT + Binance 官方 REST/data.binance.vision + 项目自写数据/风控/对账薄层。 | - | 技能说明： 任务书指定 research-harvest + diagnose。当前 Codex 技能列表未暴露 research-harvest，仅按 diagnose 做遗漏/矛盾检查；该工具链缺口已写入更新建议。；执行摘要；3. 最高价值立即行动不是换框架，而是补三件轻量能力：Freqtrade futures dry-run 模板、lookahead/slice-check、Jesse式路径 Monte Carlo + Qlib式 experiment regist… | 工具OSS | Y TOOLS_KNOWLEDGE |
| REPORT_GOV_TOOLING_EVAL_CODEX_20260621.md | 2026-06-21 | REPORTGOVTOOLINGEVALCODEX20260621 | COMPLETED | 问题 结论；任务在验证什么机制？ 验证“过去失败是否应靠更多工具解决，还是靠轻治理/纪律/状态一致性解决”。 | - | 验收标准是否可量化？ 是：逐条回答 6 个必答问题，给出总裁决和最高信息增益下一步。；有无更便宜等效实现？ 有且已采用：只读指定文档并写反审报告，不建任何治理系统。；是否触碰禁止项？ 否：未读 Holdout，未改预登记，未跑回测，未建工具，未改 Claude 独占权威文件。 | 工具OSS | Y TOOLS_KNOWLEDGE |
| REPORT_V5_DESIGN_EXTRACTION_POST_0510.md | 2026-05-10 | REPORTV5DESIGNEXTRACTIONPOST0510 | UNKNOWN | 重要结论： 5月10日之后，“V5”的含义发生了迁移：；- 早期 V5：从 V4.6.2 冻结后启动的 单 Setup / 结构事件研究分支。 | - | 按 2026-05-20 之后的版本折叠，V5 不应定义为“一个自动交易脚本”或“一个 OpenClaw/Hermes Agent 系统”，而应定义为：；AI Quant Company：一套 AI-native Quant Research Operating System。；投研和执行运营不应在 Phase 0 抢跑。 | 工具OSS | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,STRUCTURE_SETUP_FAILURE_LESSONS_v1,TOOLS_KNOWLEDGE,V4_REUSABLE_ASSETS_v1 |

### TSMOM-Alpha（29）

| 文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复? |
|---|---:|---|---|---|---|---|---|---|
| REPORT_D2.md | 未知 | REPORTD2 | BLOCKED | 状态；BLOCKED。 变体 C 复现完成；变体 A/B 未执行，原因是继续执行会违反单变量、完整成本和 DEC-070 universe 约束。 | BLOCKED。 变体 C 复现完成；变体 A/B 未执行，原因是继续执行会违反单变量、完整成本和 DEC-070 universe 约束。；七问自查；6. 最可能失败原因：扩展资产高相关/高 beta 使表面分散无效，或低质量小币引入更大尾部；当前输入无法区分。 | 4. 禁止项：未读 Holdout、未改预登记、未简化成本、未用全样本分位、未引黑箱依赖。；5. 变量能否作用于 DD：能，但只有价格源、成本和 universe 质量固定时才是 universe 单变量。；6. 最可能失败原因：扩展资产高相关/高 beta 使表面分散无效，或低质量小币引入更大尾部；当前输入无法区分。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_B1.md | 2024-12-09 | REPORTB1 | FAILED | - B1 判定：FAILED。；- E[R] 0：True (0.016321)。 | - | - 禁止项：未读 HOLDOUT，未读 2026H1，未改预登记，未调参，未引黑箱依赖。；验收自检 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_D1.md | 2024-12-09 | D1 TSMOM Universe Tier 1 数据下载执行报告 | BLOCKED | 状态；BLOCKED - 本地沙箱禁止出站网络连接，未完成数据下载。 | BLOCKED - 本地沙箱禁止出站网络连接，未完成数据下载。；实际报错：；脚本检测到该权限错误后停止继续请求 Binance，避免把同一环境错误重复打到 35 个资产。DOWNLOADMANIFEST.json 已生成，但成功资产数为 0，D1 验收未通过。 | BLOCKED - 本地沙箱禁止出站网络连接，未完成数据下载。；实际报错：；- 禁止项：脚本不读取 Holdout，不修改 06RESEARCH/DATA/FUTURES/，不引入黑箱依赖，不读取全样本分位。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_TSMOM_DUAL_ENGINE.md | 2024-12-10 | REPORTTSMOMDUALENGINE | FAILED | - 引擎 L/S 独立二值判定：已写入 RESULTS 报告。；- 策略数据边界：回测脚本未读取 2026H1 文件，未解析 2024-12-10 之后行情/资金费；所有使用数据末条 timestamp 已列出且 <= 2024-12-09 23:59 UTC。 | - | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260606_tsmom_trend.md | 2026-06-06 | P1-01 TSMOM 90日趋势策略回测 | FAILED | 结论： FAILED / COST-LIMITED；1. 门槛结论 | Sharpe 0.720 1.0 未通过；MaxDD 68.38% < 25% 未通过；净收益 +345.76% 诊断项 - | 不建议在本任务内加入中性带或修改回看期。若继续研究，必须作为新的；预登记假设；同时需先处理 68% 回撤和空头侧负贡献，而不能只优化成本。 | TSMOM-Alpha | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,TREND_TSMOM_LESSONS_v1 |
| 20260606_tsmom_voltarget.md | 2026-06-06 | P1-02 TSMOM v2 波动率目标定仓 | FAILED | 结论： FAILED；1. 联合门槛 | 净 Sharpe 0.720 0.505 1.0 未通过；毛 Sharpe 1.043 0.916 诊断项 毛边沿下降；MaxDD 68.38% 69.70% <25% 未通过 | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_P1_01_TSMOM.md | 2026-06-06 | REPORT-P1-01 TSMOM 时间序列趋势策略回测 | FAILED | 状态： COMPLETED；实验判定： FAILED / COST-LIMITED | - | Claude 待处理事项；1. 将 P1-01 状态登记为 FAILED / COST-LIMITED。；2. 将独立 Alpha 失败计数从 4/8 更新为 5/8。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_P1_02_TSMOM_VOLTARGET.md | 2026-06-06 | REPORT-P1-02 TSMOM v2 波动率目标定仓 | FAILED | 状态： COMPLETED；实验判定： FAILED | - | Claude 待处理事项；1. 将 P1-02 登记为 FAILED，不要标记 COST-LIMITED。；2. 历史实验失败总数应由 9 更新为 10；独立 Alpha 维持 5/8。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260612_tsmom_dual_engine.md | 2026-06-12 | TSMOM 扩样本·多空双引擎 v1 | FAILED | 判定；- 引擎 L：FAILED | - | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260612_tsmom_v2_riskbudget.md | 2026-06-12 | TSMOM dual engine v2 risk budget | FAILED | 判定；- B1 二值判定：FAILED | - | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260613_d1_tsmom_tier1_download.md | 2026-06-13 | D1 TSMOM Tier 1 数据下载结果 | FAILED | 结论；D1 数据下载未完成。原因是当前 Codex 沙箱禁止出站网络连接，首次请求 Binance monthly kline ZIP 时返回： | D1 数据下载未完成。原因是当前 Codex 沙箱禁止出站网络连接，首次请求 Binance monthly kline ZIP 时返回：；text；network permission denied: [Errno 1] Operation not permitted | D1 数据下载未完成。原因是当前 Codex 沙箱禁止出站网络连接，首次请求 Binance monthly kline ZIP 时返回：；text；network permission denied: [Errno 1] Operation not permitted | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260613_tsmom_extended_backtest_report.md | 2026-06-13 | D2 TSMOM 扩展 Universe 信号层回测 | BLOCKED | 技术结论；任务状态：BLOCKED。不能回答“扩 universe 后 P(DD≥20%) 是否 <10%”。 | 任务状态：BLOCKED。不能回答“扩 universe 后 P(DD≥20%) 是否 <10%”。；变体 C 已按冻结的 8 币 tsmomdualL 口径精确复现；变体 A/B 因输入不满足同源价格、真实 funding 和 DEC-070 universe 审计要求而暂停。用零 funding 或混用 contract/mark K 线继续计算会直接违反成本完整与单变量原则。；E[R] per trade 0.066073 BL… | - 结论字段保持 null，不得把阻塞结果写成 DDimproved 或 DDnotimproved。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260613_tsmom_universe_expansion.md | 2026-06-13 | C1 TSMOM Universe 扩充可行性评估 | FAILED | 结论；状态：FAILED（网络/代理错误导致 HEAD 结果不完整）。 | - | 当前不能给出 universe 扩充规模建议；需在 HTTPSPROXY=http://127.0.0.1:7897 可用后复跑脚本。；口径；禁止项自检 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_BUILD_PROJECT_PLAN.md | 2026-06-15 | BUILDPROJECTPLAN 执行报告 | FAILED | 状态： COMPLETED / 待 Claude 验收、待 Founder D 级确认推荐项；任务前七问自查 | 2. 量化验收： 9 个能力域、7 条 L1 价值流、Phase 0-3、缺口矩阵、成熟度热力、统一状态 taxonomy、逐任务七字段、真实状态回填、权威指针和完成事件均可计数核验。；3. 更便宜等效实现： 直接重用现有 Markdown、DEC/报告/预登记证据和现有目录，不引入新项目管理系统或数据库。；4. 禁止项： 未读取 Holdout；未修改 DECISIONLOG、预登记或研究结论；未改成本模型；未使用全样本分位；未引入… | 4. 禁止项： 未读取 Holdout；未修改 DECISIONLOG、预登记或研究结论；未改成本模型；未使用全样本分位；未引入黑箱依赖；失败项保留为失败/废弃。；已完成；2. 建立 PROJECTTASKPLAN.md 作为唯一详细任务权威，共 108 个唯一任务；逐项包含 ID、任务、状态、负责人、依赖、下一步和证据。 | TSMOM-Alpha | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,TREND_TSMOM_LESSONS_v1 |
| REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md | 2026-06-22 | REPORTX3MOMENTUMREDTEAMB120260622 | KILL | 最终裁决: KILL；脚本: 06RESEARCH/CODE/x3momentumredteamb1audit.py | 关键理由：未通过：截面单调/显著门、幸存者偏差门、被动基准门、v1.3 年化log增长、v1.3 赢亏比；默认 KILL 基线下不得靠改 L/分位/频率续命。 | - 禁止项检查：未读取 Holdout；未改预登记；未使用全样本分位阈值；未引入黑箱依赖；失败按 KILL 写入。；1. 阶段 0 方向红队；关键理由：未通过：截面单调/显著门、幸存者偏差门、被动基准门、v1.3 年化log增长、v1.3 赢亏比；默认 KILL 基线下不得靠改 L/分位/频率续命。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| X3_MOMENTUM_REDTEAM_B1_20260622.md | 2026-06-22 | X3 Momentum Redteam B1 Result - 2026-06-22 | KILL | Verdict: KILL；Stage 0: PROCEED to fixed-parameter B1 audit. | Final reason: 未通过：截面单调/显著门、幸存者偏差门、被动基准门、v1.3 年化log增长、v1.3 赢亏比；默认 KILL 基线下不得靠改 L/分位/频率续命。 | Final reason: 未通过：截面单调/显著门、幸存者偏差门、被动基准门、v1.3 年化log增长、v1.3 赢亏比；默认 KILL 基线下不得靠改 L/分位/频率续命。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_B2.md | 未知 | REPORT B2 | MIXED | 状态： COMPLETED；结论： P1-04 第五件失败；P1-06 第五件通过。昨日 P1-06 大额负超额是追溯口径差，不是 P1 冻结窗口结论。 | - | 4. 禁止项：未改预登记，未读 HOLDOUT 内容，未用全样本分位，未引黑箱依赖，未提交 git。；结果 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260612_fifth_criterion_verification.md | 2026-06-12 | B2 第五件追溯复算验证 | MIXED | 结论；独立复算显示，按 P1 冻结快照和 B2 字面门控口径：P1-04 第五件失败，P1-06 第五件通过。 | - | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_P1_05_REGIME_ATTRIBUTION.md | 未知 | REPORT P1-05：两轴市场状态归因 | DIAGNOSTIC | REPORT P1-05：两轴市场状态归因；专业审查七问 | - | Claude 待处理事项；1. 审阅并决定是否把“P1-04 下一版采用高周期宏观牛市过滤”升级为正式预登记；建议保持单变量，不只过滤 trendupbear。；2. 在 DECISIONLOG/CURRENTSTATE 中记录：精确反弹陷阱假设被否定，宏观熊市暴露解释得到支持；本任务不计失败。 | TSMOM-Alpha | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,TREND_TSMOM_LESSONS_v1 |
| 20260606_regime_attribution.md | 2026-06-06 | P1-05 两轴市场状态归因 | DIAGNOSTIC | P1-05 两轴市场状态归因；日期： 2026-06-07 | - | - 建议交 Claude 审阅： 下一预登记若以 P1-04 为基础，最干净的单变量是宏观牛市过滤，而不是只过滤 trendupbear。Sweep 应保留为“牛市下跌/震荡后的反弹”候选机制，另行预登记验证。；口径限制；- 交易 MaxDD 是把每个状态格的交易按退出时间独立串联、以 $100,000 为基准的诊断值，不是可交易组合的反事实净值；部分格可低于 -100%，不得用于仓位决策。 | TSMOM-Alpha | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,TREND_TSMOM_LESSONS_v1 |
| REPORT_P1_06_TSMOM_MACRO_BULL.md | 未知 | REPORT P1-06：TSMOM + 宏观牛市门控 | PASS | 2. 证据是否支持继续？ 支持。P1-05 显示 P1-04 的 2022 负向状态格亏损有 94.4% 位于宏观熊市。；3. 有无更上游问题未答？ 没有。状态定义和归因已经由 P1-05 完成，本任务正是研究铁律第 4 步。 | - | Claude 待处理事项；1. 将 P1-06 登记为 PASSED / EXPLORATORY，但注明“机制部分验证、非 P1-04 全面升级”。；2. 不增加失败计数；独立 Alpha 维持 5/8。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260606_tsmom_regime_long.md | 2026-06-06 | P1-04 Regime-First 长偏向 TSMOM | PASS | 结论： PASSED / EXPLORATORY；1. 冻结门槛 | - | “趋势强度过滤”，不是完整的牛熊方向分类器。下一步不应调 ADX 阈值，应先由；Claude 决定是否增加独立的高周期方向层并重新预登记，或直接启动一次性；Holdout 确认。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_P1_04_TSMOM_REGIME_LONG.md | 2026-06-06 | REPORT-P1-04 Regime-First 长偏向 TSMOM | PASS | 状态： COMPLETED；实验判定： PASSED / EXPLORATORY | - | Claude 待处理事项；1. 将 P1-04 登记为 PASSED / EXPLORATORY，不是确认级通过。；2. 不增加失败计数；独立 Alpha 保持 5/8。 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| 20260607_tsmom_macro_bull.md | 2026-06-07 | P1-06 TSMOM + 宏观牛市门控 | PASS | 结论： PASSED / EXPLORATORY，但未证明全面优于 P1-04；Holdout： 未访问 | - | - SMA200 预热不足标为 unknown 并禁止做多。；- 状态在 t 确认，统一于 t+1 4H 开盘执行；转熊不使用收盘价偷跑。；- ADX 14/25/20、L=540、成本、资金费率、目标权重和 gross≤1x 均继承 P1-04。 | TSMOM-Alpha | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,TREND_TSMOM_LESSONS_v1 |
| 20260610_tsmom_recheck_new_criteria.md | 2026-06-10 | TSMOM 新口径复读（DEC-066④授权，纯重算 / 无新实验 / Holdout 未访问） | PASS | 性质： 重打分，不是新证据。样本同前（探索级），WF/Holdout 结论不变。；预登记判据（计算前锁定，防搬龙门） | - | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_P1_03_DATA_RECON_OI.md | 2026-06-06 | REPORT-P1-03 持仓量/清算数据可得性核查 | COMPLETED | 状态： COMPLETED；性质： 纯数据核查，未做收益或预测力分析 | - | - 官方公共仓库未发现历史清算归档，第一版信号不得依赖 liquidation。；数据总览；Claude 待处理事项 | TSMOM-Alpha | N |
| REPORT_GOV-AUTO-001_TOP_LEVEL_ANALYSIS.md | 2026-06-20 | GOV-AUTO-001 项目顶层治理与 Claude-Codex 高自治协作分析 | COMPLETED | 状态： ANALYSIS / 供 Claude 独立论证，非正式架构决策；日期： 2026-06-20 | - | 本报告是给 Claude 的独立分析输入。Claude 应逐条反驳、确认或修订，不应直接把本报告升级为 DECISION。；1.1 本报告覆盖矩阵；实时风控 什么能力未建成前禁止实盘，AI 不得进入哪条权限链 | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1,TOOLS_KNOWLEDGE |
| REPORT_STRATEGIC_REVIEW_ARENA_METHOD_20260622.md | 2026-06-22 | REPORTSTRATEGICREVIEWARENAMETHOD20260622 | COMPLETED | 结论状态: completed；0. 执行前自查 | - | 4. 禁止项：未触碰 Holdout；未改预登记；未简化成本模型；未引入依赖；未把失败写成成功。；1. 最终裁决；我的独立结论不是“换板块救项目”，而是“换机制层级 + 分层 universe + 把事件/资金流升格”。加密合约仍是当前核心猎场，但不是因为 alpha 最厚，而是因为它在多空对称、杠杆表达、免费结构数据、24x7、低准入上综合最优。A 股可能 payer 最肥，但不符合当前“市场中性多空对称 + 快速可复现系统化”的硬约束，只能作为中期研究观察或外部合作方向… | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |
| REPORT_TSMOM_EXPANSION_DATA.md | 2026-06-11 | REPORTTSMOMEXPANSIONDATA | UNKNOWN | REPORTTSMOMEXPANSIONDATA；Generated: 2026-06-11 16:19:41 UTC | - | - | TSMOM-Alpha | Y TREND_TSMOM_LESSONS_v1 |

### 治理审计（15）

| 文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复? |
|---|---:|---|---|---|---|---|---|---|
| REPORT_A1_RR3.md | 2026-06-14 | A1-RR3 执行报告 | NOT APPROVED | 状态： completed；正式输出： 06RESEARCH/PREREGISTRATIONS/A1RISKREVIEWv3.md | APPROVED/NOT APPROVED 明确结论 NOT APPROVED；最小第三轮必改 完成，共 5 项；历史样本不可约判断 yes，仅强平方向/因果归因不可约；其余可修复 | - | 治理审计 | N |
| REPORT_A1_RR4.md | 2026-06-14 | A1-RR4 执行报告 | NOT APPROVED | 状态： completed；审查结论： NOT APPROVED | 审查结论： NOT APPROVED；RR3 条件完全闭合： 2/5；交付 | - | 治理审计 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_P1RES039_PHASEA_20260622.md | 2026-06-22 | REPORTP1RES039PHASEA20260622 | KILL | 结论：本地价格腿真实存在，但不能覆盖 2024-12-09 之后事件。；B2. 解锁日历源 schema / 免费边界 | - | 建议：不应直接进 B1。 应先补一个可复现的历史解锁事件源，或补 post-2024-12-09 价格面板并只研究当前/未来解锁。理由：；1. B0 对“解锁日历免费且不截断”的表述过强。Tokenomist/TokenUnlocks 的公开网页能看当前/未来表格，API/CSV 才能稳定拿事件级历史数据；Tokenomist 文档显示 API 需要 x-api-key，CSV 导出是 Pro 功能，Free trial/Standard 的 Unlock Events 历… | 治理审计 | N |
| REPORT_DEC070_AUDIT.md | 2024-12-10 | DEC070-AUDIT 执行报告 | PASS | 状态：COMPLETED（审计任务完成；DEC-070 四过滤器仍未全部验证）；[专业异议] | - | float 和 OI 三部分仍缺输入或定义。D2 的 DEC070FILTERSNOTAUDITABLE 不应仅凭；本报告被整体解除。 | 治理审计 | N |
| 20260613_c5_governance_report.md | 2026-06-13 | C5 Governance Report | PASS | C5 Governance Report；确认：04AITEAM/RUNLOG.jsonl 追加 B1-B5 结构化条目 5 条（JSONL 校验通过，共 7 行）；04AITEAM/AGENTREGISTRY.md 追加脚本/文档注册条目 10 条（B1-B5 5 条，C1-C4 5 条）。 | - | - | 治理审计 | N |
| 20260614_dec070_filter_audit.md | 2026-06-14 | DEC-070 过滤器可审计性审计（35 候选资产） | PASS | 摘要：4 过滤器可审计性；过滤器 本地可算? 结论 | - | - ADTV 建议门槛：最近 180 日中位数 ≥10m USDT/day 为达标，5m-10m 为边缘，<5m 为不达标。其含义是 10,000 USDT 订单在门槛处约占中位日成交额 0.10%；这是容量初筛，不替代盘口冲击模型。；- 跳动：rt = ln(closet/close{t-1})，仅统计时间戳严格相差 4H 的连续 bar；jump(J)=1(rtJ)，频率为异常次数/有效连续收益数。；- 跳动建议门槛：主阈值 J=15%；频率 ≤0.20% 达标，0.2… | 治理审计 | N |
| REPORT_A1_RR5.md | 2026-06-14 | A1-RR5 执行报告 | PASS | 状态： completed；审查结论： APPROVED | - | - | 治理审计 | N |
| REPORT_E1.md | 2026-06-14 | REPORTE1：公司组织架构文档 | PASS | 状态：COMPLETED；执行日期：2026-06-14 | - | - 禁止项：未触碰 Holdout、未改预登记、未改成本模型、未用全样本分位、未引入依赖、未包装失败结论、未超范围优化。 | 治理审计 | N |
| REPORT_E2.md | 2026-06-14 | REPORTE2：技术系统架构文档 | PASS | 状态：COMPLETED；执行日期：2026-06-14 | - | - 禁止项：未触碰 Holdout、预登记、成本模型、全样本分位或权威内存文件，未引入依赖或扩展任务范围。 | 治理审计 | N |
| REPORT_E3.md | 2026-06-14 | REPORTE3：执行工作流文档 | PASS | 状态：完成；日期：2026-06-14 | - | - 禁止项：未触碰 Holdout、未修改预登记/研究协议、未读取或修改 01MEMORYCORE/；验收自检；- Git 提交未完成：当前环境禁止写入 .git/index.lock，无法执行 git add | 治理审计 | N |
| REPORT_DRAFT_MASTERPLAN.md | 2026-06-15 | DRAFTMASTERPLAN 执行报告 | PASS | 状态： completed（两份文件均为 DRAFT，待 Founder D 级确认/验收）；专业异议： 无。任务方向正确，且已用反膨胀边界限制治理扩张。 | - | 4. 禁止项检查： 未读 Holdout，未改 DECISIONLOG、预登记、研究文件、成本模型或实时任务台账。；2. 交付物；- 明确禁止单策略复制订单、状态、风控、监控、账务或数据库底座。 | 治理审计 | N |
| REPORT_P0-C_HYGIENE.md | 2026-06-21 | REPORTP0-CHYGIENE | PASS | 任务在验证什么机制？ 验证研究输入卫生：旧状态、规则冲突、假绿灯不得污染 B0-B4。；验收标准是否可量化？ 是：退出码、路径定位、坏串命中、最新 DEC 一致性、自测、冲突清单、冻结清单。 | - | 范围： T1 statecheck 修复；T2 四份规则文件冲突裁决建议；T3 防扩张闭环。；未改动： CLAUDE.md、AGENTS.md、01MEMORYCORE/SYSTEMRULES.md、04AITEAM/AGENTREGISTRY.md 正文均只读，未直接修改。；执行前七问自查 | 治理审计 | N |
| REPORT_E4.md | 未知 | REPORTE4：系统模块设计文档 | COMPLETED | - 每个模块均包含职责、组件、依赖、当前状态、负责方。；- 补充模块依赖图与 Phase 2 建设优先级。 | - | Claude 验收时建议同步判断：是否需要把 Phase 2 蓝图 §五中的执行风控参数补记为正式 DEC，避免后续实现阶段出现“蓝图参数已写、DEC 来源不足”的审计断点。 | 治理审计 | N |
| REPORT_BPR_TOP_LEVEL_FRAMEWORK_REVIEW.md | 2026-06-15 | REPORTBPRTOPLEVELFRAMEWORKREVIEW | COMPLETED | 状态： completed；完成时间： 2026-06-15T03:59:51Z | - | 4. 将待 Claude 评估建议写入 CURRENTSTATE §1c。；核心判断；- OPERATINGMODELDESIGNv2 应重定位为策略交付生命周期 SOP，不应继续承担公司运营模型职责。 | 治理审计 | N |
| REPORT_P0RES038_PHASEA_20260622.md | 2026-06-22 | P0-RES-038-B1-PHASEA 报告 | COMPLETED | 纪律声明：未读取 HOLDOUT/、未回测、未调参、未做方向择优；描述统计只作毛效应上限与 B1 冻结建议，不作显著性或方向结论。；A. 机制红队反审 B0 卡 | - | 纪律声明：未读取 HOLDOUT/、未回测、未调参、未做方向择优；描述统计只作毛效应上限与 B1 冻结建议，不作显著性或方向结论。；A. 机制红队反审 B0 卡；但 AGENTS.md 铁律写明手续费 0.1%/边，即 10bp/边；按项目硬纪律，应同时或优先报告 80/120/220bp。建议 B1 把 70/110/210bp 作为乐观交易费口径，把 80/120/220bp 作为纪律硬口径，除非 Claude 明确覆写手续费假设。 | 治理审计 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |

### 其他（56）

| 文件名 | 日期 | 主题 | 结论或状态 | 核心发现 | 根因 | 负面结论或行动建议 | 类别 | 疑似与现有知识库重复? |
|---|---:|---|---|---|---|---|---|---|
| REPORT_0B4_V4_STRATEGY_BACKTEST.md | 2026-06-06 | 执行报告 TASK-0B4 v4 Strategy Backtest | FAILED | 任务状态： COMPLETED；策略结论： FAILED | 判定规则为 Sharpe1.0 且 MaxDD<25%。MaxDD 通过，Sharpe 未通过，因此；策略 FAILED。；交易漏斗：425 候选 = 360 成交 + 63 同品种持仓冲突 + 2 已占满 1x | Claude 待处理事项；1. CURRENTSTATE 建议更新；- v4 完整策略回测：COMPLETED / FAILED； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_B1_KILLCARD_FORCED_FLOW_20260621.md | 2026-06-21 | REPORTB1KILLCARDFORCEDFLOW20260621 | KILL | 结论：OFI KILL；清算流休眠；lead-lag 当前 KILL。；成本带（round-trip drift hurdle，来自审计脚本）： | 原因不是“OFI 没有统计相关性”，而是当前任务问的是交易路径：非共置、分钟级、全成本、含 maker 成交率和逆选折扣后，合理毛效应上限不能超过有效成本；同时本地没有可审计 aggTrades/L2 连续重建数据。；6.2 免费清算流 | 总建议：不进 B2。；子机制 总裁决 依据；禁止两头测后择优。当前免费数据状态下，“用真实强平流直接观测”这一点也没有成立，因此不能与墓园 A-1 的 OI proxy 48h 回弹 FAILED 做真实区分。清算路径继续推进会成为 A-1 换皮。 | 其他 | N |
| REPORT_REDTEAM_FORCED_FLOW_20260621.md | 2026-06-21 | [专业异议] REPORTREDTEAMFORCEDFLOW20260621 | KILL | 总裁决：ACCEPT-with-MODIFY，但当前 B0 的 PROCEED 到 B1（建议 OFI 先行） 判定过宽，必须降级为 REVISEONCE。；强制/激进流作为机制家族有真实 payer，但 B0 当前把两个高风险子机制放得太宽： | - | 总裁决：ACCEPT-with-MODIFY，但当前 B0 的 PROCEED 到 B1（建议 OFI 先行） 判定过宽，必须降级为 REVISEONCE。；强制/激进流作为机制家族有真实 payer，但 B0 当前把两个高风险子机制放得太宽：；我的建议不是直接杀掉整个强制/激进流方向，而是杀掉 “按当前 B0 直接推进 OFI 或免费强平流 B1”。B1 若要继续，必须改成一个更窄的 数据-功效 Kill Card，先证明可检测、可交易、可审计，再允许进入 B2。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_atr_strategy.md | 2026-06-06 | 0B17 ATR×1.9 动态止损策略回测 | FAILED | 判定： FAILED；预登记判定 | Sharpe 0.86 1.00 未通过；MaxDD 24.80% <25.00% 通过；联合门槛未满足，因此实验 FAILED。MaxDD 距离上限约 0.20 个百分点，但失败 | 有限，不建议在没有 L3 审计的情况下消耗最后一次失败机会。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_choch_fvg_bull_v1_EVAL.md | 2026-06-06 | 实验结论报告 | FAILED | 实验结论报告；实验版本号： v5sweepchochfvgbullv1 | 三个窗口均为正，但收益、Sharpe和Expectancy连续下降。根据预登记“无明显持续衰减”的要求，判定未通过。；参数敏感性 | 假设无效。 当前版本在真实永续标记价格、历史资金费率和完整交易成本下，不满足预登记门槛；不得进入 Holdout，不得进入实盘，不应围绕当前参数继续优化。；虽然预-Holdout全区间组合净值增长68.9%，但这是长时间持有风险暴露下的累计结果，不能覆盖以下失败事实：；本版本按预登记条件判定失败。Holdout 不启用，不为当前 Setup 提供任何最终确认信息。不得通过修改止盈、Regime、品种权重或信号窗口把本版本重新包装为成功；任何新设计必须建立新版本并重新预登记。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_choch_fvg_bull_v2_EVAL.md | 2026-06-06 | 实验结论报告 | FAILED | 实验结论报告；实验版本号： v5sweepchochfvgbullv2 | 表现从强正快速衰减到负值，未通过Walk-Forward。；参数敏感性；- 时期稳定性和跨品种稳定性未通过。 | 本版本失败，不得通过调整1H窗口参数、删除BTC/ETH、改变Regime或修改止盈规则把本版本重新包装为成功。任何后续研究必须提出新的、更基础的可证伪假设。；下一步建议；停止研究当前三重确认交易链。下一假设应降维为单事件研究： | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_only_bull_v3_EVAL.md | 2026-06-06 | 实验结论报告 | FAILED | 实验结论报告；实验版本号： v5sweeponlybullv3 | 预登记要求三个窗口全部均值为正且p < 0.05。t+24未通过，因此整体假设失败。；此外，t+12效应从Walk-Forward第一段的+1.441%衰减至+0.262%和+0.089%，后两段均不显著。时期分层显示正向效应主要集中于2021，不能解释为跨时期稳定预测力。；因此普通t检验p值可能偏乐观。本实验即使采用该偏乐观方法，t+24仍未通过，且稳定性审计失败。无需进一步复杂校正即可拒绝主假设。 | t+6和t+12的合并显著结果只能作为“短期、时期依赖的弱证据”，不得直接声称Sweep因子有效，更不得升级为完整交易策略。；下一步建议；不建议立即围绕Sweep继续调整窗口或Regime。连续三个假设失败已达到DEC-022的L3紧急审计触发条件，应由Claude先执行L3审计，再决定下一Alpha来源。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_regime_bear_v5_EVAL.md | 2026-06-06 | 实验结论报告 | FAILED | 实验结论报告；实验版本号： v5sweepregimebearv5 | 校正后三窗口均未通过。跨品种同期相关性仍未消除，因此不能把当前 p 值解释得；比该校正更强。；Red Team 自查 | 完整事件数为 344，按 DEC-018 属探索级，不得作为实盘依据。；主检验；结论与下一步 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_regime_bull_v4_BACKTEST.md | 2026-06-06 | 实验结论报告 | FAILED | 实验结论报告；实验版本号： v5sweepregimebullv4strategy | Sharpe 0.31 未通过 1.0；Sortino 0.42 偏低；MaxDD 19.08% 通过 <25% | 结论与下一步；策略未达到 Sharpe 门槛，不应打开 Holdout，也不应进入实盘候选。失败并非；完全由成本造成：成本侵蚀严重，但 2022、SOL 和晚期 Walk-Forward 的交易 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_regime_bull_v6b_BACKTEST.md | 2026-06-06 | v6b Sweep 止损位置对照回测 | FAILED | 结论： FAILED；Holdout： 未读取，固定 nrows 物理截断 | 三品种版本 FAILED。baseline 的 Sharpe 和 MaxDD 均未通过。；BTC + ETH | Holdout 保持封存，不得据此开启。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_regime_bull_v7_EVAL.md | 2026-06-06 | 实验结论报告 | FAILED | 实验结论报告；实验版本号： v5sweepregimebullv7 | v4 的任何核心稳定性缺口，不具备可观察的增量研究价值。；条件 3 只从 v4 的 425 个事件中删去 14 个，保留 411 个，仍满足探索级。；被删事件全部来自 2019-2021；2022 的 12 个负贡献事件一个也未过滤， | 目标时期不匹配，不是阈值执行错误。不得在本版本中调整阈值或窗口。；时期分层；不建议仅因形式主检验通过就立即安排 v7 策略回测；v4 策略已证明退出与成本 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_volpos_strategy.md | 2026-06-06 | 0B18 波动率缩仓策略回测 | FAILED | 判定： FAILED / 机制无效；联合门槛 | 退出时间和退出原因。；机制检验；1. 总体 Sharpe 0.78，未通过联合门槛； | 按 DEC-044/045/046，v4 的止损、退出、仓位实现研究至此关闭。不得调整；180、0.66、0.5、250 或改用另一个恐惧度定义继续追试。下一步应转向全新、；独立预登记的 Alpha 假设。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B10_WIDER_STOP.md | 2026-06-06 | 执行报告 TASK-0B10 v6b 止损位置对照 | FAILED | 任务状态： COMPLETED；实验结论： FAILED | - 历史资金费率真实读取，缺口按 0.01%/8h；；- Holdout 固定 nrows 物理截断，未读取；；- 原有回测规则测试：3/3 通过； | 新假设，禁止据此查看 Holdout。；Claude 待处理事项；1. 建议记录 v6 baseline：三品种 Sharpe 0.87 / MaxDD 36.32%，BTC+ETH | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B11_REGIME_V3.md | 2026-06-06 | 执行报告 TASK-0B11 Regime V3 | FAILED | 任务状态： COMPLETED；形式主假设： PASSED | 2022 和 WF 第二段缺口，答案为否。由于它只删除早期事件并使总体均值略降，；不建议立即执行 v7 策略回测。继续调 20% 阈值或 90 日窗口会违反本次单变量；预登记，若探索其他 Regime 必须建立新版本。 | 不建议立即执行 v7 策略回测。继续调 20% 阈值或 90 日窗口会违反本次单变量；预登记，若探索其他 Regime 必须建立新版本。；Claude 待处理事项 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B17_ATR_STRATEGY.md | 2026-06-06 | 执行报告 TASK-0B17 ATR 动态止损策略 | FAILED | 状态： COMPLETED；实验结论： FAILED | 3. 记录压力测试：Sharpe 0.95 / MaxDD 14.93%，仍未通过；；4. 更新 CURRENTSTATE.md，标明 ATR 止损解决部分回撤问题，但未解决；WF2/WF3 稳定性； | Claude 待处理事项；1. 将 0B17 记录为 FAILED，并将权威失败计数更新为 7/8；；2. 记录主结果：Sharpe 0.86 / MaxDD 24.80% / 止损率 47.74%； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B18_VOLPOS_STRATEGY.md | 2026-06-06 | 执行报告 TASK-0B18 波动率缩仓策略 | FAILED | 状态： COMPLETED；实验结论： FAILED / 机制无效 | - 所有 236 笔退出时间、原因与 0B17 ATR×3.5 一致；；- 高恐惧仓位比例逐笔 0.5，低恐惧逐笔 1.0；；- 百分位独立重算误差 <2e-16； | Claude 待处理事项；1. 将 0B18 记录为 FAILED，并确认机制无效；；2. 按 DEC-044/046 并列更新： | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B1_SWEEP_EVENT_STUDY.md | 2026-06-06 | 执行报告 TASK-0B1 Sweep Event Study | FAILED | 任务状态： COMPLETED；实验结论： FAILED | - | Claude 待处理事项；1. DECISIONLOG建议；本实验结果是FACT，不建议直接新增“决策”条目。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B3_BEARISH_SWEEP.md | 2026-06-06 | 执行报告 TASK-0B3 Bearish Sweep | FAILED | 任务状态： COMPLETED；主假设结论： FAILED | t+24 未通过预登记门槛，因此主假设 FAILED。非重叠校正后三窗口全部不显著。；关键解释；未通过。t+6、t+12 原始合并统计显著为负，但 t+24 失败；非重叠校正后三窗口 | Claude 待处理事项；1. 做空信号是否通过；不应把做空腿加入当前候选策略。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260611_a2_event_study.md | 2026-06-11 | A-2 Funding Extreme Reversal Event Study | FAILED | Conclusion: FAILED；Six Registered Tests | - | - | 其他 | N |
| REPORT_R2_A2_EVENT_STUDY.md | 2026-06-11 | REPORTR2A2EVENTSTUDY | FAILED | Conclusion: FAILED；Deliverables | - | - | 其他 | N |
| 20260613_a1_vs_a2_mechanism_diff.md | 2026-06-13 | A-1 与 A-2 机制区分分析（Risk Reviewer 碰撞门准备材料） | FAILED | Risk Reviewer 前置说明： 本文件将随预登记提交，作为 A-2 碰撞门的通过依据或拒绝依据。如结论为"碰撞点过大"，则 A-1 预登记须补充额外隔离条件或等待前向强平数据后再立项。；- 实证判决：双向均无可检测 edge（六检验全不显著）；n=91 功效不足是局部原因，更根本的是"先验错误"——交易所博客级外部 grounding，未经独立检验 | 1. A-2 失败的精确根因；根据墓园索引及 B4 报告：；- 实证判决：双向均无可检测 edge（六检验全不显著）；n=91 功效不足是局部原因，更根本的是"先验错误"——交易所博客级外部 grounding，未经独立检验 | 4. 可能的碰撞点及处理方案；碰撞点 1：部分 A-1 事件发生在 A-2 触发条件下（高 funding 期间发生强平）；- 处理方案：在 A-1 事件研究中，加入"事件前 24h funding 分位"作为分层变量——如果高 funding 期间的 A-1 事件 CAR 与低 funding 期间无显著差异，则 A-2 失败对 A-1 的有效性无直接否定力 | 其他 | N |
| REPORT_A1_TIERA.md | 2026-06-14 | REPORTA1TIERA | BLOCKED | PASS/FAILED 科学判决，不能以数据缺失或权限阻塞改写为 FAILED。；已完成 | [专业异议] A1TIERA 当前为 BLOCKED，不得运行事件后收益计算。；REPORTA1TIERA；阻塞原因 | [专业异议] A1TIERA 当前为 BLOCKED，不得运行事件后收益计算。；REPORTA1TIERA；且 RR5 明确要求封存和正式执行身份负向权限测试完成前不得计算事件后收益。 | 其他 | N |
| REPORT_A1_TIERA_EXEC.md | 2026-06-14 | REPORTA1TIERAEXEC | FAILED | 状态： completed；判决： FAILED | 最终判决为 FAILED。48h CAR 点估计为 1.3225%，raw p=0.115988，Holm 后 p=0.315568，basic 95% CI=[-0.9528%, 3.2674%]，未通过主硬门。；§11 验收逐项 | - | 其他 | N |
| 20260615_a1_tierA_screen.md | 2026-06-15 | A-1 Tier A 历史关联快筛 | FAILED | 项目 判决 估计/数值 raw p Holm p basic 95% CI n neff (ICC=0.5)；48h CAR（硬门） FAIL 1.3225% 0.115988 0.315568 [-0.9528%, 3.2674%] 152 131.58 | - | - | 其他 | N |
| REPORT_X2_RV_REDTEAM_B1_20260622.md | 2026-06-22 | [专业异议] REPORTX2RVREDTEAMB120260622 | KILL | 最终裁决: KILL；B1 是否执行: 否。按任务书要求，阶段 0 判 KILL 后停止，不进入 B1 三门。 | B1 门 结论 关键数字 / 原因；门1 两腿成本门 未执行；阶段 0 已被成本逻辑 KILL base taker break-even 0.80%；maker+逆选下界 0.48%；压力 1.60% / 2.40% / 4.40%。；门2 协整稳定门 未执行 不假设总回归；阶段 0 已判断 crypto 协整/相关关系不具备足够强先验，且负外溢文献更像脱钩/趋势尾部证据。 | - 禁止项检查：未读取 Holdout；未改预登记；未调参；未扫全配对；未引入黑箱依赖。；1. 阶段 0 方向红队；这意味着每次配对交易必须先跨过 0.48% 到 0.80% 的正常成本门，压力下是 1.60% 到 4.40%。对于高流动性主流币同 beta 配对，现实中可持续、可捕获、未被竞争吃掉的均值回复空间不应被预设为高于 0.8%；若实际偏离经常大于此，先进入的一般是做市/套利库存而不是慢速研究策略。 | 其他 | N |
| X2_RV_REDTEAM_B1_20260622.md | 2026-06-22 | X2 RV Redteam B1 Result - 2026-06-22 | KILL | Verdict: KILL；B1 gates run: No. Stage 0 killed the line before statistical testing. | - | - | 其他 | N |
| 20260606_atr_stop_diagnostic.md | 2026-06-06 | 0B16 ATR 动态止损诊断 | DIAGNOSTIC | 核心结论；ATR×3.5 的平均止损距离为 8.69%，远宽于 sweeplow 的 2.30% 和 | - | 建议；若启动下一次计入失败的策略回测，建议预登记 纯 ATR×1.9 止损 作为主；候选，而不是 max(reflow, ATR×3.5)： | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_mae_analysis.md | 2026-06-06 | 0B14 MAE / MFE 诊断 | DIAGNOSTIC | 核心结论；盈利交易 MAE 的 80 分位为 4.38%，即止损距离约需达到入场价的 | - | 建议；后续止损研究应使用波动率归一化，而不是直接把 4.38% 固定应用于所有品种。；诊断参考中心为 1.9x ATR，3.5x ATR 可作为更宽压力测试；SOL 应单独检查 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_no_stop_t24_diagnostic.md | 2026-06-06 | 0B12 t+24 无止损诊断 | DIAGNOSTIC | 结论；完全删除止损、每笔固定使用入场时账户净值 10% 名义仓位、持有至第 24 | - | 建议： 不自动消耗第 7 次失败机会。先由 Claude 审阅本诊断，再决定是否；继续已预设的 0B13。若继续，必须保持原预登记门槛，不得依据本结果修改。；产物 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_time_exit_sensitivity.md | 2026-06-06 | 时间退出持仓期敏感性诊断 | DIAGNOSTIC | 结论；1. t+24 是六组中风险调整收益最强的持仓期，且相对 t+12 的日收益改善在探索性 bootstrap 中为正。 | - | 4. 建议，非决策： t+24 可作为下一版预登记的候选退出期，但不应按当前仓位/止损结构直接升级；必须在运行前固定回撤控制变量，并重新做独立验证。；产物与验证 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_vol_compression_analysis.md | 2026-06-06 | 0B15 波动率压缩分组分析 | DIAGNOSTIC | 结论；两种压缩定义都未验证“压缩组信号更强”： | - | 框架下的有效过滤器。不建议增加第三或第四层波动压缩条件。；定义；建议 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B12_NO_STOP_DIAGNOSTIC.md | 2026-06-06 | 执行报告 TASK-0B12 t+24 无止损诊断 | DIAGNOSTIC | 任务状态： COMPLETED；性质： 诊断，不计入失败次数 | - | Claude 待处理事项；1. 审阅并记录 0B12：三品种 Sharpe 1.28 / MaxDD 12.06%，BTC+ETH；Sharpe 1.06 / MaxDD 7.38%；本任务不改变失败计数 6/8； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B14_MAE_ANALYSIS.md | 2026-06-06 | 执行报告 TASK-0B14 MAE 分析 | DIAGNOSTIC | 状态： COMPLETED；性质： 诊断，不计失败次数 | - | Claude 待处理事项；1. 记录盈利交易 MAE 80 分位 4.38%，对应 1.87x ATR；；2. 记录 sweeplow 与 reflow 平均距离均处于盈利交易正常 MAE 区间内； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B15_VOL_COMPRESSION.md | 2026-06-06 | 执行报告 TASK-0B15 波动率压缩分组 | DIAGNOSTIC | 状态： COMPLETED；性质： 诊断，不计失败次数 | - | Claude 待处理事项；1. 记录 V4 历史波动压缩 IC 因子在当前 v4 双层 Regime 下未复现；；2. 不建议增加波动率压缩过滤层，压缩样本也低于 300； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B16_ATR_STOP_DIAGNOSTIC.md | 2026-06-06 | 执行报告 TASK-0B16 ATR 止损诊断 | DIAGNOSTIC | 状态： COMPLETED；性质： 诊断，不计失败次数 | - | 建议下一策略假设以 ATR×1.9 为主参数，3.5x 作为压力测试。任务书建议的；max(reflow, ATR×3.5) 没有复合效果，因为它在全部事件中都退化为纯；ATR×3.5。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B8_TIME_SENSITIVITY.md | 2026-06-06 | 执行报告 TASK-0B8 时间退出敏感性 | DIAGNOSTIC | 状态： COMPLETED；任务性质： 诊断，不计失败 | - | Claude 待处理事项；1. t+12 comparator：三品种 Sharpe 0.59 / MaxDD 37.83%；BTC+ETH Sharpe 0.58 / MaxDD 26.59%。；2. 最优持仓期：t+24，但三品种 MaxDD 37.63%、BTC+ETH MaxDD 27.26%，不应直接升级。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B9_STOP_DIAGNOSTIC.md | 2026-06-06 | 执行报告 TASK-0B9 止损触发诊断 | DIAGNOSTIC | 任务状态： COMPLETED；实验计数： 纯诊断，不计入失败计数 | - | Claude 待处理事项；1. 审阅“止损过早为主因、固定TP限制补偿”为何种后续假设依据；；2. 如预登记更宽止损，必须维持风险预算并按止损距离缩小仓位； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0A6_SIGNAL_DETECTOR.md | 2026-06-05 | 执行报告 TASK-0A6 | PASS | 状态： COMPLETED；数据修正附注（2026-06-06）： 0A-NEW2 发现原 BTC 文件缺失 2020-07 和 2024-07。补齐后使用同一检测器重跑，当前结果为：16,267根K线、Sweep 738、CHoCH 2,410、FVG 1,507、三重确认465。下方456次为任务首次执行时的原始验收记录。 | - | - | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,STRUCTURE_SETUP_FAILURE_LESSONS_v1 |
| 20260606_v4_bootstrap_validation.md | 2026-06-06 | v4 Bootstrap 稳健性验证报告 | PASS | 结论： Bootstrap 支持 v4 样本内正均值，但不改变时期稳定性仍未完全通过的边界；方法核验 | - | 因此建议标注为：v4 样本内统计信号三层稳健性校验通过；跨时期稳定性仍未完全通过。；产物 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v5_sweep_regime_bull_v4_EVAL.md | 2026-06-06 | 实验结论报告 | PASS | 实验结论报告；实验版本号： v5sweepregimebullv4 | - | 结论与下一步；事件未来窗口可能重叠，三个品种同期收益也存在相关性，普通 t 检验的独立性；假设并不严格成立，p 值可能偏乐观。此外，本研究未包含成本、退出规则、仓位 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B2_SWEEP_DUAL_REGIME.md | 2026-06-06 | 执行报告 TASK-0B2 Sweep Dual Regime | PASS | 任务状态： COMPLETED；主假设结论： PASSED | - | Claude 待处理事项；1. CURRENTSTATE 建议更新；请由 Claude 审阅后写入： | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B5_V4_BOOTSTRAP.md | 2026-06-06 | REPORT 0B5 — v4 Bootstrap 稳健性验证 | PASS | 状态： COMPLETED；Holdout： 未访问 | - | Claude 待处理事项；1. Bootstrap p 值：；- t+6：0.005799 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_0B6_BACKTEST_UNIT_TESTS.md | 2026-06-06 | REPORT 0B6 - Backtest Unit Tests | PASS | REPORT 0B6 - Backtest Unit Tests；Task: 0B-6-v5 | - | Claude 待处理事项；1. PASS/FAIL: 9 PASS, 0 FAIL, 0 ERROR.；2. P1-4 audit item: May be marked resolved for the requested repeatable | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| REPORT_R1_A2_FEATURES.md | 2026-06-11 | REPORTR1A2FEATURES | PASS | 结论： 已交付 A-2 funding 极端事件特征脚本、工作集事件表、事件级 Holdout 文件与 pytest。未读取 MARK 价格文件，未做收益/价格反应分析。；交付物 | - | - 禁止项：未读取 MARK 文件；未改预登记；未引入第三方 TA/事件库；未做收益分析。 | 其他 | N |
| 20260612_a1_mde_precheck.md | 2026-06-12 | A-1 MDE Precheck（B4） | PASS | 结论；功效门预判：通过。 | - | 禁止项自检；- 未读取或写入 HOLDOUT 目录。；- 未计算事件后实际收益。 | 其他 | N |
| REPORT_B3.md | 2026-06-12 | REPORTB3 — A-4 新上市数据普查 | PASS | - 原始 HEAD 状态只有 200 与 404，无 timeout/URLError；可得率未受网络失败污染。；- Funding 用 monthly 归档 HEAD 判断覆盖月份可得性；因任务禁止下载，未验证 monthly ZIP 内部逐条 funding 行。 | - | - Funding 用 monthly 归档 HEAD 判断覆盖月份可得性；因任务禁止下载，未验证 monthly ZIP 内部逐条 funding 行。 | 其他 | N |
| REPORT_B4.md | 2026-06-12 | REPORTB4 | PASS | 结论：三个 horizon 的 MDE 均低于 1.5%-3.0% 机制合理效应区间下沿，因此 B4 功效门输入件预判为 通过。；自实现公式 | - | 4. 禁止项检查： 不碰 HOLDOUT，不改预登记，不算事件后收益，不使用全样本分位，不读 2024-12-10 后行情参与计算。；交付物 | 其他 | N |
| REPORT_B5.md | 2026-06-12 | REPORTB5 - 采集器数据面隔离测试 | PASS | 结论: 全部可握手 Mac 侧路径 60s 零 aggTrade 数据帧。按任务书口径判定：Mac 侧无解，须 VM 直跑。；任务前自查 | - | 是否触碰禁止项 不读 HOLDOUT，不读 06RESEARCH/DATA/；但初始 broad rg 误显过 post-cutoff 行情行，见“偏差记录”；产出；采集器建议 | 其他 | N |
| 0A5_REGIME_SAMPLE_GAP_REPORT.md | 2026-06-06 | 0A-5 Regime 样本缺口核查 | COMPLETED | 状态： COMPLETED；目的： 在首个假设预登记前验证 Research Protocol 强制 Regime 条件后的真实样本量 | - | 建议（未决策）；将 SOL/USDT 4H 纳入首个探索级假设，品种为 BTC、ETH、SOL；分别报告单品种结果和组合结果。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,STRUCTURE_SETUP_FAILURE_LESSONS_v1 |
| 0A_NEW2_ETH_EXTENSION_REPORT.md | 2026-06-06 | 0A-NEW2 ETH 样本扩展报告 | COMPLETED | 状态： COMPLETED；适用决策： DEC-018、DEC-024 | - | 两个合并口径均处于 DEC-018 的 探索级（300-499）。当前样本足以启动第一个研究闭环，但禁止据此进入实盘；后续仍需扩样本升级到至少500次确认级。；数据；可用于定义并执行第一个研究假设和完成 Phase 0A 的首个研究闭环；不得进入实盘候选，除非后续扩样本达到至少500次且其他研究门槛全部通过。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,STRUCTURE_SETUP_FAILURE_LESSONS_v1 |
| 0A_NEW2_SAMPLE_FEASIBILITY_REPORT.md | 2026-06-06 | 0A-NEW2 样本量可行性核查报告 | COMPLETED | 状态： COMPLETED；后续修正（2026-06-06）： 本报告使用的 BTC 文件缺失 2020-07 和 2024-07。数据补齐并加入 ETH 后，最新结论见 0ANEW2ETHEXTENSIONREPORT.md。本报告保留用于追踪修正过程，不再作为当前样本量结论。 | - | 方案A：并入 ETH/USDT 4H（建议优先）；保持三重确认语义、参数和4H周期不变，在 ETH 上独立检测，再按“品种 + 唯一入场时刻 + 正风险”合并统计。；代价： 改变信号语义并提高噪声，容易演变为为了满足样本门槛而调规则，存在数据挖掘偏差。当前不建议。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2,STRUCTURE_SETUP_FAILURE_LESSONS_v1 |
| V2_1H_SAMPLE_FEASIBILITY_REPORT.md | 2026-06-06 | 第二候选假设：1H样本可行性报告 | COMPLETED | 状态： COMPLETED；核心结论 | - | 建议；创建独立版本 v5sweepchochfvgbullv2，正式预登记后运行训练、验证、Walk-Forward和完整成本回测。不得使用1H结果反向修改窗口参数。 | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260613_a1_framework_report.md | 2026-06-13 | C3 A-1 事件研究框架报告 | COMPLETED | 结论；状态：COMPLETED。已在 B4 MDE 报告末尾追加 alpha-only / alpha+beta 双参数对照表，并新增 A-1 事件研究框架与合成数据 pytest。 | - | 禁止项自检；- 未读取 HOLDOUT 路径。；- 未读取真实行情数据。 | 其他 | N |
| 20260606_v4_nonoverlap_validation.md | 2026-06-06 | 非重叠子集校正验证报告 | UNKNOWN | 窗口 原始(N=425) 均值 原始 p 非重叠(N=215) 均值 非重叠 p 结论；t+6 +0.770% 0.000078 +0.595% 0.0213 ✅ 仍显著 | - | - | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| 20260606_v4_stop_diagnostic.md | 2026-06-06 | v4 策略止损触发诊断 | UNKNOWN | 仅 11 笔交易，结论方向明确、精度有限。2021 止损率最低且平均 R 最高，与；既有时期稳定性结论一致。 | - | 六、供 Claude 决策的建议；建议，不是既定决策：；- 下一次预登记优先验证更宽、且预先定义的结构止损或风险等价止损； | 其他 | Y SWEEP_SIGNAL_FAILURE_LESSONS_v2 |
| A1_FORWARD_EVENT_COUNT.md | 2026-06-14 | A1 Forward Liquidation Event Count | UNKNOWN | performance metrics, or edge conclusion. All trigger parameters below are；placeholders and must be frozen only by the formal Path B preregistration. | - | - | 其他 | N |

## 2. 待写条目草稿（不写正式库）

以下编号均为暂存编号，不代表正式 C/RA 编号。

### Carry

#### 教训C-DRAFT-CARRY-001：[草稿待Claude审] Carry 可行性必须先过数据与封存权限门，不能用 scaffold 或粗筛报告替代 v4 历史可行性
**来源：** REPORT_CARRY_FEASIBILITY.md；20260615_carry_feasibility.md；REPORT_CARRY_SCAFFOLD.md  
**核心发现：** v4 可行性失败的主因不是单一参数，而是 custodian 封存、8类输入、真实 funding/bracket/事件压力和权限负向测试未闭合。synthetic self-test 只能证明代码骨架可运行，不能证明策略可行。  
**对当前研究的影响/行动建议：** Carry 进入正式研究前必须先列数据输入权威清单、封存工件、权限负向测试和可复跑审计；缺任一项时只能写 BLOCKED/FAILED，不得包装为部分成功。

#### 教训C-DRAFT-CARRY-002：[草稿待Claude审] BTC/ETH carry 是低容量、运营重策略，不是高收益 Alpha 替代品
**来源：** 20260612_carry_feasibility.md；20260613_carry_empirical_analysis.md  
**核心发现：** 粗筛材料显示 BTC/ETH 可能通过历史成本初筛，但收益来源偏基础底仓/资金费，容量和运营要求高；SOL funding 和极端波动不适合作主假设。  
**对当前研究的影响/行动建议：** 若 Claude 继续推进，候选边界应限 BTC/ETH，并把 basis、spot history、margin/liquidation stress、执行流程和资本效率写成硬门。

#### 行动RA-DRAFT-CARRY-001：[草稿待Claude审] 补齐 carry 8项数据输入和 parquet writer 环境后再复跑 feasibility
**来源：** REPORT_DATA-001_carry_data_procurement.md；20260613_carry_basis_stats.md  
**核心发现：** 数据抓取多次因代理、网络、parquet writer 缺失失败；脚本已强调 schema/range 校验失败不得写目标 parquet。  
**对当前研究的影响/行动建议：** 先修网络/代理与 pyarrow/fastparquet，再补 spot OHLCV、basis、bracket、depeg、公告等输入；失败日志保留为证据。

### 系统工程

#### 行动RA-DRAFT-SYS-001：[草稿待Claude审] 清算/aggTrade 采集器应转 VM 直跑，Mac 侧不继续补丁
**来源：** REPORT_B5.md；20260612_collector_dataplane.md；REPORT_DEPLOY_COLLECTOR_VM.md；REPORT_VERIFY_LIQ_COLLECTOR_20260621.md  
**核心发现：** Mac 可握手路径 60s 零数据帧，任务书分支结论是 Mac 侧无解；继续修本地代理/URL 只会消耗工程时间。  
**对当前研究的影响/行动建议：** 把 VM 直跑、ready gate、frame counter、run log 和部署验证作为唯一执行线。

#### 行动RA-DRAFT-SYS-002：[草稿待Claude审] 数据下载任务需要显式区分网络阻塞、源缺失和本地 writer 缺失
**来源：** REPORT_D1.md；20260613_d1_tsmom_tier1_download.md；REPORT_UNIVERSE_PIT.md；20260613_tsmom_universe_expansion.md  
**核心发现：** 多份报告把 Binance/S3/代理失败记录为 blocked/failed；这些不是 alpha 失败，但会阻塞 universe 和 TSMOM 输入。  
**对当前研究的影响/行动建议：** 后续下载报告必须输出 total/success/failed、首个失败原因、代理状态、是否写入目标文件；禁止用不完整 HEAD 结果下研究结论。

#### 教训C-DRAFT-SYS-001：[草稿待Claude审] 事件/阈值工具要用滚动可审计阈值，不允许当前值进入自身阈值
**来源：** 20260615_pb1_harness_selftest.md；20260614_dec070_filter_audit.md  
**核心发现：** PB1 与 DEC-070 审计都强调阈值和过滤器可本地复算；阈值计算必须只用 t 前数据。  
**对当前研究的影响/行动建议：** 所有 ready gate/过滤器先做离线自测与 manifest，再接研究脚本。

### 工具OSS

#### 教训C-DRAFT-TOOL-001：[草稿待Claude审] 当前瓶颈不是缺重型工具，而是轻治理、状态一致性和验证门
**来源：** REPORT_GOV_TOOLING_EVAL_CODEX_20260621.md；REPORT_RESEARCH-AI-NATIVE-20260621.md；REPORT_OSS-001_oss_tool_synthesis.md  
**核心发现：** 工具调研反复指向同一结论：Backstage/Spec Kit/Discord/Paperclip 等重工具不能解决方向纪律和状态权威问题。  
**对当前研究的影响/行动建议：** 优先做小 validator、state_check、任务事件日志、Skill/Workflow 路由；重工具必须等连续失败样本证明本地机制不足。

#### 行动RA-DRAFT-TOOL-001：[草稿待Claude审] 建立插件/Skill/MCP 的许可、版本、权限和撤销登记
**来源：** REPORT_RESEARCH-AI-NATIVE-20260621.md；REPORT_RESEARCH_OSS.md  
**核心发现：** AI 原生报告明确外部 Skill/插件有 prompt injection、恶意脚本、数据出境和许可证风险。  
**对当前研究的影响/行动建议：** 任何新工具进入研究路径前，先登记来源、版本/哈希、权限、API key 边界、撤销方式和是否可离线复现。

#### 教训C-DRAFT-TOOL-002：[草稿待Claude审] 工具只能沉淀判断或跑确定性检查，不能替 Claude 做最终研究裁决
**来源：** REPORT_V5_DESIGN_EXTRACTION_POST_0510.md；REPORT_VERIFY_V462.md  
**核心发现：** 历史 V4/V5 设计可复用的是资产和流程，不是未验证的大系统方案；过早平台化会放大错误方向。  
**对当前研究的影响/行动建议：** 工具知识库应区分“可立即用的小工具”和“Phase 2 蓝图”，不得把蓝图当当前执行依据。

### TSMOM-Alpha

#### 教训C-DRAFT-TSMOM-001：[草稿待Claude审] TSMOM 表面通过必须经第五件、WF 和 v1.3 四件套复核
**来源：** REPORT_B1.md；REPORT_B2.md；20260612_fifth_criterion_verification.md；20260610_tsmom_recheck_new_criteria.md  
**核心发现：** P1-04/P1-06 曾出现冻结窗口与追溯口径差；第五件复算显示同一策略在不同门控口径下结论可能改变。  
**对当前研究的影响/行动建议：** TSMOM 候选只能按冻结快照复算；追溯包装不能覆盖 B2 字面门控。

#### 教训C-DRAFT-TSMOM-002：[草稿待Claude审] 扩 universe / 多空双引擎未证明降低尾部风险，且输入质量先于回测
**来源：** REPORT_D2.md；20260612_tsmom_dual_engine.md；20260612_tsmom_v2_riskbudget.md；20260613_tsmom_extended_backtest_report.md  
**核心发现：** 双引擎和风险预算版本均未全过；扩 universe 因同源价格、真实 funding、DEC-070 universe 审计不闭合而 BLOCKED。  
**对当前研究的影响/行动建议：** 不得用零 funding、混用 contract/mark K 线或幸存者子集继续得出 DD 改善结论。

#### 教训C-DRAFT-TSMOM-003：[草稿待Claude审] X3 截面动量已被 Stage0/B1 红队 KILL，默认不得靠改 L/分位/频率续命
**来源：** REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md；X3_MOMENTUM_REDTEAM_B1_20260622.md  
**核心发现：** X3 未通过截面单调/显著、幸存者偏差、被动基准、年化 log 增长和赢亏比门。  
**对当前研究的影响/行动建议：** 若要重启，必须提出新机制和新数据输入，而不是调参续命。

### 治理审计

#### 行动RA-DRAFT-GOV-001：[草稿待Claude审] 把状态权威、任务计划和完成事件收敛到文件级单一事实源
**来源：** REPORT_BUILD_PROJECT_PLAN.md；REPORT_BPR_TOP_LEVEL_FRAMEWORK_REVIEW.md；20260613_c5_governance_report.md  
**核心发现：** 项目计划报告把 108 个任务、状态 taxonomy、证据和权威指针统一化；BPR 报告要求 OPERATING_MODEL 重定位为交付生命周期 SOP。  
**对当前研究的影响/行动建议：** Claude 可审后决定是否把 PROJECT_TASK_PLAN、RUNLOG、AGENT_REGISTRY 和 TASK_INBOX 的同步检查固化为 routine。

#### 教训C-DRAFT-GOV-001：[草稿待Claude审] NOT APPROVED 的价值在于关闭歧义，不是失败噪音
**来源：** REPORT_A1_RR3.md；REPORT_A1_RR4.md；REPORT_CARRY_RR1.md；REPORT_CARRY_RR2.md；REPORT_CARRY_RR3.md；REPORT_CARRY_RR4.md  
**核心发现：** 多轮 RR 把不可约历史样本、权限负向测试、OI 双腿、结算顺序和风险状态语义逐步闭合。  
**对当前研究的影响/行动建议：** 治理库应保留“最小必改”类型条目，避免未来预登记重复踩同类歧义。

#### 行动RA-DRAFT-GOV-002：[草稿待Claude审] 把 broad rg / Holdout 误显事故写成验证前置检查
**来源：** 06_RESEARCH/RESULTS/20260612_tsmom_dual_engine.md；REPORT_B5.md  
**核心发现：** 至少两份报告记录了 broad rg 或偏差行误显；即使未进入计算，也破坏 no-Holdout 自证。  
**对当前研究的影响/行动建议：** 建议在研究任务前置加路径 denylist 检查和 rg 范围模板，失败即停止。

### 其他

#### 教训C-DRAFT-OTHER-001：[草稿待Claude审] Sweep/CHoCH/FVG/v4 实现线已形成稳定负面知识，不应继续微调续命
**来源：** REPORT_0B1_SWEEP_EVENT_STUDY.md；REPORT_0B3_BEARISH_SWEEP.md；REPORT_0B4_V4_STRATEGY_BACKTEST.md；REPORT_0B17_ATR_STRATEGY.md；REPORT_0B18_VOLPOS_STRATEGY.md；20260606_v5_sweep_choch_fvg_bull_v1_EVAL.md；20260606_v5_sweep_choch_fvg_bull_v2_EVAL.md  
**核心发现：** 失败根因跨报告一致：效应集中于少数年份、t+24/WF/非重叠不过、成本与退出后策略 Sharpe 不过，仓位/止损/ATR/波动缩仓未解决方向失效。  
**对当前研究的影响/行动建议：** 把“不得调整止盈、Regime、窗口、仓位、恐惧度定义继续追试”吸收为正式负面条目。

#### 教训C-DRAFT-OTHER-002：[草稿待Claude审] A-1/A-2/清算流类机制最大风险是先验和数据源不够硬
**来源：** REPORT_A1_TIERA_EXEC.md；20260611_a2_event_study.md；20260613_a1_vs_a2_mechanism_diff.md；REPORT_B1_KILLCARD_FORCED_FLOW_20260621.md  
**核心发现：** A-2 六检验不显著，A-1 Tier A 未过主硬门；forced-flow/OFI/lead-lag 在非共置、分钟级、全成本和免费数据下被 KILL 或休眠。  
**对当前研究的影响/行动建议：** 后续任何清算/订单流议题必须先证明真实强平流或 L2/aggTrades 连续数据可得，并过成本上限门。

#### 教训C-DRAFT-OTHER-003：[草稿待Claude审] RV/X2 已在 Stage0 被 KILL，不应进入统计检验消耗资源
**来源：** REPORT_X2_RV_REDTEAM_B1_20260622.md；X2_RV_REDTEAM_B1_20260622.md  
**核心发现：** X2 RV 红队在统计测试前即被 Stage0 kill，说明机制前置门足以阻断低质量候选。  
**对当前研究的影响/行动建议：** 这类结果应进墓园候选，而不是因为没跑 B1 就视为无信息。

## 3. 给 Claude 的判断线索

- 反复出现的失败根因不是“某个参数没调好”，而是：数据输入不完整、状态/口径漂移、机制先验弱、成本门过不了、以及把 scaffold/诊断/追溯包装误当正式证据。
- FAILED/KILL/NOT APPROVED 中最有知识价值的三组：Sweep/v4 连续变体关闭；Carry v4 feasibility 的数据与权限门失败；TSMOM 在新四件套/第五件/WF 下的口径复核。
- 工具类报告基本一致：当前不应先上重型项目管理或多 Agent 平台，优先小而确定的 validator、state_check、路径 denylist、任务事件日志。
- 多份报告记录网络/代理/下载失败。这些不应计作 Alpha 失败，但会污染 universe、funding、basis、清算流等输入；需要在任务状态中单独标 BLOCKED/DATA-FAILED。
- broad rg / Holdout 误显是治理高优先级风险：即使未参与计算，也会削弱“未读 Holdout”的审计可信度。
- 很多既有知识库已覆盖大类结论（Sweep、TSMOM、Carry、工具），本轮更适合补“具体边界条件/禁止续命/数据门”而非重复写大而泛的教训。
