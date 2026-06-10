# Codex 任务：MAE 最大逆势运动分析

```xml
<task>
  <id>0B-12-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断，不计入失败计数</type>

  <context>
    外部调研确认：MAE（Maximum Adverse Excursion，最大逆势运动）分析是
    确定最优止损位置的行业标准方法。逻辑：
    
    对于每笔交易，记录"持仓期间最不利的价格点距入场价的距离"（即MAE）。
    - 最终盈利的交易：它们的 MAE 就是"能容忍的最大逆势"
    - 如果止损设在 80% 盈利交易 MAE 的 1.1 倍处，就能让大部分盈利交易活下来
    
    我们现在的困境：止损在第1根K线触发（中位），80%止损在t+6前触发。
    这说明我们的止损比大部分盈利交易的 MAE 还要紧——实际是在"正常波动范围"内止损。
    
    本任务目标：用已有的360笔v4策略交易 + 价格数据，计算每笔交易的MAE，
    找出"止损应该放在哪里才不会提前截断大部分盈利交易"。
    
    这是最高优先级诊断，因为它直接给出止损位置的数据依据，
    而不是猜测"2倍ATR"或"ref_low"。
  </context>

  <data_inputs>
    必须读取：
      06_RESEARCH/CODE/output/v4_strategy_trades.csv   ← 360笔交易记录
      价格数据文件（4H OHLCV）：
        06_RESEARCH/DATA/BTCUSDT_4H.csv 或同目录下的BTC数据
        06_RESEARCH/DATA/ETHUSDT_4H.csv
        06_RESEARCH/DATA/SOLUSDT_4H.csv
    
    参考：
      06_RESEARCH/CODE/v4_strategy_backtest.py  ← 了解trades字段含义和entry逻辑
  </data_inputs>

  <required_analysis>
    一、计算每笔交易的 MAE
      对每笔交易：
        - 找到入场时间戳和入场价
        - 从入场K线开始，逐根K线追踪最低价（做多=最低价是最不利方向）
        - MAE = (入场价 - 持仓期间最低价) / 入场价 × 100%（以百分比表示）
        - 同时记录 MFE（最大顺势运动：持仓期间最高点）
      
    二、MAE 分布分析
      按最终交易结果分组：
        组A：最终盈利的交易（TP2退出）
        组B：最终止损的交易（STOP退出）
      
      对组A（盈利交易）统计 MAE：
        - 中位数、均值、25th/75th/90th percentile
        - 分布直方图
        - 这些数字代表"盈利交易能承受的正常逆势"
      
      关键问题：
        - 组A的 MAE p50（中位数）是多少？ → 止损至少应在此之下
        - 组A的 MAE p75/p90 是多少？ → 止损放这里能保留75%/90%的盈利交易
        - 当前 sweep_low 止损平均距离是多少？与MAE p50对比
    
    三、止损位置建议
      计算：
        - 当前实际止损距离（入场价 - sweep_low）/ 入场价的分布
        - 如果止损设在 MAE p50 × 1.2 处，能保留多少原本被止损的盈利交易？
        - 对应的 Expectancy 改善估算
    
    四、按品种和时期分层
      BTC / ETH / SOL 各自的 MAE p50/p75 对比
      2021 / 2022 / 2023-2024 各时期的 MAE 分布变化
    
    五、MAE vs MFE 散点图
      横轴：MAE（逆势运动）
      纵轴：MFE（顺势运动）
      颜色：盈利=绿，亏损=红
      → 直观显示盈利/亏损交易的分布边界
  </required_analysis>

  <outputs>
    <file>06_RESEARCH/CODE/v12_mae_analysis.py</file>
    <file>06_RESEARCH/RESULTS/20260606_mae_analysis.md</file>
    <file>06_RESEARCH/CODE/output/mae_analysis_charts.png</file>
    <file>06_RESEARCH/CODE/output/mae_analysis_metrics.json</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B12_MAE_ANALYSIS.md</file>
  </outputs>

  <acceptance>
    <item>每笔交易的MAE均已计算（不能只统计平均）</item>
    <item>盈利交易 MAE p50/p75/p90 明确列出</item>
    <item>当前止损距离 vs MAE分位数对比表</item>
    <item>MAE vs MFE 散点图（区分盈亏）</item>
    <item>给出止损位置的数据建议（如"将止损设在MAE p75处，预计可保留X%盈利交易"）</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止修改任何策略参数或运行新策略回测</item>
    <item>禁止查看Holdout</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 盈利交易 MAE p50/p75/p90（百分比）
    2. 当前止损平均距离（百分比）vs MAE p50
    3. 如果止损设在 MAE p75，能"救活"多少被止损的盈利交易？
    4. BTC/ETH/SOL 的 MAE 分布差异
    5. 核心结论：止损应放在多少%以下？
  </report_to_claude>
</task>
```
