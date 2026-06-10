# Codex 任务：波动率压缩分组分析

```xml
<task>
  <id>0B-15-diag</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>诊断分析，不计入失败计数</type>

  <context>
    来源1（内部，V4历史）：
      V4系统的22分制评分中，波动率压缩因子是唯一通过IC分析的因子：
        BTC IC +0.0579，SOL IC +0.0816
      V4的解释：在Sweep发生之前市场处于"压缩状态"（价格区间收窄，ATR相对历史偏低），
      随后的突破更有方向性，信号质量更高。
    
    来源2（外部调研 EXTERNAL_RESEARCH_v3 方向4）：
      使用ATR相对高度过滤器（14周期ATR > ATR的50周期均值）使利润因子提升40%。
      波动率压缩过滤的作用：判断是否处于"信号有效的环境"，与方向过滤不互斥。
    
    当前问题：
      我们的425个事件没有做任何质量筛选——全部进入统计。
      如果其中一部分发生在"高波动扩张期"（Sweep是真正的方向性突破），
      而另一部分发生在"低波动压缩期"（Sweep是噪声后的方向性反转），
      两组的信号质量可能差异显著。
    
    本任务研究问题：
      将v4的425个事件按"Sweep发生前的波动率状态"分成两组，
      分别计算止损率和t+24收益分布，验证波动率压缩是否能提升信号质量。
    
    参考：04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md
  </context>

  <volatility_compression_definition>
    定义（两种方案，同时计算，便于对比）：
    
    方案A（简单ATR比较，与外部研究一致）：
      使用 4H 收盘价计算 ATR(14)
      信号发生前一根K线：
        压缩组：ATR(14)[t_sweep-1] < ATR(50)[t_sweep-1]（当前ATR低于长期ATR均值）
        扩张组：ATR(14)[t_sweep-1] >= ATR(50)[t_sweep-1]
    
    方案B（布林带收窄，与V4波动压缩因子逻辑一致）：
      使用 4H 收盘价计算 BBW（布林带宽度）= (BB上轨 - BB下轨) / BB中轨
      参数：BB窗口=20，倍数=2
      信号发生前一根K线：
        压缩组：BBW[t_sweep-1] < BBW_median（布林带宽度低于历史中位数）
        扩张组：BBW[t_sweep-1] >= BBW_median
    
    两种方案都测试，报告各自的结果，不提前判断哪个更好。
    
    注意：波动率数据必须使用 t_sweep-1 的数据（前一根K线），避免前视偏差。
  </volatility_compression_definition>

  <required_analysis>
    以v4的425个事件为数据集（已有，无需重新运行信号检测器）：
    
    一、分组基本信息
      | 分组方案 | 压缩组N | 扩张组N |
      |----------|-------:|-------:|
      | 方案A（ATR）| ? | ? |
      | 方案B（BBW）| ? | ? |
    
    二、t+6/12/24收益对比
      压缩组 vs 扩张组的均值、中位数、标准差
      以及单侧t检验p值
      
      期望：压缩组均值 >> 扩张组均值（验证假设）
      如果压缩组比扩张组信号更强 → 波动率压缩是有效过滤器
    
    三、止损率对比（对0B9数据的分组重新分析）
      如果无止损数据（0B12 trades.csv）中有足够字段，
      统计压缩组 vs 扩张组的"交易在前6根K线的逆向运动幅度"
      作为止损率的代理指标
    
    四、时期分布
      压缩组 vs 扩张组在各年份的分布（%）
      2022年的12个事件属于哪一组？
    
    五、Bootstrap稳健性（快速版）
      对压缩组和扩张组分别做1000次Bootstrap
      验证两组均值差异是否显著
    
    六、关键结论
      如果压缩组信号明显更强（均值差>0.5%，p<0.05）：
        建议将波动率压缩作为第三层过滤条件
        预估过滤后样本量：压缩组N（仍需≥300）
      如果两组差异不显著：
        V4的IC发现可能对当前双层Regime框架下已不显著
        不建议增加此过滤层
  </required_analysis>

  <data_inputs>
    v4事件文件（信号时间和品种）：
      06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv
    
    0B12无止损交易记录（有完整持仓路径）：
      06_RESEARCH/CODE/output/no_stop_t24_three_symbols_trades.csv
    
    4H OHLCV价格数据（计算ATR和布林带）：
      与v4相同数据源
    
    参考代码：
      06_RESEARCH/CODE/sweep_dual_regime.py（数据加载参考）
      06_RESEARCH/CODE/v12_no_stop_diagnostic.py（0B12框架参考）
  </data_inputs>

  <outputs>
    <file>06_RESEARCH/CODE/v15_vol_compression.py</file>
    <file>06_RESEARCH/RESULTS/20260606_vol_compression_analysis.md</file>
    <file>06_RESEARCH/CODE/output/vol_compression_charts.png</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_0B15_VOL_COMPRESSION.md</file>
  </outputs>

  <acceptance>
    <item>方案A（ATR）和方案B（BBW）两种定义均计算</item>
    <item>t+6/12/24收益对比完整（含p值）</item>
    <item>压缩组 vs 扩张组N数报告</item>
    <item>时期分布完整（2022事件属于哪组）</item>
    <item>明确结论：是否建议加入波动率压缩过滤</item>
    <item>Holdout未读取</item>
    <item>执行报告含「Claude 待处理事项」</item>
  </acceptance>

  <forbidden>
    <item>禁止查看Holdout</item>
    <item>禁止修改v4信号或Regime参数</item>
    <item>禁止直接写入Memory Core文件</item>
  </forbidden>

  <report_to_claude>
    1. 两种方案下压缩组 vs 扩张组的t+24均值差异
    2. 差异是否统计显著（p值）
    3. 压缩组样本量（是否仍≥300探索级）
    4. 2022年12个事件主要在哪一组（解释2022一直失败的原因？）
    5. 综合结论：是否建议将波动率压缩作为第四层过滤条件
    6. 若建议加入：预估过滤后样本量，下一步建议
    7. 建议更新的CURRENT_STATE字段
  </report_to_claude>

  <references>
    <file>06_RESEARCH/CODE/output/events_v5_sweep_regime_bull_v4.csv</file>
    <file>06_RESEARCH/RESULTS/20260606_v5_sweep_regime_bull_v4_EVAL.md（v4基准）</file>
    <file>00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md（方向4外部研究）</file>
    <file>01_MEMORY_CORE/PROJECT_CONTEXT.md（PC-09：V4波动率压缩IC数据）</file>
    <file>04_AI_TEAM/CODEX_TASKS/COLLABORATION_RULES.md</file>
  </references>
</task>
```
