# 20260612 Collector Data-Plane Diagnostic

## Scope

- Task: B5 only; test Binance USDT-M `btcusdt@aggTrade` WebSocket data frames through independent Mac-side paths.
- Payload discipline: raw trade frames and prices were not persisted; only transport metadata was written.
- Run timestamp UTC: `2026-06-12T17:24:27+00:00`.
- Per-path target window: `60.0s`.

## Tool Availability

- curl: `/usr/bin/curl` does not advertise ws/wss protocol support.
- websocat: not installed.

## 判定矩阵

| Path | Client | Proxy | URL | Handshake | Frames | First frame s | Elapsed s | Verdict | Error |
|---|---|---|---|---:|---:|---:|---:|---|---|
| websocket_client_http_ws | websocket-client | http://127.0.0.1:7897 | wss://fstream.binance.com/ws/btcusdt@aggTrade | YES | 0 |  | 60.545 | HANDSHAKE_ONLY_ZERO_FRAMES |  |
| websockets_socks_ws | websockets | socks5://127.0.0.1:7897 | wss://fstream.binance.com/ws/btcusdt@aggTrade | YES | 0 |  | 65.005 | HANDSHAKE_ONLY_ZERO_FRAMES |  |
| websocket_client_http_stream | websocket-client | http://127.0.0.1:7897 | wss://fstream.binance.com/stream?streams=btcusdt@aggTrade | YES | 0 |  | 61.189 | HANDSHAKE_ONLY_ZERO_FRAMES |  |
| websockets_socks_stream | websockets | socks5://127.0.0.1:7897 | wss://fstream.binance.com/stream?streams=btcusdt@aggTrade | NO | 0 |  | 0.545 | CONNECT_FAIL | ConnectionResetError:  |
| websocket_client_http_stream_explicit_443 | websocket-client | http://127.0.0.1:7897 | wss://fstream.binance.com:443/stream?streams=btcusdt@aggTrade | YES | 0 |  | 60.266 | HANDSHAKE_ONLY_ZERO_FRAMES |  |
| websockets_socks_stream_explicit_443 | websockets | socks5://127.0.0.1:7897 | wss://fstream.binance.com:443/stream?streams=btcusdt@aggTrade | YES | 0 |  | 65.003 | HANDSHAKE_ONLY_ZERO_FRAMES |  |

## Layer Diagnosis

All handshake-capable Mac-side paths received zero aggTrade frames for the full 60s windows across independent client/proxy/URL combinations. This rules out a single Python library failure and points below the library layer, most likely Clash/upstream VM forwarding or provider data-plane filtering. Mac-side collector changes are not sufficient; run on the VM directly. Non-handshake variants: websockets_socks_stream.

## Collector Patch Recommendation

全部测试路径 60s 零数据帧；按任务书口径，结论为 "Mac 侧无解，须 VM 直跑"。不建议在 Mac 采集器上继续打补丁。

## Reproducibility

```bash
PYTHONPATH=/private/tmp/ai_quant_b5_deps python3 06_RESEARCH/CODE/collector_dataplane_diag.py --duration 60
```

JSON output: `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/output/collector_dataplane_diag.json`

## Protocol Notes

- No HOLDOUT path was read.
- The diagnostic script does not read `06_RESEARCH/DATA/`.
- During initial repository search, a broad `rg` command accidentally printed post-cutoff market rows because the text pattern matched numeric values. Those rows were not used in this diagnostic or conclusion.
