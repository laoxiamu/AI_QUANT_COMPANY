# REPORT_P0RES018_A4_LISTING_CENSUS_20260721

Generated: 2026-07-21 08:02:36 UTC

## 结论

- 本轮只做可行性普查；未计算收益、CAR、残差、方向胜率、Sharpe、回撤或回测。
- 事件表总数 686：本地 `UNIVERSE_PIT.csv` 驱动 530，官方公告补充但不在本地 universe 的 156。
- `existing_spot_then_perp` 总数 132；其中 Kline/funding/OI 三项 30 天窗口完整 89。
- 出口判据：有效样本 `existing_spot_then_perp & data_complete_all` = 89，阈值 100，结论 **不够格**。

## 口径

- PIT universe：以 `06_RESEARCH/DATA/UNIVERSE_PIT.csv` 为主，保留已退市合约；`fapi.binance.com` 当前返回 HTTP 451，未用当前可交易清单删除样本。
- 公告源：Binance 官方 CMS `bapi/apex` 列表 + `bapi/composite` 文章详情；抓取目录为 New Cryptocurrency Listing 与 Latest Binance News。
- 现货判定：对候选 Binance spot symbol 的上市前 30 个 UTC 自然日 `1h` 日归档逐日 HEAD；不下载现货 Kline。
- 永续数据完整性：上市日起最多 30 个 UTC 自然日，Kline 用 daily `1h` ZIP HEAD，OI 用 daily `metrics` ZIP HEAD，funding 用 monthly `fundingRate` ZIP HEAD。
- 首周成交额代理：只读取永续 `1h` Kline ZIP 的 quote volume 字段，按日求和后取首 7 日中位数；不计算任何价格变动或收益。
- 截止日：daily futures/OI 归档按 2026-07-19 为可闭合日；monthly funding 按 2026-06 为可闭合月份。

## 分层计数

| event_type | events | data_complete_all | valid_existing_spot_sample | delisted_later | delisted_rate |
| --- | --- | --- | --- | --- | --- |
| existing_spot_then_perp | 132 | 89 | 89 | 49 | 37.12% |
| simultaneous_spot_perp | 165 | 150 | 0 | 9 | 5.45% |
| tradfi_or_special | 113 | 40 | 0 | 0 | 0.00% |
| zero_base_new_asset | 276 | 262 | 0 | 40 | 14.49% |

## 分年计数

| year | events | existing_spot_then_perp | data_complete_all | valid_existing_spot_sample | delisted_later |
| --- | --- | --- | --- | --- | --- |
| 2022 | 22 | 13 | 3 | 0 | 2 |
| 2023 | 96 | 56 | 61 | 29 | 28 |
| 2024 | 131 | 39 | 127 | 37 | 31 |
| 2025 | 252 | 22 | 250 | 22 | 37 |
| 2026 | 185 | 2 | 100 | 1 | 0 |

## 数据可得性

| check | ok | denominator | rate |
| --- | --- | --- | --- |
| spot pre30 complete | 132 | 686 | 19.24% |
| perp kline 30d complete | 583 | 686 | 84.99% |
| funding window complete | 601 | 686 | 87.61% |
| OI 30d complete | 584 | 686 | 85.13% |
| kline+funding+OI complete | 541 | 686 | 78.86% |

## 公告/生效时间覆盖

| coverage | count | denominator | rate |
| --- | --- | --- | --- |
| all events with official announcement code | 423 | 686 | 61.66% |
| UNIVERSE_PIT rows with official announcement code | 267 | 530 | 50.38% |
| effective timestamp exact from announcement body | 289 | 686 | 42.13% |

| effective_ts_source | events | rate |
| --- | --- | --- |
| official_announcement_body | 289 | 42.13% |
| official_announcement_release_date_midnight_proxy | 5 | 0.73% |
| universe_onboard_date_midnight_proxy | 392 | 57.14% |

未从公告正文解析到精确 UTC 生效时间的事件，`perp_listing_effective_ts_utc` 使用本地 PIT `onboard_date` 的 UTC 午夜代理，或公告发布日期午夜代理；CSV 的 `effective_ts_source` 逐行标明。

## 幸存者偏差量化

| segment | delisted_later | denominator | rate |
| --- | --- | --- | --- |
| all events | 98 | 686 | 14.29% |
| existing_spot_then_perp | 49 | 132 | 37.12% |
| valid existing_spot sample | 37 | 89 | 41.57% |

已退市合约被保留在事件分母和失败率中；若只用当前仍可交易合约，会漏掉 98 / 686 = 14.29% 的历史事件。

## 缺失样例

| symbol | event_day | delisted_later | kline_complete | funding_complete | oi_complete | missing_kline_days | missing_funding_months | missing_oi_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DUSKUSDT | 2022-01-06 | False | False | True | False | 2022-01-06 |  | 2022-01-06 |
| FLOWUSDT | 2022-02-09 | False | False | True | False | 2022-02-09 |  | 2022-02-09 |
| IMXUSDT | 2022-02-10 | False | False | True | False | 2022-02-10 |  | 2022-02-10 |
| API3USDT | 2022-02-21 | False | False | True | False | 2022-02-21 |  | 2022-02-21 |
| ANCUSDT | 2022-03-07 | False | False | True | False | 2022-03-07 |  | 2022-03-07 |
| WOOUSDT | 2022-04-07 | False | False | True | False | 2022-04-07 |  | 2022-04-07 |
| FTTUSDT | 2022-04-14 | True | False | True | False | 2022-04-14 |  | 2022-04-14 |
| JASMYUSDT | 2022-04-20 | False | False | True | False | 2022-04-19 |  | 2022-04-19 |
| DARUSDT | 2022-04-28 | True | False | True | False | 2022-04-28 |  | 2022-04-28 |
| INJUSDT | 2022-08-16 | False | False | True | False | 2022-08-16 |  | 2022-08-16 |
| SPELLUSDT | 2022-09-05 | False | False | True | False | 2022-09-05 |  | 2022-09-05 |
| LDOUSDT | 2022-09-21 | False | False | True | False | 2022-09-21 |  | 2022-09-21 |
| QNTUSDT | 2022-10-18 | False | False | True | False | 2022-10-18;2022-10-19 |  | 2022-10-18;2022-10-19 |
| FETUSDT | 2023-01-15 | False | False | True | False | 2023-01-15;2023-01-16 |  | 2023-01-15;2023-01-16 |
| FXSUSDT | 2023-01-19 | True | False | True | False | 2023-01-19 |  | 2023-01-19 |
| HOOKUSDT | 2023-01-19 | True | False | True | False | 2023-01-19;2023-01-20;2023-01-21;2023-01-22 |  | 2023-01-19;2023-01-20;2023-01-21;2023-01-22 |
| MAGICUSDT | 2023-01-23 | False | False | True | False | 2023-01-23;2023-01-24 |  | 2023-01-23;2023-01-24 |
| TUSDT | 2023-01-31 | False | False | False | False | 2023-01-31 | 2023-01 | 2023-01-31 |
| HIGHUSDT | 2023-02-03 | True | False | True | False | 2023-02-03;2023-02-04;2023-02-05;2023-02-06 |  | 2023-02-03;2023-02-04;2023-02-05;2023-02-06 |
| MINAUSDT | 2023-02-03 | False | False | True | False | 2023-02-03;2023-02-04;2023-02-05 |  | 2023-02-03;2023-02-04;2023-02-05 |

## 源与限制

- 官方公告详情有少数格式不可解析时，事件仍按本地 universe 日期保留，并在 CSV 的 `announcement_parse_status` 标注。
- Binance spot 历史只核验 Binance 官方现货归档；未核验其他交易所现货历史。因此 `zero_base_new_asset` 是“Binance spot archive 未发现”的工程分类，不等同于全市场没有现货。
- Funding 只有 monthly archive 可免费核验；当窗口落在当前未闭合月份时，标为不完整，不据此删除事件。

## 产物

- CODE: `06_RESEARCH/CODE/p0res018_a4_listing_census_redefined.py`
- EVENT CSV: `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/DATA/LISTING_EVENTS/p0res018_a4_redefined_listing_events_20260721.csv`
- HEAD PROBES: `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/DATA/LISTING_EVENTS/p0res018_a4_redefined_head_probes_20260721.csv`
- ANNOUNCEMENT DETAILS: `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/DATA/LISTING_EVENTS/p0res018_a4_redefined_announcement_details_20260721.csv`
- FIRST WEEK VOLUME: `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/DATA/LISTING_EVENTS/p0res018_a4_redefined_first_week_volume_20260721.csv`
- RESULTS copy: `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/RESULTS/20260721_p0res018_a4_redefined_listing_census.md`

## 验收自检

| requirement | status | evidence |
| --- | --- | --- |
| 不看收益/不做回测 | PASS | 脚本无 return/CAR/residual/backtest 计算；Kline 仅读取 quote volume |
| PIT universe 驱动并保留退市 | PASS | `UNIVERSE_PIT.csv` 530 行入表；`delisted_later` 98 |
| 公告与生效分列 | PASS | `perp_listing_announcement_ts_utc` 与 `perp_listing_effective_ts_utc` 分列 |
| 现货前 30 天 HEAD | PASS | `spot_1h_daily_pre30` HEAD 明细 20970 行 |
| Kline/funding/OI 可得性 | PASS | HEAD 明细 67526 行 |
| 首周成交额代理 | PASS | volume 明细 4778 行，仅用于分层字段 |
| 不碰 Holdout/不 commit | PASS | 未读取 `06_RESEARCH/DATA/HOLDOUT`; 未执行 git commit |
