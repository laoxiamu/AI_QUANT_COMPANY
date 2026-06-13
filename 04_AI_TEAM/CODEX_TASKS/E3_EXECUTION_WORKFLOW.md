# E3：执行工作流文档

**任务类型：** 文档创建（简单）
**输出：** `05_TECH_DESIGN/03_EXECUTION_WORKFLOW.md`
**验收：** 文件存在，包含两条流程（项目执行流 + 投研执行流），格式清晰

---

## 背景

Phase 2 系统蓝图重构第3张图：两条核心执行工作流。

参考来源（只做对比，不直接复制）：
- Codex V5研究报告 §5 Phase路线图（`04_AI_TEAM/CODEX_TASKS/REPORT_V5_DESIGN_EXTRACTION_POST_0510.md` line 188）
- 当前研究协议：`06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`（投研流程以此为准，不降级）

---

## 输出内容规格

文件路径：`05_TECH_DESIGN/03_EXECUTION_WORKFLOW.md`

### 必须包含的内容：

**1. 文件头**
```
# 执行工作流 v1.0
状态：ACTIVE
更新：[日期] Claude（主理人/CTO）
说明：两条核心工作流——项目执行流（任何任务）+ 投研执行流（研究实验）
```

**2. 工作流一：项目执行流（任何任务/模块的流转方式）**

```
Founder 提出目标 / D级确认
    ↓
Claude 规划、拆任务、定验收标准
    ↓
任务分配：
  ≤50行/简单执行 → Claude 直接执行
  >100行/多文件/需大量迭代 → Codex 任务规格
    ↓
Codex 执行：写代码/建文件/跑脚本/自动化
    ↓
自动验证（必须先于 Claude Review）：
  - 代码：单元测试 / Lint
  - 数据：数据校验 / 格式检查
  - 回测：回测引擎 / Holdout 断言
  - 风控：风控规则检查
    ↓
Claude 关键节点 Review（验证自动验证结果 + 专业判断）
    ↓
归档：CURRENT_STATE 更新 / DECISION_LOG 记录 / 报告存档
    ↓
§1b 活动工作区清空（任务完成）
```

附注：
- Founder 主动打断时，Claude 更新 §1b 记录断点，任务状态持久化
- 新对话开局读 §1b，有内容则恢复，无内容则正常开局

**3. 工作流二：投研执行流（研究实验的完整生命周期）**

```
Idea / 外部观察
    ↓
机制审查（七问必答）：
  ①谁在付钱 ②为什么付 ③我们凭什么拿到
  ④数据/约束允许吗 ⑤市场状态归因 ⑥信号是机制的正确映射吗
  ⑦是否有信息增益更高的实验
    ↓
查墓园（GRAVEYARD_INDEX.md）：是否已经测过同类假设？
    ↓
预登记（必须在看数据前）：
  - 单变量冻结
  - MDE / 功效门设计
  - Holdout 物理隔离声明
  - 与已有预登记的碰撞门检查
    ↓
数据验证：数据质量门 / 样本量充分性
    ↓
开发集回测（Walk-Forward 3段）：
  - 四件套：E[R] / 赢亏比 / 正年比例 / P(DD≥20%)
  - 第五件：与相关性卡尺（TSMOM Baseline）超额对比
  - 成本压力档
    ↓
Claude Review（主理人专业透镜）：
  - 结果是否如预期
  - 失败原因归因
  - 是否触发改参数修补禁令
    ↓
[通过] → Risk Reviewer 盲审 → Paper Trading → Production Candidate
[失败] → 记入墓园，注明根因和复活条件 / 禁引用措辞
```

附注：
- 禁止"信号失败→改参数→再回测"的修补搜索
- 家族内变体不耗独立计数，但家族穷尽后禁第三变体
- Holdout 只在 Risk Reviewer 盲审前读取一次

**4. 流程触发与分工**

| 场景 | 触发方 | 执行路径 |
|---|---|---|
| 新研究实验 | Claude 主动 / Founder 提出 | 投研执行流 |
| 系统建设任务 | Claude 规划 → Codex 执行 | 项目执行流 |
| Founder 发现标的 | Founder 发起 | AI Pre-Execution Analyst 分析 → Founder 决策 |
| 策略调整 | 研究结果触发 | 必须新预登记，不得直接修改生产参数 |

---

## 格式要求

- 不超过 80 行
- 流程图用 ASCII 箭头，不用外部工具
- 不修改 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`（这是投研流的权威源）
- 不触碰 Holdout 数据，不触碰 `01_MEMORY_CORE/` 权威文件
