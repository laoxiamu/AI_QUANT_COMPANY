# FIX-COLLECTOR：强平采集器零采集修复（22h process_messages=0）

**问题（已诊断）：** 腾讯云SG VM 上 `aiquant-liq-collector.service` 显示 active，但 22 小时 `process_messages=0 / last_message_utc=None`，`/opt/ai_quant_liq_collector/data/LIQUIDATIONS/` 无任何 .jsonl。日志只有一条 `[connected]`（2026-06-13T09:43 UTC），之后无 `[message]`、无 `ws error`、无 `ws closed`——**连上一次后静默假死，0 帧**。采集器用 `import websocket`（websocket-client 同步库），订阅 `wss://fstream.binance.com/ws/!forceOrder@arr`。
**最可能根因：** `run_forever` 缺 ping 保活（`ping_interval/ping_timeout`）→ Binance 端 ~10min 静默断开但客户端未触发 on_close/重连 → 连接半开假死；或缺自动重连循环。
**SSH：** `sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh -o StrictHostKeyChecking=no root@43.160.200.224`（密码在项目外文件，**禁止写入任何会被 git 提交的文件、禁止 echo 进日志**）。

## 服务器红线（勿动）
- **danted.service / v4-proxy.service 绝对不能停**（全局翻墙出口+链式代理跳板，停了 Mac 侧全断）。
- 只动 `aiquant-liq-collector.service` 与 `/opt/ai_quant_liq_collector/`。改前先 `systemctl list-units --state=running | grep -E 'danted|v4-proxy'` 确认在跑。

## 任务
1. SSH 读 `/opt/ai_quant_liq_collector/liquidation_collector.py` 完整代码，确认 `main()` 里 `run_forever` 调用方式。
2. **先取证**：在服务器用采集器同款 `websocket` 库写个 ~30s 自测，连 `!forceOrder@arr`，确认能否收到帧（区分"代码 bug" vs "stream/网络问题"）。Binance forceOrder 是稀疏流但全市场每分钟应有多帧。
3. **修复**（最小改动，可审计）：
   - `run_forever(ping_interval=180, ping_timeout=60, reconnect=5)` 或等价；
   - 外层 `while True` 自动重连循环（异常/断开后 sleep 重连，指数退避封顶）；
   - on_open 后日志确认订阅；首 3 帧打印样本；
   - 保持原始 JSONL 写盘逻辑与字段不变（完整原始消息 + recv_ts）。
4. 重启服务 `systemctl restart aiquant-liq-collector`，**验证 2 分钟内 `process_messages>0` 且 LIQUIDATIONS 下出现当日 .jsonl 且行数增长**；贴日志证据。
5. 备份原文件为 `liquidation_collector.py.bak` 再改。

## 完成
写 `04_AI_TEAM/TASK_INBOX/FIX_COLLECTOR_DONE.json`(task_id=FIX_COLLECTOR,status,fixed=yes/no,frames_after_restart=N,notes=根因一句话+验证证据)。报告 `04_AI_TEAM/CODEX_TASKS/REPORT_FIX_COLLECTOR.md`。**不要 commit 任何含密码的内容。**
