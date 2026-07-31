#!/usr/bin/env python3
"""S1 稳健性：剔除最强币/最强天后还剩什么（#X3 同款死法检验）"""
import json, statistics, collections, datetime as dt, math
raw=json.load(open("/root/funlab_raw.json"))
def day(ts): return dt.datetime.fromtimestamp(ts,dt.timezone.utc).strftime("%m-%d")

for key in ("S1趋势延续|无过滤","S1趋势延续|缩量"):
    tr=raw.get(key,[])
    if not tr: continue
    n=len(tr); tot=sum(x["net"] for x in tr)
    print("="*88); print(f"### {key}   n={n}  原始总净={tot*100:+.1f}%  平均={tot/n*100:+.3f}%"); print("="*88)

    bysym=collections.defaultdict(list)
    for x in tr: bysym[x["sym"]].append(x)
    rank=sorted(bysym.items(), key=lambda kv:-sum(y["net"] for y in kv[1]))

    print(f"\n{'剔除':<28}{'剩余笔数':>8}{'总净':>10}{'平均/笔':>11}{'胜率':>8}")
    print("-"*70)
    print(f"{'（原始，不剔除）':<28}{n:>8}{tot*100:>9.1f}%{tot/n*100:>10.3f}%{sum(1 for x in tr if x['net']>0)/n:>7.1%}")
    cum=list(tr)
    for k in (1,2,3):
        drop={s for s,_ in rank[:k]}
        rest=[x for x in tr if x["sym"] not in drop]
        if not rest: continue
        t2=sum(x["net"] for x in rest)
        print(f"{'最强'+str(k)+'个币 ('+','.join(sorted(drop))[:18]+')':<28}{len(rest):>8}{t2*100:>9.1f}%{t2/len(rest)*100:>10.3f}%{sum(1 for x in rest if x['net']>0)/len(rest):>7.1%}")

    byday=collections.defaultdict(list)
    for x in tr: byday[day(x["t"])].append(x)
    drank=sorted(byday.items(), key=lambda kv:-sum(y["net"] for y in kv[1]))
    for k in (1,3,5):
        drop={d for d,_ in drank[:k]}
        rest=[x for x in tr if day(x["t"]) not in drop]
        if not rest: continue
        t2=sum(x["net"] for x in rest)
        print(f"{'最强'+str(k)+'天':<28}{len(rest):>8}{t2*100:>9.1f}%{t2/len(rest)*100:>10.3f}%{sum(1 for x in rest if x['net']>0)/len(rest):>7.1%}")

    # 同时剔最强1币+最强1天
    drop_s={rank[0][0]}; drop_d={drank[0][0]}
    rest=[x for x in tr if x["sym"] not in drop_s and day(x["t"]) not in drop_d]
    if rest:
        t2=sum(x["net"] for x in rest)
        print(f"{'最强1币 + 最强1天':<28}{len(rest):>8}{t2*100:>9.1f}%{t2/len(rest)*100:>10.3f}%{sum(1 for x in rest if x['net']>0)/len(rest):>7.1%}")

    # 统计显著性：平均净是否显著>0
    xs=[x["net"] for x in tr]
    m=statistics.fmean(xs); sd=statistics.pstdev(xs); se=sd/math.sqrt(len(xs))
    print(f"\n  平均净 {m*100:+.3f}%  95%CI [{(m-1.96*se)*100:+.3f}%, {(m+1.96*se)*100:+.3f}%]  {'显著>0 ✅' if m-1.96*se>0 else '❌ CI跨0/不显著'}")
    # 剔除最强币后
    rest=[x["net"] for x in tr if x["sym"]!=rank[0][0]]
    if rest:
        m2=statistics.fmean(rest); sd2=statistics.pstdev(rest); se2=sd2/math.sqrt(len(rest))
        print(f"  剔最强币后 {m2*100:+.3f}%  95%CI [{(m2-1.96*se2)*100:+.3f}%, {(m2+1.96*se2)*100:+.3f}%]  {'显著>0 ✅' if m2-1.96*se2>0 else '❌ CI跨0/不显著'}")
    print()
