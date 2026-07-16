#!/usr/bin/env python3
"""THESIS_003/004 结算取数（只读，通道B执行）。窗口与判据见两份thesis文件字段11，此处只取数不判定。"""
import json, urllib.request

B = "https://fapi.binance.com"

def g(u):
    return json.loads(urllib.request.urlopen(u, timeout=20).read())

CASES = [
    # (symbol, win_start_ms, win_end_ms) — UTC
    ("TUSDT", 1783831740000, 1784004540000),    # 07-12 04:49 -> 07-14 04:49
    ("SXTUSDT", 1783839600000, 1784012400000),  # 07-12 07:00 -> 07-14 07:00
]

for sym, t0, t1 in CASES:
    print(f"===== {sym} window {t0}->{t1}")
    kl = g(f"{B}/fapi/v1/markPriceKlines?symbol={sym}&interval=1h&startTime={t0}&endTime={t1}&limit=60")
    highs = [float(k[2]) for k in kl]; lows = [float(k[3]) for k in kl]
    print("KLINES n=", len(kl), "maxHigh=", max(highs), "minLow=", min(lows),
          "lastClose=", float(kl[-1][4]), "lastOpenTime=", kl[-1][0])
    # 触及时间（诊断）
    hi_i = highs.index(max(highs)); lo_i = lows.index(min(lows))
    print("maxHigh@", kl[hi_i][0], " minLow@", kl[lo_i][0])
    fr = g(f"{B}/fapi/v1/fundingRate?symbol={sym}&startTime={t0}&endTime={t1}&limit=20")
    print("FUNDING n=", len(fr))
    for f in fr[:8]:
        print("  fundingTime=", f["fundingTime"], "rate=", f["fundingRate"])
    oi = g(f"{B}/futures/data/openInterestHist?symbol={sym}&period=1h&startTime={t0}&endTime={t0+86400000}&limit=30")
    vals = [float(x["sumOpenInterestValue"]) for x in oi]
    print("OI_24H n=", len(oi), "min=", min(vals) if vals else None, "max=", max(vals) if vals else None,
          "first=", vals[0] if vals else None, "last=", vals[-1] if vals else None)
    oi2 = g(f"{B}/futures/data/openInterestHist?symbol={sym}&period=1h&startTime={t1-7200000}&endTime={t1}&limit=5")
    if oi2:
        print("OI_at_window_end≈", float(oi2[-1]["sumOpenInterestValue"]))
print("DONE")
