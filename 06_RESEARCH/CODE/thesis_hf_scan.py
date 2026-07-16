#!/usr/bin/env python3
"""高频thesis候选扫描器（投研线1个月冲刺工具，2026-07-12建）。
只读扫描：funding极端 / OI骤变 / 价格异动 复合事件 → 候选清单JSON。
不登记、不判定——登记与闸0/闸1裁决仍由Claude人工完成（THESIS_TEMPLATE纪律）。
通道A执行：Mac直连fapi.binance.com，代理unset（RUNBOOK 2026-06-22铁律）。
"""
import json, ssl, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://fapi.binance.com"
OUT = Path(__file__).resolve().parent / "output"
CTX = ssl.create_default_context()

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "aiquant-scan/1.0"})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        return json.loads(r.read().decode())

def main():
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    prem = get(f"{BASE}/fapi/v1/premiumIndex")
    tick = {t["symbol"]: t for t in get(f"{BASE}/fapi/v1/ticker/24hr")}
    rows = []
    for p in prem:
        s = p.get("symbol", "")
        if not s.endswith("USDT"):
            continue
        try:
            fr = float(p.get("lastFundingRate") or 0)
            t = tick.get(s, {})
            chg = float(t.get("priceChangePercent") or 0)
            qv = float(t.get("quoteVolume") or 0)
        except (TypeError, ValueError):
            continue
        # 初筛：funding极端（|8h费率|>=0.3%）或 价格异动（|24h|>=25%且量>=500万USDT）
        if abs(fr) >= 0.003 or (abs(chg) >= 25 and qv >= 5e6):
            rows.append({"symbol": s, "funding_8h": fr, "chg24h_pct": chg, "quote_vol_usdt": qv})
    rows.sort(key=lambda r: abs(r["funding_8h"]), reverse=True)
    # 对前8个候选补OI 24h变化（骤增/骤降是机制核心变量）
    for r in rows[:8]:
        try:
            oi = get(f"{BASE}/futures/data/openInterestHist?symbol={r['symbol']}&period=1h&limit=25")
            if len(oi) >= 2:
                a, b = float(oi[0]["sumOpenInterestValue"]), float(oi[-1]["sumOpenInterestValue"])
                r["oi_24h_ago_usdt"], r["oi_now_usdt"] = a, b
                r["oi_24h_ratio"] = round(b / a, 3) if a > 0 else None
            time.sleep(0.3)
        except Exception as e:  # noqa: BLE001 —— 单symbol失败不废全扫描
            r["oi_error"] = str(e)[:80]
    out = {"scan_utc": now, "n_prescreen": len(rows), "candidates": rows[:20]}
    OUT.mkdir(exist_ok=True)
    f = OUT / f"thesis_hf_scan_{now}.json"
    f.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("WROTE", f)
    for r in rows[:8]:
        print(r["symbol"], "fund=%.4f%%" % (r["funding_8h"] * 100), "chg=%.1f%%" % r["chg24h_pct"],
              "vol=%.1fM" % (r["quote_vol_usdt"] / 1e6), "oiX=", r.get("oi_24h_ratio"))

if __name__ == "__main__":
    main()
