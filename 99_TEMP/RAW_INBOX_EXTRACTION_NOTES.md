# RAW_INBOX 提炼笔记（仅参考，不直接继承）

**读取时间：** 2026-06-05  
**读取文件：** D29、D30、D31、D35  
**信息等级声明：** 所有内容默认为 EXPERIENCE 或 HYPOTHESIS，不直接升级为 DECISION  
**使用规则：** 本文件是内部工作笔记，供 B2 架构复核和后续 Research Protocol 设计参考。不写入 DECISION_LOG，不作为架构依据，不引用为「当前事实」

---

## D31：研究协议（EXPERIENCE 级）

**来源：** V4.6.2 观察期失效后编写，写作背景是「有运行中的实盘系统」  
**与V5的关键差异：** V5 目前无实盘系统，Phase 0A/0B 是纯历史回测。D31 的「观察期执行协议」（§2）是为监控实盘系统设计的，对 V5 纯回测阶段不适用。

**可参考的核心原则（与当前架构一致）：**
- 单变量原则（D31 §3.1）→ 已在 Architecture v2 §7.3 体现 ✅
- Walk-Forward 验证（D31 §6.2）→ 已在 Architecture v2 §7.1 作为硬门槛 ✅
- 统计污染处理（INVALIDATED 剔除，D31 §4.3）→ 已在 DEC-009/010/011 体现 ✅
- 实验版本命名（D31 §3.2）→ V5 应采用，当前未定义

**阈值对比（注意差异）：**

| 指标 | D31 值 | V5 当前值（DEC-018/Architecture v2）| 分析 |
|------|--------|------|------|
| 单Setup回测最小样本 | 1000 穿仓 | 500（确认级）/ 300-500（探索级）| D31 是实盘背景，1000是适合长期运营的阈值；V5历史回测500在统计上合理，差异属于合理的情境适配 |
| Sharpe 阈值 | > 0.5 | > 1.0 | Architecture v2 明确将0.5标注为「过于宽松」并升级为1.0，属于有意识的V5改进 ✅ |
| IC最小样本 | 500 个观测点 | 同为500 | 一致 ✅ |

**D31 有但 V5 当前缺失的内容（供 Research Protocol 设计参考）：**
- 实验版本命名规则（如 `v5_sweep_bull_v1` 格式）
- 无效实验声明流程（当发现变量混杂时，如何正式声明「本次数据不具备结论效力」）
- 变更后是否需要重新实验的判断规则（D31 §7.1）

**结论：** D31 的核心精神（单变量、Walk-Forward、统计有效性）已被 V5 架构正确吸收。具体阈值已有意识地升级。V5 Research Protocol 应独立设计，可参考 D31 的框架结构，但不应沿用其「观察期监控」框架——V5 是从零历史回测开始，不是监控运行中的系统。

---

## D30：持仓生命周期规格书（EXPERIENCE 级）

**来源：** Ghost Position Incident 根因分析后编写的 V5 Phase B 任务书

**关键发现：Architecture v2 §8.2 状态机与 D30 有细节差异**

Architecture v2 §8.2（当前图示）：
```
PENDING → OPEN → ACTIVE → MANAGING → EXITED
                    ↓               ↓
                ORPHANED       REPLACED
                    ↓
               INVALIDATED
```

D30 §3.1 定义的完整规则（对比）：

| 差异点 | Architecture v2 图示 | D30 规范 |
|--------|---------------------|---------|
| REPLACED 来源 | 图示显示从 MANAGING | D30：可来自任意活跃状态（OPEN/ACTIVE/MANAGING），通过显式替换操作触发 |
| INVALIDATED 来源 | 图示显示从 ORPHANED | D30：可来自任意活跃状态，由 Reconciliation Loop 在发现生命周期断裂时触发 |
| ORPHANED 来源 | ACTIVE | D30：Phase 1 超过 N 次扫描未检查，来自任意活跃状态 |

**结论：** Architecture v2 的状态机图示是简化版，与 D30 的完整定义存在逻辑差异。当前已有 P-002 警告注释，Phase 2 时必须以 D30 为准重新设计。目前 Phase 0A 不涉及持仓管理，此差异不影响当前工作，但需确保 Phase 2 时不直接使用 v2 图示。

**D30 对 Phase 2 的直接价值（EXPERIENCE，Phase 2 参考）：**
- 数据库字段定义（§8）：trade_id、trade_status、max_profit、exit_reason、holding_time、last_risk_check_at、peak_pnl、replaced_by_trade_id
- 重启恢复流程（§6.2）：从 PostgreSQL 按 trade_id 恢复，不用 DISTINCT ON 丢数据
- 新信号处理规范（§7.2）：先 REPLACED 旧仓 → 记录 PnL → 再开新仓的完整流程

---

## D29：V4.6.2 系统架构文档（EXPERIENCE 级）

**来源：** V4.6.2 冻结后的系统快照，2026-05-09 状态

**对 P-001 修正的补充确认：**
D29 §4.1 显示 2026-05-09 时的状态：
- PostgreSQL/Redis/Grafana/Gateway 均处于 Docker 容器运行中
- 这是2026-05-09的状态，距今近一个月，无法确认当前状态
- P-001 修正（改为 HYPOTHESIS）是正确的

**D29 对 V5 的参考价值：**

D29 §4.3 将以下资产标注为「直接继承」（注：这是 V4 自己的规划，不是当前验证事实）：
- PostgreSQL + Redis + Grafana：13天稳定运行数据（截至2026-05-09）
- systemd 保活体系
- Gateway 裁决框架（风控规则硬编码 + HMAC签名）
- 微观结构过滤 + 冷却期机制（拦截率65%+28%）
- Docker 部署体系

以上均应在 Phase 2 实际系统设计时验证，不得作为当前事实。

**V4 架构关键点（供 Phase 2 参考）：**
- V4 使用 OpenClaw Gateway（消息路由）+ Decision Gateway（风控裁决）的双层 Gateway 设计
- V4 的 AI 层使用 Main Agent（Kimi K2.6）+ Signal Agent（DeepSeek）+ Risk Agent（DeepSeek）——V5 不继承此设计，改用 Claude + Codex
- Hermes 在 V4 中用于 RL 模型更新，当前「Hermes Agent 变身 Codex」的外部文章验证了 Hermes 作为 Agent 框架的演进方向

**Architecture v2 与 D29 的关键一致性确认：**
- 四层分层架构（Human/Governance/Research/Execution/Infrastructure）与 D29 的分层思路一致，V5 做了正确的升级和重新定义 ✅
- DEC-008（PostgreSQL权威源）与 D29 AD-1/原则3 一致 ✅
- DEC-009（禁止同向覆盖）与 D29 AD-4 一致 ✅
- DEC-010（trade_id）与 D29 AD-5 一致 ✅
- DEC-011（Reconciliation Loop）与 D29 AD-6 一致 ✅

---

## D35：技术债务登记表（EXPERIENCE 级）

**来源：** V4.6.2 冻结后的技术债务全景图

**与当前架构的对照：**

| D35 债务 | 在当前架构中的处理状态 |
|---------|-------------------|
| P0-4 同向覆盖 | DEC-009 ✅ |
| P0-5 Phase 1 依赖内存 | DEC-008 ✅ |
| P0-6 log_trade粗粒度 | DEC-010 ✅ |
| P1-1 49笔僵尸持仓 | PC-03（FACT记录），Phase 2 时处理 |
| P1-7 固定1.5%止损 | Architecture v2 §17 已标注为V5改为结构止损 ✅ |
| P3-1 22分制IC≈50% | PC-09（EXPERIENCE记录），Architecture v2 §17 否定方向 |

**D35 的 V5 阶段命名（注意：与我们的阶段命名不同）：**
- D35 说的「V5 Phase B/C/D」是 V4 时的规划命名，对应我们的 Phase 2+ 
- 我们的 Phase 0A/0B/1/2/3/4 是独立的重新定义，不继承 D35 的 Phase 编号

**D35 提供的额外参考（当前架构未覆盖）：**
- P1-8 「无'不做'条件」：无宏观事件/周末/连亏后暂停机制 → V5 Research Protocol 中应包含 Regime 定义，但连亏暂停等运营规则是 Phase 2+ 的设计内容
- P2-3 「币种相关性未控制」：BTC/ETH/SOL 高相关 → 在扩品种时需要注意（Phase 1+ 考虑）

---

## 综合结论

**给 B2 架构复核的关键发现：**

1. **Architecture v2 DEC-008~011 来源确认**：D29/D30 完整印证了这四条决策的正确性。✅
2. **Architecture v2 §8.2 状态机差异**：与 D30 有结构性差异（P-002 已加注警告）。Phase 2 前必须以 D30 为准重新绘制。
3. **Architecture v2 §17 策略方向**：否定 22分制（D35 P3-1）和固定止损（D35 P1-7）的判断与 D35 一致。
4. **P-001 修正正确性**：D29 §4.1 确认了 V4 基础设施在2026-05-09时运行，但距今近一个月状态未知，P-001 修正为 HYPOTHESIS 是正确的。
5. **Research Protocol 设计方向**：D31 的核心原则已被正确吸收，但 V5 协议需要重新设计为「纯历史回测」语境，不是「实盘监控」语境。

**给 Master Plan B4 任务的关键发现：**

D31 中有一个 V5 当前缺失的要素：**实验版本命名规则**。这应补充到 Research Protocol 任务的验收标准中。
