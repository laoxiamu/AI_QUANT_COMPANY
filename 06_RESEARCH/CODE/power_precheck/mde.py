import pickle, glob, os, csv, math, statistics, datetime as dt, collections
P="/sessions/loving-brave-gates/mnt/AI_QUANT_COMPANY/06_RESEARCH/DATA/FUTURES_EXPANDED_2026"
D=pickle.load(open("/tmp/pw/liq_buckets.pkl","rb"))
b4h=D["b4h"]

# --- 价格面板：读 4H 收盘，算 next-bar 收益 ---
panel={}   # sym -> {bucket_idx: (close, next_ret)}
syms=[]
for fp in sorted(glob.glob(os.path.join(P,"*_4H.csv"))):
    s=os.path.basename(fp).replace("_4H.csv","")
    rows=[]
    with open(fp) as f:
        r=csv.reader(f); next(r)
        for row in r:
            t=dt.datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
            rows.append((int(t.timestamp())//14400, float(row[4])))
    m={}
    for i in range(len(rows)-1):
        b,c=rows[i]; _,c2=rows[i+1]
        if c>0: m[b]=(c,(c2-c)/c)
    panel[s]=m; syms.append(s)

# --- 重叠窗：强平数据 ∩ 面板 ---
liq_b=[b for (s,b) in b4h.keys()]
lo_l,hi_l=min(liq_b),max(liq_b)
pan_b=[b for s in syms for b in panel[s]]
lo_p,hi_p=min(pan_b),max(pan_b)
lo,hi=max(lo_l,lo_p),min(hi_l,hi_p)
def d(b): return dt.datetime.fromtimestamp(b*14400,dt.timezone.utc).strftime("%Y-%m-%d")
overlap_days=(hi-lo+1)*4/24
print(f"强平覆盖 {d(lo_l)}→{d(hi_l)} | 面板覆盖 {d(lo_p)}→{d(hi_p)}")
print(f"** 重叠窗 {d(lo)}→{d(hi)} = {overlap_days:.1f} 天 ({hi-lo+1} 个4H bar) **")
print(f"面板 symbol 数 = {len(syms)}")

# --- 事件构造：panel symbol 的 4H 强平 notional，按阈值取簇 ---
ev=[]   # (sym, bucket, notional, next_ret)
for s in syms:
    for b in panel[s]:
        if lo<=b<=hi:
            nz=b4h.get((s,b),0.0)
            if nz>0: ev.append((s,b,nz,panel[s][b][1]))
print(f"重叠窗内 有强平的 (symbol,4H) 单元 = {len(ev)}")

rets_all=[e[3] for e in ev]
sd_all=statistics.pstdev(rets_all)
print(f"全体 next-4H 收益 σ = {sd_all*100:.2f}%  (n={len(rets_all)})")

# --- MDE 表 ---
Z_A, Z_B = 1.96, 0.8416      # 双侧 α=.05, power=80%
COST_BP  = 220               # AGENTS 硬口径 级联档 往返全成本
print()
print("阈值(4H强平notional) | 事件数N | 窗内N/天 | σ(%)  | MDE(bp) | 可检出的最小毛效应=220+MDE (bp)")
print("-"*104)
rows=[]
for thr in (1e5, 3e5, 1e6, 3e6, 1e7):
    sub=[e for e in ev if e[2]>=thr]
    N=len(sub)
    if N<8: 
        print(f"${thr:>12,.0f} | {N:7d} | 样本过少"); continue
    sd=statistics.pstdev([e[3] for e in sub])
    mde=(Z_A+Z_B)*sd/math.sqrt(N)
    rows.append((thr,N,sd,mde))
    print(f"${thr:>12,.0f} | {N:7d} | {N/overlap_days:8.1f} | {sd*100:5.2f} | {mde*1e4:7.0f} | {COST_BP+mde*1e4:>10.0f}")

# --- 反推：要把 MDE 压到目标以下需要多少天 ---
print()
print("反推所需重叠天数（按当前事件密度线性外推，σ 不变）：")
print("阈值 | 目标MDE=100bp需N | 需天数 | 目标MDE=50bp需N | 需天数")
print("-"*88)
for thr,N,sd,mde in rows:
    per_day=N/overlap_days
    out=[]
    for tgt in (0.01,0.005):
        need_N=((Z_A+Z_B)*sd/tgt)**2
        out.append((need_N, need_N/per_day))
    print(f"${thr:>12,.0f} | {out[0][0]:14.0f} | {out[0][1]:6.0f} | {out[1][0]:14.0f} | {out[1][1]:6.0f}")
