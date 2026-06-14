# PB1 强平解析与就绪门计数器自测

**生成时间 UTC：** 2026-06-14T04:09:49Z  
**任务性质：** 离线工具/监控，不耗 Alpha 计数，不计算事件后收益，不下 edge 结论。

## 模块用途

- `liq_parser.py`：逐行解析 Binance `forceOrder` JSONL，输出 UTC
  `ts_utc, symbol, side, qty, price, notional_usdt` 六列 DataFrame。
- `forward_event_counter.py`：仅对 BTCUSDT/ETHUSDT/SOLUSDT 的 SELL
  强平名义额计算历史信息集内的滚动阈值，统计候选强平卖压 pulse，
  并更新 `A1_FORWARD_EVENT_COUNT.md`。
- 解析器跳过并统计坏行；完整原始 JSON 规范化后用 SHA-256 处理重复行。
  `ap` 为正数时优先，否则回退到 `p`。

## 默认参数

| 参数 | 默认值 |
| --- | --- |
| 品种 | BTCUSDT, ETHUSDT, SOLUSDT |
| SELL 名义额短窗 | 1h |
| 历史扩张分位 | 0.99 |
| 最少历史滚动观测 | 24 |
| 计数模式 | episode_start |
| 就绪门 n_min | 120 |

阈值在时点 `t` 只使用 `t` 之前的滚动名义额，禁止当前值进入自身阈值。
`episode_start` 将连续超阈值区间只计为一个 pulse；相邻消息间隔达到一个
短窗时重置 pulse。`all_hits` 仅作为参数化审计模式。

**上述全部触发参数均为占位值，未冻结、非预登记值；必须等路径B正式预登记时
统一冻结后才能用于机制确证。**

## 单元测试

运行命令：

```bash
python3 -m pytest -q 06_RESEARCH/CODE/forward_liq/tests
```

结果：

```text
......                                                                   [100%]
6 passed in 0.37s
```

覆盖：

- 正常 SELL/BUY、UTC 时间、`ap` 优先和零 `ap` 回退 `p`。
- 名义额计算、坏 JSON、缺字段、空值和重复行计数、坏行比例。
- 合成 JSONL 的手算候选事件数。
- 分位边界使用 `>=`，且当前观测不进入自身历史分位。
- 连续 pulse 去重、跨文件完整 payload 去重，以及参数范围校验。

## 指向真实 LIQUIDATIONS

```bash
python3 06_RESEARCH/CODE/forward_liq/forward_event_counter.py /opt/ai_quant_liq_collector/data/LIQUIDATIONS --window 1h --quantile 0.99 --min-history 24 --n-min 120 --output 06_RESEARCH/RESULTS/A1_FORWARD_EVENT_COUNT.md
```

本地 `06_RESEARCH/DATA/LIQUIDATIONS/` 在自测时无 JSONL，因此正式监控文件明确
显示 `NO INPUT JSONL FOUND`、累计 `n=0`、预计日期 `N/A`。合成数据仅用于 pytest，
未写入正式就绪门计数。

## 治理自检

- 未读取任何 HOLDOUT 文件内容。
- 未读取或修改路径A `A1_WORK/sealed`。
- 未修改 `A1_FORWARD_LIQUIDATION_PATH.md` 或其他预登记文件。
- 未计算收益、成本、CAR、显著性或任何策略表现。
