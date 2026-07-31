import pickle, collections, statistics, glob, os, csv, datetime as dt
D=pickle.load(open("/tmp/pw/liq_buckets.pkl","rb"))
b5=D["b5"]; b4h=D["b4h"]
P="/sessions/loving-brave-gates/mnt/AI_QUANT_COMPANY/06_RESEARCH/DATA/FUTURES_EXPANDED_2026"
syms={os.path.basename(f).replace("_4H.csv","") for f in glob.glob(os.path.join(P,"*_4H.csv"))}

# 对每个"大簇"4H桶，看其 notional 在内部48个5min桶里的时间集中度
big=[(s,b,v) for (s,b),v in b4h.items() if s in syms and v>=1e6]
conc=[]; span=[]
for s,b,v in big:
    parts=[]
    for k in range(48):
        idx=b*48+k                     # 4H = 48 个 5min
        nz=b5.get((s,idx),0.0)
        if nz>0: parts.append((k,nz))
    if not parts: continue
    parts.sort(key=lambda x:-x[1])
    top1=parts[0][1]/v
    conc.append(top1)
    # 覆盖 80% notional 所需的 5min 桶数
    acc=0; cnt=0
    for _,nz in parts:
        acc+=nz; cnt+=1
        if acc>=0.8*v: break
    span.append(cnt)

conc.sort(); span.sort()
n=len(conc)
def q(a,p): return a[min(len(a)-1,int(len(a)*p))]
print(f"大簇样本数 (4H notional >= $1M, panel symbols) = {n}")
print()
print("【簇内时间集中度】单个5分钟桶占该4H桶总强平额的比例：")
print(f"  中位数 {q(conc,.5)*100:.1f}%   p75 {q(conc,.75)*100:.1f}%   p90 {q(conc,.90)*100:.1f}%")
print()
print("【覆盖80%强平额所需的5分钟桶数】（共48个可用）：")
print(f"  中位数 {q(span,.5):.0f} 个  = {q(span,.5)*5:.0f} 分钟")
print(f"  p75    {q(span,.75):.0f} 个  = {q(span,.75)*5:.0f} 分钟")
print(f"  p90    {q(span,.90):.0f} 个  = {q(span,.90)*5:.0f} 分钟")
frac=sum(1 for x in span if x<=6)/len(span)
print(f"  ** {frac*100:.0f}% 的大簇在 <=30 分钟内完成 80% 的强平额 **")
