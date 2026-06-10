# Codex 任务：下载1H数据并扩展历史覆盖

```xml
<task>
  <id>INF-01</id>
  <version>1.0</version>
  <created>2026-06-06</created>
  <created_by>Claude（CTO）</created_by>
  <status>READY_FOR_EXECUTION</status>
  <type>基础设施，不计入研究失败计数</type>

  <context>
    当前项目的数据基础：
    - 只有 4H K线数据（BTC/ETH/SOL）
    - 历史覆盖范围需要确认（特别是SOL的起始时间）
    
    为什么需要1H数据：
    1. 延迟入场诊断（等1H确认K线）需要更细粒度数据
    2. 做空信号研究可能需要1H信号
    3. 1H数据也可用于构建更精确的入场过滤（如入场后1H内的走势）
    4. 未来阶段2研究会用到1H数据做实盘监控
    
    本任务：下载 BTC/ETH/SOL 的1H历史数据，并验证4H数据的完整性。
  </context>

  <required_work>
    一、下载1H OHLCV数据
      品种：BTCUSDT、ETHUSDT、SOLUSDT
      周期：1H（1小时）
      起始时间：
        - BTC/ETH：尽量回溯到2019-01-01
        - SOL：从上线时间起（2020-04-10）
      结束时间：当前
      数据源：Binance（使用 ccxt 库）
      
      注意：数据量较大，BTC 1H从2019年至今约50,000根K线，
      需要分批下载（Binance单次最多1000条），做好进度记录。
    
    二、验证现有4H数据完整性
      检查 06_RESEARCH/DATA/ 目录下现有数据文件：
      - 数据时间范围（start/end）
      - 是否有缺口（连续两条记录时间差 > 4.5小时）
      - 总行数
      生成数据质量报告
    
    三、数据存储规范
      存储路径：
        06_RESEARCH/DATA/BTCUSDT_1H.csv
        06_RESEARCH/DATA/ETHUSDT_1H.csv
        06_RESEARCH/DATA/SOLUSDT_1H.csv
      
      格式与4H数据保持一致：
        timestamp（Unix毫秒）, open, high, low, close, volume
      
      同时生成 DATA_MANIFEST.json，记录每个文件的：
        - 时间范围
        - 总行数
        - 数据源
        - 下载时间
  </required_work>

  <outputs>
    <file>06_RESEARCH/DATA/BTCUSDT_1H.csv</file>
    <file>06_RESEARCH/DATA/ETHUSDT_1H.csv</file>
    <file>06_RESEARCH/DATA/SOLUSDT_1H.csv</file>
    <file>06_RESEARCH/DATA/DATA_MANIFEST.json</file>
    <file>06_RESEARCH/CODE/download_1h_data.py</file>
    <file>04_AI_TEAM/CODEX_TASKS/REPORT_INF01_1H_DATA.md</file>
  </outputs>

  <acceptance>
    <item>三个品种1H数据均已下载</item>
    <item>BTC 1H数据行数 > 45,000（2019-01至今）</item>
    <item>DATA_MANIFEST.json 记录完整</item>
    <item>4H数据质量报告：确认无重大缺口</item>
    <item>执行报告含实际下载行数和时间范围</item>
  </acceptance>

  <forbidden>
    <item>禁止修改任何研究文件</item>
    <item>禁止直接写入Memory Core文件</item>
    <item>禁止使用付费数据源（只用 Binance 公开API）</item>
  </forbidden>

  <report_to_claude>
    1. 三个品种1H数据的时间范围和行数
    2. 4H数据质量检查结果（有无缺口）
    3. 下载是否完整，有无失败的片段
  </report_to_claude>
</task>
```
