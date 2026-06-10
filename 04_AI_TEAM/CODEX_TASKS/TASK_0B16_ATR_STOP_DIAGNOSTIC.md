# Codex 任务：ATR 动态止损诊断

```xml
<task>
  <id>0B-16-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断分析，不计入失败计数</type>

  <context>
    外部研究结论（EXTERNAL_RESEARCH_v3 方向2）：
      加密货币建议止损距离为 3.5-4x ATR(14)
      最优方案：max(结构止损, entry - N×ATR)，两者取更远者
    
    V4历史（PC-11）：
      结构止损方案（swing low + 0.5×ATR）从未在V5中测试过。
    
    当前问题：
      所有策略变体均使用固定结构止损（sweep_low 或 ref_low）。
      这两种止损在高波动期间（如2022）比ATR止损更紧，导致90.91%止损率。
      ATR止损会随市场波动自动变宽，理论上可以避免"第1根K线被止损"的问题。
    
    本任务是诊断，不是策略回测：
      对v4的425个事件，计算入场时的ATR值，
      对比三种止损的距离分布：sweep_low、ref_low、ATR×3.5。
      回答：ATR止损是否比结构止损更宽（特别在2022年）？
            如果用ATR止损，有多少比例的"第1根K线被止损"会消失？
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <methodology>
    数据：v4的425个事件（events_v5_sweep_regime_bull_v4.csv）
    
    计算三种止损距离（每个事件）：
    
    1. sweep_low止损距离：
       (entry_price - sweep_low) / entry_price × 100%
       entry_price = 信号后下一根K线开盘价
       sweep_low = t_sweep K线的最低价
    
    2. ref_low止损距离：
       (entry_price - ref_low) / entry_price × 100%
       ref_low = min(low[t_sweep-20 : t_sweep-1])
    
    3. ATR×3.5止损距离：
       ATR(14)[t_sweep] × 3.5 / entry_price × 100%
       ATR使用标准True Range计算，14周期
       注意：ATR使用入场时刻的值，避免前视偏差
    
    4. ATR×3.5与ref_low的复合止损：
       max(ref_low距离, ATR×3.5距离)
       即两者取更宽的一个
    
    分析维度：
    一、四种止损距离的描述统计（均值/中位数/分位数/分布直方图）
    二、各止损类型"比上一类更宽"的比例
        有多少事件中 ATR×3.5 > ref_low > sweep_low？
    三、按时期分层：2022年四种止损距离对比
        2022年的高波动是否导致ATR止损更宽？
    四、理论止损率估算：
        从0B9的止损诊断中已知止损触发在第N根K线。
        对每个被止损的交易，计算如果用ATR×3.5止损，
        该止损价格是否比实际逆向运动的最低点更低（即是否能"撑过去"）？
    五、与MAE分析的对比（如0B14已完成）：
        ATR×3.5止损距离是否覆盖了盈利交易MAE的80th percentile？
  </methodology>

  <data_inputs>
    v4事件文件：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    4H OHLCV价格数据（计算ATR和止损价格）
    0B9 trades数据（如有止损事件的价格路径）：
      06_RESEARCH/CODE/output/v4_stop_diagnostic_metrics.json
    参考：0B14 MAE结果（若已完成可引用，若未完成则独立分析）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v16_atr_stop_diagnostic.py</file>
    <file>06_RESEARCH/RESULTS/20260606_atr_stop_diagnostic.md</file>
    <file>06_RESEARCH/CODE/output/atr_vs_structure_stop_charts.png</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B16_ATR_STOP_DIAGNOSTIC.md</file>
  </outputs>

  <required_output_table>
    | 止损类型 | 平均距离 | 中位数 | 80th pct | 比上类更宽比例 |
    |----------|--------:|------:|--------:|-------------:|
    | sweep_low | ~2.33% | ? | ? | 基准 |
    | ref_low | ~1.37% | ? | ? | ?% 更窄（已知）|
    | ATR×3.5 | ? | ? | ? | ?% 更宽于ref_low |
    | max(ref_low, ATR×3.5）| ? | ? | ? | ?% 更宽于ref_low |
    
    2022年单独对比表：
    | 止损类型 | 2022平均距离 | vs 全局均值 |
    |----------|------------:|----------:|
    | sweep_low | ? | ?×全局 |
    | ref_low | ? | ?×全局 |
    | ATR×3.5 | ? | ?×全局 |
    
    （如果2022的ATR×3.5比sweep_low大很多，说明ATR止损在熊市更保护）
  </required_output_table>

  <acceptance>
    <item>四种止损距离均正确计算</item>
    <item>按时期（尤其2022）分层报告</item>
    <item>理论止损率改善估算（多少"第1根K线止损"能避免）</item>
    <item>与MAE分析对比（ATR×3.5是否覆盖80th pct MAE）</item>
    <item>明确建议止损方案（为0B13或后续策略回测提供参数）</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号或Regime参数</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. ATR×3.5的平均止损距离（vs sweep_low的2.33%和ref_low的1.37%）
    2. ATR×3.5是否覆盖了MAE 80th percentile盈利交易（若0B14已完成）
    3. 使用ATR×3.5止损，理论上能避免多少"第1根K线被止损"的情况
    4. 2022年ATR止损距离 vs 当前结构止损的差异（说明ATR在熊市是否更保护）
    5. 推荐的止损设计方案（供0B13升级版策略回测使用）：
       a. ATR×3.5纯ATR止损？
       b. max(ref_low, ATR×3.5)复合止损？
       c. 其他方案？
    6. 建议更新的CURRENT_STATE字段
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B9_STOP_DIAGNOSTIC.md（止损诊断基准）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B14_MAE_ANALYSIS.md（若已完成，引用80th pct数据）</file>
    <file>00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md（方向2 ATR研究）</file>
    <file>01_MEMORY_CORE/PROJECT_CONTEXT.md（PC-11：V4历史结构止损方案）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
