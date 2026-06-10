# Codex 任务：t+24 纯时间退出（无止损）回测

```xml
<task>
  <id>0B-13-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断，不计入失败计数</type>

  <context>
    0B8 时间敏感性分析显示：t+24（持有96小时）Sharpe 1.31（三品种），
    是我们测试过的最佳持仓期。但 MaxDD 37.63% 超过门槛 25%。
    
    0B9 止损诊断显示：68% 的 t+24 版本交易最终被止损，平均在第 5 根 K 线触发。
    
    核心问题：如果把止损完全去掉（纯时间退出），Sharpe 和 MaxDD 会怎样变化？
    这个测试揭示"信号质量天花板"——在没有止损干预的理想状态下，策略能达到什么水平。
    
    如果无止损版本 Sharpe 明显高于 1.31：说明止损结构是主要障碍，值得继续优化。
    如果无止损版本 Sharpe ≈ 1.31：说明信号本身的盈亏分布就是瓶颈，止损优化空间有限。
    如果无止损版本 MaxDD 也很高（>35%）：说明信号本身需要对冲或过滤，而非止损问题。
    
    重要提示：无止损不是实盘可用的策略设计，仅作诊断用。
  </context>

  <data_inputs>
    事件数据（已有）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv  ← 425个事件
    
    价格数据：
      06_RESEARCH/DATA/BTCUSDT_4H.csv
      06_RESEARCH/DATA/ETHUSDT_4H.csv
      06_RESEARCH/DATA/SOLUSDT_4H.csv
    
    参考代码：
      06_RESEARCH/CODE/v8_time_sensitivity.py  ← t+24版本的基础实现，在此基础上去掉止损逻辑
  </data_inputs>

  <hypothesis_spec>
    信号：Bullish Liquidity Sweep + 双层Regime（与v4完全相同）
    样本：前80%数据（固定nrows，Holdout物理截断，绝对禁止读取）
    
    版本1（三品种，无止损）：
      - 入场：与v4相同
      - 止损：无
      - 退出：持有至第24根4H K线收盘（t+24，即96小时后退出）
      - 品种：BTC + ETH + SOL
    
    版本2（BTC+ETH，无止损）：
      - 与版本1相同，仅去除SOL
    
    成本：与v4相同（手续费0.08%，滑点0.10%，资金费率每8小时0.01%）
    仓位：固定1x名义仓位（与v4相同）
    持仓冲突规则：同一品种同一时间只能有一笔持仓
  </hypothesis_spec>

  <required_outputs_per_version>
    - 总交易数、净收益率、Sharpe、MaxDD、Expectancy
    - Walk-Forward三段结果
    - 各时期（2019-2020/2021/2022/2023-2024）分段表现
    - 权益曲线图
    - 与 v4（有止损，固定TP）和 0B8-t+24（有止损）的三者对比表
  </required_outputs_per_version>

  <outputs>
    <file>06_RESEARCH/CODE/v13_t24_no_stop.py</file>
    <file>06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v8_no_stop.md</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v8_no_stop_BACKTEST.md</file>
    <file>06_RESEARCH/CODE/output/v8_no_stop_metrics.json</file>
    <file>06_RESEARCH/CODE/output/v8_no_stop_trades.csv</file>
    <file>06_RESEARCH/CODE/output/v8_no_stop_equity_curve.png</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B13_T24_NO_STOP.md</file>
  </outputs>

  <acceptance>
    <item>无止损逻辑（每笔交易都持有到第24根K线收盘）</item>
    <item>Holdout物理截断，nrows固定</item>
    <item>资金费率按每8小时0.01%累计计入</item>
    <item>三品种和BTC+ETH两版本均有输出</item>
    <item>含与v4和0B8-t+24的三版本对比表</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号检测逻辑</item>
    <item>禁止直接写入Memory Core文件</item>
    <item>禁止将无止损版本结论写入DECISION_LOG（Claude处理）</item>
  </forbidden>

  <report_to_claude>
    1. 三品种无止损：Sharpe / MaxDD / Expectancy
    2. BTC+ETH无止损：Sharpe / MaxDD / Expectancy
    3. 三版本对比表（v4 vs 0B8-t+24有止损 vs 无止损）
    4. 2022年单独表现（无止损情况下2022的亏损有多严重）
    5. 结论：止损去掉后Sharpe提升了多少？MaxDD变化如何？
  </report_to_claude>
</task>
```
