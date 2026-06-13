# REPORT_B1

## 任务

- 执行 B1：v2 风险预算版回测；其他批次任务未执行。
- 预登记：`06_RESEARCH/HYPOTHESES/tsmom_dual_engine_v2_riskbudget.md`。
- 实现：复用 `06_RESEARCH/CODE/tsmom_dual_engine.py`，新增 `--riskbudget-v2` 可复跑入口。

## 七问自查

- 机制：验证 v1 引擎 L 的定仓风险预算是否降低爆仓概率且保留正期望。
- 验收可量化：四件套 + 第五件 + WF 三段，全过才 PASSED。
- 更便宜实现：在既有脚本中加单变量缩放与报告入口，未另起框架。
- 禁止项：未读 HOLDOUT，未读 `*_2026H1`，未改预登记，未调参，未引黑箱依赖。

## 验收自检

- B1 判定：FAILED。
- E[R] > 0：True (0.016321)。
- 赢亏比 >= 1.5：True (2.074)。
- 分档爆仓概率：DD35=0.003 pass=True；DD20=0.174 pass=False。
- 年化 log 增长 > 0：True (0.293)；分年正期望多数：True (4/4)。
- 第五件基准超额 > 0：False (-992784.95)。
- WF：2/3 positive，pass=True。
- k_t <= 1：True；σ_t prior-only：True。
- cutoff：所有行情/资金费末条 <= 2024-12-09 23:59:00 UTC。
- pytest：`MPLCONFIGDIR=/tmp/mplconfig NUMBA_DISABLE_JIT=1 python3 -m pytest 06_RESEARCH/CODE/tests/test_tsmom_dual_engine.py -q`，8 passed。
- git commit：批次书要求全程禁 git commit，本任务未 commit。

## 产出

- `06_RESEARCH/RESULTS/20260612_tsmom_v2_riskbudget.md`
- `04_AI_TEAM/CODEX_TASKS/REPORT_B1.md`
- `06_RESEARCH/CODE/output/tsmom_v2_riskbudget_L_metrics.json`
