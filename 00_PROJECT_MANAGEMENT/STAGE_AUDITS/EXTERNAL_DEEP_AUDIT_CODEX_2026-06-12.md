# 外部独立深度审计报告（Codex 综合重审版） 2026-06-12

**审计身份：** 外部独立审计委员会，九专家逐一切换视角。  
**审计边界：** 只读项目材料与公开资料；未运行实验/回测；未读取 `06_RESEARCH/DATA/HOLDOUT/`；未修改既有项目状态文件；只写/更新本审计报告与本轮调研报告。  
**新增调研纳入：** Codex/Claude 能力优化、同类优质项目、OPC/AI-Native/AI治理/agent harness、量化/AI量化/加密永续策略、小红书替代来源 `arXiv:2605.16895`。  
**证据等级：** A=官方/同行评审/交易所 API；B=arXiv/工作论文/高质量开源文档；C=行业文章/经验线索；D=不可访问或未核验。

## 执行摘要（≤15行）

1. 项目最危险的问题不是 OS 混乱，而是 **流程成功掩盖机会地图错误**：A-2 死亡后，两主线不能继续按 DEC-066 原权重冻结。
2. `DEC-068` 若把“OS 流水线可冻结”扩展为“研究方向可冻结”，结论过宽；只能冻结协作/纪律，不能冻结 A-1/A-2 机会地图。
3. A-2 首测即死且方向相反，是机制先验失败：funding/OI 是状态变量，不天然推出反转；极端拥挤更可能是趋势延续相位。
4. TSMOM 应从“旧线候选”升级为基准线/组合底座候选；它是当前唯一较强内部正证据。
5. A-1 仍可保留，但必须改成“强制流两相位 + 数据门”候选；1H/OI 代理不能证明清算级联可交易 edge。
6. AI-Native 不是多开 AI，而是 agent-readable、eval-driven、traceable、permissioned operating system；当前只到 L1-L2，未到 L3 治理。
7. arXiv `The Alpha Illusion` 对项目是 P0 提醒：LLM 交易 agent 的 reported alpha 不能当部署证据；AI 策略只算 hypothesis。
8. 剩 2 条独立实验命：第 7 命只给通过数据门的 A-1；第 8 命保留，默认给 A-4 新上市/新永续或独立机制。
9. 低模型层有价值，但必须只能做机械 diff；禁止语义修改 DEC、Protocol 门槛、研究结论。
10. 工具路线不是继续装插件，而是项目 skill + 只读 MCP + hook 护栏；交易执行 MCP Phase 1 禁装。
11. 成本台账累计 871.93 元，runway 健康；但 Claude/Codex/服务器月度细项仍待填，5000 元硬止损尚未完全可审计。
12. 本审计建议：先补 AI Alpha Evidence Gate、A-1 数据门、agent trace，再花第 7 命。

## 九专家分视角发现

### 1. 项目管理专家

**发现：** R0-R4、DEC、墓园、状态同步已经让项目超出普通个人项目水平；但 `DEC-068` 的风险在于把“最小工作流验证通过”解释成“OS 正式冻结”。A-2 在同一阶段暴露机制方向相反，项目管理上应触发 scope exception。

**判定：**

| 维度 | 项目现实 | 外部审计判断 |
|---|---|---|
| 阶段治理 | R0-R4 已成形 | 流程可冻结 |
| 机会地图 | A-1/A-2 两主线仍沿 DEC-066 | 不可冻结 |
| WIP | A-1、TSMOM、采集器、OS治理并行 | 本周必须收窄 |
| 失败响应 | L3 已触发 | 但 A-2 死亡后的地图重排不够彻底 |

**改法：** 在下一次 Founder 决策中把 `DEC-068` 解释为：冻结协作 OS、文档纪律、直调流程；不冻结策略主线权重。新增一个 `OPPORTUNITY_MAP_STATUS`，把方向标成 `Baseline / Conditional / Dead / Quarantined`。

### 2. 量化产品设计专家

**发现：** 本项目的第一产品不是交易 bot，而是 Founder 每天 1 小时可理解的决策控制台。现在文档很多，但 Founder 面临的是“该不该花下一条命”的产品问题。

**改法：**

| 产品模块 | 当前 | 应改 |
|---|---|---|
| 机会地图 | 散在蓝图/L3/结果报告 | 一页状态机：TSMOM baseline、A-1 conditional、A-4 candidate、A-2 dead |
| Founder 日报 | BOOT_BRIEF 泛摘要 | 固定 5 行：今日是否需拍板、哪个命、为什么、风险、替代 |
| 资本表达 | 核心/围栏两层 | edge 证据等级解锁风险预算，不默认 25% |
| AI 系统定位 | AI 执行组织 | AI-native research OS，不是 AI trading alpha |

**审计结论：** 产品化重心应从“研究文档更全”转向“Founder 不被漂亮叙事误导”。

### 3. 系统/软件架构师

**发现：** 当前先研究后执行是正确的；但 A-1 所需数据粒度与现有数据不匹配。Binance 强平流适合前向监控，不等于完整历史强平 tape；OI 文献还提示部分交易所 OI/强平数据可能误报或延迟。

**改法：**

| 架构项 | P级 | 具体动作 |
|---|---:|---|
| A-1 数据门 | P0 | 先定义 1m/5m price、volume、OI delta、liquidation stream 的质量标签，再决定是否耗第 7 命 |
| 数据层 | P1 | CSV 可保留，但 R1 起建立 DuckDB/Parquet 元数据索引和 hash manifest |
| 研究 harness | P1 | 每次实验产出 `run_trace`：输入、命令、版本、数据 hash、禁区检查 |
| 执行层 | P2 | Phase 2 再考虑 Nautilus/Hummingbot/Freqtrade/Jesse 思路，不在 Phase 1 接交易权限 |

### 4. AI治理与安全专家

**发现：** Claude/Codex/低模型四层组织是合理的一人公司压缩组织形态，但尚未达到 AI-Native L3。当前最大风险是 AI 生成 alpha 幻觉、agent 越权、memory poisoning、prompt injection、低模型语义误改。

**改法：**

| 风险 | P级 | 具体动作 |
|---|---:|---|
| AI alpha 幻觉 | P0 | Research Protocol 增加 `AI_ALPHA_EVIDENCE`，按 P1-P6 填写 |
| Agent 越权 | P0 | 建 `AGENT_REGISTRY`：role、owner、allowed paths/tools、forbidden paths、status |
| 独立复核污染 | P1 | 复核任务必须用白名单 context pack，报告列读取文件 |
| 插件/MCP 风险 | P1 | 所有插件/MCP 登记数据外发、读写权限、用户确认风险；交易执行类禁装 |

**小红书替代来源吸收：** `The Alpha Illusion` 结论直接适用本项目：LLM 是 auditable information interface，不是最终 trading authority。GitHub 仓库当前公开 404，不能作为已审计代码证据。

### 5. 工作流与组织设计专家

**发现：** 三层/四层 AI 组织把 Founder 从执行中解放出来，这是对的；但审计与治理产出已经偏密。项目需要更少活跃工作流，而不是更多角色。

**本周 WIP 限制建议：**

1. `TSMOM 扩样本/更新数据/成本敏感性`：不耗命，作为 baseline。
2. `A-1 数据门/前向采集质量检查`：不耗命；通过后才预登记第 7 命。
3. 其他新方向只做资料卡，不进入实验。

**组织规则：** 低模型只能做：索引、横幅、逐字 payload、格式、表格补全。禁止它判断方向、改门槛、写结论。

### 6. 专业加密量化投研专家（主合约）

**发现一：A-2 是机制错误，不只是一个失败实验。** 永续合约的 funding 是锚定机制和持仓成本；极端 funding 可以对应趋势拥挤、逼空/逼多、风险偏好、套利约束，不自动对应反转。

**发现二：内部证据已经偏向动量/延续。** TSMOM 四件套过，A-2 三主窗口方向相反，二者合起来说明：本样本中 24-72h/4H 级别更像延续市场，而不是简单反转市场。

**发现三：A-1 必须两相位：**

| 相位 | 交易含义 | 数据要求 | 不合格替代 |
|---|---|---|---|
| 级联进行中 | 顺强制流延续 | 分钟级价格/成交/OI/强平 | 1H 收益代理 |
| 级联耗竭后 | 反弹/均值回归 | 强平密度衰减、深度恢复、停止创新低/高 | 事后窗口挑选 |

**机会地图重排：**

| 状态 | 方向 |
|---|---|
| Baseline candidate | TSMOM/regime continuation |
| Conditional candidate | A-1 forced-flow two-phase |
| Candidate | A-4 new listing/new perp |
| State / benchmark | funding/carry/OI |
| Dead | A-2 funding extreme reversal |

### 7. 数据工程专家

**发现：** 项目已纠正“数据截止 2025-12”的过时认知，A-2 也体现了较好的无前视纪律。但现状仍欠缺机器可检查的数据契约，尤其是 AI/agent 参与后，数据路径和时间戳必须更硬。

**改法：**

| 数据项 | P级 | 动作 |
|---|---:|---|
| `DATA/HOLDOUT` 禁区 | P0 | hook/lint 检查任何任务书和命令不得引用 |
| rolling/expanding 分位 | P1 | 单元测试确保每个事件只使用过去数据 |
| universe | P1 | 上市、下架、流动性、缺失处理写入数据字典 |
| XHS/x-reader | P2 | `x-reader` CLI 已装；XHS 需登录态；建议做 skill wrapper，不作为关键数据源 |

### 8. 风控专家

**发现：** 两层资本架构方向正确；但围栏子账户 25% 默认表达偏激。对 30k 本金，策略证据等级未达 R4 前，任何固定 25% 风险预算都是过早资金承诺。

**改法：**

| 风险 | P级 | 动作 |
|---|---:|---|
| 资金表达 | P0 | 围栏资金按证据等级解锁：paper-only=0，backtest=watch，walk-forward=小额，dry-run=更高 |
| 爆仓风险 | P0 | 杠杆只表达 edge，不制造 edge；2x 爆仓概率高的结论写入风险宪法 |
| 交易所风险 | P1 | 交易所/API key/提现/稳定币/托管风险单列，不混入策略 Sharpe |
| 成本 runway | P1 | `COST_LOG_2026.md` 仍需填 Claude/Codex/服务器明细 |

### 9. 决策科学 / 行为偏差专家

**发现：** 项目目前最大认知偏差是“治理完成感”和“主线沉没成本”。A-2 失败后，最容易出现的错误不是停项目，而是把 A-2 的相反证据转译成 A-1 的继续理由。

**偏差清单：**

| 偏差 | 迹象 | 反制 |
|---|---|---|
| 叙事黏性 | 两主线被蓝图认可后难以降权 | 状态机强制改为 Dead/Conditional |
| 行动偏差 | 剩 2 命诱导尽快实验 | 数据门不耗命，实验命需 Founder 显式批准 |
| AI 权威偏差 | Claude/Codex 输出越流畅越可信 | AI 输出只算假设，必须过 P1-P6 |
| 过程安慰 | OS 跑通带来安全感 | 流程成功与 alpha 成功分开打分 |

## P0 / P1 / P2 清单

### P0：危及目标函数/资金安全，立即改

| 编号 | 问题 | 改法 |
|---|---|---|
| P0-1 | `DEC-068` 冻结范围过宽 | 明确冻结 OS，不冻结机会地图；A-2 dead、A-1 conditional |
| P0-2 | AI-generated alpha 缺证据门 | Protocol 增加 `AI_ALPHA_EVIDENCE`，P1-P6 必填 |
| P0-3 | A-1 数据不足却可能耗第 7 命 | 建 A-1 数据门：分钟级数据、强平/OI 质量、两相位预登记 |
| P0-4 | TSMOM 未被升为 baseline | 机会地图新增 `Baseline candidate`，TSMOM 扩样本不耗命 |
| P0-5 | 围栏 25% 默认表达过激 | 改为证据等级解锁风险预算，未过 R4 不固定 25% |
| P0-6 | 低模型可触碰权威文件的语义风险 | 低模型只许逐字 payload/格式/索引；禁止结论与门槛 |

### P1：本阶段内显著优化

| 编号 | 问题 | 改法 |
|---|---|---|
| P1-1 | agent 治理未达到 AI-Native L3 | 建 `AGENT_REGISTRY` + `AGENT_RUN_TRACE_TEMPLATE` |
| P1-2 | 数据契约仍偏文档化 | 建数据 hash、schema、no-lookahead test、universe log |
| P1-3 | 外部 evidence grade 未制度化 | 每个机制卡必须列 A/B/C/D 证据与冲突项 |
| P1-4 | 成本台账细项未填 | Founder 填 Claude/Codex/服务器；月审自动引用 |
| P1-5 | 工具路由缺安装风险登记 | 插件/MCP/skill 清单列权限、外发、确认弹窗、禁用状态 |
| P1-6 | XHS 读取依赖登录态 | `x-reader` 建 skill wrapper；XHS 仅作 C 级辅助源 |
| P1-7 | 多 agent 复核可能共识幻觉 | 单 agent baseline、分歧率、反方隔离、读取路径披露 |

### P2：观察项 / Phase 2 评估

| 编号 | 观察项 | 建议 |
|---|---|---|
| P2-1 | Nautilus/Hummingbot/Freqtrade/Jesse | 只学架构和 lookahead/dry-run，不引实盘内核 |
| P2-2 | OpenBB/Notion/Drive 等外部工具 | 仅作研究 UI/归档，不接交易权限 |
| P2-3 | A2A/LangGraph/AutoGen | 先 harness，后 orchestration；Phase 2 再评估 |
| P2-4 | 情绪/社媒/LLM news | 仅作上游特征，不作端到端 agent |
| P2-5 | cross-exchange/stat-arb | 需运维和执行工程，非当前 1h/day 优先项 |

## 五处以上明确挑战项目现有共识

1. **挑战 `DEC-066`：两主线 A-1/A-2 被认可后仍按主线推进。**  
   替代：A-2 反转版入 Dead；A-1 降为 Conditional；TSMOM 升 Baseline；A-4 升 Candidate。

2. **挑战 `DEC-068`：OS 正式冻结的表述过宽。**  
   替代：只冻结操作系统和工作流，不冻结机会地图、证据等级、资金表达。

3. **挑战 `L3_EMERGENCY_2026-06-11` 中“无需暂停、A-1 优先”的节奏。**  
   替代：无需停项目，但必须暂停耗命实验；先做 A-1 数据门和 TSMOM baseline 扩样本。

4. **挑战 `PHASE1_RESEARCH_RISK_BLUEPRINT_v1` 的 A-2 持仓极端反向论断。**  
   替代：funding/OI 改为状态变量；方向由 trend/liquidity/liquidation phase 决定，不预设反转。

5. **挑战 `OPERATING_MODEL_DESIGN_v1` / 低模型章程中“低模型可批量改文档”的隐含乐观。**  
   替代：低模型只能做结构性、逐字、可 diff 的机械任务；权威语义文件只由 Claude/Codex 高层处理并审计。

6. **挑战 `PHASE1_TECH_ORG_GOVERNANCE_v1` 对 Codex 直调通道的充分性假设。**  
   替代：直调前必须有 agent registry、allowed path、forbidden path、run trace、禁读 Holdout lint。

7. **挑战 `RESEARCH_PROTOCOL_v1.3_ADDENDUM` 对 AI 生成 alpha 风险覆盖不足。**  
   替代：新增 `AI_ALPHA_EVIDENCE`；端到端 LLM 策略只允许称 prototype，不能称 deployable alpha。

8. **挑战两层资本中围栏 25% 默认表达。**  
   替代：证据等级解锁资金，未过 R4 不固定 25%，盈利回流核心，但亏损阈值更细。

## 剩 2 条独立实验命的花法建议

### 不耗命前置

| 动作 | 目的 |
|---|---|
| TSMOM 扩样本/更新数据/成本敏感性 | 建 baseline，不占新命 |
| A-1 数据门 | 判断是否具备级联研究资格 |
| A-4 数据可行性普查 | 给第 8 命准备独立机制 |
| AI Alpha Evidence Gate 落地 | 防 AI 策略幻觉消耗命 |

### 第 7 命

**只给 A-1，但必须改题：** `liquidation/forced-flow two-phase event study`。  
通过条件：分钟级价格/成交/OI/强平数据质量可描述；事件定义无前视；分清“级联进行中延续”和“级联耗竭后反弹”；成本压力档预登记。

若数据门不过：第 7 命不花，继续 TSMOM baseline 和 A-4 普查。

### 第 8 命

**暂存。** 默认候选：A-4 新上市/新永续错位；备选为与 funding/OI 叙事独立的新机制。禁止从 A-2 失败样本中事后抽象“延续版 A-2”直接开新命。

## 建议安装的工具 / skill / MCP / 插件清单

| 类型 | 名称 | 用途 | 风险 | 优先级 |
|---|---|---|---|---|
| Skill | `ai-alpha-evidence-gate` | P1-P6 检查 AI 生成策略 | 低 | P0 |
| Skill | `research-preregistration` | 预登记模板、耗命判断 | 低 | P0 |
| Skill | `agent-run-trace` | Codex/Claude/低模型执行 trace | 低 | P1 |
| Skill | `x-reader-wrapper` | 调用本机 `x-reader`，记录登录态/失败原因 | 中：平台登录/版权/风控 | P1 |
| Hook | `no-holdout-pretool` | 阻止读取 Holdout | 低 | P0 |
| Hook | `no-authority-low-tier` | 低模型禁改权威语义文件 | 低 | P0 |
| MCP | read-only data catalog | 暴露数据 schema/hash/目录，不暴露 Holdout | 中 | P1 |
| MCP | read-only cost/status | 暴露成本台账、运行状态 | 低 | P1 |
| MCP | docs/source index | 外部资料与证据等级索引 | 低 | P2 |
| 插件 | 不建议安装交易执行插件 | Phase 1 禁交易权限 | 高 | 禁 |

**x-reader 说明：** 本机已有 CLI：`/Library/Frameworks/Python.framework/Versions/3.13/bin/x-reader`。Codex 插件市场未发现精确 `x-reader` 插件；XHS 读取需要 `x-reader login xhs` 保存会话，本次登录超时。用户已提供替代链接，本审计采用 arXiv 论文与 GitHub 访问状态作为来源。

## 资料与调研吸收

| 报告 | 本审计吸收 |
|---|---|
| `AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12.md` | Skill/hook/只读 MCP 优先，不追求工具数量 |
| `PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12.md` | 学 Freqtrade lookahead、Qlib recorder、Nautilus event log、RD-Agent trace |
| `FRONTIER_AI_OPC_AGENT_GOVERNANCE_RESEARCH_2026-06-12.md` | AI-Native = agent-readable + eval + trace + permission |
| `AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12.md` | 机会地图重排、AI Alpha Evidence Gate、A-1 数据门 |
| `XHS_NOTE_SUBSTITUTE_ALPHA_ILLUSION_2026-06-12.md` | LLM reported alpha 不能当部署证据；代码仓库 404 降级 |

**关键外部来源：**

- `The Alpha Illusion`（B）：https://arxiv.org/abs/2605.16895
- `Fundamentals of Perpetual Futures`（B）：https://arxiv.org/abs/2212.06888
- `Reconciling Open Interest with Traded Volume in Perpetual Swaps`（A/B）：https://arxiv.org/abs/2310.14973
- BIS `Crypto carry`（A/B）：https://www.bis.org/publ/work1087.pdf
- `Risk Premia in the Bitcoin Market`（B）：https://arxiv.org/abs/2410.15195
- Freqtrade lookahead analysis（A/B）：https://docs.freqtrade.io/en/stable/lookahead-analysis/
- NautilusTrader overview（A/B）：https://nautilustrader.io/docs/latest/concepts/overview/
- Qlib introduction（A/B）：https://qlib.readthedocs.io/en/latest/introduction/introduction.html
- NIST AI RMF（A）：https://airc.nist.gov/airmf-resources/airmf/
- OWASP LLM / Agentic AI（A）：https://owasp.org/www-project-top-10-for-large-language-model-applications/ 、https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- OpenAI Agents/Codex docs（A）：https://developers.openai.com/
- Claude Code memory/hooks/skills/subagents docs（A）：https://docs.anthropic.com/en/docs/claude-code/

## 附录A：零锚定预期

以下为只读 `CLAUDE.md` 与 `COMPANY_STRATEGY_PRODUCT_v1.md` 后、读取其他材料前形成的外部预期；本节保留用于防锚定对比。

### A1. 项目管理专家

从零设计，我会把公司拆成四个 stage：研究 OS、候选机制、最小策略、实盘前风控。每个 stage 有明确 kill criteria、资源预算、Founder 拍板点。剩余资金小、时间少，因此默认 WIP=1，最多 2。

### A2. 量化产品设计专家

产品不是“自动交易机器人”，而是“小资金 founder 的证据控制台”。第一屏应回答：现在有哪些候选 edge、证据等级、风险预算、下一步是否消耗实验命。

### A3. 系统/软件架构师

先建研究数据契约和可复现 harness，再建执行系统。Phase 1 不接交易权限；所有数据、实验、报告要有 hash、版本、输入输出和无前视检查。

### A4. AI治理与安全专家

AI agent 必须有身份、权限、禁区、trace、owner、生命周期。Claude/Codex/低模型都不能直接触达 Holdout 或交易权限；AI 生成策略只能算假设。

### A5. 工作流与组织设计专家

Founder 只做最终 D 级决策；Claude 做 CEO/CTO；Codex 做工程实现；低模型做机械任务；Risk Reviewer 独立反审。所有 handoff 都用 context pack，而不是长聊天。

### A6. 专业加密量化投研专家

我会优先找小资金可表达、容量小但机制强的方向：趋势延续/regime、强制流、上市/结构变化、carry/basis。反转只在明确耗竭机制和微观数据支持后测试。

### A7. 数据工程专家

先盘点可得数据、时间戳、粒度、缺失、延迟和授权；再定策略。加密永续至少需要 price、volume、funding、OI、liquidation、交易规则、上市/下架元数据。

### A8. 风控专家

30k 本金下，第一原则是活下来。核心资本不碰高杠杆；围栏资金按证据等级解锁；任何策略先算爆仓路径、交易所风险、滑点、funding、尾部相关性。

### A9. 决策科学/行为偏差专家

默认假设团队会被漂亮回测、AI 叙事、沉没成本和“差一点就成”诱惑。必须用预登记、墓园、反方审计、耗命闸门来阻止自我说服。

### A10. 零锚定预期 vs 项目现实

| 差异 | 判定 |
|---|---|
| 项目文档治理比预期成熟 | 项目做对了，应保留 |
| 机会地图比预期更偏 funding/OI 反转 | 项目需修正 |
| AI 组织比预期丰富 | 方向对，但治理需机器化 |
| TSMOM 内部证据强于我初始预期 | 外部预期需更新，TSMOM 应升 baseline |
| 成本 runway 好于预期 | 项目健康，但细项要填 |
| A-1 数据要求高于项目当前支撑 | 项目需先数据门，不应直接耗命 |
