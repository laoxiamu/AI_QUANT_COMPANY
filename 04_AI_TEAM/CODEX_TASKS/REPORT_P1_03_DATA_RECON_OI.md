# REPORT-P1-03 持仓量/清算数据可得性核查

**执行日期：** 2026-06-06  
**任务书：** `TASK_P1_03_DATA_RECON_OI.md`  
**状态：** COMPLETED  
**性质：** 纯数据核查，未做收益或预测力分析

## 结论

**OI 微结构方向具备数据前提，可以进入正式信号设计与预登记。**

- OI、Top Trader LSR、Global LSR、Taker Ratio 均可从 Binance 官方公共
  Futures metrics 日归档获得。
- BTC 从 2020-09-01 起；ETH/SOL 从 2021-12-01 起；最新归档日为
  2026-06-05，末条时间为 2026-06-06 00:00:00。
- 三品种合计约 155.4 万条 5 分钟观测。
- OI 两列完整无空值；LSR/taker 存在间歇缺失。
- 官方公共仓库未发现历史清算归档，第一版信号不得依赖 liquidation。

## 数据总览

| 品种 | 归档起点 | 归档终点 | 5m 行数 | 理论覆盖率 | >6分钟真缺口 |
|---|---|---|---:|---:|---:|
| BTCUSDT | 2020-09-01 | 2026-06-05 | 605,318 | 99.895% | 160 |
| ETHUSDT | 2021-12-01 | 2026-06-05 | 474,484 | 99.971% | 14 |
| SOLUSDT | 2021-12-01 | 2026-06-05 | 474,467 | 99.967% | 18 |

大量“非精确 5 分钟”间隔是原始时间戳 ±数秒抖动，不等于缺失；上表单列
真正超过 6 分钟的间隔。三个文件的 OI 列均无空值。

## 字段

所有品种字段一致：

| 字段 | 含义 |
|---|---|
| `sum_open_interest` | 合约数量口径 OI |
| `sum_open_interest_value` | 名义价值口径 OI |
| `count_toptrader_long_short_ratio` | Top Trader 账户数多空比 |
| `sum_toptrader_long_short_ratio` | Top Trader 持仓量多空比 |
| `count_long_short_ratio` | 全市场账户数多空比 |
| `sum_taker_long_short_vol_ratio` | 主动买卖成交量比 |

## 有效观测

### BTCUSDT

| 数据 | 5m 有效行 | 有效日 | 4H 有效观测 |
|---|---:|---:|---:|
| OI / OI value | 605,318 | 2,105 | 12,623 |
| Top Trader LSR | 513,092–513,126 | 1,790 | 10,709 |
| Global LSR | 599,521 | 2,086 | 12,504 |
| Taker Ratio | 568,047 | 1,977 | 11,849 |

### ETHUSDT

| 数据 | 5m 有效行 | 有效日 | 4H 有效观测 |
|---|---:|---:|---:|
| OI / OI value | 474,484 | 1,649 | 9,887 |
| Top Trader LSR | 382,265–382,303 | 1,334 | 7,973 |
| Global LSR | 468,695 | 1,630 | 9,768 |
| Taker Ratio | 437,237 | 1,521 | 9,113 |

### SOLUSDT

| 数据 | 5m 有效行 | 有效日 | 4H 有效观测 |
|---|---:|---:|---:|
| OI / OI value | 474,467 | 1,649 | 9,887 |
| Top Trader LSR | 382,250–382,286 | 1,334 | 7,973 |
| Global LSR | 468,677 | 1,630 | 9,768 |
| Taker Ratio | 437,217 | 1,521 | 9,113 |

所有字段的原始及 4H 有效观测均远超 DEC-018 数量门槛。但时间序列高度
自相关，不能把每个 5 分钟点当作独立事件；未来预登记仍须定义事件去重和
有效样本口径。

## 牛熊覆盖

- BTC：覆盖完整 2021 牛市与 2022 熊市。
- ETH/SOL：从 2021-12-01 起，不覆盖完整 2021 牛市，但覆盖完整 2022
  熊市及 2023–2026 多种环境。
- 三品种共同主样本应从 2021-12-01 开始；若使用 BTC 更长历史作为补充，
  必须预先定义为单品种机制诊断，不能与共同样本混用后择优汇报。

## 清算数据

Binance 官方公共归档的常见历史路径 `liquidationSnapshot` 与
`forceOrders` 均无文件，metrics 字段中也不包含清算量。交易 API 在当前
环境不可达，且实时/近端接口不能替代多年历史归档。

**结论：历史 liquidation 对本项目当前官方数据约束下不可得。** 不使用
非授权第三方爬取，也不以合成清算数据替代。

## 数据产物

- `06_RESEARCH/DATA/FUTURES/BTCUSDT_METRICS_5M.csv`（约 56MB）
- `06_RESEARCH/DATA/FUTURES/ETHUSDT_METRICS_5M.csv`（约 45MB）
- `06_RESEARCH/DATA/FUTURES/SOLUSDT_METRICS_5M.csv`（约 45MB）
- `06_RESEARCH/CODE/p1_03_data_recon_oi.py`
- `06_RESEARCH/CODE/output/p1_03_data_recon_oi.json`

## Claude 待处理事项

1. 将 P1-03 标记为完成：OI 微结构数据前置通过。
2. 下一独立 Alpha 可以进入预登记，但第一版建议以无缺失的
   `sum_open_interest_value` 或 `sum_open_interest` 为核心。
3. LSR/taker 只能作为预先声明缺失处理规则的辅助变量，不建议第一版同时
   堆入多个字段，避免变量混杂。
4. liquidation 从第一版假设中删除，不再等待或寻找非官方历史数据。
5. 主实验共同起点固定为 2021-12-01；BTC 2020-09 至 2021-11 只能作为
   预先定义的单品种补充诊断。
6. 在消耗独立 Alpha 第 6 次槽位前，先做不看收益的事件样本量前置：
   明确定义 OI 异常事件、去重窗口、方向语义和各 Regime 覆盖。
7. 不要直接把 155 万行当成 155 万独立样本；须按事件或低频重采样后重新
   对照 DEC-018。
8. Codex 未修改 Memory Core 或项目管理文件。

【需要Claude】
