# REPORT_P1PIPE_S1_PANEL

**任务**：P1-RES-039-PIPELINE-S1｜面板完整性核对  
**执行时间**：2026-06-27 UTC  
**复现脚本**：`06_RESEARCH/CODE/p1pipe_s1_panel_audit.py`  
**机器结果**：`06_RESEARCH/CODE/output/p1pipe_s1_panel_audit.json`  
**纪律声明**：未碰 Holdout；未回测；未调参；只读 `06_RESEARCH/DATA/FUTURES_EXPANDED/` 与 `06_RESEARCH/DATA/FUTURES_EXPANDED_2026/`。

## 结论

**Step 1 通过，允许进入 Step 2。** 新面板 `FUTURES_EXPANDED_2026` 有 31 个 4H 合约，全部止于 `2026-06-22 00:00:00`，满足“到 2026-06”的止点要求；与旧 `FUTURES_EXPANDED` 的共同 symbol 接缝连续：旧面板最后一根 `2024-12-09 20:00:00` 在新面板中存在，下一根为 `2024-12-10 00:00:00`，无接缝跳空。

需要带口径限制：10 个 symbol 在 2022-02/2022-03 有历史缺口，因此**全历史严格连续 universe 为 21 个**；但本任务后续 Step 3 是 post-2025 解锁事件 overlap，**2025-01-01 以后 31 个 symbol 均无 4H 缺口**，可用于近端事件普查。若后续事件窗口跨到 2022 缺口，必须逐事件剔除。

## 面板摘要

| 项 | 结果 |
|---|---:|
| 旧面板 symbol 数 | 35 |
| 新面板 symbol 数 | 31 |
| 新面板是否全部到 2026-06 | 是 |
| 新面板重复时间戳 | 0 |
| 与旧面板共同 symbol 接缝不连续数 | 0 |
| 全历史严格连续 universe | 21 |
| post-2025 事件可用 universe | 31 |

旧面板有、新面板缺失：`ALGO, ETC, FIL, MKR, OMG`。  
新面板新增：`ETH`。

## Universe

post-2025 事件可用 universe（31）：  
`AAVE, ATOM, AVAX, AXS, COMP, CRV, DASH, DOT, EGLD, ENJ, ETH, FTM, ICX, KNC, KSM, LINK, LRC, NEAR, REN, RUNE, SNX, SUSHI, THETA, TRX, UNI, XLM, XMR, XTZ, YFI, ZEC, ZRX`

全历史严格连续 universe（21）：  
`AAVE, ATOM, AVAX, AXS, COMP, CRV, DASH, DOT, EGLD, ENJ, ETH, ICX, LINK, REN, RUNE, SNX, THETA, UNI, XMR, XTZ, ZRX`

## 缺口明细

以下 10 个 symbol 在新面板全历史中各有 2 个共同历史缺口，但 2025 以后无缺口：

| Symbol | 缺口 |
|---|---|
| FTM | `2022-02-25 20:00` → `2022-03-01 00:00`；`2022-03-31 20:00` → `2022-04-03 00:00` |
| KNC | 同上 |
| KSM | 同上 |
| LRC | 同上 |
| NEAR | 同上 |
| SUSHI | 同上 |
| TRX | 同上 |
| XLM | 同上 |
| YFI | 同上 |
| ZEC | 同上 |

## 验收自检

| 验收项 | 结果 |
|---|---|
| 核 31+ symbol 止点是否到 2026-06 | 通过，31 个全部到 `2026-06-22 00:00:00` |
| 缺哪些旧 symbol | 已列：`ALGO, ETC, FIL, MKR, OMG` |
| 与旧 `FUTURES_EXPANDED` 接缝是否连续 | 通过，共同 symbol 无接缝跳空 |
| 无重复 bar | 通过，新面板重复时间戳为 0 |
| 给可用 universe 清单 | 已给全历史严格连续 21 与 post-2025 事件可用 31 两口径 |

**下一步闸门**：通过，进入 Step 2 OI/funding 回填。
