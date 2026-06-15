# CARRY-RR4：Carry 预登记 v4 第四轮独立盲审

**角色：** 独立 Risk Reviewer（与 v4 起草者分离）。**对象：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md`
**对照：** `CARRY_RISK_REVIEW_v3.md`（v3 闭 4/6，剩资本/USDT计价账 + 1H强平路径 + 交易小时PnL）。**输出：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v4.md`，结论 APPROVED/NOT APPROVED + 最小必改。

## 逐条裁决（CLOSED/PARTIAL/NOT_CLOSED + 证据§/行）
1. 资本/USDT 计价账：全程 USDT 口径、资本与损益恒等式、USDT 脱锚是否计入、分母唯一。
2. 1H 合成强平路径：2000 路径逐 1H 保证金账本(维持/补款延迟/强平)、buffer_breach/liquidation 两级、seed。
3. 交易小时 PnL 计账：funding/成交/再平衡/强平 损益归属到哪个 8h interval、无重复/漏计、与观测单位一致。
4. 核心重构(历史=可行性复核不耗计数/前向shadow=真确认/不自动上线)是否仍完整；有无新自由度。

## 结论：按"历史可行性复核"标尺，三项 CLOSED 且无新阻塞→APPROVED(可放行历史可行性复核,不耗计数/不上线核心资本);否则 NOT APPROVED + 最小必改。
## 铁律：禁读HOLDOUT/`01_MEMORY_CORE/`/禁改预登记/禁跑回测。完成写`04_AI_TEAM/TASK_INBOX/CARRY_RR4_DONE.json`(task_id=CARRY_RR4,review_conclusion,conditions_closed=x/3,notes)。
