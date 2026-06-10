# AI_QUANT_COMPANY_ARCHITECTURE_v1.md

⚠️ **本文件已降级（2026-06-10，依据 PHASE1_TECH_ORG_GOVERNANCE_v1 §3.1 文档权威层级）**：仅作历史参考，禁止作为当前架构、计划或决策依据。现行权威：`01_MEMORY_CORE/BOOT_BRIEF.md` + 公司OS四蓝图。

**版本：** 1.0 草案  
**创建时间：** 2026-06-02  
**作者：** Claude（CTO）  
**状态：** 草案，待用户确认后生效  
**存放：** 00_PROJECT_MANAGEMENT/（正式版移入 05_ARCHITECTURE）

---

## 一、项目定性

**项目名称：** AI Quant Company  
**项目本质：** AI-Native Quant Research Operating System  
**North Star：** 找到可持续产生 Alpha 的方法，最终实现自动化量化交易

这不是一个量化交易系统。这是一个能够持续提出假设、验证假设、积累知识、沉淀决策，并最终发现 Alpha 的 AI 原生研究系统。交易系统是这个系统的产出物，不是系统本身。

---

## 二、整体架构分层

### 架构概览

```
┌─────────────────────────────────────────────────────┐
│                  HUMAN LAYER                        │
│   Founder（你）：最终决策 / 风险确认 / 方向判断       │
└─────────────────────────────────────────────────────┘
                        ↕ 决策确认
┌─────────────────────────────────────────────────────┐
│               GOVERNANCE LAYER                      │
│   Claude（CTO）：架构规划 / 任务分解 / 知识治理       │
│   Memory Core / Decision Log / Research Protocol    │
└─────────────────────────────────────────────────────┘
                        ↕ 任务规格
┌─────────────────────────────────────────────────────┐
│               RESEARCH LAYER                        │
│   假设定义 → 实验设计 → 回测执行 → 结论归档           │
│   Research Protocol / Backtest Framework            │
└─────────────────────────────────────────────────────┘
                        ↕ 验证通过的策略
┌─────────────────────────────────────────────────────┐
│               EXECUTION LAYER                       │
│   Codex：代码实现 / 系统部署 / 自动化执行             │
│   Trading System / Risk Engine / Data Pipeline      │
└─────────────────────────────────────────────────────┘
                        ↕ 运行数据
┌─────────────────────────────────────────────────────┐
│             INFRASTRUCTURE LAYER                    │
│   PostgreSQL / Redis / Grafana / Telegram Bot       │
│   腾讯云（新加坡）/ MacBook M1 / Windows i7          │
└─────────────────────────────────────────────────────┘
```

---

## 三、角色与职责定义

### 3.1 Human（Founder）
- 最终决策者，所有关键方向由人确认
- 日常操作：手机审批 + 桌面执行，碎片化时间可参与
- 不参与技术判断，但保持对系统运行状态的基本感知
- 核心职责：设定目标、确认决策、发现问题

### 3.2 Claude（CTO）
- 架构设计、规划、任务分解、知识治理、文档写作
- 不写代码，不直接部署，不执行终端命令（通过 Desktop Commander 辅助读写文件）
- 向 Codex 输出任务规格，向用户输出决策建议
- 维护 Memory Core，确保项目上下文可跨对话恢复

### 3.3 Codex（工程执行）
- 代码实现、单元测试、部署、调试、重构
- 输入：Claude 产出的任务规格文档
- 输出：可运行代码 + 执行报告
- 不参与架构决策，工程层发现的架构问题必须反馈给 Claude 裁决

### 3.4 Claude → Codex 交接规范

每个 Codex 任务必须包含：

```
目标：[具体可验证的产出]
输入：[数据源、文件路径、依赖]
约束条件：[技术限制、兼容性要求]
验收标准：[如何判断完成]
禁止事项：[不允许做的事]
参考文档：[相关规格文件路径]
```

---

## 四、基础设施架构

### 4.1 硬件资源分配

| 设备 | 用途 | 说明 |
|------|------|------|
| MacBook Pro M1 | 主开发机 / Claude 操作端 | Desktop Commander 运行于此 |
| 腾讯云轻量（新加坡，2核4G） | 策略引擎 / 数据库 / 监控 | 可访问 Binance，链式代理已配置 |
| Windows i7-11700/16G | 备用 / 回测加速 | 按需使用 |

### 4.2 软件基础设施（继承自 V4，已验证13天稳定）

| 组件 | 用途 | 状态 |
|------|------|------|
| PostgreSQL | 唯一权威状态源 | ✅ 继承，稳定运行 |
| Redis | 实时缓存（非权威） | ✅ 继承 |
| Grafana | 可视化监控 | ✅ 继承 |
| Docker Compose | 容器管理 | ✅ 继承 |
| systemd | 进程保活 | ✅ 继承 |
| Telegram Bot（×3） | 告警通知 | ✅ 继承 |
| Gateway 裁决框架 | 风控硬编码 | ✅ 继承，需改造 |

### 4.3 AI 工具链

| 工具 | 角色 | 状态 |
|------|------|------|
| Claude Desktop（Sonnet 4.6） | CTO / 主控 AI | ✅ 完全可用 |
| Desktop Commander v0.2.41 | 文件系统访问 | ✅ 完全可用 |
| Codex | 工程执行 | ⚠️ 已配置，待验证 |
| Obsidian + Sync | 知识管理 | ✅ 可用 |
| Context7 | 技术文档检索 | ⚠️ 待实际使用 |

### 4.4 Codex 五层架构（来自 5/21 DeepSeek 讨论，EXPERIENCE 级参考）

Codex 工程执行层将按以下五层组织：

```
Layer 1：记忆层（AGENTS.md / CLAUDE.md）
  → 全局规则、项目级配置、工程红线
Layer 2：知识层（skills/）
  → 工作流模板、最佳实践、可复用脚本
Layer 3：护栏层（hooks/）
  → 执行前拦截、执行后记录、危险命令阻断
Layer 4：委派层（subagents/）
  → 独立上下文子任务、互不干扰、结果回传
Layer 5：分发层（plugins/）
  → 团队配置同步、版本管理
```

此架构在 Phase 0B 建立 Codex 工作流时实施，当前阶段不展开。

---

## 五、信息流架构

```
RAW_INBOX（原始信息）
    ↓ 提炼（MEMORY_EXTRACTION_PROTOCOL）
MEMORY CORE（已验证知识）
    ↓ 支撑
RESEARCH LAYER（假设→实验→结论）
    ↓ 验证通过
DECISION LOG（确认决策）
    ↓ 转化
SYSTEM SPECS（技术规格）
    ↓ 实现
EXECUTION LAYER（代码→部署→运行）
    ↓ 产生
RESULTS（回测数据 / 实盘数据）
    ↓ 归档
KNOWLEDGE BASE（积累知识）
    ↓ 反哺
RESEARCH LAYER（下一轮假设）
```

每一个文档在信息流中都有明确状态（RAW → HYPOTHESIS → EXPERIMENT → RESULT → KNOWLEDGE → DECISION），Obsidian Properties 标注状态，不依赖目录位置判断。

---

## 六、研究流程架构（Research OS 核心）

### 6.1 标准研究闭环（来自 D31，已验证）

```
Hypothesis（提出假设）
    ↓ 定义规则
Experiment Design（实验设计）
    ↓ 获取数据
Data（历史数据获取）
    ↓ 执行
Backtest（回测）
    ↓ 统计
Analysis（统计分析）
    ↓ 判断
Conclusion（结论）
    ↓ 记录
Knowledge Base（归档）
    ↓ 如通过
Decision（进入下一阶段）
```

### 6.2 假设验证标准（来自 D31）

| 指标 | 最低阈值 | 说明 |
|------|---------|------|
| Expectancy | > 1.0 | 正期望 |
| Sharpe Ratio | > 0.5 | 风险调整后收益可接受 |
| Max Drawdown | < 25% | 风险可控 |
| 回测样本量 | ≥ 1000 次穿仓 | 统计显著性 |
| IC（因子有效性） | > 0.02 | 有统计意义的预测力 |

### 6.3 单变量原则（来自 D31，铁律）

一次只验证一个变量。V4 观察期13天修改了7个核心变量，导致无法追溯每个改动的独立贡献。V5 严格禁止此类操作。

---

## 七、风控架构（继承 V4，修复 Ghost Position 根因）

### 7.1 四条铁律（来自 D34 已确认决策）

```
DEC-008：PostgreSQL 是唯一权威状态源
DEC-009：禁止同向覆盖
DEC-010：持仓必须有全局唯一 trade_id
DEC-011：Reconciliation Loop + Orphan Detection 强制执行
```

### 7.2 持仓生命周期状态机（来自 D30）

```
PENDING → OPEN → ACTIVE → MANAGING → EXITED（终态）
                    ↓               ↓
                ORPHANED       REPLACED（终态）
                    ↓
               INVALIDATED（终态）
```

禁止状态：
- ACTIVE → ACTIVE（同向覆盖 = Ghost Position，绝对禁止）
- EXITED → 任何其他状态
- ORPHANED → ACTIVE（必须人工审核）

### 7.3 风控层级（继承自 V4 Gateway 框架）

```
Layer 1：持仓生命周期风控（trade_id + 状态机）
Layer 2：Phase 1 风控检查（从 PostgreSQL 读取，Reconciliation Loop 前置）
Layer 3：Gateway 裁决（熔断 / Kelly / 冲突检查）
Layer 4：单日风控（连亏暂停 / 最大回撤停止）
```

---

## 八、目录结构（当前版本，Phase 0A~0B 适用）

当前保留现有目录结构，Phase 0B 完成后按信息流驱动重构为：

```
AI_QUANT_COMPANY/
├── 00_GOVERNANCE/          ← 项目如何运转
│   ├── CONSTITUTION.md     ← 项目宪法（本文档升级版）
│   ├── PROJECT_OPERATING_STATE.md
│   ├── AI_CAPABILITY_BASELINE.md
│   └── WORKFLOWS/          ← Claude→Codex 协作规范
│
├── 01_MEMORY/              ← 项目知道什么
│   ├── CURRENT_STATE.md
│   ├── PROJECT_CONTEXT.md
│   ├── DECISION_LOG.md
│   ├── SYSTEM_RULES.md
│   └── MEMORY_EXTRACTION_PROTOCOL.md
│
├── 02_KNOWLEDGE/           ← 经过验证的知识
│   ├── ARCHITECTURE/
│   ├── RESEARCH/
│   ├── TRADING/
│   └── TOOLS/
│
├── 03_RESEARCH/            ← 研究工作区
│   ├── HYPOTHESES/         ← 假设库
│   ├── EXPERIMENTS/        ← 进行中实验
│   ├── RESULTS/            ← 实验结论归档
│   └── SETUPS/             ← Setup 规格文档
│
├── 04_SYSTEM/              ← 系统代码和配置
│   ├── ARCHITECTURE/
│   ├── SPECS/
│   └── RUNBOOKS/
│
├── 05_OPERATIONS/          ← 日常运营
│   ├── MONITORING/
│   ├── INCIDENTS/
│   └── REPORTS/
│
├── 06_INBOX/               ← 原始资料（现 03_RAW_INBOX）
│   ├── PAPERS/             ← 学术论文
│   ├── CHATGPT_EXPORT/
│   ├── DEEPSEEK_EXPORT/
│   ├── PROJECT_DOCS/
│   └── STATUS_RECORDS/
│
├── 99_TEMP/                ← 临时文件
└── 99_ARCHIVE/             ← 已废弃内容归档
```

**目录重构时机：** Phase 0B 启动前执行，届时大部分目录仍为空，迁移成本接近零。

---

## 九、阶段路线图

### Phase 0A：Research Capability Infrastructure（当前）

**目标：** 建立能够执行第一个研究闭环的最低能力  
**完成标准（五条，全部满足）：**
1. Memory 恢复能力 ✅
2. Research Protocol 存在 ❌
3. Backtest Framework 可运行 ❌
4. 第一个假设定义 ❌
5. 第一个研究闭环完成 ❌

**剩余任务：**
- Research Protocol 建立（基于 D31，按当前约束适配）
- Backtest Framework 选型与搭建
- 第一个 Setup 假设定义
- 执行第一个完整研究闭环

---

### Phase 0B：First Validated Hypothesis

**目标：** 证明系统能产生可判断的研究结论  
**完成标准：**
- 第一个 Setup 回测完成，有统计结论（不论正负）
- Codex 工程执行流程验证（首次完整 Claude→Codex 任务）
- 目录结构重构完成
- 知识库骨架建立（D30、D31、D32、D33 提炼完成）

---

### Phase 1：Research Engine Running

**目标：** 持续产生研究结论，找到第一个通过验证的 Setup  
**完成标准：**
- 至少完成 3 个 Setup 的完整研究闭环
- 至少 1 个 Setup 通过统计验证（Expectancy > 1.0）
- Research Protocol 经过实际验证并迭代
- Python 量化环境完整（pandas/numpy/ccxt 等）

---

### Phase 2：System Build

**目标：** 基于验证通过的 Setup 重建交易系统  
**前提条件：** Phase 1 至少有 1 个 Setup 验证通过  
**核心任务：**
- V5 系统重建（修复 D35 全部 P0/P1 技术债务）
- 持仓生命周期状态机实现（D30 规格）
- Reconciliation Loop + Orphan Detection 实现
- 模拟盘验证

---

### Phase 3：Live Trading

**目标：** 小资金实盘验证  
**前提条件：** 模拟盘连续30天无 P0 级事故  
**资金路径：** 1000元 → 10000元 → 30000元（按风险容忍度逐级）

---

## 十、核心约束（影响所有设计决策）

| 约束 | 值 | 影响 |
|------|-----|------|
| 月预算 | ~1000元 | 工具链选免费/低成本方案 |
| 服务器 | 腾讯云2核4G | 不适合高频、大数据量策略 |
| 本金上限 | 30000元 | 策略聚焦低频、高确定性 |
| 用户时间 | 1~5小时/天 | 系统设计强调自动化，减少人工干预 |
| 用户技术背景 | 无 | 所有技术决策需非技术语言说明 |
| 首要风险 | 风险C | 防止长期停留在讨论层 |

---

## 十一、V5 策略方向（HYPOTHESIS 级，待验证）

**方向：** 结构行为统计交易（Structure Behavior Statistical Trading）  
**核心理念：** 不信仰 SMC 概念本身，而是将结构行为拆解为可统计验证的行为因子

**第一个待验证的 Setup（候选）：**

```
品种：BTC
周期：4H
环境：Bullish Regime（Daily 确认）
信号：Liquidity Sweep + Bullish CHoCH + FVG Retrace（三重确认）
止损：结构止损（Swing Low + ATR Buffer）
止盈：分批（TP1: 1R / TP2: 2R / TP3: 跟踪止盈）
验证目标：1000次历史穿仓的 Expectancy 和 Sharpe
```

**注意：** 此 Setup 是方向假设，不是已确认决策。需要经过完整研究闭环验证后方可进入系统实现。

**已确认否定的方向（不再探索）：**
- 22分制/指标体系扩展（IC≈50%，预测力随机）
- K线形态系统（假阳性高，程序化困难）
- 多 AI 平权协作（结论冲突，无裁决机制）
- 强化学习（样本量严重不足）
- 高频策略（手续费劣势，本金约束）

---

## 十二、已继承的 V4 技术资产

以下 V4 组件经过13天压力测试，可直接继承：

| 资产 | 继承方式 |
|------|---------|
| 四层分层架构设计 | 直接继承，保持职责隔离原则 |
| PostgreSQL + Redis + Grafana | 直接继承，PostgreSQL 继续作为权威源 |
| Docker Compose 部署体系 | 直接继承 |
| systemd 保活体系 | 直接继承 |
| Gateway 裁决框架 | 继承框架，重写持仓逻辑（修复 P0 技术债务） |
| Telegram 三 Bot 告警通道 | 直接继承 |
| 微观结构过滤（OBI/Flow） | 作为参考，V5 中重新统计验证 |

**不继承的部分：**

| 组件 | 原因 |
|------|------|
| `_positions` 字典作为风控输入源 | Ghost Position 根因，已废弃 |
| `symbol_direction` 作为唯一标识 | 无法区分同向多笔，已废弃 |
| `log_trade()` 粗粒度匹配 | 数据写入错误，已废弃 |
| 22分制评分系统 | IC≈50%，已废弃 |
| OpenClaw 多 Agent 主控 | 复杂度失控，已废弃 |

---

*本文档为 Phase 0A 阶段产出的顶层架构草案，待用户确认后作为项目宪法基础文件。正式版将在 Phase 0B 启动时更新为 V1.0。*
