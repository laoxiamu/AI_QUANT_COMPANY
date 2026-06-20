# AI-Native / Agent / OPC 资料台账（2026-06-21）

**任务号：** RESEARCH-AI-NATIVE-20260621  
**范围：** Founder 提供的 31 个链接  
**获取结果：** 28 篇微信公众号正文已读取；3 篇小红书正文因缺少登录态未取得  
**证据规则：** 公众号文章默认是二手资料（C 级），只能形成候选机制；开源项目结论须回到官方仓库核验；无法读取的资料不得推断补全。

## 一、分类索引

| 主题 | 文章编号 | 主要问题 |
|---|---|---|
| 战略、OPC 与 AI-native 公司 | W08、W13、W24、W26、W27 | 小团队如何验证需求、形成闭环、保持盈利和沉淀组织能力 |
| 组织、管理与决策权 | W09、W16、W21、W23、W27 | 负责人、Agent、人工判断和持久角色如何分工 |
| 任务规格与研发流程 | W01、W05、W20 | 如何把意图变成边界清楚、可验证、可回滚的任务 |
| Harness、上下文与大型项目 | W03、W07、W14、W17、W19 | 规则、工具、上下文、观测、安全和生产工程如何组合 |
| Loop 与确定性 Workflow | W06、W11、W12、W15、W28 | 状态、生成、验证、记录、退出和恢复如何闭环 |
| 多 Agent、子代理与路由 | W10、W21、W23 | 角色、权限、上下文隔离、交接和运行形态如何选择 |
| 记忆、知识与本体 | W02、W25、W27 | 短期/工作/长期记忆、治理、关系和判断资产如何管理 |
| 控制面与办公入口 | W04、W22 | 微信/飞书等入口如何连接 Agent，但不成为权威状态源 |
| Skill 优化与组织学习 | W18、W27 | 如何用评测门优化 Skill，如何把隐性判断变成可复用资产 |

## 二、逐篇摘要与项目判断

| ID | 标题 | 核心内容 | 对 AI_QUANT_COMPANY 的价值判断 |
|---|---|---|---|
| W01 | Codex 干活总翻车？先学拆任务 | 健康任务应小、边界清楚、可验证、可逆；从验证目标逐层拆到 0.5-2 小时增量；一个任务只做一种改变。 | **采用机制。** 升级任务包质量门，补充“验证什么、禁止什么、证据是什么”；不能把所有公司工作都切成局部任务，需配 Strategy Governor。 |
| W02 | Agent 记忆系统 | 短期记忆服务当前任务，工作记忆保存目标/计划/约束，长期记忆保存事件/知识/经验，治理层负责 TTL、权限、审计和脱敏。 | **采用分层原则。** 当前项目文档很多但层级与权威关系混杂；先做来源、TTL、权威性和写入条件，不急于上向量库。 |
| W03 | Claude Code 大型项目最佳实践（卡片） | 大仓库效果取决于 CLAUDE.md、Hooks、LSP、Skills、Plugins 和上下文配置，而非只换模型。 | **方向成立，证据较弱。** 用于核对 harness 缺口，不据此安装全部组件。 |
| W04 | FanBox 2.0 | 用微信远程操作 Claude Code/Codex、感知终端、保持 Mac 任务运行，定位为 coding agent 驾驶舱。 | **仅观察入口层。** 可借鉴移动控制面，但不允许其直接扩大沙箱或接触交易/资金；与 Discord/Web/Lark 不能并建多个控制面。 |
| W05 | AI Coding 研发体系（二） | AI 进入研发不是替换写代码，而是 Intent -> Context Package -> Generate -> Automated Verification -> Human Judgment -> Feedback Assets；验证应先设计。 | **高价值采用。** 直接作为任务生命周期骨架；反馈必须回灌模板、测试、规则或知识，不得只留聊天。 |
| W06 | Loop Engineering 橙皮书 | 从 prompt/context/harness 上移到循环系统；发现、交付、验证、记录、决定下一步；生成者不能自评；强调验证债、理解衰减、成本和认知让渡。 | **采用方法，不安装平台。** 转化为本项目 Loop Contract；官方仓库已核验，MIT。 |
| W07 | ClaudeCode Harness 搭建指南 | 五组件：规则、agents、skills、workflow、workspace；先定义目标和重复任务，再设计角色与流程，最后生成文件。 | **采用建设顺序。** 项目过去先堆文件后补运行机制，应改为“需求/失败模式驱动 harness”。 |
| W08 | Anthropic 一人公司 Playbook（二手解读） | Idea -> MVP -> Launch -> Scale；先验证需求，AI 成为团队成员，真实反馈形成迭代，规模阶段靠数据与工作流形成壁垒。 | **用于公司阶段门，不作官方事实。** 项目应把“研究产出”连接到可验证公司价值，而不只累计文档与实验。 |
| W09 | AI-Native 工程团队管理实践 | 负责人要亲自使用 Agent；技术争论可用可运行方案对比；信任但验证；代码、规格、ADR 和清洁提交提升 AI 可导航性。 | **采用组织原则。** Claude 保持问责与裁决，但不能成为搬运/轮询瓶颈；管理指标看可靠性、返工和周期，不看 AI 生成代码占比。 |
| W10 | Claude Code 子代理完全指南 | 子代理用描述、模型和工具权限路由；适合上下文隔离与专门角色；应最小权限、显式交接，避免过度拆分。 | **部分采用。** 用于研究检索、日志阅读、独立审查；权威更新和复杂裁决不能下放。文章中的具体能力上限需以官方版本核验。 |
| W11 | 周报 Skill 切成 Workflow | 软性 Skill 会漏步骤；确定性部分应写成代码硬门，判断留给人/模型；结构化 schema、覆盖检查、内容哈希、固定数据源和内部重试提高可靠性。 | **最高价值之一。** 项目当前大量规则仍是软文本；优先把任务包、完成事件、证据完整性、状态同步做成确定性校验。 |
| W12 | Loop Engineering：用循环驱动智能体 | 调度器决定下一步，独立检查器评分，文件/图谱保存共享状态；状态在磁盘而非上下文；不同模型复核；需退出条件和成本控制。 | **采用。** 与本项目 Orchestrator 方向一致；Discord 只能是适配器，后台状态机才是核心。 |
| W13 | 打造 AI Native 公司的行动指南（YC 二手解读） | 组织应成为闭环、可查询、以产物为中心；人定义目标并判断，Agent 执行；保留清晰 DRI；重要行动产生可追溯资产。 | **采用闭环/DRI，不采用“最大化 token”口号。** 项目需要结果到知识、知识到下一任务的价值链，并加预算上限。 |
| W14 | Claude Code 大型项目最佳实践 | 建议按 CLAUDE.md、Hooks、Skills、Plugins、LSP、MCP、Subagents 分层；大仓库依赖即时检索和正确上下文。 | **选择性采用。** 当前先解决规则冲突、检索入口和 hook 门禁，不按清单全装。 |
| W15 | Claude Code/Codex 可靠 Loop | 五拍 Orient -> Plan -> Act -> Verify -> Record；每轮一个增量；状态外置、原子记录、幂等续跑；完成/阻塞/硬上限三类停止条件；防止改测试过关。 | **直接采用为运行合同。** TASK_INBOX 需升级为可恢复状态与事件，而不仅是完成通知文件。 |
| W16 | Anthropic 如何管理 AI-native 工程团队（二手解读） | 管理者亲自 dogfood；用多个可运行 PR 化解争议；保留动态人工审查清单；合规、安全、产品品味由人负责；淘汰噪声流程和虚荣指标。 | **高价值采用。** Claude 裁决必须书面回应高严重度异议；人工审查范围要定期增删，不应永久依赖直觉。 |
| W17 | 生产级人工智能系统架构（卡片） | 生产 AI 不只有模型，还包括推理成本、上下文、工具调用、检索记忆、评估观测、安全可靠性。 | **仅作检查表。** 内容不完整且偏通用 AI 服务；本项目更急的是 Agent 运行观测、权限、恢复和交易系统 SRE。 |
| W18 | 微软 SkillOpt | 用 rollout -> reflect -> aggregate -> select -> update -> evaluate 优化 Skill；验证集门控，只接受更好版本，输出可部署 skill。 | **不重复安装。** 官方仓库 MIT，项目现有 Darwin Skill 已集成其思想；只有建立代表性评测集后才允许优化，防止对历史任务过拟合。 |
| W19 | 智能体系统失败根源：工程化债务 | 技术、运营、评估、集成、治理五类债务；需 schema、重试、fail-fast、owner、健康指标、评测集、契约、HITL 和不可变审计。 | **采用债务分类。** 用于公司 AI 风险台账和 Orchestrator 验收，不另建泛化框架。 |
| W20 | CLAUDE.md 错误率大幅下降（二手文章） | 提倡先思考、保持简单、外科式修改、目标驱动、确定性决策写代码、预算、冲突显式化、读后写、检查点、响亮失败；警告规则过长。 | **采纳原则，拒绝未经核验的 41%/3% 数字。** 当前 CLAUDE/AGENTS 重复且冲突，规则应映射真实失败并转为 workflow/hook。 |
| W21 | 多 Agent 如何进入真实研发 | 多 Agent 价值来自角色边界、输入输出、权限、交接和验证；建议 PM/架构/编码/审查/QA/Ops 角色；不清楚、影响扩大、验证失败、合并前人工接管。 | **采用契约，不照搬角色数量。** 一人公司要少角色、多视角；同一 Agent 可在隔离会话中承担不同角色，但决策权必须唯一。 |
| W22 | Codex + 飞书 CLI + 27 办公 Skills | 把文档、表格、邮件、知识库等飞书能力聚合为插件/Skills，形成办公工作台和自动化链路。 | **借鉴插件聚合，不引入第二控制面。** 飞书适合文档/协作，但当前项目已选 Web + Discord 方向；除非 Founder 改变入口战略，否则只观察。 |
| W23 | Claude Code 持久子代理 | 持久领域 Agent、临时噪声 Agent 和薄协调层；resume/fork/fresh 按任务选择；会话上下文持续增长，应定期交接重建。 | **采用冷热 Agent 分层思想。** 权威状态必须在文件/事件库；不能把可恢复 session 当长期记忆，文中实验能力需官方核验。 |
| W24 | AI Agent x OPC x 自媒体地图 | 工具、商业模式、渠道三维；认知、工具、流程、运营、战略五阶段；标准化工作交 AI，人保留观点、经历、判断和连接。 | **只借鉴 OPC 能力分层。** 自媒体渠道与量化公司主线关联弱，不应转化为当前项目任务。 |
| W25 | RAG 的下一步：本体 | 向量 RAG 处理文本知识但难表达实体关系、约束和多跳推理；GraphRAG/ontology 用结构和规则提高检索与推理。 | **观察，不建系统。** 项目当前问题是权威冲突和元数据缺失，不是检索技术不足；先做轻量实体/关系/来源字段，达到规模门槛再评估图谱。 |
| W26 | 《小而美》极简创业指南 | 优先盈利、自主与可持续；从社区找真实需求，用极简 MVP、100 个核心客户、私域、控成本和节制扩张构建小公司。附带的 10 个 Skill 未提供可审计正文。 | **采用经营原则，不采用未知 Skill。** 对应资本 runway、固定成本、阶段门和“不过度建设”；项目仍需量化交易特有的资本/风险框架。 |
| W27 | AI Native 的管理副产品 | 工作流中的判断沉淀为 Skill，工具连接与 Skill 组合成 Plugin；组织知识从个人经验变为可复用、可对齐的运行资产。 | **采用知识资产观点。** 但 Skill 不是权威事实库；判断需来源、版本、owner、适用边界、评测和废弃机制。 |
| W28 | Loop Engineering 重塑 AI 工程 | 状态机、自动反馈、观测和容错构成循环；从小循环开始，状态优先于 prompt，管理不确定性，需要跨职能定义评估。 | **采用总结，不新增工具。** 可作为 Orchestrator PoC 的原则性检查表。 |

## 三、未取得正文的 3 篇小红书

| ID | 链接 | 当前状态 | 处理规则 |
|---|---|---|---|
| X01 | https://www.xiaohongshu.com/explore/6a22c63f000000003501ec12 | BLOCKED：x-reader 无登录态；公开页面返回“页面不见了” | 等 Founder 明确授权使用已登录 Chrome，或提供截图/正文后补录 |
| X02 | https://www.xiaohongshu.com/explore/6a3241f10000000011017308 | BLOCKED：同上 | 同上 |
| X03 | https://www.xiaohongshu.com/explore/69d9f710000000001f0070ac | BLOCKED：同上 | 同上 |

## 四、证据限制

1. 文章高度集中于 2026 年 AI coding/Agent 热点，存在互相转述和营销放大的相关性，不能把“多篇一致”误当独立证据。
2. W03、W04、W07、W08、W17 为短卡片或摘要，信息完整性低。
3. W18 的效果数字仅在官方仓库/论文层面记录，本任务不复现实验，因此不把提升比例用于项目 ROI 承诺。
4. 这些资料几乎不覆盖量化研究统计有效性、实时交易风控、资本账务、监管与事故响应，不能据此定义完整公司架构。
5. 任何需要落地的开源组件，仍需独立做许可证、维护活跃度、权限面、数据出境、成本和退出方案核验。

## 五、微信公众号原始链接

| ID | 标题 | 原始链接 |
|---|---|---|
| W01 | Codex 干活总翻车？先学拆任务 | https://mp.weixin.qq.com/s/xUzFcKFustVwKaSpV8zOkQ |
| W02 | Agent 记忆系统 | https://mp.weixin.qq.com/s/YEftn6f-ddT0gnQglflmZA |
| W03 | Claude Code 大型项目最佳实践（卡片） | https://mp.weixin.qq.com/s/8h1KBzb_NUp0Jw9lFJsOAQ |
| W04 | FanBox 2.0 发布 | https://mp.weixin.qq.com/s/EZcaSDTe6FoiaczAtqcYXw |
| W05 | AI Coding 研发体系（二）：AI 如何进入研发流程 | https://mp.weixin.qq.com/s/TfS3Hmo28vZFanpZESKVtw |
| W06 | Loop Engineering 橙皮书发布 | https://mp.weixin.qq.com/s/KukCs9yg_8YJdnayUui-hg |
| W07 | ClaudeCode Harness 搭建指南 | https://mp.weixin.qq.com/s/U-K0okyqm6PPJBYGuFvB9g |
| W08 | Anthropic 下场教你如何做一人公司 | https://mp.weixin.qq.com/s/R7rw5kz32zUY24RbObBCrA |
| W09 | 打造 AI-Native 工程团队 | https://mp.weixin.qq.com/s/KKmwop73kmDIbPDVAlI_nQ |
| W10 | Claude Code 子代理完全指南 | https://mp.weixin.qq.com/s/jWVWm8kL4x-mf_fB3oh-SA |
| W11 | 我把一个周报 Skill 切成了 Workflow | https://mp.weixin.qq.com/s/Xub4C2gVx3M2_zN5n99zYQ |
| W12 | Loop Engineering：用循环驱动智能体 | https://mp.weixin.qq.com/s/mueHtDJ067-AOf6p1VdOww |
| W13 | 打造 AI Native 公司的行动指南 | https://mp.weixin.qq.com/s/sYuW4gDJPaK1JssaSL9K_w |
| W14 | Claude Code 在大型项目中的最佳实践 | https://mp.weixin.qq.com/s/QfmXF5caPESBvs2Gqkhijw |
| W15 | 在 Claude Code/Codex 里写可靠 Loop | https://mp.weixin.qq.com/s/H0Izaab6O6pIUByr_GBvzA |
| W16 | Anthropic 如何管理 AI-native 工程团队 | https://mp.weixin.qq.com/s/Ip3wVHBFDtCha-tCk9zMIQ |
| W17 | 生产级人工智能系统架构设计 | https://mp.weixin.qq.com/s/YCaAigKb2EzUpVCH9Ap5Aw |
| W18 | 微软开源 SkillOpt | https://mp.weixin.qq.com/s/3pMDNUflL9Xr-9KaNym5uQ |
| W19 | 智能体系统失败的根源：工程化债务 | https://mp.weixin.qq.com/s/-1N6CEcmMYQMxmjge4tEhQ |
| W20 | CLAUDE.md 错误率宣传文章 | https://mp.weixin.qq.com/s/hCSPHxZ316N2qZP8YpuqJw |
| W21 | 多 Agent 协作如何进入真实研发任务 | https://mp.weixin.qq.com/s/cEnjCES0XGx8uGOrZxniRQ |
| W22 | Codex + 飞书 CLI + 27 个办公 Skills | https://mp.weixin.qq.com/s/4QNyP4fncciSmqfnzAZ7hw |
| W23 | Claude Code 持久子代理 | https://mp.weixin.qq.com/s/kuXfrr21ezD_dlFe2v-XRA |
| W24 | AI Agent x OPC x 自媒体认知地图 | https://mp.weixin.qq.com/s/vrqelEY8dsww60P_NuwSRg |
| W25 | RAG 的下一步：本体 | https://mp.weixin.qq.com/s/BJ6zqQrEhukcVpc4nmcwXw |
| W26 | 《小而美》一人公司极简创业指南 | https://mp.weixin.qq.com/s/7F0FKlNXto_t0JDdZ13k2w |
| W27 | AI Native 工作流中长出的管理资产 | https://mp.weixin.qq.com/s/fm1JMIZn468UjBqLdA1LqA |
| W28 | Loop Engineering 如何重塑 AI 工程化 | https://mp.weixin.qq.com/s/hAJLK1u-t6ydpNzGwXyMAQ |
