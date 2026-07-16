# P0-RES-008 完成报告：价格面板6个SSL失败symbol修复

**执行：** Claude（直接执行，非Codex——诊断后判断属≤50行小规模修复，走DC直连通道，未走codex exec）
**执行时间：** 2026-07-06

## 根因

6个symbol（ALGOUSDT/BTCUSDT/ETCUSDT/FILUSDT/MKRUSDT/OMGUSDT）原失败错误为
`SSL: UNEXPECTED_EOF_WHILE_READING`——**不是symbol特定的数据/代码问题，是瞬时网络连接问题**（原2026-06-22执行时很可能代理/连接被重置）。诊断方式：对BTCUSDT单独重试（直连、代理env全unset）立即成功，证实root cause是连接层瞬时故障而非请求本身有误。

## 修复方式

直接调用 `06_RESEARCH/CODE/panel_refresh_2026.py` 中现成的 `refresh_symbol()` 函数（未改代码），
用 `env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy` 直连Binance fapi，对6个symbol逐个重跑。
首轮4/6成功（ALGOUSDT/FILUSDT/MKRUSDT/OMGUSDT），BTCUSDT/ETCUSDT仍SSL EOF（判断=批量连续请求触发限流/连接重置，非确定性per-symbol故障）；
二轮对这2个加重试+间隔后**全部成功**。

## 修复后数据

| symbol | 行数 | 起始 | 截止 |
|---|---|---|---|
| ALGOUSDT | 13181 | 2020-06-16 | 2026-06-22 |
| BTCUSDT | 3361 | 2024-12-09 | 2026-06-22 |
| ETCUSDT | 14093 | 2020-01-16 | 2026-06-22 |
| FILUSDT | 12420 | 2020-10-16 | 2026-06-22 |
| MKRUSDT | 12804 | 2020-08-13 | 2026-06-22 |
| OMGUSDT | 13055 | 2020-07-02 | 2026-06-22 |

6个symbol现在都续到2026-06-22，与其余31个symbol截止日期一致，gaps_over_4h=0或与原有panel持平（无新增缺口），duplicate_timestamps=0。

## ⚠️ 重要发现（非本次任务制造，但本次修复过程中确认）：BTCUSDT历史深度远低于其他symbol

`06_RESEARCH/DATA/FUTURES_EXPANDED/`（2024-12-09截止的旧面板）**从未包含过BTCUSDT文件**——这不是本次刷新引入的新缺口，是项目原始价格面板建立时就存在的遗留缺口。结果：BTCUSDT当前只有约1.5年历史（2024-12-09起），而其余6个symbol样本里的对照组（ALGOUSDT/ETCUSDT/FILUSDT/MKRUSDT/OMGUSDT）都有2020年至今约6年历史。

**这件事的分量：** BTCUSDT是清算数据采集器的核心覆盖标的、也是加密市场机制研究里最重要的核心资产，历史深度只有其余标的的1/4不到。任何用到"标的间历史长度需要基本一致"的分析（如TSMOM引擎的cross-asset相关性估计、组合式晋级未来若启用后的相关性计算）都需要注意BTCUSDT这个不对称——不是"缺数据"，是"数据比别人短得多"，且这个缺口目前尚未补。是否需要另外找回2020-2024年这段的BTCUSDT历史（Binance该合约本身自2019年就有），是一个新的、值得单独评估的候选任务，本次未处理（超出SSL修复范围）。

## 产出文件

- `06_RESEARCH/DATA/FUTURES_EXPANDED_2026/{ALGOUSDT,BTCUSDT,ETCUSDT,FILUSDT,MKRUSDT,OMGUSDT}_4H.csv`（已更新）
- `06_RESEARCH/CODE/output/panel_refresh_2026_sslfix_20260706.json`（首轮记录）
- `06_RESEARCH/CODE/output/panel_refresh_2026_sslfix_retry2_20260706.json`（二轮BTCUSDT/ETCUSDT重试记录）

**37/37 symbol现在全部续到2026-06-22。** forced-flow v2重启后的分档检验不再受BTCUSDT数据缺失阻塞（但BTCUSDT历史深度不对称问题仍待另行评估，见上）。
