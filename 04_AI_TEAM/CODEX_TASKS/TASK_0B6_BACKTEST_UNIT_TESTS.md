# Codex 任务：回测规则自动测试套件（P1-4）

```xml
<task>
  <id>0B-6-v5</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    Phase 0A L2 审计 P1-4 问题：「回测自动测试未完整覆盖」。
    
    目前回测规则（止损优先、持仓冲突、资金费率）只做过手工验证，
    没有可重复运行的自动化测试。这意味着每次修改回测代码，
    都可能静默破坏关键规则而无法察觉。
    
    本任务写一套 pytest 单元测试，覆盖三条最关键的回测规则，
    可在每次更新回测代码后一键验证规则是否仍正确执行。
    
    测试不依赖真实数据——全部使用构造的最小合成数据集。
    这是基础设施建设，不是研究任务。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <test_cases>
    必须覆盖的三条规则：
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    规则1：同K线止损优先于止盈
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    场景描述：
      入场价 100，止损价 98（-2%），止盈1目标 102（+2%，50%仓位）
      构造一根K线：open=100, high=103, low=97, close=100
      → 该K线同时触及止损(97<98)和止盈(103>102)
      预期结果：执行止损，亏损约-2%；不执行止盈
    
    测试变种：
      a. 正常止盈K线（不触及止损）→ 正确止盈
      b. 正常止损K线（不触及止盈）→ 正确止损
      c. 同时触及 → 止损优先
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    规则2：持仓冲突——同品种同向拒绝
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    场景描述：
      在T=0开了BTC多仓（未平仓）
      在T=5又出现BTC多头信号
      预期结果：T=5的BTC多头信号被拒绝，持仓数量不变
    
    测试变种：
      a. BTC有多仓 + BTC新多头信号 → 拒绝
      b. BTC有多仓 + ETH新多头信号 → 正常开仓（不同品种不受限）
      c. BTC多仓平仓后 + BTC新多头信号 → 正常开仓
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    规则3：资金费率计算正确性
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    场景描述：
      持仓从T=0持有到T=24（24根4H K线 = 4天）
      期间经历3次资金费率结算（UTC 0:00/8:00/16:00各一次）
      使用固定利率 0.01%/8h
      预期：总资金费率成本 = 持仓价值 × 0.01% × 3次
    
    测试变种：
      a. 标准持仓期（验证结算次数正确）
      b. 持仓跨越多个结算点（验证不漏算、不多算）
      c. 已平仓后不再计入资金费率
    
    额外测试（可选，若时间允许）：
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    规则4：Walk-Forward 边界不泄露
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      第N段训练集的K线数据不包含第N+1段的任何数据点
      预期：segment 1 结束时间 < segment 2 开始时间，无重叠
  </test_cases>

  <implementation_note>
    测试框架：pytest
    
    实现建议：
    - 不依赖 ccxt 或真实数据文件，全部用 pandas DataFrame 构造最小数据集
    - 每个规则写独立的 test_rule_X.py 或合并到 test_backtest_rules.py
    - 测试应该在 < 5秒内全部通过（无需网络请求）
    - 使用 assert 明确验证预期结果，不要用 print 代替断言
    
    如果当前回测代码（v4_strategy_backtest.py）尚未存在或不可导入，
    可以写「测试优先」的实现：
      - 先写测试
      - 在同一个文件中写一个最小化的回测函数让测试通过
      - 注释标注「此函数供测试用，正式回测见 v4_strategy_backtest.py」
  </implementation_note>

  <outputs>
    <file>06_RESEARCH/CODE/tests/test_backtest_rules.py</file>
    <file>06_RESEARCH/CODE/tests/README_TESTS.md（说明如何运行）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B6_BACKTEST_UNIT_TESTS.md</file>
  </outputs>

  <acceptance>
    <item>pytest 运行后全部 PASSED，无 FAILED 或 ERROR</item>
    <item>三条规则（止损优先/持仓冲突/资金费率）各有至少2个测试变种</item>
    <item>测试不依赖真实数据文件</item>
    <item>执行报告包含 pytest 输出截图或文本</item>
    <item>README 说明运行命令（如 cd 06_RESEARCH/CODE && pytest tests/）</item>
    <item>执行报告包含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止直接写入 Memory Core 文件</item>
    <item>测试不得依赖网络请求（离线可运行）</item>
  </forbidden>

  <report_to_claude>
    执行报告 REPORT_0B6 的「Claude 待处理事项」须包含：
    1. 所有测试是否通过（PASS/FAIL统计）
    2. P1-4 审计项是否可标记为已解决
    3. 发现的任何现有回测代码的潜在 bug（如有）
    4. 建议更新的 CURRENT_STATE 字段（写草稿）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
    <file>00_PROJECT_MANAGEMENT/STAGE_AUDITS/L2_AUDIT_PHASE_0A_2026-06-06.md（P1-4来源）</file>
  </references>
</task>
```
