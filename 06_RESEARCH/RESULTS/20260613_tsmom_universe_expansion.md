# C1 TSMOM Universe 扩充可行性评估

生成时间（UTC）：2026-06-13T02:28:36Z

## 结论

状态：**FAILED（网络/代理错误导致 HEAD 结果不完整）**。

当前不能给出 universe 扩充规模建议；需在 `HTTPS_PROXY=http://127.0.0.1:7897` 可用后复跑脚本。

## 口径

- 输入：`06_RESEARCH/DATA/UNIVERSE_PIT.csv`
- 候选筛选：`onboard_date <= 2021-06-30`，且未退市或 `delist_date >= 2024-06-01`；排除当前 v1 8 币。
- HEAD 探测：Binance 官方月度 4H K 线 ZIP，`monthly/klines/<symbol>/4h/<symbol>-4h-YYYY-MM.zip`。
- 探测次数：每个 symbol 两次，首月为 onboard 月，近月为 `2024-11` 或退市前月。
- 估算 bars：`(min(2024-12-09 23:59:59, delist前一秒) - onboard) / 4h * 0.95`。
- 网络：必须经 `HTTPS_PROXY=http://127.0.0.1:7897`；不下载 ZIP。

## 汇总统计

- 总候选数：`88`
- 首月可得数：`NA`（HEAD 存在网络不确定结果）
- 近月可得数：`NA`（HEAD 存在网络不确定结果）
- 两端均可得数：`NA`（HEAD 存在网络不确定结果）
- 网络不确定 symbol 数：`88`

## 可建库候选

无可建库候选可列示（或 HEAD 结果不完整）。

## 产物

- `06_RESEARCH/CODE/c1_tsmom_universe_feasibility.py`
- `06_RESEARCH/CODE/output/c1_tsmom_universe_candidates.csv`
- `06_RESEARCH/CODE/output/c1_tsmom_universe_summary.json`

## 禁止项自检

- 未下载 ZIP。
- 未读取 `HOLDOUT` 路径。
- 未读取 `*_2026H1` 行情文件。
- 未计算收益、信号或回测。
- 未执行 git commit。
