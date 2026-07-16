# REPORT P0-RES-011 - 期权对冲流 DEFER 前提复核

执行时间：2026-07-16 UTC  
任务性质：数据可得性侦察；未做信号研究、未跑回测、未读取 Holdout、未花钱。

## 结论

“期权对冲流必须付费数据”这个 DEFER 前提不成立。更准确的状态提案：

> 公开数据足够做 Deribit 主导的期权对冲流初筛；跨所标准化、长历史可复跑、全量流式监控、策略标签和生产级数据质量仍需要付费或授权数据。机会地图建议从 `DEFER: 需付费数据` 改为 `WATCH / FREE-SCREENABLE: 免费数据可初筛，正式研究前需确认历史留存和跨所质量`，由 Claude 裁决。

## 免费可得字段

Deribit Public API：

- 合约链：`instrument_name`, `expiration_timestamp`, `strike`, `option_type`, `kind=option` 等。来源：https://docs.deribit.com/api-reference/market-data/public-get_instruments
- 链级摘要：`bid_price`, `ask_price`, `mark_price`, `underlying_price`, `open_interest`, `volume`, `volume_usd` 等。来源：https://docs.deribit.com/api-reference/market-data/public-get_book_summary_by_currency
- 单合约盘口/Greeks：`asks`, `bids`, `open_interest`, `mark_iv`, `bid_iv`, `ask_iv`, `greeks`, `index_price` 等。来源：https://docs.deribit.com/api-reference/market-data/public-get_order_book
- 单合约 ticker：`mark_price`, `index_price`, `underlying_price`, `open_interest`, `stats.volume`, `greeks.delta/gamma/theta/vega/rho`, `mark_iv/bid_iv/ask_iv`。来源：https://docs.deribit.com/api-reference/market-data/public-ticker
- 成交历史：`trade_id`, `timestamp`, `instrument_name`, `price`, `amount`, `direction`, `tick_direction`，支持按时间窗分页。来源：https://docs.deribit.com/api-reference/market-data/public-get_last_trades_by_currency_and_time
- 辅助字段：mark price history、perp funding history。来源：https://docs.deribit.com/api-reference/market-data/public-get_mark_price_history 和 https://docs.deribit.com/api-reference/market-data/public-get_funding_rate_history

其他免费补充：

- Bybit V5 public market data 覆盖 option instruments、tickers、orderbook、recent trades；ticker 文档列 option 的 mark/index/underlying、OI、volume、IV、Greeks。来源：https://bybit-exchange.github.io/docs/v5/market/instrument 和 https://bybit-exchange.github.io/docs/v5/market/tickers
- Binance Options REST 市场数据覆盖 exchangeInfo、order book、recent trades、block trades、mark price、ticker、open interest 等公开端点。来源：https://developers.binance.com/docs/derivatives/options-trading/market-data/Exchange-Information

## 限制

- Deribit `get_instruments` 文档列该端点 1 request/s；Deribit 全局速率见官方 rate-limit 页。来源：https://docs.deribit.com/api-reference/market-data/public-get_instruments 和 https://support.deribit.com/hc/en-us/articles/25944617523357-Rate-Limits
- Deribit 公开成交历史有 `start_timestamp`, `end_timestamp`, `count`, `has_more`，但公开文档没有给出完整历史留存承诺；因此只能认定为“初筛可用”，不能认定为“全历史 tick 仓库”。来源：https://docs.deribit.com/api-reference/market-data/public-get_last_trades_by_currency_and_time
- 本机直连 Deribit/Binance 文档/API 有 TLS 或 HTTP 202 空响应问题，Laevitas 和 Bybit 文档可直连；这是执行环境可达性风险，不改变公开文档字段可得性。

## Laevitas 复核

Laevitas 免费档不适合作为可复跑核心数据源，但不是“必须付费才能初筛”的证据。

从 https://www.laevitas.ch/ 抽取到的公开价格/权限：

- Free：$0/mo，1 week historical data，Basic charting。
- Premium：$50/mo/seat，1 year historical data，Unlimited charting，CSV exports。
- Enterprise：$500/mo/seat，API historical data。

Laevitas OpenAPI 可直连，`https://apiv2.laevitas.ch/openapi.json` 返回 110 个路径，security scheme 为 `X-API-Key`；options 路径包括 `/api/v1/options/catalog`, `/api/v1/options/volume`, `/api/v1/options/trades`, `/api/v1/options/open-interest`, `/api/v1/options/level1`, `/api/v1/options/volatility` 等。结论：Laevitas 免费网页可人工辅助，Laevitas API/长历史需要付费或 key；但 Deribit/Bybit/Binance 的公开 market data 已足够做免费初筛。

## 护栏自检

- 未碰 `06_RESEARCH/DATA/HOLDOUT/`。
- 未跑信号、回测或统计检验。
- 未购买或调用付费接口。
- 所有事实保留 URL；付费墙/API key 后内容按不可得处理。
- 结论只到数据可得性和机会地图状态提案，裁决留 Claude。

