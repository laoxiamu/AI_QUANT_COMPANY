# Codex 直调配方（DEC-061 落地，2026-06-11 验证通过）

**通道：** Claude 经 Desktop Commander 调 Codex CLI（v0.139.0，npm @openai/codex；与桌面客户端共享 ~/.codex/auth.json，免登录）。

## 标准调用（三要素缺一卡死）

```bash
cd <项目根> && export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 && \
codex exec --skip-git-repo-check -C /Users/yaomingyu/Documents/AI_QUANT_COMPANY \
  --sandbox workspace-write \
  "$(cat 04_AI_TEAM/CODEX_TASKS/TASK_XXX.md)" < /dev/null
```

1. **代理 env 必须显式给**（CLI 不走系统代理，缺了无输出卡死）。
2. **`< /dev/null` 必须加**（否则等 stdin 卡死）。
3. 写文件任务用 `--sandbox workspace-write`；纯分析可用默认 read-only。
4. **必须显式 `-m gpt-5.5` 指定模型**（2026-07-12 P0-RES-015 教训：CLI v0.139.0 的默认模型已变为 gpt-5.6-sol，需新版 CLI，不带 `-m` 派发即刻报错死掉且 nohup 下无人看见；`-m gpt-5.5` 实测可用。升级 CLI 前所有派发一律带 `-m`，定时任务同样）。

## 护栏（DEC-061 原定，不变）
- 任务书先落文件（04_AI_TEAM/CODEX_TASKS/），调用引用文件——保留文件留痕。
- 七问前置由 Claude 在出任务书时完成；D 级仍人工确认；执行报告回 CODEX_TASKS/REPORT_*.md。
- 项目根已部署 AGENTS.md（Codex 自动读取，含 Protocol 铁律/禁止项）。
- 成本：每次调用 token 用量记入观察（首测 10.8k tokens）；大任务优先夜间。

## DC 稳定性配方（2026-06-22 定，强制）

**根因：** DC 掉线 = App↔DC 的 stdio MCP 心跳被饿死，两个触发器：①VM 大下载热循环吃满 App CPU（实测 172%）；②**Claude 连发长阻塞 DC 调用**（`read_process_output` timeout=180s 连发 ~12min 堵死传输）。DC 进程本身健康（1451 调用仅 6 失败）；掉的是连接。注册表无替代本地 shell 工具，故改用法不换工具。

**铁律（解触发器②，已验证）：**
1. **DC 只做秒级 fire-and-forget。** 派 codex 一律 `nohup ... < /dev/null > LOG 2>&1 &` 发完即返回，不在 DC 上等结果。
2. **轮询一律走 `mcp__workspace__bash` 读挂载的 LOG 文件**（tail/wc/grep），**永不在 DC 上做长阻塞 `read_process_output`**。
3. Mac→VM 挂载有同步时差（数十秒）：DC 侧 tail 可能暂看不到、VM 侧能看到，以 VM 为准。
4. 判进度看：log 行数增长 / 报告文件是否生成 / `TASK_INBOX/{ID}_DONE.json` 是否出现。

**标准派发式：**
```bash
cd /Users/yaomingyu/Documents/AI_QUANT_COMPANY && export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 && \
nohup codex exec -m gpt-5.5 --skip-git-repo-check -C /Users/yaomingyu/Documents/AI_QUANT_COMPANY --sandbox workspace-write \
  "$(cat 04_AI_TEAM/CODEX_TASKS/TASK_XXX.md)" < /dev/null > 04_AI_TEAM/CODEX_TASKS/xxx_run.log 2>&1 &
```
然后 VM：`tail -N 04_AI_TEAM/CODEX_TASKS/xxx_run.log`。

**注意：** Codex 的 429/"Reconnecting" = codex↔OpenAI（限流+双跳代理），与 DC 掉线是两个独立问题，勿混。

**派发后强制验活（2026-07-20 教训，"已派≠在跑"第3次变体）：** 派发后 2-5 分钟内必须查 `wc -l LOG` 是否增长；**进程存在 ≠ 任务在跑**——2026-07-20 外部审计首派用 `--sandbox workspace-write`，进程活着但 ~2h 零输出（log 停在只回显任务书的 54 行），改 `--sandbox danger-full-access` 重派后立即正常流式输出。经验法则：**读全库/需 rg 遍历/联网的任务一律 danger-full-access**；workspace-write 留给纯写文件任务。log 中 `ERROR codex_models_manager: failed to renew cache TTL` 为非致命告警，不影响执行。
**更强可选（未建，待 Founder）：** Mac launchd 监听 trigger 文件夹跑 codex（VM 可写 trigger），彻底脱 DC。

## 数据采集 / 出网通道（2026-06-22 定，强制——根治"沙箱出不去网"反复卡死）

**根因（为什么反复出现）：** ①codex `--sandbox workspace-write` 在 macOS seatbelt 下**封对外网络 socket**——读本地文件的任务不联网故从不暴露，一遇取数任务同模板静默卡死；②RUNBOOK 旧模板写死 `HTTPS_PROXY=127.0.0.1:7897`（Clash），该代理**经常是死的**，每次默认它活着；③取数脚本预检把 HTTP 4xx 当"网络不可达"（4xx=已连通的假阴性）。三层叠加=看似"网络全没"。

**铁律（联网/取数任务 ≠ 本地分析任务，走独立通道）：**
1. **联网任务禁用 codex `--sandbox workspace-write`**（封 socket）。取数走下面两通道之一。
2. **不假设 7897 代理活着。** 实测（2026-06-22）：**Mac 直连 `fapi.binance.com` / `api.llama.fi` 通**；Bybit/defillama 直连 SSL EOF；代理 7897 死。**取数默认直连，把代理 env 全 unset**：`env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy ...`。
3. **通道 A（首选，已验证）：** DC 非沙箱 bash 跑 python 取数脚本，代理 unset 直连，`nohup ... < /dev/null > LOG 2>&1 &` 发，VM 轮询 LOG（同 DC 稳定配方）。
4. **通道 B（兜底/被 geo 挡时）：** SSH SG 服务器 `root@43.160.200.224`（在 SG、无 geo 问题、采集器同源），跑取数 + rsync 回本地 repo（密钥 `~/.ssh/id_ed25519_aiquant`）。
5. **预检纪律：** HTTP 4xx/5xx = 可达（拿到响应），不得判"网络不可达"。`panel_refresh_2026.py` 曾因裸 klines 探测 400 误跳全量，已修（probe 视 HTTPError 为 reachable）。

## 验证记录
2026-06-11：smoke test 返回 CODEX_DIRECT_CALL_OK（model gpt-5.5，session 019eb623）。
2026-06-22：DC 稳定性配方自证——#X3 经 nohup 发、全程 VM 轮询、DC 未碰，跑动期间未掉线（对照 #X2 长阻塞读致 DC 中途断）。
