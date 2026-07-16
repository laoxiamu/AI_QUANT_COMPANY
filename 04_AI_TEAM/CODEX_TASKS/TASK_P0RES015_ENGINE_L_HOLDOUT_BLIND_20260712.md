# TASK P0-RES-015 — TSMOM 引擎L（10%目标波动率点）Holdout 一次性盲验

**ID：** P0-RES-015 ｜ **日期：** 2026-07-12 ｜ **授权：** DEC-093（Founder 2026-07-12 批准消耗 Holdout）
**性质：** 既有候选的终局验收步骤（预登记盲验），**不消耗独立试验计数**；家族=TSMOM（DEC-092 复查链 P0-RES-006/014 的收尾）。
**执行人：** Codex（编写 runner + 执行 + 出报告）｜ **验收人：** Claude ｜ **判据：本文件写定即冻结，执行中不得修改任何判据/窗口/参数。**

---

## 0. 七问前置审查（Claude，出任务书时完成）

① 验证什么机制：宏观牛市门控下的时序动量（趋势延续）在样本外是否仍然成立。② 现有证据：DEC-092 复查七项检查全过（P0-RES-006/014），项目唯一走完全流程候选，支持进入终局验收。③ 更上游问题：无——Holdout 盲验就是该候选当前最上游的未答问题。④ 变量作用于目标：直接（同一冻结引擎，仅换未见数据）。⑤ 失败区分力：能——过=获得唯一样本外证据；不过=候选证伪，不存在"改参数解释"空间（判据冻结）。⑥ 更高信息增益实验：无（这是当前全项目信息增益最高的单个实验）。⑦ 异议：无；风险=样本外窗口 ~1.47 年功效有限，已在 §5 诚实量化并预先接受。

## 1. 盲验对象（全部冻结，禁止任何改动）

- **策略：** `06_RESEARCH/CODE/tsmom_dual_engine.py` 引擎 L（宏观牛市门控多头 TSMOM），**冻结代码路径**，禁止修改该文件本身。
- **仓位点：** 仅 **10% 目标波动率** 一个点（P0-RES-006 已登记、P0-RES-014 主口径点）。**15% 点不跑**（Holdout 只用一次，防择优）。
- **重构方式：** 沿用 `p0res014_engine_l_benchmark_recheck_20260706.py` 的既有重构代码路径（同 warm-up、同成本 FEE=0.001/SLIPPAGE=0.001、同 funding、同 universe 8 symbol：BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LTC、LEVERAGE_CAP=1.0）。禁止改动 lookback / ADX / macro gate / universe / 成本 / funding 任何一项。

## 2. Holdout 窗口与数据边界（冻结）

- **Holdout 评估窗：** `2024-12-10 00:00 UTC` → `2026-05-31 20:00 UTC`（mark 4H 收盘）；funding 用到 `2026-05-31 16:00 UTC`。
- **数据源：** `06_RESEARCH/DATA/FUTURES/{SYM}USDT_MARK_4H.csv` 与 `{SYM}USDT_FUNDING_8H.csv` 全行数读取（本任务 runner 获 DEC-093 一次性授权解除 `PRE_CUTOFF_ROWS` 截断；**只允许在新 runner 内实现自己的 loader，不得改 `tsmom_dual_engine.py` 的 `read_csv_until_cutoff`/`safe_market_path`**）。
- **禁用：** `*_2026H1*` 增量文件（仅 3/8 symbol、仅 5 天，破坏共同窗口）；`DATA/HOLDOUT/`（a2 事件级，与本任务无关）；`~/.aiquant_sealed/`。
- **Warm-up：** 指标暖机（540 bars lookback / 200D MA / ADX）允许并应使用 cutoff 前数据，全历史连续运行引擎；**盲验计量只取 Holdout 窗内**。
- **计量口径：** 窗口起点权益 rebase（等效初始资金 100,000）；跨界持仓（cutoff 时在场的仓位）其窗内损益按窗口起点 mark 价起算计入权益曲线；**交易级统计（H1）只计窗内入场的交易**，跨界交易单独列示不入 H1。

## 3. 通过/失败判据（四门全过=PASS，任一不过=FAIL；写定即冻结）

| 门 | 判据 | 冻结参数 |
|---|---|---|
| **H1 正期望（生存底线）** | Holdout 窗内入场交易的单笔 E[R] > 0（净额：扣手续费+滑点+funding） | 成本模型与样本内完全一致 |
| **H2 几何增长** | Holdout 窗年化对数增长率 > 0（10%点，rebase 权益曲线） | — |
| **H3 风险声明检验** | Holdout 窗实现最大回撤 < 20%（对应样本内声称 P(年DD≥20%)=2.60%；1.47年窗触发概率≈4%，触发即高置信证伪风险声明） | DD 按窗内 rebase 权益峰谷 |
| **H4 v1.5 第5件** | 同门控被动基准（`prepare_passive_dataset("L")` 同法重构至 Holdout 窗、同 rebase），双方各自缩放到 10% 年化波动率后比较年化 log 增长；paired moving-block bootstrap 判"策略显著跑输"不成立（diff 95%CI 上界 ≥ 0 即过；上界 < 0 = FAIL） | 块长 42 根 4H；5000 次；**seed=20260712** |

- **PASS 含义：** 获得唯一一份样本外证据，晋级 paper-forward 前向纸面记录。**≠ edge 已证实，不碰核心资本。**
- **FAIL 含义：** 引擎 L 真正判死，写回墓园，不可复活，禁开任何变体。
- **诊断输出（只报告不判定）：** 窗内交易数、赢均/亏均、分季度收益、funding 贡献、跨界交易明细、与样本内点估计的对比。若窗内交易数 < 10，如实标注低功效，但判据仍按本预登记执行。

## 4. 一次性纪律（反续命，冻结）

1. **一次执行：** 脚本一次跑完，结果无论好坏当轮落盘（JSON + 报告）。禁止看结果后改窗口/参数/判据/仓位点重跑。唯一允许的重跑=代码 bug 致崩溃或输出自检不一致，且修复 diff 须完整记录进报告、判据零改动。
2. **Hash 冻结：** runner 执行开始时记录并写入报告：本任务书、`tsmom_dual_engine.py`、`p0res014_engine_l_benchmark_recheck_20260706.py`、16 个数据文件（8×MARK_4H+8×FUNDING_8H）的 SHA256。
3. **自检（报告必含）：** ①10%点在 cutoff 前区段的重构结果与 P0-RES-006/014 登记值完全一致（ending equity / ann log growth 对账）；②数据末行时间戳列表；③未读 `*_2026H1*`、`DATA/HOLDOUT/`。
4. **Holdout 封账：** 本次运行后，引擎 L 对本 Holdout 窗的任何再评估永久禁止（无论 PASS/FAIL）。

## 5. 功效诚实声明（预先接受，不得事后引用为翻案理由）

窗口 ~1.47 年、目标波动率 10%：若真实效应=样本内点估计（年化 log 增长 ~18%），H2 通过概率 ≈98%；若真实效应减半，≈85%。四门合计"真 edge 被假杀"概率粗估 ~10–15%，**预先接受为一次性盲验的代价**；同理 FAIL 后不得以"低功效"为由申请复活。

## 6. 交付物

1. Runner：`06_RESEARCH/CODE/p0res015_engine_l_holdout_blind_20260712.py`（自实现可审计小函数，禁黑箱依赖，DEC-061）
2. 审计 JSON：`06_RESEARCH/CODE/output/p0res015_engine_l_holdout_blind_20260712.json`
3. 报告：`04_AI_TEAM/CODEX_TASKS/REPORT_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712.md`（含四门判定表、诊断表、hash 表、自检节）
4. 完成信号：`04_AI_TEAM/TASK_INBOX/P0RES015_DONE.json`（status=PASS/FAIL/ERROR + 一句话结果）

**结果判定权：** runner 只输出四门布尔值与数字；PASS/FAIL 的正式裁决与墓园/机会地图写回由 Claude 验收后执行。
