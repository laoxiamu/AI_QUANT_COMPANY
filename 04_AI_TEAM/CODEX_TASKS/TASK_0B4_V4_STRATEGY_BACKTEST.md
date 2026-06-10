# Codex 任务：v4 完整策略回测

```xml
<task>
  <id>0B-4-v5</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v5_sweep_regime_bull_v4 的事件研究主假设已通过（PASSED），
    425个事件在t+6/12/24均显著为正。

    但事件研究≠策略有效：它没有止损/止盈/成本/持仓冲突。
    本任务是下一步：用VectorBT做完整策略回测，
    产出真实的净P&L曲线和Sharpe，判断信号是否能转化为可交易策略。

    决策依据：DEC-027（假设预登记）、DEC-019（U本位永续合约回测要求）
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <strategy_spec>
    品种：BTC/USDT、ETH/USDT、SOL/USDT，4H周期，仅做多
    Regime：双层（v4规格）
      - 各品种前一完整UTC日收盘价 > Daily EMA200（span=200，shift(1)）
      - 前一完整UTC日BTC 30日对数收益率 > 0（shift(1)）
    入场：Sweep K线收盘后下一根K线开盘价（即signal_time+1根K线open）
    止损：Sweep K线最低价 low[t_sweep]
    止盈：
      - 第一目标：入场价 + 1×风险（平仓50%仓位）
      - 第二目标：入场价 + 2×风险（平仓剩余50%仓位）
    持仓冲突：同品种已有多仓时拒绝后续同向信号
    同K线冲突：止损优先于止盈（同一K线同时触发止损和止盈，执行止损）
    仓位管理：每笔交易固定风险1%（即每笔亏损上限=账户净值×1%）
    初始资金：100,000 USDT（标准化，不影响比例指标）
    杠杆：1x（DEC-019要求首轮1x）
    时间范围：与v4事件研究相同（前80%数据，保留Holdout）
  </strategy_spec>

  <costs>
    手续费：吃单0.04%（taker），入场和出场均按taker
    滑点：0.05%（入场和出场各）
    资金费率：
      - 使用历史真实资金费率数据（从ccxt获取，或使用近似方法）
      - 若无法获取精确历史资金费率，使用近似值：每8小时0.01%（即年化~10.95%）
      - 资金费率在结算时间（UTC 0:00/8:00/16:00）从持仓盈亏中扣除
      - 注意：只有开仓期间的资金费率才计入，已平仓不计
    总成本说明：单边约0.09%（手续费+滑点），资金费率按持仓时长累加
  </costs>

  <data_inputs>
    事件文件（已有）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
      （包含brand、signal_time、sweep_low等字段）
    
    价格数据：与sweep_dual_regime.py使用相同的数据源
    日线数据：与sweep_dual_regime.py使用相同的数据源（用于资金费率时间对齐）
    
    参考代码：06_RESEARCH/CODE/sweep_dual_regime.py（v4事件研究，数据加载方式相同）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v4_strategy_backtest.py</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_BACKTEST.md</file>
    <file>06_RESEARCH/CODE/output/v4_strategy_equity_curve.png</file>
    <file>06_RESEARCH/CODE/output/v4_strategy_trades.csv</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B4_V4_STRATEGY_BACKTEST.md</file>
  </outputs>

  <required_metrics>
    核心指标（必须报告）：
    - 总交易次数（三品种合计 + 分品种）
    - 净收益率（总体）
    - 年化收益率
    - Sharpe Ratio（年化，使用无风险利率0）
    - Sortino Ratio
    - 最大回撤（MaxDD）
    - 平均持仓K线数
    - 胜率（盈利交易/总交易）
    - 平均盈亏比（平均盈利/平均亏损）
    - Expectancy（期望值，单位：R）
    - 资金费率总成本（占净收益的比例）

    Walk-Forward（与v4事件研究相同的三段划分）：
    - 每段的净收益率和Sharpe分别报告
    - 检查是否出现v1/v2实验的严重衰减

    时期分层（与v4一致）：
    - 2019-2020 / 2021 / 2022 / 2023-2024 各时期净收益率

    分品种单独报告：
    - BTC、ETH、SOL各自的Sharpe和MaxDD

    对比参照（在报告中呈现）：
    - v1（4H三重确认）Sharpe：0.60，MaxDD：33.14%
    - v2（1H三重确认）Sharpe：0.90，MaxDD：36.61%
    - v4事件研究不涉及P&L，此处无直接对比值
  </required_metrics>

  <acceptance>
    <item>止损采用sweep_low，不采用其他参考低点</item>
    <item>同K线止损优先于止盈</item>
    <item>持仓冲突正确（同品种同向有仓时拒绝新信号）</item>
    <item>资金费率已计入（即使使用近似值，须说明方法）</item>
    <item>Walk-Forward三段单独报告</item>
    <item>权益曲线图输出</item>
    <item>Holdout物理截断，未读取</item>
    <item>执行报告包含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout数据</item>
    <item>禁止修改Regime参数（不调参数来改善结果）</item>
    <item>禁止修改止损止盈规则来改善结果</item>
    <item>禁止直接写入Memory Core文件</item>
    <item>禁止使用杠杆>1x</item>
  </forbidden>

  <report_to_claude>
    执行报告REPORT_0B4的「Claude 待处理事项」须包含：
    1. 策略核心指标（Sharpe/MaxDD/Expectancy）
    2. 策略回测结论：PASSED/FAILED（Sharpe>1.0且MaxDD<25%为通过）
    3. 与v1/v2对比：是否有改善
    4. 是否建议进行双向策略设计（结合v5做空结果）
    5. 建议更新的CURRENT_STATE字段（写草稿）
    6. 若失败：主要失败原因分析（成本侵蚀/信号本身/特定时期）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B2_SWEEP_DUAL_REGIME.md（v4事件研究规格）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md（事件研究结果）</file>
    <file>06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v4.md（预登记文件）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
