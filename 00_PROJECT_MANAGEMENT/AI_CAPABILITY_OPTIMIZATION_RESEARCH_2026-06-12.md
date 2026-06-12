# Codex / Claude 能力优化调研（上下文、记忆、文件结构、插件、Skill、MCP）

**日期：** 2026-06-12  
**定位：** 承接 `AI_CAPABILITY_TOOLING_AUDIT_v1.md` 与 `OS_TUNING_PLAN_v1.md` 的升级调研。  
**结论口径：** 以本项目“小资金、Founder 1h/天、月预算约1000、研究期严禁过度系统化”为约束。  
**资料来源：** OpenAI Codex customization / plugin docs，Claude Code memory / skills / subagents / MCP / hooks docs，MCP 官方架构文档，项目现有 OS 文件。Codex manual helper 本次因官方站点 HEAD 403 未成功，已用 OpenAI 官方网页文档 fallback。

## 结论摘要

1. **最优路线不是装更多工具，而是把当前流程产品化为项目级 Skill + 少量只读 MCP + 钩子护栏。**
2. `CLAUDE.md`/`AGENTS.md` 应继续保持“小而硬”，反复流程移出到 Skill，长参考移出到 Context Pack 或 reference 文件。
3. Claude 与 Codex 的能力边界应统一成四层：判断层 Claude、复杂实现 Codex、机械执行低模型、外部系统只读 MCP。
4. MCP 只应连接“外部系统/结构化数据/共享状态”，不应当成通用记忆库；交易执行类 MCP 在 Phase 1 禁装。
5. 项目最值得立刻自研的不是 agent 框架，而是 8 个项目技能：预登记、证据分级、数据契约、Codex 任务书、独立复核、结果 intake、state-sync、成本 runway。
6. 插件化应晚于 Skill 成熟。先在 repo 内 `.claude/skills/` 或 `$CODEX_HOME/skills` 迭代，等流程稳定后打包成 `ai-quant-os` 插件。
7. 记忆工程正确方向是“权威文件 + 派生摘要 + 墓园 + 索引”，外部云记忆/Mem0/Graphiti 类方案不适合当前资金安全要求。
8. 需要新增机器可检查护栏：禁止读 Holdout、禁止低模型语义改权威文件、禁止全样本分位、禁止未列 evidence grade 的外部引用。

## 外部能力要点

### Codex 官方能力映射

OpenAI Codex 文档把 durable instruction surfaces 分成互补层：`AGENTS.md` 约束项目行为，memories 承接历史上下文，skills 封装可复用工作流，MCP 连接外部系统，subagents 做专门分工。官方建议先建 `AGENTS.md`，再用 plugin/skill，再接 MCP，最后才上 subagents；这与本项目“先纪律，后编排”的原则一致。来源：[Codex customization](https://developers.openai.com/codex/concepts/customization)。

官方对 Skill 的定位很贴合本项目：可复用流程、团队专业知识、需要脚本/模板/参考文件的步骤；它采用 progressive disclosure，先暴露元数据，只有命中时才加载 `SKILL.md` 和引用材料，能降低上下文成本。来源：[Codex skills](https://developers.openai.com/codex/concepts/customization#skills)。

插件是分发单位，不是第一天就该上的抽象。Codex plugin 结构要求 `.codex-plugin/plugin.json`，可包含 `skills/`、`hooks/`、`.mcp.json`、`.app.json` 和 assets；适合把成熟的项目能力打包给多个工作区复用。来源：[Codex build plugins](https://developers.openai.com/codex/plugins/build)。

### Claude Code 官方能力映射

Claude Code 记忆文档明确区分 `CLAUDE.md` 与 auto memory：`CLAUDE.md` 是人为写入的持久规则，auto memory 是模型根据纠正沉淀的学习；两者都是上下文，不是硬 enforcement。若要硬阻止动作，应使用 hook。官方还建议单个 `CLAUDE.md` 控制在约 200 行以内，程序性流程移入 skill 或 path-scoped rules。来源：[Claude Code memory](https://docs.anthropic.com/en/docs/claude-code/memory)。

Claude Skill 的关键价值是“长程序不常驻上下文”：当你不断粘贴同一套 checklist/流程时，应创建 skill；skill body 只有被调用时才加载，支持支持文件、动态上下文注入、subagent fork、allowed/disallowed tools。来源：[Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills)。

Claude subagents 适合把会淹没主上下文的搜索、日志、文件读取放到独立窗口，只返回摘要；项目级 subagent 可放 `.claude/agents/` 并随 repo 版本化。来源：[Claude Code subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)。

Claude MCP 支持 local/project/user/plugin 多作用域；project scope 会写入项目根 `.mcp.json` 并可随版本控制共享。官方也强调外部内容可能带 prompt injection 风险，必须信任服务器。来源：[Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)。

Claude hooks 的 `PreToolUse` 可在工具调用前 allow/deny/ask/defer 或改写输入；适合把“禁止读 Holdout、禁止 destructive command、禁止写权威文件”等从软规则变成硬护栏。来源：[Claude Code hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)。

### MCP 官方能力边界

MCP 是 host/client/server 架构；server 可暴露三类核心 primitive：Tools（动作）、Resources（上下文数据）、Prompts（可复用模板）。它适合做结构化外部上下文和受控动作，不适合替代研究协议或决策判断。来源：[MCP architecture](https://modelcontextprotocol.io/docs/concepts/architecture)。

## 对本项目的能力架构建议

### 目标架构

```text
Founder
  只批 D 级：钱/阶段/范围/重大方向

Claude 主会话
  判断、研究主张、风控、验收、状态同步
  读取：BOOT_BRIEF + 当前任务 Context Pack

Codex
  复杂实现、测试、复现、报告
  读取：AGENTS.md + 任务书 + 必要数据路径

低模型执行层
  机械搬运、索引、横幅、格式化
  禁止：语义判断、改研究结论、改 DEC 正文

只读 MCP / 数据工具
  数据目录查询、DuckDB/Parquet 查询、GitHub/Docs 查询
  禁止：交易执行、Holdout 暴露、密钥写入
```

### 上下文工程

| 层 | 放什么 | 不放什么 | 推荐动作 |
|---|---|---|---|
| `CLAUDE.md` | 宪法级角色、D级边界、启动协议、研究铁律 | 具体实验流程、长表、历史记录 | 控制在 200 行左右；流程迁到 skills |
| `AGENTS.md` | Codex 执行约束、禁止项、交付物格式、测试命令 | Claude 的经营判断、历史叙事 | 将 `AGENTS_DRAFT.md` 升为根目录实装，并记录 hash |
| `BOOT_BRIEF.md` | 2 屏以内当前态、下一步、风险闸 | 详细时间线 | 预算 60 行；超限自动触发瘦身 |
| Context Pack | Risk Reviewer / Independent Review 的允许读路径、禁读路径、任务定义 | 全项目背景 | 每个 Pack 增加“允许读取白名单” |
| Skill | 可复用流程与 checklist | 项目永久规则 | 预登记、结果 intake、证据分级等 |
| MCP Resource | 数据 schema、数据目录、报告索引、成本台账摘要 | 原始 Holdout、密钥、交易权限 | 只读化，按资源分级 |

### 记忆工程

当前“文件式单一权威”是对的，应继续强化，而不是外接云记忆。

**建议分层：**

| 记忆类型 | 文件/系统 | 维护方式 |
|---|---|---|
| 决策记忆 | `DECISION_LOG.md` | 只写 Founder 确认；头部索引强制同步 |
| 运行记忆 | `CURRENT_STATE.md` | 只留活状态；历史归档 |
| 冷启动记忆 | `BOOT_BRIEF.md` | 派生摘要，不作权威 |
| 失败记忆 | `06_RESEARCH/GRAVEYARD_INDEX.md` | 新假设前必查 |
| 能力记忆 | `TOOL_ROUTING.md` / skills | 只写可复用流程 |
| 数据记忆 | `data_inventory` + hash manifest | 每次实验报告引用 |

**新增检查：**

1. `state_check.py` 增加“最新活动日期不得晚于 BOOT_BRIEF 顶部更新时间”。
2. 增加“DECISION_LOG 新 DEC 后索引必须同步”检查。
3. 增加“报告引用外部来源必须标 evidence grade”检查。
4. 增加“任何任务书不得出现 `DATA/HOLDOUT` 作为输入路径”检查。

### 文件结构治理

现有目录大体合理，但 00 与 01 容易变成“文档沼泽”。建议只做轻量重排，不大迁移：

```text
00_PROJECT_MANAGEMENT/
  INDEX.md                         # 一页权威地图
  COMPANY_STRATEGY_PRODUCT_v1.md
  OPERATING_MODEL_DESIGN_v1.md
  PHASE1_RESEARCH_RISK_BLUEPRINT_v1.md
  PHASE1_TECH_ORG_GOVERNANCE_v1.md
  TOOL_ROUTING.md
  CAPABILITY_RESEARCH/              # 后续能力调研归档，可选
  STAGE_AUDITS/

01_MEMORY_CORE/
  BOOT_BRIEF.md
  CURRENT_STATE.md
  DECISION_LOG.md
  STATE_SYNC_CHECKLIST.md
  ARCHIVE/                          # 历史运行快照

04_AI_TEAM/
  CODEX_TASKS/
  CONTEXT_PACKS/
  LOW_TIER_TASKS/
  SKILL_SPECS/                       # 项目 skill 草案

06_RESEARCH/
  HYPOTHESES/
  RESULTS/
  CODE/
  DATA/
  DATA_CATALOG/                      # schema/hash/manifest
```

不要现在把所有旧文档搬来搬去；先加 `INDEX.md` 与降级横幅，等月度 consolidate-memory 再归档。

## 推荐自研 Skill 清单

| Skill | 触发 | 输入 | 输出 | 风险控制 |
|---|---|---|---|---|
| `aiq-preregister` | 新机制/策略预登记 | 机制命题、数据路径、样本口径 | 标准预登记文档 | 强制失效条件、MDE、evidence grade |
| `aiq-evidence-grade` | 引用外部材料 | URL/文献/博客 | A/B/C 证据表 | C 级不得单独支撑主线 |
| `aiq-codex-task-spec` | 给 Codex 发包 | 目标、路径、禁止项 | Codex 任务书 | 自动插入 Holdout 禁止、验收标准 |
| `aiq-result-intake` | Codex 报告回收 | REPORT + RESULTS | 验收意见、失败计数建议 | 不自动写 DEC，只给建议 |
| `aiq-state-sync` | 状态变化后 | 变更摘要 | 更新清单和检查命令 | 先 diff，后写入 |
| `aiq-data-contract` | R1/R2 数据任务 | 数据路径 | schema/hash/缺口报告 | 检查 UTC、排序、滚动分位 |
| `aiq-independent-review` | 独立复核 | 预登记 + 原始数据白名单 | 复核报告模板 | 禁读提案结果/中间 CSV |
| `aiq-cost-runway` | 月审/大任务前 | 成本台账、计划调用 | runway 摘要 | 只读，不触发资金动作 |

**先做顺序：** `aiq-codex-task-spec` → `aiq-result-intake` → `aiq-data-contract` → `aiq-evidence-grade`。  
原因：它们直接防 A-2 这类“证据等级不足 + 内部证据未对撞”的损失。

## Plugin 路线

不要立刻插件化。先让 Skill 在项目内跑 2-3 轮，稳定后再打包。

**未来插件名建议：** `ai-quant-os`

```text
ai-quant-os/
  .codex-plugin/
    plugin.json
  skills/
    preregister/
    evidence-grade/
    codex-task-spec/
    result-intake/
    data-contract/
    state-sync/
  hooks/
    hooks.json
  .mcp.json
  assets/
```

插件化的唯一理由：让同一套研究 OS 在 Claude/Codex/未来新项目间复用。当前阶段若只服务本项目，repo skill 足够。

## MCP 建议清单

| MCP | 优先级 | 作用 | 作用域 | 风险 |
|---|---|---|---|---|
| OpenAI Docs MCP | P1 | Codex/OpenAI 官方文档查询 | user | 只读，低风险 |
| GitHub MCP | P1 | issues/PR/commit/备份状态 | local/user | 注意私库权限，默认只读 |
| Read-only DuckDB MCP | P1 | 查询研究结果、数据 catalog、成本台账 | project | 必须屏蔽 Holdout |
| Custom Data Catalog MCP | P1 | 暴露 schema/hash/data inventory/resources | project | 只读资源优先，不给写工具 |
| arXiv/Semantic Scholar/Exa | P2 | 外部论文与资料检索 | user | prompt injection，需 evidence grade |
| Binance/Exchange Data MCP | P2 | funding/OI/klines 查询 | local | API 限流、地区访问、不能带交易权限 |
| Hummingbot/Jesse MCP | P3 | 未来策略执行/回测控制参考 | local | Phase 1 不接交易执行 |
| Trading execution MCP | 禁装 | 下单、改仓、资金操作 | — | Phase 1 禁止 |

**MCP 原则：**

1. 本项目优先用 Resources 暴露上下文，用 Tools 只做只读查询。
2. 所有含凭据的 MCP 走 local/user scope，不提交 `.mcp.json`。
3. 项目共享 `.mcp.json` 只允许无密钥、只读、本地 stdio 服务。
4. MCP 输出的网页/外部文本默认不可信，必须经过 evidence-grade skill。

## Hooks / 自动化护栏

本项目最值得加的 hook 是“禁止错事”，不是“自动做更多事”。

| Hook | 触发 | 行为 |
|---|---|---|
| `block-holdout-read` | PreToolUse Read/Grep/Bash | 命令或路径含 `06_RESEARCH/DATA/HOLDOUT` 则 deny |
| `block-memory-core-low-tier-write` | PreToolUse Edit/Write | 低模型任务写 `01_MEMORY_CORE` 或 DEC 正文时 deny/ask |
| `block-full-sample-quantile` | PostToolUse / lint | 检测研究脚本中全样本 `.quantile()` 无 rolling/expanding 注释 |
| `require-evidence-grade` | Stop / report lint | 外部链接无 A/B/C 标记则提醒 |
| `codex-task-output-check` | Result intake | 检查 CODE/RESULT/REPORT/pytest 是否齐全 |

## Claude / Codex 分工升级

| 工作 | Claude | Codex | 低模型 | MCP |
|---|---|---|---|---|
| 研究方向判断 | R | C/异议 | 禁 | 资料 |
| 预登记 | R | C | 禁 | 数据目录 |
| 数据契约脚本 | V | R | 禁 | DuckDB/schema |
| 事件研究实现 | V | R | 禁 | 只读数据 |
| 文件横幅/索引 | V | 禁判断 | R | — |
| 独立复核 | R/V，隔离上下文 | 可复算 | 禁 | 原始数据白名单 |
| 状态同步 | R | 报告输入 | 机械候选 | state_check |

## P0 / P1 / P2 落地清单

### P0：立即修

1. 根目录 `AGENTS.md` 实装并记录 hash，避免 `AGENTS_DRAFT.md` 与 runbook 说法不一致。
2. Context Pack 加“允许读取路径白名单”，不是只写禁读原则。
3. 低模型章程新增硬禁：不得语义修改 DECISION_LOG、CURRENT_STATE、Protocol 门槛、研究结论。
4. 所有新研究任务书强制 evidence grade 表和“内部证据冲突检查”。

### P1：本阶段完成

1. 建 4 个高杠杆 skill：`codex-task-spec`、`result-intake`、`data-contract`、`evidence-grade`。
2. 建只读 data catalog：先用 markdown/json manifest，后续再接 DuckDB MCP。
3. `state_check.py` 加日期/索引/外部来源等级/holdout 路径检查。
4. 把 `TOOL_ROUTING.md` 升级为“工具路由 + 权限矩阵”。

### P2：后续评估

1. 打包 `ai-quant-os` 插件。
2. 接 GitHub MCP 做 issue/PR/审计联动。
3. 接 Exa/arXiv 类检索 MCP，但所有输出必须经 evidence grade。
4. Phase 2 再评估 Nautilus/Hummingbot/Jesse 的 MCP/执行控制。

## 不建议做

1. 不接外部云记忆。项目的 Memory Core 已经更可审计。
2. 不上 LangGraph/重型 multi-agent 框架。当前 WIP 和预算不支持。
3. 不把交易所下单做成 MCP tool。Phase 1 研究期没有这个权限。
4. 不把所有文档塞进 `CLAUDE.md` 或 `AGENTS.md`。这会降低遵循率并烧上下文。
5. 不追求“全自动研究发现”。剩余独立实验命太少，自动探索会扩大过拟合风险。

## 30 天路线

| 时间 | 动作 | 验收 |
|---|---|---|
| D1-D2 | 实装 `AGENTS.md` + Context Pack 白名单 | Codex 任务书能引用 hash |
| D3-D5 | 建 `aiq-codex-task-spec` / `aiq-result-intake` | 下一次 Codex 发包和验收使用 |
| D6-D10 | 建 `aiq-data-contract` + data catalog manifest | 每份结果报告有数据 hash |
| D11-D15 | 建 evidence-grade 流程 | 外部来源全部 A/B/C |
| D16-D20 | hook/lint 试运行 | 能拦截 Holdout 路径和无 evidence grade |
| D21-D30 | 评估是否插件化 | 2 轮任务稳定后再打包 |

