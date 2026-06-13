# 强平采集器 VM 部署任务（Codex Computer Use via Termius）

**操作者：** Codex desktop（Computer Use）
**目标：** 腾讯云 SG 服务器，已在 Termius 中打开 SSH 会话
**前提：** Termius 已连接，终端可输入命令
**纪律：** 每步确认输出再进下一步；遇到报错先停下截图，不盲目继续

---

## Step 1：确认环境

在 Termius 终端中依次执行，确认每条输出正常再继续：

```bash
whoami
python3 --version
pip3 --version
curl -s https://fstream.binance.com/ping
```

期望：python3 ≥ 3.8，curl 返回 `{}` 表示服务器可直连 Binance（无需代理）。

---

## Step 2：创建目录结构

```bash
mkdir -p ~/ai_quant/06_RESEARCH/DATA/LIQUIDATIONS
mkdir -p ~/ai_quant/06_RESEARCH/CODE
mkdir -p ~/ai_quant/logs
```

---

## Step 3：安装依赖

```bash
pip3 install websocket-client --break-system-packages
python3 -c "import websocket; print('websocket-client OK:', websocket.__version__)"
```

---

## Step 4：写入采集器脚本

```bash
cat > ~/ai_quant/06_RESEARCH/CODE/liquidation_collector.py << 'PYEOF'
#!/usr/bin/env python3
"""强平数据前向采集器 - VM 直连版（无代理）
Binance USDT-M 全市场强平流 -> 每日 JSONL 落盘。
运行: nohup python3 liquidation_collector.py >> ~/ai_quant/logs/collector.log 2>&1 &
数据: ~/ai_quant/06_RESEARCH/DATA/LIQUIDATIONS/liq_YYYYMMDD.jsonl
"""
import json, time, os, datetime, threading
import websocket

WS_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
OUT_DIR = os.path.expanduser("~/ai_quant/06_RESEARCH/DATA/LIQUIDATIONS")
os.makedirs(OUT_DIR, exist_ok=True)

def _path_for_today():
    return os.path.join(OUT_DIR, "liq_%s.jsonl" % datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d"))

def on_message(ws, message):
    try:
        data = json.loads(message)
        data["recv_ts"] = int(time.time() * 1000)
        with open(_path_for_today(), "a") as f:
            f.write(json.dumps(data, separators=(",", ":")) + "\n")
    except Exception as e:
        print("write error:", e, flush=True)

def on_open(ws):
    print("[connected]", datetime.datetime.now(datetime.timezone.utc).isoformat(), flush=True)

def on_error(ws, err):
    print("ws error:", err, flush=True)

def on_close(ws, code, msg):
    print("ws closed:", code, msg, flush=True)

def heartbeat_log():
    while True:
        time.sleep(3600)
        p = _path_for_today()
        n = sum(1 for _ in open(p)) if os.path.exists(p) else 0
        print("[heartbeat]", datetime.datetime.now(datetime.timezone.utc).isoformat(), "today_rows=", n, flush=True)

if __name__ == "__main__":
    threading.Thread(target=heartbeat_log, daemon=True).start()
    print("starting liquidation collector (no proxy, direct connect)", flush=True)
    while True:
        try:
            ws = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message,
                                        on_error=on_error, on_close=on_close)
            ws.run_forever(ping_interval=180, ping_timeout=10)
        except Exception as e:
            print("reconnect after error:", e, flush=True)
        time.sleep(5)
PYEOF
echo "script written OK"
```

---

## Step 5：冒烟测试（60秒，确认真实数据帧）

**这是关键步骤——必须看到数据帧才算成功，只有 [connected] 不够。**

```bash
timeout 60 python3 ~/ai_quant/06_RESEARCH/CODE/liquidation_collector.py &
TEST_PID=$!
sleep 30
echo "=== LIQUIDATION DATA CHECK ==="
ls -la ~/ai_quant/06_RESEARCH/DATA/LIQUIDATIONS/
wc -l ~/ai_quant/06_RESEARCH/DATA/LIQUIDATIONS/liq_*.jsonl 2>/dev/null || echo "NO DATA FILE YET"
wait $TEST_PID
```

期望：30 秒内出现 `liq_YYYYMMDD.jsonl` 且行数 > 0（强平单低频，市场活跃时约每分钟几条）。
若 60 秒内行数为 0（但连接建立），正常——可能恰好无强平单，继续 Step 6。
若连接失败报错，截图后停下，等待人工判断。

---

## Step 6：配置 systemd 守护服务

```bash
# 获取 python3 完整路径
PYTHON_PATH=$(which python3)
echo "python3 path: $PYTHON_PATH"

# 获取当前用户
CURRENT_USER=$(whoami)
echo "user: $CURRENT_USER"

# 写 systemd unit
sudo tee /etc/systemd/system/liq-collector.service << EOF
[Unit]
Description=Binance Liquidation Collector
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=/root/ai_quant
ExecStart=${PYTHON_PATH} /root/ai_quant/06_RESEARCH/CODE/liquidation_collector.py
Restart=always
RestartSec=10
StandardOutput=append:/root/ai_quant/logs/collector.log
StandardError=append:/root/ai_quant/logs/collector.log

[Install]
WantedBy=multi-user.target
EOF

echo "systemd unit written"
```

> **注意**：如果 whoami 不是 root，把上面 `/root/ai_quant` 替换为 `/home/<用户名>/ai_quant`。

---

## Step 7：启动并验证

```bash
sudo systemctl daemon-reload
sudo systemctl enable liq-collector
sudo systemctl start liq-collector
sleep 3
sudo systemctl status liq-collector
```

期望：`Active: active (running)`。

```bash
# 查看实时日志
tail -20 ~/ai_quant/logs/collector.log
```

期望：看到 `[connected]` 行。

---

## Step 8：24 小时后检查（可选，今天不做）

```bash
wc -l ~/ai_quant/06_RESEARCH/DATA/LIQUIDATIONS/liq_*.jsonl
```

---

## 完成标志

- [ ] Step 1 curl 返回 `{}`（直连 Binance 成功）
- [ ] Step 3 websocket-client 安装成功
- [ ] Step 5 连接建立（有 [connected] 输出）
- [ ] Step 7 systemd 服务 `active (running)`
- [ ] 在 Termius 截图/记录最终 `systemctl status` 输出，发给 Claude 验收
