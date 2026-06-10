# 结构信号量化定义规格

**文档编号：** SPEC-0A6  
**版本：** 1.0  
**作者：** Claude（CTO）  
**用途：** Codex 实现信号检测器的唯一语义依据，禁止 Codex 自行修改或扩展信号定义  
**关联任务：** TASK_0A6_SIGNAL_DETECTOR.md  

---

## 重要说明

本规格定义三个信号的精确判定条件。Codex 的职责是按规格实现，**不得自行定义信号语义**。如发现规格存在歧义或矛盾，必须在执行报告中注明，由 Claude 裁决后修改规格再重新实现。

---

## 一、Liquidity Sweep（流动性扫荡）

### 定义

价格短暂突破近期显著低点（扫荡下方流动性），但收盘价回到该低点上方。这代表「空头陷阱」——诱发止损后被主力接管。

### 精确判定条件（看涨版，Bullish Sweep）

```
参数：
  sweep_lookback = 20  # 向前查找多少根K线寻找参考低点

条件（在第 i 根K线上判断）：
  1. 参考低点：ref_low = min(low[i-sweep_lookback : i-1])
     （取当前K线之前20根K线中的最低收盘价，不含当前K线）
  
  2. 扫荡发生：low[i] < ref_low
     （当前K线的最低价低于参考低点）
  
  3. 收盘回位：close[i] > ref_low
     （当前K线的收盘价高于参考低点）
  
  4. 信号确认：条件1+2+3同时满足，记录为 Bullish Sweep，发生在第 i 根K线
```

### 边界情形处理

- 若 `i < sweep_lookback`，该K线不做判断（数据不足）
- ref_low 使用 `low` 价格序列（不是 close），取最低值

---

## 二、CHoCH（结构转变，Change of Character）

### 定义

价格突破近期下跌结构中的最近一个显著摆动高点，标志市场结构从空头转为多头。

### 精确判定条件（看涨版，Bullish CHoCH）

```
参数：
  swing_lookback = 10  # 向前查找摆动高点的窗口
  swing_n = 2          # 判定摆动高点所需的两侧确认K线数

步骤一：识别摆动高点（Swing High）
  一根K线 j 满足以下条件时，记为摆动高点：
    high[j] > high[j-1] AND high[j] > high[j-2]  （左侧2根K线更低）
    high[j] > high[j+1] AND high[j] > high[j+2]  （右侧2根K线更低）
  
步骤二：找参考摆动高点
  在当前K线 i 之前的 swing_lookback 根K线内（不含当前K线），
  取最近一个满足摆动高点定义的K线的 high 值，记为 ref_swing_high
  
  如果窗口内没有摆动高点，退而求其次：
  ref_swing_high = max(high[i-swing_lookback : i-1])

条件（在第 i 根K线上判断）：
  close[i] > ref_swing_high  →  记录为 Bullish CHoCH，发生在第 i 根K线
```

### 边界情形处理

- 若 `i < swing_lookback + swing_n`，该K线不做判断（数据不足）
- 摆动高点识别需要右侧确认，因此有 `swing_n` 根K线的滞后

---

## 三、FVG（公允价值缺口，Fair Value Gap）

### 定义

三根K线形成的价格缺口：第1根K线的最高价低于第3根K线的最低价，中间留下未被触及的价格区间。

### 精确判定条件（看涨版，Bullish FVG）

```
三根连续K线：bar[i-2], bar[i-1], bar[i]

条件：
  high[i-2] < low[i]   →  存在看涨 FVG
  
FVG 区间：
  fvg_low  = high[i-2]
  fvg_high = low[i]
  
记录为 Bullish FVG，位置在第 i-1 根K线（中间K线），
区间为 [fvg_low, fvg_high]
```

### 边界情形处理

- 若 `i < 2`，不做判断（数据不足）
- FVG 区间宽度 `fvg_high - fvg_low` 必须 > 0（若等于0则不是有效FVG）

---

## 四、三重确认信号（Triple Confirmation Entry Signal）

### 定义

三个信号按特定顺序在时间上串联出现，构成一次潜在入场机会。

### 精确判定条件

```
参数：
  sequence_window = 20  # 三个信号必须在此窗口内完成序列

序列要求（按顺序）：

步骤1：发生 Bullish Sweep，记录时间索引为 t_sweep

步骤2：在 t_sweep 之后的 sequence_window 根K线内（即 t_sweep < t_choch <= t_sweep + sequence_window），
       发生 Bullish CHoCH，记录时间索引为 t_choch

步骤3：在 t_sweep 到 t_choch 之间（含两端），存在至少一个 Bullish FVG
       记录最近一个FVG的区间为 [fvg_low, fvg_high]，时间索引为 t_fvg

步骤4：在 t_choch 之后的 sequence_window 根K线内，
       价格回撤进入FVG区间（即某根K线的 low <= fvg_high 且 close >= fvg_low）
       记录时间索引为 t_entry，这是入场K线

三重确认信号成立条件：
  t_sweep < t_fvg <= t_choch < t_entry <= t_choch + sequence_window

触发时记录：
  - signal_time: t_entry（入场K线时间）
  - sweep_time: t_sweep
  - choch_time: t_choch
  - fvg_zone: [fvg_low, fvg_high]
  - entry_price: 建议入场价 = fvg_high（FVG区间上沿）
  - stop_loss: ref_low（Sweep 时的参考低点，即扫荡低点）
  - risk_pct: (entry_price - stop_loss) / entry_price * 100
```

---

## 五、输出格式

检测器必须输出两种格式：

### 格式1：信号列表 CSV

文件名：`06_RESEARCH/CODE/output/triple_signals_BTCUSDT_4H.csv`

| 列名 | 说明 |
|------|------|
| signal_time | 入场K线时间（datetime格式）|
| sweep_time | Sweep K线时间 |
| choch_time | CHoCH K线时间 |
| fvg_low | FVG区间低点 |
| fvg_high | FVG区间高点 |
| entry_price | 建议入场价（fvg_high）|
| stop_loss | 止损价（sweep参考低点）|
| risk_pct | 止损幅度（%）|

### 格式2：摘要统计（打印到控制台）

```
=== 信号统计摘要 ===
数据范围：[起始日期] ~ [结束日期]
总K线数：[N]
Bullish Sweep 次数：[N]
Bullish CHoCH 次数：[N]
Bullish FVG 次数：[N]
三重确认信号次数：[N]
信号触发频率：[N]次 / [总年数]年 = 平均每年[N]次
```

---

*本规格由 Claude（CTO）定义，Codex 不得修改信号语义。如实现过程中发现规格问题，在执行报告中注明，等待 Claude 裁决。*
