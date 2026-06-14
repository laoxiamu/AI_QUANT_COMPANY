# FIX-COLLECTOR-V2：采集器零采集修复（已诊断=Binance 限服务器IP的WS行情流）

**调用：** 本任务需网络，由调用方用 `--sandbox danger-full-access` 启动（workspace-write 关 shell 网络）。
**已诊断（Claude 2026-06-14，勿重复推翻，可验证）：** 采集器代码健康（run_forever 含 ping_interval=180 + 重连）。但腾讯云SG服务器(43.160.200.224)上：REST `fapi/v1/ping` HTTP200 正常；**WS `wss://fstream.binance.com/ws/...` 握手 OPEN 成功但 0 帧**（aggTrade 20s/forceOrder 25s 均 0 帧，forceOrder OPEN 后立即 CLOSE）→ **Binance 不向该云IP推送行情流**（数据中心IP限制）。故 22h `process_messages=0`。
**SSH：** `sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh -o StrictHostKeyChecking=no root@43.160.200.224 "<cmd>"`。**禁浏览器/WebShell**，只命令行。
**服务器红线：** danted.service/v4-proxy.service **绝不能停**；只动 aiquant-liq-collector 与 /opt/ai_quant_liq_collector/。

## 任务：让采集器经"干净IP"拿到行情
1. **复核诊断**（可选快验）：服务器上同款 websocket-client 直测 aggTrade 20s 计帧确认 0。
2. **方案A：经住宅代理路由 WS**。住宅 SOCKS5 凭据在 `~/.aiquant_sealed/resi_proxy`（格式 `socks5 HOST PORT USER PASS`）。
   - 先测服务器能否直连该住宅代理（SG 内网应可达）：`curl -m10 -x socks5h://USER:PASS@HOST:PORT https://fapi.binance.com/fapi/v1/ping`。
   - 用 websocket-client 经该 SOCKS5 连 `!forceOrder@arr`（`http_proxy_host/port + proxy_type='socks5h' + http_proxy_auth`），测 30s 是否有帧。
   - **若有帧** → 修改 `liquidation_collector.py`：WS 连接走该 SOCKS5（代理参数从环境变量/项目外配置读，**禁止把密码硬编码进会被 git/日志暴露的地方**），备份原文件 .bak，重启服务，**验证 2 分钟内 process_messages>0 且 LIQUIDATIONS 出现当日 jsonl 行数增长**，贴证据。
3. **方案B（A 不通时）**：测试其它可达且 Binance 放行的出口（如新加坡跳板 danted 自身 SOCKS、或其它），择一可行者同法接入。
4. **都不通** → 不强改，报告：确认是 IP 限制、各出口测试结果、建议（换非云住宅IP托管采集器 / 用第三方数据源）。**路径B当前休眠，修不成不阻塞，如实报告即可。**

## 完成写 `04_AI_TEAM/TASK_INBOX/FIX_COLLECTOR_DONE.json`(task_id=FIX_COLLECTOR,status,fixed=yes/no,route=直连/住宅代理/跳板/未解决,frames_after=N,notes)。报告 `REPORT_FIX_COLLECTOR.md`。**不 commit 任何含密码内容。**
