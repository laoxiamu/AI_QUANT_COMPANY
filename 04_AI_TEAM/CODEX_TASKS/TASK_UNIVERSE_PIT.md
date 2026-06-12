# TASK_UNIVERSE_PIT —— 无幸存者偏差 universe 数据资产（DEC-069③前置，双审计收敛项2）

**发包：** Claude 2026-06-12 ｜ **用途：** TSMOM 扩样本与 A-4 普查共用（一鱼两吃）。**只建数据资产，不跑任何策略/统计。**

## 交付物
1. `06_RESEARCH/DATA/UNIVERSE_PIT.csv`：Binance USDT-M 永续**全量历史合约**（含已退市/已下架），列=symbol, onboard_date, delist_date(空=仍在市), 数据来源标注。来源用官方（exchangeInfo API + data.binance.vision 归档目录枚举交叉验证）；网络经 `export HTTPS_PROXY=http://127.0.0.1:7897`。
2. `06_RESEARCH/CODE/build_universe_pit.py`（可复跑）+ 简短 pytest（point-in-time 查询函数：给定日期返回当日可交易集合，验证不含未来上市/已退市合约——无前视）。
3. 报告 `04_AI_TEAM/CODEX_TASKS/REPORT_UNIVERSE_PIT.md`：总数/退市数/各年度上市数表、与现有 9 品种覆盖对照、数据缺口与来源可信度说明、复算命令。

## 验收
退市合约必须出现在清单中（抽查 ≥3 个已知退市永续）；PIT 查询测试过；UTC；不改既有文件；不碰 HOLDOUT；不 git commit。
