# REPORT_V5_DESIGN_EXTRACTION_POST_0510

**任务：** 从 `conversations_timeline.md` 中提炼 2026-05-10 之后的 V5 设计方案  
**执行人：** Codex  
**日期：** 2026-06-13  
**输入文件：** [conversations_timeline.md](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md)  
**范围：** 仅提炼 ChatGPT 导出文件中 2026-05-10 之后的 V5/AI Quant Company 相关内容；当前项目正式口径仍以 `01_MEMORY_CORE` / `00_PROJECT_MANAGEMENT` / `05_TECH_DESIGN` 的权威文件为准。

---

## 0. 执行口径

这份提炼采用 **时间优先级**：

1. 同一主题后续版本默认覆盖前序版本。
2. 早期版本只作为来源证据，不与后期版本平权混合。
3. 2026-05-20 之后关于 Claude/Codex 分工、PMO、Project OS、知识库、工作流的内容，权重大于 2026-05-10 当天的初始蓝图。
4. `conversations_timeline.md` 的文件顺序不完全等于时间顺序，已按消息时间戳重新判断。该导出中最新 V5 相关内容到 2026-05-24。

**重要结论：** 5月10日之后，“V5”的含义发生了迁移：

- 早期 V5：从 V4.6.2 冻结后启动的 **单 Setup / 结构事件研究分支**。
- 后期 V5：升级为 **AI Quant Company / AI-Native Research OS / 一人公司 + AI Team 的项目操作系统**。

因此，不能把 “SMC 单 setup 策略方案” 和 “AI Quant Company 组织/系统蓝图”混成一个同等层级的最终方案。后者是更新、更高层的设计。

---

## 1. 版本演化时间线

| 时间 | 版本焦点 | 后续状态 |
|---|---|---|
| 2026-05-10 13:23 | V4.6.2 冻结为 Baseline，V5 作为独立 Research Branch，重写 Position/Risk/Entry/Exit 核心模块 | 保留为历史起点 |
| 2026-05-10 13:23-14:03 | V5 从 22 分制转向 Structure Event / 单 Setup 验证，强调 Event Engine、Setup Engine、Replay、Lifecycle | 策略层早期蓝图，后续被降级为研究候选 |
| 2026-05-10 14:19-14:35 | 识别“多 AI 聊天接力”是信息同步灾难，提出 AI Copilot Quant System 和 Control Plane | 保留为架构核心 |
| 2026-05-11 | 最终形态定义为 AI-assisted Quant Trading OS；OpenClaw/Hermes 从核心降级为可替换插件/工具 | 保留，后续继续强化 |
| 2026-05-13 | V5 Phase 0 被定义为 Research OS Foundation，不先做交易系统 | 保留，成为 Phase 0 主线 |
| 2026-05-14 | 从“交易系统”转为“一人 AI Quant Company”；区分研发 Agent Team 与交易系统内自治 Agent | 保留，成为组织架构主线 |
| 2026-05-19 | Agent 编排不引入额外框架；当前用 Codex Desktop 原生能力即可 | 保留，避免过度工程 |
| 2026-05-20 | 明确 Claude 主脑 / Codex 执行 / 自动验证 / Claude 关键节点 Review | 覆盖此前“Codex 主脑”倾向 |
| 2026-05-21 | 建立 PMO、Project OS、Raw Inbox、知识提取流水线、Obsidian、成本监控、反迎合治理 | 当前导出内最完整的工程治理蓝图 |
| 2026-05-24 | 引入 Founder's Playbook 的“Founder 从执行者变编排者”；Codex `/goal` 用作长期任务合同 | 当前导出内最后增量 |

关键证据：V4 冻结/V5 Research Branch 见 [conversations_timeline.md:99215](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:99215)，单 Setup 见 [conversations_timeline.md:99219](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:99219)，Research OS Phase 0 见 [conversations_timeline.md:107804](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:107804)，Claude/Codex 最终分工见 [conversations_timeline.md:117874](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:117874) 与 [conversations_timeline.md:118291](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:118291)。

---

## 2. 最终版 V5 定义

按 2026-05-20 之后的版本折叠，V5 不应定义为“一个自动交易脚本”或“一个 OpenClaw/Hermes Agent 系统”，而应定义为：

> **AI Quant Company：一套 AI-native Quant Research Operating System。**

它的目标不是立刻实盘赚钱，而是建立一个能长期稳定地产生、验证、归档、审查交易假设的研究公司操作系统。交易系统是后续产出，不是 Phase 0 的主体。

最终形态：

```text
Founder（目标 / 风险 / D级决策）
    ↓
Claude（AI CTO：规划 / 架构 / 研究判断 / 关键Review）
    ↓
PMO / Project OS（项目治理 / 状态 / 任务 / 成本 / 决策）
    ↓
Codex（AI Engineer Team：执行 / 自动化 / 代码 / 文档维护）
    ↓
自动验证层（Tests / Lint / Backtest / 数据校验 / 风控检查）
    ↓
Research Platform（数据 / 因子 / 回测 / Walk-forward / 报告）
    ↓
Deterministic Execution System（信号 / 风控 / 执行 / 对账 / 监控）
```

这一版覆盖了早期“Codex 做主脑”的倾向。最新口径是：

- **Claude 做大脑**：负责方向、规则、架构、规划、研究判断、关键节点 Review。
- **Codex 做双手**：负责创建目录、写代码、跑脚本、整理文件、自动化执行、生成报告。
- **程序做验证**：Claude Review 不能替代测试、回测、数据校验、风控检查。
- **Founder 做最终 D 级决策**：不再做人肉消息总线。

证据：Claude/Codex 职责划分见 [conversations_timeline.md:117874](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:117874)，Claude > Codex 主脑判断见 [conversations_timeline.md:118291](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:118291)。

---

## 3. 公司/组织架构

2026-05-21 之后的更优版本是按组织职能拆，而不是按技术模块拆：

```text
Founder（CEO + PM + 最终决策）
    ↓
Claude（AI CTO / 主脑）

1. 公司管理中心（Management / PMO）
   - 项目规划
   - 决策记录
   - 文档体系
   - 知识库
   - 每日计划 / 周计划
   - 成本监控
   - 项目看板

2. 产品研发中心（Product & Engineering）
   - 产品设计
   - 架构设计
   - 技术选型
   - API 设计
   - 开发 / 测试 / 运维

3. 投研中心（Research）
   - 数据处理
   - 因子研究
   - 策略研究
   - 回测验证
   - 风险研究

4. 执行运营中心（Execution & Operations）
   - 行情扫描
   - 信号生成
   - 风控
   - 下单
   - 通知
   - 监控
```

当前阶段只应真正启动两个部门：

1. **公司管理中心 / PMO**：解决“项目会不会失控”。
2. **产品研发中心**：解决“未来系统怎么设计和落地”。

投研和执行运营不应在 Phase 0 抢跑。

证据：组织职能拆分见 [conversations_timeline.md:120829](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:120829)，上帝视角组织图见 [conversations_timeline.md:121063](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:121063)，PMO 独立层修正见 [conversations_timeline.md:124786](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:124786)。

---

## 4. 技术系统架构

早期 V5 有一个较重的 Control Plane 设想，但后续被收敛为“先 Project OS，再 Research，再 Execution”。最终技术视角应为：

```text
User / Founder
    ↓
Claude 主脑
    ↓
Control Plane / PMO
    ├── Task Scheduler
    ├── State Store
    ├── Event Bus
    ├── Governance
    ├── Memory
    └── Cost / Decision / Roadmap

Research Layer
    ├── 数据
    ├── 因子
    ├── 回测
    ├── Walk-forward
    └── 验证报告

Execution Layer
    ├── 信号
    ├── Decision Gateway
    ├── Risk Engine
    ├── Order Execution
    ├── Reconciliation
    └── Notification

Knowledge Layer
    ├── 文档
    ├── 决策
    ├── 项目上下文
    ├── 学习记录
    └── 历史档案
```

其中执行层必须是确定性系统，不是 AI 自治系统：

- AI 可做研究、分析、代码生成、日志解释、复盘、候选方案排序。
- AI 不应进入实时交易闭环。
- 真实下单、仓位、熔断、风控必须由可审计程序控制。
- OpenClaw/Hermes 不再是系统本体，只能作为参考工具、插件、外部执行/编排能力候选。

证据：AI Copilot Quant System 见 [conversations_timeline.md:101054](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:101054)，AI 不在交易闭环见 [conversations_timeline.md:101131](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:101131)，AI-assisted Quant Trading OS 见 [conversations_timeline.md:103289](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:103289)，OpenClaw 作为可替换插件的判断见 [conversations_timeline.md:105051](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:105051)。

---

## 5. Phase 路线图

按 2026-05-21/05-24 的后续版本，阶段划分应采用：

| 阶段 | 名称 | 目标 | 退出条件示例 |
|---|---|---|---|
| Phase 0 | Project OS / 基础建设 | 建目录、文档、规则、Inbox、PMO、成本、AI治理 | 目录、`CLAUDE.md`/`AGENTS.md`、`CURRENT_STATE`、`DECISION_LOG`、Inbox、项目看板完成 |
| Phase 1 | AI Team 建设 | Claude 主脑、Codex 执行、任务模板、Review 机制 | Claude→Codex 文件式交接跑通，自动验证/日报/周报有模板 |
| Phase 2 | Research Platform | 数据层、因子层、回测层、验证层 | 一个研究任务可从假设到报告闭环 |
| Phase 3 | Trading Execution System | 确定性执行内核、风控、通知、对账 | 模拟环境可跑完整信号→风控→执行→日志 |
| Phase 4 | 模拟盘验证 | Paper trading、运行稳定性、日报复盘 | 连续运行无状态漂移，风险/日志/对账可审计 |
| Phase 5 | 小资金实盘 | 小资金、硬风控、人工 D 级确认 | 通过实盘风险试运行，不扩大权限 |
| Phase 6 | 自动化扩展 | 更多 Agent、更多策略、更多自动化 | 仅在前面闭环稳定后扩展 |

当前导出里的最终动作建议仍是：**先做 Phase 0，不写交易系统，不研究策略，不上 OpenClaw/Hermes，不引入复杂编排框架。**

证据：阶段路线图见 [conversations_timeline.md:121063](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:121063)，Founder's Playbook 改造后的阶段制见 [conversations_timeline.md:127584](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:127584)。

---

## 6. 知识库与上下文管理

这是 5月20日之后最重要的更新之一。

最终口径不是“把所有历史资料喂给 Claude”，而是：

```text
Raw Archive / Inbox
    ↓
知识提取
    ↓
去重
    ↓
冲突检测
    ↓
决策抽取
    ↓
当前状态提取
    ↓
主脑上下文
```

规则：

1. 所有历史资料都可以进入 Inbox。
2. 只有提炼后的事实、决策、当前状态进入 Claude 主脑上下文。
3. V4 文档只能作为历史参考，不能直接继承。
4. 旧方案必须标注 Deprecated / Superseded / Active / Pending。
5. 主脑长期读取的应该是少量核心文件，而不是几千页聊天记录。

推荐结构（历史版本中的方向，当前仓库已调整为实际目录）：

```text
00_PROJECT_MANAGEMENT
01_MEMORY_CORE / 或 PROJECT_CONTEXT
03_RAW_INBOX / 99_INBOX
04_AI_TEAM
06_KNOWLEDGE_BASE / REFERENCE
07_COST_TRACKING
```

Obsidian 的定位：

- 不是第二个项目。
- 是本地 Markdown 知识管理系统。
- 适合承载 `CURRENT_STATE`、`DECISION_LOG`、`ROADMAP`、`SYSTEM_ARCHITECTURE`、`LESSONS_LEARNED`。
- 只先用基础能力，不要先折腾大量插件。

证据：历史资料分层见 [conversations_timeline.md:117414](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:117414)，Inbox vs Claude 主脑见 [conversations_timeline.md:119956](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:119956)，半自动知识流水线见 [conversations_timeline.md:120160](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:120160)，Obsidian 使用建议见 [conversations_timeline.md:120461](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:120461)。

---

## 7. AI Agent Team 与工具编排

### 7.1 正确区分两类 Agent

后续版本明确区分：

- **危险层：交易系统内自治 Agent**  
  AI 自动决定、自动下单、自动改风控、自动改仓位。当前阶段禁止。

- **合理层：研发协作 Agent**  
  架构 Agent、文档 Agent、代码 Agent、Review Agent、测试 Agent、研究 Agent。可以轻量化使用，但必须受 Claude 主脑统一调度。

证据：两类 Agent 区分见 [conversations_timeline.md:108842](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:108842)。

### 7.2 当前不引入重型编排框架

2026-05-19 的后续版本覆盖了早期对 OpenClaw/Hermes/多 Agent 编排的兴趣：

- 当前阶段 Codex Desktop 自带能力够用。
- 不需要 LangGraph / AutoGen / CrewAI / OpenClaw / Hermes 做 Agent 编排。
- 真正缺的是 Project OS 和治理，不是更多 Agent 框架。
- 后续如果需要复杂 DAG、多系统自治协同、大规模工具路由，再评估编排框架。

证据：开发/上线阶段 Agent 编排建议见 [conversations_timeline.md:115897](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:115897)，Codex Desktop 已够用见 [conversations_timeline.md:116478](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:116478)。

### 7.3 Claude/Codex 配置体系

社区整理的 `CLAUDE.md / AGENTS.md / skills / hooks / subagents / plugins` 五层模型被后续版本重新定位：

- 这是 **AI 研发团队内部工作手册 + 工具箱**，不是整个 V5 系统。
- 当前先做 `CLAUDE.md` / `AGENTS.md` / 项目规则 / 工作流。
- `skills`、`hooks`、`subagents`、`plugins` 放到后续阶段。

证据：Claude/Codex 五层架构映射见 [conversations_timeline.md:126262](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:126262)。

---

## 8. 交易系统与风控原则

虽然 Phase 0 不做交易系统，但后续交易系统有几条不可变骨架来自 5月10日之后的多轮收敛：

1. **AI 不进实时交易路径**：AI 只做研究和分析。
2. **策略层只产出信号**：不得直接下单。
3. **Decision Gateway 唯一裁决**：所有信号必须过硬风控。
4. **PostgreSQL / 权威状态源**：内存字典只能是缓存，不能是风控依据。
5. **Reconciliation 必须有**：交易所 / DB / runtime 状态必须对账。
6. **Position Journal / Event Sourcing**：交易生命周期要可追溯。
7. **Risk Timestamp**：每个 position 必须知道最近一次风险检查时间。
8. **自动验证优先于模型 Review**：Claude 不能替代测试和回测。

证据：Reconciliation / Position Journal / Risk Timestamp 见 [conversations_timeline.md:100427](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:100427)，Event Sourcing / CQRS 见 [conversations_timeline.md:100655](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:100655)，AI 权限边界见 [conversations_timeline.md:106216](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:106216)。

---

## 9. 研究策略方向的处理

早期 V5 策略蓝图是：

```text
BTC only
4H bullish regime
15m liquidity sweep + CHoCH + FVG retrace
structure stop
RR >= 2
时间止损
```

并配套 Event Engine、Setup Engine、Replay Engine、Trade Lifecycle Engine、Research Dataset。

但按时间优先级，这不应作为当前最终 V5 主体，而应降级为：

- **历史上的第一个单 Setup 实验候选**
- 或 **V5 Research Layer 的一个早期研究方向**

它不应覆盖 5月20日之后的主线：先建立 Project OS / AI Quant Company / Research Protocol / 研究基础设施，再进入具体策略研究。

此外，当前工作区已有 2026-06-13 的后续项目蓝图，已将 V5 历史 SMC/FVG/BOS 方向标为不采用的历史路径，见 [PHASE2_SYSTEM_BLUEPRINT.md:196](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md:196)。因此本报告不把早期 SMC 方案提升为当前策略路线。

早期策略证据：V5 第一阶段模块见 [conversations_timeline.md:92873](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:92873)，单 Setup 见 [conversations_timeline.md:93014](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:93014) 与 [conversations_timeline.md:99219](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:99219)。

---

## 10. 需要明确废弃或降级的旧内容

| 内容 | 处理 | 原因 |
|---|---|---|
| V4.6.2 继续 patch | 废弃 | V4 已冻结为 Baseline，V5 是独立 Research/Company OS |
| 22 分制评分继续扩展 | 废弃/仅基线 | IC 和准确率不足，且属于规则堆叠 |
| OpenClaw 作为系统核心 | 废弃 | 它是工具/插件候选，不是交易系统本体 |
| Hermes / RL 进入实时路径 | 废弃 | Alpha 未稳定前 RL 只会学噪声；实时 AI 风控不可审计 |
| 多 Agent 自治交易 | 禁止 | 状态漂移、幻觉、不可审计 |
| 所有历史资料直接喂 Claude | 禁止 | 会污染主脑上下文 |
| 自建复杂知识系统/RAG | 当前不做 | 会让 Project OS 变成新项目，拖慢主线 |
| 重型 Agent 编排框架 | 当前不做 | Codex Desktop + 文件式 handoff 已够用 |
| 用 `/goal` 做“赚钱/找圣杯” | 禁止 | 完成条件不可验证 |

---

## 11. 当前最优执行顺序

按 5月21日之后版本，当前应该执行：

1. 建/确认项目根目录和权威目录。
2. 建 PMO / Project OS：`CURRENT_STATE`、`DECISION_LOG`、`ROADMAP`、`DOCUMENT_INDEX`、任务看板。
3. 建 AI 规则：`CLAUDE.md`、`AGENTS.md`、AI 反迎合规则、Review Protocol。
4. 建 Inbox：所有历史资料进入 Raw Archive，不直接进入主脑。
5. 建知识提取流程：分类、去重、过期判断、冲突检测、决策抽取。
6. 建日报/周报/次日计划机制。
7. 建成本监控：AI token、软件订阅、服务器、代理、未来交易成本。
8. Claude 做规划/架构/关键 Review；Codex 做目录、文件、脚本、模板、自动化。
9. 使用 Codex `/goal` 做有清晰完成条件的长任务，如项目基础设施、Inbox 整理、工程模块开发；禁止用于模糊投研和交易决策。

证据：Project Bootstrap 见 [conversations_timeline.md:116967](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:116967)，工作计划/日报机制见 [conversations_timeline.md:118809](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:118809)，成本和反迎合治理见 [conversations_timeline.md:122104](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:122104)，Codex `/goal` 使用规范见 [conversations_timeline.md:128049](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/03_RAW_INBOX/CHATGPT_EXPORT/conversations_timeline.md:128049)。

---

## 12. 与当前仓库状态的对齐

当前仓库已经不是 5月下旬的 Phase 0 状态。`CURRENT_STATE.md` 显示项目已进入 Phase 1（找真实 edge），公司 OS 原则层已冻结，Codex 直调、低模型执行层、强平采集器等也已有后续进展，见 [CURRENT_STATE.md:10](/Users/yaomingyu/Documents/AI_QUANT_COMPANY/01_MEMORY_CORE/CURRENT_STATE.md:10)。

因此本报告的正确用途是：

- 回溯 V5 设计思想的演化来源；
- 识别哪些设计是历史上被后续吸收的；
- 防止把早期策略蓝图误当成当前权威；
- 为后续 Memory Core / Architecture 文档做溯源材料。

本报告不替代：

- `01_MEMORY_CORE/CURRENT_STATE.md`
- `01_MEMORY_CORE/DECISION_LOG.md`
- `00_PROJECT_MANAGEMENT/CONSTITUTION.md`
- `05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md`

---

## 13. 验收自检

| 项目 | 结果 |
|---|---|
| 是否重点覆盖 2026-05-10 之后 | 是 |
| 是否按时间优先级处理版本更新 | 是 |
| 是否区分早期策略 V5 与后期公司/Research OS V5 | 是 |
| 是否把后续版本覆盖前序版本 | 是 |
| 是否避免把 V4/V5 旧技术债直接继承 | 是 |
| 是否触碰 Holdout | 否 |
| 是否修改预登记文档 | 否 |
| 是否输出到 CODEX_TASKS | 是 |

**Codex 判断：** 导出文件中 5月10日后的最终 V5 蓝图，核心不是某个具体交易策略，而是“Claude 主脑 + Codex 执行 + Project OS/PMO + Research Protocol + 确定性交易执行层”的 AI Quant Company 操作系统。早期的 SMC 单 setup 是历史研究候选，不是最终主线。
