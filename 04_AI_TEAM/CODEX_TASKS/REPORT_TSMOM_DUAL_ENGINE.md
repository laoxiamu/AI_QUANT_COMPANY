# REPORT_TSMOM_DUAL_ENGINE

## 验收自检

- pytest 全绿：`MPLCONFIGDIR=/tmp/mplconfig NUMBA_DISABLE_JIT=1 python3 -m pytest 06_RESEARCH/CODE/tests/test_tsmom_dual_engine.py 06_RESEARCH/CODE/tests/test_p1_06_tsmom_macro_bull.py 06_RESEARCH/CODE/tests/test_tsmom_regime_long.py 06_RESEARCH/CODE/tests/test_tsmom_voltarget.py 06_RESEARCH/CODE/tests/test_tsmom_rules.py -q`，30 passed。
- 参数与 P1-06 对照表：已写入 RESULTS 报告。
- 引擎 L/S 独立二值判定：已写入 RESULTS 报告。
- 策略数据边界：回测脚本未读取 `*_2026H1` 文件，未解析 2024-12-10 之后行情/资金费；所有使用数据末条 timestamp 已列出且 <= 2024-12-09 23:59 UTC。
- 全局 Holdout 自证：FAILED。本次 Codex 会话曾因一次仓库级 `rg` 范围过宽命中 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv` 并显示若干行；未用于 TSMOM 计算，但不能声称本轮完全未碰 Holdout。
- no-holdout lint：`bash scripts/no_holdout_lint.sh` 退出码 0；该 lint 不覆盖本次人工 `rg` 输出事故。
- 预登记/任务书/AGENTS.md：未修改。
- git commit：任务书要求 no git commit，本轮未 commit。

## 结论

- L: FAILED
- S: FAILED
