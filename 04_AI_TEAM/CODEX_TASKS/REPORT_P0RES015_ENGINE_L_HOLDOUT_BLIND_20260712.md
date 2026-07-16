# REPORT_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712

**任务 ID:** P0-RES-015  
**生成时间:** 2026-07-12T06:05:03Z  
**性质:** DEC-093 授权的 TSMOM 引擎L 10%目标波动率点 Holdout 一次性盲验  
**Runner:** `06_RESEARCH/CODE/p0res015_engine_l_holdout_blind_20260712.py`  
**审计 JSON:** `06_RESEARCH/CODE/output/p0res015_engine_l_holdout_blind_20260712.json`

## 1. 四门判定

Runner 仅输出四门布尔值；正式 PASS/FAIL 由 Claude 验收后裁决。

| 门 | 数值 | 判据 | 是否通过 |
|---|---:|---|---:|
| H1_E_R_gt_0 | -0.0062898641011967585 | > 0 | False |
| H2_annualized_log_growth_gt_0 | -0.06863517052284801 | > 0 | False |
| H3_max_drawdown_lt_20pct | -0.17026933705240732 | > -0.20 | True |
| H4_not_significantly_underperform_passive | 0.10232850807371027 | diff 95%CI upper >= 0 | True |

## 2. Holdout 指标

- 窗口：2024-12-10 00:00:00 -> 2026-05-31 20:00:00 UTC；rebase 初始权益 100,000。
- 策略 ending equity：90387.17；年化 log growth：-0.068635；最大回撤：-0.170269。
- 基准 ending equity：60828.29；缩放到 10% vol 后年化 log growth：-0.056310。
- H4 diff(strategy-benchmark)：0.005899；95%CI=[-0.090761, 0.102329]。

## 3. 交易诊断

- 窗内入场交易数：151。
- E[R]：-0.0062898641011967585；赢均：0.04175072493374661；亏均(abs)：0.037964977750609974；赢亏比：1.0997168287047348。
- funding 贡献（窗内入场交易口径，cost为正）：1838.06；手续费：7614.59；滑点：7614.58。
- 低功效标记（交易数<10）：False。

| 季度 | 起点 | 终点 | simple return | log return |
|---|---|---|---:|---:|
| 2024Q4 | 2024-12-10 00:00:00 | 2024-12-31 20:00:00 | -3.03% | -0.0307 |
| 2025Q1 | 2025-01-01 00:00:00 | 2025-03-31 20:00:00 | -9.10% | -0.0954 |
| 2025Q2 | 2025-04-01 00:00:00 | 2025-06-30 20:00:00 | -2.56% | -0.0259 |
| 2025Q3 | 2025-07-01 00:00:00 | 2025-09-30 20:00:00 | 8.70% | 0.0835 |
| 2025Q4 | 2025-10-01 00:00:00 | 2025-12-31 20:00:00 | -3.12% | -0.0317 |
| 2026Q1 | 2026-01-01 00:00:00 | 2026-03-31 20:00:00 | 0.00% | 0.0000 |
| 2026Q2 | 2026-04-01 00:00:00 | 2026-05-31 20:00:00 | 0.00% | 0.0000 |

### 跨界交易（不入 H1）

| symbol | entry_time | exit_time | net_pnl | E[R] |
|---|---|---|---:|---:|
| none | - | - | - | - |

## 4. Hash 冻结

| 文件 | SHA256 |
|---|---|
| task_spec | `07ac51bb138ee21850b39c2939621a140822f209aae73e20873c88ea5b5862cf` |
| tsmom_dual_engine | `3c5379b27da8397e9ad50d8f6cc1da7dce3c464374b2a144685dbb7f91f17bb4` |
| p0res014_recheck_script | `ba37c5c57f944ee66a344f74bd58e525de9673eab082f7d8e3b41d59254afb0d` |
| BTC_MARK_4H | `7127294528e65f78965765d315f3bb684dca61941b5f3edc2140081cfa080e47` |
| BTC_FUNDING_8H | `5803cb5e8ffb4dc8b5a1cb4a989ea7477597882341fafbf2a54e0f7148a3b7bf` |
| ETH_MARK_4H | `53135ef7aca6d4dd713cadc3c937b7b3aafcabce76ac20bfa4ab5865d5bba567` |
| ETH_FUNDING_8H | `e3333672e3dd7b9e46592df34a86a33cb599ee6ee8458a09db0d0236e3c76d08` |
| SOL_MARK_4H | `fc58a2e85afa0d71d7d5cd4ef6a56a6975512a9cde4ac0084ebaf5f3d2f6ceb8` |
| SOL_FUNDING_8H | `24456f2c9e71caf27b910aab0b2a1bf7f17b2ee9f0048486a1e07541e3ae3df3` |
| BNB_MARK_4H | `add65e6d6d9a932ece44d6a803dac95b2ed61b535b9255b1dd13167ca0de82c7` |
| BNB_FUNDING_8H | `81f4a92b9d2b6f14185567567a78f3d2389548ce255933eb13083b436a513cb9` |
| XRP_MARK_4H | `04dc42d2bb17d2028da4990695bafca6af83c01f764862668620e1ccb89148e9` |
| XRP_FUNDING_8H | `41deb77f53cdb8502bad8d161d991d5258f61bf0d66644579fd1bd01f791a778` |
| DOGE_MARK_4H | `5e7cf36bb221672417ddba7743dc986b90d9da3267e7c7acfec93d9998511701` |
| DOGE_FUNDING_8H | `e07f22a72564e0fd1b8486dcf55063cfb1dc723cc38b592f446a1340ca33d5cf` |
| ADA_MARK_4H | `b833a72be8f11552f0e85a27e0790705542455ecec9cb6986b78a7dfbd4a5ee4` |
| ADA_FUNDING_8H | `f9be04cfb1a1737384cc700a010fb85744288cb1accf2b9bf67ed9f2b21a4873` |
| LTC_MARK_4H | `fae3a992dc9082ad1923d5f344d6170da9689b326a10f71322f996b878af4f02` |
| LTC_FUNDING_8H | `3c6270f57fcee58ecfd01dcd834faa73ccfd70057f54847f9af3b7ebe06f9b0c` |

## 5. 数据与自检

| symbol | mark rows read | mark last timestamp | funding rows read | funding last timestamp |
|---|---:|---|---:|---|
| BTC | 14010 | 2026-05-31 20:00:00 | 7029 | 2026-05-31 16:00:00 |
| ETH | 14046 | 2026-05-31 20:00:00 | 7029 | 2026-05-31 16:00:00 |
| SOL | 12478 | 2026-05-31 20:00:00 | 6334 | 2026-05-31 16:00:00 |
| BNB | 13854 | 2026-06-05 20:00:00 | 6923 | 2026-06-05 16:00:00 |
| XRP | 14016 | 2026-06-05 20:00:00 | 7028 | 2026-06-05 16:00:00 |
| DOGE | 12930 | 2026-06-05 20:00:00 | 6470 | 2026-06-05 16:00:00 |
| ADA | 13966 | 2026-06-05 20:00:00 | 6988 | 2026-06-05 16:00:00 |
| LTC | 14027 | 2026-06-05 20:00:00 | 7019 | 2026-06-05 16:00:00 |

- cutoff 前 10% 点重构对账：True；diffs={'vs_p006_acceptance_ending_equity_abs_diff': 0.0, 'vs_p006_acceptance_annualized_log_growth_abs_diff': 0.0, 'vs_p014_unadjusted_ending_equity_abs_diff': 0.0, 'vs_p014_unadjusted_return_mean_log_growth_abs_diff': 0.0}。
- 禁读检查：未读取 `*_2026H1*`、`DATA/HOLDOUT/`、`~/.aiquant_sealed/`；runner 只从 `06_RESEARCH/DATA/FUTURES/` 指定 16 个文件读取。
- 参数冻结：lookback / ADX / macro gate / universe / FEE=0.001 / SLIPPAGE=0.001 / funding / LEVERAGE_CAP=1.0 均来自冻结引擎路径或任务书常量，未扫描 15% 点。
- Holdout 封账：本 runner 已对引擎 L 该 Holdout 窗完成一次性评估；后续不应再评估本窗。
