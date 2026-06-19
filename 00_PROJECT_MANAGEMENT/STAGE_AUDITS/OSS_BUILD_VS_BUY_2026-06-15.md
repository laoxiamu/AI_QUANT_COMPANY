# RESEARCH-OSS-TOOLS: Build-vs-Buy 调研结论

生成时间: 2026-06-19 UTC+08  
任务口径: 3 万本金 / 1 人 / 月预算 1000 元 / 1-2 月出最小可跑系统 / Binance 为主  
约束确认: 未读取 Holdout；未改预登记或研究数据；只写项目管理审计报告和 Codex 任务交接文件。

## Executive Summary

- **结论: 不应从零建交易系统，也不应继续依赖脆弱自建 WS 采集器做核心生产链路。** 1-2 月目标下，最小可跑系统应采用 `Freqtrade` 做回测/纸面/实盘地基，`Binance 官方 REST/data.binance.vision` 做历史事实源，`CCXT` 做轻量统一接口和兜底适配，强平数据优先买 `CoinGlass` 小套餐或暂降级为 Binance 官方 snapshot WS。
- **CCXT 可替代大部分自建交易所接口，但不能单独替代所有历史采集。** 它覆盖行情、K线、账户、下单、余额、仓位、funding/OI 的统一方法；但 Binance 特有字段、长期历史、强平 snapshot 语义、数据校验仍要项目自己做薄封装。
- **Freqtrade 最适合 Phase 1；NautilusTrader 更适合 Phase 2；vectorbt 只适合研究加速。** Freqtrade 已提供 dry-run、live、DB 持久化、策略回调、保护/止损、REST/FreqUI/Telegram 等低成本能力；NautilusTrader 生产级但学习和接入成本更高；vectorbt 很适合批量研究，但不是执行系统。
- **强平数据不值得 1 人团队继续手搓为关键依赖。** Binance 官方 `forceOrder` WS 是 snapshot，不是完整逐笔强平；REST 只能查用户自己的强平订单且最多过去 90 天。若强平是研究主因子，应买 CoinGlass；若只是辅助监控，先用官方 WS + 断线/缺口标记即可。
- **MCP/插件不应进交易闭环。** CoinAPI MCP 可作为人工/AI 查询入口；Binance/CCXT MCP 多为第三方小项目，不应持有交易权限或替代可审计代码路径。

## 专业自查

1. 本任务验证的机制: 工程实现机制，不是交易 Alpha；验证“借成熟组件能否降低 Phase 1 系统风险和时间成本”。
2. 验收是否可量化: 有。每项需给能力、成熟度、成本、接入难度、推荐与理由；还需技术栈、路线和完成事件。
3. 更便宜等效实现: 有。Freqtrade/CCXT/Binance 官方数据优先于自建交易系统和商业机构数据。
4. 禁止项: 不触碰 Holdout、不改研究文件、不简化研究成本模型、不引入不可审计黑箱依赖到研究结论。

## 自建 vs 采用对照表

| 能力层 | 自建方案 | 采用方案 | 推荐 |
|---|---|---|---|
| 交易所 REST/WS 接口 | 自己维护 Binance endpoint、签名、重连、限速、错误映射 | CCXT + Binance 官方 SDK 薄封装 | **采用**。自写只保留项目语义层和校验。 |
| 历史 K线/成交 | 自己 REST 回填和断点续跑 | data.binance.vision 官方 zip + checksum；必要时 REST 补洞 | **采用**。官方归档是更低维护成本的事实源。 |
| Mark/index/premium/funding/OI | 自己混用 contract Kline、mark、base/quote volume | Binance 官方专用 endpoint + schema 校验 | **采用**。必须显式区分 contract vs mark。 |
| 强平实时 | 自建 `!forceOrder@arr` WS collector | Binance 官方 WS snapshot + 完整重连/缺口标记 | **谨慎采用**。只适合监控或弱特征，不适合声称完整强平历史。 |
| 强平历史 | 自己长期运行采集器攒数据 | CoinGlass / CoinAPI / Amberdata / Kaiko | **优先买 CoinGlass**。月预算内可覆盖研究验证。 |
| 回测/纸面/实盘 | 从零写事件循环、撮合、持仓、风控、对账、监控 | Freqtrade Phase 1；NautilusTrader Phase 2 候选 | **采用 Freqtrade**。最快给出最小可跑闭环。 |
| 快速研究 | 自己循环 pandas 回测 | vectorbt + 项目自实现统计校验 | **采用为研究工具**，不做实盘地基。 |
| 风控/状态权威 | 内存字典/脚本变量 | Freqtrade DB + 项目外部风控守门脚本 | **采用 DB 权威**，符合 V4 事故复盘。 |
| AI/MCP 接口 | 让 AI 直接交易 | 只读查询 MCP；交易必须走代码和人工审批 | **不进交易闭环**。 |

## 1. CCXT

| 维度 | 结论 |
|---|---|
| 能力 | 覆盖统一 REST/WebSocket、行情、OHLCV、订单簿、成交、余额、订单、仓位；CCXT manual 明确是多个交易所公共/私有 API 的统一类库，Binance 参考页列出 `fetchBalance`、`createOrderWs`、`watchBalance`、`fetchPositionsWs` 等能力。[CCXT manual](https://github.com/ccxt/ccxt/wiki/manual), [CCXT Binance reference](https://docs.ccxt.com/docs/exchanges/binance) |
| Funding/OI | CCXT Binance reference 支持 `fetchOpenInterestHistory`；CCXT 通用接口也覆盖 funding/open-interest 类方法，但不同交易所实现和字段完整性要逐项测。 |
| 实时 WS | CCXT Pro 已并入免费 CCXT，支持 `watchOrderBook`、`watchTrades`、`watchOHLCV`、`watchLiquidations`、`watchBalance`、`watchOrders` 等。[CCXT Pro manual](https://docs.ccxt.com/docs/pro-manual) |
| 成熟度 | 高。长期维护、多语言、交易所覆盖广。缺点是统一抽象会遮蔽 Binance 特有字段，参数仍需传 exchange-specific `params`。 |
| 成本 | 开源免费；主要成本是接入测试、限速、异常处理、schema 固化。 |
| 接入难度 | 中低。1-3 天可封装项目需要的 read-only 方法；下单前需要单独做 testnet/小额验证。 |
| 是否推荐 | **推荐作为统一交易所适配层，但不推荐裸用作研究事实源。** 用它取代自建通用接口；但 Binance 历史数据、funding、OI、强平要保留官方 endpoint/字段级校验。 |

**能否取代自建采集器:** 对普通 ticker/orderbook/trades/klines/账户/订单，可以替代。对强平历史，不能完全替代，因为 Binance 官方强平流本身是 snapshot，语义不是完整逐笔历史。

## 2. Freqtrade / NautilusTrader / vectorbt

| 框架 | 能力 | 成熟度 | 成本 | 接入难度 | 是否推荐 |
|---|---|---:|---:|---:|---|
| Freqtrade | 免费开源 crypto bot，支持 backtesting、plotting、money management、dry-run、live、REST/FreqUI/Telegram；dry-run 订单和钱包模拟写 DB；WS 失败可回退 REST；futures 需 `trading_mode="futures"` 并配置 margin mode。[Freqtrade intro](https://www.freqtrade.io/en/stable/), [dry-run](https://www.freqtrade.io/en/stable/configuration/), [leverage](https://www.freqtrade.io/en/stable/leverage/) | 高 | 免费 | 低-中 | **Phase 1 推荐。** 最快获得回测-纸面-实盘闭环。 |
| NautilusTrader | Rust core + Python strategy；同一事件驱动架构覆盖 research、deterministic simulation、live；内置 Cache/MessageBus/Portfolio/Execution Algorithms；Binance adapter 支持 spot、USDT-M futures、coin futures、mark price、liquidation custom data、reduce-only 等。[Nautilus docs](https://nautilustrader.io/docs/latest/), [backtesting](https://nautilustrader.io/docs/latest/concepts/backtesting/), [Binance adapter](https://nautilustrader.io/docs/latest/integrations/binance/) | 高但更工程化 | 免费 | 高 | **Phase 2 候选。** 不适合作为 1-2 月最小系统第一选择。 |
| vectorbt | pandas/NumPy/Numba/Rust 加速的向量化研究和回测，适合成千上万参数组合快速探索。[vectorbt docs](https://vectorbt.dev/) | 高 | OSS 免费，Pro 另计 | 低 | **只做研究加速。** 不提供完整实盘执行、对账和风控闭环。 |

**推荐判断:**  
Phase 1 不需要“生产级交易引擎”，需要“能少犯低级工程错的最小闭环”。Freqtrade 白送的价值最大: 交易循环、dry-run、live、DB、UI/API、基本订单/止损/保护、策略回调、配置管理。我们只需要自写:

- 策略信号层: 只实现已通过研究验收的规则，不把 Freqtrade 当参数搜索器。
- 数据适配层: 将官方 Binance 历史数据、funding/OI、商业强平数据转为统一 parquet/CSV，并写 schema/UTC/checksum 校验。
- 研究验收层: 项目协议要求的 E[R]、赢亏比、块 bootstrap 爆仓概率、年化 log 增长、分年正期望占多数，仍自实现为可审计小函数。
- 风控守门层: 最大杠杆、最大名义、最大日亏、断连停机、只读/交易 key 分离、订单白名单。
- 对账审计层: 每日导出 Freqtrade DB、Binance account/trade/income/funding，做余额/仓位/成交一致性检查。

## 3. Binance 官方 SDK + 历史数据正确取法

### 推荐接口分工

| 数据/操作 | 正确来源 | 关键坑 |
|---|---|---|
| Contract Kline | `/fapi/v1/klines` 或 data.binance.vision `futures/um/.../klines` | USD-M kline volume 是 base quantity，quote asset volume 另有字段；不要把 contract close 当 mark price。Binance public-data README 明确 USD-M Kline 字段含 Volume 与 Quote asset volume。[Binance public data](https://github.com/binance/binance-public-data) |
| Continuous Kline | `/fapi/v1/continuousKlines` | 用 `pair` + `contractType`，不是普通 `symbol`；适合连续合约分析但不能混成具体可交易合约成交源。[Binance continuous klines](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Continuous-Contract-Kline-Candlestick-Data) |
| Mark Price Kline | `/fapi/v1/markPriceKlines` | 响应中的 volume 字段是 ignore；只能当 mark price 序列，不可当成交量。[Binance mark price klines](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price-Kline-Candlestick-Data) |
| Funding history | `/fapi/v1/fundingRate` | limit max 1000，按时间升序，返回 fundingRate、fundingTime 和关联 markPrice；需分页拉取。[Binance funding history](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History) |
| 当前 OI | `/fapi/v1/openInterest` | 只取当前特定 symbol 的 present open interest。[Binance open interest](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest) |
| OI 历史统计 | `/futures/data/openInterestHist` | 官方 REST 只提供 latest 1 month；长期历史需 data.binance.vision metrics 或第三方数据。[Binance OI statistics](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics) |
| 强平实时 | `<symbol>@forceOrder` / `!forceOrder@arr` | Binance 文档写明每 symbol 每 1000ms 只推最大/最新一笔 liquidation snapshot；不是完整强平逐笔数据。[Binance liquidation stream](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams) |
| 用户强平订单 | `/fapi/v1/forceOrders` | 这是 USER_DATA，只查自己的强平/ADL；默认 7 天，最多过去 90 天；不能当全市场强平历史。[Binance user force orders](https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Users-Force-Orders) |
| 账户/下单 | Binance official connector 或 CCXT | Binance `binance-futures-connector-python` repo 已标注 deprecated，建议关注新 modular connector；`python-binance` 可用但不是 Binance 官方主 SDK。 |

### SDK 选择

- **历史下载/研究:** 直接用 `requests/httpx + data.binance.vision zip + checksum`，不必引 SDK。
- **交易执行:** Phase 1 可随 Freqtrade 内置交易所层；项目外部只做只读对账时可用 Binance official connector 或 CCXT。
- **不要依赖已 deprecated 的 `binance-futures-connector-python` 作为新系统长期基础。** 它的仓库说明建议使用新 modular connector。[Binance futures connector repo](https://github.com/binance/binance-futures-connector-python), [binance-connector PyPI](https://pypi.org/project/binance-connector/)

## 4. 强平/衍生品数据商

| 数据商 | 能力 | 成熟度 | 成本 | 接入难度 | 是否推荐 |
|---|---|---:|---:|---:|---|
| CoinGlass | Futures/spot/options，Liquidation Orders & Funding，OI history endpoint，aggregated liquidation history endpoint；覆盖多交易所。 | 中高，面向交易员/量化用户 | Hobbyist $29/mo；Startup $79/mo；Standard $299/mo；商业使用从 Standard 起；历史分钟级范围随套餐受限。[Pricing](https://www.coinglass.com/pricing) | 低 | **推荐先买 Hobbyist/Startup 做研究验证；如进入商业化再升级。** |
| CoinAPI | Market Data API 有 REST/WS/MCP，$25 free credits，Startup $79/mo，Streamer $249/mo，Pro $599/mo；博客说明 funding/OI 可通过 Metrics API 取历史。 | 高，工程化强 | 月预算内可试，但衍生品细项和 credit 成本需实测 | 中 | **备选。** 更像统一数据基础设施，不是最便宜强平专项源。 |
| Kaiko | 机构级数据；Derivatives Risk Indicators 覆盖 open interest、funding、liquidations、Greeks；页面列 Basic 从 $1,000/mo，Advanced 从 $2,000/mo；2026 页面显示 Kaiko 已收购 Amberdata。 | 很高 | 超出当前月预算 | 中-高 | **不推荐 Phase 1。** 未来机构化或融资后再评估。 |
| Amberdata | Binance futures/perpetuals 历史+实时，包含 OI、long/short、order books、liquidations、funding、insurance funds；API 文档有 futures information 和 liquidation endpoints。 | 很高 | Quote/在线购买，通常偏机构；需询价/试用 | 中 | **不推荐 Phase 1 购买；可作为后续替代 CoinGlass 的机构源。** |

**能否取代自建强平采集器:**  
可以。若强平特征是核心研究变量，CoinGlass 是当前预算内最务实替代；如果月预算必须压到 0，则只能用 Binance 官方 snapshot WS，并在报告中标注“非完整强平序列”，不能把缺失数据写成精确强平流。

## 5. 交易所 MCP/插件现状

| 类型 | 现状 | 判断 |
|---|---|---|
| CoinAPI MCP | CoinAPI 官方提供 MCP server，用于 AI 助手访问实时/历史 crypto market data；其 pricing 页也列 MCP API。[CoinAPI MCP](https://www.coinapi.io/learn/academy/tutorials/getting-started-with-coinapi-and-mcp), [CoinAPI pricing](https://www.coinapi.io/products/market-data-api/pricing) | **可用于只读查询/调研，不进交易闭环。** |
| Binance MCP | 多为第三方 GitHub/marketplace 项目，星数低、维护和权限边界不可作为生产前提。 | **不推荐。** 尤其不应把交易 API key 交给 LLM 工具。 |
| CCXT MCP | 有第三方 CCXT MCP server，但本质是“LLM 调 CCXT”。 | **不推荐进核心系统。** 如果要用，也只读、无交易权限、无资金账户。 |

原则: MCP 是交互层，不是账本、风控或执行层。任何 AI 工具只能提出候选操作，真实交易必须走可审计代码、配置、权限、日志、人工确认和 kill switch。

## 推荐最小可跑技术栈

### Phase 1 目标栈

1. **数据层**
   - `data.binance.vision` 官方 zip 作为 contract klines/trades/aggTrades 基础历史源。
   - Binance REST 专用 endpoint 拉 `fundingRate`、`markPriceKlines`、`openInterest`、`openInterestHist` 近期数据。
   - CoinGlass Hobbyist/Startup 作为强平/OI/funding 跨交易所验证源；预算不足时仅用 Binance snapshot WS 并降级研究口径。

2. **研究层**
   - 保留现有项目自实现的验收统计函数，不引 MLFinPy 等黑箱硬依赖。
   - vectorbt 只用于探索性批量回测或参数面扫描；正式结论仍按项目协议重跑。

3. **交易/纸面/实盘层**
   - Freqtrade 做 backtest、dry-run、live、DB、基本订单管理、UI/API。
   - 先只跑 Binance USDT-M futures 单账户、低杠杆、单策略、单向模式。
   - 不在 Phase 1 迁移 NautilusTrader，避免 1 人团队被工程学习曲线吞掉。

4. **项目自写层**
   - `market_data/binance_official.py`: 官方历史下载、REST 拉取、checksum、schema、UTC 校验。
   - `features/derivatives.py`: mark/contract/funding/OI/强平字段标准化。
   - `risk_gate.py`: 名义上限、杠杆上限、日亏停机、异常停机。
   - `reconcile.py`: Freqtrade DB vs Binance account/trades/income/funding 对账。
   - `reports/`: 固定 seed、固定配置、输出验收四件套。

## 1-2 月落地路线

### 第 1-2 周: 替换脆弱数据链路

- 建官方 Binance 下载器: klines/trades/aggTrades zip、checksum、UTC、schema、base/quote volume 字段测试。
- 建衍生品 REST 拉取器: fundingRate、markPriceKlines、openInterest、openInterestHist。
- 强平路线二选一:
  - 买 CoinGlass Hobbyist/Startup，跑 BTC/ETH/SOL 主合约历史样本；
  - 或将自建 WS 降级为“实时 snapshot 监控”，不再作为完整历史研究源。

### 第 3-4 周: Freqtrade 最小闭环

- Docker/venv 部署 Freqtrade；配置 Binance futures dry-run；DB 落盘。
- 接入一个已通过研究验收的最简单策略模板；不在 Freqtrade 内做新 Alpha 搜索。
- 配好 stoploss_on_exchange、最大 open trades、stake sizing、只读/交易 key 分离。
- 建每日对账脚本: DB trades、orders、fees、funding income、账户余额。

### 第 5-6 周: Paper / Shadow

- 连续 2 周 dry-run/shadow，记录信号、订单、滑点估计、拒单、断线、对账差异。
- 所有异常形成 issue: 数据缺口、Funding 不一致、订单未成交、仓位偏差。
- 若强平数据来自 CoinGlass，做 Binance snapshot vs CoinGlass 的抽样一致性检查。

### 第 7-8 周: 小额围栏实盘

- 只允许最小资金子账户，不触碰核心资本。
- 启用固定 kill switch: 日亏、连续拒单、对账不平、WS/REST 长时间不可用即停。
- 每日生成运行报告，Claude 验收后再决定是否扩大。

## 结论

最小可跑系统的正确路线是“买/采用成熟地基 + 自写可审计薄层”，不是从零造交易系统。当前资金和人力条件下，推荐组合为:

> **Freqtrade + Binance 官方历史/REST + CCXT 薄适配 + CoinGlass 小套餐（若强平是核心变量） + 项目自写研究验收/风控/对账。**

不推荐 Phase 1 使用 NautilusTrader 作为第一地基，也不推荐把 MCP 插件放入交易或资金权限路径。NautilusTrader 可以在 Freqtrade 跑通后作为 Phase 2 生产级引擎候选，用真实需求反推迁移，而不是提前重建大系统。

## Sources

- CCXT manual: https://github.com/ccxt/ccxt/wiki/manual
- CCXT Binance reference: https://docs.ccxt.com/docs/exchanges/binance
- CCXT Pro manual: https://docs.ccxt.com/docs/pro-manual
- Freqtrade docs: https://www.freqtrade.io/en/stable/
- Freqtrade configuration/dry-run: https://www.freqtrade.io/en/stable/configuration/
- Freqtrade leverage/futures: https://www.freqtrade.io/en/stable/leverage/
- NautilusTrader docs: https://nautilustrader.io/docs/latest/
- NautilusTrader Binance integration: https://nautilustrader.io/docs/latest/integrations/binance/
- vectorbt docs: https://vectorbt.dev/
- Binance public data: https://github.com/binance/binance-public-data
- Binance USD-M Futures API docs: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
- Binance liquidation stream: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams
- CoinGlass API pricing/docs: https://www.coinglass.com/pricing, https://docs.coinglass.com/reference
- CoinAPI pricing/MCP/docs: https://www.coinapi.io/products/market-data-api/pricing, https://www.coinapi.io/learn/academy/tutorials/getting-started-with-coinapi-and-mcp
- Kaiko derivatives risk indicators: https://www.kaiko.com/products/derivatives-risk-indicators
- Amberdata Binance market data/docs: https://www.amberdata.io/binance-market-data, https://docs.amberdata.io/http/market/futures-exchanges-information
