# RESEARCH-AI-NATIVE-20260621 公司级综合分析

**任务性质：** 外部资料综合、项目事实核验、行动设计  
**日期：** 2026-06-21  
**输入：** Founder 提供 31 个链接；项目现有顶层治理、Agent 协作、任务路由、Discord、OSS 和研究行动文件  
**配套文件：** `SOURCE_CATALOG_AI_NATIVE_20260621.md`、`DRAFT_ACTION_PACKAGE_AI_NATIVE_20260621.md`  
**边界：** 未读取 Holdout；未改预登记；未初始化 Spec Kit；未修改 `00_PROJECT_MANAGEMENT/` 或 `01_MEMORY_CORE/` 权威文件。

> **[专业异议]** 不能把本轮调研收敛成“找几个开源项目、做 Agent 路由、搭一个工作流”。31 篇资料能启发 AI 组织和工程方法，但它们严重偏向 AI coding 热点，并不覆盖一家量化公司的完整经营与风险责任。如果直接围绕文章中的工具开工，会再次发生治理建设取代公司主线、局部效率掩盖全局缺口的问题。本报告因此按公司九大能力域分析，工具只作为手段。

## 一、结论先行

### 1. 这些文章真正共同指向什么

28 篇可读资料虽然表面上谈 Codex、Claude、Loop、Skill、子代理、飞书、RAG 和 OPC，底层反复指向五件事：

1. **AI 产能必须被确定性系统包住。** 目标、状态、权限、证据、退出、恢复和审计不能只写在 prompt 里。
2. **人的价值从执行上移到方向、边界和裁决。** 但“人少”不等于“责任消失”；Founder、Claude 和 Codex 的决策权必须清楚。
3. **组织学习必须转成资产。** 失败、判断和反馈要进入测试、规则、Skill、ADR、知识条目或任务模板，而不是停在聊天和报告。
4. **多 Agent 的价值是独立视角和上下文隔离，不是角色数量。** 没有契约和验证，多 Agent 只会增加漂移、成本和责任模糊。
5. **速度必须服从真实反馈。** 小步、可逆、可验证成立；无反馈地快速生产文档、代码或实验不创造公司价值。

### 2. 对当前项目的总判断

AI_QUANT_COMPANY 不是“缺方法论”，而是存在三层断裂：

- **公司层断裂：** 策略研究、交易平台、实时风控、资本账务、运营、AI 团队和治理没有共同的能力地图、经营指标和阶段门。
- **治理层断裂：** 已有规则很多，但权威文件冲突、研究行动积压、任务状态和验收证据不能被机器可靠检查。
- **运行层断裂：** Claude 能派 Codex，Codex 能回报告，但没有耐久状态机负责依赖、重试、恢复、预算、人工接管和战略复评。

因此当前不需要全项目重构，也不应先上重型多 Agent 平台。正确顺序是：

```text
统一权威和公司能力地图
  -> 手工跑通任务/辩论/研究回灌协议
  -> 把稳定协议编码成轻量 Orchestrator
  -> Web/Discord/飞书等只作为可替换入口
  -> 达到明确规模门槛后才评估 LangGraph/Temporal/A2A/RAG
```

### 3. Claude 还是 Codex 主导

维持已经确定的责任结构：

- **Claude：** 公司/研究/架构主理人，整合证据，回应异议，形成裁决；不能只做被动验收和状态搬运。
- **Codex：** 工程实现者、工程反方、可复现验证者；有专业异议义务，但不直接升级公司决策。
- **Founder：** 资本、公司终态、研究方向、资金和不可逆事项的最终责任人。
- **确定性 Orchestrator：** 只管理流程事实，不做专业判断。

不是把主导权换给 Codex，而是用**独立反审 + 书面裁决 + Strategy Governor + 数据验证**约束 Claude 单点偏差。两个模型达成一致也不是事实证明。

## 二、公司九大能力域分析

| 能力域 | 文章提供的有效启发 | 项目已有基础 | 顶层缺口 | 本轮建议 |
|---|---|---|---|---|
| 1. 战略与业务组合 | Idea/MVP/Launch/Scale；小而美、盈利和真实反馈；AI-native 是闭环组织 | Master Plan、阶段与研究命管理 | 公司终态、收益来源、资本 runway、治理投入和 Alpha 组合没有统一经营看板；治理任务可吞噬研究主线 | 建公司级能力地图与季度一页记分卡；每项建设必须说明服务哪个公司风险/价值 |
| 2. 组织与决策权 | 清晰 DRI；管理者 dogfood；人保留合规、安全、品味与裁决；多方案用可运行证据比较 | Claude/Founder/Codex 基本分工、DR 机制、专业异议 | Claude 既主理又轮询/同步，形成瓶颈；高严重度异议没有机器阻断；人工审查清单未动态维护 | 保持 Claude 裁决；建立决策分级、异议响应 SLA、动态 HITL 清单和角色绩效指标 |
| 3. 研究与 Alpha | 单次任务要验证机制；先验收再生成；生成者不能自评；反馈回资产 | Research Protocol 强、Holdout 隔离、预登记、结果报告 | 外部资料不提供 Alpha 证据；调研和失败结论没有系统触发下一步；重复研究和局部下钻仍存在 | 建 Research-to-Value Gate；研究输出必须绑定“改变哪个决策/任务/规则”，无行动也要记录拒绝理由 |
| 4. 策略规格与产品化 | Spec、计划、任务、验证分层；一个增量一个变化；真实消费者验收 | 有任务书、RESULTS、CODEX_REPORT | 研究结论到冻结策略规格、ATD、交易接口和上线条件的通道不完整 | Spec Kit 仅试点工程功能；研究规格仍走预登记；后续补 Strategy Product Contract |
| 5. 数据、知识与记忆 | 短期/工作/长期/治理分层；Skill 沉淀判断；Ontology 表达关系与约束 | Memory Core、Knowledge Base、文件式 handoff | 权威冲突、重复文档、来源/TTL/owner/适用边界不完整；检索问题常被误判为 RAG 问题 | 先建元数据和权威关系，不上 RAG/GraphRAG；区分事实、决定、经验、假设、技能和运行事件 |
| 6. 工程与交易平台 | Harness、hooks、workflow、生产观测、错误显式化、最小改动 | AGENTS/CLAUDE、hooks、Codex 直调、研究代码、交易系统蓝图 | Harness 是文档密集而非运行完整；当前态 C4 缺失；交易平台真实能力与蓝图混杂 | G0 修规则冲突；画当前态 C4；把软规则转为少量硬门；平台继续 build-vs-buy 渐进路线 |
| 7. 实时风控、安全与合规 | 最小权限、HITL、审计、fail-fast、治理债；入口不能扩大权限 | Holdout hook、写入边界、禁止 AI 交易执行 | Agent 安全与交易风控容易混在一起；缺 prompt injection/供应链/凭据/紧急停机统一威胁模型 | 单独建立 AI Control Plane Threat Model；交易与资金路径保持确定性代码和人工批准 |
| 8. 运营、监控与事件响应 | 状态机、可恢复循环、独立 evaluator、日志、超时/预算、移动驾驶舱 | TASK_INBOX、RUN_LOG、定时任务、Discord 提案 | DONE 文件不是完整状态机；缺依赖、租约、重试、幂等、心跳、阻塞恢复、事件指标；Discord 尚未解决后台可靠性 | 先建 SQLite append-only Orchestrator PoC；Web/Discord 是 Adapter；launchd/VM 承载常驻进程 |
| 9. 资本、账务与绩效学习 | 小而美强调盈利/控成本；AI 团队强调 outcome 而非 AI 代码比例；SkillOpt 强调验证集 | 有预算意识、研究成本模型和资本目标讨论 | 文章几乎不覆盖交易资本账、PnL 归因、费用/funding 对账、AI token 成本、机会成本和组织绩效 | 建公司记分卡：资本、研究、平台、风险、运营、AI 协作六类指标；技能优化必须绑定基准和业务收益 |

## 三、这批文章没有回答、但项目必须回答的问题

### 1. 资本与公司生存

- 资本本金、可承受亏损、固定成本、数据/API/模型成本和机会成本如何统一入账？
- 没有通过 Alpha Gate 时，公司如何控制治理和平台建设 burn rate？
- 何时停止某一策略族、工具建设或自动化项目，避免沉没成本？

### 2. 量化研究有效性

- 统计显著、经济显著、机制解释和可执行性如何共同决定研究去留？
- 多次尝试、数据窥探、策略家族相关性和 regime 选择如何进入组合级 error budget？
- AI 参与假设生成后，如何记录搜索空间，防止隐形多重检验？

### 3. 交易生产责任

- 回测、paper、shadow、小额实盘和扩容的具体阶段门是什么？
- 实时风控、仓位权威、订单状态、对账、kill switch、灾难恢复和事故复盘由谁负责？
- 交易所故障、API 语义变化、数据延迟和资金异常如何降级？

### 4. 安全、合规和供应链

- Agent 读取外部网页、仓库和 Skill 时的 prompt injection、恶意脚本和数据出境风险如何控制？
- 插件/MCP/Skill 的许可证、版本、哈希、权限和撤销如何登记？
- Founder 作为唯一自然人的操作连续性、凭据恢复和紧急接管如何设计？

### 5. 组织可持续性

- Claude 主会话额度、上下文腐烂和单点裁决失败如何测量？
- Agent 的“判断资产”何时过期、由谁复核、如何废弃？
- 自动化减少的是人工时间，还是把人工时间转移到更难发现的验证债？

这些问题应进入公司总框架，不能指望 Loop、Spec Kit、Discord 或 RAG 自动回答。

## 四、文章之间的冲突与裁决

| 表面冲突 | 本项目裁决 |
|---|---|
| “让 Agent 自主循环” vs “人类保持判断” | 自主只覆盖可逆、低风险、可机器验证的流程；研究方向、架构、资本和上线由 Claude/Founder 裁决 |
| “Skill 沉淀判断” vs “Workflow 硬门可靠” | 判断、启发式和解释写 Skill；计数、权限、schema、状态、验收完整性写代码/Workflow |
| “持久 Agent 更快” vs “上下文越长越腐烂” | 持久的是 mission、状态和资产，不是无限增长的会话；定期 handoff 到新会话 |
| “RAG/本体解决知识问题” vs “大型项目即时搜索代码” | 当前先做权威、元数据和检索入口；达到跨文档关系查询的真实失败门槛再上图谱 |
| “多 Agent 提升质量” vs “DRI 必须唯一” | 多 Agent 提供独立分析，单一 DRI 承担最终决定；禁止共识替代问责 |
| “一人公司快速扩张” vs “小而美节制经营” | 以可持续 Alpha 和资本安全为目标，速度服从反馈，不以 Agent 数量/文档量/代码量衡量规模 |

## 五、任务路由：从静态表升级为风险路由

当前 `TOOL_ROUTING.md` 主要按工作类型和代码行数路由，无法覆盖不确定性、可逆性、验证难度、权限和状态时长。建议路由器按七个维度评分：

1. **决策等级：** 公司/资本/研究/架构/实现/机械。
2. **不确定性：** 目标和方法是否明确。
3. **可验证性：** 是否有确定性检查器。
4. **可逆性与影响面：** 错误是否容易回退，是否影响资金/权威状态。
5. **上下文需求：** 需要全局理解还是局部文件。
6. **工具与权限：** 只读、workspace write、网络、凭据、交易。
7. **持续时间与状态：** 交互任务、一次性 headless、长任务、常驻进程。

### 推荐路由矩阵

| 任务类 | 首责 | 复核/裁决 | 运行形态 | 关键限制 |
|---|---|---|---|---|
| 公司战略、资本、研究方向 | Claude 起草 | Codex/独立角色反审；Claude 综合；D 级 Founder | 隔离只读会话 + DR 文件 | 不允许自动执行后续任务 |
| 架构设计、复杂研究设计 | Claude 或领域主责起草 | Codex 独立 critique；Claude 裁决 | 有限轮辩论 | 先列替代方案和反证，最多三轮 |
| 多文件实现、测试、复现 | Codex | 确定性测试 + Claude 验收 | `codex exec`/独立线程 | 有任务快照、写入范围、预算、退出条件 |
| 独立证据搜索、日志/大文件阅读 | 新鲜子代理/只读 Codex | 主责核对来源 | 临时隔离进程 | 只回传结构化摘要和引用，不写权威文件 |
| 格式、索引、搬运等机械任务 | 低成本模型或脚本 | diff/schema 校验 | 短 headless 进程 | 禁止语义判断和权威变更 |
| 计数、状态、权限、验收完整性 | 确定性代码 | CI/Orchestrator | 本地进程 | 不交给 LLM 猜测 |
| 长期采集、监控、队列 worker | launchd/VM service | 健康检查和告警 | 常驻进程 | 会话内进程不可作为生产服务 |
| 交易、资金、kill switch | 确定性交易系统 | 人工批准/双重检查 | 受控服务 | Agent 只能建议或只读，不能持交易权限 |

### 模型与代理选择原则

- 高歧义、高影响、需综合权衡：使用最强推理模型，限制并发，强制反审。
- 边界清楚、可测试的工程任务：Codex；不需要 Claude 重复实现。
- 大量噪声读取：隔离子代理，主会话只接收小型 evidence pack。
- 机械且可写规则：优先脚本；其次低成本模型。
- 同一模型不可同时充当提案者和唯一 evaluator；至少使用新鲜上下文，关键项优先异模型。
- 路由决定、降级和 fallback 必须写事件日志，不能只由模型临场决定。

## 六、Claude-Codex 自动化协作方案

### 1. 最小可靠内核

```text
Founder / Claude 创建已批准任务快照
  -> Router 根据策略选择 actor/runtime/permission
  -> Orchestrator 生成 context snapshot hash 并派发
  -> Worker 运行、心跳、产出结构化结果
  -> Deterministic Verifier 检查文件/schema/tests/evidence
  -> Claude 处理专业异议并验收
  -> Action Gate 强制生成下一行动或“无行动理由”
  -> 更新权威文档的建议交 Claude 执行
```

建议首版 Python + SQLite 即可，状态和事件必须耐久；CLI、Web、Discord 只是 Adapter。不要让 Claude/Codex Bot 在群聊中自由互相触发。

### 2. 复杂方案辩论

```text
QUESTION_FREEZE
 -> CLAUDE_PROPOSAL（至少两个方案、假设、失败条件）
 -> CODEX_BLIND_CRITIQUE（工程/可验证性/局部最优反审）
 -> CLAUDE_REVISION
 -> INDEPENDENT_CHECK（是否回应高严重度异议）
 -> CLAUDE_ADJUDICATION
 -> FOUNDER_DECISION（仅 D 级）
```

辩论不是自由聊天。每轮输出固定字段：主张、证据、假设、反证、风险、建议、置信度、未解决分歧。达到三轮、预算上限或没有新增高严重度问题即停止。

### 3. 防局部最优的 Strategy Governor

局部任务循环之外必须有独立的升维循环。以下任一条件触发冻结新任务并复评：

- 连续 3 个任务围绕同一局部变量修改，仍无新增机制证据。
- 同类失败重复 2 次且没有新信息。
- 治理/工具任务连续消耗超过当期 WIP 或预算上限。
- 当前行动无法映射到公司九域中的明确目标或风险。
- 关键假设、数据可得性或外部制度发生变化。
- Claude/Codex 分歧涉及研究合法性、资金、安全或不可逆架构。

Strategy Governor 必答：我们在优化哪个公司目标？最上游未验证假设是什么？停止当前路线的证据是什么？还有没有更便宜的实验？继续下钻的机会成本是什么？

## 七、开源项目、插件与 Skill 的定位

### 1. 立即借鉴或复用现有能力

| 项目/能力 | 官方核验 | 建议 | 具体价值 |
|---|---|---|---|
| Superpowers | 项目已安装 | **继续用** | brainstorming、TDD、debug、review、verification 的执行纪律 |
| Loop Engineering 橙皮书 | 官方仓库、MIT、2026-06 活跃 | **借鉴方法** | 形成本项目 Loop Contract 和停止/恢复规则，不作为平台依赖 |
| Darwin Skill / SkillOpt 思想 | SkillOpt 官方仓库 MIT；Darwin 已集成 | **使用现有 Darwin，暂不另装 SkillOpt** | 对有基准集的 Skill 做验证门优化，保留 rejected edits 和版本 |
| ADR + C4 | `adr-tools`/C4-PlantUML 已核验 | **采用格式** | 分离技术决策，建立当前态架构；CLI 可选，不为工具而装工具 |
| RD-Agent/Qlib 机制 | 官方项目已在此前调研核验 | **借鉴 trace/eval/recorder** | 研究/开发分离、实验注册和可追溯，不引入自动 Alpha 工厂 |

### 2. 限时试点

| 项目 | 建议 | 试点边界 | 成功标准 |
|---|---|---|---|
| GitHub Spec Kit | **G0 后做一个工程功能试点** | 不用于新 Alpha、预登记、公司 Constitution 或总 WBS | 需求遗漏/返工下降；不产生第二任务源；产物可归档/删除 |
| LiteLLM 或 Portkey Gateway | **只有出现 3+ API 模型、预算/熔断/审计需求时再 PoC** | 不代理 Claude/Codex 本地订阅会话，不接交易凭据 | 统一成本/限额/fallback 有真实收益，且许可证/数据路径可接受 |
| Claude-to-IM / Discord Adapter | **Orchestrator 稳定后再接** | 只做通知、批准、stop/resume、展示 | 断线不影响后台状态；消息不可直接升级权限 |

### 3. 只借机制，当前不安装

| 项目/方法 | 借鉴内容 | 不安装原因 |
|---|---|---|
| BMAD-METHOD | 角色分离、不同规模工作流、多人讨论 | 与 Superpowers + Spec Kit + 自有角色体系重叠，会增加第二套生命周期 |
| Task Master | task dependency、workstream、main/research/fallback model、loop | 会形成第二套 WBS/状态源；许可证和外部 API 配置也需额外治理 |
| LangGraph / Temporal | checkpoint、durable execution、HITL、重试 | 当前流程尚未稳定，先用 SQLite 状态机验证需求；达到复杂度门槛再迁移 |
| A2A | 跨组织/不透明 Agent 互操作协议 | 当前是同机两类 Agent，内部任务契约足够；过早协议化增加攻击面 |
| CrewAI / AutoGen | 多角色对话与流程编排 | 易放大角色戏剧化和自由对话，不适合研究/资金责任链 |
| RAG / GraphRAG / Ontology | 关系检索和规则表达 | 当前瓶颈是权威与元数据，不是向量召回；先修内容治理 |
| 飞书 27 Skills / FanBox | 聚合工具和移动驾驶舱 | 当前不能同时建设 Web、Discord、飞书、微信四个入口 |

### 4. 之前讨论的项目治理开源项目如何真正利用

这些项目不能停留在“装/不装”的结论；即使不安装，也应把有价值机制明确回灌到自有治理层。

| 项目 | 当前决策 | 现在具体借什么 | 写入本项目哪里 | 重评触发 |
|---|---|---|---|---|
| Superpowers | 已采用 | 设计前澄清、计划、TDD、系统调试、独立 review、完成前验证 | Claude/Codex 共同执行纪律；任务验收字段 | 持续使用，定期核对两端版本共同能力 |
| Spec Kit | 限时试点 | what/why spec、技术 plan、可独立 tasks、artifact analyze | 单一工程功能目录；向 PROJECT_TASK_PLAN 只回写状态链接 | G0 权威冲突修复后 |
| adr-tools | 采用格式，CLI 可选 | Context/Decision/Alternatives/Consequences/Supersedes | 技术 ADR 目录；与业务 DEC 互链而不复制 | 出现第一个已裁决技术架构选择 |
| C4-PlantUML | 近期采用 | System Context、Container、Deployment、代码化 diff | 当前态架构目录；元素标 CURRENT/PLANNED/DEPRECATED | G0 立即需要，不等服务规模增长 |
| BMAD-METHOD | 不安装 | 角色分离、规模适配、Party Mode 的多视角审议 | 自有 DR 协议和 Router 角色模板 | 自有协议无法覆盖产品/UX等新工作流时隔离 PoC |
| Task Master | 不安装 | task dependency、workstream、loop、main/research/fallback model | Orchestrator 数据模型和风险路由，不复制任务库 | PROJECT_TASK_PLAN 依赖图确实无法自动执行时 |
| MCP Shrimp Task Manager | 不安装 | 跨会话任务记忆、复杂任务拆解和继续执行 | task snapshot、context hash、resume token 设计 | 自有状态恢复连续失败并有可测样本时 |
| Plane | 后置 | Work Item/Cycle/Module/Roadmap 的交互模型 | 未来 Web 控制面可借信息架构 | 人类协作者 >3 或多项目并行，且可单向同步 |
| Backstage | 后置 | 软件目录、Owner、模板、TechDocs、资产关系 | 未来服务/数据/模型 catalog schema | 可运行资产约 15-20 个或多 Owner/多环境 |
| Apache DevLake / DORA | 后置 | 部署、失败、恢复和 lead time 的事件口径 | 先在本地 event store 记录原始事件 | 连续 8-12 周 paper/live/CI 数据后 |

**回灌原则：** 每个“借鉴机制”必须在行动包里对应字段、状态或验收；否则仍属于没有后续的调研。本轮已经把 Task Master/Shrimp 的依赖、恢复、workstream 思想写入 Orchestrator 草案，把 BMAD 的多视角写入设计辩论协议，把 DORA 的结果指标写入公司记分卡建议。

## 八、Spec Kit 是否适合

**适合，但只适合工程规格层的限时试点。**

可用范围：

- 明确产品/工程功能的 what/why。
- 技术计划、任务拆分和一致性分析。
- 把一个已批准、边界稳定的功能变成可执行任务。

禁止范围：

- 不替代 Research Protocol、假设预登记和 Holdout 纪律。
- 不决定公司战略、资本目标或研究方向。
- 不建立第二份项目总计划和第二套 Constitution。
- 不把尚未裁决的想法包装成“完整规格”后自动实施。

第一个试点建议选 Orchestrator 的**只读任务快照校验器**或**完成事件 schema 校验器**，而不是 Alpha 实验。试点结束必须做保留/修改/删除裁决。

## 九、AGENTS / CLAUDE / ADR / C4 / 任务计划书落地

| 产物 | 应解决什么 | 当前必须先处理 | 落地边界 |
|---|---|---|---|
| AGENTS.md | Codex 的稳定职责、禁区、项目入口和完成证据 | 与 AGENT_REGISTRY 的 commit 权限冲突；压缩重复流程 | 只放稳定规则，重复步骤转 Skill/validator |
| CLAUDE.md | Claude 的决策责任、读取入口、升级规则 | 与 SYSTEM_RULES 的 Memory 写入冲突；避免超长 | 决策原则与入口，详细流程转 Skill/Workflow |
| ADR | 技术架构选择、备选和后果 | 不把研究方向 DEC 伪装成 ADR | 首篇可记录 Orchestrator + Adapter 分层；后续记录事件库和交易平台选择 |
| C4 | 当前真实系统边界、容器、部署和责任 | 明确 CURRENT vs TARGET | 先 L1/L2/Deployment 当前态；未来态单独标识 |
| PROJECT_TASK_PLAN | 公司项目群、依赖、WIP、阶段门和 owner | 避免完整实现细节和第二 WBS | 只保留组合级任务；实现细节进 Spec/任务包 |

## 十、调研如何强制产生价值

从本轮起，研究任务只有同时满足以下条件才算完成：

1. 有明确决策问题，不以“了解一下”为目标。
2. 每个来源有证据等级、日期、适用边界和冲突记录。
3. 结论映射到公司能力域和现有项目事实，而非只总结文章。
4. 每项结论必须是 `ADOPT / PILOT / OBSERVE / REJECT` 之一。
5. `ADOPT/PILOT` 必须绑定 owner、依赖、验收证据、成本上限和停止条件。
6. `OBSERVE` 必须有重评触发条件；`REJECT` 必须记录原因，防止重复调研。
7. 至少生成一个机器可检查的行动项，或明确证明“无行动是最优决策”。
8. 下一次相关任务开工前必须读取行动登记；过期项触发复评而不是继续堆报告。

具体行动包见 `DRAFT_ACTION_PACKAGE_AI_NATIVE_20260621.md`。Codex 未直接修改 `RESEARCH_ACTION_REGISTRY.md`，由 Claude 验收后选择性升级。

## 十一、推荐顺序

### G0：先修可信输入（不增加新平台）

- Claude 裁决 AGENTS/CLAUDE/SYSTEM_RULES/AGENT_REGISTRY 冲突。
- 建当前态公司九域图、C4 L1/L2 和技术 ADR 边界。
- 将本报告行动提案升级到正式登记，明确“不采用”项。

### G1：手工验证协议

- 用一项低风险工程任务跑任务闭环。
- 用一个真实架构问题跑 Claude 提案 -> Codex 反审 -> Claude 裁决。
- 用下一次外部调研跑 Research-to-Value Gate，验证是否真的产生后续动作。

### G2：编码最小 Orchestrator

- SQLite task/event store、状态机、context hash、租约、重试、幂等和 verifier。
- 先只读/模拟，不自动改权威文件。
- 加 Strategy Governor 触发器和人工接管。

### G3：再接入口和规格工具

- Web 主控制面、Discord 远程 Adapter。
- Spec Kit 单功能试点。
- 达到明确阈值后再评估模型网关、LangGraph/Temporal、RAG/本体。

这条路线不要求全项目重构，也不会让治理无限占用 Alpha 研究。公司主线与治理轨应双轨推进，并设置治理 WIP 上限。

## 十二、需 Claude 裁决

1. 是否接受“公司九大能力域”作为后续顶层诊断和任务归属框架。
2. 是否批准 Research-to-Value Gate 成为所有外部调研的完成门。
3. 是否将静态 TOOL_ROUTING 升级为七维风险路由，并由确定性策略文件记录理由。
4. 是否先手工运行三种协议，再开发 Orchestrator。
5. 是否确认 Web 为主控制面、Discord 为 Adapter，暂停飞书/FanBox 等并行入口。
6. 是否将 Spec Kit 首个试点限定为非交易、非 Alpha、只读校验功能。
7. 是否同意 SkillOpt 不重复安装，先用现有 Darwin + 项目评测集。
8. 是否为治理工作设置 WIP/预算上限，防止再次挤占公司主线。

## 十三、官方项目核验索引

- Superpowers: https://github.com/obra/superpowers
- GitHub Spec Kit: https://github.com/github/spec-kit
- Loop Engineering Orange Book: https://github.com/alchaincyf/loop-engineering-orange-book
- Microsoft SkillOpt: https://github.com/microsoft/SkillOpt
- Microsoft RD-Agent: https://github.com/microsoft/RD-Agent
- BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
- Task Master: https://github.com/eyaltoledano/claude-task-master
- adr-tools: https://github.com/npryce/adr-tools
- C4-PlantUML: https://github.com/plantuml-stdlib/C4-PlantUML
- Backstage: https://github.com/backstage/backstage
- Apache DevLake: https://github.com/apache/devlake
- Middleware/DORA: https://github.com/middlewarehq/middleware
- MCP Shrimp Task Manager: https://github.com/cjo4m06/mcp-shrimp-task-manager
- Plane: https://github.com/makeplane/plane
- LangGraph: https://github.com/langchain-ai/langgraph
- Temporal Python SDK: https://github.com/temporalio/sdk-python
- A2A Protocol: https://github.com/a2aproject/A2A
- LiteLLM: https://github.com/BerriAI/litellm
- Portkey Gateway: https://github.com/Portkey-AI/gateway
- Claude-to-IM: https://github.com/op7418/Claude-to-IM

核验内容限于官方定位、仓库活跃状态、README 和许可证线索；本任务没有安装或运行这些项目。文章原始链接见配套资料台账。

## 十四、执行自检

| 检查项 | 结果 |
|---|---|
| 是否覆盖 31 个链接 | 是：28 已读，3 受登录阻塞并显式记录 |
| 是否只讨论开源/工作流/路由 | 否：按公司九大能力域分析，并列出文章盲区 |
| 是否核对项目当前事实 | 是：对照 Agent Registry、Collaboration Rules、Direct Call、Discord、Tool Routing、Research Action Registry 和既有顶层报告 |
| 是否把二手文章当官方证据 | 否：关键开源结论回到官方仓库；宣传数字未直接采用 |
| 是否给出采用/拒绝边界 | 是 |
| 是否生成后续行动与验收 | 是，见配套行动包 |
| 是否改动权威治理文件 | 否，等待 Claude 验收升级 |
| 是否触碰 Holdout/预登记 | 否 |
