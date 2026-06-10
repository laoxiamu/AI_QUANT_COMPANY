# Codex 任务：时间退出持仓期敏感性分析

```xml
<task>
  <id>0B-8-v6</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v6（TASK_0B7）只测试了 t+12 时间退出。
    但事件研究显示三个窗口均显著：
      t+6  均值 +0.770%（24小时持仓）
      t+12 均值 +1.364%（48小时持仓）← v6测试
      t+24 均值 +2.337%（96小时持仓）
    
    本任务测试 t+6 和 t+24 两个持仓期，与 v6（t+12）构成完整的
    "持仓期敏感性图谱"，回答：哪个持仓期能在成本和信号捕获之间
    取得最佳平衡？
    
    注：本任务与 v6 并行，使用相同事件文件和相同逻辑，仅持仓期不同。
    不是新假设闭环，不计入失败计数——这是诊断分析。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <strategy_spec>
    与 TASK_0B7（v6）完全相同，仅以下参数不同：
    
    本任务同时运行两个版本：
      版本A：持有至入场后第 6 根 4H K线收盘退出（t+6，24小时）
      版本B：持有至入场后第 24 根 4H K线收盘退出（t+24，96小时）
    
    两个版本的其他规则完全一致：
    - 信号/Regime/品种/入场/止损：与 v6 相同
    - 持仓冲突：同品种同向有仓时拒绝新信号
    - 成本：手续费0.04%，滑点0.05%，历史资金费率
    - 仓位：固定风险1%，初始100,000 USDT，1x杠杆
    - 时间范围：前80%数据，Holdout保持封存
    
    每个版本均输出三品种合并 + BTC+ETH双品种子集（共4个结果）
  </strategy_spec>

  <data_inputs>
    直接复用 v4 事件文件：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    参考代码：06_RESEARCH/CODE/v6_time_exit_backtest.py（若 v6 已完成）
              或 06_RESEARCH/CODE/v4_strategy_backtest.py（若 v6 尚未完成）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v8_time_sensitivity.py</file>
    <file>06_RESEARCH/RESULTS/20260606_time_exit_sensitivity.md</file>
    <file>06_RESEARCH/CODE/output/time_sensitivity_equity_curves.png（四条曲线对比图）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B8_TIME_SENSITIVITY.md</file>
  </outputs>

  <required_output_table>
    核心汇总表（5列对比，v6结果由Codex从REPORT_0B7读取填入）：
    
    | 指标 | v4固定TP | v6（t+12） | t+6版本 | t+24版本 |
    |------|--------:|----------:|-------:|--------:|
    | 实际交易数（三品种）| 360 | ? | ? | ? |
    | 净收益率 | +20.11% | ? | ? | ? |
    | Sharpe | 0.31 | ? | ? | ? |
    | MaxDD | 19.08% | ? | ? | ? |
    | Expectancy（R） | +0.032R | ? | ? | ? |
    | 平均持仓K线数 | — | ? | ? | ? |
    | 手续费+资金费率 | 54.64%毛利 | ? | ? | ? |
    | WF Sharpe（三段）| 0.85→0.34→0.11 | ? | ? | ? |
    
    注：v4固定TP和v6的值从已有报告读取，本任务只输出t+6和t+24。
    
    同样提供 BTC+ETH 双品种版本的对比。
  </required_output_table>

  <acceptance>
    <item>t+6 和 t+24 两个版本均完整运行</item>
    <item>三品种和BTC+ETH双品种各自报告</item>
    <item>四条权益曲线在同一图中对比</item>
    <item>平均实际持仓K线数报告（诊断止损频率）</item>
    <item>Holdout未读取</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号或Regime参数</item>
    <item>禁止根据结果选择性只报告表现好的持仓期</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 三个时间退出版本（t+6/12/24）的Sharpe和MaxDD
    2. 哪个持仓期表现最好？是否有显著差异？
    3. 平均止损触发发生在第几根K线（说明止损紧不紧）
    4. 是否建议将最优持仓期纳入下一版预登记
    5. 建议更新的CURRENT_STATE字段
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B7_V6_TIME_EXIT.md</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B4_V4_STRATEGY_BACKTEST.md（v4基准数据）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
