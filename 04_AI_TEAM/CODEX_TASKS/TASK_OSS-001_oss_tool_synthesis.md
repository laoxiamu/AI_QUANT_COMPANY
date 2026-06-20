# Codex任务书：OSS工具综合调研 —— carry + 1个月实盘路线可借鉴项目矩阵

**任务ID：** OSS-001  
**对应项目任务：** P1-OSS-001前置研究  
**优先级：** P1（与DATA-001并行，互不干扰）  
**创建时间：** 2026-06-20  
**预估规模：** 只读扫描 + 一份报告，约300行  
**指定Codex Skill：** `research-harvest`（多文件扫描提炼）+ `diagnose`（识别遗漏和矛盾）  
**沙箱模式：** workspace-write（只写报告文件，不改任何已有文件）

---

## 背景与目的

项目已决策走 Freqtrade + CCXT + data.binance.vision 的最小借力闭环（DEC-076，2026-06-20），目标1个月内进小额实盘（DEC-077）。

项目历史上做过**多轮独立的OSS/工具/框架调研**，分散在多个文件中，从未做过系统整合。当前决策（DEC-076）主要基于 `OSS_BUILD_VS_BUY_2026-06-15.md`，但至少还有以下文件未被折入：

- `00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_REPORT_v1.md`
- `00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md`
- `00_PROJECT_MANAGEMENT/AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12.md`
- `00_PROJECT_MANAGEMENT/AI_CAPABILITY_TOOLING_AUDIT_v1.md`
- `00_PROJECT_MANAGEMENT/AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12.md`
- `00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v1.md`（v2已读，v1未读）
- `00_PROJECT_MANAGEMENT/CAPABILITY_ENV_REGISTRY.md`
- `00_PROJECT_MANAGEMENT/FRONTIER_AI_OPC_AGENT_GOVERNANCE_RESEARCH_2026-06-12.md`
- `00_PROJECT_MANAGEMENT/BPR_TOP_LEVEL_FRAMEWORK_REFERENCE_2026-06-15.md`
- `03_RAW_INBOX/STATUS_RECORDS/D38：工具集成评估报告.md`
- `00_PROJECT_MANAGEMENT/TOOL_ROUTING.md`
- `00_PROJECT_MANAGEMENT/AI_CAPABILITY_BASELINE.md`
- `02_KNOWLEDGE_BASE/TOOLS_KNOWLEDGE.md`（已有总结，但需核对有无遗漏）

**本任务目的：** 从上述所有文件中提取与以下三个问题直接相关的结论：

1. **carry策略实现参考**：有无开源项目实现了funding rate arbitrage / delta-neutral carry？可借鉴哪些设计（参数、触发逻辑、对冲结构）？
2. **1个月实盘路线加速器**：有无工具/框架能缩短carry从FEASIBILITY-LOCK→dry-run→实盘的路径？
3. **DEC-076遗漏项**：有无重要OSS工具/方法被DEC-076和TOOLS_KNOWLEDGE遗漏，值得现在纳入？

---

## 研究约束（强制继承）

- 禁止读取 `~/.aiquant_sealed/` 下任何文件
- 禁止修改任何已有文件（只读扫描）
- 结论必须按"现在可用 / Phase 2 / 明确跳过"三档分类，不得给开放性建议
- 已在DEC-076/TOOLS_KNOWLEDGE中明确决策的工具，只需注明"已决策"，不重新论证
- 如发现与DEC-076冲突的结论，标注冲突点，不自行裁决

---

## 具体扫描任务

### Step 1：扫描所有待读文件

对每个文件，提取：
- 文件性质（研究报告/工具调研/审计/方向分析）
- 涉及的OSS工具/框架/方法（列名）
- 与carry策略或1个月实盘路线的直接相关性（高/中/低/无）
- 有无被TOOLS_KNOWLEDGE/DEC-076覆盖（是/否/部分）

### Step 2：专项提取——carry策略参考

重点搜索以下关键词：
- "funding rate arbitrage"、"carry"、"delta neutral"、"delta-neutral"
- "Hummingbot"中的具体策略实现（尤其 Funding Rate Arbitrage bot）
- "Jesse"中的carry/funding相关能力
- 任何提到funding套利的开源实现

对命中项：提取具体设计细节（entry条件、exit触发、对冲逻辑、已知风险），写入报告"carry参考"节。

### Step 3：专项提取——1个月实盘路线加速器

搜索以下关键词：
- "dry-run"、"paper trading"、"live trading"、"实盘"
- "lookahead"、"lookahead-analysis"（前视偏差检测工具）
- "Monte Carlo"、"path simulation"（稳健性测试）
- "data contract"、"schema validation"（数据层质量保证）
- 任何能在Freqtrade集成中直接使用的工具/命令

### Step 4：构建决策矩阵

输出格式：

| 工具/方法 | 来源文件 | 与carry/实盘相关性 | DEC-076状态 | 建议 | 理由 |
|---|---|---|---|---|---|
| {工具名} | {文件名} | {高/中/低} | {已覆盖/遗漏/冲突} | {立即用/Phase2/跳过} | {一句话} |

---

## 输入文件（必读）

主要待扫描文件（上述列表）+ 对照文件：
- `02_KNOWLEDGE_BASE/TOOLS_KNOWLEDGE.md` — 已有决策（作对照，避免重复）
- `00_PROJECT_MANAGEMENT/STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md` — DEC-076依据（作对照）
- `00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v2.md` — 已有矩阵（作对照）
- `00_PROJECT_MANAGEMENT/PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12.md` — 已有对标（作对照）

---

## 输出产物

- `04_AI_TEAM/CODEX_TASKS/REPORT_OSS-001_oss_tool_synthesis.md` — 综合报告（必须）

报告结构：
```
## 执行摘要（3-5行：发现了什么DEC-076遗漏、carry参考有哪些、最高价值立即行动是什么）
## 文件扫描汇总（每个文件一行：性质/主要发现/相关性/是否已覆盖）
## carry策略开源参考（重点节：funding arbitrage实现细节提取）
## 1个月实盘路线加速器（重点节：可立即用的工具/命令/方法）
## 决策矩阵（完整表格）
## 对TOOLS_KNOWLEDGE.md的更新建议（具体指出新增哪些条目）
## 与DEC-076的冲突或补充（如无则写"无冲突"）
## 建议下一步（Claude验收后立即可以执行的3件事，按优先级）
```

---

## 禁止项

- 禁止修改任何现有文件
- 禁止读取 `~/.aiquant_sealed/` 下任何文件
- 禁止在报告里只列工具名不给判断（每项必须有"建议"和"理由"）
- 禁止重新论证DEC-076已明确否决的工具（如CoinGlass、自建重型平台）
- 禁止建议引入任何付费工具（DEC-076约束：免费工具链）

---

## 验收标准（Claude验收）

- [ ] 所有列出的待扫描文件都在"文件扫描汇总"中出现（即使是"内容与本任务无关"也要说明）
- [ ] "carry策略开源参考"节存在，且含Hummingbot funding arbitrage的具体设计提取（如有）
- [ ] 决策矩阵含"DEC-076状态"列（已覆盖/遗漏/冲突）
- [ ] 报告末尾有"对TOOLS_KNOWLEDGE.md的更新建议"（即使是"无需更新"也要说明）
- [ ] 报告末尾有"建议下一步"，3件事按优先级排列

---

## Codex执行说明

**重要：** 本任务与DATA-001并行运行，两者写入不同目录，互不干扰。

本任务是**纯读取+报告写入**，不修改任何现有文件，可安全并行。
