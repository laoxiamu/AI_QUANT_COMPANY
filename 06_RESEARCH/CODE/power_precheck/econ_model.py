CASH = 12000.0          # 现金成本/年（月预算约1000元，DEC 关键约束）
HOURS = 365.0           # Founder 1h/天
CAPS = [30000, 100000, 300000]
RETS = [0.03, 0.10, 0.20]
TIME_RATES = [0, 50, 100, 200]   # 元/小时，时间机会成本情景

print("=== 表1：扣现金成本后的净值（元/年） ===")
print(f"{'本金':>8} |" + "".join(f"{int(r*100):>6}% " for r in RETS) + " | 打平现金成本所需净年化")
print("-"*68)
for c in CAPS:
    row=f"{c:>8,} |"
    for r in RETS:
        row += f"{c*r-CASH:>7,.0f}"
    be = CASH/c
    print(row + f" | {be*100:>6.1f}%")

print()
print("=== 表2：再扣 Founder 时间机会成本后（元/年） ===")
print(f"{'本金':>8} {'净年化':>6} |" + "".join(f"{v:>9}元/h" for v in TIME_RATES))
print("-"*66)
for c in CAPS:
    for r in RETS:
        row=f"{c:>8,} {int(r*100):>5}% |"
        for tr in TIME_RATES:
            row += f"{c*r-CASH-HOURS*tr:>12,.0f}"
        print(row)
    print()

print("=== 表3：各本金档打平门槛 ===")
print(f"{'本金':>8} | 打平现金 | 打平现金+50元/h | 打平现金+100元/h")
print("-"*62)
for c in CAPS:
    print(f"{c:>8,} | {CASH/c*100:>7.1f}% | {(CASH+HOURS*50)/c*100:>14.1f}% | {(CASH+HOURS*100)/c*100:>15.1f}%")

print()
print("=== 参照：已实测的负向证据 ===")
print("  引擎L Holdout盲验: 年化log增长 -6.86%，成本拖累 ≈11.6%/年")
print("  投研线 5簇结算:    窗末方向命中 2/7，费后净R -17.00% / -0.94%（仅006/007有此口径）")
