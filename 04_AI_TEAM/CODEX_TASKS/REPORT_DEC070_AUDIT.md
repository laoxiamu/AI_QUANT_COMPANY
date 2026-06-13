# DEC070-AUDIT 执行报告

**状态：COMPLETED（审计任务完成；DEC-070 四过滤器仍未全部验证）**

## [专业异议]

任务书假设 `FUTURES_EXPANDED` CSV 含 `quote_volume`，实际 35/35 文件仅含
`datetime,open,high,low,close,volume`。Binance 原始 kline 的 `volume` 是基币量，
下载脚本落盘时丢弃了独立的 quote asset volume 列。因此不能把当前 ADTV 结果表述为
精确 quote-volume 计算。

本任务未因此臆造字段，而是：

1. 使用 `volume × HLC3` 计算透明、可复算的 USDT 名义成交额代理。
2. 同时计算 `volume × low` 与 `volume × high` 边界。
3. 验证 35/35 资产的上下界、代理值均落在相同 ADTV 档位。
4. 在报告和 JSON 中保留 `exact_quote_volume_available=false`，不宣称 ADTV 已精确验证。

另一个定义缺口是 `float_market_cap_ratio` 未明确分母。报告只列出
`market_cap/FDV`、`circulating_supply/total_supply`、
`circulating_supply/max_supply` 的定义分歧，未替 DEC-070 擅自选定。

## 交付物

- CODE：`06_RESEARCH/CODE/dec070_filter_audit.py`
- TEST：`06_RESEARCH/CODE/tests/test_dec070_filter_audit.py`
- RESULTS：`06_RESEARCH/RESULTS/20260614_dec070_filter_audit.md`
- JSON：`06_RESEARCH/CODE/output/dec070_filter_audit.json`
- REPORT：`04_AI_TEAM/CODEX_TASKS/REPORT_DEC070_AUDIT.md`

复跑命令：

```bash
python3 06_RESEARCH/CODE/dec070_filter_audit.py
```

## 冻结口径

- cutoff：`datetime < 2024-12-10 00:00:00 UTC`
- 最近 180 日：`2024-06-13` 至 `2024-12-09`
- 日成交额：仅使用含六根标准 4H bar 的完整 UTC 日
- ADTV 代理：`Σ volume × (high + low + close) / 3`
- ADTV 达标/边缘/不达标：`>=10m` / `[5m,10m)` / `<5m` USDT/day
- 跳动收益：连续 4H bar 的 `ln(close_t/close_t-1)`
- 主跳动阈值：`|r| > 15%`；另报 10%/20% 敏感性
- 跳动达标/边缘/不达标：`<=0.20%` / `(0.20%,0.30%]` / `>0.30%`
- 未使用全样本分位数；无随机过程，不需要 seed

## 核心事实

- 部分证据分层：Tier 1-clean `20/35`，Tier 1-watch `10/35`，排除 `5/35`
- ADTV 代理：达标 `24`，边缘 `9`，不达标 `2`
- jump 15%：达标 `27`，边缘 `4`，不达标 `4`
- 排除：`AXSUSDT, FTMUSDT, ICXUSDT, OMGUSDT, RENUSDT`
- 精确 quote volume：`0/35` 可用
- 35/35 资产最近 180 日均有 180 个完整 UTC 日
- 13 个资产存在 2022 年历史缺口；跨缺口收益未计入跳动分母
- `float_market_cap_ratio`：本地不可计算，且公式分母需先冻结
- `oi_market_cap_ratio`：本地不可计算；Binance `openInterestHist` 仅最近一个月，
  无法在 2026-06-14 追回 2020-2024 历史

该结果不对 universe 是否扩展下结论，也不表示任何资产已通过 DEC-070 四项硬过滤。

## 外部数据最小需求

### float_market_cap_ratio

需要资产 ID 映射、历史 circulating supply、total/max supply 或 FDV、历史 market cap。
最小可行源为 CoinGecko/CMC 等历史基本面 API。预计 1-3 工程日完成 35 资产映射、
cutoff 对齐、缺失值核对和原始响应归档，历史供给端点可能需要付费层。

### oi_market_cap_ratio

需要 cutoff 对齐的历史 OI notional、circulating market cap 和场所聚合规则。
需可信历史归档或供应商数据，预计 2-5 工程日，另加数据费用。
`近端 OI/ADTV` 只能作为监控代理，不能替代历史 `OI/market cap`。

## 验证

```text
python3 -m py_compile ...                                  PASS
python3 -m pytest -q test_dec070_filter_audit.py           4 passed
git diff --check                                           PASS
全量脚本运行                                               PASS
```

机器结果复核：

- `asset_count == 35`
- tier count 合计 `20 + 10 + 5 + 0 == 35`
- `exact_quote_volume_asset_count == 0`
- `all_adtv_proxy_classes_robust_to_ohlc_bounds == true`
- 每资产 `recent_180d_complete_dates == 180`
- 每资产输入 CSV SHA-256 已写入 JSON

## 验收标准自检

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| 35 资产逐项 ADTV 数值 | PASS（代理） | 全样本、最近 180 日、上下界及状态均已输出；精确 quote volume 缺失已显式标记 |
| 35 资产逐项 jump 10/15/20% | PASS | 次数、频率、分母和状态均已输出 |
| 公式自包含、阈值冻结 | PASS | 脚本常量、JSON 和报告三处一致 |
| float_mcap 数据缺口 | PASS | 字段、定义缺口、最小数据源和成本已列明 |
| oi_mcap 数据缺口 | PASS | 历史窗口约束、所需字段、可行路径和非等价代理已列明 |
| 基于本地指标分层 | PASS | 20 clean / 10 watch / 5 exclude；明确为部分证据 |
| 不读 Holdout | PASS | 脚本和执行只读取 `FUTURES_EXPANDED` 与其 manifest |
| 不读 `01_MEMORY_CORE/` | PASS | 本任务执行未读取该目录 |
| 不下载新数据 | PASS | 只读取本地 CSV；外部文档仅用于核对字段和 API 窗口 |
| 不构建回测 | PASS | 无信号、仓位、PnL 或策略计算 |
| 不下 D 级结论 | PASS | 报告明确不构成 universe 最终确认 |

## Git 状态

执行期间外部并发流程创建了 commit `cf91c54`，其中已包含本任务的脚本、测试、JSON 和
结果报告，但该 commit message 不含任务号。随后尝试单独提交执行报告与完成事件时，
当前沙箱因 `.git` 只读而拒绝创建 `.git/index.lock`：

```text
fatal: Unable to create '.git/index.lock': Operation not permitted
```

因此 `REPORT_DEC070_AUDIT.md` 与 watcher 已移入 `TASK_INBOX/PROCESSED/` 的完成事件仍为
untracked；未暂存或修改任何无关文件。

## 专业判断

当前最大的审计风险不是阈值高低，而是“过滤器名称存在”被误当作“过滤器证据存在”。
本次结果只能说明价格跳动可本地精确复算、成交额可做稳健代理分档；精确 ADTV、
float 和 OI 三部分仍缺输入或定义。D2 的 `DEC_070_FILTERS_NOT_AUDITABLE` 不应仅凭
本报告被整体解除。
