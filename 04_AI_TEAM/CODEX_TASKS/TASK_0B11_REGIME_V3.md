# Codex 任务：第三层Regime过滤（回撤过滤，事件研究）

```xml
<task>
  <id>0B-11-v7</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v4 双层 Regime 残留问题：2022 年 12 个事件全部为负（t+12 均值 -1.386%）。
    v4 策略 2022 净收益 -6.51%，是拖累 Sharpe 的主要时期之一。
    
    v4 的双层 Regime：
      条件1：各品种前一日收盘 > Daily EMA200
      条件2：BTC 前一日 30 日对数收益 > 0%
    
    2022 年问题：熊市期间即使 EMA200 和 30 日动量均不满足，
    但 2022 年初（1-4月）BTC 仍在 EMA200 之上，30 日动量仍为正，
    因此12个事件没有被过滤出去，而这段时间实际处于见顶回落阶段。
    
    本任务添加第三层过滤条件（单变量）：
      BTC 当前价格距 90 日滚动最高价的回撤幅度 < 20%
      （即：价格没有从近期高点大幅下跌，说明不处于明显下跌趋势中）
    
    逻辑：做多 Sweep 需要多头市场的主力资金支撑。
    当价格已经从近期高点回撤超过 20%，即使 EMA200 和动量条件还未失效，
    多头市场的实质已经发生变化，Sweep 不容易被快速吸收。
    
    本任务是事件研究（event study），不是策略回测，与 v4 格式完全相同。
    若事件研究通过，后续再做策略回测。
    
    注：本任务是新假设研究闭环，若失败计入失败计数。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <regime_v3_definition>
    在 v4 双层 Regime 基础上新增第三条件：
    
    条件1（不变）：各品种前一完整UTC日收盘价 > 该日 Daily EMA200（span=200，shift(1)）
    条件2（不变）：BTC 前一完整日 30 日对数收益率 > 0%（shift(1)）
    条件3（新增）：BTC 前一完整日收盘价距过去 90 日最高收盘价的回撤 < 20%
    
    条件3的计算：
      rolling_high_90 = BTC_daily_close.rolling(90).max().shift(1)
      drawdown_from_high = (rolling_high_90 - BTC_daily_close.shift(1)) / rolling_high_90
      条件3 = drawdown_from_high < 0.20
      （即：过去90日最高点到现在的跌幅 < 20%）
    
    注意：
    - rolling_high_90 使用 shift(1)，避免前视偏差（使用前一日已知数据）
    - ETH 和 SOL 的条件3也使用 BTC 数据（与条件2相同，只有 BTC 作为市场温度计）
    - min_periods=90，前90日数据不足时该条件不满足（信号不生效）
    
    单变量原则：相比 v4 仅新增条件3，Sweep定义、品种、周期、评估方法完全不变。
  </regime_v3_definition>

  <event_study_spec>
    与 v4 事件研究（TASK_0B2）完全相同的格式和方法：
    
    品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多
    未来收益：log(close[t+6]/close[t])、log(close[t+12]/close[t])、log(close[t+24]/close[t])
    统计检验：单侧 t-test，alternative="greater"，H0: mean=0
    预登记主假设门槛：三个窗口 t+6/12/24 均值>0 且 p<0.05
    时间范围：前80%数据，Holdout封存
    
    必须报告：
    - 与 v4 的完整对比（事件数/各窗口均值+p值）
    - 时期分层（重点：2022的事件数是否显著减少？均值是否改善？）
    - Walk-Forward（三段，与v3/v4格式相同）
    - 非重叠子集校正（与v4相同，间隔>24根K线）
  </event_study_spec>

  <key_diagnostic>
    本任务的核心诊断问题（必须在报告中明确回答）：
    
    1. 条件3过滤后，2022年事件数从12个减少到多少？
    2. 2022年过滤后，合并样本的均值和显著性是否改善？
    3. 总样本量从425减少到多少？是否仍满足探索级（≥300）？
    4. v4 vs v7 各时期均值对比（特别是2022和2019-2020）
  </key_diagnostic>

  <sample_estimate>
    预估：v4的425个事件中，2022年12个全部过滤（条件3在2022熊市下大概率触发）
    以及部分2019-2020的弱势期事件也可能被过滤
    估计保留350-410个事件，仍处于探索级
    若低于300，在报告中标注样本不足风险
  </sample_estimate>

  <data_inputs>
    BTC/ETH/SOL 4H和Daily数据（与v4相同数据源）
    参考代码：06_RESEARCH/CODE/sweep_dual_regime.py（v4，添加条件3即可）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v11_regime_v3_event_study.py</file>
    <file>06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v7.md（预登记，运行前先写）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v7_EVAL.md</file>
    <file>06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v7.csv</file>
    <file>06_RESEARCH/CODE/output/stats_v5_sweep_regime_bull_v7.json</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B11_REGIME_V3.md</file>
  </outputs>

  <required_output_table>
    核心对比（v3/v4/v7三版本）：
    
    | 指标 | v3（EMA200）| v4（+30日动量）| v7（+回撤<20%）|
    |------|------------:|---------------:|---------------:|
    | 完整事件数 | 748 | 425 | ? |
    | 2022事件数 | 20 | 12 | ? |
    | t+6 均值/p | +0.489%/0.0022 | +0.770%/0.000078 | ? |
    | t+12 均值/p | +0.513%/0.0122 | +1.364%/<0.000001 | ? |
    | t+24 均值/p | +0.465%/0.0918 | +2.337%/<0.000001 | ? |
    | WF第二段t+12 p | 0.2026 | 0.1251 | ? |
    
    重点：v7 能否解决 v4 的两个稳定性缺口
      - 2022事件数→0且均值不再为负
      - WF第二段变为显著
  </required_output_table>

  <acceptance>
    <item>预登记文件在运行前写入</item>
    <item>条件3正确计算（90日滚动高点，shift(1)，不含前视）</item>
    <item>v3/v4/v7三版本对比表完整</item>
    <item>2022年过滤效果单独报告</item>
    <item>非重叠子集校正完整</item>
    <item>Walk-Forward三段报告</item>
    <item>Holdout未读取</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改条件1/2（不变）</item>
    <item>禁止调整20%阈值（即使效果不好也不得修改，记录原始结果）</item>
    <item>禁止在看到结果后调整回撤窗口（90日固定）</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. v7主假设是否通过（t+6/12/24三窗口）
    2. 2022年事件数减少情况（过滤效果是否达预期）
    3. WF第二段是否改善（这是v4最大的稳定性缺口）
    4. 总样本量（是否仍满足≥300探索级）
    5. 结论：第三层Regime条件是否有效改善跨时期稳定性？
    6. 建议更新的CURRENT_STATE字段
    7. 若通过：建议立即安排v7策略回测；若失败：下一步方向建议
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B2_SWEEP_DUAL_REGIME.md（v4，本任务基础）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md（v4结果）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B2_SWEEP_DUAL_REGIME.md（v4执行报告）</file>
    <file>02_KNOWLEDGE_BASE/SWEEP_SIGNAL_FAILURE_LESSONS_v2.md（失败经验）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
