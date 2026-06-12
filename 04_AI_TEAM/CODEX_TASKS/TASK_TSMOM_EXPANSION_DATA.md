# TASK_TSMOM_EXPANSION_DATA —— TSMOM 扩样本数据准备（不耗独立计数；只备数据不跑策略）

**发包：** Claude 2026-06-11 ｜ **依据：** DEC-066④（TSMOM=R2后扩样本候选，P1-06优先）+ DEC-068③（不耗命并行推进）

## 目标
为 TSMOM 家族扩样本（更多品种+2026H1纯样本外）准备数据。**本任务只下载与质检数据，不跑任何回测/策略/统计检验**（那需另案预登记）。

## 交付物
1. 扩展品种永续数据（沿用 `06_RESEARCH/CODE/download_futures_data.py` 的 data.binance.vision 官方归档源与既有文件格式/命名）：
   - 品种：BNBUSDT、XRPUSDT、DOGEUSDT、ADAUSDT、LTCUSDT（按上市日起至 2026-06-05）
   - 内容：MARK_4H K线 + FUNDING_8H（与既有 BTC/ETH/SOL 文件同 schema、同 UTC、存 `06_RESEARCH/DATA/FUTURES/`）
   - 网络若需代理：export HTTPS_PROXY=http://127.0.0.1:7897
2. 既有 BTC/ETH/SOL 的 MARK_4H/MARK_1H/FUNDING_8H 增量补到 2026-06-05（**追加为带 `_2026H1` 后缀的独立文件，严禁合并改写原文件**——原文件是已封存实验的数据快照）。
3. 质检报告 `04_AI_TEAM/CODEX_TASKS/REPORT_TSMOM_EXPANSION_DATA.md`：每文件行数/起止/缺口（>1个周期的gap列表）/与既有文件 schema 一致性核对；新文件 sha256 追加写入 `06_RESEARCH/DATA/DATA_HASHES_20260611.txt`（新建，不改旧哈希文件）。

## 验收标准
schema 与既有文件逐列一致；UTC；缺口率<1% 或逐段说明；原 9 个数据文件的 sha256 与 `06_RESEARCH/DATA/DATA_HASHES_20260610.txt` 完全一致（证明未被触碰）。

## 禁止
跑回测/统计；改既有数据文件；碰 HOLDOUT；git commit（Claude 验收后统一提交）。
