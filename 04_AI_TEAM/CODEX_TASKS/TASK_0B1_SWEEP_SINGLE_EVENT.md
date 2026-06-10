# Codex 任务：Phase 0B 第三研究闭环——Sweep 单事件收益分布验证

```xml
<task>
  <id>0B-1-v3</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <background>
    前两个研究闭环均已失败（v1=4H，v2=1H），Walk-Forward 均呈现衰减趋势。
    失败模式分析：三重确认链（Sweep+CHoCH+FVG+Retrace）组合过于严格，可能过滤掉了
    有效信号，或者信号之间的组合本身不稳定。
    
    降维方向：先验证 Liquidity Sweep 单事件是否携带价格信息，再决定是否有必要
    加入 CHoCH、FVG 等后续条件。这是标准的因子研究路径——先验证因子的预测力，
    再构建交易规则。
    
    协作规范：参见 04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </background>

  <hypothesis_v3>
    版本号：v5_sweep_only_bull_v3
    
    研究问题：在 Daily EMA200 多头 Regime 下，BTC/ETH/SOL 发生 Bullish Liquidity Sweep
    后的第 6、12、24 根 4H K线收盘收益率分布，是否显著偏正？
    
    这是一个统计检验任务，不是完整策略回测。
    不需要入场、止盈、止损规则——只需要统计「Sweep 后 N 根K线的未来收益」。
    
    Sweep 定义：沿用 SPEC_0A6_SIGNAL_DEFINITIONS.md §一中的完整定义（sweep_lookback=20）。
    Regime 定义：前一完整 UTC 日收盘价 > 该日 Daily EMA200。
    
    研究假设：Sweep 后第 6/12/24 根 4H K线（约24h/48h/96h后）的未来对数收益率均值 > 0，
    且在统计显著性检验（t-test，p < 0.05）下成立。
    
    失效条件：任意一个时间窗口的均值收益率在统计检验下不显著（p ≥ 0.05），
    或收益率均值 ≤ 0。
  </hypothesis_v3>

  <inputs>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/BTC_USDT_4H.csv</path>
      <desc>BTC 4H K线，datetime/open/high/low/close/volume</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/CODEX_TASKS/SPEC_0A6_SIGNAL_DEFINITIONS.md</path>
      <desc>Liquidity Sweep 定义（§一），严格遵守</desc>
    </file>
    <note>ETH 和 SOL 数据路径由 Codex 确认（上一任务已下载，路径参见 REPORT_0A6 或同目录）</note>
  </inputs>

  <outputs>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/sweep_event_study.py</path>
      <desc>事件研究主程序</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/HYPOTHESES/v5_sweep_only_bull_v3.md</path>
      <desc>假设预登记文档（按 Research Protocol §三格式）</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/RESULTS/20260606_v5_sweep_only_bull_v3_EVAL.md</path>
      <desc>实验结论报告（按 Research Protocol §八格式）</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/CODEX_TASKS/REPORT_0B1_SWEEP_EVENT_STUDY.md</path>
      <desc>执行报告（Codex 写给 Claude 看的，含需要 Claude 更新到 Memory Core 的内容）</desc>
    </file>
  </outputs>

  <implementation_steps>
    步骤1：数据加载与预处理
    - 加载 BTC/ETH/SOL 的 4H 和 Daily 数据
    - 计算每个交易日的 EMA200（基于 Daily 收盘价）
    - 标记多头 Regime：前一完整 UTC 日收盘价 > Daily EMA200

    步骤2：Sweep 事件检测
    - 使用 SPEC_0A6_SIGNAL_DEFINITIONS.md §一的精确定义
    - 在 Regime 过滤后保留有效 Sweep 事件（按 DEC-025 去重规则）
    - 统计各品种 Sweep 事件数

    步骤3：事件研究（Event Study）
    对每个 Sweep 事件，计算：
    - future_ret_6  = log(close[t+6] / close[t])   # Sweep K线收盘后第6根K线
    - future_ret_12 = log(close[t+12] / close[t])
    - future_ret_24 = log(close[t+24] / close[t])
    
    注意：t 是 Sweep 发生的 K线索引，确保使用未来数据（不构成前视偏差，因为是研究收益）

    步骤4：统计检验
    对每个时间窗口（6/12/24），分别计算：
    - 收益率均值（mean）
    - 收益率标准差（std）
    - t 统计量和 p 值（scipy.stats.ttest_1samp，H0: mean=0）
    - 正收益率占比（hit rate）
    - 中位数收益率
    
    输出：按品种（BTC/ETH/SOL）和合并（三品种）分别统计

    步骤5：数据分层分析（重要）
    按市场时期分层（参考 DEC-028 发现的时期集中风险）：
    - 2019-2020（早期）
    - 2021（牛市）
    - 2022（熊市）
    - 2023-2024（复苏）
    - 2025-2026（当前）
    各时期分别统计均值和 p 值，检验是否有时期依赖性

    步骤6：Walk-Forward 稳定性检验
    将数据按时间分3段，每段独立计算 t+12 的收益率均值，
    观察是否跨时段稳定（不要求 p<0.05，只观察方向是否一致）
  </implementation_steps>

  <constraints>
    <item>只使用 pandas、numpy、scipy（scipy.stats），不引入新依赖</item>
    <item>Sweep 定义必须 100% 遵守 SPEC §一，不得修改参数</item>
    <item>Holdout（最后20%数据）物理截断，不得参与任何分析，不得打印或查看</item>
    <item>这是事件研究，不是策略回测，不需要考虑手续费/滑点（纯统计分析）</item>
    <item>禁止修改 01_MEMORY_CORE/ 下的文件（参见 COLLABORATION_RULES.md）</item>
  </constraints>

  <acceptance>
    <item>三品种 Sweep 事件数统计清晰，有 Regime 过滤前后对比</item>
    <item>t+6/12/24 三个时间窗口的均值、p值、hit rate 完整输出</item>
    <item>按市场时期分层的子样本统计完整</item>
    <item>Walk-Forward 三段稳定性观察完整</item>
    <item>假设预登记文档已写入 06_RESEARCH/HYPOTHESES/（包含 Holdout 范围声明）</item>
    <item>结论报告给出明确判断：「Sweep 单事件有统计显著的正向预测力」或「无」</item>
    <item>执行报告中单独列出「需 Claude 更新到 DECISION_LOG 的内容」（如发现新的决策性结论）</item>
  </acceptance>

  <forbidden>
    <item>禁止查看或使用 Holdout 数据（最后20%）</item>
    <item>禁止根据结果修改 Sweep 定义参数</item>
    <item>禁止直接写入 DECISION_LOG 或 CURRENT_STATE（写执行报告，Claude 来升级）</item>
    <item>禁止将事件研究结果直接声称为完整策略有效</item>
  </forbidden>

  <report_to_claude>
    执行报告 REPORT_0B1 中，专门写一节「Claude 待处理事项」，包含：
    1. 是否需要在 DECISION_LOG 新增决策条目（写出草稿，Claude 审阅后决定）
    2. CURRENT_STATE 需要更新的字段
    3. 发现的规格问题或模糊点
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/SPEC_0A6_SIGNAL_DEFINITIONS.md（Sweep定义）</file>
    <file>06_RESEARCH/RESEARCH_PROTOCOL_v1.md（研究协议）</file>
    <file>02_KNOWLEDGE_BASE/STRUCTURE_SETUP_FAILURE_LESSONS_v1.md（失败经验）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md（文件协作规范）</file>
  </references>
</task>
```
