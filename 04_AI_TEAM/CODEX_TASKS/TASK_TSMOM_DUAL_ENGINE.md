# TASK_TSMOM_DUAL_ENGINE —— TSMOM 扩样本·多空双引擎回测

**发包：** Claude 2026-06-12 ｜ **口径权威：** 预登记 `06_RESEARCH/HYPOTHESES/tsmom_expansion_dual_engine_v1.md`（逐条遵守，本文不复述）+ AGENTS.md + Protocol v1.3/v1.4 增补件。

## 实现要点
1. 复用 `06_RESEARCH/CODE/p1_06_tsmom_macro_bull.py` 的冻结逻辑（参数零改动），扩 universe 至 8 品种（数据：FUTURES/ 下 MARK_4H 与 FUNDING_8H）。**〔勘误 2026-06-12，随预登记勘误同步〕评估窗口=各自上市→2024-12-09 23:59 UTC：代码硬编码 cutoff，加载后立即截断；*_2026H1 增量文件与 2024-12-10 之后的任何行情数据一律禁读（它们是家族确认级 Holdout）；报告须印出每品种实际使用的末条时间戳以证明未越界。** 上市满 540 根 4H 才可入场（PIT 规则，参照 UNIVERSE_PIT.csv）。
2. 引擎 S=严格镜像实现（做空、SMA200下方、close<close[t-540]、ADX同参；funding 方向正确结算）。
3. 输出：每引擎 trades/equity/metrics（命名 tsmom_dual_L_* / tsmom_dual_S_*）+ 四件套与第五件基准对照计算（块bootstrap seed=20260612）+ WF 三段 + P1-04/P1-06 基准对照追溯 + L/S 相关性与组合描述。
4. pytest：镜像逻辑对称性（构造序列：上涨样本 L 触发 S 不触发，反之）；PIT 入场规则；funding 方向结算正误用例。
5. 报告：`06_RESEARCH/RESULTS/20260612_tsmom_dual_engine.md`（两引擎独立判定 PASSED/FAILED，按预登记失效条款，禁模糊）+ REPORT_TSMOM_DUAL_ENGINE.md（验收自检）。

## 验收
pytest 全绿；参数与 P1-06 逐项一致的对照表；判定二值；未碰 Holdout；未改既有文件；no git commit。
