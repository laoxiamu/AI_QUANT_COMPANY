# CARRY-RR2：Delta 中性 Carry 预登记 v2 第二轮独立盲审

**角色：** 独立 Risk Reviewer，只审设计。**审查对象：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v2.md`
**对照：** `CARRY_RISK_REVIEW_v1.md` 八项最小必改。**输出：** `06_RESEARCH/PREREGISTRATIONS/CARRY_RISK_REVIEW_v2.md`，结论 APPROVED / NOT APPROVED + 最小必改。

## 逐条裁决 RR1 八项必改是否闭合（CLOSED/PARTIAL/NOT_CLOSED + 证据§/行 + 仍缺）
1. **研究身份/独立性**：v2 §0 把历史段降为"可行性复核(feasibility-lock)、不耗计数、不上线"，真确认交前向 shadow，上线走 DEC-069 证据等级——这个重构是否真正消除了"用已探索工作集做确认"的 HARKing？feasibility-lock 的定性是否自洽、是否仍有把历史 PASS 当确认的残留措辞？
2. **构造唯一化**：§2 venue=Binance/现货用现货1H close非mark/N=初始分配名义/再平衡现货腿次根open/杠杆1.0全仓/缓冲=维持×3/补款延迟/强平公式/basis路径账本——是否还有不唯一处？
3. **OI触发器**：§3 变量(d6h下尾分位)/状态机/配对非劣检验(δ=0.5%)/唯一尾部硬门(事件期liquidation次数严格减少)——是否闭合？基础carry先独立过门、禁有无触发器择优 是否守住？
4. **成本逐腿逐成交**：§4 是否每笔成交单独计fee+slippage、financing冻结为0、事件压力0.3/0.5/1.0、basis/ADL/脱锚入账？
5. **验收四件套闭合**：§5 赢亏比≥1.5/分档爆仓概率(标准35%@20%+保守20%@10%,路径级短腿强平)/年化log growth/现金零/MDD≤15%/唯一WF/N.A.→FAIL/观测单位=8h interval/多变量同步块bootstrap+seed——是否齐全唯一？
6. **功效门**：§8 n_eff/4-5独立年/合理净edge上限(事前经济5-12%非工作集反推)/MDE——v2 是否诚实承认历史段功效弱、并据此不以历史耗计数？该逻辑是否成立？
7. **事件+Holdout权限**：§6 冻结事件清单(Merge/LUNA/FTX/3AC/脱锚规则)+路径级强平硬门；§7 全输入同cutoff+SHA+执行身份永久不可读——是否闭合？
8. **审计元数据**：日期改回2026-06-14、AI证据三行是否补齐？

## 第二部分：v2 新结构(feasibility-lock+前向shadow确认+证据等级上线)是否引入新缺陷或新自由度。
## 结论：APPROVED(可放行历史可行性复核,明确不耗计数不上线)/NOT APPROVED(最小必改)。按"可行性复核"标尺，不要求达独立确认级严格度，但复核结论须无偏可复现。

## 铁律：禁读HOLDOUT/`01_MEMORY_CORE/`/禁改预登记/禁跑回测。完成写`04_AI_TEAM/TASK_INBOX/CARRY_RR2_DONE.json`(task_id=CARRY_RR2,review_conclusion,conditions_closed=x/8,notes)。
