# REPORT_PANEL_REFRESH_2026_20260622

**任务**：DATA-PANEL-REFRESH-2026｜价格面板刷新到 2026 + 解锁日历 overlap 普查
**Codex 执行时间**：2026-07-16T06:24:09Z
**纪律声明**：纯数据工程；未回测；未碰 Holdout；未调参；未做信号/方向；旧面板只读，新产出限定写入 `FUTURES_EXPANDED_2026/`、`CODE/output/`、本报告与 TASK_INBOX。

## 总裁决

**完成：面板刷新脚本已成功写入 2026 目录。**

## A. 面板刷新结果

- Universe：旧面板 35 个 symbol + BTCUSDT/ETHUSDT 补齐后 37 个。
- 成功/有文件：37；失败：0。
- 输出目录：`06_RESEARCH/DATA/FUTURES_EXPANDED_2026`。

| Symbol | 状态 | 源 | 新下载行 | 合并止点 | 行数 | 失败摘要 |
|---|---|---|---:|---:|---:|---|
| AAVEUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12595 |  |
| ALGOUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 13326 |  |
| ATOMUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14105 |  |
| AVAXUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12733 |  |
| AXSUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12385 |  |
| BTCUSDT | downloaded | binance_fapi | 3506 | 2026-07-16 04:00:00 | 3506 |  |
| COMPUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 13242 |  |
| CRVUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12865 |  |
| DASHUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14124 |  |
| DOTUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12925 |  |
| EGLDUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12787 |  |
| ENJUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12697 |  |
| ETCUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14238 |  |
| ETHUSDT | downloaded | binance_fapi | 3506 | 2026-07-16 04:00:00 | 3506 |  |
| FILUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12565 |  |
| FTMUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12697 |  |
| ICXUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12781 |  |
| KNCUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 13260 |  |
| KSMUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12577 |  |
| LINKUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14232 |  |
| LRCUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12547 |  |
| MKRUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12949 |  |
| NEARUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12570 |  |
| OMGUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 13200 |  |
| RENUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12613 |  |
| RUNEUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12847 |  |
| SNXUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12973 |  |
| SUSHIUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12817 |  |
| THETAUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 13446 |  |
| TRXUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14214 |  |
| UNIUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12763 |  |
| XLMUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14184 |  |
| XMRUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14130 |  |
| XTZUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14112 |  |
| YFIUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 12841 |  |
| ZECUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 14088 |  |
| ZRXUSDT | downloaded | binance_fapi | 3500 | 2026-07-16 04:00:00 | 13278 |  |

## B. 解锁日历 overlap 普查

- 目标窗口：2025-06-01..2026-06-22。
- 免费事件拉取状态：not_completed。
- overlap episode 数：0。
- episode ≥100：False。
- episode ≥300 可 60/20/20：False。
- 规模档分布：`{}`。

说明：上轮已核 Tokenomist event API/CSV 的免费边界；本轮因网络不可达，未能获得 2025-06..2026-06 的免费事件级日历。脚本保留 overlap 计算入口，但当前不把历史文章样本冒充为目标窗口事件。

## C. OI/funding 可得性计划

- 本任务未做大规模 OI/funding 回填。
- Binance REST：`/fapi/v1/fundingRate` 可分页取 funding 历史；`/futures/data/openInterestHist` 可取 near-term OI 历史。
- Binance Data Vision：优先用 `data/futures/um/daily/metrics`、`monthly/markPriceKlines`、`monthly/fundingRate` 月/日压缩包做受控回填，写 checksum/manifest，避免 VM 热循环。
- 本地已存在相关文件数：0。

## D. 复现

脚本：`06_RESEARCH/CODE/panel_refresh_2026.py`

```bash
python3 06_RESEARCH/CODE/panel_refresh_2026.py
```

若需要显式代理，先修正当前死端口，例如：

```bash
HTTPS_PROXY=http://127.0.0.1:<可用端口> HTTP_PROXY=http://127.0.0.1:<可用端口> python3 06_RESEARCH/CODE/panel_refresh_2026.py
```

审计 JSON：`06_RESEARCH/CODE/output/panel_refresh_2026_audit.json`

## 验收标准自检

| 验收项 | 结果 |
|---|---|
| 新面板写入 `FUTURES_EXPANDED_2026/` | 完成 |
| 不覆盖旧文件 | 达标 |
| 已下架/无数据如实标注 | 达标：失败逐 symbol 记录源错误；未伪造 |
| 解锁 overlap episode 普查 | 未达成完整事件拉取；当前 episode=0 |
| OI/funding 只报可得性计划 | 达标 |
| 不碰 Holdout / 不回测 / 不调参 | 达标 |
