# Codex 任务：更宽止损变体（ref_low替代sweep_low）

```xml
<task>
  <id>0B-10-v6b</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v4 策略止损使用 Sweep K线最低价（sweep_low），这是最紧的止损位。
    
    诊断假设：止损太紧导致在信号充分发展前被止损出场，
    使策略无法捕获事件研究显示的 t+12/t+24 收益。
    
    本任务测试单变量修改：
      原止损：sweep_low（Sweep K线最低价）
      新止损：ref_low（Sweep事件之前20根K线的最低价）
    
    逻辑：
      Bullish Sweep 的定义是"价格向下突破 ref_low 后收盘收回"。
      ref_low 是信号的结构性支撑——如果价格跌破 ref_low，
      说明 Sweep 已失效（不只是正常波动），是更有意义的止损位。
      sweep_low 是 Sweep K线内的最低点，可能只是正常的下影线噪声。
    
    风险：更宽止损意味着每笔交易的最大亏损更大，
    需要对应缩小仓位（仍按1%固定风险计算，仓位会自动变小）。
    
    单变量原则：仅修改止损位，所有其他参数与v4策略相同。
    退出方式：使用 t+12 时间退出（与v6相同，而非原来的1R/2R止盈）
              因为 v6 已是单变量退出对比，本任务在此基础上修改止损。
    
    注：本任务是新策略变体，属于研究级假设，结果若失败计入失败计数。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <stop_loss_definition>
    原止损（v4/v6）：
      stop_price = low[t_sweep]
      （Sweep K线的最低价，即 signal_time 对应K线的 low）
    
    新止损（本任务）：
      ref_low 已在事件文件中记录
      stop_price = ref_low = min(low[i-20 : i-1])，其中 i = t_sweep
      （Sweep K线之前20根K线的最低价，不含Sweep K线本身）
    
    注意：
    - ref_low < sweep_low 时，新止损更宽（允许更大波动）
    - ref_low ≥ sweep_low 的情况理论上不存在（Sweep定义要求 low[i] < ref_low）
      实际上 sweep_low ≤ ref_low 总成立，ref_low 止损总是更宽或相等
    
    风险金额计算：
      风险 = 入场价 - ref_low（而非入场价 - sweep_low）
      仓位 = (账户净值 × 1%) / 风险
      → 风险更宽 → 仓位更小 → 每笔名义敞口减少
  </stop_loss_definition>

  <strategy_spec>
    【修改】止损：ref_low（Sweep前20根K线最低价）
    【修改】退出：t+12 时间退出（48小时，与v6相同）
    【不变】信号：Bullish Sweep（sweep_lookback=20）
    【不变】Regime：双层（EMA200 + BTC 30日动量>0）
    【不变】品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多
    【不变】入场：信号K线下一根K线开盘价
    【不变】持仓冲突：同品种同向有仓时拒绝新信号
    【不变】仓位：固定风险1%账户净值，100,000 USDT初始，1x杠杆
    【不变】时间范围：前80%数据，Holdout封存
    【不变】成本：手续费0.04%，滑点0.05%，历史资金费率
  </strategy_spec>

  <data_inputs>
    事件文件：06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    （需确认该文件含 ref_low 字段；若无，从价格数据重新计算）
    
    价格数据：与v4相同
    参考代码：
      06_RESEARCH/CODE/v6_time_exit_backtest.py（退出逻辑参考）
      06_RESEARCH/CODE/v4_strategy_backtest.py（整体框架参考）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v10_wider_stop_backtest.py</file>
    <file>06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v6b.md（预登记，运行前先写）</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v6b_BACKTEST.md</file>
    <file>06_RESEARCH/CODE/output/v6b_strategy_equity_curve.png</file>
    <file>06_RESEARCH/CODE/output/v6b_strategy_trades.csv</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B10_WIDER_STOP.md</file>
  </outputs>

  <required_output_table>
    | 指标 | v4（sweep_low止损+固定TP） | v6（sweep_low+t+12） | v6b（ref_low+t+12）|
    |------|------------------------:|-------------------:|------------------:|
    | 实际交易数 | 360 | (v6结果) | ? |
    | 净收益率 | +20.11% | (v6结果) | ? |
    | Sharpe | 0.31 | (v6结果) | ? |
    | MaxDD | 19.08% | (v6结果) | ? |
    | 平均止损宽度（风险，% of价格）| — | — | ? |
    | 平均仓位大小（vs v4）| — | — | ? |
    | 止损触发率 | — | — | ? |
    | WF Sharpe | 0.85→0.34→0.11 | (v6结果) | ? |
    
    额外输出：
    - 止损宽度分布（ref_low - sweep_low 的直方图，了解平均额外风险幅度）
    - 按品种和时期的止损触发率（与v4对比）
  </required_output_table>

  <acceptance>
    <item>预登记文件在运行前写入</item>
    <item>ref_low 止损正确实现（非 sweep_low）</item>
    <item>仓位根据 ref_low 风险重新计算</item>
    <item>三品种合并 + BTC+ETH 双品种子集均报告</item>
    <item>止损宽度分布输出（诊断ref_low比sweep_low宽多少）</item>
    <item>Holdout未读取</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号或Regime参数</item>
    <item>禁止修改持仓期（固定为t+12）</item>
    <item>禁止在看到结果后调整止损定义</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 核心指标（Sharpe/MaxDD/Expectancy）
    2. 止损触发率变化（vs v4 的 sweep_low）
    3. 平均止损宽度（ref_low 平均比 sweep_low 宽多少 %）
    4. 更宽止损是否改善了策略表现？
    5. SOL 单独表现（是否仍拖累）
    6. 建议更新的 CURRENT_STATE 字段
    7. 若失败：主要失败原因（更宽止损是否反而增加了亏损金额？）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B7_V6_TIME_EXIT.md（v6，本任务基础）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B4_V4_STRATEGY_BACKTEST.md（v4基准）</file>
    <file>02_KNOWLEDGE_BASE/SWEEP_SIGNAL_FAILURE_LESSONS_v2.md（失败经验）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
