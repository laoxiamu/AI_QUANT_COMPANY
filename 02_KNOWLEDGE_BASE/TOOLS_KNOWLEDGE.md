# 工具/能力/插件知识库

**定位：** 项目所有工具调研、能力审计、插件评估的综合"已知结论"。避免重复调研同一工具。  
**使用规则：** 引入新工具前必读本文件。有新调研结论当轮写入，不存在"下次补"。  
**调研来源（8份，2026-06-04至06-19）：**
- EXTERNAL_RESEARCH_REPORT_v1（06-04）
- V5_TOOL_INTEGRATION_PLAN_v1/v2
- TOOL_RESEARCH_BRIEF_v1（06-06）
- AI_CAPABILITY_TOOLING_AUDIT_v1（06-08）
- AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12
- PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12
- CODEX_SKILLS_INSTALL_LOG_2026-06-14
- OSS_BUILD_VS_BUY_2026-06-15（唯一真正落地的）

**最后更新：** 2026-06-20

---

## 一、已决策、已落地的工具（不再讨论）

| 工具 | 决策 | 用途 | 来源 |
|---|---|---|---|
| Freqtrade | Phase 1 借力首选 | dry-run/回测/最小闭环；**只学lookahead检测和控制面，禁用hyperopt** | OSS_BUILD_VS_BUY |
| CCXT | Phase 1 采用 | 统一交易所REST/WS薄适配层 | OSS_BUILD_VS_BUY |
| vectorbt | 研究加速 | 批量参数扫描；不用于实盘/风控 | OSS_BUILD_VS_BUY |
| Binance 官方REST | 数据主管道 | funding/OI/klines；data.binance.vision历史 | OSS_BUILD_VS_BUY |
| NautilusTrader | Phase 2候选 | 生产级事件驱动；现在引入太重 | OSS_BUILD_VS_BUY |
| Desktop Commander | Mac主执行通道 | 本地脚本/Codex CLI直调 | 运行中 |
| WebSearch | 外部研究 | 文献/行业/竞品 | 已有但**用得极少** |

---

## 二、已调研、已建议、从未执行的高优先级项

### ⚠️ 项目级Claude Skill（2026-06-20更新）

来源：AI_CAPABILITY_TOOLING_AUDIT_v1（06-08）——最高杠杆、免费、直接降本。

| Skill名称 | 状态 | 路径 |
|---|---|---|
| **result-intake** | ✅已建（2026-06-20） | `.claude/skills/result-intake/SKILL.md` |
| **codex-task-spec** | ✅已建（2026-06-20） | `.claude/skills/codex-task-spec/SKILL.md` |
| **research-harvest** | ✅已建（2026-06-20） | `.claude/skills/research-harvest/SKILL.md` |
| **hypothesis-preregister** | ❌待建 | — |
| **state-sync** | ❌待建 | — |

**Holdout硬门控：** ✅已建（2026-06-20）`.claude/hooks/protect-holdout.py`

### ⚠️ 14个Codex Skills已安装，从未在任务书里指定使用（仍未解决）

### ⚠️ 14个Codex Skills已安装，从未在任务书里指定使用

来源：CODEX_SKILLS_INSTALL_LOG_2026-06-14。**CTO级盲区（2026-06-20确认）**：之前能力升级方案只看Claude端，完全忽略Codex端14个Skills——安装了但0利用率=安装前。

**即将任务的Codex Skill映射（强制指定，不得用默认）：**

| 即将任务 | 应指定Skill | 原因 |
|---|---|---|
| carry数据采购（8个缺失输入） | `PlanToDelivery` | 多步骤交付：下载→验证→格式化→文件写入，需完整交付闭环 |
| carry feasibility代码实现 | `tdd` | 有测试才能信任结果；数值计算脚本没有测试等于不可信 |
| carry scaffold架构评估 | `improve-codebase-architecture` | 在加功能前先评估当前结构是否合理 |
| 文件归档（REORGANIZE-ARCHIVE-001） | `PlanToDelivery` | 机械多步骤操作，需要交付清单和验收 |
| 采集器bug排查 | `diagnose` | 系统性诊断流程，防止"重启+观察"的表面修法 |
| 任何新研究假设实现 | `tdd` + `nuwa`（风险审查） | TDD写代码+女娲扮演"挑剔的风险审查员" |

**下一次派Codex任务时，任务书中必须指定使用哪个Skill。** 否则Codex用默认行为，等于浪费安装成本。

### ⚠️ Triple Barrier / Meta-Labeling 已调研，从未引入

来源：TOOL_RESEARCH_BRIEF_v1（06-06）。López de Prado方法论是为解决金融ML中过拟合/标签质量问题的标准方法。

- **Triple Barrier Method**：比固定持仓期更合理的事件标签——上轨/下轨/时间轨三个出口，适合carry这类有强平风险的策略
- **Meta-Labeling**：先有基础模型给方向，再用ML模型决定是否执行——适合carry信号+OI过滤的两层架构
- **Purged/Embargo CV**：防止carry回测中样本内外数据泄漏

**当前状态：** carry v4用的是固定时间窗口验收，不是Triple Barrier。v4设计已冻结，但下一个策略引入时应考虑。

### ⚠️ Freqtrade lookahead-analysis 从未使用

来源：PEER_PROJECTS_BENCHMARK_2026-06-12。Freqtrade有专门命令检测回测脚本的前视偏差：
```bash
freqtrade lookahead-analysis --strategy YourStrategy
```
carry feasibility脚本在运行前应过此检测，或等效地做"切片复算"。已在RESEARCH_ACTION_REGISTRY登记（RA-003）但从未执行。

---

## 三、已评估、明确否决的工具

| 工具 | 否决原因 | 日期 |
|---|---|---|
| 外部云记忆（Mem.ai等） | DEC-061：记忆留repo，不引云端黑箱 | 06-08 |
| 交易执行类MCP | Phase 1安全边界，MCP不进交易闭环 | 06-08 |
| Hyperopt（Freqtrade参数优化） | 容易诱导过拟合，与"禁止改参数→回测"方向矛盾 | 06-12 |
| ClawHub Skill市场（部分） | D38：341个恶意加密Skill风险，未审计不装 | 06-06 |
| 定时任务做Claude-Codex进度同步 | Founder否决，定时方案费额度且傻 | 早期 |
| Obsidian（知识图谱可视化） | 解决"难导航"不解决"结论没写进去"；vault需额外同步维护；当前知识库刚建，条目个位数，不到使用门槛；Phase 2+可重新评估 | 06-20 |
| alphaXiv/Elicit/Tavily MCP（研究搜索） | 当前项目不被研究能力阻塞，被数据采购和协作机制阻塞；推荐这三个是受对话上下文引导的局部最优错误；carry可行性跑起来进入新机制研究阶段后再评估 | 06-20 |

---

## 四、待评估（有调研记录，尚未决策）

| 工具 | 调研来源 | 待决策的问题 |
|---|---|---|
| CoinGlass API | OSS_BUILD_VS_BUY | 强平历史数据是否是A-1路径B的必需？价格/覆盖是否值得？需用真实key做1天抽样再决定 |
| Exa MCP（增强搜索） | AI_CAPABILITY_TOOLING_AUDIT | 已有WebSearch时是否值得？研究密集期再评估 |
| LunarCrush（社交情绪） | AI_CAPABILITY_TOOLING_AUDIT | 仅当positioning机制立项时再评估；现在不需要 |
| Jesse框架 | PEER_PROJECTS_BENCHMARK | Monte Carlo能力有价值；但当前不是优先，Freqtrade先用够 |
| Qlib实验记录器 | PEER_PROJECTS_BENCHMARK | 概念值得学（实验ID+参数+结果结构化存储）；是否自实现一个轻量版？ |

---

## 五、Claude自身能力中未充分使用的

| 能力 | 现状 | 应该用在哪里 |
|---|---|---|
| **WebSearch** | 几乎未用 | carry机制文献搜索、竞品方法论、当前funding rate市场结构 |
| **workspace bash** | 偶尔用 | ≤50行分析脚本直接跑，不必全派Codex |
| **mcp-builder Skill** | 从未用 | 建CoinGlass MCP、Binance carry数据MCP |
| **skill-creator Skill** | 从未用 | 建上述5个项目级Skill |
| **Claude subagents** | 从未用 | 把重搜索/日志分析放独立窗口，防主上下文漂移 |
| **Claude hooks** | 从未用 | 把"禁读Holdout"从软规则变硬门控 |

---

## 六、工具使用路由（快速决策）

```
新研究任务？
  → 查 RESEARCH_ACTION_REGISTRY 有无相关结论
  → 查 CARRY_KNOWLEDGE.md（如果是carry相关）
  → 不超50行脚本 → Claude直接跑（workspace bash/DC）
  → 超50行/多文件 → Codex任务书（指定使用哪个Codex Skill）

引入新工具？
  → 先查本文件§三（是否已否决）
  → 查§四（是否已调研待决策）
  → 否则走完整调研流程，结论当轮写入本文件

数据问题？
  → 查 CAPABILITY_ENV_REGISTRY.md §4（Binance数据边界）
```

---

*TOOLS_KNOWLEDGE.md 是活文件。新调研/新决策当轮更新。下次工具相关任务开工前必读。*
