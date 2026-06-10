# Codex 任务：波动率压缩因子分组分析

```xml
<task>
  <id>0B-14-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断，不计入失败计数</type>

  <context>
    两个独立来源均指向波动率压缩因子的价值：
    
    1. V4 项目历史发现（PC-09）：在所有V4评分因子中，波动率压缩是唯一通过
       IC分析的因子（BTC IC +0.0579，SOL IC +0.0816）。
    
    2. 外部调研（EXTERNAL_RESEARCH_v3）：ATR相对高度过滤器（只在低波动环境
       入场）在外部回测中使利润因子提升40%，在加密量化社区有广泛验证。
    
    逻辑：当市场处于"压缩状态"（近期波动率低于历史均值）时发生Sweep，
    随后的反转更有方向性，信号质量更高，止损被过早触发的概率更低。
    
    本任务：把425个事件按"入场前波动率是否压缩"分成两组，
    分别统计止损率、MAE、t+24收益，验证波动率压缩是否能提升信号质量。
    
    这是诊断任务，不运行新策略，直接分析现有事件数据。
  </context>

  <data_inputs>
    事件数据（已有）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv  ← 425个事件
    
    交易数据（已有）：
      06_RESEARCH/CODE/output/v4_strategy_trades.csv  ← 360笔交易
    
    价格数据（需要计算ATR）：
      06_RESEARCH/DATA/BTCUSDT_4H.csv
      06_RESEARCH/DATA/ETHUSDT_4H.csv
      06_RESEARCH/DATA/SOLUSDT_4H.csv
  </data_inputs>

  <volatility_compression_definition>
    定义：在Sweep K线入场时，当前ATR（14周期）< ATR的50根均线（即近期波动率
    低于历史中期均值），则认为处于"压缩状态"。
    
    具体计算：
      current_atr = ATR(14) 在入场K线时的值
      atr_ma50 = current_atr 的50根移动平均（即前50根K线ATR的均值）
      压缩组：current_atr < atr_ma50
      非压缩组：current_atr >= atr_ma50
    
    备选定义（同时计算，供比较）：
      current_atr < atr_ma50 × 0.8  ← 更严格的压缩定义
  </volatility_compression_definition>

  <required_analysis>
    一、分组统计
      对425个事件按压缩/非压缩分组后：
        - 各组事件数量
        - 各组 t+6/t+12/t+24 平均收益（与v4整体对比）
        - 各组 t+24 p值（统计显著性是否保持）
    
    二、止损率对比（基于 v4_strategy_trades.csv）
      把每笔v4交易关联到其对应事件，判断该事件是否属于压缩组：
        - 压缩组交易止损率 vs 非压缩组交易止损率
        - 压缩组交易平均持仓K线数 vs 非压缩组
        - 压缩组 Expectancy vs 非压缩组
    
    三、关键问题回答
      如果压缩组止损率显著低于非压缩组（如 <50% vs >65%）：
        → 波动率压缩过滤有实质价值，建议纳入下一策略版本预登记
      如果两组止损率接近：
        → 波动率压缩对我们的止损问题无帮助，不纳入
    
    四、可视化
      - 压缩组 vs 非压缩组 t+24 收益分布箱线图
      - 止损率对比柱状图（按品种+压缩状态分层）
  </required_analysis>

  <outputs>
    <file>06_RESEARCH/CODE/v14_vol_compression_analysis.py</file>
    <file>06_RESEARCH/RESULTS/20260606_vol_compression_analysis.md</file>
    <file>06_RESEARCH/CODE/output/vol_compression_charts.png</file>
    <file>06_RESEARCH/CODE/output/vol_compression_metrics.json</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B14_VOL_COMPRESSION.md</file>
  </outputs>

  <acceptance>
    <item>两种压缩定义均已计算（ATR<MA50 和 ATR<MA50×0.8）</item>
    <item>压缩组 vs 非压缩组的 t+6/12/24 均值和p值对比</item>
    <item>止损率对比（压缩组 vs 非压缩组）</item>
    <item>明确结论：波动率压缩过滤是否值得纳入策略</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止运行新策略回测（本任务只分析现有数据）</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 压缩组事件数 vs 非压缩组事件数
    2. 压缩组 t+24 均值和p值 vs 整体（v4：+2.34%，p<0.000001）
    3. 压缩组止损率 vs 非压缩组止损率
    4. 压缩组 Expectancy vs 非压缩组 Expectancy
    5. 结论：是否建议将波动率压缩纳入下一版本策略过滤条件？
  </report_to_claude>
</task>
```
