# REPORT_VERIFY_V462

## 结论

- 任务状态：`completed`
- v4.6.2 路径：`/opt/v4`
- v4.6.2 当前收数：`no`
- 判定：`v4.6.2方法可用`
- 根因：**不是 Binance 封锁 SG IP，而是采集器仍使用 2026-04-23 已退役的 futures WS 旧路由。**

同一台 SG、同一 `websocket-client 1.7.0` 的差分结果：

| 地址 | 时长 | 结果 |
|---|---:|---:|
| `wss://fstream.binance.com/ws/btcusdt@aggTrade` | 10 秒 | 握手成功，0 帧 |
| `wss://fstream.binance.com/market/ws/btcusdt@aggTrade` | 1.107 秒 | 3 帧 |
| `wss://fstream.binance.com/ws/!forceOrder@arr` | 15 秒 | 握手成功，0 帧 |
| `wss://fstream.binance.com/market/ws/!forceOrder@arr` | 2.649 秒 | 3 帧 |

旧 URL 的“握手后 0 帧”是 Binance 路由迁移后的预期行为，不能作为 IP 封锁证据。

## 1. v4.6.2 定位

- systemd unit：`v4-strategy-runner.service`
- unit 描述：`V4.6.2 Strategy Runner`
- 工作目录：`/opt/v4/strategy`
- 启动文件：`/opt/v4/strategy/strategy_runner.py`
- 源码版本标记：`strategy_runner.py`、`data_fetcher.py`、`config.py` 均声明 `V4.6.2`
- 源码 SHA-256：
  - `data_fetcher.py`：`723bd8803a3e5333f3e48030b718a275691ef0dadf90f562a90bbb56cd2c4abe`
  - `strategy_runner.py`：`8ed05231c3bbb57e3aebe9a34c7d2d20b1feb7ed3fff29d4bb0b92496804af11`
  - `config.py`：`096ebc6882e22f90613e02aa11bedf31caf3c4e67bd3c29c9ae42a96d0e9f5ab`

当前状态：

- `v4-strategy-runner.service`：`inactive/disabled`
- `v4-proxy.service`：`inactive/disabled`，本任务未操作
- `danted.service`：`active/enabled`，本任务未操作
- 未发现容器、cron 或其他进程替代运行 `strategy_runner.py`

## 2. 币安数据源

v4.6.2 使用 **Binance USD-M futures 公共 REST**，不是 WebSocket：

- Base：`https://fapi.binance.com/fapi/v1`
- 客户端：Python `requests.get(..., timeout=10)`
- `ticker/24hr`：全市场 24 小时行情，进程内缓存 60 秒
- `klines`：每币种 30 根 K 线，进程内缓存 120 秒
- `ticker/price`：最新价，缓存 10 秒
- `depth`：订单簿，缓存 5 秒
- `trades`：近期成交，缓存 3 秒
- 策略调度：每小时扫描一次

鉴权和出网：

- 无 Binance API key、签名或 listen key。
- 源码未设置 HTTP/SOCKS proxy。
- systemd unit 无 proxy 环境变量。
- 直接从 SG 公网出口访问 Binance REST；`danted` 是入站代理，不在 v4.6.2 请求链上。
- `v4-proxy.service` 是模型代理，不是 Binance 行情代理。

## 3. 历史与当前活跃性

v4.6.2 **历史上确实持续取得 Binance 数据**，但当前未运行：

- 策略日志最后一轮：`2026-06-13T08:46:06.696Z`
- `signals` 表：3,469 行，最大时间戳 `2026-06-13T08:46:06.690Z`
- 最后信号包含当时的 BTC/ETH/SOL 实时入场价。
- systemd 停止时间：`2026-06-13T09:45:54Z`
- 停止后 `signals` 无新增。

`health_checks` 和 `system_metrics` 仍在由 cron 写入，最大时间分别为
`2026-06-14T13:30:02.198Z` 和 `2026-06-14T13:46:02.184Z`；这些不是币安行情数据，不能据此认定策略仍在收数。

## 4. 同款 REST 探针

探针时间：`2026-06-14T13:47:14Z`，SG 直连、无代理、无鉴权。

| 请求 | HTTP | 现场证据 |
|---|---:|---|
| `/fapi/v1/ticker/24hr?symbol=BTCUSDT` | 200 | 返回实时价格与 closeTime |
| `/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=2` | 200 | 返回 2 根最新 K 线 |
| `/fapi/v1/depth?symbol=BTCUSDT&limit=5` | 200 | 返回 5 档 bid/ask |
| `/fapi/v1/trades?symbol=BTCUSDT&limit=2` | 200 | 返回最新成交 |
| `/fapi/v1/openInterest?symbol=BTCUSDT` | 200 | 返回当前 OI |
| `/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1` | 200 | 返回最近 funding |
| `/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=2` | 200 | 返回历史 OI |

因此“Binance 封整个 SG IP”明确为假。

## 5. WS 根因

Binance 官方在 2026-04-23 后将 futures WS 拆分为：

- `/public`：高频订单簿等
- `/market`：`aggTrade`、ticker、kline、mark price、`forceOrder`
- `/private`：用户数据

未带路由的旧连接只会收到 `/public` 类 stream；`aggTrade` 和 `forceOrder`
在旧 URL 上仍可握手，但不会推送。

官方依据：

- https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams
- https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Important-WebSocket-Change-Notice
- https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Liquidation-Order-Streams

## 6. 采集器修复路径

最小修复只有一处：

```python
WS_URL = "wss://fstream.binance.com/market/ws/!forceOrder@arr"
```

适用文件：

- 本地：`06_RESEARCH/CODE/liquidation_collector.py`
- 远端：`/opt/ai_quant_liq_collector/liquidation_collector.py`

不需要 Binance API key，不需要住宅代理，也不需要 `danted` 出网。
新路由消息仍是顶层 `forceOrder` 对象，现有原始 JSONL 写入和
`forward_liq/liq_parser.py` 的字段约定兼容。

建议在独立修复任务中执行部署和重启，验收顺序：

1. 先用 `/market/ws/btcusdt@aggTrade` 确认 10 秒内有帧。
2. 改为 `/market/ws/!forceOrder@arr` 后重启采集器。
3. 2 分钟内确认 `process_messages > 0`、`last_message_utc` 非空且当日 JSONL 行数增长。
4. 保留小时 heartbeat，以真实帧和文件增量为健康标准。

OI/funding 可直接使用上述公共 REST 端点。`GET /fapi/v1/forceOrders`
查询的是已鉴权账户自身的强平/ADL 订单，不是全市场强平流，不能替代
`!forceOrder@arr`。

## 7. 红线与验收自检

- [x] 定位并确认 v4.6.2 目录、unit 和版本。
- [x] 确认 REST/futures、端点、鉴权、代理和频率。
- [x] 用日志与 DB 最大时间戳区分历史收数和当前停服。
- [x] 完成同机 REST 及旧/新 WS 差分探针。
- [x] 给出强平、OI、funding 的具体修复路径。
- [x] 未启动、停止、重启或修改任何远端服务和文件。
- [x] 未触碰 `danted`、v4.6.2、Holdout 或研究数据。
- [x] 未写入或提交 SSH 密码、代理凭据或 API key。
