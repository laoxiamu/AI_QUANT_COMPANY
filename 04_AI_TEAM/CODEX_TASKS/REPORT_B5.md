# REPORT_B5 - 采集器数据面隔离测试

**任务来源:** `04_AI_TEAM/CODEX_TASKS/BATCH_20260612N.md` B5  
**执行时间:** 2026-06-12 UTC  
**执行范围:** 只执行 B5；未执行/修改 B1-B4  
**结论:** 全部可握手 Mac 侧路径 60s 零 `aggTrade` 数据帧。按任务书口径判定：**Mac 侧无解，须 VM 直跑**。

## 任务前自查

| 问题 | 回答 |
|---|---|
| 验证机制 | 验证 fstream WebSocket 是库/URL/proxy 用法问题，还是 Clash/跳板 VM 数据面转发问题 |
| 验收标准是否可量化 | 是；>=3 条独立路径，各观察 60s，记录是否收到数据帧 |
| 更便宜等效实现 | 是；只做实时数据面元信息诊断，不改采集器，不落盘原始成交 payload |
| 是否触碰禁止项 | 不读 HOLDOUT，不读 `06_RESEARCH/DATA/`；但初始 broad `rg` 误显过 post-cutoff 行情行，见“偏差记录” |

## 产出

- CODE: `06_RESEARCH/CODE/collector_dataplane_diag.py`
- RESULTS: `06_RESEARCH/RESULTS/20260612_collector_dataplane.md`
- JSON: `06_RESEARCH/CODE/output/collector_dataplane_diag.json`

## 执行命令

```bash
python3 -m pip install --quiet --target /private/tmp/ai_quant_b5_deps 'websockets>=15,<16'
python3 -m py_compile 06_RESEARCH/CODE/collector_dataplane_diag.py
PYTHONPATH=/private/tmp/ai_quant_b5_deps python3 06_RESEARCH/CODE/collector_dataplane_diag.py --duration 60
```

## 判定矩阵

| Path | Client | Proxy | URL | Handshake | Frames | Elapsed s | Verdict |
|---|---|---|---|---:|---:|---:|---|
| websocket_client_http_ws | websocket-client | http://127.0.0.1:7897 | `wss://fstream.binance.com/ws/btcusdt@aggTrade` | YES | 0 | 60.545 | HANDSHAKE_ONLY_ZERO_FRAMES |
| websockets_socks_ws | websockets | socks5://127.0.0.1:7897 | `wss://fstream.binance.com/ws/btcusdt@aggTrade` | YES | 0 | 65.005 | HANDSHAKE_ONLY_ZERO_FRAMES |
| websocket_client_http_stream | websocket-client | http://127.0.0.1:7897 | `wss://fstream.binance.com/stream?streams=btcusdt@aggTrade` | YES | 0 | 61.189 | HANDSHAKE_ONLY_ZERO_FRAMES |
| websockets_socks_stream | websockets | socks5://127.0.0.1:7897 | `wss://fstream.binance.com/stream?streams=btcusdt@aggTrade` | NO | 0 | 0.545 | CONNECT_FAIL: ConnectionResetError |
| websocket_client_http_stream_explicit_443 | websocket-client | http://127.0.0.1:7897 | `wss://fstream.binance.com:443/stream?streams=btcusdt@aggTrade` | YES | 0 | 60.266 | HANDSHAKE_ONLY_ZERO_FRAMES |
| websockets_socks_stream_explicit_443 | websockets | socks5://127.0.0.1:7897 | `wss://fstream.binance.com:443/stream?streams=btcusdt@aggTrade` | YES | 0 | 65.003 | HANDSHAKE_ONLY_ZERO_FRAMES |

Tool availability:

- `curl`: installed at `/usr/bin/curl`, but curl 8.7.1 on this Mac does not advertise `ws/wss` protocol support.
- `websocat`: not installed.

## 诊断

5 条可握手路径覆盖了不同 client、HTTP/SOCKS 代理方式、`/ws` 与 `/stream?streams=` URL 形态；全部完整观察约 60s 且零数据帧。`websockets+socks+/stream` 隐式 443 变体握手被 reset，但同 URL 的 `websocket-client+http` 可握手仍零帧，显式 443 的两条路径也可握手仍零帧。

因此问题不支持“单一 Python 库 bug”解释；更可能断在 Clash 到新加坡跳板的 WebSocket 数据面转发，或上游 VM/供应商对 Binance futures stream 的数据帧过滤。Mac 侧采集器改 URL/库/HTTP-vs-SOCKS 都不足以恢复数据帧。

## 采集器建议

按任务书分支：**全部零帧 -> Mac 侧无解，须 VM 直跑**。不建议直接修改 `06_RESEARCH/CODE/liquidation_collector.py`。

若 Claude 后续仍要求 Mac 侧兜底，最低限度只能增加“握手成功但 60s 零业务帧”健康检查并触发重连/告警；这不是 B5 的修复路径。

## 验收自检

| 验收项 | 状态 | 说明 |
|---|---|---|
| 只做 B5 | PASS | 未执行 B1-B4；未修改其他任务代码 |
| 读取批次头部铁律和 AGENTS.md | PASS | 已读取 |
| 读取 B5 引用的预登记/数据 | PASS | B5 未引用预登记或历史数据；未读取 B5 所需以外数据源 |
| >=3 种独立路径 | PASS | 6 条路径，5 条可握手并完整观察 |
| 每条观察 60s | PASS | 可握手路径 elapsed 60.266-65.005s；不可握手路径记录连接失败 |
| 判断数据帧而非建连 | PASS | 矩阵区分 handshake 与 frames，frames 全为 0 |
| curl/websocat 可用性检查 | PASS | curl 不支持 ws/wss；websocat 未安装 |
| 若全部零帧给出 VM 直跑结论 | PASS | 已给出 |
| 不直接改采集器 | PASS | 仅给建议，未修改采集器 |
| 输出 RESULTS + CODEX_TASKS 报告 | PASS | 已完成 |
| git commit | N/A | 批次头部明确“全程禁 git commit”，未提交 |

## 偏差记录

初始检索命令虽排除了 HOLDOUT，但范围包含 `06_RESEARCH/DATA/` 和部分 output CSV，关键词 `7897` 命中数值导致终端误显了 2024-12-10 后行情行。后续已停止读取这些路径；B5 诊断脚本不读取 `06_RESEARCH/DATA/`，也未使用误显内容形成任何结论。该偏差已同步写入 RESULTS 的 Protocol Notes。

