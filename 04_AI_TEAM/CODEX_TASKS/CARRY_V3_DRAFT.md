# CARRY-V3-DRAFT：起草 Carry 预登记 v3（闭合 CARRY-RR2 六项开口）

**角色：** 实现细化（非核心 thesis 改写）。CTO 已锁定核心重构（§0 历史=feasibility-lock 不耗计数 / 前向 shadow=真确认 / 证据等级上线），**不得改动该重构与机制命题**；只闭合 RR2 仍开的 6 项实现细节。
**输入：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v2.md`（基线）+ `CARRY_RISK_REVIEW_v2.md`（必改）。
**输出：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v3.md`（完整自包含）。

## 须闭合的 6 项（按 RR2 review 逐条，CTO 约束如下）
1. **资本/N 恒等式**：显式写出 sleeve 资本 = 现货本金 + 永续初始保证金 + 闲置缓冲现金 + 事件备用现金 的**恒等关系与初始分配数值化规则**；收益率分母唯一；`N`、保证金、缓冲、备用现金之间无重复计/漏计。给出一张"资本占用表"。
2. **OI 单腿减仓机制**：§3 触发减仓"降至50%"明确**只动现货腿还是双腿**、delta 在减仓期是否仍中性（CTO 约束：减仓=同比例减双腿保持 delta 中性，避免减仓本身制造方向暴露）；成交时点、恢复顺序唯一化。
3. **1H 强平路径 bootstrap**：分档爆仓概率的 2000 条 1 年路径**必须逐 1H 重演短永续腿保证金账本**（维持保证金/补款延迟/强平），而非只对组合收盘 MDD 重采样；写清路径生成如何保留 1H 粒度的保证金动态。
4. **事件清单冻结**：把 §6 事件清单**每个事件的 UTC 起止精确化**（Merge/LUNA/FTX/3AC + 脱锚规则），并写明"新事件只能按预登记规则纳入"的算法。
5. **前向 shadow 确认门**：把 §0 的前向 shadow 升为**可执行的确认协议**：纸面跑多久（最少独立月数）、确认门的统计判据（前向 net E[R] 显著>0 的检验/seed/最小 n）、达到后如何计入证据等级解锁小额真金。
6. **其余 RR2 点**：venue/合约/现货价源/再平衡腿/费率档若 v2 仍有残留歧义一并唯一化；保留 Protocol v1.4 AI 证据三行；日期 2026-06-14。

## 铁律：禁读 HOLDOUT/`01_MEMORY_CORE/`；不跑回测；不改 §0 核心重构与机制命题。完成写 `04_AI_TEAM/TASK_INBOX/CARRY_V3_DRAFT_DONE.json`(task_id=CARRY_V3_DRAFT,status,output_file,items_closed,notes)。**完成后不要自审通过**——v3 须由独立 Reviewer 另轮盲审（CTO 另派）。
