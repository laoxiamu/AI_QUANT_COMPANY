# REPORT P0-RES-012 - 美股事件 x Binance bStocks 容量核实

执行时间：2026-07-16 UTC  
任务性质：产品/容量侦察；未做信号研究、未跑回测、未读取 Holdout、未花钱。

## 结论

bStocks 是真实在跑的 Binance Tokenized Securities 产品，但不能支持“美股事件类候选经 bStocks 渠道有小资金容量优势”的强结论。

更合适的判断：

- 可行性：适合继续观察为“合格用户的 24/7 现货事件反应渠道”，不适合直接立项为美股事件策略主渠道。
- 样本/容量：公开成交热度不低，但精确 Binance 7日真实成交量、盘口深度和洗量剔除口径不可得；不能把第三方聚合 24h volume 当作真实可成交容量。
- 准入：产品明确受 jurisdiction eligibility 限制，不向美国人/美国境内开放；当前环境请求 Binance ticker API 返回 HTTP 451 restricted location；大陆用户是否可交易无法从公开 bStocks 页面逐国确认，执行级假设应按“不可假设可用”处理。
- 做空/杠杆：spot 可交易；部分 bStocks 可作 Cross Margin / Portfolio Margin collateral，但 Binance 公告明确“Borrowing is not currently supported”，且 collateral 功能要求 VIP 3+ 和 permitted jurisdictions；这不是小资金可用的做空/杠杆通道。

## 官方状态

Binance 介绍页称 bStocks 是 1:1 backing 的 tokenized securities，可在 Binance spot 24/7 交易、低至 $5 fractional access、BEP-20/BSC 可提现；同页也写明 bStocks 不是直接持有股票，且只对 permitted jurisdictions 的 eligible users 可用。来源：https://www.binance.com/en/support/announcement/detail/2c0c92ed15ac42d1b14bb1eac00d22bb

Binance Academy 写明：bStocks 可在 Binance spot 24/7 交易；支持 self-custody；有 geography restrictions；不向 US persons 提供；第三方集成需要 country eligibility endpoint。来源：https://www.binance.com/en/academy/articles/what-are-bstocks-a-guide-to-tokenized-stocks-on-binance

Binance Research 在 2026-07-10 报告：bStock listings 从 5 增至 25；on-chain market cap 接近 US$300M；cross-market arbitrage-like volume 为 US$216M；off-hours bStocks 占相关交易量 58%。来源：https://www.binance.com/en/research/analysis/early-momentum-in-tokenized-stock-adoption

Binance 在 2026-07-15 公告新增 10 个 bStocks spot trading pairs：AAOIB/USDT, ARMB/USDT, AVGOB/USDT, BABAB/USDT, HOODB/USDT, IBMB/USDT, MRVLB/USDT, NOKB/USDT, RKLBB/USDT, TSMB/USDT，并设 zero maker fee 至 2026-08-31。来源：https://www.binance.com/en/support/announcement/detail/f198d9602f3b4604a9b15cd0a1529e32

Binance 在 2026-07-03 公告 15 个 bStocks 可作为 Cross Margin / Portfolio Margin / Portfolio Margin Pro collateral；公告同时写明 borrowing is not currently supported、VIP 3+、permitted jurisdictions。来源：https://www.binance.com/en/support/announcement/detail/0e22b98c9f154d35b50f40dbad43d1c5

Binance 在 2026-07-15 又公告新增 10 个 bStocks collateral assets，并同样写明 borrowing is not currently supported、VIP 3+、permitted jurisdictions。来源：https://www.binance.com/en/support/announcement/detail/62c2a684d09f445295b87797acc71ae8

## 成交量与洗量口径

Binance 官方公开页面没有给出可直接下载的逐标 7日真实成交量；本机对 `https://api.binance.com/api/v3/ticker/24hr?symbol=SNDKBUSDT` 的一手请求返回 HTTP 451，正文为 restricted location，并指向 Binance Terms：https://www.binance.com/en/terms 。因此本轮无法从 Binance API 直接核验逐标 24h/7d volume、trade count 或 order book depth。

CoinGecko 免费 API 可访问。`https://api.coingecko.com/api/v3/coins/list` 识别出 32 个 `bStocks Tokenized Stock` ID；`https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=...` 在 2026-07-16T06:12Z 附近返回 32 个市场样本，合计 24h `total_volume` 约 US$271.77M。快照文件：`06_RESEARCH/CODE/output/p0res012_coingecko_bstocks_snapshot_20260716.csv`。

CoinGecko top 24h volume 样本：

| symbol | name | 24h total_volume |
|---|---|---:|
| qqqb | Invesco QQQ Trust (bStocks Tokenized Stock) | 100,824,275 |
| mub | Micron Technology (bStocks Tokenized Stock) | 43,426,971 |
| sndkb | SanDisk (bStocks Tokenized Stock) | 21,180,916 |
| dramb | Roundhill Memory ETF (bStocks Tokenized Stock) | 16,539,143 |
| spcxb | SpaceX (bStocks Tokenized Stock) | 15,081,780 |
| skhyb | SK Hynix (bStocks Tokenized Stock) | 11,425,321 |
| soxlb | Semicon Bull 3X ETF (bStocks Tokenized Stock) | 10,308,756 |

这不能直接视为 Binance 真实 7日可成交容量，原因：

- CoinGecko 是第三方聚合，不保证只代表 Binance CEX。
- 24h volume 不是 7日真实成交量。
- Binance 自己在新增 bStocks 公告中设置 zero maker fee，并保留对刷量、self dealing、market manipulation 的 disqualification 权利；这说明刷量风险需要单独剔除，不能只看 nominal volume。来源：https://www.binance.com/en/support/announcement/detail/f198d9602f3b4604a9b15cd0a1529e32
- 本轮尝试 CoinGecko `market_chart?days=7` 时前 3 个 ID 成功，随后免费 API 429 rate limit；得到的部分 7日样本不可扩展为全量 7日结论。部分输出：`06_RESEARCH/CODE/output/p0res012_coingecko_bstocks_7d_volume_snapshot_20260716.csv`。429 说明见 CoinGecko API pricing URL：https://www.coingecko.com/en/api/pricing

## 对“美股事件小资金容量优势”的回答

不支持立项级优势判断。

支持观察的事实：

- 24/7 spot 交易、秒级结算、低至 $5 fractional access、可提现到 BSC，这些对小资金用户有便利性。来源：https://www.binance.com/en/support/announcement/detail/2c0c92ed15ac42d1b14bb1eac00d22bb
- Binance Research 报告显示 bStocks 在 off-hours 占比更高，并有 US$216M arbitrage-like volume。来源：https://www.binance.com/en/research/analysis/early-momentum-in-tokenized-stock-adoption

否定立项级容量优势的事实：

- 美国人/美国境内不可用，jurisdiction eligibility 会限制真实用户池。来源：https://www.binance.com/en/academy/articles/what-are-bstocks-a-guide-to-tokenized-stocks-on-binance
- 当前环境 Binance API 一手请求返回 451 restricted location，说明地理/合规限制不是纸面风险。
- margin/collateral 功能要求 VIP 3+，且 borrowing currently not supported；这不提供小资金做空或稳定杠杆优势。来源：https://www.binance.com/en/support/announcement/detail/0e22b98c9f154d35b50f40dbad43d1c5 和 https://www.binance.com/en/support/announcement/detail/62c2a684d09f445295b87797acc71ae8
- 精确 7日真实成交量、盘口深度、trade count 和 wash-adjusted volume 不可得；不能把 nominal volume 当作可执行容量。

## 护栏自检

- 未碰 `06_RESEARCH/DATA/HOLDOUT/`。
- 未做信号研究、回测、收益归因或策略筛选。
- 未购买数据、未开通账户、未绕过地区限制。
- 事实断言均附 URL 或本地产物路径；不可得项明确标注。
- 结论只到可行性、样本量和数据可得性，裁决留 Claude。

