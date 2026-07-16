# P0-RES-038-B1-PHASEA 报告

**[专业异议]** 任务书要求用 `LIQUIDATIONS + FUTURES_EXPANDED` 计算强平簇后 1-4 根 4H 毛漂移，但本地核验后该 join 不成立：`LIQUIDATIONS` 覆盖 2026-06-15 到 2026-06-21，`FUTURES_EXPANDED` 只到 2024-12-09，且字段只有 OHLCV、无 OI/funding。强平簇只能完成可得性与规模描述，不能合法给漂移分布；若强行补价或外拉数据会违反本任务“只用已落地免费/本地数据”。

执行脚本：`06_RESEARCH/CODE/p0res038_phasea_free_data_audit.py`  
输出 JSON：`06_RESEARCH/CODE/output/p0res038_phasea_free_data_audit.json`  
纪律声明：未读取 `HOLDOUT/`、未回测、未调参、未做方向择优；描述统计只作毛效应上限与 B1 冻结建议，不作显著性或方向结论。

## A. 机制红队反审 B0 卡

### A1. 机制真伪裁决

| 子机制 | 裁决 | 理由 |
|---|---:|---|
| 强平簇 | ACCEPT-with-MODIFY | payer 真实、机械、非自愿。强制平仓/ADL 的交易不是价值判断，理论上最硬。但 Binance 免费流是 1000ms 内每币只推最大一条的下界样本，不能把观测 notional 当全量强平。 |
| OI 重置 | ACCEPT-with-MODIFY | 杠杆去化/追保减仓有机械性，但 OI 下降本身没有多空方向，必须另行、预先定义方向。它比强平簇软，容易混入主动降杠杆、换仓、跨所迁移。 |
| funding 极端 | ACCEPT-with-MODIFY | DEC-089 放行作触发器是合理的，但它最弱、最容易退化成“拥挤行为软驱动”或 funding carry 换皮。必须用价格 PnL 与 funding cashflow 拆账坐实“不吃票息”。 |
| taker 失衡 | ACCEPT-with-MODIFY | 激进 taker 支付 spread/impact 真实，但不必然非自愿；也可能是信息交易者主动跨价。若没有 L2/tick 真值与成本模型，最容易重演 v1 OFI 的成本门死亡。 |

最弱项：funding 极端。它从“资金费压力导致被迫出清”到“拥挤仓位反转”之间有一层行为假设，最容易滑回 #X2 式软驱动；taker 失衡次弱，因为 payer 可能是 informed taker。

### A2. 成本门裁决

§3 的 70/110/210bp 在自身假设“费 5bp/边 + 滑点 30/50/100bp/边”下算术正确：往返分别为 70/110/210bp。  
但 AGENTS.md 铁律写明手续费 0.1%/边，即 10bp/边；按项目硬纪律，应同时或优先报告 80/120/220bp。建议 B1 把 70/110/210bp 作为乐观交易费口径，把 80/120/220bp 作为纪律硬口径，除非 Claude 明确覆写手续费假设。

强制清算类要求高档 E[R]>0 不过严；在级联态使用 210/220bp 才是最低门槛。真正风险是“毛漂移看似大，但可成交净边际被滑点、逆向选择、截断数据误判吃光”。分钟级最容易被全成本吃掉的是 taker 失衡/OFI；其次是 funding 极端触发，因为如果 price impulse 不够快，信号会变成低频拥挤 proxy。

### A3. 防换皮四门

| 门 | 裁决 | 漏洞与修正 |
|---|---:|---|
| 反 A-1 单一方向冻结 | ACCEPT-with-MODIFY | 方向冻结必须在 B1 预登记前完成；阶段 A 只能给方向先验，不能用“延续/耗尽两边都测，择优进 B2”。 |
| 反 Sweep 价格白名单 | ACCEPT-with-MODIFY | 白名单基本正确。漏洞在 maker 救活敏感带：若挂单价位由结构位/突破/插针决定，就是 Sweep 复活；只能由流变量决定。 |
| 反清算数据旧伤 | ACCEPT | 当前审计再次确认旧伤仍在：Binance forceOrder 是截断下界，单源不能进 B2。必须有第二免费源方向一致或转被动攒数。 |
| 反 DEC-084 funding 票息边界 | ACCEPT-with-MODIFY | 需要操作化：收益拆成 price PnL、fee/slippage、funding cashflow；B1/B2 结果以 funding cashflow 置零或剔除后为准；默认不跨 funding settlement 持仓，若跨越则必须扣除并单列。 |

funding 约束可被绕过的方式：用 funding 极端入场，持仓穿越结算点，然后把票息混在总 PnL 里说成价格收益。防绕过做法是逐笔 ledger 拆账、报告 ex-funding PnL、对跨结算交易单列敏感性；若 edge 依赖 funding cashflow，直接回 DEC-084 禁区。

### A4. 诚实基线与死亡概率先验

免费数据版最可能死在两道门：第一是强平路径的“单源截断 + 无本地价格重叠”；第二是 B1 净期望成本门，尤其 210/220bp 高档。我的先验：

| 子机制 | 阶段 A/B1 死亡概率先验 | 主要死因 |
|---|---:|---|
| 强平簇 | 85% | 免费 Binance 流是下界样本，且本轮无合法 drift join；需等第二源或新价格面板。 |
| OI 重置 | 65% | 毛漂移上限存在，但方向性可能很弱，净 E[R] 可能过不了成本门/MDE。 |
| funding 极端 | 80% | 最容易被判 carry/拥挤换皮；需严格 ex-funding 归因。 |
| taker 失衡 | 90% | 免费数据不足以还原 L2/MLOFI 与可成交成本，v1 OFI 死法风险最高。 |

全军覆没先验：75%。若只能选一个进 B1，选 OI 重置；强平簇本轮不应进 B1 实算，只能转被动攒数或等 Tardis/Coinalyze/Hyperliquid 可用样本补齐。

## B. 阶段 A 免费数据可得性审计 + 初步描述统计

### B1. 已落地本地数据审计

| 数据源 | 真实可得 | 字段/跨度 | 结论 |
|---|---:|---|---|
| `06_RESEARCH/DATA/LIQUIDATIONS/` | 7 个 JSONL，245,614 行 | 2026-06-15 00:38:31Z 到 2026-06-21 16:47:08Z；672 symbols；字段含 `E, recv_ts, o.s/o.S/o.q/o.ap/o.z/o.T` | 可做强平规模下界审计；不可单源当全量。Binance 官方说明 `!forceOrder@arr` 每 symbol 每 1000ms 只推最大一条。 |
| `06_RESEARCH/DATA/FUTURES_EXPANDED/` | 35 个 4H CSV，339,206 行 | 2020-01-15 到 2024-12-09；字段仅 `datetime, open, high, low, close, volume` | 可做历史 4H OHLCV 面板；无 OI/funding；与本地强平流无时间重叠。 |
| `06_RESEARCH/DATA/FUTURES/` 本地辅助 | BTC/ETH/SOL OI metrics：BTC 605,319 行，ETH 474,485 行，SOL 474,468 行 | BTC 2020-09-01 到 2026-06-06；ETH/SOL 2021-12-01 到 2026-06-06；字段含 `sum_open_interest` | 这是本轮 OI reset 唯一可用的本地 OI 源；不是 `FUTURES_EXPANDED`。 |

未混用 `08_DATA/carry/spot_1h`；脚本和输出中无该路径。

### B2. 免费外部源 schema/额度边界核实

| 源 | 核实结果 | 阶段 A 评价 |
|---|---|---|
| Coinalyze | 官方 API 需要 API key，40 calls/min；intraday 历史只保留约 1500-2000 datapoints；liquidation history 返回 `t/l/s`，支持 1min 到 daily interval。来源：https://api.coinalyze.net/v1/doc/ | 可做 1-2 月级聚合强平/OI/funding 快筛；不适合直接替代事件级真值。 |
| Tardis.dev | 官方文档说明 CSV tick 数据含 liquidations、trades、book 等；每月第一天历史数据可无 API key 下载；CSV 时间为 UTC epoch microseconds。来源：https://docs.tardis.dev/downloadable-csv-files/overview 和 `/data-types` | 适合拿月初样本校准 Binance 截断偏差，但不是多周全量免费源。 |
| Hyperliquid | 官方 info endpoint 有 public mids/L2/candles 等；time range 响应需分页，candle 最近 5000 根；IP REST 权重 1200/min，`l2Book` 等权重 2。来源：https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint 和 rate limits | 可审 L2/candle schema；本轮未核到“公开历史清算全量”端点，不能把它计作强平第二源。 |

文献核实：
- arXiv:2102.04591 真实存在，题为 *Liquidation, Leverage and Optimal Margin in Bitcoin Futures Markets*；支撑“强平/杠杆/保证金压力真实存在”，不直接支撑本策略 edge。
- arXiv:1907.06230 真实存在，题为 *Multi-Level Order-Flow Imbalance in a Limit Order Book*；支撑 MLOFI 作为订单簿流变量定义，不支撑免费 perp OFI 可交易。
- arXiv:2603.15963 真实存在，题为 *Risk-Based Auto-Deleveraging*；支撑 ADL 是规则化去杠杆机制，不支撑具体交易信号。

### B3. 强平簇描述统计

可算内容：强平规模下界。不可算内容：事件后 1-4 根 4H 漂移。

强平按 `symbol × side × 4H` 聚合后共 24,088 个簇：

| 指标 | 数值 |
|---|---:|
| 4H 簇 notional p50 | 821 USDT |
| p75 | 5,324 USDT |
| p90 | 25,707 USDT |
| p95 | 74,689 USDT |
| max | 42,977,207 USDT |
| size bucket `<1k / 1k-10k / 10k-100k / 100k-1m / >=1m` | 12,630 / 7,212 / 3,271 / 843 / 132 |

Top notional symbols：ETHUSDT 257.2M、BTCUSDT 194.3M、SPCXUSDT 54.9M、SOLUSDT 38.9M、ETHUSDC 23.9M。

裁决：强平簇本轮不能给毛漂移上限，因 `FUTURES_EXPANDED` 无重叠。不得据此进 B1 实算；应转“被动攒数/补第二源”。

### B4. OI 重置描述统计

定义：用本地 Binance metrics 5m 重采样为 4H，固定 OI 24h 跌幅档：2-5%、5-10%、>=10%。方向中立：用触发前 24h 价格方向定义“延续”，其相反为“耗尽/反转”，两侧同时报告，不择优。

事件数：8,434 个固定档事件；BTC 3,070、SOL 2,911、ETH 2,453。分档：2-5% 跌幅 5,492；5-10% 跌幅 2,313；>=10% 跌幅 629。

绝对毛漂移分布（bp，log return 绝对值）：

| OI 24h 跌幅档 | 1x4H p90/p95 | 2x4H p90/p95 | 3x4H p90/p95 | 4x4H p90/p95 |
|---|---:|---:|---:|---:|
| 2-5% | 231 / 315 | 341 / 467 | 417 / 569 | 484 / 649 |
| 5-10% | 279 / 383 | 382 / 527 | 478 / 640 | 551 / 731 |
| >=10% | 392 / 526 | 496 / 646 | 592 / 758 | 666 / 886 |

单调性初判：绝对毛漂移 p90 在 1x/2x/3x/4x 4H 窗口均随 OI 跌幅档加深而上升。该结论只是描述统计，不是净 edge。

方向中立中位数（bp）：各档各窗口中，延续侧 p50 为负，耗尽/反转侧 p50 为正，但幅度很小。例如 >=10% 跌幅档：1x4H 耗尽 p50 15bp，4x4H 耗尽 p50 43bp；这远低于 70/110/210bp 成本门，不能作方向结论。

成本门并列：

| 口径 | 低 | 中 | 高/级联 |
|---|---:|---:|---:|
| B0 乐观费率 | 70bp | 110bp | 210bp |
| AGENTS 铁律费率修正 | 80bp | 120bp | 220bp |
| OI reset 最大 p95 绝对毛漂移 | 886bp | 886bp | 886bp |
| OI reset 方向中位数 | 约 3-43bp | 约 3-43bp | 约 3-43bp |

解释：OI reset 有“波动/毛漂移上限”足以进入 B1 的 cheap falsification，但方向性很可能弱；B1 必须用冻结方向、完整成本、MDE、bootstrap 爆仓概率与分年正期望裁决，不能把 p95 绝对漂移当 edge。

## 建议落点

推荐 B1 冻结：**OI 重置 + 耗尽/反转方向**。

理由：强平簇本轮无合法漂移 join，taker 失衡缺 L2/tick 成本真值，funding 极端 carry 边界最危险；OI reset 是唯一已落地本地数据能算、且固定跌幅档绝对毛漂移单调的子机制。方向建议只作为 B1 预登记先验：机制上“杠杆骤降后强迫流耗尽”比“继续同向追价”更贴近 payer-flow；本轮描述统计中耗尽侧中位数为正但幅度小，不构成方向结论。

若 Claude 认为方向中位数过小不足以立项，则替代建议是：不进 B1，全部回墓园/转被动攒数，重点补强平第二源与 2026-06-15 之后 4H mark price 面板。

## 验收自检

- A/B 两节已写。
- 已核真实文件存在与字段，未写死不存在路径。
- 已核 Coinalyze/Tardis/Hyperliquid schema 与免费边界，未大规模拉取。
- 已核三篇 arXiv 编号真实存在，并限制其支撑范围。
- 已同时报告延续与耗尽，不择优。
- 已把毛效应上限与 70/110/210bp 成本门、80/120/220bp 修正口径并列。
- 未触碰 Holdout，未回测，未调参，未耗独立计数。
