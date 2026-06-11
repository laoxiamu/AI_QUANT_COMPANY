# REPORT_R1_A2_FEATURES

**任务：** TASK_R1_A2_FEATURES  
**执行时间：** 2026-06-11 UTC  
**结论：** 已交付 A-2 funding 极端事件特征脚本、工作集事件表、事件级 Holdout 文件与 pytest。未读取 MARK 价格文件，未做收益/价格反应分析。

## 交付物

- CODE: `06_RESEARCH/CODE/features/a2_funding_features.py`
- TEST: `06_RESEARCH/CODE/features/test_a2_features.py`
- WORK: `06_RESEARCH/CODE/output/a2_events_work.csv`
- HOLDOUT: `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv`
- SUMMARY: `06_RESEARCH/CODE/output/a2_events_summary.json`

## 实现口径

- 输入：`06_RESEARCH/DATA/FUTURES/{BTCUSDT,ETHUSDT,SOLUSDT}_FUNDING_8H.csv`
- 分位：每个读数只与其此前 `[t-365d, t)` funding 读数比较；首年扩张窗口；少于 180 天历史标记 warmup，不参与事件判定。
- 分位算法：经验 midrank percentile，当前 t 和未来数据不进入窗口。
- 事件档位：负侧 P5/P2.5/P1，正侧 P95/P97.5/P99。
- episode 合并：同一 `symbol × side × tier` 下，相邻极端读数间隔 `<=24h` 合并，事件时间取首次触发。该边界与普查报告中“间隔 >24h 记为新事件，否则合并”的 324 锚点一致；任务测试要求的 23h/25h 用例不受影响。
- Holdout：全池化事件按 `event_time, symbol, side, tier` 稳定排序后，序号 `mod 5 == 4` 写入 Holdout，其余写入 work。Holdout 写完后未再读取内容。

## 事件计数

| side | tier | 全量事件 | Work | Holdout | 普查锚 | 说明 |
|---|---:|---:|---:|---:|---:|---|
| neg | P5 | 407 | 319 | 88 | 324 | Work 低于普查 5 个；全量高于普查，原因是滚动阈值在部分历史阶段比全样本阈值更宽，增加触发；Holdout 切分后工作集落入验收区间。 |
| neg | P2.5 | 264 | 218 | 46 | 182 | 滚动阈值导致全量高于普查；work 仍保留足够单调性样本。 |
| neg | P1 | 117 | 91 | 26 | 80 | 滚动阈值导致全量高于普查。 |
| pos | P95 | 117 | 91 | 26 | 172 | 低于普查，符合滚动分位减少正侧触发的方向。 |
| pos | P97.5 | 103 | 85 | 18 | 111 | 略低于普查。 |
| pos | P99 | 84 | 70 | 14 | 66 | 全量略高于普查，work 接近普查锚。 |

## Warmup 排除

| symbol | 排除读数 |
|---|---:|
| BTCUSDT | 540 |
| ETHUSDT | 540 |
| SOLUSDT | 540 |
| **合计** | **1620** |

## Holdout 切分

- 全量事件：1092
- Work：874
- Holdout：218
- Work/Holdout：4.009:1，符合约 4:1。

## 测试结果

命令：

```bash
pytest -q 06_RESEARCH/CODE/features/test_a2_features.py
```

结果：

```text
3 passed in 0.55s
```

覆盖：

- 无前视：人工构造 180 天历史 + 当前读数，验证 t 分位只由 t 之前数据决定，当前值变化会改变 t 自身分位，未来/当前不污染此前 warmup 状态。
- 合并规则：23h 间隔合并，25h 间隔开新事件。
- Holdout：确定性验证 `mod 5 == 4` 切分。

## 复算命令

```bash
python3 06_RESEARCH/CODE/features/a2_funding_features.py
pytest -q 06_RESEARCH/CODE/features/test_a2_features.py
```

## 验收自检

- pytest 全绿：通过。
- 无前视测试真实有效：通过，测试断言当前值不进入 prior window。
- 负侧 P5 工作集池化事件数 319：通过，位于 150~350。
- Work + Holdout 计数比约 4:1：通过，874:218 = 4.009:1。
- Holdout 文件存在且已写入：通过。
- 全 UTC：通过，输出 `event_time` 为 `YYYY-MM-DDTHH:MM:SSZ`。
- seed：不适用，无随机过程。
- 禁止项：未读取 MARK 文件；未改预登记；未引入第三方 TA/事件库；未做收益分析。
