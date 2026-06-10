# Codex 任务：第五研究闭环——Bearish Sweep 做空事件研究

```xml
<task>
  <id>0B-3-v5</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    前四次实验全部只测试做多（Bullish Sweep）。
    永续合约支持双向交易，做空方向从未验证——这是研究覆盖缺口。
    本任务测试镜像信号：Bearish Liquidity Sweep 在熊市 Regime 下
    对未来收益率是否有显著负向预测力（即做空有正期望）。
    
    决策依据：DEC-032
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <single_variable>
    相比 v4（做多），唯一变化：信号方向和 Regime 方向完全镜像取反。
    sweep_lookback=20 等所有参数不变。
    t+6/12/24 窗口不变。
    统计方法：单侧 t-test，但方向改为 alternative="less"（H0: mean=0，期望均值<0）
  </single_variable>

  <bearish_sweep_definition>
    Bearish Liquidity Sweep（做空信号）：
    
    参数：sweep_lookback = 20（不变）
    
    条件（在第 i 根 4H K线上判断）：
      1. 参考高点：ref_high = max(high[i-sweep_lookback : i-1])
         （当前K线之前20根K线的最高价，不含当前K线）
      2. 扫荡发生：high[i] > ref_high
         （当前K线最高价突破了参考高点）
      3. 收盘回位：close[i] < ref_high
         （当前K线收盘价收回到参考高点下方）
      
      三条件同时满足 → Bearish Sweep，发生在第 i 根K线
    
    边界处理：
      - i < sweep_lookback 不判断
      - ref_high 使用 high 价格序列
  </bearish_sweep_definition>

  <bearish_regime>
    双层熊市 Regime（两条件同时满足，镜像于 v4）：
    
    条件1（镜像）：各品种前一完整 UTC 日收盘价 < 该日 Daily EMA200
      - EMA200：span=200，min_periods=200，shift(1)
    
    条件2（镜像）：BTC 30日对数收益率 < 0%
      - 计算：log(BTC_daily_close[t] / BTC_daily_close[t-30])，shift(1)
      - ETH/SOL 的条件2同样使用 BTC 数据
    
    注意：条件1中 ETH/SOL 使用各自品种的 Daily EMA200（不是 BTC 的）
  </bearish_regime>

  <future_returns>
    未来收益定义（做空视角，期望为负）：
    - future_ret_6  = log(close[t+6]  / close[t])
    - future_ret_12 = log(close[t+12] / close[t])
    - future_ret_24 = log(close[t+24] / close[t])
    
    注意：收益仍然以价格上涨为正、下跌为负来计算。
          做空方向成功意味着收益应该为负（价格下跌）。
    
    统计检验：单侧 t-test，alternative="less"（期望均值 < 0）
    预登记失效条件：三个窗口任意一个 p≥0.05，或均值≥0
  </future_returns>

  <inputs>
    <file>BTC/ETH/SOL 的 4H 和 Daily 数据（路径参见 REPORT_0B2）</file>
    <file>04_AI_TEAM/CODEX_TASKS/SPEC_0A6_SIGNAL_DEFINITIONS.md（Bearish Sweep是§一的镜像）</file>
  </inputs>

  <outputs>
    <file>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/bearish_sweep_event_study.py</file>
    <file>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/HYPOTHESES/v5_sweep_regime_bear_v5.md</file>
    <file>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bear_v5_EVAL.md</file>
    <file>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/CODEX_TASKS/REPORT_0B3_BEARISH_SWEEP.md</file>
    <file>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/output/events_v5_sweep_regime_bear_v5.csv</file>
  </outputs>

  <required_analysis>
    与 v4 完全对称的输出，便于直接对比：
    
    1. 事件数对比：
       | 品种 | Regime前 | Regime后 | 完整事件 |
       Bearish Regime 过滤后事件数
    
    2. 主检验（单侧 less）：
       | 窗口 | 均值 | 单侧p | 结论 |
       各品种独立 + 合并
    
    3. 与 v4（做多）对比表：
       | 窗口 | v4做多均值 | v4 p | v5做空均值 | v5 p |
       注意：做空期望为负，做多期望为正，方向相反才是对称信号
    
    4. 时期分层：2019-2020/2021/2022/2023-2024/2025
       重点：做空信号在 2022 熊市是否最强？（应该是）
    
    5. Walk-Forward 三段均值趋势
    
    6. 非重叠子集校正（同 v4，间隔>24根K线）
  </required_analysis>

  <acceptance>
    <item>Bearish Sweep 定义正确（high突破ref_high且close收回）</item>
    <item>双层熊市 Regime 正确（两条件均镜像于 v4）</item>
    <item>统计检验方向正确（alternative="less"）</item>
    <item>v4/v5 对比表完整</item>
    <item>时期分层完整（重点看2022表现）</item>
    <item>非重叠子集校正完整</item>
    <item>Holdout 物理截断，未读取</item>
    <item>执行报告包含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止修改 sweep_lookback=20 等参数</item>
    <item>禁止查看 Holdout</item>
    <item>禁止直接写入 Memory Core 文件</item>
    <item>禁止将做空信号与做多信号混合统计</item>
  </forbidden>

  <interpretation_note>
    做空信号的统计解读：
    - 如果 t+12 均值 = -1.5%，p=0.001（单侧 less）→ 做空有效
      表示 Bearish Sweep 后 48小时，价格平均下跌1.5%，做空可盈利
    - 如果 t+12 均值 = +0.3%，p=0.8 → 做空无效
      表示 Bearish Sweep 后价格没有明显下跌，不适合做空
    
    在报告中明确说明：「均值越负，做空信号越强」
  </interpretation_note>

  <report_to_claude>
    执行报告 REPORT_0B3 的「Claude 待处理事项」区域需包含：
    1. 做空信号是否通过（与做多对比）
    2. 是否支持设计双向策略（做多+做空组合）
    3. 建议 Claude 更新的 CURRENT_STATE 字段
    4. 是否需要新增 DECISION_LOG 条目（写草稿）
  </report_to_claude>

  <references>
    <file>04_AI_TEAM/CODEX_TASKS/TASK_0B2_SWEEP_DUAL_REGIME.md（v4做多，本任务的镜像）</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B2_SWEEP_DUAL_REGIME.md（v4基准数据）</file>
    <file>06_RESEARCH/RESULTS/20260606_v4_nonoverlap_validation.md（非重叠校正方法）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
