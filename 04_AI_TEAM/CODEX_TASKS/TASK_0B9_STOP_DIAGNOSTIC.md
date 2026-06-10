# Codex 任务：止损触发诊断分析

```xml
<task>
  <id>0B-9-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v4 策略 Expectancy 仅 +0.032R，事件研究 t+12 均值 +1.364%。
    两者之间存在巨大落差，根因假设是：止损在信号充分发展之前频繁触发。
    
    本任务是纯诊断分析，不是新假设，不计入失败计数。
    直接读取 v4 策略的交易记录 CSV，分析每笔交易的实际退出方式和退出时机，
    回答：止损到底在哪一根K线触发？有多少比例的交易在 t+12 之前就退出了？
    
    这个诊断直接决定下一步策略设计方向：
    - 如果止损主要在 t+3~t+6 触发 → 止损太紧，需要更宽的止损或其他风险控制
    - 如果止损主要在 t+8~t+11 触发 → 持仓期本身合理，止损位可微调
    - 如果大部分交易都到时间退出 → 问题在于盈利交易平均收益不够高
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <data_inputs>
    主要输入（已有）：
      06_RESEARCH/CODE/output/v4_strategy_trades.csv
      （每笔交易记录，包含入场时间、退出时间、盈亏、退出原因等字段）
    
    如果 trades CSV 中没有足够字段，可补充读取：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv（入场事件）
      价格数据（从事件入场时间起逐K线追踪）
    
    参考代码：06_RESEARCH/CODE/v4_strategy_backtest.py（了解trades CSV的字段含义）
  </data_inputs>

  <required_analysis>
    一、退出方式分布
      - 止损退出笔数 vs 时间退出笔数（若trades CSV有退出类型字段）
      - 或按实际持仓K线数分桶：1-3根/4-6根/7-9根/10-12根/12根（完整）
    
    二、止损触发时机分布
      对所有止损退出的交易，统计：
        - 在第几根K线触发止损（直方图）
        - 中位数/均值/25th percentile
        - 在 t+6 之前触发的比例（这部分完全损失了t+6信号）
        - 在 t+12 之前触发的比例
    
    三、盈亏分布对比
      止损退出交易的平均R收益（期望为约-1R）
      时间退出交易的平均R收益
      → 两者之比是否解释了低Expectancy
    
    四、按品种分层
      BTC / ETH / SOL 各自：
        - 止损触发率
        - 平均持仓K线数
        - 平均R收益
      → 确认SOL是否止损更频繁/更早
    
    五、按时期分层
      2019-2020 / 2021 / 2022 / 2023-2024：
        - 止损触发率
        - 平均持仓K线数
      → 确认2022是否止损率异常高
    
    六、关键可视化
      - 退出K线数分布直方图（止损 vs 时间退出对比）
      - 各时期止损触发率柱状图
  </required_analysis>

  <outputs>
    <file>06_RESEARCH/CODE/v9_stop_diagnostic.py</file>
    <file>06_RESEARCH/RESULTS/20260606_v4_stop_diagnostic.md</file>
    <file>06_RESEARCH/CODE/output/v4_stop_diagnostic_charts.png</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B9_STOP_DIAGNOSTIC.md</file>
  </outputs>

  <acceptance>
    <item>退出方式分布完整（止损 vs 时间退出数量和比例）</item>
    <item>止损触发时机分布（含直方图和分位数）</item>
    <item>按品种和时期分层报告</item>
    <item>明确回答「止损在哪个阶段触发最频繁」</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止修改任何策略参数</item>
    <item>禁止查看Holdout</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 止损触发比例（全体/按品种/按时期）
    2. 止损平均触发时机（第几根K线）
    3. 在t+6前触发的止损比例
    4. SOL与BTC/ETH止损行为对比
    5. 核心诊断结论：是止损太紧？还是盈利交易收益不足？还是两者都有？
    6. 对下一步策略设计的具体建议（供Claude决策参考）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B4_V4_STRATEGY_BACKTEST.md</file>
    <file>06_RESEARCH/CODE/output/v4_strategy_trades.csv</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
