# REPORT_FIX_COLLECTOR

## 结论

- 任务状态：`completed`
- 修复状态：`fixed=no`
- 路由：`未解决`
- 修复后 Binance 帧数：`0`
- 记录时间：`2026-06-14T13:20:23Z`

**专业判断：** 零采集不是采集器代码、`websocket-client` 或 SOCKS 数据面故障。住宅代理使用独立出口，且同一路径能正常接收 Coinbase WebSocket 帧，但 Binance futures 流仍只完成握手、不下发数据帧。现有两个出口均被 Binance 限制，不能通过配置修改恢复采集。

按任务书“都不通则不强改”分支，未修改或重启生产采集器。

## 执行前自查

1. 验证机制：更换 WS 出口后，Binance 是否恢复真实数据帧。
2. 验收标准：住宅代理 `!forceOrder@arr` 30 秒有帧；接入后 2 分钟内 `process_messages > 0` 且当日 JSONL 行数增长。
3. 最小实现：仅在出口探针有帧后才注入环境变量和代理参数；探针失败则不改生产。
4. 禁止项：未触碰 Holdout、研究数据、成本模型或其他业务服务；未使用浏览器/WebShell；未记录或提交代理凭据。

## 证据

| 路径 | 目标 | 结果 |
|---|---|---|
| SG 直连 | `btcusdt@aggTrade`，20 秒 | 握手成功，`0` 帧 |
| 住宅 SOCKS5H | Binance REST | SOCKS reply `4`，代理端 DNS 无法完成 Binance 连接 |
| 住宅 SOCKS5 | Binance REST | HTTP `200` |
| 住宅 SOCKS5 | `btcusdt@aggTrade`，20 秒 | 握手成功，`0` 帧 |
| 住宅 SOCKS5 | `!forceOrder@arr`，30 秒 | 握手成功，`0` 帧 |
| 住宅 SOCKS5 | Coinbase ticker WS | 2.5 秒收到 `3` 帧 |

额外核验：

- 住宅代理出口与 SG 直连出口不同，排除“实际未走代理”。
- `danted.service` 是该 SG 跳板的入站 SOCKS，出口仍是已验证零帧的 SG 公网路径，不构成第三个独立出口。
- 本机密封目录只有 `sg_pass` 与 `resi_proxy`，无其他出口凭据。

## 服务器状态

- `danted.service`：`active`，本任务未操作。
- `v4-proxy.service`：任务开始前已是 `inactive/disabled`；本任务未启动、停止或修改。
- `aiquant-liq-collector.service`：`active/running`，PID 未变，`NRestarts=0`。
- 远端采集器源码时间与大小未变：`2026-06-13 17:42:21 +0800`，2899 bytes。
- 最终数据行数：`0`；最新 heartbeat 仍为 `process_messages=0`。

探针期间仅在 `/opt/ai_quant_liq_collector/.deps` 临时 vendoring `python-socks 2.8.1`，用于验证 SOCKS WebSocket；结束后已删除。未创建 `.bak`，因为没有进入生产修改分支。

## 建议

1. 将采集器迁移到先经 30 秒 Binance `aggTrade` 实测有帧的非云住宅网络，再部署 `forceOrder` 采集。
2. 若无法获得可用出口，改用能提供原始强平方向、价格、数量和事件时间的第三方数据源。
3. 不应把“REST 200”或“WS OPEN”作为数据面健康标准；监控必须继续以消息计数和 JSONL 增量为准。

## 敏感信息检查

SSH 密码由 `sshpass -f ~/.aiquant_sealed/sg_pass` 读取；住宅凭据只经 SSH 标准输入传入临时文件并立即删除。报告、项目文件和命令输出均未写入代理主机、用户名或密码。
