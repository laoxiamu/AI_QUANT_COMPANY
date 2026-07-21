# REPORT P0-RES-017：扫描器周期语义修复 + EVENT_LEDGER_V1 落地

任务：`P0-RES-017`  
执行时间锚：2026-07-21，最终回读截至 `2026-07-21T07:57:45Z`  
状态：completed

## 结论

已修复 funding 周期语义缺陷：扫描器不再把 `lastFundingRate` 固定命名/解释为 8h 费率；新增 `funding_per_settlement`、`interval_hours`、`funding_per_day`，排序与 funding 阈值统一改用 `funding_per_day`，日阈值为 `0.009`（原 8h 每期 0.3% 的日化等价）。旧字段 `funding_8h` 保留为兼容别名；`legacy_funding_oi` 子输出保持旧字段形态。

已落地 EVENT_LEDGER_V1：

- SQLite：`06_RESEARCH/DATA/EVENT_LEDGER/ledger.db`
- Parquet 快照：`06_RESEARCH/DATA/EVENT_LEDGER/snapshots/event_ledger_20260712.parquet`、`20260715`、`20260716`、`20260717`、`20260721`
- 写入器：`06_RESEARCH/CODE/event_ledger_v1.py`
- 历史回填：`06_RESEARCH/CODE/backfill_event_ledger_v1.py`
- 独立结算器：`06_RESEARCH/CODE/resolve_event_ledger_v1.py`

## 代码改动

- `06_RESEARCH/CODE/thesis_hf_scan.py`
  - funding 初筛先用 `fundingRate` 历史相邻 `fundingTime` 推断周期，再计算 `funding_per_day`。
  - funding 排序从 `abs(funding_8h)` 改为 `abs(funding_per_day)`。
  - OI 从“只补前 8 名”改为“全部通过初筛候选补 OI”。
  - 主输出 `schema_version` 升为 `P0-RES-017`。
  - 默认扫描后写 EVENT_LEDGER_V1；可用 `--no-event-ledger` 做调试跳过。

- `06_RESEARCH/CODE/event_ledger_v1.py`
  - 建表字段覆盖 schema A/B/C/D 四组，并增加 operational 字段：`symbol`、`event_type`、`cluster_id`、`backfilled`、`outcome_status`、`scan_file`、`raw_candidate_json`、创建/更新时间。
  - `near_miss` 自动判定：funding / OI / price 三腿差且仅差一条腿。
  - C 组更新接口 `update_decision_fields()`：校验 `decision`、`p_up`、方向/规则字段。
  - 结局字段计算：`ret_1h/2h/4h/8h/24h/48h_pct`、`mae_pct`、`mfe_pct`、路径 JSON、lookahead 校验。

- `06_RESEARCH/CODE/backfill_event_ledger_v1.py`
  - 回填 4 个历史 `thesis_hf_scan_*.json`。
  - `--fetch-via-ssh-sg` 可用 SG 通道补旧 funding 行的实测周期字段。

- `06_RESEARCH/CODE/resolve_event_ledger_v1.py`
  - 独立结算器，只按 post-decision 时间取 markPrice/OI/funding 路径并写 D 组。

## 周期语义验证

单测覆盖同为每期 `-0.3%` 时：

```text
1h: funding_per_day = -0.072
8h: funding_per_day = -0.009
ratio(abs 1h / abs 8h) = 8
```

SG 历史回填实测样例：

```text
TUSDT    2026-07-12T06:58:00Z  settlement=-0.536688%  interval=1h  per_day=-12.880512%
GWEIUSDT 2026-07-12T06:58:00Z  settlement=-0.454247%  interval=1h  per_day=-10.901928%
HOTUSDT  2026-07-12T06:58:00Z  settlement=-0.551227%  interval=8h  per_day=-1.653681%
CATUSDT  2026-07-17T08:05:00Z  settlement=-0.493000%  interval=8h  per_day=-1.479000%
```

## 回归对照

按 P0-RES-016 的固定假数据对照方法，从 `git show HEAD:06_RESEARCH/CODE/thesis_hf_scan.py` 加载旧脚本，与新脚本同输入比较：

```text
legacy_funding_exact_equal True
announcements_equal True
depeg_equal True
token_unlock_equal True
```

其中 `legacy_funding_oi` 的旧字段输出逐字相等；新字段只出现在主 candidates / ledger，不污染 legacy 子输出。

## Ledger 回填统计

回填命令：

```bash
python3 06_RESEARCH/CODE/backfill_event_ledger_v1.py --fetch-via-ssh-sg
```

结果：

```text
input_files = 4
candidate_rows = 196
unique_schema_events = 192
backfilled = 192
near_miss = 10
rejected = 182
```

`196 -> 192` 的差异来自 schema 主键粒度：`event_id = sha256(symbol|source|decision_ts_utc|scanner_version)[:16]`。历史公告里同一 symbol/source/scan 有重复公告候选（KORUUSDT、UTK 各 2 次，跨 2 个扫描日共 4 次冲突）。实现未改 event_id 语义；冲突候选合并进同一行的 `raw_candidate_json` list，保留原始证据。

Source / decision 分布：

```text
binance_announcement  rejected   151
depeg                 rejected     2
funding_oi_squeeze    near_miss   10
funding_oi_squeeze    rejected    21
token_unlock          rejected     8
```

Funding 周期补齐：

```text
funding rows = 31
interval filled = 30
interval missing = 1  # ZHIPUUSDT: 历史 funding 点不足，未假设 8h
1h = 2, 4h = 19, 8h = 9
```

## 结算器结果

结算器只处理 futures funding rows；非 funding 来源没有可机械匹配的 futures symbol/path，本批保持 outcome 空值。

```text
funding rows = 31
resolved = 29
RESOLVE_ERROR = 2  # BUSDT, BOTUSDT；SG SSH 子请求失败
INVALID_LOOKAHEAD = 0
```

`net_r_at_cost`：本批历史回填没有冻结 C 组 `expected_direction/entry_rule/exit_rule/invalidation_rule`，因此结算器不凭空发明规则，四档成本 JSON 保持 null。未来由 Claude/巡检班写入 C 组后，结算器会按冻结方向/期限补成本后数值。

## 验证

```text
python3 -m pytest 06_RESEARCH/CODE/tests/test_thesis_hf_scan.py 06_RESEARCH/CODE/tests/test_event_ledger_v1.py -q
18 passed in 0.44s
```

```text
python3 -m pytest 06_RESEARCH/CODE/tests -q
93 passed in 5.83s
```

```text
python3 -m py_compile 06_RESEARCH/CODE/thesis_hf_scan.py 06_RESEARCH/CODE/event_ledger_v1.py 06_RESEARCH/CODE/backfill_event_ledger_v1.py 06_RESEARCH/CODE/resolve_event_ledger_v1.py
exit 0
```

Parquet 回读：

```text
event_ledger_20260712.parquet 192 rows
event_ledger_20260715.parquet 192 rows
event_ledger_20260716.parquet 192 rows
event_ledger_20260717.parquet 192 rows
event_ledger_20260721.parquet 192 rows
```

## 护栏自检

- 未读取 Holdout 文件内容，未做量化实验，未产生交易建议，未自动登记 thesis。
- 未修改预登记判据、模板或 8-06 冲刺判据。
- 未新增黑箱依赖；使用标准库、`pandas`、`sqlite3`，parquet 由环境已有 `fastparquet` 引擎写出。
- Binance 取数走 SG 通道。
- 未 git commit / push。
- 说明：早期范围扫描命令枚举过 `06_RESEARCH` 文件名，输出中出现 HOLDOUT 路径名；没有打开或读取 Holdout 内容，未参与任何计算。
