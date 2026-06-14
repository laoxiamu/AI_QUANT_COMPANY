# VERIFY-V462：核实历史 v4.6.2 的币安数据源（可能推翻"Binance封本IP"结论）

**调用：** 需网络+SSH，用 `--sandbox danger-full-access`。
**背景（Founder 提供线索）：** 腾讯云SG服务器(43.160.200.224)上有**之前部署的历史版本 v4.6.2**，其数据源**也是币安**（疑与 `v4-strategy-runner.service` / `v4-proxy.service` 相关）。
**关键疑问：** 我（Claude）此前测得 `wss://fstream.binance.com/ws/!forceOrder@arr`（**futures 公共WS**）经 SG直连+住宅代理均握手后0帧，据此判"Binance 封本IP"。**但若 v4.6.2 能正常从币安取数，说明该结论过宽**——v4.6.2 可能用的是币安 REST / 现货WS / 不同 futures 端点 / 带鉴权 / 经某代理，那才是修采集器的正路。**本任务核实之，勿想当然。**

**SSH：** `sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh -o StrictHostKeyChecking=no root@43.160.200.224 "<cmd>"`。**禁浏览器/WebShell。服务器红线：danted/v4-proxy 绝不能停；只读不改 v4.6.2（核实性质，不动生产）。**

## 任务
1. **定位 v4.6.2**：找其部署目录/服务（systemctl 查 v4-strategy-runner 等、ps、/opt 或 /root 下 v4* 目录）、版本号确认。
2. **识别其币安数据源**：读其代码/配置——用的是 REST 还是 WS？现货(spot)还是合约(futures/fapi/fstream)？哪个端点/stream？是否带 API key 鉴权？是否经代理(danted/住宅)出网？拉取频率/方式。
3. **核实它现在是否真在取到币安数据**：看其日志/数据文件/DB 最近写入时间戳，确认当前是否活跃收数（不只是 service active）。
4. **关键对照**：在服务器上用 v4.6.2 的**同款方法/端点**做一次最小取数测试（如它用 REST 则 curl 其端点、用某 WS 则连该 WS 计帧），与我们采集器的 `fstream forceOrder WS` 对照——**区分"Binance 封整个IP" vs "只是某些 futures 公共WS端点/方式不通"**。
5. **结论与修复建议**：若 v4.6.2 的方法能取到币安数据 → 给出采集器改用该方法取强平/OI 数据的具体路径（端点、是否需鉴权、是否经代理）；若 v4.6.2 也取不到/已停 → 确认 IP 级封锁结论。

## 完成写 `04_AI_TEAM/TASK_INBOX/VERIFY_V462_DONE.json`(task_id=VERIFY_V462,v462_path,binance_source=REST/WS+spot/futures+端点,currently_active=yes/no,verdict=IP全封/仅某端点不通/v4.6.2方法可用,fix_path=...,notes)。报告 `04_AI_TEAM/CODEX_TASKS/REPORT_VERIFY_V462.md`。**只读不改生产，不commit密码。**
