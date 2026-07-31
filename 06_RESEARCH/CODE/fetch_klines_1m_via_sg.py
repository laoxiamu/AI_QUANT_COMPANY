#!/usr/bin/env python3
"""拉 Binance USDⓈ-M 永续 1m K线（阶段A 分辨率修复，2026-07-31 DEC-097 议程）。

背景：`20260731_forced_flow_stageA_power_precheck.md` 实测——强平簇机制寿命中位 25min，
而全库最细价格粒度只有 4H（=机制寿命的 8-10 倍），用 4H 测该机制必然稀释至 ≈0。
故阶段A 的绑定约束是**分辨率**不是样本量；本脚本换仪器。

⚠️ 反 p-hacking 纪律：symbol universe **固定为既有 37 个面板 symbol**（在看到任何结果之前就已确定），
   不因本次取数而扩表——事后扩 universe 是选择性偏差入口。扩表须另立决定并说明理由。

在 SG 上跑（Mac 直连 Binance = HTTP 451）。
"""
import json, os, sys, time, urllib.request, urllib.error, gzip, glob

BASE = "https://fapi.binance.com/fapi/v1/klines"
OUT  = os.environ.get("KL_OUT", "/root/DATA/KLINES_1M")
START_MS = int(os.environ.get("KL_START", "1781395200000"))   # 2026-06-14 00:00 UTC（强平自采起始 06-15 前留 1 天缓冲）
END_MS   = int(os.environ.get("KL_END",   str(int(time.time()) * 1000)))
INTERVAL = os.environ.get("KL_INTERVAL", "1m")
LIMIT    = 1500
SLEEP    = float(os.environ.get("KL_SLEEP", "0.25"))

def get(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(2 ** i); continue
            raise
        except Exception:
            if i == tries - 1: raise
            time.sleep(2 ** i)
    raise RuntimeError("unreachable")

def fetch_symbol(sym):
    path = os.path.join(OUT, f"{sym}_1m.csv.gz")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return sym, "skip(exists)", 0
    rows, t, calls = [], START_MS, 0
    while t < END_MS:
        url = f"{BASE}?symbol={sym}&interval={INTERVAL}&startTime={t}&limit={LIMIT}"
        batch = get(url); calls += 1
        if not batch: break
        for k in batch:
            # openTime, o,h,l,c, volume, closeTime, quoteVol, trades, takerBuyBase, takerBuyQuote
            rows.append((int(k[0]), k[1], k[2], k[3], k[4], k[5], k[7], k[8], k[9], k[10]))
        nt = int(batch[-1][0]) + 60_000
        if nt <= t: break
        t = nt
        time.sleep(SLEEP)
    if not rows: return sym, "EMPTY", calls
    rows.sort()
    # 去重（按 openTime）
    ded, seen = [], set()
    for r in rows:
        if r[0] in seen: continue
        seen.add(r[0]); ded.append(r)
    os.makedirs(OUT, exist_ok=True)
    with gzip.open(path, "wt") as f:
        f.write("open_time,open,high,low,close,volume,quote_volume,trades,taker_buy_base,taker_buy_quote\n")
        for r in ded:
            f.write(",".join(str(x) for x in r) + "\n")
    return sym, f"ok bars={len(ded)}", calls

def main():
    syms = sys.argv[1:]
    if not syms:
        print("usage: fetch_klines_1m_via_sg.py SYM1 SYM2 ..."); return 2
    os.makedirs(OUT, exist_ok=True)
    tot_calls = 0
    for i, s in enumerate(syms, 1):
        try:
            sym, status, calls = fetch_symbol(s)
        except Exception as e:
            sym, status, calls = s, f"FAIL {type(e).__name__}: {e}", 0
        tot_calls += calls
        print(f"[{i}/{len(syms)}] {sym}: {status} (calls={calls})", flush=True)
    print(f"DONE symbols={len(syms)} total_api_calls={tot_calls}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
