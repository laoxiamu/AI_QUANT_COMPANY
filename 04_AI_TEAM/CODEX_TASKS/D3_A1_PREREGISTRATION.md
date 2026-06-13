# D3：A-1 正式预登记文档起草

**任务类型：** 文档生成（分析+写作）  
**优先级：** 高，独立于 D1/D2，立即启动  
**输出文件：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v1.md`

---

## 背景

A-1（强制流两相位/清算级联后回弹）是项目当前唯一的 Conditional 方向，也是独立 Alpha 计数中的关键候选。预登记须通过四道门：

1. **数据质量门** ✅（B3/B4 结果确认数据可用）
2. **功效门（MDE）** ✅（B4：n=163，MDE 24/48h 均 < 1.5%）
3. **A-2 尸检碰撞门** — 必须在预登记中明确处理
4. **Risk Reviewer 物理盲审门** — 预登记完成后由独立视角审核

本任务完成第三道门的文档化，生成供 Risk Reviewer 审核的预登记文档。

---

## 必须生成的文档结构

文件路径：`06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v1.md`

### 必须包含的 10 个部分：

**§1 机制假设**
- 精确的因果链：强制平仓（机械事件）→ 临时超额供给 → 价格 overshooting → 主动买方回归 → 均值回归
- 明确区分：这是"事件后均值回归"，不是"预测事件何时发生"

**§2 触发定义（冻结，不可修改）**
- 信号：6h OI 骤降，滚动分位 ≤ 0.01（365天窗口，最少180天，midrank）
- 品种：BTCUSDT, ETHUSDT, SOLUSDT（池化）
- 截止：< 2024-12-10T00:00:00Z
- Episode 合并规则：同品种距上一触发 ≤ 24h 归为同一 episode
- 工作集 n = 163（池化 203 扣除 Holdout 40）

**§3 Regime Gate**
- 继承 P1-06 验收口径的 regime 定义（牛市/熊市状态）
- 说明：A-1 在熊市 regime 下的效应可能与牛市不同，子样本分析为辅助检验

**§4 检验设计（主检验 + 辅检验）**

主检验：
- 指标：Cumulative Abnormal Return（CAR），对数收益，相对于事件前基准期（-72h ~ -1h）
- Horizons：24h, 48h, 72h
- 检验：单侧 t-test，H0: CAR ≤ 0，H1: CAR > 0，α = 0.05
- 单位：池化，每个 episode 一个观测值

辅检验 1（单调性）：
- 按 OI 骤降幅度（d6h_rolling_pctl）分三档，检验 CAR 是否单调递增
- 预期：骤降越剧烈，回弹幅度越大

辅检验 2（A-2 碰撞门分层）：
- 将 episode 按"事件前 24h funding rate 分位"分为高 funding / 低 funding 两组
- 分别计算 CAR，检验两组方向是否一致
- 预期：无论 funding 高低，CAR 均为正（证明 A-1 机制独立于 funding 状态）

辅检验 3（成本压力档）：
- 0.05% / 0.1% / 0.2% 三档交易成本下的 net CAR
- 验收要求：0.1% 档下 CAR 仍显著

**§5 功效段（MDE）**
- 引用 B4 结果：alpha-only 公式，n=163，MDE_24h=0.625%，MDE_48h=0.872%，MDE_72h=1.073%
- 说明正式检验采用 alpha-only 口径（α=0.05 单侧，不加 power 项）
- 注：alpha+beta（80% power）时 72h MDE=1.622% > 1.5% 下沿，但 24h/48h 仍通过

**§6 第五件：被动基准对照**
- 基准：同 regime 条件下，不使用 OI 信号，被动持有同样品种的 buy-and-hold
- 计算方式：在 A-1 触发 episode 对应的 regime 窗口内，计算基准的平均 CAR
- 验收：A-1 CAR > 基准 CAR（超额存在）

**§7 A-2 碰撞门声明**
- 引用并摘要 `06_RESEARCH/RESULTS/20260613_a1_vs_a2_mechanism_diff.md` 的核心区分
- 明确写出：A-2 失败根因（timing 问题）vs A-1 机制（已发生事件后的均值回归）
- 碰撞门处理方案：funding 分层辅检验（§4 辅检验2）是本预登记对碰撞门的操作化响应

**§8 Holdout 声明**
- A-2 Holdout（a2_events_holdout.csv，218 条）：与本研究完全独立，本研究不读取
- A-1 Holdout：从 203 个 episodes 中按第 5 个预留（floor(203/5)=40 个），物理隔离
- Holdout 隔离方法：按 episode index 预留，不按时间前后切，防止 regime 偏差
- 禁止在任何分析步骤前读取 Holdout

**§9 验收标准（明确量化）**

通过条件（全部满足）：
- [ ] 主检验 24h 或 48h CAR > 0，单侧 p < 0.05
- [ ] 0.1% 成本档下 net CAR > 0
- [ ] 第五件：A-1 CAR > 被动基准 CAR
- [ ] A-2 碰撞门：高 funding / 低 funding 子样本 CAR 方向一致（均正或均不显著负）
- [ ] WF：3 段中至少 2 段 CAR > 0

失败条件（任一满足即 FAILED）：
- 主检验 24h + 48h CAR 均不显著（p ≥ 0.05）
- 第五件：A-1 CAR ≤ 被动基准 CAR
- A-2 碰撞门：高 funding 子样本 CAR 显著为负

**§10 失败后禁止行为（预登记锁死）**

若本预登记 FAILED：
- 禁止修改 OI 骤降阈值（如从 P1 改为 P2 或 P5）重测
- 禁止更换 episode 合并规则后重测
- 禁止排除特定年份子样本后重测
- 允许：若功效不足，等待前向强平采集数据 3-6 个月后以更大 n 重新立项

---

## 参考文件（必须读取）

```
06_RESEARCH/RESULTS/20260612_a1_mde_precheck.md        # 功效数据
06_RESEARCH/RESULTS/20260613_a1_vs_a2_mechanism_diff.md # 碰撞门材料
06_RESEARCH/RESULTS/20260613_a1_framework_report.md     # 框架代码说明
06_RESEARCH/CODE/a1_event_study_framework.py            # 实现参考
01_MEMORY_CORE/CURRENT_STATE.md                         # 验收口径（v1.3/v1.4）
```

## 禁止项

- 不运行事件研究（不计算真实 CAR）
- 不读取 HOLDOUT 目录
- 不修改任何现有文件
- 只生成预登记文档
