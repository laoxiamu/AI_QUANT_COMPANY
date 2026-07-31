#!/usr/bin/env python3
"""S1 结果审计 —— 三个决定性检验
1) 按币拆：是不是靠一两个币
2) 按天拆：是不是靠某几天
3) 买入持有基准：是不是在吃 beta
"""
import json, gzip, glob, os, statistics, collections, datetime as dt

raw = json.load(open("/root/funlab_raw.json"))
KL = "/root/DATA/KLINES_1M"

def fmt(ts): return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%m-%d")

print("="*96)
print("S1 趋势延续 · 三个决定性检验")
print("="*96)

for key in ("S1趋势延续|无过滤","S1趋势延续|缩量"):
    tr = raw.get(key, [])
    if not tr: continue
    n=len(tr); tot=sum(x["net"] for x in tr)
    print(f"\n### {key}  n={n}  总净R={tot*100:+.1f}%\n")

    # 1) 按币
    bysym=collections.defaultdict(list)
    for x in tr: bysym[x["sym"]].append(x["net"])
    rank=sorted(bysym.items(), key=lambda kv:-sum(kv[1]))
    print(f"  [按币] 共 {len(bysym)} 个币有信号")
    print(f"  {'币':<12}{'笔数':>5}{'净R合计':>10}{'占总收益':>10}")
    for s,v in rank[:6]:
        print(f"  {s:<12}{len(v):>5}{sum(v)*100:>9.1f}%{sum(v)/tot*100 if tot else 0:>9.0f}%")
    top1=sum(rank[0][1])/tot*100 if tot else 0
    top3=sum(sum(v) for _,v in rank[:3])/tot*100 if tot else 0
    print(f"  → 最赚的1个币贡献 {top1:.0f}% / 前3个币贡献 {top3:.0f}%")
    neg=sum(1 for _,v in bysym.items() if sum(v)<0)
    print(f"  → {len(bysym)-neg}/{len(bysym)} 个币为正")

    # 2) 按天
    byday=collections.defaultdict(list)
    for x in tr: byday[fmt(x["t"])].append(x["net"])
    dr=sorted(byday.items(), key=lambda kv:-sum(kv[1]))
    print(f"\n  [按天] 共 {len(byday)} 天有信号")
    for d,v in dr[:5]:
        print(f"  {d:<12}{len(v):>5}{sum(v)*100:>9.1f}%{sum(v)/tot*100 if tot else 0:>9.0f}%")
    top3d=sum(sum(v) for _,v in dr[:3])/tot*100 if tot else 0
    print(f"  → 最赚的3天贡献 {top3d:.0f}%")
    posd=sum(1 for _,v in byday.items() if sum(v)>0)
    print(f"  → {posd}/{len(byday)} 天为正")

# 3) 买入持有基准
print("\n" + "="*96)
print("### 基准对照：同期【买入持有】收益（是不是在吃 beta）")
print("="*96)
bh=[]
for p in sorted(glob.glob(os.path.join(KL,"*_1m.csv.gz"))):
    s=os.path.basename(p).replace("_1m.csv.gz","")
    first=last=None
    with gzip.open(p,"rt") as f:
        f.readline()
        for line in f:
            c=float(line.split(",")[4])
            if first is None: first=c
            last=c
    bh.append((s,(last-first)/first))
bh.sort(key=lambda x:-x[1])
allr=[r for _,r in bh]
print(f"  37个币买入持有: 中位 {statistics.median(allr)*100:+.1f}%  均值 {statistics.fmean(allr)*100:+.1f}%")
print(f"  上涨的币: {sum(1 for r in allr if r>0)}/37")
print(f"  最好: {bh[0][0]} {bh[0][1]*100:+.1f}%   最差: {bh[-1][0]} {bh[-1][1]*100:+.1f}%")

# S1 信号币 vs 全体
tr=raw.get("S1趋势延续|无过滤",[])
sigsyms={x["sym"] for x in tr}
sig_bh=[r for s,r in bh if s in sigsyms]
if sig_bh:
    print(f"\n  【关键】S1 有信号的 {len(sig_bh)} 个币，其买入持有中位收益 = {statistics.median(sig_bh)*100:+.1f}%")
    print(f"          全部37币中位 = {statistics.median(allr)*100:+.1f}%")
    print(f"  → 若S1只在已经大涨的币上触发，说明它筛的是【涨得好的币】而非【形态】")
