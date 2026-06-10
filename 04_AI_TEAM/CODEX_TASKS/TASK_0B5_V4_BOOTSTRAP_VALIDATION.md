# Codex 任务：v4 Bootstrap 置换检验

```xml
<task>
  <id>0B-5-v5</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <context>
    v4 事件研究使用标准 t 检验，p 值显著（t+12: p<0.000001）。
    但 v4 的评估报告明确标注了两个潜在问题：
      1. 事件窗口重叠：同一品种相邻事件的 t+12/t+24 窗口可能重叠，
         违反独立性假设，导致 p 值偏乐观
      2. 跨品种相关性：BTC/ETH/SOL 同期走势高度相关，
         合并三品种后有效样本数远低于 425
    
    本任务使用 Bootstrap 置换检验（permutation test）提供更保守、
    更可信的 p 值估计。这不是重新验证假设，而是对已通过假设的
    稳健性校验——让结论更难被攻击。
    
    若 Bootstrap 仍通过 → v4 信号可信度大幅提升
    若 Bootstrap 不通过 → 需在 DECISION_LOG 记录信号强度存疑
    
    决策依据：DEC-031（v4方向确认）、非重叠校正已在
              20260606_v4_nonoverlap_validation.md 中完成（N=215仍通过），
              本任务是更严格的第三层校验。
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <method>
    方法A：Block Bootstrap（首选）
    
    核心思路：保留事件的时间结构，打破"信号→未来收益"的对应关系，
    检验观察到的均值是否超过随机基准。
    
    步骤：
    1. 加载 events_v5_sweep_regime_bull_v4.csv（425个事件）
    
    2. 计算观察值：
       - obs_mean_6  = mean(future_ret_6)
       - obs_mean_12 = mean(future_ret_12)
       - obs_mean_24 = mean(future_ret_24)
    
    3. Bootstrap置换（N=10000次）：
       对于每一次置换：
         - 对每个品种独立做时间块打乱（block_size = 20根4H K线 ≈ 80小时）
         - 重新抽取该品种的未来收益序列（保留块内相关结构）
         - 计算三个品种合并后的均值
       得到 null_distribution（10000个均值）
    
    4. p 值计算（单侧，期望均值>0）：
       p_bootstrap_6  = mean(null_distribution_6  >= obs_mean_6)
       p_bootstrap_12 = mean(null_distribution_12 >= obs_mean_12)
       p_bootstrap_24 = mean(null_distribution_24 >= obs_mean_24)
    
    方法B（可选，作为对照）：简单置换检验
       - 将 425 个事件的 future_ret 随机重排 10000 次（不保留块结构）
       - 同样计算 p 值
       - 与方法A并排展示，说明差异
    
    参数选择说明：
    - block_size=20 是根据 4H 数据的自相关特性选择的合理值
    - N=10000 足够稳定，计算时间约 1-2 分钟
    - 如果方法A实现困难，方法B也可接受，但需在报告中标注局限性
  </method>

  <inputs>
    <file>06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md（原始t检验结果参照）</file>
    <file>06_RESEARCH/RESULTS/20260606_v4_nonoverlap_validation.md（非重叠215事件校正结果）</file>
  </inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v4_bootstrap_validation.py</file>
    <file>06_RESEARCH/RESULTS/20260606_v4_bootstrap_validation.md</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B5_V4_BOOTSTRAP.md</file>
  </outputs>

  <required_output_table>
    报告的核心表格（三种检验方法对比）：
    
    | 窗口 | t检验均值 | t检验p | 非重叠t检验p(N=215) | Bootstrap p(N=10000) | 结论 |
    |------|----------:|-------:|-------------------:|--------------------:|------|
    | t+6  | +0.770%   | 0.000078 | 0.0213           | ?                  | ?    |
    | t+12 | +1.364%   | <0.000001 | 0.0001          | ?                  | ?    |
    | t+24 | +2.337%   | <0.000001 | <0.0001         | ?                  | ?    |
    
    （t检验和非重叠检验的值已知，Bootstrap值为本任务产出）
    
    同时报告：
    - null distribution 的均值和标准差
    - 观察值在 null distribution 中的百分位（如"超过99.5%的随机样本"）
    - Bootstrap 置信区间（95% CI）
  </required_output_table>

  <acceptance>
    <item>Block Bootstrap 正确实现（每个品种独立打乱，再合并）</item>
    <item>N=10000 次置换</item>
    <item>三种方法对比表完整</item>
    <item>null distribution 可视化（直方图 + 观察值位置）</item>
    <item>结论明确：Bootstrap 是否支持 v4 信号可信</item>
    <item>执行报告包含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看 Holdout 数据</item>
    <item>禁止修改 v4 的任何参数</item>
    <item>禁止直接写入 Memory Core 文件</item>
  </forbidden>

  <report_to_claude>
    执行报告 REPORT_0B5 的「Claude 待处理事项」须包含：
    1. Bootstrap 三个窗口 p 值
    2. 综合结论：三层校验（t检验/非重叠/Bootstrap）一致性如何？
    3. 是否建议将 v4 信号可信度标注为「三层校验通过」升入 DECISION_LOG
    4. 建议更新的 CURRENT_STATE 字段（写草稿）
  </report_to_claude>

  <references>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md</file>
    <file>06_RESEARCH/RESULTS/20260606_v4_nonoverlap_validation.md</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
