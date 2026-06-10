# TASK-P1-03 持仓量/清算 数据可得性核查（预登记前置）

**创建：** 2026-06-06 · Claude（CTO）· 执行人：Codex
**依据：** DEC-054（下一信号=OI/清算微结构）；DEC-018（样本门槛）
**性质：** 数据可得性核查，**非回测、非信号研究、不碰任何收益/预测分析**。目的只回答"数据拿不拿得到、覆盖多长、够不够"。

## 1. 目标

确认能否拿到、以及拿到多长历史的以下数据（BTC/ETH/SOL，U本位永续）：
1. **持仓量 OI**（sum_open_interest / sum_open_interest_value）
2. **多空比 LSR**（top trader long/short、global long/short）
3. **主动买卖量比**（taker buy/sell volume ratio）
4. **清算 liquidation 历史**（确认公开渠道是否可得）

数据源优先：`data.binance.vision`（项目既有管线，与现有OHLCV/funding同源）
- metrics 路径参考：`data/futures/um/daily/metrics/{SYMBOL}/`
- 若 binance.vision 无清算归档，明确记录"不可得"，不要用非授权第三方爬取。

## 2. 必须输出（核查报告）

对每个品种、每类数据：
- **是否可得**（可下载/不可得）
- **确切起止日期**（首条~末条）与**总行数/频率**（日频/5m等）
- **字段清单**（列名）
- 样本充足性对照 DEC-018：以"事件/有效观测"口径估算量级（仅计数，**不做收益统计**）
- **清算数据**：明确结论可得/不可得；不可得则说明（端点限制等）

汇总判断：OI/LSR 历史是否覆盖完整牛熊（2021牛、2022熊）？还是仅~2023起短样本？

## 3. 禁止事项

- ❌ 任何收益率/预测力/信号有效性分析（那是实验本身，须先预登记）。
- ❌ 读取或接触任何已封存 Holdout。
- ❌ 用非官方/非授权来源爬取清算数据。
- ❌ 覆盖 Memory Core；结论写执行报告由 Claude 审阅。

## 4. 产物

- 下载的数据存 `06_RESEARCH/DATA/FUTURES/`（按品种/类型命名）
- 核查报告 `04_AI_TEAM/CODEX_TASKS/REPORT_P1_03_DATA_RECON_OI.md`，含§2全部结论

## 5. 后续（Claude 据核查决定，不在本任务内做）

- 若 OI/LSR 覆盖完整周期且样本够 → 设计 OI 微结构信号并预登记（消耗独立Alpha槽）。
- 若仅短样本(~2023起) → 评估是否仅作探索级、或改回其他方向（须Founder知情）。
- 若清算不可得 → 信号仅基于 OI/LSR/taker-volume 设计。

【需要Codex】
