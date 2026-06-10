# Codex 任务：v8 策略回测——t+24 + ref_low止损

```xml
<task>
  <id>0B-13-v8</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>新假设策略回测，计入失败计数（当前6/8，本任务若失败→7/8）</type>

  <context>
    本任务合并两个已验证的最优单变量发现：
    
    发现1（来自0B8时间敏感性）：
      t+24是最优持仓周期，Sharpe 1.31 > t+12的0.87
      原因：信号统计边沿在t+24最强（事件研究t+24均值+2.34%）
    
    发现2（来自0B10/v6b）：
      ref_low止损比sweep_low止损给出更高Sharpe（1.22 vs 0.87）
      原因：ref_low离入场价更近 → 风险距离更小 → 仓位更大 → 盈利放大
      注意：ref_low是更紧的止损（ref_low > sweep_low，距入场价更近）
    
    逻辑：
      v6b（ref_low+t+12）Sharpe 1.22，MaxDD 28.45%，接近门槛但未过
      0B8 t+24 Sharpe 1.31，MaxDD 37.63%，Sharpe过但MaxDD过高
      
      组合假设：ref_low止损让仓位更大，t+24让信号充分发展，
      两者组合有可能在Sharpe和MaxDD之间取得平衡。
      
      不确定性：t+24持仓期更长 → 资金费率累积更多，可能抵消Sharpe改善。
                止损更紧 → 止损触发更早，t+24的信号优势能否体现有待验证。
    
    ⚠️ 重要提示：当前失败计数6/8，本任务若FAILED则为7/8，仅剩1次机会。
    执行前请确认此决策。本任务是基于现有最优组合的最理性下一步，
    不是孤注一掷，但需要充分认识到风险。
    
    单变量原则：相比v6b，唯一变化是持仓期从t+12改为t+24。
    
    决策依据：Claude（CTO）基于0B8/0B9/0B10诊断数据的综合判断
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <strategy_spec>
    与 v6b（TASK_0B10 candidate版本）完全相同，仅修改持仓期：
    
    【修改】退出：持有至入场后第24根4H K线收盘退出（t+24，96小时）
    【不变】止损：ref_low（Sweep事件前20根K线最低价，即signal_time前20根的min(low)）
    【不变】信号：Bullish Sweep（sweep_lookback=20，v4定义）
    【不变】Regime：双层（各品种前一日close>EMA200 AND BTC前一日30日对数收益>0）
    【不变】品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多
    【不变】入场：信号K线下一根K线开盘价
    【不变】持仓冲突：同品种同向有仓时拒绝新信号
    【不变】仓位：固定风险1%账户净值 / ref_low风险距离，100,000 USDT初始，1x杠杆
    【不变】成本：手续费0.04%，滑点0.05%，历史资金费率（注：t+24持仓更长，资金费率累积更多）
    【不变】时间范围：前80%数据，Holdout封存
    
    止损逻辑说明：
      ref_low = min(low[i-20:i-1])，i = sweep发生的K线
      stop_price = ref_low
      因为 sweep_low < ref_low（Sweep定义要求价格刺破ref_low），
      ref_low止损比sweep_low更紧（距入场价更近），风险距离更小，仓位更大
  </strategy_spec>

  <pre_registration>
    本任务在运行前必须写预登记文件（先登记，再运行）。
    版本号：v5_sweep_regime_bull_v8
    
    预登记成功条件（硬性门槛，不得根据结果调整）：
    三品种合并：Sharpe > 1.0 AND MaxDD < 25%
    
    若仅BTC+ETH通过而三品种未通过：
    记录为"条件通过（双品种）"，不计入失败次数，
    但需要新假设单独预登记BTC+ETH版本（不得追认本次结果）。
  </pre_registration>

  <data_inputs>
    事件文件（已有，直接复用）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    
    价格数据：与v4相同数据源
    参考代码：
      06_RESEARCH/CODE/v10_wider_stop_backtest.py（v6b，本任务基础）
      06_RESEARCH/CODE/v6_time_exit_backtest.py（t+12时间退出逻辑参考）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v13_t24_reflowstop_backtest.py</file>
    <file>06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v8.md（预登记，运行前先写）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v8_BACKTEST.md</file>
    <file>06_RESEARCH/CODE/output/v8_strategy_equity_curve.png</file>
    <file>06_RESEARCH/CODE/output/v8_strategy_trades.csv</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B13_T24_REFLOWSTOP.md</file>
  </outputs>

  <required_output_table>
    核心对比表（所有策略版本汇总）：
    
    | 版本 | 止损 | 退出 | Sharpe | MaxDD | Expectancy |
    |------|------|------|-------:|------:|-----------:|
    | v4（固定TP）| sweep_low | 1R/2R | 0.31 | 19.08% | +0.032R |
    | v6（0B10 baseline）| sweep_low | t+12 | 0.87 | 36.32% | — |
    | v6b（0B10 candidate）| ref_low | t+12 | 1.22 | 28.45% | +1.009R |
    | v8（本任务）| ref_low | t+24 | ? | ? | ? |
    
    额外分析：
    - 资金费率总成本（t+24持仓更长，需要对比v6b的资金费率成本）
    - 止损触发率（预期比v6b更高，因为t+24意味着更多交易活过止损进入最终退出）
    - Walk-Forward三段（重点：WF第二段是否改善）
    - 时期分层（2022年净收益是否比v6b更差，因持仓更长被止损率90%截断）
    - BTC+ETH双品种子集单独报告
  </required_output_table>

  <acceptance>
    <item>预登记文件在运行前写入</item>
    <item>退出时机正确：第24根K线收盘（不是第25根）</item>
    <item>止损使用ref_low（非sweep_low）</item>
    <item>仓位按ref_low风险距离计算</item>
    <item>三品种 + BTC+ETH 双品种均完整报告</item>
    <item>所有策略版本对比表完整</item>
    <item>Walk-Forward三段报告</item>
    <item>时期分层报告（含2022单独展示）</item>
    <item>Holdout未读取</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号或Regime参数</item>
    <item>禁止在看到结果后调整持仓期（只测t+24）</item>
    <item>禁止将BTC+ETH通过结果追认为三品种假设通过</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <risk_warning>
    当前失败计数6/8，本任务若失败→7/8（仅剩1次）。
    报告中必须明确标注本次结论对失败计数的影响。
    如果FAILED，Claude待处理事项必须包含：
    - 是否触发L3审计
    - 最后1次失败应该测什么
  </risk_warning>

  <report_to_claude>
    1. v8三品种和BTC+ETH的核心指标（Sharpe/MaxDD/Expectancy）
    2. 是否通过预登记门槛（Sharpe>1.0 AND MaxDD<25%）
    3. 与v6b的直接对比（t+24是否改善了t+12的问题）
    4. 资金费率成本对比（t+24比t+12多多少）
    5. 2022年表现（持仓更长是否让2022更难看）
    6. Walk-Forward第二段是否改善（这是长期的稳定性缺口）
    7. 若FAILED（7/8）：
       - 当前6种策略变体（v4/v6/v6b/v8）全部失败的统一模式是什么？
       - 最后1次建议测什么（建议ATR止损/组合法/还是换信号）
       - 是否建议现在就触发L3审计（不等第8次失败）
    8. 建议更新的CURRENT_STATE字段
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B10_WIDER_STOP.md（v6b规格，本任务基础）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B10_WIDER_STOP.md（v6/v6b结果）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B8_TIME_SENSITIVITY.md（t+24最优依据）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B9_STOP_DIAGNOSTIC.md（止损诊断）</file>
    <file>02_KNOWLEDGE_BASE/SWEEP_SIGNAL_FAILURE_LESSONS_v2.md</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
