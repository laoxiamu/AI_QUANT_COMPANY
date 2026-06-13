# C3 A-1 事件研究框架报告

生成时间（UTC）：2026-06-13T02:36:00Z

## 结论

状态：**COMPLETED**。已在 B4 MDE 报告末尾追加 alpha-only / alpha+beta 双参数对照表，并新增 A-1 事件研究框架与合成数据 pytest。

## MDE 双参数补充

- 已追加到 `06_RESEARCH/RESULTS/20260612_a1_mde_precheck.md`，未改动原有 B4 内容。
- alpha-only：24h/48h/72h 均通过 1.5% 机制区间下沿。
- alpha+beta（α=0.05 单侧、power=0.8）：24h/48h 通过，72h 为 `1.622%`，不通过 1.5% 下沿。

## 代码框架

- `06_RESEARCH/CODE/a1_event_study_framework.py`
- `load_episodes(path: str) -> pd.DataFrame`
- `align_windows(episodes, price_df, horizons=[24,48,72]) -> pd.DataFrame`
- `compute_car(window_df) -> pd.DataFrame`
- `monotonicity_test(window_df, quantile_col) -> pd.DataFrame`
- `permutation_test(window_df, n_perm=10000, seed=42) -> dict`
- `run_full_study(episode_path, price_path, cutoff) -> dict`

硬约束已写入：`run_full_study` cutoff assert、`align_windows` price cutoff assert、HOLDOUT path assert/注释。框架未运行真实事件数据。

## pytest 输出

```text
$ python3 -m pytest 06_RESEARCH/CODE/tests/test_a1_event_study.py -q
....                                                                     [100%]
4 passed in 0.39s
```

## 禁止项自检

- 未读取 `HOLDOUT` 路径。
- 未读取真实行情数据。
- 未运行 A-1 实际事件研究。
- 未计算任何真实事件收益。
- 未修改预登记文档。
- 未执行 git commit。
