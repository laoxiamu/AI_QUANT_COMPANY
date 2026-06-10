# Codex 任务：MAE 分析（最大逆势运动分析）

```xml
<task>
  <id>0B-14-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断分析，不计入失败计数</type>

  <context>
    MAE（Maximum Adverse Excursion，最大逆势运动）由 John Sweeney 1996年提出，
    是止损位优化的行业标准方法。
    
    核心原理：
    对所有历史交易，统计从入场到最终退出之间，价格在反向最多走了多远。
    - 盈利交易的MAE分布 → 止损应设在这个分布的80~90%分位之外
    - 若止损比80%盈利交易的MAE还紧，就是在把正确方向的交易震出去
    
    我们的问题：
    - 止损中位在第1根K线触发，80%止损在t+6前发生
    - 止损用的是 sweep_low（或 ref_low），可能都落在了正常噪声区间内
    - 但我们从未知道"盈利交易到底被逆向推了多远"
    
    本任务直接回答：止损应该放哪里？
    使用0B12无止损版本的交易记录（有完整持仓路径），
    统计每笔交易的MAE，找到理论上的最优止损位置。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <methodology>
    数据来源：
      0B12无止损版本的交易记录
        06_RESEARCH/CODE/output/no_stop_t24_three_symbols_trades.csv
        06_RESEARCH/CODE/output/no_stop_t24_btc_eth_trades.csv
      以及对应的4H K线OHLCV数据（计算入场到退出期间的价格路径）
    
    MAE定义（做多方向）：
      对每笔交易，从入场K线（t=1）到退出K线（t=24），
      计算每根K线的 low 相对于入场价的距离：
        adverse_move[i] = (entry_price - low[i]) / entry_price × 100%（百分比）
      MAE = max(adverse_move[1:25])（持仓期内最大逆势移动百分比）
    
    MFE（Maximum Favorable Excursion，最大顺势运动）同步计算：
      favorable_move[i] = (high[i] - entry_price) / entry_price × 100%
      MFE = max(favorable_move[1:25])
    
    分组分析：
      盈利交易（最终净收益 > 0）
      亏损交易（最终净收益 ≤ 0）
  </methodology>

  <required_analysis>
    一、MAE分布（核心输出）
      盈利交易 vs 亏损交易的MAE分布直方图
      关键分位数：10th / 25th / 50th / 75th / 80th / 90th percentile
      
      核心问题：
        覆盖80%盈利交易的MAE是多少？（这就是止损应设的位置）
        vs 当前 sweep_low 止损距离（平均约2.33%）
        vs 当前 ref_low 止损距离（平均约1.37%）
    
    二、MAE vs 最终收益散点图
      X轴：MAE（最大逆向运动%）
      Y轴：最终收益（%）
      分色：盈利（绿）vs 亏损（红）
      
      期望看到："U形"分布——MAE小的交易最终收益分布宽（好坏都有），
      MAE大的交易更倾向亏损。如果盈利交易有一个MAE聚集区，
      这就是止损最安全的区域。
    
    三、MFE vs MAE 对比
      盈利交易的MFE/MAE比（利润因子的逆市版本）
      如果 MFE >> MAE，说明盈利交易在逆向运动后确实反弹了很多，
      宽止损是合理的。
    
    四、按品种分层
      BTC / ETH / SOL 各自的MAE分位数
      SOL的MAE是否比BTC/ETH更大？（与止损率67%对应）
    
    五、按时期分层
      2019-2020 / 2021 / 2022 / 2023-2024
      2022的MAE是否异常大？（对应90.91%止损率）
    
    六、关键表格（必须输出）
      | 分位数 | 所有交易MAE | 盈利交易MAE | 亏损交易MAE |
      |--------|----------:|----------:|----------:|
      | 25th % | ?% | ?% | ?% |
      | 50th % | ?% | ?% | ?% |
      | 75th % | ?% | ?% | ?% |
      | 80th % | ?% | ?% | ?% |（这是关键止损参考位）
      | 90th % | ?% | ?% | ?% |
      
      当前止损距离对比：
        sweep_low平均距离：约2.33%（来自0B10报告）
        ref_low平均距离：约1.37%（来自0B10报告）
        MAE建议止损位（80th盈利）：?%  ← 本任务的核心输出
  </required_analysis>

  <outputs>
    <file>06_RESEARCH/CODE/v14_mae_analysis.py</file>
    <file>06_RESEARCH/RESULTS/20260606_mae_analysis.md</file>
    <file>06_RESEARCH/CODE/output/mae_distribution_chart.png</file>
    <file>06_RESEARCH/CODE/output/mae_vs_return_scatter.png</file>
    <file>06_RESEARCH/CODE/output/mae_metrics.json</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B14_MAE_ANALYSIS.md</file>
  </outputs>

  <acceptance>
    <item>MAE和MFE均正确计算（从入场到退出，逐根K线）</item>
    <item>盈利/亏损分组清晰</item>
    <item>关键分位数表格完整（含80th percentile盈利MAE）</item>
    <item>MAE vs 收益散点图输出</item>
    <item>按品种分层完整</item>
    <item>明确回答：当前sweep_low/ref_low止损是否在盈利MAE 80th之内？</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止修改任何策略参数</item>
    <item>禁止查看Holdout</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 盈利交易MAE 80th percentile是多少%？
    2. 当前sweep_low（平均2.33%）和ref_low（平均1.37%）止损是否落在盈利MAE 80th之内？
       （如果是，说明止损确实太紧）
    3. ATR止损建议（基于MAE数据计算建议的ATR倍数）
    4. SOL的MAE是否异常大（解释SOL止损率更高的原因）
    5. 基于MAE分析，建议下一个策略版本的止损设计
    6. 建议更新的CURRENT_STATE字段
  </report_to_claude>

  <references>
    <file>06_RESEARCH/CODE/output/no_stop_t24_three_symbols_trades.csv（主数据）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B12_NO_STOP_DIAGNOSTIC.md（无止损版本参考）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B9_STOP_DIAGNOSTIC.md（止损诊断基准）</file>
    <file>00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md（MAE方法论）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
