# 技术系统架构 v1.0
状态：DRAFT（随 Phase 1 研究验证持续完善）
更新：2026-06-14 Claude（主理人/CTO）
原则：AI不进实时交易闭环；Track A（自动执行）与 Track B（AI分析）完全分离

## 总体架构（双轨制）

```text
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

## Track A：自动执行轨道

| 层级 | 核心职责 | 关键组件 | 当前建设状态 |
|---|---|---|---|
| Layer 1 数据与执行 | 采集并持久化市场数据，可靠执行订单 | Binance API 实时行情；`aiquant-liq-collector.service`；PostgreSQL（计划）；限价优先、市价仅用于熔断 | 采集器✅已运行；订单执行待建 |
| Layer 2 策略 | 产生信号和市场状态，不直接下单 | TSMOM 信号引擎（4H）；A-1 事件检测（OI骤降）；Carry 状态管理（每8H funding rate）；Regime 分类器 | Phase 1 研究中；代码化待 Phase 2 |
| Layer 3 Decision Gateway | 唯一有权下单；完成最终裁决、风控和状态一致性检查 | 单日-2%熔断；-20%总回撤；事件窗禁交易；极端波动熔断；仓位计算；Position Journal；Risk Timestamp；交易所/PostgreSQL/runtime 三方对账 | 规则设计完成（DEC-015/063/069）；代码化待 Phase 2 |
| Layer 4 监控与报告 | 提供运行可观测性及 Track B 只读输入 | 结构化日志；异常告警；每日数据快照 | 待 Phase 2 |
| Layer 5 Knowledge Layer | 沉淀决策、研究、经验和历史档案 | `DECISION_LOG`；`GRAVEYARD_INDEX`（含正向知识库）；研究报告归档；`01_MEMORY_CORE/` | ✅运行中 |

## Track B：AI 分析轨道
角色：**AI Pre-Execution Analyst**（执行前分析师）
设计版本：v1.1（整合 DR-E2 Codex 工程评审结论，2026-06-14）
职责边界：
- 可以分析市场状态、信号质量、风险容量和异常情况，并输出建议。
- v1 是 advisory/audit layer，不是 veto gate；`no_trade` 仅为建议，不得自动阻断 Track A。
- 不得下单、改仓位、改风控、绕过 Gateway 或进入实时执行路径。

### 集成架构

```text
Decision Gateway
  -> 写入不可变 decision_request（冻结 snapshot + decision_id）
  -> 异步触发 AI analysis job
  -> 按确定性规则继续执行（不等待 AI）

AI Worker（独立进程）
  -> 只读 decision_request snapshot（禁止重新查询当前 DB）
  -> 调用 claude-haiku API（timeout=2.5s，连接 timeout=0.5s）
  -> 校验 JSON schema
  -> 写入 PostgreSQL ai_analyst_log 审计表
```

Fallback 语义：
- 正常返回：`recommendation = approve/caution/no_trade/needs_human_review`。
- API 不可用、超时或 schema 错误：`analysis_status = unavailable, recommendation = null`。
- 禁止把不可用伪装成 `approve`；Track A 始终按确定性规则继续。

频率控制：
- 自动触发全局 cap ≤50次/日；同品种同触发每个 4H bar 最多1次。
- 同一 A-1 episode 仅做1次初始分析。
- 连续3次 timeout/5xx 后打开 circuit breaker，暂停 AI 调用15分钟。

| 触发 | 频率 | 内容 |
|---|---|---|
| 定时日报 | 每日 | 信号是否如预期、市场状态、下一步预警 |
| 执行前分析 | 每次有信号时 | 背景与信号质量评估；异步输出建议，不阻塞执行 |
| 事件触发 | A-1/熔断/异常 | 事件解读与严重程度评估 |
| Founder发起 | 按需 | 标的分析；timeout 放宽至30s |
| 定时深度 | 每周/每月 | P&L归因、机会地图重评 |

AI 输入仅来自冻结 decision snapshot：`decision_id` / `decision_context_id`、当前持仓、近期 K 线/OI/funding rate、当前风险容量及触发信号或事件；输入上限4000-6000 tokens，超限时确定性截断。

## 六条工程铁律

单向控制流 / Risk-First / 唯一真实数据源（PostgreSQL）/ 可审计 / 先可靠再盈利 / AI分析独立于执行链路。

## 阶段建设计划

| 范围 | 计划 |
|---|---|
| Track A Layer 1 | ✅部分完成：采集器已建 |
| Track A Layer 1-3 | Phase 2 主要建设内容 |
| Track B | Phase 2 同步建设，调用 Claude API |
| Track A Layer 4-5 | Phase 2 配套建设 |
