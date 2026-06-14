# CARRY-RR3：Carry 预登记 v3 第三轮独立盲审

**角色：** 独立 Risk Reviewer（与 v3 起草者分离）。**审查对象：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v3.md`
**对照：** `CARRY_RISK_REVIEW_v2.md`（v2 闭 2/8，余 6 项）。**输出：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v3.md`，结论 APPROVED/NOT APPROVED + 最小必改。

## 逐条裁决 RR2 仍开的 6 项是否在 v3 闭合（CLOSED/PARTIAL/NOT_CLOSED + 证据§/行 + 仍缺）
1. **资本/N 恒等式**：sleeve 资本=现货本金+永续保证金+缓冲+事件备用 的恒等与数值化、收益率分母唯一、无重复/漏计、资本占用表。
2. **OI 双腿减仓**：触发减仓是否双腿同比例保持 delta 中性（避免减仓制造方向暴露）、成交时点、恢复顺序唯一。
3. **逐 1H 强平路径 bootstrap**：2000 条 1 年路径是否逐 1H 重演短永续腿保证金账本（维持保证金/补款延迟/强平），非仅组合收盘 MDD。
4. **事件清单**：每事件 UTC 起止精确、新事件纳入算法冻结。
5. **前向 shadow 确认门**：最少独立月数、统计判据/seed/最小 n、证据等级解锁路径是否可执行。
6. **其余 RR2 执行歧义**：venue/合约/现货价源/再平衡腿/费率档唯一化；AI 证据三行；日期。

## 第二部分：v3 是否引入新缺陷或新自由度；核心重构（历史=可行性复核/前向shadow=真确认/不耗计数/不自动上线）是否仍完整未被稀释。
## 结论：按"历史可行性复核"标尺（非独立确认级），6 项均 CLOSED 且无新阻塞→APPROVED(可放行历史可行性复核,明确不耗计数不上线核心资本)；否则 NOT APPROVED + 最小必改。

## 铁律：禁读HOLDOUT/`01_MEMORY_CORE/`/禁改预登记/禁跑回测。完成写`04_AI_TEAM/TASK_INBOX/CARRY_RR3_DONE.json`(task_id=CARRY_RR3,review_conclusion,conditions_closed=x/6,notes)。
