# FIX-COLLECTOR-URL：采集器一行修复（Binance WS 路由迁移，已查实）

**调用：** `--sandbox danger-full-access`（需 SSH）。
**已查实根因（VERIFY-V462）：** 非IP封锁；Binance 2026-04-23 WS 路由迁移。旧 `wss://fstream.binance.com/ws/!forceOrder@arr`→0帧；新 `wss://fstream.binance.com/market/ws/!forceOrder@arr`→立即收帧（同机已验 3 帧）。
**SSH：** `sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh -o StrictHostKeyChecking=no root@43.160.200.224 "<cmd>"`。**禁浏览器。红线：danted/v4-proxy 不能停；只动 aiquant-liq-collector。**

## 任务
1. 备份 `/opt/ai_quant_liq_collector/liquidation_collector.py` 为 `.bak.20260615`。
2. 把 `WS_URL` 从 `wss://fstream.binance.com/ws/!forceOrder@arr` 改为 `wss://fstream.binance.com/market/ws/!forceOrder@arr`（仅改这一行；其余逻辑不动）。
3. `systemctl restart aiquant-liq-collector`。
4. **验证**：2-3 分钟内 collector.log 出现 `[message]`、`process_messages>0`、`/opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_YYYYMMDD.jsonl` 出现且行数增长；贴日志+样本首行证据（确认含 `o.S` side 字段）。
5. 若新路由仍 0 帧→回滚 .bak，报告并改用 VERIFY-V462 的 REST 方案备选（`/fapi/v1` futures REST 轮询强平/OI）。

## 安全：**不要把任何 API key / 密码写入报告或 commit**；若 run 日志混入服务器上无关服务的凭据，脱敏，且该 run 日志不纳入 git。
## 完成写 `04_AI_TEAM/TASK_INBOX/FIX_COLLECTOR_URL_DONE.json`(task_id=FIX_COLLECTOR_URL,fixed=yes/no,frames_after=N,notes)。报告 `REPORT_FIX_COLLECTOR_URL.md`。
