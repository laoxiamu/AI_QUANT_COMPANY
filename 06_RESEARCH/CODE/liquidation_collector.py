#!/usr/bin/env python3
"""强平数据前向采集器（DEC-066①优化点2）
Binance USDT-M 全市场强平流 -> 每日 JSONL 落盘。
历史强平数据不可得（P1-03 已确认），从今起自建。供 A-1 清算级联主线日后使用。

依赖: pip install websocket-client --break-system-packages
运行: nohup python3 liquidation_collector.py >> collector.log 2>&1 &
数据: 06_RESEARCH/DATA/LIQUIDATIONS/liq_YYYYMMDD.jsonl （每行一条强平单）
字段: 交易所推送原文（含 symbol/side/price/origQty/avgPrice/status/time）+ 本地接收时间 recv_ts
"""
import json, time, os, datetime, threading

import websocket  # websocket-client

WS_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DATA", "LIQUIDATIONS")
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

# 代理（大陆网络直连 Binance 被阻断；默认走本机系统代理，可用环境变量覆盖/置空禁用）
PROXY_HOST = os.environ.get("LIQ_PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.environ.get("LIQ_PROXY_PORT", "7897") or 0)

if __name__ == "__main__":
    threading.Thread(target=heartbeat_log, daemon=True).start()
    kw = dict(ping_interval=180, ping_timeout=10)
    if PROXY_HOST and PROXY_PORT:
        kw.update(http_proxy_host=PROXY_HOST, http_proxy_port=PROXY_PORT, proxy_type="socks5h")
        print("using proxy %s:%s" % (PROXY_HOST, PROXY_PORT), flush=True)
    while True:  # 断线重连
        try:
            ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_error=on_error, on_close=on_close)
            ws.run_forever(**kw)
        except Exception as e:
            print("reconnect after error:", e, flush=True)
        time.sleep(5)
