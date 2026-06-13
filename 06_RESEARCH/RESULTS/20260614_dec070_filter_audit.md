# DEC-070 过滤器可审计性审计（35 候选资产）
**执行：** Codex｜**日期：** 2026-06-14｜**数据：** FUTURES_EXPANDED 4H klines（cutoff<2024-12-10）

**[专业异议]** 任务书假设本地 CSV 含 `quote_volume`，但 35/35 文件实际只有 `datetime,open,high,low,close,volume`。下载脚本从 Binance 原始 12 列中只保留了 OHLCV，且 `volume` 是基币量。因此精确 quote-volume ADTV 不能由当前落盘文件复原；本报告计算透明的 `HLC3 × base volume` USDT 名义成交额代理，并同时给出 `low × volume` / `high × volume` 边界，不把代理冒充精确 quote volume。

第二个定义缺口是 `float_market_cap_ratio` 未冻结分母：`market_cap/FDV`、`circulating_supply/total_supply` 与 `circulating_supply/max_supply` 并非总是等价。本任务只记录缺口，不替 DEC-070 修改定义。

## 摘要：4 过滤器可审计性
| 过滤器 | 本地可算? | 结论 |
| --- | --- | --- |
| ADTV | 部分 | HLC3 名义成交额代理可算；精确 quote volume 缺列，35/35 未精确验证 |
| price_jump_frequency | 是 | 连续 4H close-to-close 对数收益可精确复算 |
| float_market_cap_ratio | 否 | 缺历史 supply/mcap/FDV，且比率分母尚未冻结 |
| oi_market_cap_ratio | 否 | 缺历史 OI 与对齐市值；Binance REST 仅保留最近 1 个月 |

基于两个本地指标的**部分证据**：Tier 1-clean 20/35，Tier 1-watch 10/35，排除 5/35。其中 ADTV 是有价格边界的代理，不是精确 quote-volume 证明。

## 第一部分：ADTV + price_jump_frequency
### 公式与冻结口径
- 数据边界：只用 `datetime < 2024-12-10 00:00:00 UTC`；最近 180 日固定为 `2024-06-13` 至 `2024-12-09`（含首尾）。
- 日成交额代理：`Q_d^proxy = Σ volume_t × (high_t + low_t + close_t) / 3`。只纳入含 `00/04/08/12/16/20 UTC` 六根 K 线的完整日。
- 可行边界：每根 bar 的真实 VWAP 必在 `[low, high]`，故 `Σ volume×low ≤ 当日真实 quote volume ≤ Σ volume×high`。35 个资产的上下界与代理均落在同一 ADTV 档位。
- ADTV 建议门槛：最近 180 日中位数 `≥10m USDT/day` 为达标，`5m-10m` 为边缘，`<5m` 为不达标。其含义是 10,000 USDT 订单在门槛处约占中位日成交额 0.10%；这是容量初筛，不替代盘口冲击模型。
- 跳动：`r_t = ln(close_t/close_{t-1})`，仅统计时间戳严格相差 4H 的连续 bar；`jump(J)=1(|r_t|>J)`，频率为异常次数/有效连续收益数。
- 跳动建议门槛：主阈值 `J=15%`；频率 `≤0.20%` 达标，`0.20%-0.30%` 边缘，`>0.30%` 不达标。按每年约 2,190 根 4H bar，0.20%/0.30% 分别约为每年 4.4/6.6 次异常。
- 上述均为本审计提出并写死在脚本常量中的绝对建议门槛，不是 DEC-070 已预登记数值；未使用 35 资产的全样本分位数。

### 每资产数值表
| 资产 | 全样本日成交额中位数* | 最近180d* | ADTV | jump 10% | jump 15% | jump | jump 20% | 分层 |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: | --- |
| AAVEUSDT | 93.68m | 128.31m | 达标 | 67/9094 (0.7367%) | 8/9094 (0.0880%) | 达标 | 2/9094 (0.0220%) | Tier 1-clean |
| ALGOUSDT | 43.93m | 14.91m | 达标 | 68/9825 (0.6921%) | 8/9825 (0.0814%) | 达标 | 1/9825 (0.0102%) | Tier 1-clean |
| ATOMUSDT | 91.84m | 52.95m | 达标 | 66/10604 (0.6224%) | 12/10604 (0.1132%) | 达标 | 3/10604 (0.0283%) | Tier 1-clean |
| AVAXUSDT | 241.52m | 217.96m | 达标 | 72/9232 (0.7799%) | 14/9232 (0.1516%) | 达标 | 5/9232 (0.0542%) | Tier 1-clean |
| AXSUSDT | 81.40m | 22.91m | 达标 | 118/8884 (1.3282%) | 28/8884 (0.3152%) | 不达标 | 8/8884 (0.0900%) | exclude |
| COMPUSDT | 32.38m | 12.31m | 达标 | 65/9741 (0.6673%) | 11/9741 (0.1129%) | 达标 | 2/9741 (0.0205%) | Tier 1-clean |
| CRVUSDT | 99.94m | 114.12m | 达标 | 133/9364 (1.4203%) | 24/9364 (0.2563%) | 边缘 | 8/9364 (0.0854%) | Tier 1-watch |
| DASHUSDT | 18.54m | 5.43m | 边缘 | 47/10623 (0.4424%) | 8/10623 (0.0753%) | 达标 | 3/10623 (0.0282%) | Tier 1-watch |
| DOTUSDT | 214.33m | 102.63m | 达标 | 46/9424 (0.4881%) | 11/9424 (0.1167%) | 达标 | 2/9424 (0.0212%) | Tier 1-clean |
| EGLDUSDT | 33.22m | 10.14m | 达标 | 50/9286 (0.5384%) | 12/9286 (0.1292%) | 达标 | 3/9286 (0.0323%) | Tier 1-clean |
| ENJUSDT | 28.67m | 6.99m | 边缘 | 98/9196 (1.0657%) | 18/9196 (0.1957%) | 达标 | 3/9196 (0.0326%) | Tier 1-watch |
| ETCUSDT | 138.87m | 65.72m | 达标 | 75/10737 (0.6985%) | 14/10737 (0.1304%) | 达标 | 4/10737 (0.0373%) | Tier 1-clean |
| FILUSDT | 158.04m | 126.88m | 达标 | 68/9062 (0.7504%) | 16/9062 (0.1766%) | 达标 | 4/9062 (0.0441%) | Tier 1-clean |
| FTMUSDT | 152.68m | 164.93m | 达标 | 146/9194 (1.5880%) | 40/9194 (0.4351%) | 不达标 | 11/9194 (0.1196%) | exclude |
| ICXUSDT | 13.54m | 4.18m | 不达标 | 78/9280 (0.8405%) | 15/9280 (0.1616%) | 达标 | 4/9280 (0.0431%) | exclude |
| KNCUSDT | 21.97m | 5.17m | 边缘 | 69/9757 (0.7072%) | 9/9757 (0.0922%) | 达标 | 1/9757 (0.0102%) | Tier 1-watch |
| KSMUSDT | 21.69m | 6.89m | 边缘 | 72/9074 (0.7935%) | 17/9074 (0.1873%) | 达标 | 4/9074 (0.0441%) | Tier 1-watch |
| LINKUSDT | 259.99m | 146.53m | 达标 | 47/10731 (0.4380%) | 9/10731 (0.0839%) | 达标 | 2/10731 (0.0186%) | Tier 1-clean |
| LRCUSDT | 19.12m | 5.76m | 边缘 | 116/9044 (1.2826%) | 27/9044 (0.2985%) | 边缘 | 8/9044 (0.0885%) | Tier 1-watch |
| MKRUSDT | 37.91m | 52.36m | 达标 | 54/9446 (0.5717%) | 10/9446 (0.1059%) | 达标 | 3/9446 (0.0318%) | Tier 1-clean |
| NEARUSDT | 144.94m | 148.18m | 达标 | 79/9067 (0.8713%) | 14/9067 (0.1544%) | 达标 | 5/9067 (0.0551%) | Tier 1-clean |
| OMGUSDT | 22.11m | 5.52m | 边缘 | 96/9697 (0.9900%) | 30/9697 (0.3094%) | 不达标 | 9/9697 (0.0928%) | exclude |
| RENUSDT | 19.61m | 4.81m | 不达标 | 94/9112 (1.0316%) | 28/9112 (0.3073%) | 不达标 | 7/9112 (0.0768%) | exclude |
| RUNEUSDT | 67.04m | 55.70m | 达标 | 116/9346 (1.2412%) | 15/9346 (0.1605%) | 达标 | 2/9346 (0.0214%) | Tier 1-clean |
| SNXUSDT | 36.19m | 12.73m | 达标 | 96/9472 (1.0135%) | 12/9472 (0.1267%) | 达标 | 4/9472 (0.0422%) | Tier 1-clean |
| SUSHIUSDT | 67.54m | 14.29m | 达标 | 122/9314 (1.3099%) | 23/9314 (0.2469%) | 边缘 | 9/9314 (0.0966%) | Tier 1-watch |
| THETAUSDT | 45.33m | 23.92m | 达标 | 67/9945 (0.6737%) | 11/9945 (0.1106%) | 达标 | 3/9945 (0.0302%) | Tier 1-clean |
| TRXUSDT | 64.31m | 65.53m | 达标 | 49/10711 (0.4575%) | 11/10711 (0.1027%) | 达标 | 3/10711 (0.0280%) | Tier 1-clean |
| UNIUSDT | 87.82m | 84.10m | 达标 | 61/9262 (0.6586%) | 12/9262 (0.1296%) | 达标 | 4/9262 (0.0432%) | Tier 1-clean |
| XLMUSDT | 41.46m | 23.93m | 达标 | 55/10681 (0.5149%) | 13/10681 (0.1217%) | 达标 | 6/10681 (0.0562%) | Tier 1-clean |
| XMRUSDT | 31.07m | 13.42m | 达标 | 39/10629 (0.3669%) | 7/10629 (0.0659%) | 达标 | 2/10629 (0.0188%) | Tier 1-clean |
| XTZUSDT | 34.97m | 8.32m | 边缘 | 51/10611 (0.4806%) | 9/10611 (0.0848%) | 达标 | 4/10611 (0.0377%) | Tier 1-watch |
| YFIUSDT | 34.70m | 6.70m | 边缘 | 74/9338 (0.7925%) | 14/9338 (0.1499%) | 达标 | 4/9338 (0.0428%) | Tier 1-watch |
| ZECUSDT | 32.23m | 27.27m | 达标 | 64/10585 (0.6046%) | 16/10585 (0.1512%) | 达标 | 3/10585 (0.0283%) | Tier 1-clean |
| ZRXUSDT | 17.83m | 8.95m | 边缘 | 91/9777 (0.9308%) | 25/9777 (0.2557%) | 边缘 | 7/9777 (0.0716%) | Tier 1-watch |

\* 成交额列均为 `HLC3 × base volume` 代理。逐资产 lower/upper 边界、输入 SHA-256、完整日数量与时间缺口见 `06_RESEARCH/CODE/output/dec070_filter_audit.json`。

### 数据质量事实
- 35/35 文件均覆盖到 `2024-12-09 20:00 UTC`，最近 180 日各有 180 个完整 UTC 日。
- 13 个资产在 2022 年存在 2 个跨日历缺口；跳动分母已排除跨缺口收益，完整日 ADTV 聚合也不会把缺失整日当作零成交。
- ADTV 代理状态：达标 24，边缘 9，不达标 2；jump15 状态：达标 27，边缘 4，不达标 4。

## 第二部分：外部数据缺口（float_mcap_ratio / oi_mcap_ratio）
### float_market_cap_ratio
- **当前不可计算。** 本地 K 线没有 circulating supply、total/max supply、market cap 或 FDV，也没有可靠的交易对到资产 ID 映射。
- **定义必须先冻结。** 最小可审计定义候选是 `circulating market cap / FDV`；若 DEC-070 意图不同，必须明确分母和无 max-supply 资产的处理规则。
- **最小外部源：** [CoinGecko Coin Historical Data](https://docs.coingecko.com/reference/coins-id-history)，并结合其 circulating/total supply 历史端点；CMC 或同等级历史基本面库可替代。
- **估计成本：** 35 个资产 ID 映射、cutoff 对齐、缺失值核对与原始响应归档约 1-3 工程日；历史 supply 端点/吞吐可能需要付费 API。未在本任务下载。

### oi_market_cap_ratio
- **当前历史不可计算。** 需要同一时点的 OI notional、circulating market cap，以及 Binance 单场所或全场所聚合规则。
- [Binance Open Interest Statistics](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics) 官方限制为最近 1 个月；在 2026-06-14 无法从该 REST 端点追回 2020-2024 历史。
- **可行路径：** 采购/取得可信的历史 OI 归档后，与同频市值快照按 UTC 对齐；预计 2-5 工程日，另加数据供应商费用。任何归档都需先核对字段定义、复权/换币及缺口。
- **替代代理：** `近端 OI notional / 近端 ADTV` 可监控拥挤度，但不等价于历史 `OI / market cap`，不能据此把该过滤器标成已通过。

### 外部参考与本地 schema 证据
- [Binance Public Data kline schema](https://github.com/binance/binance-public-data) 列出 base volume 与 quote asset volume 为两个独立字段；本地 CSV 只保留前者。
- [CoinGecko historical endpoint](https://docs.coingecko.com/reference/coins-id-history) 可作为历史市值/供给采集入口，实际字段覆盖需在后续数据任务逐资产验收。

## 第三部分：基于2个本地指标的分层（部分证据）
分层规则：任一指标不达标即“排除”；两项都达标为 `Tier 1-clean`；无不达标但至少一项边缘为 `Tier 1-watch`。`N.A.` 不强行归类。

**Tier 1-clean（20）：** AAVEUSDT, ALGOUSDT, ATOMUSDT, AVAXUSDT, COMPUSDT, DOTUSDT, EGLDUSDT, ETCUSDT, FILUSDT, LINKUSDT, MKRUSDT, NEARUSDT, RUNEUSDT, SNXUSDT, THETAUSDT, TRXUSDT, UNIUSDT, XLMUSDT, XMRUSDT, ZECUSDT

**Tier 1-watch（10）：**
- CRVUSDT: ADTV代理=达标, jump15=边缘
- DASHUSDT: ADTV代理=边缘, jump15=达标
- ENJUSDT: ADTV代理=边缘, jump15=达标
- KNCUSDT: ADTV代理=边缘, jump15=达标
- KSMUSDT: ADTV代理=边缘, jump15=达标
- LRCUSDT: ADTV代理=边缘, jump15=边缘
- SUSHIUSDT: ADTV代理=达标, jump15=边缘
- XTZUSDT: ADTV代理=边缘, jump15=达标
- YFIUSDT: ADTV代理=边缘, jump15=达标
- ZRXUSDT: ADTV代理=边缘, jump15=边缘

**排除（5）：**
- AXSUSDT: ADTV代理=达标, jump15=不达标
- FTMUSDT: ADTV代理=达标, jump15=不达标
- ICXUSDT: ADTV代理=不达标, jump15=达标
- OMGUSDT: ADTV代理=边缘, jump15=不达标
- RENUSDT: ADTV代理=不达标, jump15=不达标

**边界声明：** 该分层只使用本地可复算的价格跳动和成交额代理。`float_market_cap_ratio`、`oi_market_cap_ratio` 均未验证，且 ADTV 缺精确 quote volume；因此它是部分证据，不构成 universe 最终确认，也不解除 D 级决策责任。

## 给主理人的一句话事实结论（不下D级结论）
按冻结的本地代理门槛，20/35 为 clean、10/35 为 watch、5/35 因低成交额代理或高跳动而排除；但 35/35 缺精确 quote volume，float/OI 两项也无本地历史数据，故当前证据不能证明任何资产已通过 DEC-070 四项硬过滤。
