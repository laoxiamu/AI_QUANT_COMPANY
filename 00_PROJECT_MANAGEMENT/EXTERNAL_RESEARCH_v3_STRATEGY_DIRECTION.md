# EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md

**版本：** 1.0  
**撰写时间：** 2026-06-06  
**撰写者：** Claude（CTO）  
**目的：** 针对当前核心矛盾（信号真实但策略失败）的外部调研，为下一步方向提供外部视角依据  
**触发背景：** 连续失败计数6/8，核心矛盾为「紧止损 vs 长持仓周期不可兼得」，MaxDD 37.63% 超过门槛 25%

---

## 核心问题（调研前明确）

我们面临的核心矛盾是：
- 信号统计上真实（Bootstrap p=0.0003，t+24均值+2.34%）
- 止损中位触发在第1根K线，80%在t+6（24小时）前发生
- 最优持仓期t+24（96小时）但 MaxDD 37.63% 超标
- 六种策略变体全部失败

---

## 方向1：Liquidity Sweep / Smart Money Concepts 量化研究

### 核心发现

**发现1.1：SMC量化回测存在系统性"后验幻觉"问题**  
来源：[Smart Money Concepts (ICT): The Institutional Trading Strategy Explained](https://strategyarena.io/blog/smart-money-concepts-ict-strategie) | [ICT SMC Entry Models: Critical Smart Money Guide | AlgoStorm](https://algostorm.com/ict-smc-entry-models/)

ICT方法论的最大缺陷：回测时你已经知道哪个 swing point 是"真正的"支撑、哪个 sweep 是"真正的"流动性抓取、哪个 FVG 是入场点——但在实时交易中这些都不明确。这制造了一种"回测幻觉"，使 ICT 看起来比实际更有效。"valid displacement"和"clean sweeps"等概念高度主观，**从根本上难以系统化回测**。

**对我们的启发：** 我们的信号定义（Bullish Liquidity Sweep：价格扫穿近期低点后快速反转收回）已经做了关键一步——将主观判断转为可量化的价格结构规则。这是一个明确的竞争优势。但需要持续警惕：信号定义是否在事后优化中引入了过拟合？

**发现1.2：系统化回测结果远低于ICT宣称的70-80%胜率**  
来源：[I Backtested 2,600 Trades Using Smart Money Concepts — Here's What Actually Works](https://medium.com/@space.garaa/i-backtested-2-600-trades-using-smart-money-concepts-heres-what-actually-works-bb3c671098c6)

10个资产、26个月（2024年1月~2026年3月）的2600笔交易系统回测显示：实际胜率**61%**，利润因子**2.17**，平均+2.27R。普通零售策略通常45-55%胜率、利润因子<1.5。**SMC框架整体优于普通零售策略，但并非ICT宣称的70-80%。**

**对我们的启发：** 我们的事件研究三层校验通过是可信的正面信号。但61%胜率、2.17利润因子是在**多重过滤+良好风控**下实现的，而我们目前58.33%的止损率（即约42%胜率）表明风控部分（止损设计）是主要拖累，而非信号本身。

**发现1.3：需要多层确认才能达到60-70%精度**  
来源：[Liquidity Sweep in Trading Explained: Definition, Mechanics, Identification, and Trading Strategies](https://xbtfx.com/article/liquidity-sweeps-in-trading-explained)

单独使用 wick（影线）时失败率约50%；加入结构转换（structure shift）确认后，在趋势市场中精度可达60-70%。**单一 sweep 事件不够，必须结合多层过滤。**

**对我们的启发：** 我们的双层Regime过滤（EMA200多头 + BTC 30日动量）是正确方向。问题不在信号质量，在于止损设计无法让信号的统计优势得以发挥。

---

## 方向2：止损设计与持仓生存率

### 核心发现

**发现2.1：MAE分析是止损优化的行业标准方法**  
来源：[Maximum Adverse Excursion (MAE): The Data Behind Your Stop Loss Placement](https://nexusfi.com/a/risk-management/maximum-adverse-excursion-mae) | [Max Adverse Excursion (MAE): Where Your Stops Should Sit](https://docs.tradingmetrics.com/en/technical-analysis/trading-metrics/trade-specific-metrics/max-adverse-excursion)

MAE（最大逆向偏移）由 John Sweeney 在1996年形式化，**核心原则：止损应设在80%胜利交易的MAE价格处**。如果止损在MAE区域内部（即比80%的盈利交易的最大逆势运动还紧），你将在「方向正确但时机稍早」时被震出。

**对我们的启发：** 这直接对应我们的诊断——止损中位在第1根K线触发，正是因为止损（Sweep低点）太靠近入场价，落入了大量正常噪声区间内。**我们需要立即运行MAE分析**：统计360笔交易中，盈利交易的最大逆势运动分布，找到覆盖80%盈利交易的MAE位置，这就是理论上的止损应设位置。

**发现2.2：加密货币需要3.5-4x ATR的止损空间**  
来源：[ATR vs Structure: How to Set Stop Losses in Futures Trading](https://justintrading.com/atr-vs-structure-stop-losses-futures/) | [ATR Stop Loss Strategy For Crypto Trading](https://flipster.io/blog/atr-stop-loss-strategy)

加密货币的极端日内波动（极端wick）需要比传统市场更宽的止损。建议在加密市场使用3.5-4x ATR作为止损乘数。**ATR止损 vs 结构止损的最优方案**：先按结构设置止损位，再确保该止损位距入场价至少1-1.5x ATR，两者取更远者。

**对我们的启发：** 我们的 Sweep 低点止损（ref_low 或 sweep_low）是纯结构止损，没有考虑ATR动态调整。在高波动期间，Sweep 低点距入场价可能极小，根本无法容纳正常噪声。建议测试：`stop = max(sweep_low, entry - 2×ATR)`，即两者取更保守的一个。

**发现2.3：止损太紧是量化策略最常见的失败模式**  
来源：[📉 Maximum Adverse Excursion (MAE) — The Key to Better Stop Placement](https://www.mql5.com/en/blogs/post/765746)

"如果你的止损在MAE区域内部，即便你的方向判断是正确的，你也会被止损出局。"这种情况下，增加信号质量无法解决问题，因为根本原因是风控设置，而非信号识别。

**对我们的启发：** 这精确描述了我们的困境——事件研究证明信号方向是对的（t+24均值+2.34%），但策略在达到这个窗口前就被止损扫出。这不是信号失败，是止损放置失败。

---

## 方向3：时间退出策略（Time Exit）

### 核心发现

**发现3.1：事件驱动策略随持仓期延长普遍出现性能衰减**  
来源：[Janus-Q: End-to-End Event-Driven Trading via Hierarchical-Gated Reward Modeling](https://arxiv.org/pdf/2602.19919)

最新学术研究（2026年2月）明确指出：随着持仓窗口增大，大多数事件驱动模型表现出明显的性能衰减。一个在1天持仓期表现为正收益的模型，到第3天可能转为负收益，Sharpe Ratio 跌破-1.5。**衰减原因：持仓时间越长，不相关的市场波动累积越多，信号的信噪比下降。**

**对我们的启发（批判性解读）：** 这个研究结论与我们的发现表面上矛盾——我们的t+24（4H周期的24根K线=4个日历天）是最优点。但注意：这篇论文的"day 1/day 3"可能是指日线，而我们的t+24是4H周期。实际上，我们的t+24=4日历天，与论文"day 3后衰减"基本吻合。这意味着我们的t+24可能已经是边际最优，继续增大持仓期（t+36, t+48）会更差。

**发现3.2：567,000次回测揭示的退出策略规律**  
来源：[What 567,000 Backtests Taught Me About Algo Trading Exits](https://kjtradingsystems.com/algo-trading-exits.html)

大规模回测研究发现：在持有时间缩短的同时，降低敞口往往比追求更高利润目标更能提升风险调整后收益。策略**更少时间在市场中暴露**往往意味着更好的Sharpe。这支持了时间止损（time stop）的概念价值：不能让不确定的持仓无限拖延。

**对我们的启发：** 纯时间退出（t+24无止损）的诊断实验是合理的下一步——它可以揭示在**没有止损干扰**时，信号的Sharpe上限和MaxDD是多少，确认是否值得继续寻找更好的止损方案。

**发现3.3：Triple Barrier Method 是处理持仓-止损矛盾的学术主流方案**  
来源：[Stop-Loss, Take-Profit, Triple-Barrier & Time-Exit: Advanced Strategies for Backtesting](https://medium.com/@jpolec_72972/stop-loss-take-profit-triple-barrier-time-exit-advanced-strategies-for-backtesting-8b51836ec5a2) | [Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning](https://link.springer.com/article/10.1186/s40854-025-00866-w)

Triple Barrier Method（出自 Marcos Lopez de Prado《金融机器学习进阶》）：同时设置上方止盈、下方止损、时间止损三道屏障，价格先触碰哪道就退出。这个方法的关键优势：**时间屏障作为兜底**，防止持仓在趋势反转后继续承担不必要风险。局限：固定参数门槛在市场环境切换时适应性差。

**对我们的启发：** 这正是我们尚未测试的方向——不设固定止盈，改用「止损保护 + 时间止损 + 浮盈回撤」三重机制。注意：我们的 V4 历史设计（PC-11）已经提出了类似的七状态机方案，与Triple Barrier高度一致。这是一个值得在失败次数恢复前优先测试的方向。

---

## 方向4：波动率压缩因子作为信号过滤器

### 核心发现

**发现4.1：ATR相对高度过滤器使利润因子提升40%**  
来源：[Using Strategy Filters (Time of Day, Volatility) to Enhance Backtest Performance and Robustness](https://quantstrategy.io/blog/blog/using-strategy-filters-time-of-day-volatility-to-enhance/)

使用ATR过滤器（仅在14周期ATR > ATR的50周期均值时激活策略）确保市场处于"足够波动能维持突破"的状态。**回测证实此过滤器使利润因子提升40%，因为它排除了波动压缩/区间震荡期间的错误入场。**

**对我们的启发：** 这是V4唯一通过IC分析的因子（BTC IC +0.0579，SOL IC +0.0816）的外部验证。波动率压缩过滤器的作用不是判断方向，而是**判断是否处于"信号有效的环境"**。我们当前双层Regime过滤（EMA200 + BTC动量）是方向过滤，波动率压缩是质量过滤，两者不互斥，可以叠加。

**发现4.2：TTM Squeeze连续3根K线在压缩状态才触发，降低假信号**  
来源：[Volatility Compression Momentum Breakout Tracking Strategy: Quantitative Implementation of TTM Squeeze Indicator](https://medium.com/@FMZQuant/volatility-compression-momentum-breakout-tracking-strategy-quantitative-implementation-of-ttm-dfe0232ccf51) | [TTM Squeeze Indicator: Setup, Signals, and Trading Rules](https://volatilitybox.com/research/ttm-squeeze-indicator/)

TTM Squeeze（布林带收窄至肯特纳通道内部）检测波动压缩。**要求连续3根K线处于压缩状态后再触发信号，可有效过滤"假压缩"，减少错误信号。**

**对我们的启发：** 我们目前没有在信号前置条件中加入波动率状态判断。如果 Sweep 发生在一个已经处于高波动扩张阶段（而非压缩释放阶段），其统计意义可能下降。可以测试：将V4的波动压缩因子作为第三层过滤条件，检验其在当前信号框架下的有效性。

**发现4.3：波动率压缩对做空方向的信号改善可能不对称**  
来源：[Volatility Compression: Why This Breakout Pattern Beats the Market 63% of the Time](https://www.stockdataanalytics.com/blog/volatility-compression-stock-breakout-pattern/)

波动率压缩突破在股票市场的系统回测显示63%的胜率（基于股票市场研究，非加密）。但关键发现：**压缩后的突破方向具有较强的趋势延续性，这对多头（顺势突破后Sweep反转）比对空头更有利。**

**对我们的启发：** 这部分解释了为什么我们的做空镜像信号（v5）失败——Bearish Sweep（向上扫穿高点后反转）在波动率压缩框架下并不天然符合方向，因为压缩后的向上突破更多是真正的方向性突破，而非流动性抓取。

---

## 方向5：加密货币2022熊市的系统性处理

### 核心发现

**发现5.1：2022年是极端Fear Regime，现有过滤器普遍失效**  
来源：[The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets](https://arxiv.org/pdf/2602.07018) | [Trading Games: Beating Passive Strategies in the Bullish Crypto Market](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.70018)

2022年整年处于93%的Fear Regime（极度恐惧57% + 恐惧36%），与2021年和2023-2024年完全不同的市场环境。**这是一个结构性的市场体制切换，而非正常的趋势周期。** 同期主要加密货币相关性超过0.90，BTC跌10%时大多数山寨币跌15-25%。

**对我们的启发：** 这解释了为什么我们的第三层Regime过滤对2022年无效（v7结论：WF第二段p=0.1251无改善）——2022年不是一个可以通过添加过滤器来"避开"的正常熊市区间，而是一个整体性的系统崩溃期。任何依赖历史数据的过滤器在2022都难以有效区分信号。

**发现5.2：EMA200过滤器在2022-2023盘整期有效性显著下降**  
来源：[Share: Crypto Universe Trend Following w/EMA Crossovers](https://www.quantconnect.com/forum/discussion/12949/share-crypto-universe-trend-following-w-ema-crossovers)

QuantConnect平台的实测：9/21 EMA穿越系统在BTC日线的2018-2024年测试中54%胜率、MaxDD 34%；但仅在2022-2025年（利率上升+盘整周期）测试时，胜率降至49%，基本接近随机。**同一系统在趋势牛市中有效，在2022风格的熊市中无效。**

**对我们的启发（重要）：** 我们的双层Regime过滤（EMA200多头 + BTC 30日动量）在2022年内本应大幅过滤入场机会，但我们的数据显示2022年事件数并未大幅减少（v7 2022年事件：12个）。这意味着EMA200过滤器在2022确实减少了信号，但剩余的12个信号仍然表现很差（2022年10/11笔止损，全部在t+6前触发）。这印证了2022是系统性风险，不可通过更多过滤解决。

**发现5.3：2022类极端事件的处理：减少总敞口而非改进信号**  
来源：[The Role of Risk Management in Surviving Crypto Bear Markets](https://medium.com/@laostjen/the-role-of-risk-management-in-surviving-crypto-bear-markets-11fbc43b954f)

学术研究和实战经验均显示：在2022风格的崩溃期，**关键不是信号质量，而是仓位大小**。LSTM多智能体模型通过主动将配置从高相关加密资产转移出来，实现了显著更浅的MaxDD，而非依赖更好的入场信号。

**对我们的启发：** 我们面临的2022问题，可能最终只有一个解决方案：**降低2022期间的仓位敞口**（如固定小仓位），或者接受2022是系统适用范围外的市场环境（明确标注不适用区间），而不是继续尝试通过信号过滤器来消除2022的亏损。

---

## 方向6：延迟入场（Confirmation Entry）

### 核心发现

**发现6.1：加入趋势对齐过滤可使胜率提升22%**  
来源：[How I Improved My Backtest Win Rate by 22% with This Visual Trick (Built in Pine Script)](https://medium.com/@betashorts1998/how-i-improved-my-backtest-win-rate-by-22-with-this-visual-trick-built-in-pine-script-bbd10365288d)

一个实测案例：通过添加基于趋势对齐的上下文过滤（context filter），回测胜率提升22%。但关键警告：**提升胜率往往降低了利润因子**，因为更严格的过滤减少了高回报机会的参与。

**对我们的启发：** 这里存在一个权衡——如果通过等待确认K线（下一根K线收盘确认方向）来提升胜率，可能减少交易次数，也可能错失部分最快速的利润行情。在我们样本量本已偏少（315次）的情况下，进一步减少信号数量需要谨慎。

**发现6.2：多时框架入场：高时框做方向，低时框精确入场**  
来源：[Quantitative Trading Explained: Strategy Design, Backtesting & Optimization](https://www.quantvps.com/blog/guide-to-quantitative-trading-strategies-and-backtesting)

专业量化策略普遍采用：**日线图判断方向 + 小时线精确入场**，结合高时框的稳定性和低时框的精确性。例如，只在日线RSI > 50时才做多，但用1小时线的看涨信号入场。

**对我们的启发：** 我们已经在用日线EMA200做Regime过滤，但入场使用4H收盘价。一个值得测试的变体是：在4H Sweep信号确认后，等待1H级别的ChoCH（结构转变）或FVG确认再入场，可能减少"第1根K线止损"的发生率——因为入场时机更精确，不再是Sweep K线收盘即入场。

**发现6.3：Freqtrade/回测框架中延迟入场默认在下一根K线开盘价执行**  
来源：[Backtesting - Freqtrade](https://www.freqtrade.io/en/stable/backtesting/)

行业标准回测框架的做法：信号在t收盘产生，在t+1开盘价执行入场，这是避免前视偏差（lookahead bias）的标准做法。我们当前已经是这样处理的（信号K线收盘时入场），符合规范。

**对我们的启发：** 确认入场（Confirmation Entry）相对于我们当前的实现是额外一根K线的延迟，即等到t+1收盘确认方向后在t+2开盘价入场。这会进一步延迟入场，可能改善止损被触发的比例（因为入场时市场已展示了更多意图），但也会降低每笔交易的期望利润。

---

## 方向7：加密货币做空策略设计

### 核心发现

**发现7.1：市场中性统计套利在加密市场实现Sharpe 2.1+，但不依赖方向判断**  
来源：[A 2+ Sharpe Market-Neutral Statistical Arbitrage Strategy in Cryptocurrency](https://medium.com/@luitingronald.us/a-2-sharpe-market-neutral-statistical-arbitrage-strategy-in-cryptocurrency-0f0b7728cf1e)

基于ETH/SOL、ETH/ADA、ETH/DOT价格比值的统计套利：当比值偏离历史均值2个标准差时建仓，做多低估资产、做空高估资产。12个月回测：18.5%收益，Sharpe 2.1。**关键：这是市场中性的，2022年同样有效。**

**对我们的启发：** 这提供了一个完全不同的思路——与其继续在单品种方向性做空上挣扎，不如考虑跨品种的相对价值策略。但这需要完全不同的信号体系，超出了当前阶段范围。

**发现7.2：资金费率套利：零方向判断，最大亏损仅1.92%**  
来源：[Market Neutral Crypto Trading: Hedge Fund Strategies Guide](https://deliberatedirections.com/market-neutral-crypto-trading-strategies/)

2025年学术研究：60个资金费率套利场景（BTC/ETH/XRP/BNB/SOL），6个月最高回报115.9%，最大亏损仅1.92%。**资金费率套利完全回避了方向判断问题。**

**对我们的启发：** 这是一个在我们解决当前核心矛盾之前，可以并行研究的低风险策略方向。但它的Alpha来源与信号真实性研究完全不同，属于不同的研究路线。

**发现7.3：Bearish Liquidity Sweep做空的方向性本质问题**  
来源：[Liquidity Sweeps: A Complete Guide to Smart Money Manipulation!](https://www.tradingview.com/chart/BTCUSDT.P/xMPbR4ug-Ultimate-Guide-to-Liquidity-Sweeps-Trading-Smart-Money-Moves/)

Bearish Sweep（价格上扫高点→快速回落）与Bullish Sweep（价格下扫低点→快速反弹）在市场结构上是**非对称**的——在牛市中，价格向上突破高点更多是真正的方向性突破，而非流动性抓取。这解释了为什么做空镜像信号（v5）在除2022年外的时期都无效。

**对我们的启发：** v5 FAILED的根本原因被外部研究进一步印证：Bearish Sweep的市场语义本质上是牛市中的"最后一跌后快速上涨"的镜像——在熊市中才有价值，但熊市的定义本身就排除了大多数可用的测试区间。双向信号的对称性假设在加密市场不成立。

---

## 外部视角发现了什么我们可能忽略的问题

### 忽略点1：我们从未做过MAE分析
这是止损优化的行业标准工具，已有360笔历史trades.csv数据，但我们没有运行MAE统计。MAE分析可以直接回答「我们的止损应该放在哪里才不会在方向正确时被震出」。**这是最大的遗漏，且成本极低（对现有数据做一次统计）。**

### 忽略点2：我们没有用ATR动态化止损
所有6次失败测试都在用固定结构止损（sweep_low 或 ref_low），没有考虑市场当时的波动率水平。在高ATR时期，Sweep K线本身可能就有很大振幅，固定使用Sweep低点作为止损等于在波动最大时止损最紧，完全逆向。

### 忽略点3：我们对2022的处理策略是"找更好的过滤器"，而外部研究表明应该是"调整仓位敞口"
我们通过7次信号迭代（包括第三层Regime）尝试过滤掉2022的亏损，但外部研究表明2022是结构性极端事件，**添加过滤器无法系统性解决，降低仓位才是正确处理方式**。这是范式级别的方向差异。

### 忽略点4：我们在信号质量通过校验后应该转向「退出机制设计」，而非继续做信号迭代
外部研究（SMC回测分析、Triple Barrier法、MAE工具）一致指向：当信号有统计优势时，**决定盈利能力的是退出机制，而非信号本身**。我们已经在用事件研究确认了信号，但随后的策略测试仍然在调整信号参数（第三层Regime过滤、做空镜像），而不是深入研究退出设计。

### 忽略点5：波动率压缩因子（V4唯一通过IC分析的因子）一直未被重新验证
自V4的历史IC分析之后，我们从未在V5框架下重新验证波动率压缩是否仍然有效。这个因子在历史上是有价值的，但被当作已知结论而非待验证的假设。

---

## 综合建议：下一步最值得测试的方向

基于7个方向的外部调研，结合我们当前核心矛盾和失败计数（6/8），以下是按优先级排序的建议：

### 建议A（最高优先级）：运行MAE分析诊断止损应设位置
**类型：** 诊断性分析，不计入失败计数  
**操作：** 对现有360笔 trades.csv，计算每笔盈利交易的MAE（入场后最大逆势运动），统计分布，找到覆盖80%盈利交易的MAE水平。  
**预期输出：** 一个数字：「80%的盈利交易最大逆势运动为 X%」，这就是理论上止损应放的位置。  
**价值：** 如果X% > 当前平均止损距离，则可量化证明止损过紧。如果X%意味着MaxDD仍然超标，则可提前判断这个方向无法解决核心矛盾。  
**成本：** 一次Python脚本对已有数据的统计，约1-2小时工作量。

### 建议B（高优先级）：测试ATR动态止损
**类型：** 策略变体，计入失败计数  
**逻辑：** `stop = max(sweep_low - ε, entry - 2×ATR_14)`，即在结构止损和ATR动态止损两者中取更保守的一个。ATR在高波动期自动扩大止损空间，在低波动期使用结构止损。  
**预期改善：** 减少「第1根K线止损」触发率，让信号的t+24统计优势有更大概率得以发挥。  
**建议在MAE分析后执行：** 用MAE分析结果校准ATR乘数（目标是让止损覆盖80%盈利交易的MAE区间）。

### 建议C（中优先级，在A/B完成后评估）：接受2022是适用边界，调整敞口而非过滤信号
**类型：** 规则变更，需要Founder级确认（D级决策）  
**内容：** 在2022类极端熊市期（定义方式TBD，例如BTC月度回撤 > 20%持续3个月以上），将每笔交易仓位降至标准仓位的25%，或完全暂停信号执行。  
**价值：** 放弃"通过更好过滤器消灭2022"的思路，改为"接受2022是系统不适用环境，用仓位管理控制损失"。  
**注意：** 2022年BTC+ETH+SOL仅12个Regime合规事件，即便全部止损，在25%仓位下整体影响也会显著降低。

---

## 附：搜索来源汇总

1. [I Backtested 2,600 Trades Using Smart Money Concepts](https://medium.com/@space.garaa/i-backtested-2-600-trades-using-smart-money-concepts-heres-what-actually-works-bb3c671098c6)
2. [ICT SMC Entry Models: Critical Smart Money Guide | AlgoStorm](https://algostorm.com/ict-smc-entry-models/)
3. [Maximum Adverse Excursion (MAE): The Data Behind Your Stop Loss Placement](https://nexusfi.com/a/risk-management/maximum-adverse-excursion-mae)
4. [Max Adverse Excursion (MAE): Where Your Stops Should Sit](https://docs.tradingmetrics.com/en/technical-analysis/trading-metrics/trade-specific-metrics/max-adverse-excursion)
5. [ATR vs Structure: How to Set Stop Losses in Futures Trading](https://justintrading.com/atr-vs-structure-stop-losses-futures/)
6. [ATR Stop Loss Strategy For Crypto Trading](https://flipster.io/blog/atr-stop-loss-strategy)
7. [Stop-Loss, Take-Profit, Triple-Barrier & Time-Exit: Advanced Strategies for Backtesting](https://medium.com/@jpolec_72972/stop-loss-take-profit-triple-barrier-time-exit-advanced-strategies-for-backtesting-8b51836ec5a2)
8. [Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning](https://link.springer.com/article/10.1186/s40854-025-00866-w)
9. [Janus-Q: End-to-End Event-Driven Trading](https://arxiv.org/pdf/2602.19919)
10. [What 567,000 Backtests Taught Me About Algo Trading Exits](https://kjtradingsystems.com/algo-trading-exits.html)
11. [Using Strategy Filters to Enhance Backtest Performance](https://quantstrategy.io/blog/blog/using-strategy-filters-time-of-day-volatility-to-enhance/)
12. [Volatility Compression Momentum Breakout Tracking Strategy](https://medium.com/@FMZQuant/volatility-compression-momentum-breakout-tracking-strategy-quantitative-implementation-of-ttm-dfe0232ccf51)
13. [TTM Squeeze Indicator](https://volatilitybox.com/research/ttm-squeeze-indicator/)
14. [The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets](https://arxiv.org/pdf/2602.07018)
15. [Trading Games: Beating Passive Strategies in the Bullish Crypto Market](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.70018)
16. [Share: Crypto Universe Trend Following w/EMA Crossovers](https://www.quantconnect.com/forum/discussion/12949/share-crypto-universe-trend-following-w-ema-crossovers)
17. [A 2+ Sharpe Market-Neutral Statistical Arbitrage Strategy in Cryptocurrency](https://medium.com/@luitingronald.us/a-2-sharpe-market-neutral-statistical-arbitrage-strategy-in-cryptocurrency-0f0b7728cf1e)
18. [Market Neutral Crypto Trading: Hedge Fund Strategies Guide](https://deliberatedirections.com/market-neutral-crypto-trading-strategies/)
19. [Deep Asia–London Session Liquidity Study (NQ, 17-Year Analysis)](https://www.hermantrading.pro/backtest-library/meditation-for-creative-block-guided-zwe47-23wcs)
20. [📉 Maximum Adverse Excursion (MAE) — The Key to Better Stop Placement](https://www.mql5.com/en/blogs/post/765746)

---

## 文件记录

**下一步行动：** 建议A（MAE分析）为当前最高优先级诊断任务，可立即安排 Codex 执行  
**决策需要：** 建议C（仓位调整）需要 Founder 级确认（D级决策）  
**失败计数影响：** 建议A/C不计入失败计数；建议B计入  

【等待Founder确认】——是否批准建议A（MAE分析）优先于运行「t+24无止损诊断」？
