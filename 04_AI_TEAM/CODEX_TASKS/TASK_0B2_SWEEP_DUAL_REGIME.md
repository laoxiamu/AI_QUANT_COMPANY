# Codex 任务：第四研究闭环——Sweep + 双层 Regime 验证

```xml
<task>
  <id>0B-2-v4</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <single_variable_change>
    相比第三个实验（v5_sweep_only_bull_v3），本次唯一的变量变化是：
    在原有「Daily close > Daily EMA200」的基础上，
    叠加第二层 Regime 条件：「BTC 30日滚动收益率 > 0%」
    
    其他一切保持不变：
    - Sweep 定义：SPEC_0A6_SIGNAL_DEFINITIONS.md §一，sweep_lookback=20
    - 研究方法：事件研究（统计检验），不是策略回测
    - 时间窗口：t+6、t+12、t+24
    - 统计检验：单侧 t-test（H0: mean=0，alternative="greater"，p<0.05）
    - 品种：BTC、ETH、SOL（4H），合并检验
    - 失效条件：三个时间窗口任意一个 p≥0.05，或均值≤0
  </single_variable_change>

  <new_regime_definition>
    双层 Regime（两条件必须同时满足）：
    
    条件1（不变）：前一完整 UTC 日的收盘价 > 该日的 Daily EMA200
      - EMA200 计算：基于 Daily 收盘价，span=200，min_periods=200
      - 使用 shift(1) 避免前视偏差（与 v3 相同）
    
    条件2（新增）：BTC 30日滚动收益率 > 0%
      - 计算方式：log(BTC_daily_close[t] / BTC_daily_close[t-30])
      - 使用 BTC 数据（不是各品种自己的 30 日收益）作为统一市场动量指标
      - 同样使用 shift(1)（前一完整日数值），避免前视偏差
      - 说明：SOL 和 ETH 的 Regime 条件中，动量部分使用 BTC 的 30 日收益，
              因为 BTC 是整个加密市场的主导指标
    
    数据计算顺序：
      1. 用 Daily BTC 数据计算 EMA200 和 30日收益
      2. 将 Daily 数据 merge 到 4H 数据（按日期对齐，shift(1)）
      3. 对 ETH/SOL 的 Regime 中，条件1用各自品种的 Daily close vs EMA200，
         条件2统一用 BTC 的 30日收益
  </new_regime_definition>

  <inputs>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/BTC_USDT_4H.csv</path>
      <desc>BTC 4H K线</desc>
    </file>
    <note>ETH 和 SOL 的 4H 和 Daily 数据路径参见上一个任务的执行报告（REPORT_0B1）</note>
    <note>如果 Daily BTC 数据已存在，直接使用；如果没有单独的 Daily 文件，
          可以从 4H 数据 resample 到 Daily（取每日最后一根4H K线的收盘价作为日收盘）</note>
  </inputs>

  <outputs>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/sweep_dual_regime.py</path>
      <desc>双层 Regime 事件研究程序</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_v4.md</path>
      <desc>假设预登记文档</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md</path>
      <desc>实验结论报告（Research Protocol §八格式）</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/CODEX_TASKS/REPORT_0B2_SWEEP_DUAL_REGIME.md</path>
      <desc>执行报告（含「Claude 待处理事项」区域）</desc>
    </file>
  </outputs>

  <required_analysis>
    在主检验之外，必须包含以下对比分析：
    
    1. Regime 过滤效果对比：
       - 原单层 Regime（v3）：748 个事件
       - 新双层 Regime（v4）：N 个事件（实际统计）
       - 各时期的事件分布（2019-2020/2021/2022/2023-2024/2025）
    
    2. 主检验（同 v3 格式，便于直接对比）：
       | 窗口 | v3均值 | v3 p值 | v4均值 | v4 p值 | 变化 |
       各品种独立 + 合并
    
    3. Walk-Forward 三段稳定性（同 v3）：
       观察 t+12 三段均值是否仍有衰减，还是趋于稳定
    
    4. 时期分层（重点）：
       v4 的 2021/2022/2023-2024 各自的均值和显著性
       重点检查：v3 中 2022 为负的问题，v4 是否已被过滤掉
  </required_analysis>

  <acceptance>
    <item>双层 Regime 计算正确（EMA200 + BTC 30日收益，均使用 shift(1)）</item>
    <item>实际事件数明确（v4 vs v3 对比输出）</item>
    <item>t+6/12/24 三窗口主检验完整（单侧 t-test）</item>
    <item>时期分层分析完整（重点：v4 能否过滤掉 v3 的负贡献时期）</item>
    <item>Walk-Forward 三段均值趋势完整</item>
    <item>Holdout 物理截断，未读取</item>
    <item>假设预登记文档已写（含 Holdout 范围声明）</item>
    <item>结论报告给出明确判断：「双层 Regime 下 Sweep 预测力显著且时期稳定」或「仍不稳定」</item>
    <item>执行报告包含「Claude 待处理事项」区域（参见 COLLABORATION_RULES.md）</item>
  </acceptance>

  <forbidden>
    <item>禁止修改 Sweep 定义参数（sweep_lookback=20 等）</item>
    <item>禁止同时改变两个以上变量（单变量原则）</item>
    <item>禁止查看 Holdout 数据</item>
    <item>禁止直接写入 DECISION_LOG 或 CURRENT_STATE</item>
    <item>如果事件数 < 100，在执行报告中标注「样本过少，结论不可靠」</item>
  </forbidden>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/SPEC_0A6_SIGNAL_DEFINITIONS.md（Sweep定义）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B1_SWEEP_EVENT_STUDY.md（v3基准数据）</file>
    <file>06_RESEARCH/RESEARCH_PROTOCOL_v1.md（研究协议）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md（文件协作规范）</file>
    <file>01_MEMORY_CORE/DECISION_LOG.md（DEC-031，本任务决策依据）</file>
  </references>
</task>
```
