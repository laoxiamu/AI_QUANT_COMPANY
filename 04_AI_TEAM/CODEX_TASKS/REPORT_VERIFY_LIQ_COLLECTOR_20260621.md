# REPORT_VERIFY_LIQ_COLLECTOR_20260621

**任务状态：** blocked  
**执行时间：** 2026-06-21T16:43:20Z  
**目标：** 核实并修复 Tencent SG VM `root@43.160.200.224:/opt/ai_quant_liq_collector/` 强平采集器真实数据流  
**结论纪律：** 本次没有拿到 VM 事实，不能声明 VM 采集器已修复或当前仍在收数。执行过程中本地 `06_RESEARCH/DATA/LIQUIDATIONS/` 从初始观测的 0 文件状态变为已有 `liq_20260615.jsonl` 至 `liq_20260621.jsonl`，证明研究目录已有一批强平 JSONL 数据回流/显现；但仍不能替代 VM 侧进程、服务和实时增量验证。

## 1. 阻塞事实

本会话可用的指定入口存在，但当前执行沙箱禁止出站 TCP 连接，SSH 在认证前被本地策略拒绝。

已验证：

```text
which sshpass
/opt/homebrew/bin/sshpass

test -r "$HOME/.aiquant_sealed/sg_pass"
sg_pass readable
```

失败命令：

```bash
sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" \
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=12 \
  -o ServerAliveInterval=5 -o ServerAliveCountMax=1 \
  root@43.160.200.224 '...diagnostic commands...'
```

实际返回：

```text
ssh: connect to host 43.160.200.224 port 22: Operation not permitted
```

解释：失败发生在本机 `connect(43.160.200.224:22)` 阶段，未进入 SSH 握手，未触达服务器，未读取远端文件，未重启任何服务。按任务边界与历史 `FIX_COLLECTOR.md` 红线，本次没有改用浏览器、Computer Use、Chrome 或腾讯云 WebShell。

## 2. 必须查清项逐项状态

### 2.1 VM 上采集器进程/服务真实状态

**状态：未能核实。**

原因：SSH 出站被本地沙箱拒绝。不能用历史 `systemctl active` 或本地记录替代真实状态。

本次本应在 VM 执行：

```bash
systemctl is-active aiquant-liq-collector.service
systemctl show aiquant-liq-collector.service \
  -p ActiveState -p SubState -p MainPID -p NRestarts -p ActiveEnterTimestamp --no-pager
ps -fp "$(systemctl show -p MainPID --value aiquant-liq-collector.service)"
```

### 2.2 最近 24h 是否有非零 liquidation rows 落盘

**VM 状态：未能核实。**

原因：无法读取 VM `/opt/ai_quant_liq_collector/data/LIQUIDATIONS/`，因此不能给出 VM 最新数据文件名/大小/mtime/行数增量。

本地事实分两段：

1. 初始检查时，`find 06_RESEARCH/DATA/LIQUIDATIONS -maxdepth 2 -type f` 无输出，符合任务触发中“本地 0 文件”的症状。
2. 后续复查时，本地目录出现 7 个非零 JSONL 文件，最新文件为 `liq_20260621.jsonl`。

```text
wc -l 06_RESEARCH/DATA/LIQUIDATIONS/liq_*.jsonl
   37649 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260615.jsonl
   35722 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260616.jsonl
   39474 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260617.jsonl
   48013 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260618.jsonl
   33235 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260619.jsonl
   31585 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260620.jsonl
   19936 06_RESEARCH/DATA/LIQUIDATIONS/liq_20260621.jsonl
  245614 total
```

最新本地文件样本边界：

```text
liq_20260621.jsonl rows=19936
first_E=2026-06-21T00:00:03.130000+00:00
last_E=2026-06-21T16:47:09.297000+00:00
last_recv=2026-06-21T16:47:09.333000+00:00
last_symbol=UBUSDT
last_side=BUY
```

45 秒复查本地 `liq_20260621.jsonl` 行数未增长，仍为 19936；所以本地只证明已有一批截至 `2026-06-21T16:47:09Z` 的数据，不证明当前正在连续写入。

本次本应在 VM 执行两次、间隔 120 秒比较增量：

```bash
date -u +"UTC %Y-%m-%dT%H:%M:%SZ"
find /opt/ai_quant_liq_collector/data/LIQUIDATIONS \
  -maxdepth 1 -type f -name 'liq_*.jsonl' \
  -printf '%TY-%Tm-%TdT%TH:%TM:%TSZ %s %p\n' | sort | tail -10
wc -l /opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_*.jsonl 2>/dev/null || true
sleep 120
date -u +"UTC %Y-%m-%dT%H:%M:%SZ"
wc -l /opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_*.jsonl 2>/dev/null || true
```

### 2.3 若零帧/零行，定位根因

**VM 根因状态：未能定位。**

已知历史事实：

- `REPORT_FIX_COLLECTOR_URL.md` 记录 2026-06-15 已把 VM 采集器 `WS_URL` 从 `wss://fstream.binance.com/ws/!forceOrder@arr` 改为 `wss://fstream.binance.com/market/ws/!forceOrder@arr`。
- 同报告记录修复后 `liq_20260615.jsonl` 从 62 行增长到 92 行，`delta=30`，样本含 `e=forceOrder` 与 `o.S=SELL`。
- 当前本地规范脚本 `06_RESEARCH/CODE/liquidation_collector.py` 的 `WS_URL` 仍为 `wss://fstream.binance.com/market/ws/!forceOrder@arr`。

未验证项：

- VM 远端代码是否仍是新 URL。
- 服务是否在跑新代码。
- 是否再次出现握手 OPEN 后零帧。
- 是否进程崩溃、卡死、日志轮转、磁盘/权限异常、或网络/WS 路由再次迁移。

### 2.4 修复与修后真实帧验证

**状态：未修复。**

没有 VM 写权限通路，本次未改 WS URL、未重启服务、未补重连逻辑，也没有修后帧数/行数增量证据。

### 2.5 数据回流

**本地事实：** 本地 repo 当前已有 `liq_20260615.jsonl` 至 `liq_20260621.jsonl`，共 245614 行，最新本地接收时间 `2026-06-21T16:47:09.333Z`。  
**仓库事实：** 未发现可运行的固定回流脚本或定时 rsync/scp 配置；现有 runbook 主要描述 Mac 本地采集与 VM 采集器部署。PB1 记录曾说明本地 `LIQUIDATIONS` 无 JSONL。  
**日志事实：** 本地 `06_RESEARCH/CODE/collector.log` 最新 heartbeat 到 `2026-06-21T16:31:22Z` 仍为 `today_rows= 0`，并有多次 `ping/pong timed out`、`UNEXPECTED_EOF_WHILE_READING`、`Connection to remote host was lost`。因此这些新出现的本地 JSONL 不像是该 Mac 侧 collector.log 对应进程直接写入。
**VM 事实：** 未能确认 VM 是否有同源文件、是否正在收数、或是否通过某个外部/后台同步通道回流。

当前可判定：

1. “本地研究目录长期 0 文件”这个症状在本次执行过程中已经不再成立。
2. 本地已有可供研究读取的 JSONL 快照，覆盖 `2026-06-15T00:38:32Z` 至 `2026-06-21T16:47:09Z`。
3. 回流机制仍未审计清楚；需要 Claude/Codex 在可 SSH 环境下确认 VM 文件、同步来源、同步频率和断点。

## 3. 恢复所需前提

需要在允许本地命令出站连接 `43.160.200.224:22` 的 Codex/终端环境中恢复执行。继续使用指定 `sshpass` SSH 入口，不需要也不应切换到浏览器/WebShell。

## 4. 恢复执行命令清单

### 4.1 一次性远端取证

```bash
sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh \
  -o StrictHostKeyChecking=no -o ConnectTimeout=12 \
  root@43.160.200.224 '
set -e
date -u +"UTC %Y-%m-%dT%H:%M:%SZ"
hostname
systemctl is-active aiquant-liq-collector.service || true
systemctl show aiquant-liq-collector.service \
  -p ActiveState -p SubState -p MainPID -p NRestarts -p ActiveEnterTimestamp --no-pager || true
grep -n "^WS_URL" /opt/ai_quant_liq_collector/liquidation_collector.py || true
sha256sum /opt/ai_quant_liq_collector/liquidation_collector.py || true
find /opt/ai_quant_liq_collector/data/LIQUIDATIONS \
  -maxdepth 1 -type f -name "liq_*.jsonl" \
  -printf "%TY-%Tm-%TdT%TH:%TM:%TSZ %s %p\n" | sort | tail -10
wc -l /opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_*.jsonl 2>/dev/null || true
tail -120 /opt/ai_quant_liq_collector/logs/collector.log || true
'
```

### 4.2 真实数据增量验证

```bash
sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh \
  -o StrictHostKeyChecking=no root@43.160.200.224 '
set -e
P=/opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_$(date -u +%Y%m%d).jsonl
date -u +"before %Y-%m-%dT%H:%M:%SZ"
[ -f "$P" ] && wc -l "$P" || true
sleep 180
date -u +"after %Y-%m-%dT%H:%M:%SZ"
[ -f "$P" ] && wc -l "$P" || true
tail -20 /opt/ai_quant_liq_collector/logs/collector.log || true
'
```

### 4.3 若零帧，远端同库探针

```bash
sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" ssh \
  -o StrictHostKeyChecking=no root@43.160.200.224 '
python3 - <<'"'"'PY'"'"'
import json, time, websocket

urls = [
    "wss://fstream.binance.com/market/ws/!forceOrder@arr",
    "wss://fstream.binance.com/ws/!forceOrder@arr",
]
for url in urls:
    frames = 0
    first = None
    start = time.time()
    try:
        ws = websocket.create_connection(url, timeout=10)
        ws.settimeout(1)
        deadline = time.time() + 45
        while time.time() < deadline:
            try:
                msg = ws.recv()
            except Exception:
                continue
            frames += 1
            if first is None:
                first = json.loads(msg)
                break
        ws.close()
        print(json.dumps({
            "url": url,
            "handshake_ok": True,
            "frames": frames,
            "elapsed_s": round(time.time() - start, 3),
            "first_event": first.get("e") if isinstance(first, dict) else None,
            "first_symbol": first.get("o", {}).get("s") if isinstance(first, dict) else None,
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "url": url,
            "handshake_ok": False,
            "frames": frames,
            "error": type(e).__name__ + ": " + str(e),
        }, ensure_ascii=False))
PY
'
```

### 4.4 若 VM 有数据，回流到本地研究目录

只在确认 VM 文件非空后执行：

```bash
mkdir -p 06_RESEARCH/DATA/LIQUIDATIONS
sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" rsync -av \
  -e "ssh -o StrictHostKeyChecking=no" \
  root@43.160.200.224:/opt/ai_quant_liq_collector/data/LIQUIDATIONS/ \
  06_RESEARCH/DATA/LIQUIDATIONS/

find 06_RESEARCH/DATA/LIQUIDATIONS -maxdepth 1 -type f -name 'liq_*.jsonl' \
  -printf '%TY-%Tm-%TdT%TH:%TM:%TS %s %p\n' | sort | tail -10
wc -l 06_RESEARCH/DATA/LIQUIDATIONS/liq_*.jsonl
```

## 5. 自检

- [x] 没有用 `service active` 替代真实数据流结论。
- [x] 没有声明 VM 最近 24h 有/无 rows；仅报告本地 JSONL 快照事实。
- [x] 没有修改采集器、预登记、Holdout、交易/持仓状态。
- [x] 没有下单。
- [x] 写明中断状态、已完成步骤、剩余步骤、恢复前提。
- [x] 本报告不含 SSH 密码、API key 或代理凭据。
