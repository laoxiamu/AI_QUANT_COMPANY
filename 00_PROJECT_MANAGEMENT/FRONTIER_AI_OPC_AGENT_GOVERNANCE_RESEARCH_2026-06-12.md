# 前沿知识调研：一人公司 / OPC / AI-Native / AI治理 / AI Coding / Agent Harness / AI编排

**日期：** 2026-06-12  
**定位：** 给 AI Quant Company 做上游知识摄取，不直接改 OS；把外部前沿翻译成本项目可执行的组织、治理、工程原则。  
**关键词：** One-Person Company / OPC、AI-native company、AI-native operating system、AI governance、AI coding、agent harness、agent orchestration、MCP、A2A、agent identity、AI security。  
**证据等级：** A=官方标准/官方文档/同行评审或机构研究；B=arXiv/工作论文/高质量开源文档；C=新闻/博客/行业观察，仅作趋势线索。

## 结论摘要

1. **一人公司不是“一个人做更多事”，而是“一个人拥有并治理一套可复用操作系统”。**
2. AI 让 solo founder/OPC 数量上升，但高质量结果仍常由团队胜出；本项目不能把“AI=无限人力”当作前提。
3. 前沿共识正在从“模型能力”转向“agent harness 能力”：工具、沙盒、权限、记忆、验证器、trace、反馈闭环决定 agent 能不能长跑。
4. AI coding 的核心变化是从 code-first 到 intent/spec-first；Founder/Claude 的价值上移到问题定义、验收、风险边界。
5. 编排框架很多，但当前阶段不该上重型 LangGraph/CrewAI/AutoGen；应先把文件式 handoff + Skill + hook + trace 做成轻量 harness。
6. AI agent 要像员工一样管理：身份、权限、负责人、生命周期、审计日志、离职/停用流程。
7. 本项目最大 AI 治理风险不是“模型不聪明”，而是 tool misuse、memory poisoning、prompt injection、过度授权和自动化消耗独立 Alpha 命。
8. 推荐路线：**Harness first, orchestration later.** 先做 agent registry、trace schema、permission matrix、eval harness，再考虑多 agent 框架。
9. 对本项目而言，AI agent 只应自动化“可复核动作”，不应自动化“研究方向下注”。
10. 未来 30 天最有价值的落地件：Agent Registry、Agent Run Trace、AI Risk Register、Harness Spec、No-Holdout Hook、Research Eval Harness。
11. **AI-Native 不是“让 AI 多干活”，而是把公司文件、流程、权限、评估和记忆设计成 AI 可以可靠执行、复核、追责的操作系统。**

## 关键定义

| 概念 | 本报告定义 | 对本项目含义 |
|---|---|---|
| OPC / One-Person Company | 一人拥有主要决策权，通过 AI、自动化、外包和软件压缩组织职能的公司 | Founder 是董事会，不是执行工；AI OS 是员工层 |
| AI-native company | 从第一天就把 AI 作为组织结构、流程和产品能力的公司 | 文件、任务、复核、审计都要给 agent 可读 |
| Agent Harness | 包围模型的运行时系统：工具、沙盒、权限、记忆、验证器、执行循环、trace、反馈通道 | 本项目应建设 harness，而不是只换更强模型 |
| AI Orchestration | 多 agent / 多步骤任务如何分工、交接、暂停、恢复、升级 | 当前用文件式 handoff；重框架 Phase 2 再评估 |
| Agent Governance | 对 agent 的身份、权限、数据访问、行为、生命周期和责任归属进行治理 | 每个 agent/任务都要有 owner、scope、日志、禁区 |
| AI Coding | 用 agent 承担代码探索、实现、测试、修复、review 的软件工程形态 | Codex 做实现，Claude 做验收与方向判断 |

## 趋势零：AI-Native 的核心不是模型，而是组织可执行性

AI-native company 经常被误解成“用很多 AI 工具的公司”。对本项目，这个定义太浅。真正有用的 AI-native 应定义为：

> 公司关键资产、流程、权限、评估、记忆和决策记录，从设计之初就能被 AI agent 安全读取、执行、复核和追责。

**AI-native 的四层成熟度：**

| 层级 | 常见形态 | 对本项目的判定 |
|---|---|---|
| L0 工具使用 | 让 Claude/Codex 帮写文档、代码、报告 | 已达到，但不能构成优势 |
| L1 文件可读 | 目录、命名、索引、BOOT_BRIEF 能让 agent 恢复上下文 | 基本达到；仍有状态文件漂移风险 |
| L2 流程可执行 | 任务包、验收口径、runbook、hook 能让 agent 稳定跑同类任务 | 部分达到；研究 eval harness 还缺 |
| L3 治理可追责 | 每个 agent 有身份、权限、trace、成本、风险、生命周期 | 尚未达到；这是本项目下一步 |

**AI-native 公司和传统自动化公司的差别：**

| 维度 | 传统自动化 | AI-native |
|---|---|---|
| 工作输入 | 人类说明 + 脚本参数 | agent-readable task spec + context pack |
| 组织记忆 | 人脑、会议纪要、Wiki | 分层 memory + BOOT_BRIEF + decision/event log + graveyard |
| 质量控制 | 人 review 结果 | preflight gate + test/eval + independent reviewer + trace |
| 权限模型 | 人拥有系统权限 | agent role 拥有最小权限，敏感路径默认拒绝 |
| 复用方式 | 复制脚本 | skill / runbook / harness / reusable context |
| 风险边界 | 事后问责 | 事前工具限制、无前视 hook、holdout 禁区、成本闸门 |

**本项目的 AI-native 机会：**

1. Founder 无技术背景、每天时间少，最适合把“判断权”和“执行权”拆开：Founder 定义风险偏好与最终否决，Claude 做主理人/CTO，Codex 做实现与复核，低模型做机械整理。
2. 量化研究高度适合 AI-native，因为它天然有 spec、数据、代码、测试、结果、墓园；只要把 eval 和 trace 做严，AI 可以压缩执行成本。
3. 量化研究也最容易被 AI-native 误伤：模型会生成漂亮但污染、过拟合、无成本、无时序纪律的 alpha 叙事。

**本项目的 AI-native 最小标准：**

- 任一研究任务必须有 `task_spec`：假设、样本、禁区、成本、通过/失败判据、输出路径、是否耗独立 Alpha 命。
- 任一 agent 执行必须有 `run_trace`：输入文件、读取禁区检查、工具、命令、结果文件、失败/异常、成本估算。
- 任一 AI 生成策略必须通过 `evidence_gate`：无前视、成本、样本外、参数数量、变体数量、DSR/PBO 或同等过拟合惩罚。
- 任一记忆更新必须通过 `state_sync`：只更新活动区/索引/状态，不改写历史决策正文。
- 任一插件/MCP/skill 必须登记：用途、权限、数据外发风险、是否可写、是否可能触发用户确认、默认是否禁用。

**与现有 OS 的差距：**

| 现有设计 | 缺口 | 建议 |
|---|---|---|
| 四蓝图 + BOOT_BRIEF + state_check | 主要是文档可读，还不是运行时治理 | 增加 `04_AI_TEAM/AGENT_REGISTRY.md`、`AGENT_RUN_TRACE_TEMPLATE.md` |
| Codex 直调通道 | 有执行路径，但 agent 权限和输出 trace 不够制度化 | 每次直调必须产出 trace；高风险工具默认禁用 |
| 低模型任务包 | 适合机械执行，但缺质量指标 | 增加验收 checklist、允许文件、禁止文件、失败回滚规则 |
| Research Protocol v1.3 | 强研究纪律，但 AI-generated alpha 风险未单列 | 增加 “AI Alpha Evidence Gate” |
| 墓园索引 | 防复活有效，但缺“相似假设/机制邻近”检索 | 增加失败机制标签：crowding, trend, reversal, funding, OI, liquidation |

**审计判断：** AI-native 是本项目的结构性优势候选，但只有在 L2-L3 成熟度后才成立。当前若继续扩大 agent 数量而不补 harness，AI-native 会变成“更快地产生幻觉 alpha 和治理债”。

## 趋势一：AI-enabled OPC 正在出现，但不是“无人公司神话”

**外部信号：**

- Nasdaq Economic Institute 2026 年 AI 研究称，生成式 AI 和 agentic coding 与美国一人企业申请增长相关；Nasdaq 页面明确说 2025 年初以来新企业申请加速，solo entrepreneurs 是核心群体（A/C，Nasdaq 官方页 + Axios 报道：[Nasdaq](https://www.nasdaq.com/economic-institute/ai-enabling-more-entrepreneurship)、[Axios](https://www.axios.com/2026/06/09/ai-entrepreneurs-founders-nasdaq)）。
- arXiv Product Hunt 研究显示：生成式 AI 后 solo entry 增加，但高排名/高质量结果仍更多由团队主导（B，[Generative AI Fuels Solo Entrepreneurship, but Teams Still Lead at the Top](https://arxiv.org/abs/2605.10291)）。
- Federal Reserve 2026 note 显示美国企业 AI 采用率到 2025 年底约 18%，个人工作中 GenAI 使用更高，说明 AI 已从玩具进入工作流，但企业级采用仍不均衡（A，[Federal Reserve](https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html)）。

**对本项目的判断：**

| 错误理解 | 正确理解 |
|---|---|
| AI 让 Founder 一个人等于十人团队 | AI 只压缩重复执行，不能替代最终风险责任 |
| 一人公司可以省掉治理 | 一人公司更需要治理，因为没有团队互相制衡 |
| 多开 agent = 扩张组织能力 | 多开无治理 agent = agent sprawl 和认知负债 |
| 外部 solo founder 趋势证明本项目该加速 | 趋势证明方向可能，但不降低交易研究的证据门槛 |

**项目原则：** 本项目的 OPC 模型应叫 **One-Person-Controlled Company**，不是 One-Person-Does-Everything Company。

## 趋势二：Agent 要像员工一样被治理

Microsoft 2026 Agent 365 / Entra Agent ID 的方向很清楚：agent 需要 identity、access control、inventory、lifecycle、audit。Microsoft 官方称 Agent 365 是用于 observe、secure、govern AI agents 的 control plane；Entra Agent ID 是给 agent 的身份与安全框架（A，[Microsoft Agent 365](https://www.microsoft.com/en-us/microsoft-agent-365)、[Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id)）。

**对一人公司的启发：**

| 企业级能力 | 一人公司最小实现 |
|---|---|
| Agent inventory | `04_AI_TEAM/AGENT_REGISTRY.md` |
| Agent identity | agent_id / role / owner / allowed paths / allowed tools |
| Access package | Context Pack + permission matrix |
| Lifecycle | draft → active → suspended → retired |
| Audit | Agent run trace + input/output files + cost + decision |
| Shadow AI discovery | 禁止未登记 agent 写项目权威文件 |

**本项目建议的 Agent Registry：**

```markdown
| agent_id | role | owner | scope | allowed_tools | forbidden_paths | output | status |
|---|---|---|---|---|---|---|---|
| claude-main | 主理人/CTO | Founder | 判断/验收/状态 | file/web/bash | HOLDOUT/交易执行 | 决策建议/报告 | active |
| codex-impl | 实现工程师 | Claude | 代码/测试/复现 | file/bash | HOLDOUT/DEC正文 | CODE/RESULT/REPORT | active |
| low-tier-doc | 机械执行 | Claude | 横幅/索引/格式 | file only | Memory Core语义/研究结论 | diff摘要 | active |
| risk-reviewer | 风控反审 | Claude | 风险/爆仓/相关性 | read only | 提案结果/equity | _RISK_REVIEW | active |
```

## 趋势三：Agent Harness 比“多 agent 编排”更关键

2026 年 “Code as Agent Harness” 综述把 agent harness 定义为包围 LLM 的软件层：工具、API、沙盒、记忆、验证器、权限边界、执行循环、反馈通道；核心观点是 autonomy bottleneck 不只在模型推理，也在模型连接外部动作和持久状态的系统可靠性（B，[arXiv 2605.18747](https://arxiv.org/html/2605.18747v1)）。

另一篇 Agent Harness survey 总结了生产级挑战：sandbox/security、evaluation、protocol standardization、runtime context、knowledge/context engineering、tool governance、memory architecture、planning loop governance、multi-agent coordination；它特别强调 memory poisoning、tool composition escalation 和 benchmark/harness coupling 风险（B，[Preprints](https://www.preprints.org/manuscript/202604.0428)）。

**本项目当前 harness 架构：**

| Harness 组件 | 当前状态 | 缺口 |
|---|---|---|
| 指令层 | `CLAUDE.md` / `AGENTS_DRAFT.md` | AGENTS 实装 hash 未记录 |
| 工具层 | Desktop Commander / Codex CLI / WebSearch / scheduled tasks | 权限矩阵不够机器可检查 |
| 记忆层 | BOOT_BRIEF / CURRENT_STATE / DECISION_LOG / GRAVEYARD | memory poisoning 防护弱 |
| 验证层 | pytest / state_check / 独立复核 | agent run eval 不成体系 |
| 权限边界 | 文档禁令 | hook/deny 规则未落地 |
| Trace | Codex REPORT | 缺 trace_id、input_hash、prompt_hash、token_cost |
| 反馈闭环 | Claude 验收 | 缺统一 result-intake schema |

**结论：** 当前最应该建设的是 `AIQ Agent Harness v0.1`，而不是上 LangGraph 或 CrewAI。

## 趋势四：AI Coding 的真实上限取决于任务长度、上下文和 harness

SWE-bench 官方 leaderboard 显示 coding agent 已在可验证 GitHub issue 上取得很高成绩，但这不等于生产级长任务可靠；SWE-Bench Pro 明确针对 long-horizon、enterprise-level、多文件复杂任务，论文报告统一 scaffold 下模型表现仍显著低于简单 benchmark（A/B，[SWE-bench](https://www.swebench.com/)、[SWE-Bench Pro arXiv](https://arxiv.org/abs/2509.16941)）。

METR 提出用“task-completion time horizon”衡量 agent 能完成多长的人类任务，显示能力快速提升，但长任务仍是关键瓶颈（B，[METR](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)）。

**项目含义：**

| AI coding 前沿 | 本项目动作 |
|---|---|
| 短任务能力很强 | 把 Codex 任务拆成可验收的短闭环 |
| 长任务容易 drift | 每个任务必须有 trace、checklist、出口闸 |
| benchmark 容易被 harness 影响 | 不用通用分数替代本项目验收 |
| coding agent 可以并行 | 并行只用于独立文件/独立调研，不并行改同一权威状态 |
| 代码生成不是终点 | pytest、数据 hash、报告验收才是终点 |

**推荐 AI coding workflow：**

```text
Explore（Claude/Codex读任务与数据契约）
→ Plan（写一屏计划 + 风险 + 测试）
→ Code（Codex实现）
→ Test（pytest + data contract + no-holdout check）
→ Report（CODE/RESULT/REPORT三件套）
→ Intake（Claude按result-intake验收）
```

## 趋势五：编排框架分化，当前应“轻编排”

| 框架/协议 | 前沿定位 | 适合什么时候用 | 本项目现在判断 |
|---|---|---|---|
| OpenAI Agents SDK | code-first agent app，支持 tools、MCP、handoff、guardrails、state、observability | 你要自己拥有 orchestration/state/approvals | 学概念，不接入 |
| LangGraph | stateful graph、durable execution、streaming、human-in-loop | 长流程、多分支、需 checkpoint | Phase 2 评估 |
| CrewAI | roles/tasks/crews/flows，偏多 agent workflow 快速搭建 | 业务自动化/内容/运营流程 | 不适合研究下注 |
| AutoGen | event-driven 多 agent 框架，研究/原型传统强项 | 多 agent 对话实验 | 注意部分版本维护状态，不作为主线 |
| Pydantic AI | typed output、schema validation、Pythonic agent | 需要强结构化输出 | 可借鉴到 result schema |
| MCP | agent-to-tool / context protocol | 给 agent 安全读工具/数据 | P1，只读 |
| A2A | agent-to-agent interoperability | 跨系统 agent 协作 | P2/观望 |

来源：OpenAI Agents SDK 官方文档说明 SDK 适合应用拥有 orchestration、tool execution、state、approvals 的场景（A，[OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents)）；OpenAI Agents SDK tracing 记录 LLM generations、tool calls、handoffs、guardrails 等 run event（A，[Tracing](https://openai.github.io/openai-agents-python/tracing/)）；LangGraph 官方强调 durable execution、human-in-the-loop 等底层编排能力（A/B，[LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview)）；A2A 是 Google 贡献给 Linux Foundation 的 agent interoperability 协议（A/B，[A2A GitHub](https://github.com/a2aproject/A2A)）。

**本项目路线：**

1. 现在：文件式 handoff + Skill + hook + Codex trace。
2. R3 后：若工作流出现长任务重试/暂停/恢复需求，再做 LangGraph 小样。
3. Phase 2：若交易系统需要 agent 控制面，再考虑 MCP/A2A。

## 趋势六：AI 治理从原则变成工程控制

NIST AI RMF 的核心函数是 Govern、Map、Measure、Manage（A，[NIST AI RMF](https://airc.nist.gov/airmf-resources/airmf/)）。OWASP LLM Top 10 与 Agentic AI threats 把风险从 prompt 层扩展到 tool misuse、identity abuse、memory/context poisoning、unexpected code execution、cascading failures（A，[OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)、[OWASP Agentic AI threats](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)、[OWASP Agentic Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)）。

**映射到本项目：**

| NIST 函数 | 项目最小控制 |
|---|---|
| Govern | Agent Registry、权限矩阵、D级决策清单 |
| Map | 每个 agent/use case 的风险地图：读什么、写什么、能否动钱 |
| Measure | trace、token cost、pytest、state_check、研究结果质量 |
| Manage | hook deny、复核、墓园、熔断、降级预案 |

**十大风险在本项目的具体形态：**

| 风险 | 项目场景 | 控制 |
|---|---|---|
| Prompt injection | WebSearch/交易所博客污染任务 | external evidence grade + 引用白名单 |
| Tool misuse | agent 顺手跑回测/读 Holdout | PreToolUse hook + task spec 禁区 |
| Identity abuse | Codex/低模型越权改 Memory Core | agent_id + allowed paths |
| Memory poisoning | 外部错误写入 BOOT_BRIEF/CURRENT_STATE | 只有 Claude 主会话可升格状态 |
| Unexpected code execution | skill/MCP 脚本带恶意代码 | skill 审查 + 禁自动安装 |
| Cascading failures | agent 输出错误 → state-sync 扩散 | result-intake 验收后才同步 |
| Excessive agency | 自动生成/测试新 Alpha | 禁自动花独立实验命 |
| Supply chain | 第三方 MCP/plugin 引入风险 | 只读、最小权限、先源码审计 |
| Data leakage | API key / 交易数据外传 | 本地文件式记忆，不用云记忆 |
| Cost DoS | agent 循环烧 token | 每个 run 有 budget + stop condition |

## 本项目应建立的 AIQ Agent Harness v0.1

### 1. Agent Registry

路径建议：`04_AI_TEAM/AGENT_REGISTRY.md`

必填字段：

```text
agent_id, role, owner, model/tool surface, allowed_tools, allowed_paths,
forbidden_paths, output_contract, max_budget, escalation_rule, status
```

### 2. Agent Run Trace

每次 Codex/子代理/低模型任务输出一条 trace：

```json
{
  "trace_id": "aiq_20260612_001",
  "agent_id": "codex-impl",
  "task_id": "TASK_R2_A1_DATA_GATE",
  "prompt_hash": "...",
  "input_files": [{"path": "...", "hash": "..."}],
  "output_files": [{"path": "...", "hash": "..."}],
  "tools_used": ["bash", "apply_patch"],
  "forbidden_paths_touched": false,
  "tests": ["pytest ..."],
  "token_cost_estimate": "...",
  "decision": "pass/fail/needs_review"
}
```

### 3. Harness Spec

路径建议：`04_AI_TEAM/AGENT_HARNESS_SPEC_v0.1.md`

内容：

1. 工具权限矩阵。
2. 读写路径白名单。
3. Trace schema。
4. Hook 规则。
5. Result intake 规则。
6. Agent lifecycle。
7. 安全事件处理流程。

### 4. Eval Harness

本项目不需要通用 SWE-bench；需要项目内部 eval：

| Eval | 目标 | 样例 |
|---|---|---|
| task-spec eval | 任务书是否有目标/禁止/验收/路径 | Codex 发包前检查 |
| no-holdout eval | 是否触碰 Holdout | shell/path lint |
| no-lookahead eval | 是否全样本分位/未来数据 | code lint + 单测 |
| result completeness eval | CODE/RESULT/REPORT/pytest 是否齐 | result-intake |
| evidence eval | 外部来源是否 A/B/C | evidence-grade |
| state-sync eval | 状态是否同步且不滞后 | state_check |

## 对现有 OS 的升级建议

### 一人公司 / OPC

现有“部门=帽子”是对的，但应再加一层：

```text
Founder = Board / Capital Owner
Claude = Operating Principal / AI Chief of Staff
Codex = Engineering Worker
Risk Reviewer = Internal Control
Independent Review = External Audit Function
Low-tier = Clerk
MCP/Data Catalog = Records Office
Hooks = Security Guard
State Files = Company Register
```

这样 Founder 不需要懂技术，也能理解谁有权做什么。

### AI Governance

新增 `AI_RISK_REGISTER.md`，每条风险写：

```text
risk_id, scenario, agent, asset_at_risk, likelihood, impact,
control, owner, review_frequency, status
```

首批风险：

1. Holdout 误读。
2. 外部来源 prompt injection。
3. Codex 越权修改 Memory Core。
4. 低模型语义误改。
5. 自动任务旧口径。
6. Agent 反复循环烧 token。
7. MCP/plugin supply-chain。
8. API key / 交易权限泄漏。

### AI Coding

Codex 任务书应升级为：

```text
Problem
Mechanism / business reason
Inputs with hashes
Forbidden paths
Allowed tools
Implementation constraints
Tests to run
Report schema
Stop condition
Professional dissent condition
```

### Agent Harness

把“七问”从自然语言 checklist 升级为结构化 YAML frontmatter：

```yaml
mechanism: ...
evidence_grade: A/B/C
internal_conflict_checked: true
holdout_forbidden: true
allowed_paths:
  - 06_RESEARCH/CODE/
  - 06_RESEARCH/RESULTS/
stop_if:
  - sample_size_below_power_threshold
  - task_requires_holdout
  - external_evidence_only_C
```

### AI 编排

当前不建议引入重型编排。推荐最小编排：

```text
task markdown -> agent run trace -> result intake -> state sync -> audit
```

只有出现以下情况才升级 LangGraph/Agents SDK：

1. 同一任务需要多次暂停/恢复。
2. 需要机器自动决定 handoff。
3. 需要长期运行的 agent worker。
4. 需要在线服务化而非文件式批处理。

## P0 / P1 / P2 清单

### P0：立即做，否则 AI OS 会带来治理债

| 编号 | 动作 | 原因 |
|---|---|---|
| P0-1 | 建 `04_AI_TEAM/AGENT_REGISTRY.md` | agent 要有身份、owner、权限、状态 |
| P0-2 | Codex/低模型/Reviewer 任务全部加 trace_id | 没有 trace 就没有审计 |
| P0-3 | 建 no-holdout hook 或 lint | 这是项目最高数据安全红线 |
| P0-4 | Context Pack 加 allowed_paths 白名单 | “禁读”不如“只准读” |
| P0-5 | 新任务书强制 evidence grade + internal conflict check | 防 A-2 式叙事确认 |
| P0-6 | 禁止任何 agent 自动消耗独立 Alpha 命 | 方向下注必须 human/Claude 评估 + Founder 知悉 |

### P1：本阶段做，显著提高质量

| 编号 | 动作 | 产物 |
|---|---|---|
| P1-1 | 建 `AGENT_HARNESS_SPEC_v0.1.md` | 权限矩阵、trace schema、hook、eval |
| P1-2 | 建 `AI_RISK_REGISTER.md` | Govern/Map/Measure/Manage 映射 |
| P1-3 | 升级 Codex task template | 结构化 frontmatter + stop condition |
| P1-4 | 建 result-intake schema | 验收可机器检查 |
| P1-5 | 建 agent run log | `04_AI_TEAM/RUN_LOG.md/jsonl` |
| P1-6 | 建 Skill：`aiq-harness-check` | 发包前自动检查任务书 |
| P1-7 | 建 Skill：`aiq-agent-review` | 审查 agent 权限与安全 |
| P1-8 | 对工具路由加权限矩阵 | 哪类 agent 能读/写/跑命令 |

### P2：观察或 Phase 2 评估

| 编号 | 动作 | 条件 |
|---|---|---|
| P2-1 | LangGraph 小样 | 出现长流程 checkpoint 需求 |
| P2-2 | OpenAI Agents SDK 小样 | 要把 agent workflow 服务化 |
| P2-3 | A2A 观望 | 多 provider agent 真要互通 |
| P2-4 | Microsoft Agent 365 类思路 | 若项目进入多设备/多人/企业账号 |
| P2-5 | Agent observability 工具 | run log 规模超过手工可读 |
| P2-6 | 本地只读 MCP control plane | 数据 catalog 稳定后 |

## 30 / 60 / 90 天路线

### 30 天：先把 agent 当员工登记

1. `AGENT_REGISTRY.md`
2. `AGENT_HARNESS_SPEC_v0.1.md`
3. Codex task trace schema
4. no-holdout lint/hook
5. Context Pack allowed_paths
6. AI_RISK_REGISTER.md

### 60 天：把研究流程变成 eval harness

1. result-intake schema
2. evidence-grade skill
3. no-lookahead check
4. experiment registry
5. agent run log dashboard
6. cost/token run accounting

### 90 天：再评估编排框架

1. 如果 R3/R4 出现长流程，做 LangGraph/Agents SDK 小样。
2. 如果实盘系统需要 AI 控制面，设计只读 MCP。
3. 如果多 agent 超过 6 个活跃角色，再考虑 agent identity/lifecycle 更正式化。
4. 如果项目仍在 Phase 1，不上重框架。

## 对本项目的最终主张

**本项目不需要“更多 AI”，需要“更像公司的 AI”。**

前沿正在告诉我们三件事：

1. **Solo founder 会变强，但最强的是会设计操作系统的人，不是最会开 agent 的人。**
2. **Coding agent 会越来越强，但可靠性来自 harness：权限、测试、trace、复核、上下文纪律。**
3. **Agent 编排不是第一性问题；agent 治理才是。**

因此，本项目下一步不应追 agent 框架热潮，而应把当前 Claude/Codex/低模型/Reviewer 变成有身份、有权限、有审计、有停用机制的“AI 员工系统”。

## 资料索引

### 一人公司 / OPC

- Nasdaq Economic Institute: AI enabling more entrepreneurship（A/C）：https://www.nasdaq.com/economic-institute/ai-enabling-more-entrepreneurship
- Axios on Nasdaq solo founder boom（C）：https://www.axios.com/2026/06/09/ai-entrepreneurs-founders-nasdaq
- Generative AI Fuels Solo Entrepreneurship, but Teams Still Lead at the Top（B）：https://arxiv.org/abs/2605.10291
- Digital Co-Founders（B）：https://arxiv.org/abs/2511.09533
- Federal Reserve AI adoption note（A）：https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html

### AI Governance / Security

- NIST AI RMF（A）：https://airc.nist.gov/airmf-resources/airmf/
- OWASP LLM Top 10（A）：https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP Agentic AI Threats and Mitigations（A）：https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/
- OWASP Top 10 for Agentic Applications 2026（A）：https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Microsoft Agent 365（A）：https://www.microsoft.com/en-us/microsoft-agent-365
- Microsoft Entra Agent ID（A）：https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id

### AI Coding / Agent Harness

- Code as Agent Harness（B）：https://arxiv.org/html/2605.18747v1
- Agent Harness survey（B）：https://www.preprints.org/manuscript/202604.0428
- SWE-bench leaderboard（A/B）：https://www.swebench.com/
- SWE-Bench Pro（B）：https://arxiv.org/abs/2509.16941
- METR long task horizon（B）：https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/

### 编排 / 工具 / 协议

- OpenAI Agents SDK（A）：https://developers.openai.com/api/docs/guides/agents
- OpenAI Agents SDK tracing（A）：https://openai.github.io/openai-agents-python/tracing/
- Codex AGENTS.md（A）：https://developers.openai.com/codex/guides/agents-md
- Codex Skills（A）：https://developers.openai.com/codex/skills
- Claude Code memory（A）：https://docs.anthropic.com/en/docs/claude-code/memory
- Claude Code hooks（A）：https://docs.anthropic.com/en/docs/claude-code/hooks
- Claude Code subagents（A）：https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Claude Code skills（A）：https://docs.anthropic.com/en/docs/claude-code/skills
- LangGraph overview（A/B）：https://docs.langchain.com/oss/python/langgraph/overview
- A2A Protocol（A/B）：https://github.com/a2aproject/A2A
