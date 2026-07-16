# Codex 任务：核实并修复强平采集器（风险E 复发排查）

**类型：** VM 运维诊断/修复（你当初部署了它，access 路径在你侧）。
**触发：** B1-KILLCARD 审计发现本地 `06_RESEARCH/DATA/LIQUIDATIONS/`=0 文件、collector.log 155 心跳全 0 行、dataplane 诊断 Mac 侧零帧。与记录"采集器 2026-06-15 已修复收数"冲突=疑风险E（信 service active 未验真实数据流）复发。Claude 侧 SSH 直连被拒（无密钥）。

## 必须查清（逐项给事实，不要乐观判断）
1. **VM 上采集器进程/服务真实状态**（腾讯SG `root@43.160.200.224`，`/opt/ai_quant_liq_collector/`）：service active≠收数，必须看**真实数据增量**。
2. **真实数据流**：最近 24h 是否有非零 liquidation rows 落盘？给最新数据文件名/大小/mtime/行数增量。
3. **若零帧/零行**：定位根因——WS URL 是否又被迁移（参 P1-RES-012 的 2026-04-23 路由迁移史）？握手 OPEN 后零帧？代理/网络？进程崩溃未重启？
4. **修复**：能改 WS URL/重启/补重连就修；修后**验证真实收到非零帧**（不要只报 service active）。
5. **数据回流**：确认 VM 上的数据如何同步到研究可用处（本地 repo `06_RESEARCH/DATA/LIQUIDATIONS/` 为何 0 文件——是 VM 没收、还是收了没同步？）。

## 交付
- 报告 `04_AI_TEAM/CODEX_TASKS/REPORT_VERIFY_LIQ_COLLECTOR_20260621.md`：真实状态 + 根因 + 已修/未修 + 验证证据（实际帧数/行数增量截图级事实）+ 数据回流方案。
- 写 TASK_INBOX DONE.json。
- **诚实纪律**：不得用"service active/进程在跑"代替"真实数据流验证"（这正是上次的教训）。修不好就如实报阻塞与所需。
- 边界：只动采集器/运维，不碰 Holdout、不改 Claude 独占权威文件、不下单。
