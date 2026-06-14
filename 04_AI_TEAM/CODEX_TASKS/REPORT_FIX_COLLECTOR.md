# REPORT_FIX_COLLECTOR

## 当前状态

- 状态：`blocked`
- `fixed`：`no`
- `frames_after_restart`：`0`
- 记录时间：2026-06-14T09:24:32Z
- 服务器变更：无；所有 SSH 尝试均未进入 TCP 握手，未执行任何远端命令。
- 红线服务：未能读取状态，但本次未触达服务器，因此未停止或修改 `danted.service`、`v4-proxy.service`。
- 敏感信息：密码仅由 `~/.aiquant_sealed/sg_pass` 传给 `sshpass`，未打印、未写入项目文件。

## 执行前自查

1. 验证机制：区分采集器连接保活/重连缺陷与 Binance 流或 SG 网络异常，并以重启后收帧和 JSONL 增长验收。
2. 验收标准：2 分钟内 `process_messages > 0`、当日 JSONL 出现且行数增长，标准可量化。
3. 最小实现：远端 30 秒同库自测后，仅补 ping、外层重连和前三帧日志，不改变原始消息与 `recv_ts` 写盘结构。
4. 禁止项：未触碰 Holdout、研究数据、成本模型或其他服务器服务；未使用浏览器、Computer Use、Chrome、WebShell。

## SSH 取证

- `sshpass`：`/opt/homebrew/bin/sshpass`
- 密码文件：可读，权限 `0600`
- `HTTPS_PROXY`：`http://127.0.0.1:7897`
- 普通 SSH、`ssh -vvv`、清空代理环境并使用 `ssh -F /dev/null` 三种调用均失败。
- 共同失败点：OpenSSH 已创建 socket，但连接 `43.160.200.224:22` 时本地 `connect()` 立即返回 `Operation not permitted`。
- `ssh -vvv` 未显示远端 banner、密钥交换或认证步骤，证明失败发生在本地执行沙箱网络策略层，不是密码错误或远端 SSH 拒绝。
- 本地 `route -n get 43.160.200.224` 也在创建路由 socket 时返回 `Operation not permitted`，与网络沙箱限制一致。

## 待验证假设

1. 缺少 ping 保活和可靠外层重连导致连接半开；预测是补齐后服务持续收帧。
2. SG 到 Binance force-order 流或网络异常；预测是 30 秒独立同库客户端同样收不到帧。
3. 远端实际源码或 `websocket-client` 版本与任务描述不一致；预测是完整源码和版本检查会发现差异。
4. 回调处理或写盘路径异常；预测是独立客户端能收帧，但服务仍不增加消息或文件行数。

以上假设均因 SSH 被本地沙箱阻断而未执行验证，不能将任一项报告为已确认根因。

## 已完成

1. 读取项目约束、任务书和已有报告。
2. 完成本地 SSH 前置检查和三次连接复核。
3. 确认阻断发生在本地 TCP 建连前，服务器未被修改。
4. 写入 `TASK_INBOX/FIX_COLLECTOR_DONE.json`；后台调度器已将事件消费至 `TASK_INBOX/PROCESSED/FIX_COLLECTOR_DONE.json`。

## 尚未完成

1. 确认 `danted.service` 与 `v4-proxy.service` 正在运行。
2. 读取远端 `liquidation_collector.py` 完整代码和 `run_forever` 调用。
3. 执行约 30 秒同库 WebSocket 收帧自测。
4. 创建 `liquidation_collector.py.bak` 并实施最小修复。
5. 重启 `aiquant-liq-collector.service`。
6. 在 2 分钟窗口验证消息数、当日 JSONL 和行数增长并采集日志证据。

## 恢复前提

在允许本地命令出站连接 `43.160.200.224:22` 的执行环境中，继续使用任务书指定的 `sshpass` SSH 命令。不得改用浏览器、Computer Use、Chrome、腾讯云 WebShell或其他远端入口。
