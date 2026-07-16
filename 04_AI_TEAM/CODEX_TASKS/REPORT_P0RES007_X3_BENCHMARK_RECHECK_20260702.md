# REPORT_P0RES007_X3_BENCHMARK_RECHECK_20260702

**任务 ID:** P0-RES-007  
**生成时间:** 2026-07-06T16:24:49Z  
**性质:** DEC-092 / v1.5 第5件诊断复查，不消耗独立试验计数  
**脚本:** `06_RESEARCH/CODE/p0res007_x3_benchmark_recheck_20260702.py`  
**审计输出:** `06_RESEARCH/CODE/output/p0res007_x3_benchmark_recheck_20260702.json`

## 0. 方法

- 策略：沿用 `REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md` 的周频低换手 CS 动量，base 成本 0.20%/fill 后净收益。
- 基准：同一周频表中的等权持有 alt 基准 `ew_alt_return`。
- 风险调整：分别将策略和基准周收益缩放到同一目标年化波动率后比较年化 log growth；主表使用 10% vol，附带“都缩放到基准实际 vol”敏感性。
- 显著性：周频 paired moving-block bootstrap，块长 4 周，5000 次，seed `20260702`，比较 `strategy - benchmark` 的年化 log growth 差。
- Holdout：未读取 Holdout；只复用原 B1 脚本从 `06_RESEARCH/DATA/FUTURES_EXPANDED` 构造原口径周频序列。

## 1. 原始未调波动结果

| series | ann. vol | ann. arithmetic return | ann. log growth |
|---|---:|---:|---:|
| CS strategy, base cost | 57.36% | 13.70% | -3.42% |
| EW alt benchmark | 89.04% | 88.48% | 48.45% |

原报告附加死因的原始口径为 CS 年化 log growth -3.42% vs 等权 alt 48.45%。

## 2. 风险调整后比较

| comparison | target vol | strategy vol | benchmark vol | strategy log growth | benchmark log growth | diff | diff 95% CI | P(strategy>=benchmark) | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| both scaled to 10% annual vol | 10.00% | 10.00% | 10.00% | 1.89% | 9.43% | -7.54% | [-19.57%, 6.11%] | 16.38% | not significant |
| both scaled to benchmark actual vol | 89.04% | 89.04% | 89.04% | -23.98% | 48.45% | -72.43% | [-192.49%, 55.52%] | 15.88% | not significant |

## 3. 判定

**RISK_ADJUSTED_GATE_NOT_CONFIRMED。** 风险调整后点估计仍跑输，但“显著跑输”未确认；被动基准门不再作为独立 KILL 死因成立。在主口径 10% 年化波动率匹配后，#X3 策略年化 log growth 为 1.89%，等权 alt 基准为 9.43%，差值 -7.54%；bootstrap 95%CI=[-19.57%, 6.11%]，P(strategy>=benchmark)=16.38%。

整体判决仍维持 **KILL**，因为原主死因“截面单调 CI 穿 0 + 删除前20%赢家后 edge 翻负”独立成立。
