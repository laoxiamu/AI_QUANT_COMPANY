# REPORT_P1PIPE_S2_OIFUNDING

**任务**：P1-RES-039-PIPELINE-S2｜OI/funding 回填到 2026  
**执行时间**：2026-06-27 UTC  
**复现脚本**：`06_RESEARCH/CODE/p1pipe_s2_oifunding_backfill.py`；REST 补源脚本 `06_RESEARCH/CODE/p1pipe_s2_funding_rest_supplement.py`  
**机器结果**：`06_RESEARCH/CODE/output/p1pipe_s2_oifunding_audit.json`  
**输出目录**：`06_RESEARCH/DATA/FUTURES_OI_FUNDING_2026/`  
**manifest**：`06_RESEARCH/DATA/FUTURES_OI_FUNDING_2026/manifest.json`  
**纪律声明**：未碰 Holdout；未回测；未调参；未用付费 API；未覆盖旧 `06_RESEARCH/DATA/FUTURES/`。

## 结论

**Step 2 通过，允许进入 Step 3，但后续结构资金流分档必须带数据可用性过滤。**

本次用 Binance Data Vision 免费源回填 `2025-01-01` 至 `2026-06-22`：funding 使用 monthly `fundingRate` 压缩包 + Binance fapi REST/curl 补近端；OI 使用 daily `metrics` 压缩包并聚合成 4H。共记录 manifest 17,247 条源记录；输出 31 个 funding CSV 与 31 个 OI metrics CSV，目录大小约 21MB。

可用性边界：

- **OI metrics 近端可用 29/31**：除 `FTM, REN` 外，均覆盖到 `2026-06-23 00:00:00` 左右；`FTM, REN` 的 Binance metrics 只覆盖到 `2025-03-10`。
- **funding 近端可用 25/31**：`FTM, LRC, REN, UNI, XMR, XTZ` 未覆盖完整到 `2026-06-22`。其中 `FTM, REN` 只到 `2025-06-19`，`LRC` 到 `2026-03-24`，`UNI/XMR/XTZ` 到 `2026-05-31`。
- Step 3/4 若事件落在缺口之后，不能使用对应 symbol 的 OI/funding 分档或 ex-funding 拆账；应剔除或标为“价格 overlap 有、结构资金流缺”。

## 数据源与 manifest

| 数据 | 主源 | 补源 | 输出 |
|---|---|---|---|
| Funding | Binance Data Vision `data/futures/um/monthly/fundingRate/{symbol}` | Binance fapi `/fapi/v1/fundingRate`，curl fallback | `funding_8h/*_funding_8h.csv` |
| OI metrics | Binance Data Vision `data/futures/um/daily/metrics/{symbol}` | 无；404 如实记录 | `metrics_4h/*_metrics_4h.csv` |

manifest 状态汇总：

| 类型 | 成功 | 失败/缺失 |
|---|---:|---:|
| metrics daily zip | 15,738 | 940（938 个 404，2 个 transport failure） |
| funding monthly zip | 503 | 24（404） |
| funding REST 原调用 | 23 | 8（Python SSL 临时失败） |
| funding REST curl 补源 | 5 | 6（REST 无返回/不可补） |

## 覆盖缺口

Funding 缺口：

| Symbol | 行数 | 覆盖起点 | 覆盖止点 |
|---|---:|---|---|
| FTM | 509 | `2025-01-01 00:00:00.015` | `2025-06-19 08:00:00.003` |
| LRC | 2,058 | `2025-01-01 00:00:00.015` | `2026-03-24 08:00:00` |
| REN | 509 | `2025-01-01 00:00:00.015` | `2025-06-19 08:00:00.003` |
| UNI | 1,548 | `2025-01-01 00:00:00.015` | `2026-05-31 16:00:00.004` |
| XMR | 1,548 | `2025-01-01 00:00:00.015` | `2026-05-31 16:00:00.004` |
| XTZ | 2,534 | `2025-01-01 00:00:00.015` | `2026-05-31 20:00:00.010` |

OI metrics 缺口：

| Symbol | 行数 | 覆盖起点 | 覆盖止点 |
|---|---:|---|---|
| FTM | 96 | `2025-01-01 00:00:00` | `2025-03-10 00:00:00` |
| REN | 69 | `2025-01-01 00:00:00` | `2025-03-10 00:00:00` |

## 后续可用 universe

价格 + OI 近端可用（29）：  
`AAVE, ATOM, AVAX, AXS, COMP, CRV, DASH, DOT, EGLD, ENJ, ETH, ICX, KNC, KSM, LINK, LRC, NEAR, RUNE, SNX, SUSHI, THETA, TRX, UNI, XLM, XMR, XTZ, YFI, ZEC, ZRX`

价格 + OI + funding 近端完整可用（25）：  
`AAVE, ATOM, AVAX, AXS, COMP, CRV, DASH, DOT, EGLD, ENJ, ETH, ICX, KNC, KSM, LINK, NEAR, RUNE, SNX, SUSHI, THETA, TRX, XLM, YFI, ZEC, ZRX`

## 验收自检

| 验收项 | 结果 |
|---|---|
| 免费回填 universe 的 OI + funding 到 2026 | 部分通过：31 个均有输出；29 个 OI 近端可用；25 个 OI+funding 近端完整可用 |
| 优先 Data Vision 月/日压缩包 | 通过：funding monthly、metrics daily |
| REST 补近端 | 通过：fapi REST + curl fallback，成功补 5 个 symbol |
| 写 checksum/manifest | 通过：17,247 条源记录，含 sha256/HTTP 状态/错误 |
| 不覆盖旧数据 | 通过：写入新目录 `FUTURES_OI_FUNDING_2026` |
| 报覆盖区间/缺口 | 通过，缺口已列 |
| 不伪造失败源 | 通过，404/SSL/REST 空返回均保留在 manifest |

**下一步闸门**：通过，进入 Step 3。Step 3 overlap 统计要同时给“价格 overlap”和“结构资金流 overlap”两种口径。
