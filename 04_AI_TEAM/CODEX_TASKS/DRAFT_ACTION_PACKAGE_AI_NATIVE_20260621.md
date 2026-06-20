# AI-Native 调研价值转化行动包（待 Claude 验收升级）

**来源任务：** RESEARCH-AI-NATIVE-20260621  
**性质：** 提案，不自动修改项目权威计划  
**原则：** 每项必须改变一个项目决策、控制、资产或指标；没有可验证价值的调研结论不进入执行。

## 一、行动总表

| ID | 优先级 | 行动 | 公司能力域 | Owner | 前置依赖 | 验收证据 | 停止/拒绝条件 |
|---|---:|---|---|---|---|---|---|
| AV-001 | P0 | Claude 裁决 AGENTS/CLAUDE/SYSTEM_RULES/AGENT_REGISTRY 冲突 | 组织、治理 | Claude；Founder 知悉 | 本报告 + GOV-AUTO-001 | 冲突清单逐条只有一个生效规则；state_check/任务执行不再各读一套 | 不得用新增文件掩盖旧冲突 |
| AV-002 | P0 | 建立 Research-to-Value Gate 并纳入调研完成定义 | 研究、学习 | Claude 设计；Codex 实现 validator | AV-001 | 新调研能产出结构化 action；无 owner/acceptance 的报告校验失败 | 若两次试运行只增加文书且不改变决策，缩减字段 |
| AV-003 | P0 | 建公司九域一页能力地图和季度记分卡 | 战略、资本、绩效 | Claude/Founder | 公司终态与阶段裁决 | 每个在途任务可映射唯一主能力域和公司指标；暴露未覆盖域 | 不创建第二 WBS；无法驱动取舍则停用 |
| AV-004 | P1 | 将任务路由升级为七维风险路由策略 | 组织、运营、风险 | Claude 规则；Codex 模拟器 | AV-001 | 20 个历史任务回放：actor/permission/HITL 路由符合人工裁决；记录理由 | 不允许 LLM 自由路由高风险任务 |
| AV-005 | P1 | 手工运行一次普通任务闭环 | 运营、工程 | Claude + Codex | AV-001、AV-004 草案 | context hash、状态、证据、验收、下一动作完整；可中断恢复 | 任务必须低风险、非 Holdout、非资金 |
| AV-006 | P1 | 手工运行一次复杂设计辩论 | 组织、架构 | Claude 提案/裁决；Codex 反审 | DR 主题冻结 | 高严重度异议被逐条回应；最多三轮；留下 consensus/disagreement | 不用自由聊天；没有新问题时必须停止 |
| AV-007 | P1 | 建当前态 C4 L1/L2/Deployment 与首批技术 ADR | 工程、平台、治理 | Claude 主责；Codex 提供事实核查 | AV-001 | 图中 CURRENT/TARGET 分开；每容器有 owner/state；ADR 不复制业务 DEC | 不画未建设系统冒充现状 |
| AV-008 | P1 | 建最小 AI Control Plane Threat Model | 风险、安全 | Claude/Risk Reviewer；Codex 工程审查 | C4 当前态 | 覆盖 prompt injection、插件供应链、凭据、越权、消息伪造、状态篡改和恢复测试 | 不与交易策略风控混为一张表 |
| AV-009 | P2 | SQLite Orchestrator 只读/模拟 PoC | 运营、AI 协作 | Codex | AV-005/006 连续通过 | 状态机、append-only event、租约、幂等、超时、预算、verifier、HITL；重启不丢状态 | 手工协议未稳定不得开发；PoC 不写权威文件 |
| AV-010 | P2 | Spec Kit 单功能限时试点 | 工程规格 | Claude 主持；Codex 实现 | AV-001、AV-007 | 一套 spec/plan/tasks/analyze；不复制 PROJECT_TASK_PLAN；复盘有留/改/删结论 | 不用于 Alpha/预登记/公司 Constitution |
| AV-011 | P2 | Web 主控制面 + Discord Adapter | 运营、控制面 | Codex | AV-009 稳定 | Adapter 断线不影响任务；批准/停止/恢复有审计；无权限升级 | 暂停飞书/FanBox等并行入口 |
| AV-012 | P3 | 模型网关/重型编排/RAG 的触发式评估 | 工程、知识 | Claude 决定 | 达到量化触发阈值 | 有真实调用规模、失败数据和 ROI，不以流行度立项 | 未达阈值保持 OBSERVE |

## 二、Research-to-Value Gate 草案

每次调研提交以下结构，缺一不可：

```yaml
research_id: RESEARCH-...
decision_question: 本调研要改变什么决定
capability_domains: [strategy, research, platform]
sources:
  - url: ...
    evidence_grade: A|B|C|D
    date_checked: YYYY-MM-DD
    claim: ...
    limitation: ...
findings:
  - finding_id: F-001
    disposition: ADOPT|PILOT|OBSERVE|REJECT
    project_fact: 与当前项目哪个事实对应
    rationale: ...
actions:
  - action_id: AV-...
    owner: Claude|Codex|Founder|deterministic-system
    dependency: ...
    acceptance_evidence: ...
    cost_box: ...
    stop_condition: ...
authority_updates_proposed: []
unresolved_questions: []
```

**完成规则：**

- `ADOPT/PILOT` 没有 action 时失败。
- `OBSERVE` 没有重评触发条件时失败。
- `REJECT` 没有理由时失败。
- 来源无法读取却存在正文摘要时失败。
- 二手来源直接支持高风险决定且没有官方/一手核验时失败。
- action 没有 owner、acceptance 或 stop condition 时失败。

## 三、公司级一页记分卡草案

记分卡不是新任务系统，只用于每周/阶段复评时判断资源是否投向正确问题。

| 维度 | 建议指标 | 目的 | 禁止替代指标 |
|---|---|---|---|
| 资本与生存 | 可用资本、当月固定/可变成本、数据/模型成本、runway、风险预算占用 | 防止治理和工具建设无上限消耗 | token 用量高、Agent 数量多 |
| 研究组合 | 在研机制数、预登记数、有效/失败/停止、搜索次数、行动回灌率 | 看信息增益和研究纪律 | 报告篇数、回测次数 |
| 策略产品化 | 冻结规格数、paper/shadow 候选、阶段门通过率、回测-live parity 缺口 | 看研究能否进入产品链 | 代码行数、策略 idea 数 |
| 平台与数据 | 数据契约覆盖、可复现率、当前态组件健康、关键债务和 owner | 看系统是否真实可运行 | 架构图完整度、安装工具数 |
| 风险与运营 | 权限违规、对账差异、数据缺口、告警、恢复时间、未关闭高风险项 | 看事故预防和恢复能力 | 只有“没有事故” |
| AI 协作 | 任务一次验收率、返工原因、handoff 完整率、人工接管、上下文/成本、异议响应率 | 看 AI 是否真正降低总成本 | AI 生成代码占比、自动化任务总量 |
| 组织学习 | 调研行动转化率、规则/测试/ADR/Skill 回灌数、过期资产数、重复调研数 | 看知识是否改变未来行为 | 知识库文件数 |

指标需先定义口径和数据源；没有稳定事件数据时用小样本人工记录，不提前部署 DevLake/DORA。

## 四、七维风险路由策略草案

### 输入字段

```yaml
task_id: ...
decision_level: founder|company|research|architecture|implementation|mechanical
ambiguity: low|medium|high
verifier: deterministic|independent_model|human|none
reversibility: easy|moderate|hard
blast_radius: local|project|production|capital
context_scope: files|subsystem|company
permissions: [read, write_workspace, network, secrets, trade]
runtime: interactive|headless|long_running|service
budget: {tokens: ..., time_minutes: ..., usd: ...}
```

### 硬规则

1. `capital`、`trade`、公司终态或研究方向不得由自动路由器直接批准。
2. `verifier: none` 且影响面超过 local 的任务不得进入自动执行。
3. 高歧义 + hard reversibility 必须先走设计评审。
4. mechanical + deterministic verifier 优先脚本/低成本模型。
5. 长期进程必须走 launchd/VM/service，不得依赖聊天会话存活。
6. 写权威文件必须由其 owner 执行；Codex 只提交升级建议。
7. fallback 只能降低能力或转人工，不能在失败后自动扩大权限。

### 路由输出

```yaml
actor: Claude|Codex|low_tier|deterministic_system|Founder
reviewer: ...
runtime_adapter: claude_interactive|claude_headless|codex_exec|local_script|service
permission_profile: ...
workflow: task_loop|design_review|research_loop|manual_only
reason_codes: [R-HIGH-AMBIGUITY, R-CAPITAL-HITL]
```

## 五、两种手工协议

### AV-005 普通任务闭环

1. Claude 冻结任务问题、边界和验收。
2. 生成上下文文件清单与内容哈希。
3. 路由策略选择 Codex/低模型/脚本和权限。
4. 执行者每次只推进一个可验证增量。
5. 确定性检查先验收文件、schema、测试和报告完整性。
6. Claude 处理专业异议，给出 ACCEPT/REWORK/BLOCKED。
7. ACCEPT 后必须产生下一行动或“流程结束理由”。
8. 运行事实追加到事件日志；长期结论由 Claude 写权威文件。

### AV-006 设计辩论闭环

1. 固定问题和决策等级，不在辩论中偷换目标。
2. Claude 提供至少两个方案、假设、证据、失败条件和推荐。
3. Codex 在不读取 Claude 最终偏好的独立上下文中反审。
4. Claude 逐条回应高严重度问题并修订。
5. 独立检查器只检查“异议是否被回应、证据是否存在、边界是否满足”。
6. Claude 裁决并记录未解决分歧；D 级上交 Founder。
7. 最多三轮；没有新增高严重度问题或预算到顶即停止。

## 六、Strategy Governor 草案

### 固定触发

- 每完成 5 个任务或每周一次，以先到者为准。
- 阶段门、公司方向、资本分配或架构基线改变前。
- 每个研究族消耗下一次独立尝试前。

### 事件触发

- 连续 3 个局部优化任务没有新增机制证据。
- 相同失败重复 2 次且没有新信息。
- 任务数、token、时间或治理 WIP 超预算 20%。
- 权威文件冲突、状态校验假绿或人工无法解释当前优先级。
- 新工具/平台建议不能映射到公司能力缺口。

### 输出字段

```yaml
objective_being_optimized: ...
company_metric: ...
upstream_assumption: ...
evidence_gained_since_last_review: ...
cheaper_alternative: ...
opportunity_cost: ...
continue|pivot|stop: ...
next_review_trigger: ...
```

## 七、开源与工具重评触发阈值

| 候选 | 现在 | 只有达到以下条件才重评 |
|---|---|---|
| LangGraph/Temporal | OBSERVE | 自研 PoC 出现 3+ 长流程、跨进程 checkpoint、补偿事务或复杂并发需求 |
| LiteLLM/Portkey | OBSERVE | 3+ API 模型提供商；月调用成本需要统一预算/熔断；本地订阅通道不再足够 |
| A2A | REJECT NOW | 出现跨机器/跨组织、不透明 Agent 服务，需要标准发现和互操作 |
| RAG/GraphRAG/Ontology | OBSERVE | 文件元数据与全文搜索已正确，但复杂关系问题仍有可测失败率；知识规模和维护 owner 明确 |
| BMAD/Task Master/CrewAI/AutoGen | REJECT NOW | 现有 Superpowers + Spec Kit + Orchestrator 无法解决一个已量化问题，且隔离 PoC 显著胜出 |
| 飞书/FanBox | OBSERVE | Founder 明确改变入口战略，且能替代而非叠加 Web/Discord |
| SkillOpt 独立安装 | REJECT NOW | 现有 Darwin 无法覆盖明确 benchmark，且独立 SkillOpt 在隔离评测中有净增益 |

## 八、建议写入正式 RESEARCH_ACTION_REGISTRY 的条目

以下仅为草案，由 Claude 选择 ID 并写入正式台账：

| 建议条目 | 核心结论 | 行动 | 优先级 |
|---|---|---|---:|
| RA-DRAFT-01 | 调研必须通过 Research-to-Value Gate，不能只交报告 | AV-002 | P0 |
| RA-DRAFT-02 | AI 协作问题首先是权威和运行协议问题，不是模型数量问题 | AV-001、AV-005、AV-006 | P0 |
| RA-DRAFT-03 | 项目任务路由需加入风险、验证、权限、状态维度 | AV-004 | P1 |
| RA-DRAFT-04 | Skill 适合判断，确定性步骤必须写 Workflow/validator | AV-002、AV-009 | P1 |
| RA-DRAFT-05 | 状态与会话分离；持久 mission 不等于无限持久会话 | AV-009 | P1 |
| RA-DRAFT-06 | RAG/本体不是当前知识治理第一优先级 | AV-012 触发式观察 | P3 |
| RA-DRAFT-07 | Spec Kit 只做工程规格隔离试点 | AV-010 | P2 |
| RA-DRAFT-08 | Discord/飞书/微信只作 Adapter，不作权威流程核心 | AV-011 | P2 |
| RA-DRAFT-09 | SkillOpt 不重复安装，先用 Darwin + 代表性评测集 | 建 benchmark 后再评估 | P2 |
| RA-DRAFT-10 | 公司级分析必须覆盖资本、账务、风险和运营，不得被 AI coding 资料替代 | AV-003 | P0 |

## 九、推荐首个真实验证任务

**建议：** 不用 Alpha 研究，也不直接造 Orchestrator。选择“TASK_INBOX 完成事件 schema 校验器”作为第一个闭环任务：

- 边界小、可逆、无资金和 Holdout 风险。
- 能直接验证 Intent/Context/Generate/Verify/Judgment/Feedback。
- 可作为 Spec Kit 后续试点候选，但先用现有任务模板手工完成一次。
- 验收可以完全确定性：合法状态、必填字段、路径存在、时间格式、报告存在、next_task 合法、重复事件拒绝。

若该任务不能稳定完成、恢复和验收，则不应进入 Orchestrator、Discord 或多模型自动路由建设。

## 十、待补资料

3 篇小红书尚未获得正文。Founder 可选择：

1. 明确授权 Codex 使用已登录 Chrome 读取这 3 个链接；或
2. 提供截图/正文；或
3. 接受本轮以 28 篇微信文章为完成范围，3 篇保持 BLOCKED 并在后续补录。

在正文取得前，不给这 3 篇分配标题、观点或行动，避免把链接主题凭空补全。
