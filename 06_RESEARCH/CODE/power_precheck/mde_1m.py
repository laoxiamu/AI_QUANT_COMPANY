#!/usr/bin/env python3
"""阶段A 功效重算（1m 分辨率）—— 2026-07-31 取数后必办的第一件事。

4H 版结论（`20260731_forced_flow_stageA_power_precheck.md`）不自动外推：短周期 σ 更小但噪声结构不同。

⚠️ 反 A-1 纪律：本脚本**只算离散度(σ)与 MDE，绝不输出收益均值/方向**。
   单一方向命题必须在 B1 预登记冻结后才允许看方向。任何打印 mean(ret) 的改动都违反 §2.1。
"""
import gzip, glob, os, json, math, statistics, collections, datetime as dt

KL   = "/root/DATA/KLINES_1M"
LIQ  = "/opt/ai_quant_liq_collector/data/LIQUIDATIONS"
Z_A, Z_B = 1.96, 0.8416
COST_BP  = 220
HORIZONS = [5, 15, 30, 60, 240]          # 分钟
BUCKET   = 300                            # 5min 聚合桶
COOLDOWN = 3600                           # 事件间最小间隔(秒)，防重叠事件
THRESHOLDS = [1e5, 3e5, 1e6, 3e6]

# ---- 1) 读 1m 收盘 ----
close = {}   # sym -> {minute_epoch: close}
for p in sorted(glob.glob(os.path.join(KL, "*_1m.csv.gz"))):
    s = os.path.basename(p).replace("_1m.csv.gz", "")
    m = {}
    with gzip.open(p, "rt") as f:
        f.readline()
        for line in f:
            a = line.split(",")
            m[int(a[0]) // 1000] = float(a[4])
    close[s] = m
syms = set(close)
print(f"1m 面板 symbols={len(syms)}  bars={sum(len(v) for v in close.values()):,}")

# ---- 2) 聚合强平到 5min 桶 ----
buck = collections.Counter()
n_raw = 0
for fp in sorted(glob.glob(os.path.join(LIQ, "liq_2026*.jsonl"))):
    with open(fp, errors="ignore") as f:
        for line in f:
            try:
                o = json.loads(line)["o"]
                s = o["s"]
                if s not in syms: continue
                T = int(o["T"]) // 1000
                buck[(s, T // BUCKET)] += float(o["ap"]) * float(o["z"])
                n_raw += 1
            except Exception:
                continue
print(f"强平(仅面板symbol) 条数={n_raw:,}  非空5min桶={len(buck):,}")

def fwd_rets(sym, t0, h):
    """t0=桶结束秒；从 t0 后第 1 分钟收盘 → +h 分钟收盘。不返回方向统计，只供 σ。"""
    c = close[sym]
    a = (t0 // 60) * 60
    p0 = c.get(a); p1 = c.get(a + h * 60)
    if p0 and p1 and p0 > 0:
        return (p1 - p0) / p0
    return None

print()
print("阈值        | 事件N | " + " | ".join(f"σ{h}m(%)  MDE{h}m(bp)" for h in HORIZONS))
print("-" * 118)
results = {}
for thr in THRESHOLDS:
    ev = sorted([(s, b) for (s, b), v in buck.items() if v >= thr])
    # cooldown 去重
    last = {}
    kept = []
    for s, b in ev:
        t = b * BUCKET
        if s in last and t - last[s] < COOLDOWN: continue
        last[s] = t; kept.append((s, t + BUCKET))
    line = f"${thr:>10,.0f} | {len(kept):5d} |"
    row = {"N_raw": len(ev), "N": len(kept)}
    for h in HORIZONS:
        r = [x for x in (fwd_rets(s, t, h) for s, t in kept) if x is not None]
        if len(r) < 8:
            line += "      n/a          |"; continue
        sd = statistics.pstdev(r)
        mde = (Z_A + Z_B) * sd / math.sqrt(len(r))
        row[f"sd_{h}m"] = sd; row[f"mde_{h}m_bp"] = mde * 1e4; row[f"n_{h}m"] = len(r)
        line += f"  {sd*100:5.2f}   {mde*1e4:7.1f}   |"
    print(line)
    results[str(int(thr))] = row

print()
print(f"成本门(级联档往返, AGENTS 硬口径) = {COST_BP} bp")
print("判据(B0卡§3通过线2): MDE ≤ (毛效应上限 − 全成本)。MDE 越小 = 分辨力越强。")
print()
print("【关键对照】4H 版(旧仪器) MDE = 14–36 bp；本表为 1m 仪器在各持有期上的 MDE。")
print("注意：横向比较需同持有期——4H 版测的是 next-4H(=240m) 收益。")
json.dump(results, open("/root/DATA/KLINES_1M/mde_1m_results.json", "w"), indent=1)
print("\nsaved -> /root/DATA/KLINES_1M/mde_1m_results.json")
