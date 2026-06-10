# Codex 任务：研究结果汇总看板

```xml
<task>
  <id>INF-02</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>基础设施，不计入研究失败计数</type>

  <context>
    目前 06_RESEARCH/CODE/output/ 目录里有大量 JSON 结果文件（每次回测输出一个）。
    每次需要比较不同版本的结果，都需要手动翻阅多个文件。
    
    本任务：写一个脚本，自动读取所有 metrics.json 文件，
    汇总成一个可读的 HTML 看板和 CSV 对比表，方便 Founder 和 Claude 随时查看全局进度。
    
    不需要任何量化知识，纯粹是数据整合和可视化工作。
  </context>

  <required_work>
    一、扫描所有结果文件
      扫描 06_RESEARCH/CODE/output/ 目录下所有 *_metrics.json 文件。
      每个 JSON 文件代表一次实验的核心指标。
    
    二、生成 CSV 汇总表
      从每个 JSON 提取：
        - 实验版本名
        - 运行日期
        - 品种范围
        - 交易数量
        - 净收益率
        - Sharpe
        - MaxDD
        - Expectancy
        - 是否通过门槛（Sharpe>1 AND MaxDD<25%）
        - 结论（PASSED/FAILED/DIAGNOSTIC）
      
      输出：00_PROJECT_MANAGEMENT/ALL_EXPERIMENTS_SUMMARY.csv
    
    三、生成 HTML 看板
      用纯 HTML + inline CSS（不依赖外部库）生成一个可直接在浏览器打开的文件：
      
      包含：
        - 顶部：核心状态卡片（当前失败计数6/8，Holdout状态：封存，最优Sharpe：1.31）
        - 实验结果表格（按日期排序，通过的行标绿色，失败标红，诊断标灰）
        - 各实验 Sharpe 和 MaxDD 的横向条形图（SVG实现，不用外部图表库）
      
      输出：00_PROJECT_MANAGEMENT/EXPERIMENTS_DASHBOARD.html
    
    四、添加到每日自动化（可选）
      在脚本末尾加一行注释，说明如何从命令行运行以更新看板：
      "python3 06_RESEARCH/CODE/generate_dashboard.py"
  </required_work>

  <outputs>
    <file>06_RESEARCH/CODE/generate_dashboard.py</file>
    <file>00_PROJECT_MANAGEMENT/ALL_EXPERIMENTS_SUMMARY.csv</file>
    <file>00_PROJECT_MANAGEMENT/EXPERIMENTS_DASHBOARD.html</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_INF02_DASHBOARD.md</file>
  </outputs>

  <acceptance>
    <item>HTML看板能在浏览器直接打开，无需网络（不依赖CDN）</item>
    <item>CSV包含所有已完成实验的核心指标</item>
    <item>通过/失败用颜色区分，可读性高</item>
    <item>脚本可重复运行（每次添加新实验后更新看板）</item>
  </acceptance>

  <forbidden>
    <item>禁止修改任何研究文件或Memory Core文件</item>
    <item>禁止使用需要 pip install 的外部可视化库（用SVG替代）</item>
  </forbidden>

  <report_to_claude>
    1. 发现了多少个 metrics.json 文件
    2. CSV 和 HTML 文件路径
    3. HTML看板是否能正常在浏览器打开
  </report_to_claude>
</task>
```
