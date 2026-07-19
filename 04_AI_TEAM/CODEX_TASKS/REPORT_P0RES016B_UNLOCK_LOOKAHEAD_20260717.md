# REPORT P0-RES-016b：解锁源 lookahead 修复

任务：`P0-RES-016b`  
执行时间锚：2026-07-17，实测样例截至 `2026-07-17 08:05 UTC`（Asia/Singapore 16:05）  
状态：completed

## 结论

已修复 `token_unlock` 源只能 T0 浮出的 lookahead 问题。

新主路径使用 CryptoRank 客户端 XHR 的真实公开 API：

```text
https://api.cryptorank.io/v0/consolidated-vesting/important-upcoming-unlocks?period=7D
```

该接口在 SG 上实测返回 T0 到未来 7 天的重要解锁事件，字段包含 `key`、`symbol`、`unlockDate`、`unlockUsd`、`tokensPercent`。`scan_token_unlocks()` 现在优先解析该 API；若 API 结构漂移或不可用，会降级到原 CryptoRank `__NEXT_DATA__` SSR 解析；两路都失败时抛出清晰错误，由 `run_scan()` 写入 `source_errors`，不拖垮全局扫描。

未接入 DropsTab：首选 CryptoRank API 已找到并实测可用，因此未走备选 HTML 解析路径。

## API 复原依据

按任务要求在 SG 下载 CryptoRank `/token-unlock` 页面引用的全部 20 个 JS chunk，关键线索如下：

- `pages/token-unlock-db0565aafda4237c.js`：页面调用 `getImportantUpcomingUnlocks({period:t})`。
- `76154-f2469bc765894956.js`：API class 暴露 `consolidated-vesting/important-upcoming-unlocks`。
- `_app-42b916cf3408af89.js`：`sendRequest()` 拼接规则为 `${REACT_APP_API_SERVER}/v0/${path}`，`REACT_APP_API_SERVER` 为 `https://api.cryptorank.io`。
- SG curl 实测 `period=D7` 返回 400，错误明示合法值为 `7D,30D`；`period=7D` 返回真实事件列表。

## 代码改动

- `06_RESEARCH/CODE/thesis_hf_scan.py`
  - 新增 `CRYPTORANK_API_BASE` 与 `CRYPTORANK_IMPORTANT_UNLOCKS_URL`。
  - 新增 API 解析辅助函数 `_scan_cryptorank_important_unlocks()`。
  - 将旧 SSR 解析拆为 `_scan_cryptorank_next_data_unlocks()`，作为 fallback。
  - 候选新增顶层 `key` 字段，满足登记通道至少需要 `symbol/key` 的要求。
  - 保留 source 名称 `token_unlock_cryptorank`，不改其他三源逻辑。

- `06_RESEARCH/CODE/tests/test_thesis_hf_scan.py`
  - 覆盖 CryptoRank upcoming API 优先路径。
  - 覆盖 hidden/no-key 行跳过，不伪造不可登记事件。
  - 覆盖源结构变化时进入 `source_errors`，不崩全局扫描。
  - 更新旧 SSR 测试，确认 fallback 仍可解析并输出顶层 `key`。

## SG 实测

命令：

```bash
python3 thesis_hf_scan.py --fetch-via-ssh-sg --sources token_unlocks,binance_announcements,depeg,funding_oi --output-dir output --table-limit 40
```

输出文件：

```text
06_RESEARCH/CODE/output/thesis_hf_scan_20260717_0805.json
```

回读统计：

```text
scan_utc 20260717_0805
sources_requested ['token_unlocks', 'binance_announcements', 'depeg', 'funding_oi']
source_errors []
n_candidates 92
```

Unlock 样例：

```text
DBR   debridge        2026-07-17  T+0  $10,454,339  10.8%
PENGU pudgy-penguins  2026-07-17  T+0  $4,296,659   1.1%
KAITO kaito           2026-07-20  T+3  $15,236,313  7.3%
ZRO   layerzero       2026-07-20  T+3  $20,529,462  7.3%
RIVER river           2026-07-22  T+5  $3,090,915   4.6%
```

修复成立：截至 `2026-07-17 08:05 UTC` 的 SG 全源扫描中，`token_unlock` 已浮出至少 3 条 T+1 到 T+14 窗口内未来事件。

备注：扫描控制台开头出现过 funding/OI 单 symbol 的 SSH banner timeout，已落到对应候选的 `oi_error` 字段；顶层 `source_errors` 为空。

## 验证

```text
python3 -m pytest tests/test_thesis_hf_scan.py
8 passed in 0.08s
```

```text
python3 -m py_compile thesis_hf_scan.py
exit 0
```

## 护栏自检

- 未读取 Holdout。
- 未做量化实验。
- 未花钱，未申请 API key，未注册 thesis。
- 未修改预登记文档或 thesis 模板。
- 未引入第三方依赖；仅使用 Python 标准库。
- 改动范围限定在 `scan_token_unlocks()` 及解锁相关辅助函数、目标测试。
- 其他三源逻辑未改；legacy funding/OI 输出函数未改。
