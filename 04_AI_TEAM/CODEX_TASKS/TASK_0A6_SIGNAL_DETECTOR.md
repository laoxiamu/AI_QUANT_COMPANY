# Codex 任务：信号检测器实现

```xml
<task>
  <id>0A-6</id>
  <version>1.0</version>
  <created>2026-06-05</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>

  <target>
    实现 BTC/USDT 4H 历史数据上的三重确认信号检测器，输出信号列表和统计摘要。
    这是 Codex 在本项目的首次真实任务，同时验证 Claude→Codex 协作流程。
  </target>

  <inputs>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/BTC_USDT_4H.csv</path>
      <desc>BTC/USDT 4H K线数据，15895行，2019-01-01 ~ 2026-06-04，列：datetime/open/high/low/close/volume</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/CODEX_TASKS/SPEC_0A6_SIGNAL_DEFINITIONS.md</path>
      <desc>信号语义定义规格，必须完全遵守，不得自行修改信号定义</desc>
    </file>
  </inputs>

  <outputs>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/signal_detector.py</path>
      <desc>信号检测器主程序</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/06_RESEARCH/CODE/output/triple_signals_BTCUSDT_4H.csv</path>
      <desc>三重确认信号列表（按规格格式输出）</desc>
    </file>
    <file>
      <path>/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/CODEX_TASKS/REPORT_0A6_SIGNAL_DETECTOR.md</path>
      <desc>执行报告（必须写，Claude 通过此文件验收）</desc>
    </file>
  </outputs>

  <constraints>
    <item>Python 3.13.5，只使用 pandas 和 numpy（已安装），不引入新依赖</item>
    <item>向量化实现优先（pandas/numpy），避免逐行 Python 循环（性能要求）</item>
    <item>信号语义必须 100% 按 SPEC_0A6_SIGNAL_DEFINITIONS.md 实现，不得扩展或简化</item>
    <item>所有参数（sweep_lookback=20, swing_lookback=10, swing_n=2, sequence_window=20）硬编码为常量，放在文件顶部，方便后续调参</item>
    <item>代码必须有注释，说明每个信号的判定逻辑对应规格的哪一节</item>
    <item>脚本从项目根目录运行：python3 06_RESEARCH/CODE/signal_detector.py</item>
  </constraints>

  <acceptance>
    <item>脚本在 BTC_USDT_4H.csv 上无报错运行完毕</item>
    <item>控制台打印统计摘要，格式与规格§5中的「格式2」一致</item>
    <item>输出 CSV 文件包含规格§5「格式1」中的所有列</item>
    <item>信号触发次数在合理范围（根据4H BTC历史数据预估：50-600次，若超出此范围必须在报告中说明）</item>
    <item>执行报告 REPORT_0A6_SIGNAL_DETECTOR.md 已写入项目目录（格式见下方）</item>
  </acceptance>

  <forbidden>
    <item>禁止修改 BTC_USDT_4H.csv 原始数据文件</item>
    <item>禁止修改 SPEC_0A6_SIGNAL_DEFINITIONS.md 中的信号定义</item>
    <item>禁止修改 01_MEMORY_CORE/ 下的任何文件</item>
    <item>禁止修改 00_PROJECT_MANAGEMENT/ 下的任何文件</item>
    <item>禁止自行扩展信号定义（如添加额外过滤条件）——如认为规格有误，在报告中说明，等待 Claude 裁决</item>
    <item>禁止引入 pandas/numpy 以外的第三方库</item>
  </forbidden>

  <report_format>
    执行完毕后，在 REPORT_0A6_SIGNAL_DETECTOR.md 中按以下格式写报告：

    ## 执行报告 TASK-0A6
    **执行时间：** [日期]
    **执行人：** Codex
    **状态：** COMPLETED / FAILED

    ### 执行结果
    - 脚本路径：06_RESEARCH/CODE/signal_detector.py
    - 运行结果：成功 / 失败（附错误信息）
    - 信号统计：[粘贴控制台输出的统计摘要]

    ### 规格执行确认
    - 信号1 Liquidity Sweep：按规格§1实现 ✅/❌
    - 信号2 CHoCH：按规格§2实现 ✅/❌
    - 信号3 FVG：按规格§3实现 ✅/❌
    - 三重确认序列：按规格§4实现 ✅/❌
    - 输出格式：按规格§5实现 ✅/❌

    ### 发现的规格问题（如有）
    [如果规格有歧义或矛盾，在此列出，等待 Claude 裁决]

    ### 技术说明
    [实现思路的简要说明，特别是向量化方法]
  </report_format>

  <references>
    <file>01_MEMORY_CORE/DECISION_LOG.md（项目决策背景）</file>
    <file>00_PROJECT_MANAGEMENT/AI_QUANT_COMPANY_ARCHITECTURE_v2.md §17（策略方向背景）</file>
    <file>06_RESEARCH/RESEARCH_PROTOCOL_v1.md（研究协议，了解项目研究规范）</file>
  </references>
</task>
```
