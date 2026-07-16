# Codex 任务：价格面板刷新到 2026 + 解锁日历 overlap 普查（数据基建）

**任务 ID：** DATA-PANEL-REFRESH-2026｜**派发：** Claude（主理人）｜**日期：** 2026-06-22
**上位：** 主理人裁决（连续三条研究线阶段A死于本地价格面板止 2024-12-09 无法与近端事件/流重叠；binding constraint=数据基建非机制）/ DEC-088 / 记忆 stale-price-panel-binding-constraint
**性质：** 纯数据工程。不回测、不碰 Holdout、不调参、不做信号/方向、不耗独立计数。免费数据源，禁付费。

---

## 背景（为什么做这个）
本地多资产研究面板 `06_RESEARCH/DATA/FUTURES_EXPANDED/`（35 资产×4H）止于 **2024-12-09**。forced-flow 强平簇（liq 是 2026-06-15 起）和 P1 解锁（免费日历 2025-06 起）都因与该面板无时间重叠，死在阶段A。本任务刷新面板到当前，解锁后续所有"向前看"机制。

## 交付

### 1. 扩展 4H OHLCV 面板到 2026（核心，免费）
- 对 `FUTURES_EXPANDED/` 现有 35 个 symbol（+ 若缺 BTCUSDT/ETHUSDT 则补上），拉 **2024-12-09 → 2026-06-22** 的 **4H K线（OHLCV）**，免费源（Binance USDⓈ-M futures klines REST `/fapi/v1/klines`；若某 symbol Binance 取不到，Bybit `/v5/market/kline` 兜底）。代理 env 已在调用层给。
- 写为与现有 schema 一致的 CSV（`datetime, open, high, low, close, volume`，UTC），**新文件写到 `06_RESEARCH/DATA/FUTURES_EXPANDED_2026/`**（不覆盖旧文件，便于对账）；或在旧文件基础上 append 并保留旧文件备份。给出每 symbol 的新止点与行数。
- ⚠️ 已下架/改名 symbol（如 REN 等幸存者偏差项）取不到的，如实标注"已下架/无数据"，不要伪造。

### 2. 免费解锁日历拉取 + overlap 普查（决定 P1 解锁 B1 生死）
- 用**免费可得**的解锁日历（Tokenomist 免费/试用页面可见的 upcoming/recent、或 DefiLlama Unlocks 公开数据，按上轮报告 `REPORT_P1RES039_PHASEA_20260622.md` 的 schema），拉 **2025-06 → 2026-06** 期间、本面板 universe 内 symbol 的解锁事件（字段尽量含 `symbol, unlockDate, 规模, 流通占比, allocation`）。
- **只用免费边界内数据**，不开通付费、不大规模抓取超额。
- 与刷新后的价格面板做时间重叠，**统计 overlap episode 数**：按 symbol×解锁日聚合，报 ①总 episode 数 ②≥100? ③≥300 可 60/20/20? ④按规模档分布。

### 3.（次要，能做则做）OI/funding 刷新
- 记录 Binance OI/funding 免费历史的可得边界（API 近端 lookback + Binance Data Vision 月度 dump 链接），**只报可得性与计划，不要在本任务大规模回填**（避免 VM 大下载热循环致 DC 掉线，参 RUNBOOK）。

## 输出
- 刷新后的面板文件（见 1）。
- 报告：`04_AI_TEAM/CODEX_TASKS/REPORT_PANEL_REFRESH_2026_20260622.md`（面板覆盖结果 + 解锁 overlap episode 普查 + OI/funding 可得性计划）。
- 复现脚本 + 审计 JSON。
- 回写：`04_AI_TEAM/TASK_INBOX/DATA-PANEL-REFRESH-2026_DONE.json`（status / 面板新止点 / overlap episode 数 / P1解锁B1 是否可行 的一句话结论）。

## 纪律
- 纯数据工程，read-only 分析 + workspace-write 写数据/报告。免费源，禁付费。不动 Holdout、不回测、不造信号。
- 大下载用分页 + 限速，避免热循环（DC 稳定性，RUNBOOK）。

【需要Codex】workspace-write（写面板/报告/脚本）。
