# Codex 任务：v6 时间止盈策略回测

```xml
<task>
  <id>0B-7-v6</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v4事件研究：三层统计校验全通过（Bootstrap p=0.003，t+24均值+2.337%）
    v4策略回测：FAILED（Sharpe 0.31，Expectancy +0.032R）
    
    根因分析：固定止损+1R/2R止盈造成系统性退出错位。
    信号的统计边沿在t+24（4天持有），但固定止盈在信号到达该周期之前就触发，
    导致策略只捕获了部分信号价值，同时承担了完整的成本和止损风险。
    
    本任务是单变量修正：
      - 相同信号 + 相同Regime（不变）
      - 相同止损（不变）
      - 去除1R/2R固定止盈，改为时间止盈：持有至第12根4H K线收盘退出
    
    研究问题：最简单的时间退出能否将事件研究信号转化为可接受的策略？
    
    唯一变量：退出方式（1R/2R固定止盈 → t+12时间退出）
    
    决策依据：Claude（CTO）架构判断，无需Founder确认（非D级决策）
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <strategy_spec>
    与 TASK_0B4 完全相同，唯一修改：
    
    【修改】退出规则：
      - 删除：第一目标1R（平仓50%），第二目标2R（平仓50%）
      - 新增：持有至入场后第12根4H K线收盘价退出（全仓退出）
      - 保留：止损仍为Sweep K线最低价 low[t_sweep]，止损优先于时间退出
    
    【不变】信号：Bullish Liquidity Sweep（sweep_lookback=20，定义与v4相同）
    【不变】Regime：双层（前一完整UTC日各品种close>EMA200 AND BTC 30日对数收益>0）
    【不变】入场：信号K线收盘后下一根K线开盘价
    【不变】品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多
    【不变】持仓冲突：同品种同向有仓时拒绝新信号
    【不变】仓位：每笔固定风险1%账户净值，初始资金100,000 USDT，1x杠杆
    【不变】时间范围：前80%数据（Holdout保持封存）
    【不变】成本：手续费0.04%吃单，滑点0.05%，历史资金费率
    
    注意：时间止盈意味着持仓最长12根4H K线（48小时），
    如未触发止损则在第12根收盘退出；若止损先触发则提前退出。
  </strategy_spec>

  <additional_analysis>
    必须输出的两个子集对比（在同一次运行中完成）：
    
    子集A（主结果）：BTC + ETH + SOL 三品种合并（与v4相同范围）
    子集B（对比）：BTC + ETH 双品种（去除SOL）
    
    目的：确认SOL是否是v4策略的主要拖累来源。
    两个子集的所有指标都完整报告，不只报告较好的那个。
  </additional_analysis>

  <data_inputs>
    可直接复用v4事件文件（信号+Regime已计算完毕）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    
    价格数据：与v4相同（用于模拟退出K线的OHLCV）
    
    参考代码：
      06_RESEARCH/CODE/v4_strategy_backtest.py（v4策略，本任务基础）
      06_RESEARCH/CODE/sweep_dual_regime.py（数据加载参考）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v6_time_exit_backtest.py</file>
    <file>06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v6.md（预登记文件，运行前先写）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v6_BACKTEST.md</file>
    <file>06_RESEARCH/CODE/output/v6_strategy_equity_curve.png</file>
    <file>06_RESEARCH/CODE/output/v6_strategy_trades.csv</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B7_V6_TIME_EXIT.md</file>
  </outputs>

  <required_metrics>
    与v4策略报告格式完全一致，便于直接对比。
    
    核心对比表（必须呈现）：
    | 指标 | v4策略（固定TP） | v6三品种（时间TP） | v6双品种BTC+ETH |
    |------|----------------:|------------------:|----------------:|
    | 实际交易数 | 360 | ? | ? |
    | 净收益率 | +20.11% | ? | ? |
    | 年化收益率 | +2.97% | ? | ? |
    | Sharpe | 0.31 | ? | ? |
    | MaxDD | 19.08% | ? | ? |
    | Expectancy（R） | +0.032R | ? | ? |
    | WF Sharpe（三段）| 0.85→0.34→0.11 | ? | ? |
    
    时期分层（与v4一致）：
    2019-2020 / 2021 / 2022 / 2023-2024 各时期净收益率
    
    止损触发分析（新增，v4未要求）：
    - 止损触发笔数 vs 时间止盈触发笔数
    - 平均实际持仓K线数（期望接近12，若远低于12说明止损频繁触发）
    - 止损触发交易的平均亏损 vs 时间止盈交易的平均盈利
    
    成本对比：
    - 手续费+资金费率总量
    - 占毛利润比例（与v4的54.64%对比）
    
    注：时间退出持仓期固定（最长48小时），资金费率相比v4的不定期持仓应有所变化。
  </required_metrics>

  <acceptance>
    <item>预登记文件在运行前写入（先登记后运行）</item>
    <item>时间退出正确（入场后第12根4H K线收盘，而非第13根）</item>
    <item>止损优先于时间止盈（同一K线止损和时间到期，执行止损）</item>
    <item>三品种和双品种（BTC+ETH）两个子集均完整报告</item>
    <item>v4 vs v6核心对比表完整</item>
    <item>止损触发分析完整</item>
    <item>Walk-Forward三段报告</item>
    <item>Holdout物理截断，未读取</item>
    <item>执行报告包含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout数据</item>
    <item>禁止修改信号参数（sweep_lookback=20等）</item>
    <item>禁止修改Regime条件</item>
    <item>禁止在看到结果后调整时间窗口（必须只测t+12，不得因为t+12差就改测t+6或t+24）</item>
    <item>禁止直接写入Memory Core文件</item>
    <item>禁止只报告表现较好的子集（两个子集必须同时报告）</item>
  </forbidden>

  <interpretation_guidance>
    时间止盈的成功条件（预登记，运行前固定）：
    - 三品种版本：Sharpe > 1.0 且 MaxDD < 25%
    - 若三品种未通过但双品种（BTC+ETH）通过：记录为"SOL拖累确认，信号本身有效"
    - 若两个版本均未通过：说明成本结构本身阻碍了信号实现，需考虑更换信号或研究仓位管理
    
    平均持仓K线数是关键诊断指标：
    - 如果均值远低于12（如6-8根）：止损频繁触发，止损位设置可能过紧
    - 如果均值接近12：大部分交易确实持有到时间止盈，信号捕获完整
  </interpretation_guidance>

  <report_to_claude>
    执行报告REPORT_0B7的「Claude 待处理事项」须包含：
    1. v6三品种和双品种的核心指标（Sharpe/MaxDD/Expectancy）
    2. 结论：时间退出是否改善了v4策略的根本问题？
    3. 止损触发率（高低是关键诊断）
    4. SOL是否确认为主要拖累（双品种结果是否显著好于三品种）
    5. 建议更新的CURRENT_STATE字段（草稿）
    6. 下一步方向建议（基于结果，不预设）
    7. 是否触发L3审计条件（连续失败计数目前4/8，若本次再FAILED→5/8，距止损线更近）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B4_V4_STRATEGY_BACKTEST.md（v4策略规格，本任务基础）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B4_V4_STRATEGY_BACKTEST.md（v4结果基准）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md（事件研究结果）</file>
    <file>02_KNOWLEDGE_BASE/SWEEP_SIGNAL_FAILURE_LESSONS_v2.md（失败经验）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
