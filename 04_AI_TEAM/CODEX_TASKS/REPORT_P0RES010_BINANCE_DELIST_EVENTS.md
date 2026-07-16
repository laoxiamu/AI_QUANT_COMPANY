# REPORT P0-RES-010 - Binance 退市强制平仓事件库存

执行时间：2026-07-16 UTC  
任务性质：侦察库存；未做信号研究、未跑回测、未读取 Holdout、未花钱。

## 结论

本轮只形成“可检索库存”，不等同 Binance 历史退市公告全量爬取成功。原因是终端直连 `www.binance.com` / `api.binance.com` 多次出现 TLS/超时或限制，无法稳定分页 CMS 接口；HTTP 4xx/5xx 按可达纪律处理，非 4xx/5xx 的 TLS/timeout 作为网络限制记录。

可检索库存 CSV 已落地：

- `06_RESEARCH/DATA/DELIST_EVENTS/binance_delist_event_inventory_p0res010_20260716.csv`
- 生成脚本：`06_RESEARCH/CODE/output/p0res010_make_delist_inventory.py`

库存口径：

- 事件总数：124 行
- USDⓈ-M 永续强制结算/退市：60 行
- 现货交易对移除/代币退市：64 行
- 本地面板目录实际 symbol 数：37 个，而任务书写 31 个；本轮按本地目录事实处理：`06_RESEARCH/DATA/FUTURES_EXPANDED_2026/`
- 公告时间落在本地面板覆盖期内且有对应 4H 价格数据：8 行
- 其中 USDⓈ-M 永续强制结算可对齐：1 行，`OMGUSDT`
- 现货 pair removal 映射到本地 USDT 面板可对齐：7 行，`ETCUSDT`, `AAVEUSDT`, `TRXUSDT`, `YFIUSDT`, `FILUSDT`, `LRCUSDT`, `EGLDUSDT`

样本量裁定建议：不满足 ≥30。若 Claude 要继续，只能先做官方公告 API/镜像抓取通道修复或扩大数据面板 universe；当前不建议立项。

## 方法

1. 预检网络：`https://example.com` 直连 HTTP/2 200；Binance 主站/API 经 `curl` 和 Node fetch 出现 TLS/timeout；后续主要使用可检索的 Binance Support/Square 页面、Binance.info 镜像、CoinCarp/PANews/Coingape/TradingView 等索引或镜像 URL。
2. 事件字段：`market`, `event_type`, `symbol`, `announcement_time_utc`, `delist_settlement_time_utc`, `announcement_to_delist_hours`, `source_url`, `source_note`。
3. 对齐字段：`local_panel_symbol`, `in_local_panel_symbol_set`, `announcement_in_panel_coverage`, `local_panel_start_utc`, `local_panel_end_utc`, `local_panel_rows`。
4. 每行 `source_url` 保留事实来源；对无法读取官方正文的条目，在 `source_note` 标明镜像/二级源。

关键来源 URL：

- Binance Delisting 分类入口：https://www.binance.com/en/support/announcement/list/161
- Binance bapi 尝试端点：https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=20&catalogId=161
- Binance Square 官方账号样例：https://www.binance.com/en/square/post/315659328967362
- Binance Support 镜像样例：https://www.binance.info/en/support/announcement/detail/f6ebc17e4dbd451b873d9ef25c801237
- CoinCarp Binance 公告镜像样例：https://www.coincarp.com/exchange/announcement/binance-27eac260521b4f40ab331e1a345887a7/

## 对齐明细

可对齐 8 行：

| market | symbol | announcement_time_utc | delist_settlement_time_utc | source_url |
|---|---:|---:|---:|---|
| USDS-M perpetual | OMGUSDT | 2024-12-06 03:02:37 | 2024-12-16 09:00:00 | https://www.coincarp.com/exchange/announcement/binance-27eac260521b4f40ab331e1a345887a7/ |
| spot | ETCUSDT | 2024-12-28 00:00:00 | 2025-01-03 08:00:00 | https://bitcoinworld.co.in/binance-delisting-spot-trading-pairs/ |
| spot | AAVEUSDT | 2025-01-09 00:00:00 | 2025-01-16 03:00:00 | https://cryptorank.io/news/feed/16461-binance-delisting-spot-trading-pairs-2 |
| spot | TRXUSDT | 2025-01-09 00:00:00 | 2025-01-16 03:00:00 | https://cryptorank.io/news/feed/16461-binance-delisting-spot-trading-pairs-2 |
| spot | YFIUSDT | 2025-01-16 00:00:00 | 2025-01-23 03:00:00 | https://coinpulsehq.com/binance-delisting-spot-trading-pairs-5/ |
| spot | FILUSDT | 2025-01-16 00:00:00 | 2025-01-23 03:00:00 | https://coinpulsehq.com/binance-delisting-spot-trading-pairs-5/ |
| spot | LRCUSDT | 2025-01-16 00:00:00 | 2025-01-23 03:00:00 | https://coinpulsehq.com/binance-delisting-spot-trading-pairs-5/ |
| spot | EGLDUSDT | 2025-12-01 00:00:00 | 2025-12-05 03:00:00 | https://www.mexc.fm/news/219087 |

## 护栏自检

- 未碰 `06_RESEARCH/DATA/HOLDOUT/`。
- 未跑收益、回测、信号或分位研究。
- 产出写入 `06_RESEARCH/DATA/DELIST_EVENTS/`。
- 所有网络事实在 CSV 或报告内保留 URL；不可稳定读取的官方内容标为镜像/二级源，不猜正文。
- 结论只到样本量和数据可得性，立项裁决留 Claude。

