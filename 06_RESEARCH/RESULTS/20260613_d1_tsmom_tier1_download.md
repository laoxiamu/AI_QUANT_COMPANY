# D1 TSMOM Tier 1 数据下载结果

## 结论

D1 数据下载未完成。原因是当前 Codex 沙箱禁止出站网络连接，首次请求 Binance monthly kline ZIP 时返回：

```text
network permission denied: [Errno 1] Operation not permitted
```

Node `fetch` 对同一 URL 的 HEAD 请求也失败，错误为 `getaddrinfo ENOTFOUND data.binance.vision`。

因此不能声称 Tier 1 数据采集成功，也不能进入依赖该 expanded universe 的 D2 回测。

## 已产出

- 可复跑脚本：`06_RESEARCH/CODE/d1_tsmom_tier1_download.py`
- Manifest：`06_RESEARCH/DATA/FUTURES_EXPANDED/DOWNLOAD_MANIFEST.json`
- CODEX 报告：`04_AI_TEAM/CODEX_TASKS/REPORT_D1.md`

Manifest 当前摘要：

```json
{"total": 35, "success": 0, "failed": 35}
```

## 恢复命令

在允许访问 Binance archive 的环境中运行：

```bash
python3 06_RESEARCH/CODE/d1_tsmom_tier1_download.py --force
```
