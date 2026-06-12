# REPORT_UNIVERSE_PIT

Generated at: 2026-06-12T07:22:17Z

## 结论

已生成 Binance USDT-M 永续 PIT universe 数据资产：

- DATA: `06_RESEARCH/DATA/UNIVERSE_PIT.csv`
- CODE: `06_RESEARCH/CODE/build_universe_pit.py`
- TEST: `06_RESEARCH/CODE/tests/test_universe_pit.py`

本任务只构建数据资产；未运行策略、信号、回测或统计检验；未读取 HOLDOUT 文件内容；未 git commit。

## 口径

- 主数据源：Binance 官方 `https://fapi.binance.com/fapi/v1/exchangeInfo`
- 过滤条件：`contractType == PERPETUAL`，`quoteAsset == USDT`，`marginAsset == USDT`，排除 `PENDING_TRADING`
- 日期口径：UTC calendar date
- `onboard_date`：UTC 上市日期，PIT 查询中包含当日
- `delist_date`：UTC 下架/交割日期，空值表示仍在市；PIT 查询中退市日为排除边界
- 归档交叉验证：先尝试 `data.binance.vision` 页面声明的 S3 ListBucket 目录枚举；当前代理环境下 S3 TLS 路径失败，脚本自动回退为官方 `data.binance.vision` monthly/daily klines `HEAD` 探测

## 汇总

| metric | value |
|---|---:|
| total rows | 646 |
| active rows (`delist_date` empty) | 527 |
| delisted/settling rows | 119 |
| archive cross-check hits | 646 |
| archive cross-check misses | 0 |
| CSV sha256 | `5c137f6c4a69bad6a9153b9cd5fd6966566ce3bb31f8359c8a8a7fc1060b8848` |

## 各年度上市数

| onboard year | count |
|---:|---:|
| 2019 | 3 |
| 2020 | 67 |
| 2021 | 46 |
| 2022 | 19 |
| 2023 | 96 |
| 2024 | 129 |
| 2025 | 246 |
| 2026 | 40 |

## 已知退市永续抽查

| symbol | onboard_date | delist_date | in CSV |
|---|---:|---:|---:|
| SCUSDT | 2021-04-12 | 2022-06-17 | yes |
| FTTUSDT | 2022-04-14 | 2022-11-14 | yes |
| WAVESUSDT | 2020-08-12 | 2024-06-11 | yes |
| FTMUSDT | 2020-09-24 | 2025-01-06 | yes |
| OMGUSDT | 2020-07-02 | 2025-01-31 | yes |

验收要求“退市合约必须出现，抽查 >=3 个”已满足。

## 现有品种覆盖对照

任务书写“现有 9 品种”。仓库内可审计到的现有 TSMOM/扩样本品种为 8 个：`prepare_tsmom_expansion_data.py` 中 `EXISTING_SYMBOLS = BTCUSDT, ETHUSDT, SOLUSDT`，`NEW_SYMBOLS = BNBUSDT, XRPUSDT, DOGEUSDT, ADAUSDT, LTCUSDT`。未发现可审计的第 9 个品种定义，因此未猜测补入。

| symbol | in universe | onboard_date | delist_date |
|---|---:|---:|---:|
| BTCUSDT | yes | 2019-09-08 |  |
| ETHUSDT | yes | 2019-11-27 |  |
| SOLUSDT | yes | 2020-09-14 |  |
| BNBUSDT | yes | 2020-02-10 |  |
| XRPUSDT | yes | 2020-01-06 |  |
| DOGEUSDT | yes | 2020-07-10 |  |
| ADAUSDT | yes | 2020-01-31 |  |
| LTCUSDT | yes | 2020-01-09 |  |

## PIT 查询验证

单元测试覆盖：

- 上市日前不返回该 symbol
- 上市日返回该 symbol
- 退市日按排除边界不返回该 symbol
- PIT 函数可从 CSV path 读取

真实 CSV spot check：

| date | universe size | BTCUSDT | FTTUSDT | OMGUSDT |
|---:|---:|---:|---:|---:|
| 2019-09-07 | 0 | no | no | no |
| 2019-09-08 | 1 | yes | no | no |
| 2022-11-14 | 133 | yes | no | yes |
| 2025-01-31 | 354 | yes | no | no |
| 2026-06-12 | 527 | yes | no | no |

## 数据缺口与可信度

- `exchangeInfo` 当前返回 646 个已上市 USDT-M perpetual 合约，包含 119 个 `SETTLING` 退市/下架合约；这是本资产的 PIT 日期主来源。
- `data.binance.vision` 官方网页的 `list.js` 声明其目录表来自 `https://s3-ap-northeast-1.amazonaws.com/data.binance.vision`。当前代理 `HTTPS_PROXY=http://127.0.0.1:7897` 下，该 S3 XML 目录枚举路径出现 TLS EOF/证书路径问题，脚本记录失败并回退到官方归档 URL 的 `HEAD` 探测。
- 回退探测仍使用 Binance 官方 `data.binance.vision/data/futures/um/...` 文件路径，646/646 symbol 至少命中一个 monthly 或 daily 1h kline 归档文件。
- `exchangeInfo` 中存在 3 个非 ASCII 官方 symbol：`币安人生USDT`、`我踏马来了USDT`、`龙虾USDT`。CSV 保留官方原 symbol；归档 URL 探测对 path 做 percent-encoding。
- 排除了 `PENDING_TRADING` symbol，因为其尚非历史可交易合约，不应进入 PIT 可交易集合。

## 复算命令

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
python3 06_RESEARCH/CODE/build_universe_pit.py
python3 -m pytest 06_RESEARCH/CODE/tests/test_universe_pit.py -q
```

本次实际验证：

```text
python3 -m pytest 06_RESEARCH/CODE/tests/test_universe_pit.py -q
2 passed in 0.49s

python3 06_RESEARCH/CODE/build_universe_pit.py
rows=646 delisted=119 archive_verified=646
```

## 验收自检

| requirement | status | evidence |
|---|---|---|
| `06_RESEARCH/DATA/UNIVERSE_PIT.csv` | PASS | 646 rows, sha256 above |
| 含已退市/已下架 | PASS | 119 rows with non-empty `delist_date`; SCUSDT/FTTUSDT/WAVESUSDT/FTMUSDT/OMGUSDT present |
| 数据来源标注 | PASS | CSV `source` column |
| 官方 API + 归档交叉验证 | PASS with caveat | `exchangeInfo` main source; S3 enum attempted; official archive `HEAD` fallback verified 646/646 |
| 可复跑脚本 | PASS | `06_RESEARCH/CODE/build_universe_pit.py` |
| 简短 pytest | PASS | `06_RESEARCH/CODE/tests/test_universe_pit.py`, 2 passed |
| UTC | PASS | UTC date conversion from exchangeInfo millisecond timestamps |
| 不改既有文件 | PASS | only new task files/data asset created |
| 不碰 HOLDOUT | PASS | no HOLDOUT file content read |
| 不 git commit | PASS | no commit executed |
