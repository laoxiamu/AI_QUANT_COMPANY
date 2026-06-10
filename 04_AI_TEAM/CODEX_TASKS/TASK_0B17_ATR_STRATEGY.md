# Codex 任务：ATR×1.9 止损策略回测

```xml
<task>
  <id>0B-17-strategy</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>策略回测，计入失败计数（若失败则7/8）</type>

  <context>
    决策依据（DEC-042）：
      三项诊断（0B14/0B15/0B16）完成，MAE法与ATR诊断法从独立角度收敛于同一止损位：
        - 0B14：盈利交易MAE 80th percentile = 4.38% = 1.87x ATR(14)
        - 0B16：ATR×1.9 覆盖 81.45% 盈利MAE，理论可避免 61.43% 历史止损
      这是目前对止损位置最强的数据依据。
    
    前序实验失败原因（已确认）：
      - v6（sweep_low止损）：止损平均2.33%，63.71%盈利交易MAE超过此值
      - v6b（ref_low止损）：止损平均1.38%，止损更紧，仓位虽大但早停比例更高
      - 两者都因止损在正常噪声范围内被触发，没有给信号时间生效
    
    本实验核心假设：
      ATR×1.9 的动态止损随市场波动自动调整，给信号足够的噪声空间，
      同时1%风险定仓使名义仓位约22.8%（vs v6b约72%），MaxDD应大幅改善。
    
    预登记门槛（DEC-042）：Sharpe > 1.0 AND MaxDD < 25%
    失败计数：若通过 → 保持6/8；若失败 → 7/8（仅剩1次）
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <signal_regime>
    信号：v4（与前所有实验相同，不得修改）
      - Bullish Liquidity Sweep：low[i] < min(low[i-20:i-1]) AND close[i] > min(low[i-20:i-1])
      - Regime 双层过滤（前视偏差均使用shift(1)）：
          条件1：各品种前一完整UTC日收盘价 > 该日Daily EMA200（shift 1）
          条件2：BTC前一完整日30日对数收益率 > 0%（shift 1）
    品种：BTC/USDT、ETH/USDT、SOL/USDT，4H永续合约，仅做多
    数据范围：前80%（训练集），不读取Holdout
    事件基准：425个v4事件（events_v5_sweep_regime_bull_v4.csv）
  </signal_regime>

  <stop_loss>
    止损类型：ATR动态止损（主测ATR×1.9，附加ATR×3.5压力测试）
    
    止损价格计算：
      ATR(14)[t_sweep] = Sweep K线时刻可见的14根4H K线TrueRange简单均值
      （使用Sweep K线本身的ATR值，无前视偏差）
      
      stop_price_1_9 = entry_price - ATR(14)[t_sweep] × 1.9
      stop_price_3_5 = entry_price - ATR(14)[t_sweep] × 3.5
      
      entry_price = 信号后下一根K线开盘价（含滑点：entry × 1.001）
    
    止损触发：收盘价或K线内最低价跌破stop_price时，该根K线收盘退出
    （与前所有版本相同的止损逻辑）
    
    注意事项：
      - ATR×1.9平均约4.1%，但会随各品种和时期的波动率动态变化
      - SOL ATR通常更大，止损距离也更大，这是合理的自然调整
      - 极端低ATR时（ATR×1.9 < 1%），名义仓位上限设为100%
  </stop_loss>

  <position_sizing>
    方法：1%风险定仓
    
    计算：
      risk_distance = ATR(14)[t_sweep] × 1.9  （以价格表示）
      risk_pct = risk_distance / entry_price    （百分比形式）
      position_size = 1% × portfolio_value / risk_distance
      nominal_pct = position_size × entry_price / portfolio_value
      
    安全约束：
      - 单笔最大名义仓位：100%（防止ATR极小时过度放大）
      - 持仓冲突：同品种已有开仓时，新信号不开仓（与前所有版本一致）
    
    初始资金：100,000 USDT（与前所有回测一致）
  </position_sizing>

  <exit_rules>
    主要退出：t+24时间退出
      - 入场后第24根4H K线收盘退出（即6天后）
      - 含滑点：exit × 0.999
    
    止损退出（优先于时间退出）：
      - 止损触发时当根K线收盘退出
      - 止损优先于同K线止盈（无止盈设置）
    
    无跟踪止盈：本实验不设止盈，纯时间+止损双出口
  </exit_rules>

  <costs>
    手续费：开仓+平仓各0.05%（共0.10%，Taker费率）
    滑点：开仓entry×1.001，平仓exit×0.999（各0.1%）
    资金费率：0.01%/8h近似（与前所有版本相同）
    合计摩擦：约0.4%/笔（不得省略）
  </costs>

  <required_outputs>
    主输出（ATR×1.9版本）：
    
    一、总体结果（三品种合并）
      | 指标 | 数值 |
      |------|------|
      | Sharpe Ratio | ? |
      | MaxDD | ? |
      | 总交易数 | ? |
      | 胜率 | ? |
      | 止损率 | ? |
      | 平均持仓时长（根） | ? |
      | 平均名义仓位% | ? |
      
    二、品种分层（必须独立报告）
      | 品种 | Sharpe | MaxDD | 交易数 | 止损率 | 均名义仓位% |
      |------|--------|-------|--------|--------|------------|
      | BTC | ? | ? | ? | ? | ? |
      | ETH | ? | ? | ? | ? | ? |
      | SOL | ? | ? | ? | ? | ? |
      
    三、Walk-Forward三段（必须独立报告）
      | 段 | 大致时期 | Sharpe | MaxDD |
      |----|---------|--------|-------|
      | WF1 | 前1/3 | ? | ? |
      | WF2 | 中1/3（包含2022）| ? | ? |
      | WF3 | 后1/3 | ? | ? |
      
    四、与基准版本对比表
      | 版本 | 止损类型 | 止损率 | Sharpe | MaxDD | 结论 |
      |------|---------|--------|--------|-------|------|
      | v6（sweep_low） | 结构止损2.33% | ? | 0.87 | 36.32% | ❌ |
      | v6b（ref_low） | 结构止损1.38% | ? | 1.22 | 28.45% | ❌ |
      | 0B12（无止损） | 无 | 0% | 1.28 | 12.06% | 仓位不可比 |
      | **0B17（ATR×1.9）** | ATR动态4.1% | ? | ? | ? | **待测** |
      
    五、ATR×3.5压力测试（附加，不计独立失败）
      仅报告Sharpe和MaxDD，用于理解止损宽度对结果的影响
      
    六、2022年单独分析
      2022年（约2021-11至2022-12）的交易数、止损率、净盈亏
      ATR×1.9是否比结构止损在2022有所改善？
  </required_outputs>

  <pre_registration_criteria>
    通过条件（DEC-042）：Sharpe > 1.0 AND MaxDD < 25%（三品种合并，ATR×1.9版本）
    
    失败条件（任一）：
      - Sharpe ≤ 1.0
      - MaxDD ≥ 25%
    
    失败后失败计数：7/8（仅剩1次机会，下次失败触发L3全面审计）
    
    注意：BTC+ETH子集、WF段、品种分层均不单独计入通过/失败，
          仅用于诊断分析。
  </pre_registration_criteria>

  <data_inputs>
    事件文件（冻结）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    
    4H OHLCV价格数据（计算ATR和回测）：
      与前所有版本相同的数据源
    
    参考代码：
      06_RESEARCH/CODE/sweep_dual_regime.py（信号+Regime参数）
      06_RESEARCH/CODE/v12_no_stop_diagnostic.py（t+24退出逻辑参考）
      06_RESEARCH/CODE/v16_atr_stop_diagnostic.py（ATR计算参考，必须使用相同方法）
    
    参考报告：
      04_AI_TEAM/CODEX_TASKS/REPORT_0B14_MAE_ANALYSIS.md（止损参数依据）
      04_AI_TEAM/CODEX_TASKS/REPORT_0B16_ATR_STOP_DIAGNOSTIC.md（ATR实现参考）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v17_atr_strategy.py</file>
    <file>06_RESEARCH/RESULTS/20260606_atr_strategy.md</file>
    <file>06_RESEARCH/CODE/output/v17_atr_equity_curve.png</file>
    <file>06_RESEARCH/CODE/output/v17_atr_trades.csv</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B17_ATR_STRATEGY.md</file>
  </outputs>

  <acceptance>
    <item>ATR使用Sweep K线可见的14根TR简单均值（无前视偏差），与0B16完全相同的计算方法</item>
    <item>1%风险定仓正确实现（position_size = 1% × portfolio / risk_distance）</item>
    <item>名义仓位100%上限已设置</item>
    <item>三品种分层结果独立报告</item>
    <item>Walk-Forward三段独立报告</item>
    <item>ATR×3.5压力测试附加报告</item>
    <item>明确宣告通过或失败（Sharpe > 1.0 AND MaxDD < 25%）</item>
    <item>与v6/v6b/0B12的对比表完整</item>
    <item>Holdout未读取</item>
    <item>pytest 9/9通过（止损优先、持仓冲突、资金费率）</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号参数或Regime条件</item>
    <item>禁止使用固定百分比止损（必须基于ATR动态计算）</item>
    <item>禁止直接写入Memory Core文件</item>
    <item>禁止省略成本（手续费+滑点+资金费率）</item>
  </forbidden>

  <report_to_claude>
    1. 明确宣告：通过 or 失败（Sharpe > 1.0 AND MaxDD < 25%）
    2. 三品种合并的Sharpe和MaxDD（ATR×1.9版本）
    3. 止损率（vs v6b的58%和v6的52%）
    4. 平均名义仓位%（vs v6b约72%，应显著更小）
    5. WF2（含2022段）的Sharpe和MaxDD
    6. ATR×3.5压力测试的Sharpe和MaxDD
    7. 若失败：最可能的失败原因（MaxDD超标？Sharpe不足？WF2拖累？）
    8. 若通过：建议是否直接进入Holdout测试（或先做什么）
    9. 建议更新的CURRENT_STATE字段和失败计数
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B14_MAE_ANALYSIS.md（止损参数依据）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B15_VOL_COMPRESSION.md（已否定过滤层）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B16_ATR_STOP_DIAGNOSTIC.md（ATR计算参考）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B12_NO_STOP_DIAGNOSTIC.md（t+24退出参考）</file>
    <file>01_MEMORY_CORE/DECISION_LOG.md（DEC-041/042）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
