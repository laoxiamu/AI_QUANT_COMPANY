# REPORT_FIX_COLLECTOR_URL

## 结论

- 任务状态：`completed`
- 修复结果：`fixed=yes`
- 根因：Binance futures WS 路由迁移；旧 `/ws/` 路由握手后不再推送 `forceOrder`
- 新 URL：`wss://fstream.binance.com/market/ws/!forceOrder@arr`
- 回滚：未触发
- REST 备选：未启用

## 1. 修复前证据

远端文件：

`/opt/ai_quant_liq_collector/liquidation_collector.py`

修复前 SHA-256：

```text
0c2db657ee4bbf0a9e66ff383c9ac30b1dfd39ecf070c3cf916e4008e3251c7c
```

修复前 URL：

```python
WS_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
```

`logs/collector.log` 从 2026-06-13T10:43:04Z 至
2026-06-14T23:43:04Z 的小时 heartbeat 均为：

```text
today_rows= 0 process_messages= 0 last_message_utc= None
```

修复前没有 `data/LIQUIDATIONS/liq_*.jsonl`。

## 2. 变更与备份

备份已创建：

```text
/opt/ai_quant_liq_collector/liquidation_collector.py.bak.20260615
```

备份 SHA-256 与修复前文件一致：

```text
0c2db657ee4bbf0a9e66ff383c9ac30b1dfd39ecf070c3cf916e4008e3251c7c
```

`diff -u` 确认远端仅改一行：

```diff
-WS_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
+WS_URL = "wss://fstream.binance.com/market/ws/!forceOrder@arr"
```

修复后 SHA-256：

```text
1bd580965527d6884f0fe4e151d48e7f69cf7153d8e1207282ec145fdbf80a36
```

本地规范脚本 `06_RESEARCH/CODE/liquidation_collector.py` 同步了相同的一行，
其余逻辑未改。

## 3. 重启与实时验收

执行：

```text
systemctl restart aiquant-liq-collector.service
```

重启后：

```text
ActiveEnterTimestamp=Mon 2026-06-15 08:38:31 CST
MainPID=4039584
active
```

日志在首秒内收到消息：

```text
[connected] 2026-06-15T00:38:32.263426+00:00 wss://fstream.binance.com/market/ws/!forceOrder@arr
[message] 2026-06-15T00:38:32.830360+00:00 count= 1
[message] 2026-06-15T00:38:39.442301+00:00 count= 2
[message] 2026-06-15T00:39:05.586781+00:00 count= 3
```

`[message] count=1` 直接证明进程内消息计数大于 0。现有程序只在每小时
heartbeat 输出 `process_messages=` 字面量，因此在不得修改其余逻辑的约束下，
2-3 分钟验收使用同一 `_message_count` 的 `[message] count>0` 证据。

首次检查时文件从 10 行增至 11 行；持续性复验：

```text
2026-06-15T00:42:58Z rows=62
2026-06-15T00:44:58Z rows=92
delta=30
```

验收时 `frames_after=92`。

数据文件：

```text
/opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_20260615.jsonl
```

样本首行：

```json
{"e":"forceOrder","E":1781483912792,"o":{"s":"ETHUSDT","S":"SELL","o":"LIMIT","f":"IOC","q":"0.023","p":"1713.87","ap":"1720.61","X":"FILLED","l":"0.023","z":"0.023","T":1781483911784},"recv_ts":1781483912830}
```

解析确认：

```text
event=forceOrder
symbol=ETHUSDT
o.S=SELL
```

## 4. 安全与验收自检

- [x] 创建指定 `.bak.20260615` 备份。
- [x] 远端仅替换 `WS_URL` 一行。
- [x] 仅重启 `aiquant-liq-collector.service`。
- [x] 2-3 分钟内出现 `[message]` 且进程消息计数大于 0。
- [x] UTC 当日 JSONL 创建并持续增长。
- [x] 样本包含 `o.S` side 字段。
- [x] `danted.service` 始终为 `active`，未操作。
- [x] `v4-proxy.service` 检查前后均为 `inactive`，未操作。
- [x] 未读取 Holdout，未改预登记，未引入依赖。
- [x] 报告和提交不含密码、API key 或代理凭据。
- [x] run log 不纳入本任务提交。
