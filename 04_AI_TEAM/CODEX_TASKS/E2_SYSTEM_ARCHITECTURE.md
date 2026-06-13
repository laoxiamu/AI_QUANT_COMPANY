# E2：技术系统架构文档

**任务类型：** 文档创建（中等复杂度）
**输出：** `05_TECH_DESIGN/02_SYSTEM_ARCHITECTURE.md`
**验收：** 文件存在，包含5层架构图 + AI Pre-Execution Analyst 角色 + Track A/B 双轨说明

---

## 背景

Phase 2 系统蓝图重构第2张图：技术系统架构。

本文件独立设计结论来源：
- Claude 主理人分析（2026-06-14）：双轨制、AI Pre-Execution Analyst 角色
- V5 研究报告提炼（仅参考对比）：`04_AI_TEAM/CODEX_TASKS/REPORT_V5_DESIGN_EXTRACTION_POST_0510.md` §4（line 137）、§8（line 298）
- 当前 Phase 2 蓝图（已有内容，可参考但不直接继承）：`05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md`

重要：历史文件只做对比参考。以下规格是独立设计结论，直接按规格写。

---

## 输出内容规格

文件路径：`05_TECH_DESIGN/02_SYSTEM_ARCHITECTURE.md`

### 必须包含的内容：

**1. 文件头**
```
# 技术系统架构 v1.0
状态：DRAFT（随 Phase 1 研究验证持续完善）
更新：[日期] Claude（主理人/CTO）
原则：AI不进实时交易闭环；Track A（自动执行）与 Track B（AI分析）完全分离
```

**2. 总体架构图（双轨制）**

```
                    ┌──────────────────────────────────────────┐
                    │  Track B: AI 主动分析轨道                  │
                    │  Claude 日报/周报/异常触发/月度评估          │
                    │  + AI Pre-Execution Analyst（执行前分析）    │
                    │  + Founder 主动发起分析（标的评估）           │
                    └──────────────┬───────────────────────────┘
                                   │ 只读（不写入执行路径）
┌──────────────────────────────────▼──────────────────────────┐
│  Track A: 自动执行轨道（5层）                                  │
│                                                              │
│  Layer 5: Knowledge Layer（知识管理）                         │
│  决策记录 / 研究归档 / 经验提炼 / 历史档案                      │
│                                                              │
│  Layer 4: 监控与报告层                                        │
│  结构化日志 / 告警推送 / 数据快照                               │
│                                                              │
│  Layer 3: 决策与风控层（Decision Gateway）                    │
│  信号聚合 / 仓位计算 / 硬熔断 / 最终裁决 / 三方对账              │
│                                                              │
│  Layer 2: 策略层                                             │
│  TSMOM信号 / A-1事件检测 / Carry状态 / Regime分类器            │
│                                                              │
│  Layer 1: 数据与执行层                                        │
│  Binance API / 强平采集器 / PostgreSQL（唯一真实源）/ 订单执行   │
└─────────────────────────────────────────────────────────────┘
```

**3. Track A 各层详细说明**

每层写：核心职责 / 关键组件 / 当前建设状态

Layer 1（数据与执行）：
- 组件：Binance API 实时行情、`aiquant-liq-collector.service`（已部署）、PostgreSQL（计划）、订单执行（限价优先/市价熔断）
- 状态：采集器✅已运行，订单执行待建

Layer 2（策略层）：
- 组件：TSMOM 信号引擎（4H）、A-1 事件检测（OI骤降监测）、Carry 状态管理（每8H funding rate）、Regime 分类器
- 状态：研究中（Phase 1），代码化待Phase 2

Layer 3（Decision Gateway）：
- 核心原则：唯一有权下单的模块；策略层只产生信号，不直接调用交易 API
- 组件：硬风控规则（单日-2%熔断/-20%总回撤/事件窗禁交易/极端波动熔断）、仓位计算、Position Journal（事件溯源）、Risk Timestamp（每个持仓的最后风控检查时间）、三方对账（交易所/PostgreSQL/runtime）
- 状态：规则设计完成（DEC-015/063/069），代码化待Phase 2

Layer 4（监控与报告）：
- 组件：结构化日志（供Track B读取）、异常告警、每日数据快照
- 状态：待Phase 2

Layer 5（Knowledge Layer）：
- 组件：DECISION_LOG、GRAVEYARD_INDEX（含正向知识库）、研究报告归档、`01_MEMORY_CORE/`
- 状态：✅ 运行中

**4. Track B：AI 分析轨道**

角色：**AI Pre-Execution Analyst**（执行前分析师）
设计版本：v1.1（整合 DR-E2 Codex 工程评审结论，2026-06-14）

职责边界（严格）：
- 可以：分析市场状态、信号质量、风险容量、异常情况，输出建议
- **v1 是 advisory/audit layer，不是 veto gate**：no-trade 只是建议，不得自动阻断 Track A
- 不可以：下单、改仓位、改风控、绕过 Gateway、进入实时执行路径

**集成架构（背景 worker 模式，不阻塞 Gateway）：**
```
Decision Gateway
  -> 写入不可变 decision_request（含冻结 snapshot + decision_id）
  -> 触发 AI analysis job（异步）
  -> 按确定性规则继续执行（不等待 AI）

AI Worker（独立进程）：
  -> 读取 decision_request snapshot（禁止重新查当前DB）
  -> 调用 claude-haiku API（timeout=2.5s，连接timeout=0.5s）
  -> 校验 JSON schema
  -> 写入 ai_analyst_log 表（PostgreSQL）
```

**Fallback 语义（必须区分）：**
- AI 返回建议：`recommendation = approve/caution/no_trade/needs_human_review`
- API 不可用/超时/schema错误：`analysis_status = unavailable, recommendation = null`
- 绝对禁止：把不可用伪装成 `approve`

**频率控制：**
- 全局 cap：自动触发 ≤ 50次/日
- 同品种同触发：每4H bar最多1次
- A-1 episode：同一 episode 只做1次初始分析
- circuit breaker：连续3次timeout/5xx → 暂停15分钟AI调用

触发方式：
| 触发 | 频率 | 内容 |
|---|---|---|
| 定时日报 | 每日 | 信号是否如预期、市场状态、下一步预警 |
| 执行前分析 | 每次有信号时 | 背景分析+信号质量评估，输出建议（异步，不阻塞执行） |
| 事件触发 | A-1/熔断/异常 | 事件解读+严重程度评估 |
| Founder发起 | 按需 | 标的分析（timeout放宽至30s） |
| 定时深度 | 每周/每月 | P&L归因、机会地图重评 |

AI 分析输入（来自冻结 decision snapshot，禁止重新查DB）：
- decision_id / decision_context_id（保证与 Gateway 使用同一数据版本）
- 当前持仓状态、近期 K 线 / OI / funding rate 快照
- 当前风险容量、触发分析的信号/事件描述
- input token 上限：4000-6000（超过则确定性截断）

**5. 六条工程铁律**（同 PHASE2_SYSTEM_BLUEPRINT.md，此处简引）
单向控制流 / Risk-First / 唯一真实数据源(PostgreSQL) / 可审计 / 先可靠再盈利 / AI分析独立于执行链路

**6. 阶段建设计划**
Track A Layer 1: ✅ 部分（采集器已建）
Track A Layer 1-3: Phase 2 主要建设内容
Track B: Phase 2 同步建设（调用 Claude API）
Track A Layer 4-5: Phase 2 配套

---

## 格式要求

- 不超过 100 行
- 架构图用 ASCII，不用外部图表库
- 保持专业但不过度繁琐
- 不触碰 Holdout 数据，不触碰 `01_MEMORY_CORE/` 权威文件
