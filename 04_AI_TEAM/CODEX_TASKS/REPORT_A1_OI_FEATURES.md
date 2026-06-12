# REPORT_A1_OI_FEATURES

生成时间（UTC）：2026-06-12T00:49:32Z

## 交付物

- CODE：`06_RESEARCH/CODE/features/a1_oi_features.py`
- TEST：`06_RESEARCH/CODE/features/test_a1_oi_features.py`
- RESULTS：`06_RESEARCH/CODE/output/a1_oi_features_BTCUSDT.csv`
- RESULTS：`06_RESEARCH/CODE/output/a1_oi_features_ETHUSDT.csv`
- RESULTS：`06_RESEARCH/CODE/output/a1_oi_features_SOLUSDT.csv`

## 实现口径

- 数据源仅为 `06_RESEARCH/DATA/FUTURES/{SYM}_METRICS_5M.csv`。
- 读取列仅为 `create_time` 与 `sum_open_interest`。
- `sum_open_interest` 按 UTC 1H 重采样，取每小时最后一条；缺口小时保留 `NaN`，不前向填充。
- `d6h_pct` / `d24h_pct` 使用 `pct_change(periods=6/24, fill_method=None)`。
- 滚动分位复用 `features.a2_funding_features.add_rolling_percentiles`，继承 365 天窗口、最少 180 天起算、midrank、仅使用 t 之前样本的口径。
- 本任务未实现事件提取、阈值选择、Holdout 切分或收益计算。

## 覆盖与缺口

| Symbol | Coverage UTC | Rows | Expected 1H rows | Warmup rows | OI gap hours | First gap | Last gap |
|---|---:|---:|---:|---:|---:|---|---|
| BTCUSDT | 2020-09-01T00:00:00Z to 2026-06-06T00:00:00Z | 50497 | 50497 | 4344 | 22 | 2021-01-20T01:00:00Z | 2024-02-16T23:00:00Z |
| ETHUSDT | 2021-12-01T00:00:00Z to 2026-06-06T00:00:00Z | 39553 | 39553 | 4344 | 10 | 2024-02-16T14:00:00Z | 2024-02-16T23:00:00Z |
| SOLUSDT | 2021-12-01T00:00:00Z to 2026-06-06T00:00:00Z | 39553 | 39553 | 4344 | 10 | 2024-02-16T14:00:00Z | 2024-02-16T23:00:00Z |

说明：`warmup` 标记滚动分位尚未满足 180 天历史要求的 1H 行；ETH/SOL 覆盖始于 2021-12-01。

## 复算命令

```bash
python3 06_RESEARCH/CODE/features/a1_oi_features.py
python3 -m pytest 06_RESEARCH/CODE/features/test_a1_oi_features.py 06_RESEARCH/CODE/features/test_a2_features.py
```

## 验收自检

- pytest：`5 passed in 1.49s`。
- 无前视测试：构造序列验证 t 分位不含当前值进入历史样本，且扰动 t+1 不改变 t 分位；同时验证测试对 t+1 扰动非恒真。
- 重采样测试：5M 到 1H 取小时最后值；中间缺口小时为 `NaN`，无前向填充。
- UTC：输出 `ts` 均为 `YYYY-MM-DDTHH:MM:SSZ`。
- 行数：三个输出均等于各自覆盖区间的完整 1H 网格。
- 数据边界：A-1 脚本只读取 FUTURES METRICS 文件；未读取 MARK、FUNDING、HOLDOUT 或其他数据目录。
- 禁止项：未新增事件、阈值、Holdout、收益代码路径；未修改 A-2 既有模块；未执行 git commit。
