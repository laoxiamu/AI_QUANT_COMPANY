CAPS=[30000,100000,300000]
# 情景：现金成本/年
SCEN={"实测run-rate(1233/2月)":1233/2*12, "保守(1233/2.5月)":1233/2.5*12,
      "预算上限(月1000)":12000.0}
HOURS=365.0
print("=== 修正：现金成本口径实测 ===")
print("Founder 报累计实际支出 = 1,233 元；成本台账建立 2026-06-07，记'项目首月 6/1 启动'")
for k,v in SCEN.items():
    print(f"  {k:24s} -> {v:8,.0f} 元/年")
print()
print("=== 表1修正：30k 本金档 打平现金成本所需净年化 ===")
print(f"{'现金成本/年':>22} |" + "".join(f"{c:>12,}" for c in CAPS))
print("-"*66)
for k,v in SCEN.items():
    print(f"{k:>22} |" + "".join(f"{v/c*100:>11.1f}%" for c in CAPS))
print()
print("=== 表2修正：30k 档 @各净年化 的年净值(元, 未计时间成本) ===")
print(f"{'现金成本/年':>22} |" + "".join(f"{int(r*100):>9}%" for r in (0.10,0.15,0.20,0.25)))
print("-"*62)
for k,v in SCEN.items():
    print(f"{k:>22} |" + "".join(f"{30000*r-v:>10,.0f}" for r in (0.10,0.15,0.20,0.25)))
print()
print("=== 成本盒(5000元硬止损)还能跑多久 ===")
used=1233; left=5000-used
for k,v in SCEN.items():
    mo=v/12
    print(f"  {k:24s} 月均{mo:6,.0f}元 -> 剩余 {left:,.0f} 元可再跑 {left/mo:4.1f} 个月")
print(f"  时间盒 2026-06-07 起 6 个月 = 2026-12-07，距今(7/31) 129 天 ≈ 4.3 个月")
print()
print("=== 参照 ===")
print("  BTC/ETH 2020-2024 funding 毛年化 14.4% / 17.5%（毛,未扣成本；DEC-095）")
print("  引擎L Holdout 年化 log 增长 -6.86%；投研线净R -17.00% / -0.94%")
