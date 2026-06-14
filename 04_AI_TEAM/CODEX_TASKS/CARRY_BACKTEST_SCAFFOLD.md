# CARRY-SCAFFOLD：Delta 中性 Carry 回测框架脚手架（仅代码+合成单测，不跑真实数据）

**定位：** 为 `CARRY_DELTA_NEUTRAL_PREREG_v1.md` 预先实现可审计回测框架，**等盲审通过 + Holdout 封存后再由独立步骤在真实数据上运行**。本任务**只写代码 + 合成数据单测**，**严禁**在真实 `*_FUNDING_8H.csv` 上跑出 §5 验收数值、严禁读 Holdout、严禁下任何 edge 结论。
**输出：** `06_RESEARCH/CODE/carry/` 下模块 + `tests/` + `06_RESEARCH/RESULTS/20260615_carry_scaffold_selftest.md`。

## 实现（严格按预登记 §2-§4 冻结口径，参数化）
1. **数据加载器**：读 `*_FUNDING_8H.csv` + `*_MARK_1H.csv`（cutoff 参数化，默认 <2024-12-10），UTC，坏行处理。**仅提供接口；单测用合成数据，不实跑真实全样本验收。**
2. **delta 中性组合引擎**：long 现货名义 N + short 永续名义 N；每 8h 结算 funding（short 在 funding>0 收取）；每日 00:00 UTC 检查 |delta 漂移|>5% 再平衡；杠杆≤2x、维持保证金≥3×最低（急涨强平检测：mark 急涨致保证金不足→记强平事件）。
3. **成本模型**：fee 0.10%/边（现货+永续各算）、滑点 0.10%/边（事件档 0.30% 参数）、再平衡换手计 fee、basis 进出场。
4. **A-1×Carry 触发器（§3）**：输入 6h 名义 OI 分位序列；≤0.01 → 该品种仓位减至 50% + 24h refractory；产出"有/无触发器"两套净值以便对比。
5. **指标计算器**：净 E[R]、profit factor、正年比例、几何增长、MDD、按时间三段 WF、cluster/块 bootstrap 单侧 p（块=覆盖 funding 自相关，参数）。**实现但不在真实数据上调用产出验收判决。**

## 单元测试（合成数据，必须全绿）
- delta 中性：价格涨跌时组合 pnl≈funding（价格中性）至少 1 例。
- funding 收取方向：funding>0 时 short 收正、<0 付费。
- 再平衡触发：漂移>5% 触发、≤5% 不触发。
- 成本：双边 fee + 滑点正确扣除。
- 触发器：OI 分位≤0.01 → 减仓 50% + 24h refractory。
- 急涨强平检测：保证金不足触发事件。
- bootstrap：合成已知分布断言 p 值合理。

## 自测报告
`20260615_carry_scaffold_selftest.md`：模块用途、参数默认、单测结果、"待盲审通过+custodian封存Holdout后如何在真实数据上运行"的命令示例、**明确声明：本脚手架未在真实数据上产出任何验收数值或 edge 结论**。

## 铁律：禁读 HOLDOUT/`01_MEMORY_CORE/`；不跑真实数据验收；不改预登记。完成写 `04_AI_TEAM/TASK_INBOX/CARRY_SCAFFOLD_DONE.json`(task_id=CARRY_SCAFFOLD,status,output_files,tests_passed,notes)。可 commit 代码（Claude 复核）。
