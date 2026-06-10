# AI 团队能力 / 工具审计 v1（结合本项目）

**作者：** Claude（CEO/CTO）
**日期：** 2026-06-08
**状态：** CTO 审计 + 推荐，待 Founder 选装
**触发：** Founder 要求重做能力审计（上次 V5_TOOL_INTEGRATION 只盘量化库，没盘 Claude/Codex 自己的"操作工具"）
**口径：** 按三类筛——**省 token / 加自动化 / 补能力**；不引不可审计黑箱（DEC-061）。

---

## A. 当前已装（基线）

- **Skills：** docx/pdf/pptx/xlsx（出报告/表格）、schedule（定时任务）、**skill-creator（关键：自研 skill）**、consolidate-memory（记忆整理）、cowork-plugin-management（把工作流打包成插件）。
- **MCP/工具：** Context7（已接，给 Codex 查最新库文档）、Desktop Commander（Mac 本地执行 + 直调 Codex CLI 的通道）、x-reader+Playwright（内容抓取）、scheduled-tasks（月审/周监控已建）、WebSearch/web_fetch、computer-use。
- **判断：** 基线够用，缺口主要在"自研流程 skill"和"外部研究/数据接入"。

---

## B. 建议接入的 MCP（注册表扫描结果，按优先级）

| MCP | 用途 | 评级 | 建议 |
|---|---|---|---|
| **Exa**（Web Search + 代码文档搜索）| 强化外部研究/知识摄取（喂机会地图）| 中高 | 可选接入；现有 WebSearch 够用时不强求，研究密集期接 |
| **CoinDesk**（实时+历史加密数据/指数）| 现货/指数 OHLCV/orderbook/trades | 中低 | 低优先——核心需要的是**永续+funding+OI**，CoinDesk 偏现货/指数，我们自有 ccxt+binance.vision 管线已覆盖 |
| **LunarCrush**（加密社交情绪数据）| 若做"拥挤/情绪"机制可作另类数据 | 低/延后 | 仅当 positioning 机制立项时再评估，社交数据噪声大 |
| 外部记忆类（Mem.ai 等）| 云端笔记/记忆 | **否决** | 与 DEC-061 一致：记忆留在 repo、文件式、单一权威，不引云端黑箱 |

> 无专门的 Binance 永续/funding/OI 的 MCP——这块继续用自有 Python 管线，不依赖第三方 MCP。

---

## C. 自研 skill（**最高杠杆、免费、直接降本+少卡壳**）

用 skill-creator 把项目里反复做、且每次重新推导的流程固化。这正好打中我们这几轮的痛点（状态滞后、token 烧、每对话重解释）：

| 自研 skill | 解决什么 | 价值 |
|---|---|---|
| **boot-brief** | 生成精简启动简报，替代每次读巨型 CURRENT_STATE/DECISION_LOG | 省 token（最大单项）|
| **state-sync** | 一键同步 CURRENT_STATE + DECISION_LOG，防滞后 | 治本"权威状态失真"（Codex P0）|
| **hypothesis-preregister** | 按模板生成预登记（强制含失效条件/门槛/单变量/样本档级）| 防数据窥探、少卡壳 |
| **codex-task-spec** | 生成 Codex 任务规格（目标+约束+验收+禁止项+路径）| handoff 标准化、可自动化 |
| **result-intake** | 接收 Codex 回报：红队清单+档级判定+失败计数+归档 | 验收标准化 |

> 这五个建好后，每轮研究的"搬运/推导"成本大降，是"丝滑长跑"最直接的投资。归会话3 AI 能力轨，但可提前做。

---

## D. Token / 上下文工程（与记忆/文件治理强相关）

- **最大 token 漏点：** 每对话冷启动读 CURRENT_STATE（数百行）+ DECISION_LOG（1650 行）。→ 用 boot-brief skill + 精简"启动简报"层解决。
- **consolidate-memory skill**（已装）：定期合并/裁剪记忆，防膨胀。
- **子会话作用域：** 不把全部状态塞进每个子会话；按职能只加载所需。
- 归到"上下文/记忆工程治理"专项轨（会话3，高优先）。

---

## E. 否决 / 不引入

- 外部云端记忆框架（Mem0/Graphiti/Mem.ai）——DEC-061，保持文件式单一权威。
- 重型多 agent 编排框架（LangGraph/A2A）——Phase 2 再评估，现在=风险 B。
- VectorBT PRO（$20/月）——延后，与"研究期压成本"一致。

---

## F. 优先级 & 下一步

1. **先做（高杠杆、低成本）：** 自研 boot-brief + state-sync（直接降 token、治状态滞后）。
2. **研究期接入：** Exa（外部知识摄取，配合不闭门造车）。
3. **按需：** CoinDesk/LunarCrush 等到对应机制立项再定。
4. **打包（Phase 2）：** 用 cowork-plugin-management 把自研 skill 打成"AI 量化操作"插件，沉淀复用。

**建议立即动作：** 先自研 boot-brief + state-sync 两个 skill（≤Claude 直接做），它们对"省 token + 少卡壳 + 防状态失真"见效最快。Founder 确认即开。
