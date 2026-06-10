# Codex 任务：t+24 无止损诊断

```xml
<task>
  <id>0B-12-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断分析，不计入失败计数</type>

  <context>
    当前状态：失败计数 6/8，再失败2次触发L3全面审计。
    
    0B9 止损诊断揭示：止损触发中位数为第1根K线，80%在t+6之前触发。
    0B8 时间敏感性显示：t+24纯时间退出的三品种Sharpe=1.31（未达门槛因MaxDD>25%）。
    
    本任务的研究问题：
    如果完全不设止损，让每笔交易从入场持有到t+24收盘，
    Sharpe和MaxDD分别是多少？
    
    这回答了：「止损是帮助还是伤害？」
    
    如果无止损 Sharpe >> 1.31（比纯时间退出还好）：
      说明止损不仅没有帮助，还因小样本噪声在错误时机截断了交易。
      → 值得探索「先让信号充分发展，再用移动止损保护盈利」的结构。
    
    如果无止损 Sharpe ≈ 1.31（与纯时间退出接近）：
      说明止损对结果影响不大，MaxDD问题来自盈亏分布本身。
      → 需要从信号层面或Regime层面降低单笔亏损。
    
    如果无止损 Sharpe 明显 < 1.31：
      说明存在编码/数据问题，需要排查。
      
    此任务不占用失败计数。目的是提供信息，不是验证假设。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <strategy_spec>
    与 v6（TASK_0B7）完全相同，仅以下修改：
    
    【删除】止损：移除所有止损逻辑（不设止损价，不在任何K线触发止损）
    【修改】退出：持有至入场后第24根4H K线收盘退出（t+24，96小时）
    【不变】信号：Bullish Sweep（sweep_lookback=20，v4定义）
    【不变】Regime：双层（EMA200 + BTC 30日动量>0，shift(1)）
    【不变】品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多
    【不变】入场：信号K线下一根K线开盘价
    【不变】持仓冲突：同品种同向有仓时拒绝新信号
    【不变】仓位：固定名义仓位（由于无止损，改为固定每笔名义金额：账户净值/10，即每笔10%资金）
    【不变】成本：手续费0.04%，滑点0.05%，历史资金费率
    【不变】时间范围：前80%数据，Holdout封存

    仓位说明：
      原策略仓位 = (账户净值×1%) / 风险距离
      无止损时风险距离为0，无法用此公式。
      改为：每笔固定名义金额 = 账户净值 × 10%（初始100,000 USDT → 每笔10,000 USDT）
      注意：此仓位方式与有止损版本不可直接比较收益率，但Sharpe和MaxDD的相对大小仍有参考价值。
      
    同时输出 BTC+ETH 双品种子集（去除SOL）。
  </strategy_spec>

  <key_comparison>
    报告中必须呈现以下对比表：
    
    | 指标 | v4策略（sweep_low+TP1R2R）| v6b（ref_low+t+12）| 0B8 t+24纯时间 | 本次无止损t+24 |
    |------|------------------------:|------------------:|---------------:|---------------:|
    | 实际交易数 | 360 | 373 | (0B8结果) | ? |
    | Sharpe | 0.31 | 1.22 | 1.31 | ? |
    | MaxDD | 19.08% | 28.45% | 37.63% | ? |
    | 止损率 | 58.33% | 71.85% | 0% | 0% |
    | 平均持仓K线 | — | — | ~24 | ~24 |
    | 成本占毛利 | 54.64% | — | — | ? |
  </key_comparison>

  <required_analysis>
    1. 核心指标（Sharpe/MaxDD/净收益率）
    2. 无止损 vs 0B8 t+24纯时间退出的对比（理论上应接近，差异来自仓位计算方式）
    3. 盈亏分布：最大单笔亏损（无止损会有大的单笔回撤）
    4. 按时期：2022年净收益和MaxDD（无止损时2022会特别难看）
    5. Walk-Forward三段（三品种+BTC+ETH双品种）
    6. 资金曲线图（显示无止损的「直线跌到底再反弹」形态）
  </required_analysis>

  <outputs>
    <file>06_RESEARCH/CODE/v12_no_stop_diagnostic.py</file>
    <file>06_RESEARCH/RESULTS/20260606_no_stop_t24_diagnostic.md</file>
    <file>06_RESEARCH/CODE/output/no_stop_equity_curve.png</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B12_NO_STOP_DIAGNOSTIC.md</file>
  </outputs>

  <acceptance>
    <item>止损逻辑完全删除（不是放宽，是删除）</item>
    <item>持仓期固定24根K线</item>
    <item>仓位使用固定名义金额（10%账户净值），并在报告中说明与有止损版本不可比</item>
    <item>三品种 + BTC+ETH 双品种均报告</item>
    <item>四版本对比表完整</item>
    <item>Walk-Forward三段报告</item>
    <item>Holdout未读取</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改信号或Regime参数</item>
    <item>禁止将本次结果与有止损版本直接比较净收益率（仓位计算方式不同）</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 无止损t+24 Sharpe和MaxDD（三品种+BTC+ETH）
    2. 与0B8 t+24纯时间退出的Sharpe对比（差异多大？）
    3. 最大单笔亏损（无止损时的极端情况）
    4. 2022年表现（无止损2022是否灾难性）
    5. 核心诊断结论：
       - 如果无止损Sharpe >> 1.31 → 止损设计有大改进空间，建议ATR止损
       - 如果无止损Sharpe ≈ 1.31 → 止损影响有限，MaxDD问题在盈亏分布
       - 如果无止损Sharpe < 1.31 → 需要排查逻辑
    6. 建议下一步（供Claude决策参考）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B8_TIME_SENSITIVITY.md（0B8 t+24数据）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B9_STOP_DIAGNOSTIC.md（止损诊断）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B10_WIDER_STOP.md（v6/v6b结果）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
