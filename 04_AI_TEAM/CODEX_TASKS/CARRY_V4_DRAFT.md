# CARRY-V4-DRAFT：起草 Carry 预登记 v4（闭 CARRY-RR3 剩余 + 新堵点）

**角色：** 实现细化（不改 §0 核心重构：历史=可行性复核不耗计数/前向shadow=真确认/证据等级上线）。
**输入：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v3.md`（基线，已闭 4/6）+ `CARRY_RISK_REVIEW_v3.md`（剩余必改）。
**输出：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md`（完整自包含）。

## 须闭合（按 CARRY_RISK_REVIEW_v3 逐条）
1. **资本 / USD-USDT 计价账（仍 PARTIAL）**：冻结全程计价单位与折算——现货以 USDT 计、永续 USDT 本位保证金、sleeve 资本分母、funding 结算名义、强平损益、basis MTM 全部统一到 USDT 口径；写明 USDT 脱锚情形是否计入（事件风险）。给出无歧义的资本与损益恒等式。
2. **1H 合成强平路径重建（仍 PARTIAL）**：把分档爆仓概率的 2000 条 1 年路径**精确化**：如何从历史 1H mark 序列 + 块 bootstrap 生成保留 1H 保证金动态的合成路径、维持保证金/补款延迟/强平判定的逐 1H 算法、buffer_breach 与 liquidation 两级、随机种子。
3. **交易小时 PnL 计账（RR3 新堵点）**：冻结"在哪个 bar 计入 funding / 成交 / 再平衡 / 强平 损益"的唯一规则——funding 8h 结算 interval、成交在 t+1 open、损益归属到哪个 interval，避免重复计或跨 bar 漏计；与 §5 观测单位(8h interval)一致。
4. 其余 RR3 残留歧义一并唯一化；保留 AI 证据三行；日期 2026-06-14。

## 铁律：禁读HOLDOUT/`01_MEMORY_CORE/`；不跑回测；不改§0核心重构。完成不自审通过。写 `04_AI_TEAM/TASK_INBOX/CARRY_V4_DRAFT_DONE.json`(task_id=CARRY_V4_DRAFT,status,output_file,items_closed,notes)。
