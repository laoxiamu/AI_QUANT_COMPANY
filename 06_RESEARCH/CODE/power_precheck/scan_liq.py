import json, glob, os, collections, math
BASE="/sessions/loving-brave-gates/mnt/AI_QUANT_COMPANY/06_RESEARCH/DATA/LIQUIDATIONS"
files=sorted(glob.glob(os.path.join(BASE,"liq_2026*.jsonl")))
# per (symbol, 5min bucket) 与 (symbol, 4H bucket) 的强平 notional
b5=collections.Counter(); b4h=collections.Counter()
days=set(); n=0; bad=0
for fp in files:
    with open(fp,'r',errors='ignore') as f:
        for line in f:
            try:
                d=json.loads(line); o=d["o"]
                s=o["s"]; T=int(o["T"])//1000
                notional=float(o["ap"])*float(o["z"])
            except Exception:
                bad+=1; continue
            n+=1; days.add(T//86400)
            b5[(s, T//300)]+=notional
            b4h[(s, T//14400)]+=notional
print(f"raw_events={n} bad={bad} files={len(files)} distinct_days={len(days)}")
import pickle
pickle.dump({"b5":dict(b5),"b4h":dict(b4h),"days":sorted(days)}, open("/tmp/pw/liq_buckets.pkl","wb"))
# 分布
for name,b,span in (("5min",b5,300),("4H",b4h,14400)):
    v=sorted(b.values())
    N=len(v)
    def q(p): return v[min(N-1,int(N*p))]
    print(f"{name}: buckets={N}  p50=${q(.5):,.0f} p90=${q(.9):,.0f} p99=${q(.99):,.0f} p999=${q(.999):,.0f} max=${v[-1]:,.0f}")
