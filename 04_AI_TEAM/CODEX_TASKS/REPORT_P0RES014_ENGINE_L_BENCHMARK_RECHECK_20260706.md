# REPORT_P0RES014_ENGINE_L_BENCHMARK_RECHECK_20260706

**任务 ID:** P0-RES-014  
**生成时间:** 2026-07-06T16:50:42Z  
**性质:** DEC-092 / v1.5 第5件诊断复查；家族内诊断复查收尾，不消耗独立试验计数  
**脚本:** `06_RESEARCH/CODE/p0res014_engine_l_benchmark_recheck_20260706.py`  
**审计输出:** `06_RESEARCH/CODE/output/p0res014_engine_l_benchmark_recheck_20260706.json`

## 0. 方法与边界

- 策略：冻结的 `tsmom_dual_engine.py` 引擎 L；只重构 P0-RES-006 已登记的 10% / 15% 目标波动率仓位点，不重扫仓位，不新增点。
- 基准：`prepare_passive_dataset("L", raw, funding)` + `run_backtest(..., label="benchmark_L_macro_bull")`，与 P0-RES-006 warm-up/旧第五件基准一致。
- 风险调整：沿用 P0-RES-007 v1.5 方法，将策略和基准收益分别缩放到同一目标年化波动率后比较年化 log growth；主表为 10% 年化 vol，敏感性为“都缩放到基准实际 vol”。
- 显著性：4H 原频率 paired moving-block bootstrap，块长 42 根 4H（沿用引擎 L 原 bootstrap 块长），5000 次，seed `20260702`。
- Holdout：未读取 `HOLDOUT` 或 `2026H1`；数据 cutoff 仍为 `2024-12-09 23:59:00`。
- 复用说明：P0-RES-006 JSON 未持久化收益序列；本脚本用同一冻结代码路径重构指定两条序列，并校验 ending equity / annualized log growth 与 P0-RES-006 完全一致。

## 1. 风险调整前对照

| position target vol | strategy ann. vol | benchmark ann. vol | strategy ann. log growth | benchmark ann. log growth | strategy-benchmark log diff | strategy ending equity | benchmark ending equity | old raw equity excess | old v1.4 fifth gate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10% | 14.43% | 57.06% | 18.42% | 53.73% | -35.31% | 248,231.44 | 1,418,594.95 | -1,170,363.51 | False |
| 15% | 17.46% | 57.06% | 22.30% | 53.73% | -31.43% | 300,693.25 | 1,418,594.95 | -1,117,901.71 | False |

旧口径用 ending equity / raw profit 直接比较，因此 10% 与 15% 两个点的 `fifth_benchmark_excess_positive` 均为 False。

## 2. 风险调整后比较

| position target vol | comparison | target vol | strategy vol | benchmark vol | strategy log growth | benchmark log growth | diff | diff 95% CI | P(strategy>=benchmark) | gate |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10% | both scaled to 10% annual vol | 10.00% | 10.00% | 10.00% | 12.98% | 11.78% | 1.20% | [-4.21%, 6.24%] | 62.10% | not significant / pass |
| 10% | both scaled to benchmark actual vol | 57.06% | 57.06% | 57.06% | 60.64% | 53.73% | 6.91% | [-23.85%, 35.52%] | 62.06% | not significant / pass |
| 15% | both scaled to 10% annual vol | 10.00% | 10.00% | 10.00% | 13.15% | 11.78% | 1.37% | [-3.90%, 6.27%] | 64.40% | not significant / pass |
| 15% | both scaled to benchmark actual vol | 57.06% | 57.06% | 57.06% | 61.58% | 53.73% | 7.85% | [-22.46%, 35.39%] | 64.50% | not significant / pass |

主口径 10% 仓位点：策略年化 log growth 12.98%，基准 11.78%，差值 1.20%；95%CI=[-4.21%, 6.24%]，P(strategy>=benchmark)=62.10%。

## 3. 七项检查复核

| position target vol | E[R]>0 | win/loss>=1.5 | P(DD35)<=20% | P(DD20)<=10% | log growth>0 | positive years majority | WF majority positive | v1.5 risk-adjusted benchmark gate | all pass |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10% | True | True | True | True | True | True | True | True | True |
| 15% | True | True | True | True | True | True | True | True | True |

## 4. 判定

**RISK_ADJUSTED_GATE_NOT_CONFIRMED。** 风险调整后，“策略显著跑输基准”不成立；旧 v1.4 原始收益比较导致的被动基准 KILL 不再成立。

TSMOM引擎L·10%目标波动率点＝七项检查全过，构成DEC-092后首个重新达标候选，是否晋级正常验收/paper-forward流程待Claude/Founder决定。

## 5. 自检

- 未改动仓位扫描范围；本脚本只跑 P0-RES-006 已登记且已通过 DD/增长门的 10% / 15% 两点。
- 未引入新仓位点，未改动 lookback / ADX / macro gate / universe / 成本 / funding / cutoff。
- 未读取 Holdout；`safe_market_path` 仍禁止 `2026H1` 文件名，数据审计最后时间为 2024-12-09。
- 10% / 15% 重构一致性校验已通过，详见 JSON 的 `p006_reconstruction_check`。
