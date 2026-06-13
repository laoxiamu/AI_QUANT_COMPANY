# A-4 新上市数据普查

Generated: 2026-06-12 16:58:50 UTC

## 结论

- `UNIVERSE_PIT.csv` 共 646 个 Binance USDT-M 永续合约；2022 起新上市 530 个。
- 已成熟的“上市后 30 天”窗口 524 个，K 线与 funding 归档均可得 472 个，可得率 90.08%。
- 未成熟窗口 6 个，未纳入可得率分母。
- 本任务只做计数与 HEAD 可得性探测；未下载 zip、未读取行情内容、未计算收益/波动/信号。

## 口径

- 数据源：`06_RESEARCH/DATA/UNIVERSE_PIT.csv`
- 范围：按 `onboard_date` 统计全部年份上市数；对 `onboard_date >= 2022-01-01` 的合约做归档探测。
- K 线：`data.binance.vision/data/futures/um/daily/klines/<symbol>/1h/`，上市日起最多 30 个 UTC 自然日逐日 `HEAD`。
- Funding：官方归档实际为 monthly `fundingRate` ZIP；对覆盖上市后 30 天窗口的月份做 `HEAD`。
- 退市边界：若合约上市 30 天内退市，期望窗口截到 `delist_date` 前一日。
- 当前 UTC 日尚未走完或 30 天窗口未结束的合约标为未成熟，不纳入可得率分母。
- 网络：`HTTPS_PROXY=http://127.0.0.1:7897`。

## 分年新上市数量

| year | new_listings |
| --- | --- |
| 2019 | 3 |
| 2020 | 67 |
| 2021 | 46 |
| 2022 | 19 |
| 2023 | 96 |
| 2024 | 129 |
| 2025 | 246 |
| 2026 | 40 |

## 2022 起前 30 天归档可得率

| year | listed | matured | kline complete | funding complete | both available | both rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | 19 | 19 | 2 | 19 | 2 | 10.53% |
| 2023 | 96 | 96 | 65 | 95 | 65 | 67.71% |
| 2024 | 129 | 129 | 129 | 128 | 128 | 99.22% |
| 2025 | 246 | 246 | 244 | 246 | 244 | 99.19% |
| 2026 | 40 | 34 | 34 | 33 | 33 | 97.06% |

## 缺口样例

| symbol | onboard | window_end | kline expected | kline found | funding months expected | funding months found | missing kline days | missing funding months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DUSKUSDT | 2022-01-06 | 2022-02-04 | 30 | 29 | 2 | 2 | 2022-01-06 |  |
| FLOWUSDT | 2022-02-09 | 2022-03-10 | 30 | 29 | 2 | 2 | 2022-02-09 |  |
| IMXUSDT | 2022-02-10 | 2022-03-11 | 30 | 29 | 2 | 2 | 2022-02-10 |  |
| API3USDT | 2022-02-21 | 2022-03-22 | 30 | 29 | 2 | 2 | 2022-02-21 |  |
| GMTUSDT | 2022-03-14 | 2022-04-12 | 30 | 29 | 2 | 2 | 2022-03-14 |  |
| WOOUSDT | 2022-04-07 | 2022-05-06 | 30 | 29 | 2 | 2 | 2022-04-07 |  |
| FTTUSDT | 2022-04-14 | 2022-05-13 | 30 | 29 | 2 | 2 | 2022-04-14 |  |
| JASMYUSDT | 2022-04-19 | 2022-05-18 | 30 | 29 | 2 | 2 | 2022-04-19 |  |
| DARUSDT | 2022-04-28 | 2022-05-27 | 30 | 29 | 2 | 2 | 2022-04-28 |  |
| INJUSDT | 2022-08-16 | 2022-09-14 | 30 | 29 | 2 | 2 | 2022-08-16 |  |
| STGUSDT | 2022-08-24 | 2022-09-22 | 30 | 29 | 2 | 2 | 2022-08-24 |  |
| SPELLUSDT | 2022-09-05 | 2022-10-04 | 30 | 29 | 2 | 2 | 2022-09-05 |  |
| 1000LUNCUSDT | 2022-09-08 | 2022-10-07 | 30 | 29 | 2 | 2 | 2022-09-08 |  |
| LUNA2USDT | 2022-09-09 | 2022-10-08 | 30 | 29 | 2 | 2 | 2022-09-09 |  |
| LDOUSDT | 2022-09-21 | 2022-10-20 | 30 | 29 | 2 | 2 | 2022-09-21 |  |
| APTUSDT | 2022-10-18 | 2022-11-16 | 30 | 29 | 2 | 2 | 2022-10-18 |  |
| QNTUSDT | 2022-10-18 | 2022-11-16 | 30 | 28 | 2 | 2 | 2022-10-18;2022-10-19 |  |
| FETUSDT | 2023-01-15 | 2023-02-13 | 30 | 28 | 2 | 2 | 2023-01-15;2023-01-16 |  |
| FXSUSDT | 2023-01-19 | 2023-02-17 | 30 | 29 | 2 | 2 | 2023-01-19 |  |
| HOOKUSDT | 2023-01-19 | 2023-02-17 | 30 | 26 | 2 | 2 | 2023-01-19;2023-01-20;2023-01-21;2023-01-22 |  |

## 产物

- `06_RESEARCH/CODE/a4_listing_census.py`
- `06_RESEARCH/CODE/output/a4_listing_census_by_year.csv`
- `06_RESEARCH/CODE/output/a4_listing_archive_head_probes.csv`
- `06_RESEARCH/CODE/output/a4_listing_archive_summary.csv`
- `06_RESEARCH/CODE/output/a4_listing_census_summary.json`
