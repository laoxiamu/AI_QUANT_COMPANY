# D2 TSMOM 扩展 Universe 信号层回测

**[专业异议]**

## 技术结论

**任务状态：BLOCKED。不能回答“扩 universe 后 P(DD≥20%) 是否 <10%”。**

变体 C 已按冻结的 8 币 `tsmom_dual_L` 口径精确复现；变体 A/B 因输入不满足同源价格、真实 funding 和 DEC-070 universe 审计要求而暂停。用零 funding 或混用 contract/mark K 线继续计算会直接违反成本完整与单变量原则。

## 三变体对比

| 指标 | 变体C（8币） | 变体A（28币） | 变体B（38币） |
|---|---:|---:|---:|
| E[R] per trade | 0.066073 | BLOCKED | BLOCKED |
| 赢亏比 | 3.828 | BLOCKED | BLOCKED |
| 正年比例 | 4/4 | BLOCKED | BLOCKED |
| P(DD≥20%) | 81.7% | BLOCKED | BLOCKED |
| 第五件：基准超额 | $168,664.44 | BLOCKED | BLOCKED |
| 完整 universe 单资产权重帽 | 12.50% | 3.57% | 2.63% |
| 历史实际最大初始权重 | 25.00% | BLOCKED | BLOCKED |
| WF 3段 Sharpe | 1.855 / -0.288 / 1.861 | BLOCKED | BLOCKED |

注意：任务书表格把变体 C 单资产最大权重写为 12.5%，这是“8 币全部可交易时”的权重帽。冻结引擎按当时 PIT 可交易资产数动态分配，早期历史实际最大初始权重为 25.00%，不能把 12.5% 误写成全历史实际最大值。

## P1-06 / 8币基线复现

- 权威基线：`tsmom_dual_L`，不是旧 3 币 `p1_06_tsmom_macro_bull`。
- E[R]：预期 `0.066073`，本次 `0.066073`，相对偏差 `0.000000%`，通过 `<5%` 验收。
- 第五件超额：预期 `$168,664.44`，本次 `$168,664.44`。
- 固定成本：手续费 `0.1%/边` + 滑点 `0.1%/边` + 真实 8H funding。
- 冻结信号：L=540 根 4H、ADX 14/25/20、前一完整 UTC 日日收盘相对 SMA200、仅做多、t+1 open。

## 阻塞项

1. **PRICE_SOURCE_MISMATCH**：D1 expanded files use contract klines, while the frozen 8-asset baseline uses mark-price klines. Mixing them is not a single-variable universe test.
2. **MISSING_REAL_FUNDING**：30/30 selected expanded assets lack pre-cutoff real 8H funding files: ETCUSDT, LINKUSDT, TRXUSDT, XLMUSDT, XMRUSDT, DASHUSDT, XTZUSDT, ATOMUSDT, ZECUSDT, THETAUSDT, ALGOUSDT, ZRXUSDT, KNCUSDT, COMPUSDT, OMGUSDT, SNXUSDT, MKRUSDT, DOTUSDT, CRVUSDT, RUNEUSDT, YFIUSDT, SUSHIUSDT, EGLDUSDT, ICXUSDT, UNIUSDT, AVAXUSDT, ENJUSDT, FTMUSDT, RENUSDT, AAVEUSDT
3. **DEC_070_FILTERS_NOT_AUDITABLE**：DOWNLOAD_MANIFEST.json does not prove the DEC-070 hard filters: adtv, float_market_cap_ratio, oi_market_cap_ratio, price_jump_frequency

## 为什么这些问题会改变结论

1. Contract K 线与 mark-price K 线会改变动量、ADX、门控、成交价和权益路径，A/B 与 C 不再只差 universe。
2. 新资产 funding 不是小额可忽略项。8 币基线 funding 成本为实质性成本，按零处理会系统性抬高 E[R]、终值和基准超额。
3. DEC-070 要求 ADTV、流通市值比、OI/市值比和异常跳动频率硬过滤；当前 manifest 只证明历史长度、归档可得与手工黑名单，不能证明入选资产是决策定义的 Tier 1。

## Holdout 与数据边界

- 本脚本只读取既有 8 币固定 pre-cutoff 行数与 D1 manifest；未读取任何 `HOLDOUT` 路径。
- 变体 C 行情与 funding 最大时间均不晚于 `2024-12-09 23:59:59`，显式 assert 已通过。
- A/B 未加载收益数据、未生成信号、未计算指标。

## 恢复前提

1. 为入选 30 个扩展资产提供截至 `2024-12-09 23:59:59 UTC` 的同源 **mark-price 4H** 文件。
2. 为同一批资产提供截至同一边界的真实 **8H funding** 文件。
3. 在 manifest 或独立审计文件中逐项证明 DEC-070 四个硬过滤器，并由 Claude 确认 universe。
4. 保持 8 币变体 C、参数、成本、WF 边界和 bootstrap seed `20260612` 不变后再恢复 A/B。

## 方法口径

- Bootstrap：4H 净值收益、块长 `42` 根、`2000` 路径、seed `20260612`、一年路径。
- WF 边界：`2020-01-01 00:00:00` / `2021-08-24 12:00:00` / `2023-04-18 04:00:00` / `2024-12-10 00:00:00`。
- 图表省略：A/B 无合法数值，绘制 DD 对比图会制造虚假可比性；保留精确审计表。
- 结论字段保持 `null`，不得把阻塞结果写成 `DD_improved` 或 `DD_not_improved`。
