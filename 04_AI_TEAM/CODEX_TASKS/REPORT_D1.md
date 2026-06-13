# D1 TSMOM Universe Tier 1 数据下载执行报告

## 状态

**BLOCKED - 本地沙箱禁止出站网络连接，未完成数据下载。**

实际报错：

```text
TRXUSDT: FAILED network permission denied: [Errno 1] Operation not permitted
```

补充验证：Node `fetch` 对同一 Binance ZIP URL 的 HEAD 请求也失败，错误为 `getaddrinfo ENOTFOUND data.binance.vision`。

脚本检测到该权限错误后停止继续请求 Binance，避免把同一环境错误重复打到 35 个资产。`DOWNLOAD_MANIFEST.json` 已生成，但成功资产数为 0，D1 验收未通过。

## 任务前自查

- 验证机制：本任务只验证 Tier 1 universe 的 4H 历史数据可采集性，不做交易信号、收益或回测判断。
- 验收标准：任务书给出可量化标准，核心为 manifest 存在、成功资产数 >= 20、成功资产 rows >= 5000。
- 更便宜等效实现：先用 C1 CSV 确定资产列表，再顺序下载月度 ZIP；不做并发，避免 rate limit。
- 禁止项：脚本不读取 Holdout，不修改 `06_RESEARCH/DATA/FUTURES/`，不引入黑箱依赖，不读取全样本分位。

## 已完成

- 读取 `06_RESEARCH/DATA/c1_candidates.csv`。
- 按任务书规则筛选 Tier 1：`head_first_ok == True`、`head_recent_ok == True`、`est_bars >= 7000`、排除黑名单、按 `est_bars` 降序取前 35。
- 新增可复跑脚本：`06_RESEARCH/CODE/d1_tsmom_tier1_download.py`。
- 脚本实现：
  - Binance USD-M monthly klines 4H URL 构造。
  - onboard 月到 2024-12 的顺序下载。
  - ZIP 解压、header/异常行通过 `to_numeric(..., errors="coerce")` 和 `dropna` 清理。
  - 截断到 `2024-12-09 23:59:59 UTC`。
  - 成功资产写入 `06_RESEARCH/DATA/FUTURES_EXPANDED/{SYM}_4H.csv`。
  - 写入 `06_RESEARCH/DATA/FUTURES_EXPANDED/DOWNLOAD_MANIFEST.json`。
- 已运行语法检查：`python3 -m py_compile 06_RESEARCH/CODE/d1_tsmom_tier1_download.py`。
- 已运行 dry selection，确认 Tier 1 资产数 35。
- 已运行真实下载入口，因沙箱网络权限失败而阻塞。

## Tier 1 资产列表

`TRXUSDT, ETCUSDT, LINKUSDT, XLMUSDT, XMRUSDT, DASHUSDT, ZECUSDT, XTZUSDT, ATOMUSDT, THETAUSDT, ALGOUSDT, KNCUSDT, ZRXUSDT, COMPUSDT, OMGUSDT, MKRUSDT, SNXUSDT, DOTUSDT, YFIUSDT, CRVUSDT, RUNEUSDT, SUSHIUSDT, EGLDUSDT, ICXUSDT, UNIUSDT, AVAXUSDT, FTMUSDT, ENJUSDT, KSMUSDT, NEARUSDT, AAVEUSDT, FILUSDT, LRCUSDT, RENUSDT, AXSUSDT`

## Manifest 摘要

- 路径：`06_RESEARCH/DATA/FUTURES_EXPANDED/DOWNLOAD_MANIFEST.json`
- generated：`2026-06-13T16:44:47Z`
- total：35
- success：0
- failed：35
- 首个失败原因：`network permission denied: [Errno 1] Operation not permitted`

## 验收标准自检

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| `DOWNLOAD_MANIFEST.json` 存在 | PASS | 已写入 `06_RESEARCH/DATA/FUTURES_EXPANDED/` |
| 成功资产数 >= 20 | FAIL | 当前环境 success = 0 |
| 每个成功资产 rows >= 5000 | FAIL | 无成功资产 |
| 不读取 HOLDOUT 目录 | PASS | 下载脚本不引用 HOLDOUT；执行中未读取 HOLDOUT 文件内容。注：初始仓库结构巡检只看到目录名，未列出或读取其内容。 |
| 不修改 `06_RESEARCH/DATA/FUTURES/` | PASS | `git status --short 06_RESEARCH/DATA/FUTURES` 无变更 |

## 剩余步骤

在允许访问 `https://data.binance.vision` 的环境中执行：

```bash
python3 06_RESEARCH/CODE/d1_tsmom_tier1_download.py --force
```

执行完成后需要重新检查：

- `DOWNLOAD_MANIFEST.json` 中 `summary.success >= 20`。
- 每个 `ok: true` 的资产 `rows >= 5000`。
- `06_RESEARCH/DATA/FUTURES_EXPANDED/*_4H.csv` 的最大时间不晚于 `2024-12-09 23:59:59 UTC`。
- `06_RESEARCH/DATA/FUTURES/` 仍无变更。

## 恢复前提

- 当前会话或执行环境需要开放出站 HTTPS 到 `data.binance.vision`。
- 不需要读取 Holdout。
- 不需要修改 C1 候选文件或现有 8 币 `FUTURES/` 数据。

## Git

未 commit。原因：D1 数据下载验收失败，当前状态应作为 blocked handoff 交给 Claude，而不是标记为完成任务提交。
