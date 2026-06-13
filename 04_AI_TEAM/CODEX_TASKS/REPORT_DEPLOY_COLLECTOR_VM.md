# REPORT_DEPLOY_COLLECTOR_VM

**执行时间：** 2026-06-13 UTC
**目标服务器：** Tencent Cloud Lighthouse Singapore `43.160.200.224`
**执行人：** Codex

## 结论

强平采集器已部署到新加坡腾讯云服务器，并以独立 systemd 服务常驻运行。

- 服务名：`aiquant-liq-collector.service`
- 部署目录：`/opt/ai_quant_liq_collector`
- 脚本：`/opt/ai_quant_liq_collector/liquidation_collector.py`
- 数据目录：`/opt/ai_quant_liq_collector/data/LIQUIDATIONS/`
- 日志：`/opt/ai_quant_liq_collector/logs/collector.log`

## 保护既有服务

部署未改动已有跳板代理、V4.6.2、Docker/OpenClaw、nginx。

部署后确认以下服务仍为 `active`：

- `danted.service`
- `v4-proxy.service`
- `v4-strategy-runner.service`
- `docker.service`
- `nginx.service`

## 验证记录

服务器环境：

- 用户：`root`
- 主机：`VM-0-14-ubuntu`
- 系统：Ubuntu 24.04.4 LTS
- Python：`3.12.3`
- `websocket-client`：`1.7.0`

网络验证：

- `https://fapi.binance.com/fapi/v1/ping` 返回 `{}`
- `https://fapi.binance.com/fapi/v1/time` 返回 serverTime
- `wss://fstream.binance.com/ws/btcusdt@trade` 直连成功，收到 3 条真实成交数据帧

服务验证：

- `systemctl status aiquant-liq-collector.service` 显示 `Active: active (running)`
- 25 秒后复查：`ActiveState=active`，`SubState=running`，`NRestarts=0`
- 日志出现 `[connected] ... wss://fstream.binance.com/ws/!forceOrder@arr`

## 当前数据状态

截至部署验收时，强平数据目录尚未产生 `liq_YYYYMMDD.jsonl`。这是低频强平事件流的可接受状态；服务已连接，后续有强平事件时会写入 JSONL。

## 后续检查命令

```bash
systemctl status aiquant-liq-collector.service --no-pager -l
tail -n 50 /opt/ai_quant_liq_collector/logs/collector.log
ls -la /opt/ai_quant_liq_collector/data/LIQUIDATIONS/
wc -l /opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_*.jsonl
```

