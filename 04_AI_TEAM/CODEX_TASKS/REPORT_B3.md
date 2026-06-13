# REPORT_B3 — A-4 新上市数据普查

Generated: 2026-06-12 17:16:00 UTC

## 任务范围

- 批次任务：`04_AI_TEAM/CODEX_TASKS/BATCH_20260612N.md` 的 B3，仅执行 B3。
- 数据输入：`06_RESEARCH/DATA/UNIVERSE_PIT.csv`
- 输出结果：`06_RESEARCH/RESULTS/20260612_a4_listing_census.md`
- 约束：只做上市计数与 data.binance.vision 归档可得性 HEAD 探测；未下载 zip；未读取行情 CSV；未计算收益、波动、信号或回测。

## 产物

- CODE: `06_RESEARCH/CODE/a4_listing_census.py`
- OUTPUT: `06_RESEARCH/CODE/output/a4_listing_census_by_year.csv`
- OUTPUT: `06_RESEARCH/CODE/output/a4_listing_archive_head_probes.csv`
- OUTPUT: `06_RESEARCH/CODE/output/a4_listing_archive_summary.csv`
- OUTPUT: `06_RESEARCH/CODE/output/a4_listing_census_summary.json`
- RESULTS: `06_RESEARCH/RESULTS/20260612_a4_listing_census.md`
- REPORT: `04_AI_TEAM/CODEX_TASKS/REPORT_B3.md`

## 执行命令

```bash
python3 -m py_compile 06_RESEARCH/CODE/a4_listing_census.py
HTTPS_PROXY=http://127.0.0.1:7897 python3 06_RESEARCH/CODE/a4_listing_census.py --workers 24
```

## 核心结果

| metric | value |
|---|---:|
| UNIVERSE rows | 646 |
| 2022 起新上市 | 530 |
| 成熟 30 天窗口 | 524 |
| 未成熟 30 天窗口 | 6 |
| HEAD probes | 16,750 |
| HEAD 200 | 16,684 |
| HEAD 404 | 66 |
| K 线完整窗口 | 474 |
| funding 完整窗口 | 521 |
| K 线 + funding 均可得 | 472 |
| 30 天数据可得率 | 90.08% |

分年上市数：

| year | count |
|---:|---:|
| 2019 | 3 |
| 2020 | 67 |
| 2021 | 46 |
| 2022 | 19 |
| 2023 | 96 |
| 2024 | 129 |
| 2025 | 246 |
| 2026 | 40 |

## 口径说明

- K 线归档：`daily/klines/<symbol>/1h/<symbol>-1h-YYYY-MM-DD.zip`，对成熟窗口内最多 30 个 UTC 自然日逐日 HEAD。
- Funding 归档：data.binance.vision 官方可得形态为 monthly `fundingRate` ZIP；对覆盖上市后 30 天窗口的月份 HEAD。
- 若合约上市 30 天内退市，期望窗口截到 `delist_date` 前一日。
- 当前 UTC 日尚未走完或窗口未结束者标记为未成熟，不纳入可得率分母。

## 验收自检

| requirement | status | evidence |
|---|---|---|
| 只做 B3 | PASS | 未执行 B4/B5；未修改 B1/B2 既有改动 |
| 读取批次铁律、AGENTS、引用数据 | PASS | 已读取 `AGENTS.md`、批次头部、`UNIVERSE_PIT.csv` |
| 分年新上市永续数量 | PASS | `a4_listing_census_by_year.csv` 与 RESULTS 表 |
| 2022 起新上市归档可得性 | PASS | 530 个合约，16,750 条 HEAD 明细 |
| 网络经 HTTPS_PROXY | PASS | `HTTPS_PROXY=http://127.0.0.1:7897` |
| HEAD 探测、不下载 | PASS | 脚本仅使用 `Request(..., method="HEAD")` |
| 禁收益/波动分析 | PASS | 脚本不解析价格/funding 内容，不计算收益、波动、信号、回测 |
| 输出 RESULTS | PASS | `06_RESEARCH/RESULTS/20260612_a4_listing_census.md` |
| 输出 CODEX_TASKS 报告 | PASS | 本文件 |
| 禁 git commit | PASS | 批次头部要求全程禁 commit；未执行 commit |

## 备注

- 原始 HEAD 状态只有 `200` 与 `404`，无 timeout/URLError；可得率未受网络失败污染。
- Funding 用 monthly 归档 HEAD 判断覆盖月份可得性；因任务禁止下载，未验证 monthly ZIP 内部逐条 funding 行。
