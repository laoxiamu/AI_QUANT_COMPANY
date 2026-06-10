# 工具 / 框架 / Skill 借鉴集成调研任务书 v1

**创建：** 2026-06-06 · Claude（CTO）
**用途：** 在**新对话**中执行的独立调研支线。本文件自包含——新对话读完核心文件后照此执行。
**原则（DEC-056）：** 不自己发明 → 先学习 → 借鉴 → 集成 → **最后才重写**。
**定位：** 并行支线，服务当前阶段（Phase 1 找 Alpha），按信息增益排序。

---

## 0. 强制纪律（执行前必读）

1. **风险B 护栏：** 本调研**不得阻塞主线**（P1-05 归因 + Alpha 研究）。产出是"集成决策矩阵 + 落地计划"，**不是装一堆工具、不是写一堆代码**。时间盒：1~2 个工作单元产出矩阵，避免无限扩张。
2. **专业审查（CLAUDE.md §专业负责人标准 / 七问精神）：** 每个候选先回答"**该不该引入、引入解决什么、是否当前阶段最该做**"，不为调研而调研。
3. **安全：** 任何拟**安装**的 Skill/工具必须先安全审计（D38：ClawHub 曾有 341 个恶意加密 Skill）。只读文档/源码评估，**不下载执行未审计代码**。
4. **借鉴 ≠ 搬码：** 默认学设计理念/方法论；搬代码要单独评估成本；重写是最后手段。
5. **不重新论证 D38 已否决项**（见 §3 Tier-X），只看"触发条件是否已变化"。

---

## 1. 新对话启动协议

先按 CLAUDE.md 读 5 个核心文件（含 CLAUDE.md v2.1「专业负责人标准」、DECISION_LOG 至 DEC-059），再读：
- `00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v1.md`（本调研的 v1 结论，待升级为 v2）
- `03_RAW_INBOX/STATUS_RECORDS/D38：工具集成评估报告.md`（V4 历史评估，HYPOTHESIS 参考）
- `02_KNOWLEDGE_BASE/V4_REUSABLE_ASSETS_v1.md`
- `00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_REPORT_v1.md`（方向⑦回测选型、⑨技术栈）

---

## 2. 调研方法（每个候选）

- 用 **context7** 查库/框架官方文档；**web search** 查 2026 现状与社区评价；GitHub/官方仓库看活跃度、许可、维护状态。
- 填写评估字段：**名称 / 来源 / 定位 / 与当前阶段相关性 / 借鉴什么(设计·方法·代码) / 决策(立即采纳·Phase2参考·否决·延迟) / 理由 / 安全 / 触发条件**。
- 决策对齐当前阶段优先级：**Alpha 方法论 > 系统参考 > Agent/编排 > 功能扩展**。

---

## 3. 调研范围（按当前相关性分层）

**Tier 1 —— 立即服务 Phase 1 方法论（最高优先）**
- Triple Barrier Method、Meta-Labeling、事件采样（López de Prado / mlfinlab / MLFinPy / 社区 triple_barrier）
- AFML 其他技术：purged/embargo 交叉验证、分数差分、trend-scanning（防过拟合/标签）
- 市场状态分类法：ADX、Kaufman 效率比、Hurst 指数、市场结构(HH/HL)——服务 P1-05 归因与后续状态过滤
- VectorBT 进阶能力（regime 分段、批量参数、IC/Walk-Forward）
- **目标产出：** 这些方法如何接入我们现有 VectorBT 回测管线的"可落地"说明；哪些库经审计后可用。

**Tier 2 —— Phase 2 系统参考（学架构不搬码，现在不建）**
- Freqtrade（Position Lifecycle / Risk Engine / Protections）
- NautilusTrader（事件驱动 / 持仓对账 / 组合状态）
- Backtrader（事件驱动二次验证）、vn.py（engine 分离 / event bus）

**Tier 3 —— Agent/编排/记忆/治理（多为 Phase 2，仅评估不建）**
- 编排/协议：MCP(已用)、A2A、LangGraph、Claude Agent SDK、CrewAI、AutoGen
  - 重点回答一个问题：**"Claude↔Codex 自动协作、停止 Founder 手工搬运"的最小可行路径是什么？**（结论大概率是 Phase 2 再建，但要给出路径与触发条件）
- 记忆：Mem0、Letta(MemGPT)、Graphiti（对照我们现有 Memory Core，看是否值得借鉴）
- 治理：ADR、OODA（已部分借鉴进 DECISION_LOG / Research Protocol，复核有无可补强）

**Tier 4 —— Skill / 连接器（复核 D38 评估 + 现状 + 安全）**
- quant-research-platform、trading-devbox（D38 曾"采纳待装"，复核现状是否仍值得）
- market-sentiment（恐惧贪婪/情绪因子，P2 候选）

**Tier X —— 携带 D38 否决清单，不重新论证，只查触发条件是否变化**
- binance-pro（实盘阶段再评估）、self-improving-agent（有盈利样本前不碰）、taskmaster（过度工程）、
  onchain/crypto-cog/trading-research（与当前框架关联低）、auto self-evolution（无 Alpha 前不碰）

---

## 4. 交付物

1. **`00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v2.md`** —— 升级版集成决策矩阵（V5 版的 D38），含上述全部候选的决策字段。
2. **Tier 1 落地说明** —— Triple Barrier / Meta-labeling / 状态分类如何接入现有回测管线（接口级，不写完整实现）。
3. **回灌主线的建议清单** —— 哪些立即写入 Research Protocol；哪些列 Phase 2；哪些否决。
4. （可选）Tier 3 的"Claude↔Codex 自动化最小路径 + 触发条件"一页评估。

---

## 5. 回灌主线流程（重要）

新对话**不直接改 Memory Core**（协作规范）。流程：
```
新对话产出 V5_TOOL_INTEGRATION_PLAN_v2 + 建议清单
   ↓
主对话 Claude(CTO) 审阅
   ↓
升级到 DECISION_LOG / Research Protocol（标注 Founder 是否需 D 级确认）
```
其中"采纳新方法论进 Research Protocol""引入会改交易标的/资金的工具"属 D 级，须 Founder 确认。

---

## 6. 一句话给新对话

> 先判断每个候选"现在该不该碰"，再决定借鉴什么；产出一份能直接指导集成的决策矩阵，而不是装工具或写代码；全程不阻塞主线 Alpha 研究。
