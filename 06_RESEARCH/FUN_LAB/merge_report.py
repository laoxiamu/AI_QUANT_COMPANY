#!/usr/bin/env python3
"""合并分片 + 出最终报告（v2 修复版 · 一年数据）"""
import json, glob, os, math, statistics, collections, datetime as dt
merged=collections.defaultdict(list); conf=0
for f in sorted(glob.glob("/root/fl_shards/*.json")):
    if f.endswith(".conf"): continue
    for k,v in json.load(open(f)).items(): merged[k].extend(v)
for f in glob.glob("/root/fl_shards/*.conf"):
    conf+=json.load(open(f)).get("conflicts",0)
json.dump(merged, open("/root/funlab_raw_1y.json","w"))

def day(ts): return dt.datetime.fromtimestamp(ts,dt.timezone.utc).strftime("%Y-%m-%d")
Z1, ZB = 1.96, 2.734   # 原始 / Bonferroni(8组)

print("="*112)
print("FUN_LAB v2【已修前视+入场价+资金费】| 一年数据 2025-08-01→2026-07-31 | 37币 | 成本0.2%+资金费")
print("随机基准胜率 33.3%（止盈=2×止损）| 覆盖成本需 40.0%")
print("="*112)
print(f"{'策略':<14}{'过滤':<8}{'笔数':>7}{'胜率':>8}{'平均净':>9}{'总净':>10}{'原始95%CI':>20}{'Bonf校正':>20}")
print("-"*112)
rows={}
for k in sorted(merged):
    tr=merged[k]; n=len(tr)
    if n<30: continue
    name,tag=k.split("|")
    xs=[x["net"] for x in tr]
    m=statistics.fmean(xs); sd=statistics.pstdev(xs); se=sd/math.sqrt(n)
    wr=sum(1 for x in xs if x>0)/n
    lo1,hi1=m-Z1*se,m+Z1*se; lo2,hi2=m-ZB*se,m+ZB*se
    f1="✅" if lo1>0 else "❌"; f2="✅" if lo2>0 else "❌"
    print(f"{name:<14}{tag:<8}{n:>7}{wr:>7.1%}{m*100:>8.3f}%{sum(xs)*100:>9.1f}%"
          f"  [{lo1*100:>+6.3f},{hi1*100:>+6.3f}]{f1} [{lo2*100:>+6.3f},{hi2*100:>+6.3f}]{f2}")
    rows[k]=(tr,m,se,n)

print(f"\n【信号冲突】S1做多 与 S2做空 同币2h内同现：{conf} 次")

# 稳健性：只对有正均值的做
print("\n"+"="*112); print("稳健性检验（仅对平均净>0 的组合）"); print("="*112)
any_pos=False
for k,(tr,m,se,n) in rows.items():
    if m<=0: continue
    any_pos=True
    print(f"\n### {k}  n={n}  平均={m*100:+.3f}%")
    bysym=collections.defaultdict(list)
    for x in tr: bysym[x["sym"]].append(x["net"])
    rank=sorted(bysym.items(), key=lambda kv:-sum(kv[1]))
    tot=sum(x["net"] for x in tr)
    print(f"  币数={len(bysym)}  最强1币贡献={sum(rank[0][1])/tot*100 if tot else 0:.0f}%  正收益币={sum(1 for _,v in bysym.items() if sum(v)>0)}/{len(bysym)}")
    for kk in (1,2,3):
        drop={s for s,_ in rank[:kk]}
        rest=[x["net"] for x in tr if x["sym"] not in drop]
        if rest:
            mm=statistics.fmean(rest)
            print(f"   剔最强{kk}币 → n={len(rest):>5} 平均={mm*100:>+7.3f}%")
    byday=collections.defaultdict(list)
    for x in tr: byday[day(x["t"])].append(x["net"])
    drank=sorted(byday.items(), key=lambda kv:-sum(kv[1]))
    for kk in (5,10,20):
        drop={d for d,_ in drank[:kk]}
        rest=[x["net"] for x in tr if day(x["t"]) not in drop]
        if rest:
            mm=statistics.fmean(rest)
            print(f"   剔最强{kk}天 → n={len(rest):>5} 平均={mm*100:>+7.3f}%")
    # 分年度/半年
    byh=collections.defaultdict(list)
    for x in tr:
        d=day(x["t"]); byh[d[:7]].append(x["net"])
    print("   按月：", " ".join(f"{mo}:{statistics.fmean(v)*100:+.2f}%(n{len(v)})" for mo,v in sorted(byh.items())))
if not any_pos:
    print("\n  没有任何组合平均净 > 0 —— 无需稳健性检验。")
