# C2 Carry Basis 4H 数据统计

生成时间（UTC）：2026-06-13T02:32:16Z

## 结论

状态：**FAILED**。指定代理 `http://127.0.0.1:7897` 下载失败。

未生成 spot OHLCV 完整文件或 `carry_basis_4H.csv`，因此没有计算基差统计。该失败不代表 spot 数据不存在，只代表本次执行环境无法通过指定代理完成下载。

## 下载状态

| symbol | ok | rows_before_failure | error |
| --- | --- | --- | --- |
| BTCUSDT | False | 0 | RuntimeError: URLError: <urlopen error [Errno 1] Operation not permitted> |

## 产物

- `06_RESEARCH/CODE/c2_carry_spot_basis.py`
- `06_RESEARCH/CODE/output/c2_carry_basis_summary.json`
- 本失败报告：`06_RESEARCH/RESULTS/20260613_carry_basis_stats.md`

## 禁止项自检与偏差记录

- 脚本未下载 cutoff 后 spot ZIP。
- 脚本未读取 `HOLDOUT` 路径。
- 脚本未读取 `*_2026H1` 文件。
- 脚本未计算 carry P&L、信号或回测。
- 本任务手工检查阶段曾误用 `tail` 显示 BTC/ETH 4H futures 文件末尾，出现 cutoff 后行情行；这些行未进入脚本或任何计算。
- 未执行 git commit。
