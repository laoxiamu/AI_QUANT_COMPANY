# Codex 任务：ATR 动态止损诊断

```xml
<task>
  <id>0B-15-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断，不计入失败计数</type>

  <context>
    外部调研（EXTERNAL_RESEARCH_v3）：加密量化领域主流建议是 3-4倍ATR 作为止损距离，
    而非固定结构止损。理由：市场波动率动态变化，高波动期固定止损反而更紧，
    导致正常波动也会触发止损。
    
    我们当前使用 sweep_low 作为止损（平均距离约2.33%），这在高波动期可能
    只有 0.5-1倍ATR，远远不够。
    
    本诊断任务：不运行新策略，直接分析现有 360 笔 v4 交易数据：
    在每笔交易入场时，如果用 2/3/4倍ATR 而非 sweep_low 做止损，
    止损率会从现在的 58.33% 降到多少？这对 Expectancy 有什么影响？
    
    重要：ATR止损更宽意味着止损R值更大，但仓位按比例缩小（保持风险金额不变）。
    需要同时计算"相同风险预算下"的收益影响。
  </context>

  <data_inputs>
    交易数据（已有）：
      06_RESEARCH/CODE/output/v4_strategy_trades.csv  ← 360笔交易
    
    价格数据（计算ATR）：
      06_RESEARCH/DATA/BTCUSDT_4H.csv
      06_RESEARCH/DATA/ETHUSDT_4H.csv
      06_RESEARCH/DATA/SOLUSDT_4H.csv
    
    参考：
      06_RESEARCH/CODE/v12_mae_analysis.py  ← 若0B12先完成，可复用ATR计算逻辑
  </data_inputs>

  <required_analysis>
    一、计算每笔交易入场时的 ATR
      对 v4 的 360 笔交易，在入场 K 线时计算 ATR(14)。
      ATR止损位置：
        - 2×ATR止损：entry_price - 2 × atr
        - 3×ATR止损：entry_price - 3 × atr
        - 4×ATR止损：entry_price - 4 × atr
      
      对比当前止损：sweep_low（从 trades CSV 中的实际止损触发价反推，
      或从价格数据和信号数据重新计算）
    
    二、止损率变化模拟
      对每笔交易，使用价格数据模拟：如果止损改为 2/3/4×ATR，
      在原始持仓期内，这笔交易是否还会被止损？
      
      输出：
        | 止损方式 | 止损率 | 平均触发时机（K线数）| t+6前触发比例 |
        |---------|--------|---------------------|--------------|
        | 当前sweep_low | 58.33% | 第1根（中位） | 80% |
        | 2×ATR | ? | ? | ? |
        | 3×ATR | ? | ? | ? |
        | 4×ATR | ? | ? | ? |
    
    三、Expectancy 估算（重要：考虑仓位缩放）
      ATR止损更宽 → 止损R值更大 → 保持风险金额不变则仓位更小。
      
      对每个ATR倍数，估算调整后的 Expectancy：
        新止损R = ATR × N / entry_price（以R计）
        调整仓位 = 原仓位 × (当前止损R / 新止损R)
        新Expectancy = 新止损率 × (-新止损R) + (1-新止损率) × 盈利交易平均R
    
    四、2022年单独分析
      2022年的11笔v4交易，ATR止损能否降低止损率？
      （0B9显示2022年10/11笔止损，全在t+6前触发）
  </required_analysis>

  <outputs>
    <file>06_RESEARCH/CODE/v15_atr_stop_diagnostic.py</file>
    <file>06_RESEARCH/RESULTS/20260606_atr_stop_diagnostic.md</file>
    <file>06_RESEARCH/CODE/output/atr_stop_diagnostic_charts.png</file>
    <file>06_RESEARCH/CODE/output/atr_stop_diagnostic_metrics.json</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B15_ATR_STOP_DIAGNOSTIC.md</file>
  </outputs>

  <acceptance>
    <item>三个ATR倍数（2/3/4×）的止损率均已计算</item>
    <item>考虑仓位缩放后的 Expectancy 估算</item>
    <item>当前sweep_low止损 vs ATR止损的完整对比表</item>
    <item>2022年单独分析</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止运行完整策略回测（本任务只做模拟分析）</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 各ATR倍数的止损率（2×/3×/4×）
    2. t+6前触发比例的变化
    3. 考虑仓位缩放后，哪个ATR倍数的Expectancy最优？
    4. 3×ATR版本能否把止损率降到50%以下？
    5. 结论：ATR止损是否值得作为下一个策略版本的止损方式？
  </report_to_claude>
</task>
```
