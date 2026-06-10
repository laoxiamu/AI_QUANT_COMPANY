# V5 工具/框架借鉴集成计划 v1

⚠️ **本文件已降级（2026-06-10，依据 PHASE1_TECH_ORG_GOVERNANCE_v1 §3.1 文档权威层级）**：仅作历史参考，禁止作为当前架构、计划或决策依据。现行权威：`01_MEMORY_CORE/BOOT_BRIEF.md` + 公司OS四蓝图。

**撰写：** 2026-06-06 · Claude（CTO，主理人身份主动产出）
**缘起：** Founder 指出"做没做工具/产品调研"。查证结论：D38（V4 历史，2026-05-09）规划过"学习→借鉴→集成"，
但**V5 从未执行**——我们一路在手写回测/退出/持仓逻辑，重复造轮，这与退出设计失败、1x口径混乱、成本建模反复直接相关。本计划补上这一缺口。
**原则（采纳 D38/ChatGPT 一致结论）：** 不自己发明 → 先学习 → 再借鉴 → 再集成 → **最后才重写**。
**性质：** 历史文档(D38)为 HYPOTHESIS 参考；本计划为 V5 现行计划，结论经评估后采纳。

---

## Track 1 —— 立即纳入方法论（直接关系当前 Alpha 研究，最高杠杆）

| 借鉴 | 来源 | 用途 | 决断 |
|------|------|------|------|
| **Triple Barrier Method** | López de Prado / mlfinlab | 标准退出框架：止盈屏障 + 止损屏障 + 时间屏障 | ✅ **立即采纳为所有未来策略的标准退出框架**。取代手写退出（Sweep 家族退出失败的根因之一）。 |
| **Meta-Labeling** | López de Prado / mlfinlab | 主信号之上加二级模型判"这单做不做" | ✅ **采纳为 regime-first 的正式框架**。P1-04（ADX 趋势门控做多）就是它的手动实例；未来用正式形式。 |
| **事件采样 event-based sampling** | López de Prado | 按市场事件而非固定时间窗采样，减少"马后炮"滞后 | ✅ 采纳为采样方法论（呼应"马后炮是方法问题"的判断）。 |

**工具落地：** 优先用开源实现（MLFinPy / 社区 triple_barrier repo），经 skill/代码审计后用；三屏障逻辑简单亦可自实现。**不重造方法论。**
**与在飞任务的关系：** P1-04 继续按原预登记跑（它已是 meta-labeling 的干净实例，ADX 门控=二级标签）；Triple Barrier 纳入后作为后续版本的标准退出。

---

## Track 2 —— Phase 2 系统建设参考（现在不建，建时再学）

| 借鉴 | 用途 | 决断 |
|------|------|------|
| **Freqtrade** | Position Lifecycle / Risk Engine / Protections(cooldown/max-DD/pair-lock) | 📋 Phase 2 参考其基础设施设计，**学架构不搬策略**（D38 结论仍成立）。 |
| **NautilusTrader** | 事件驱动架构 / 持仓对账 / 组合状态 | 📋 Phase 2 参考（Ghost Position 修复思路的来源）。不搬代码（Rust/Cython 成本高）。 |
| **VectorBT** | 向量化回测/参数实验 | ✅ 已在用。 |

**纪律：现在不建这些系统**——V4 把全套精密系统建好仍因无 Alpha 失败（风险B 活教材）。先验证 Alpha。

---

## Track 3 —— 多智能体协作自动化（"你手工搬运 Codex"的问题）

**痛点（你点的真问题）：** 目前 Founder 手工把 Codex 结果转给 Claude、把 Claude 任务转给 Codex。宪法明确禁止 Founder 当信息中转。
**2026 工具栈：** MCP（智能体↔工具，本项目已在用）+ A2A（智能体↔智能体委派，Google 2025 起）+ LangGraph（有状态编排/检查点）+ Claude Agent SDK（编码智能体）。

**CTO 决断（我主动拿主张）：现在不建重型编排层。**
- 理由：重蹈风险B（建复杂基础设施而 Alpha 未验证）。当前文件式 handoff（TASK_*.md / REPORT_*.md 存仓库）已是结构化、可追溯的协作协议，够用。
- 真正的自动化（A2A/LangGraph 让 Codex 自主接任务、回写、Claude 自动收）留到 **Phase 2、有可部署策略后**再建——那时它自动化的是一个已验证有价值的流程，而不是把一个还在试错的流程过早固化。
- 近期轻量改进（不增基础设施）：把 TASK/REPORT 的字段标准化、约定 Codex 完成即回写固定路径，减少你手工描述的环节。
- **这恰好印证你的洞察**：我们过去研究"多 agent 如何协作"，现在的问题是"自动协作、不靠手搬"——但解法的正确时机是先有值得自动化的稳定流程。

---

## 决断汇总（立即生效）

1. **采纳 Triple Barrier + Meta-Labeling + 事件采样为 V5 方法论**，写入 Research Protocol；regime-first 即 meta-labeling 的应用。
2. **P1-04 继续**（meta-labeling 手动实例）；**P1-03 OI 数据核查继续**。
3. **现在不建** 重型 agent 编排，也不建 Phase 2 交易系统；Freqtrade/Nautilus 留作 Phase 2 参考。
4. 后续若需三屏障库，先 skill/代码审计再用（D38 安全纪律：ClawHub 有恶意 Skill 风险）。

**一句话：把"自己手写一切"改成"借鉴成熟方法论(三屏障/meta-labeling)做研究、把系统和编排留到 Phase 2"，这是对'重复造轮'和'手工搬运'两个问题的统一答案。**
