#!/usr/bin/env python3
"""B1-KILLCARD 执行脚本 —— forced-flow v2 强平簇方向漂移

预登记：06_RESEARCH/PREREGISTRATIONS/FORCED_FLOW_V2_B1_KILLCARD.md
冻结 SHA256: 10b359832c4b3aa1af02e465f22b9e5d70d7c4b9e4898f0542dde4a81278a216

判据全部来自预登记，本脚本不引入任何卡外条件。默认 KILL。
"""
import gzip, glob, os, json, math, statistics, collections, random, hashlib, datetime as dt

KL="/root/DATA/KLINES_1M"; LIQ="/opt/ai_quant_liq_collector/data/LIQUIDATIONS"
PREREG_SHA="10b359832c4b3aa1af02e465f22b9e5d70d7c4b9e4898f0542dde4a81278a216"
BUCKET=300; COOLDOWN=3600
HOR=[5,15,30,60]
TH=[1e5,3e5,1e6,3e6]
COST={"低":80,"中":120,"级联":220}
random.seed(20260731)

close={}
for p in sorted(glob.glob(os.path.join(KL,"*_1m.csv.gz"))):
    s=os.path.basename(p).replace("_1m.csv.gz","")
    m={}
    with gzip.open(p,"rt") as f:
        f.readline()
        for line in f:
            a=line.split(",")
            m[int(a[0])//1000]=float(a[4])
    close[s]=m
syms=set(close)

# 有符号强平：SELL=多头被平(价被下推) / BUY=空头被平(价被上推)
sgn=collections.Counter(); absn=collections.Counter()
for fp in sorted(glob.glob(os.path.join(LIQ,"liq_2026*.jsonl"))):
    with open(fp,errors="ignore") as f:
        for line in f:
            try:
                o=json.loads(line)["o"]; s=o["s"]
                if s not in syms: continue
                v=float(o["ap"])*float(o["z"]); T=int(o["T"])//1000
                k=(s,T//BUCKET)
                sgn[k]+= (+v if o["S"]=="BUY" else -v)   # BUY=空头被平=向上推
                absn[k]+=v
            except Exception: continue

def ret(sym,t0,h):
    c=close[sym]; a=(t0//60)*60
    p0=c.get(a); p1=c.get(a+h*60)
    return (p1-p0)/p0 if (p0 and p1 and p0>0) else None

def build(th):
    ev=sorted([(s,b) for (s,b),v in absn.items() if v>=th])
    last={}; kept=[]
    for s,b in ev:
        t=b*BUCKET
        if s in last and t-last[s]<COOLDOWN: continue
        last[s]=t
        net=sgn[(s,b)]
        if net==0: continue
        # H1: 与强制流反向。BUY簇(net>0,价被上推)->预测下行(signed=-1)
        kept.append((s,t+BUCKET, -1.0 if net>0 else +1.0))
    return kept

def ci95(xs):
    n=len(xs); m=statistics.fmean(xs); sd=statistics.pstdev(xs)
    se=sd/math.sqrt(n)
    return m, m-1.96*se, m+1.96*se

print("="*96)
print("B1-KILLCARD 执行 | 预登记 SHA256 =", PREREG_SHA)
print("H1(冻结): 强平簇后价格朝与强制流【相反】方向漂移 | 默认 KILL")
print("="*96)

res={}
print("\n【P4 符号一致 + P2 成本门】方向化漂移 (bp)，正=符合H1反转\n")
print(f"{'阈值':>10} {'N':>5} |" + "".join(f"{h:>7}m  {'95%CI':>16}" for h in HOR))
print("-"*96)
for th in TH:
    kept=build(th); row={"N":len(kept)}
    line=f"${th:>9,.0f} {len(kept):>5} |"
    for h in HOR:
        xs=[d*r for s,t,d in kept if (r:=ret(s,t,h)) is not None]
        if len(xs)<30: line+=f"{'n/a':>26}"; continue
        m,lo,hi=ci95(xs)
        row[f"h{h}"]={"n":len(xs),"bp":m*1e4,"lo":lo*1e4,"hi":hi*1e4}
        line+=f"{m*1e4:>8.1f}  [{lo*1e4:>6.1f},{hi*1e4:>6.1f}]"
    print(line); res[str(int(th))]=row

print("\n【对照：绝对漂移】(bp) — 检验是否只是波动 beta（OI重置同款死法）\n")
print(f"{'阈值':>10} |" + "".join(f"{h:>10}m" for h in HOR))
print("-"*60)
for th in TH:
    kept=build(th); line=f"${th:>9,.0f} |"
    for h in HOR:
        xs=[abs(r) for s,t,d in kept if (r:=ret(s,t,h)) is not None]
        line+=f"{statistics.fmean(xs)*1e4:>11.1f}" if len(xs)>=30 else f"{'n/a':>11}"
    print(line)

print("\n【P3 被动基准】同 symbol 同期随机时点（每事件 1 个配对），风险调整前\n")
print(f"{'阈值':>10} |" + "".join(f"{h:>8}m diff" for h in HOR))
print("-"*56)
for th in TH:
    kept=build(th); line=f"${th:>9,.0f} |"
    allt=sorted({t for s,t,d in kept})
    for h in HOR:
        ev_x=[d*r for s,t,d in kept if (r:=ret(s,t,h)) is not None]
        bs=[]
        for s,t,d in kept:
            for _ in range(3):
                rt=random.choice(list(close[s].keys()))
                rr=ret(s,rt,h)
                if rr is not None: bs.append(d*rr); break
        if len(ev_x)>=30 and len(bs)>=30:
            line+=f"{(statistics.fmean(ev_x)-statistics.fmean(bs))*1e4:>12.1f}"
        else: line+=f"{'n/a':>12}"
    print(line)

print("\n" + "="*96)
print("成本门参照: 低 80bp / 中 120bp / 级联 220bp (往返, AGENTS 0.1%/边)")
print("P2 判据: 任一持有期毛方向漂移 > 220bp")
print("="*96)
json.dump(res, open("/root/b1_results.json","w"), indent=1)
print("saved -> /root/b1_results.json")
