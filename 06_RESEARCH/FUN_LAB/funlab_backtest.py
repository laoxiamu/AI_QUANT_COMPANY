#!/usr/bin/env python3
"""FUN_LAB 娱乐性回测 —— 多周期形态策略

结构（Founder 指定）：4H 定方向 → 1H 定形态/位置 → 15m 定入场点
数据：37 symbols × 1m K线 × 2026-06-14→07-31

反前视铁律：
- 所有判断只用【已收盘】的K线
- 入场价 = 信号15m K线的收盘价（不是盘中价）
- 止损/止盈用其后的 1m 数据逐分钟检查
- 同一根1m内同时触及止损和止盈 → 按【不利读法】算止损
"""
import gzip, glob, os, json, math, statistics, collections

KL = "/root/DATA/KLINES_1M"
COST = 0.002          # 往返 0.2%（手续费+滑点）
FUNDING_PER_8H = 0.0001   # 资金费 0.01%/8h（按名义），保守取值
STOP_BUF = 0.003      # 止损缓冲 0.3%
RR = 2.0              # 止盈 = 止损距离 × 2

def load(sym):
    rows = []
    with gzip.open(os.path.join(KL, f"{sym}_1m.csv.gz"), "rt") as f:
        f.readline()
        for line in f:
            a = line.split(",")
            rows.append((int(a[0])//1000, float(a[1]), float(a[2]), float(a[3]), float(a[4]), float(a[5])))
    return rows  # t,o,h,l,c,v

def agg(m1, minutes):
    """把1m聚合成N分钟K线，返回 [(t_open, o,h,l,c,v, t_close)]"""
    out, bucket = [], {}
    step = minutes*60
    for t,o,h,l,c,v in m1:
        b = (t//step)*step
        if b not in bucket:
            bucket[b] = [o,h,l,c,v]
        else:
            x = bucket[b]
            x[1] = max(x[1],h); x[2] = min(x[2],l); x[3] = c; x[4] += v
    for b in sorted(bucket):
        o,h,l,c,v = bucket[b]
        out.append((b,o,h,l,c,v,b+step))
    return out

def ema(vals, n):
    k = 2/(n+1); out=[]; e=None
    for v in vals:
        e = v if e is None else v*k + e*(1-k)
        out.append(e)
    return out

def swings(bars, k=2):
    """摆动高/低点：比左右各k根都高/低。
    ⚠️ 返回的 idx 是【摆动点本身】的位置；使用时必须要求 idx <= 当前i - k，
    因为要等右边k根走完才能确认它是摆动点（否则=前视偏差）。"""
    res=[]
    for i in range(k, len(bars)-k):
        h = bars[i][2]; l = bars[i][3]
        if all(h > bars[j][2] for j in range(i-k,i)) and all(h > bars[j][2] for j in range(i+1,i+k+1)):
            res.append((i,h,'H'))
        if all(l < bars[j][3] for j in range(i-k,i)) and all(l < bars[j][3] for j in range(i+1,i+k+1)):
            res.append((i,l,'L'))
    return res

def simulate(m1, idx_map, entry_t, direction, entry, stop, target, timeout_min):
    """从 entry_t 之后逐1m检查。返回 (exit_price, exit_t, reason, real_entry)
    ⚠️ 实际入场价 = entry_t 那根1m的【开盘价】，不是信号K线收盘价（实盘拿不到收盘价）"""
    start = idx_map.get(entry_t)
    if start is None: return None
    entry = m1[start][1]   # 用下一根1m的开盘价作为真实入场价
    end = start + timeout_min
    for i in range(start+1, min(end, len(m1))):
        t,o,h,l,c,v = m1[i]
        if direction > 0:
            if l <= stop:  return (stop, t, "止损", entry, i-start)      # 不利读法优先
            if h >= target: return (target, t, "止盈", entry, i-start)
        else:
            if h >= stop:  return (stop, t, "止损", entry, i-start)
            if l <= target: return (target, t, "止盈", entry, i-start)
    j = min(end, len(m1))-1
    return (m1[j][4], m1[j][0], "超时", entry, j-start)

def net_pnl(direction, entry, exit_p, hold_min=0):
    gross = (exit_p-entry)/entry * direction
    funding = FUNDING_PER_8H * (hold_min/480.0)
    return gross - COST - funding

# ---------------- 策略 ----------------
def strat1_trend_pullback(sym, m1, b15, b1h, b4h, idx_map, vol_filter):
    """策略一·趋势延续（右侧）：4H定方向 → 1H回调不破前低+均线 → 15m入场"""
    sig=[]
    c4 = [b[4] for b in b4h]
    if len(c4) < 60: return sig
    e50_4 = ema(c4,50); e200_4 = ema(c4,min(200,len(c4)-1))
    c1 = [b[4] for b in b1h]; e50_1 = ema(c1,50)
    sw1 = swings(b1h,2)
    lows1 = [(i,p) for i,p,t in sw1 if t=='L']
    highs1= [(i,p) for i,p,t in sw1 if t=='H']
    v15 = [b[5] for b in b15]

    def bar4_at(ts):
        lo,hi=0,len(b4h)-1; r=None
        for i in range(len(b4h)):
            if b4h[i][6] <= ts: r=i
            else: break
        return r
    def bar1_at(ts):
        r=None
        for i in range(len(b1h)):
            if b1h[i][6] <= ts: r=i
            else: break
        return r

    for i in range(20, len(b15)):
        bar = b15[i]; ts = bar[0]
        i4 = bar4_at(ts); i1 = bar1_at(ts)
        if i4 is None or i1 is None or i4 < 60 or i1 < 60: continue
        # 4H 大周期方向
        if not (b4h[i4][4] > e50_4[i4] > e200_4[i4]): continue
        # 1H 形态：从近24h高点回落 2%-8%
        w = b1h[max(0,i1-24):i1+1]
        hi24 = max(x[2] for x in w)
        hi_pos = max(range(len(w)), key=lambda z: w[z][2])   # 24h高点位置
        after = w[hi_pos:]                                   # 高点【之后】才算回调
        if len(after) < 2: continue
        lo_recent = min(x[3] for x in after)                 # 修正：只看高点之后的低点
        pull = (hi24 - b1h[i1][4]) / hi24
        if not (0.02 <= pull <= 0.08): continue
        # 撑住：回调低点 > 上一个1H摆动低点 且 > 1H EMA50
        prev_lows = [p for j,p in lows1 if j <= i1-2-2]   # -2确认延迟(k=2)，再-2保守
        if not prev_lows: continue
        prev_low = prev_lows[-1]
        if not (lo_recent > prev_low and lo_recent > e50_1[i1]*0.995): continue
        # 15m 入场触发：阳线 且 收盘>前一根最高
        if not (bar[4] > bar[1] and bar[4] > b15[i-1][2]): continue
        if vol_filter:
            if bar[5] >= statistics.fmean(v15[max(0,i-20):i]): continue
        entry = bar[4]
        stop  = prev_low*(1-STOP_BUF)
        if entry <= stop: continue
        dist = entry-stop
        prev_highs=[p for j,p in highs1 if j <= i1-2-2]
        tgt2 = entry + dist*RR
        target = min(tgt2, prev_highs[-1]) if prev_highs and prev_highs[-1]>entry else tgt2
        sig.append((bar[6], +1, entry, stop, target, 24*60, "S1"))
    return sig

def strat2_2b(sym, m1, b15, b1h, b4h, idx_map, vol_filter, side=+1):
    """策略二·2B反转（左侧）：1H假跌破前低后收回 → 15m入场"""
    sig=[]
    sw1 = swings(b1h,3)
    pts = [(i,p) for i,p,t in sw1 if (t=='L' if side>0 else t=='H')]
    CONF = 3   # 摆动点确认延迟：右侧3根走完才算数
    v15=[b[5] for b in b15]
    def bar1_at(ts):
        r=None
        for i in range(len(b1h)):
            if b1h[i][6] <= ts: r=i
            else: break
        return r
    for k,(li,lp) in enumerate(pts):
        # 在其后 48h 内找假跌破
        for j in range(li+CONF+1, min(li+48, len(b1h))):   # 从确认后才开始找假跌破
            broke = b1h[j][3] < lp if side>0 else b1h[j][2] > lp
            if not broke: continue
            ext = min(b1h[x][3] for x in range(li+1,j+1)) if side>0 else max(b1h[x][2] for x in range(li+1,j+1))
            # 4小时内收回
            back=None
            for m in range(j+1, min(j+5, len(b1h))):
                if (b1h[m][4] > lp) if side>0 else (b1h[m][4] < lp):
                    back=m; break
            if back is None: break
            ts_ok = b1h[back][6]
            # 15m 入场确认
            for i in range(len(b15)):
                if b15[i][0] < ts_ok: continue
                bar=b15[i]
                ok = (bar[4]>bar[1] and bar[4]>b15[i-1][2]) if side>0 else (bar[4]<bar[1] and bar[4]<b15[i-1][3])
                if not ok:
                    if b15[i][0] > ts_ok + 4*3600: break
                    continue
                if vol_filter and bar[5] >= statistics.fmean(v15[max(0,i-20):i]): break
                entry=bar[4]
                stop = ext*(1-STOP_BUF) if side>0 else ext*(1+STOP_BUF)
                if (side>0 and entry<=stop) or (side<0 and entry>=stop): break
                dist=abs(entry-stop)
                target = entry + dist*RR*side
                sig.append((bar[6], side, entry, stop, target, 24*60, "S2"))
                break
            break
    return sig

def strat3_hammer(sym, m1, b15, b1h, b4h, idx_map, vol_filter):
    """策略三·长下影承接：1H长下影 + 已跌3% → 15m确认"""
    sig=[]
    v15=[b[5] for b in b15]
    for i in range(24, len(b1h)):
        o,h,l,c = b1h[i][1],b1h[i][2],b1h[i][3],b1h[i][4]
        body=abs(c-o); lower=min(o,c)-l; full=h-l
        if full<=0 or body<=0: continue
        if not (lower > body*2 and lower > full*0.5): continue
        hi24=max(x[2] for x in b1h[i-24:i])
        if (hi24-c)/hi24 < 0.03: continue
        ts_ok=b1h[i][6]
        for k in range(len(b15)):
            if b15[k][0] < ts_ok: continue
            bar=b15[k]
            if not (bar[4]>bar[1]):
                if b15[k][0] > ts_ok+2*3600: break
                continue
            if vol_filter and bar[5] >= statistics.fmean(v15[max(0,k-20):k]): break
            entry=bar[4]; stop=l*(1-STOP_BUF)
            if entry<=stop: break
            target=entry+(entry-stop)*RR
            sig.append((bar[6], +1, entry, stop, target, 12*60, "S3"))
            break
    return sig

# ---------------- 主流程 ----------------
def main():
    syms=[os.path.basename(p).replace("_1m.csv.gz","") for p in sorted(glob.glob(os.path.join(KL,"*_1m.csv.gz")))]
    results=collections.defaultdict(list)
    conflicts=0; conflict_detail=[]
    for sym in syms:
        m1=load(sym)
        idx_map={t:i for i,(t,*_ ) in enumerate(m1)}
        b15=agg(m1,15); b1h=agg(m1,60); b4h=agg(m1,240)
        for vf in (False,True):
            tag="缩量" if vf else "无过滤"
            s1=strat1_trend_pullback(sym,m1,b15,b1h,b4h,idx_map,vf)
            s2l=strat2_2b(sym,m1,b15,b1h,b4h,idx_map,vf,+1)
            s2s=strat2_2b(sym,m1,b15,b1h,b4h,idx_map,vf,-1)
            s3=strat3_hammer(sym,m1,b15,b1h,b4h,idx_map,vf)
            for name,sigs in (("S1趋势延续",s1),("S2b_2B做多",s2l),("S2s_2B做空",s2s),("S3长下影",s3)):
                for (et,d,entry,stop,target,tmo,_t) in sigs:
                    r=simulate(m1,idx_map,et,d,entry,stop,target,tmo)
                    if r is None: continue
                    xp,xt,reason,real_entry,hold=r
                    results[(name,tag)].append({
                        "sym":sym,"t":et,"dir":d,"entry":real_entry,"exit":xp,
                        "net":net_pnl(d,real_entry,xp,hold),"reason":reason})
            # 冲突检测：S1(做多) 与 S2s(做空) 在 2 小时内同币同时出现
            t1={x[0] for x in s1}; t2s={x[0] for x in s2s}
            for a in t1:
                if any(abs(a-b)<7200 for b in t2s):
                    conflicts+=1; conflict_detail.append((sym,a))
    json.dump({k[0]+"|"+k[1]:v for k,v in results.items()}, open("/root/funlab_raw_v2.json","w"))
    print("="*100)
    print("FUN_LAB 回测结果【v2 已修前视+入场价+资金费】 | 37 symbols | 2026-06-14→07-31 | 成本0.2%往返 | 止盈=2×止损")
    print("随机基准胜率 = 33.3%（止盈距离是止损2倍）| 覆盖成本需 40.0%")
    print("="*100)
    print(f"{'策略':<14}{'过滤':<8}{'笔数':>6}{'胜率':>8}{'vs随机':>9}{'平均净R':>10}{'总净R':>9}{'最大连亏':>9}")
    print("-"*100)
    for (name,tag),tr in sorted(results.items()):
        n=len(tr)
        if n==0:
            print(f"{name:<14}{tag:<8}{0:>6}{'—':>8}"); continue
        wins=sum(1 for x in tr if x["net"]>0)
        wr=wins/n
        avg=statistics.fmean(x["net"] for x in tr)
        tot=sum(x["net"] for x in tr)
        streak=mx=0
        for x in tr:
            if x["net"]<=0: streak+=1; mx=max(mx,streak)
            else: streak=0
        rc=collections.Counter(x["reason"] for x in tr)
        print(f"{name:<14}{tag:<8}{n:>6}{wr:>7.1%}{wr-1/3:>+9.1%}{avg*100:>9.2f}%{tot*100:>8.1f}%{mx:>9}"
              f"   止盈{rc['止盈']/n:>5.0%} 止损{rc['止损']/n:>5.0%} 超时{rc['超时']/n:>5.0%}")
    print()
    print("【关键对照】纯二元(止盈/止损)口径下的胜率——剔除超时单：")
    for (name,tag),tr in sorted(results.items()):
        b=[x for x in tr if x["reason"] in ("止盈","止损")]
        if len(b)<30: continue
        w=sum(1 for x in b if x["reason"]=="止盈")/len(b)
        print(f"  {name:<14}{tag:<8} n={len(b):>5}  二元胜率={w:>6.1%}  vs随机33.3% {w-1/3:>+6.1%}  {'✅过40%线' if w>0.40 else '❌'}")
    print()
    print(f"【信号冲突检测】S1做多 与 S2做空 在同币2小时内同时出现：{conflicts} 次")
    print("  → 若接近0，说明 Founder 判断正确：A/B 在不同市场状态触发，不冲突")
    json.dump({"conflicts":conflicts}, open("/root/funlab_conflicts.json","w"))

if __name__=="__main__":
    main()
