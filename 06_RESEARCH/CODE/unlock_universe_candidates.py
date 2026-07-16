#!/usr/bin/env python3
"""备用 universe：币安 USDⓈ-M 永续中 2023+ 上市的较新币(高解锁候选)。
用免费 exchangeInfo(onboardDate)；不依赖付费 emissions API。
输出: 06_RESEARCH/CODE/output/unlock_universe_candidates.json
口径: 这些币天然有币安4H数据(可fetch面板)；解锁规模过滤留到扩展步用免费/抽样源做。
不碰Holdout/不回测/不调参——纯数据清单。
"""
import json, os, urllib.request, datetime as dt

ROOT = "/Users/yaomingyu/Documents/AI_QUANT_COMPANY"
OUT = os.path.join(ROOT, "06_RESEARCH/CODE/output/unlock_universe_candidates.json")
EXISTING = {  # 现有刷新面板 31 symbol(老币),用于标"新增"
 "AAVE","ATOM","AVAX","AXS","COMP","CRV","DASH","DOT","EGLD","ENJ","ETH","FTM","ICX",
 "KNC","KSM","LINK","LRC","NEAR","REN","RUNE","SNX","SUSHI","THETA","TRX","UNI","XLM",
 "XMR","XTZ","YFI","ZEC","ZRX"}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent":"AI-Quant/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

info = get("https://fapi.binance.com/fapi/v1/exchangeInfo")
rows = []
for s in info.get("symbols", []):
    if s.get("contractType")!="PERPETUAL" or s.get("quoteAsset")!="USDT" or s.get("status")!="TRADING":
        continue
    base = s.get("baseAsset")
    ob = s.get("onboardDate")
    if not ob:
        continue
    d = dt.datetime.utcfromtimestamp(ob/1000).date()
    rows.append({"symbol": s["symbol"], "base": base,
                 "onboard": d.isoformat(),
                 "in_current_panel": base in EXISTING})

rows.sort(key=lambda x: x["onboard"], reverse=True)
new_2023plus = [r for r in rows if r["onboard"] >= "2023-01-01" and not r["in_current_panel"]]
out = {
 "generated": dt.datetime.utcnow().isoformat()+"Z",
 "total_usdt_perp_trading": len(rows),
 "candidate_count_2023plus_not_in_panel": len(new_2023plus),
 "candidates_2023plus": new_2023plus,
 "note": "解锁规模过滤待扩展步用免费/抽样源(Tokenomist免费页/文章样本)叠加;本表只保证币安4H可取",
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT,"w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("total trading USDT perp:", len(rows))
print("2023+ not-in-panel candidates:", len(new_2023plus))
print("top 25 newest:")
for r in new_2023plus[:25]:
    print(" ", r["onboard"], r["base"])
print("written:", OUT)
