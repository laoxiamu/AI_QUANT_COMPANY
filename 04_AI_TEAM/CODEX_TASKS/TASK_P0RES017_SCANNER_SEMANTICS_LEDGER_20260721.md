# TASK P0-RES-017：扫描器周期语义修复 + EVENT_LEDGER_V1 落地

**派发：** 2026-07-21 | **执行：** Codex | **验收：** Claude
**来源：** 外部审计 R2-A-02（活体数据缺陷）+ R2-B1（前向事件账本）
**字段表权威：** `06_RESEARCH/INVESTMENT_RESEARCH/EVENT_LEDGER_V1_SCHEMA.md`（已冻结，实现须逐字段对齐；如认为字段设计有问题，提异议不擅改）

## 交付 A：修复 funding 周期语义（最高优先，先做先验证）

**缺陷事实：** `06_RESEARCH/CODE/thesis_hf_scan.py:138-168` 直接读 `lastFundingRate` 命名 `funding_8h`，用统一 `abs≥0.3%` 阈值排序，**未读取或推断结算周期**；1h 档与 8h 档每日资金压力差 8 倍，导致排名/阈值/"付钱方烈度"跨档不可比；且只给排序前 8 名补 OI，等于让错误排序决定谁有资格进入复合签名。

要求：
1. 字段拆为 `funding_per_settlement` / `interval_hours`（**实测推断**：由 `fundingRate` 历史相邻 `fundingTime` 差值得出，禁止假设 8h）/ `funding_per_day`（=每期 × 24/interval）。保留旧字段名做兼容别名，但排序与阈值一律改用 `funding_per_day`。
2. **阈值改为按日归一**：原"每期 ≤-0.3%"在 8h 档等价 `funding_per_day ≤ -0.9%`，以此为准跨档统一（1h 档同样每期 -0.3% 将等价 -7.2%/日，自然排到前面——这正是修复目的）。
3. **给全部通过初筛的候选补 OI**，取消"只补前 8 名"。
4. 增加周期语义测试：同为每期 -0.3% 时，1h 合约的 `funding_per_day` 必须是 8h 合约的 8 倍。
5. 回归保证：其余三源逻辑与 legacy 输出不变（同 P0-RES-016 的对照方法，报告贴对照结果）。

## 交付 B：EVENT_LEDGER_V1 落地

1. 按 schema 建 SQLite（`06_RESEARCH/DATA/EVENT_LEDGER/ledger.db`）+ 每日 parquet 快照；表结构逐字段对齐 schema §2（A/B/C/D 四组）。
2. **写入器**：扫描时对**全部**候选（含 rejected / near_miss）冻结 A+B 组字段；C 组（decision/p_up/规则）由巡检班或 Claude 写入，写入器只提供接口与校验。
3. **near_miss 自动判定**：差且仅差一条腿（funding 腿 / OI 腿 / 价格腿其一未过、其余过）自动标 `near_miss` 入账——这是对照组，不可缺。
4. **结算器**（独立脚本，只按时间补数）：按 `decision_ts` 后 1/2/4/8/24/48h 补 `ret_*`、`mae`、`mfe`、`oi_path`、`funding_path`、四档成本下的 `net_r_at_cost`；**机器校验 decision_ts < 首个 outcome ts，不合格标 `INVALID_LOOKAHEAD`**。
5. `cluster_id`：同 symbol 48h 内重叠事件归同簇（市场共振规则可先留 TODO，不阻塞）。
6. **回填历史**：用已有四个扫描快照 `06_RESEARCH/CODE/output/thesis_hf_scan_*.json` 回填 A+B 组与可得结局，**但必须标 `backfilled=true`**，且不参与"决策早于结局"的技能评分（历史快照无冻结决策）。

## 护栏

- 不碰 Holdout；不做量化实验；不产生交易建议；不自动登记 thesis；不改预登记判据/模板/8-06 冲刺判据。
- 只用标准库 + 已有依赖（pandas / sqlite3 / pyarrow 可用）；不引黑箱依赖；不建服务。
- 取数走 SG 通道（Mac 直连 Binance = HTTP 451）。
- 不 git commit（AGENTS.md）；不删 git lock。
- 发现 schema 设计问题：在报告中提专业异议，不擅自改字段语义。

## 交付物

`REPORT_P0RES017_SCANNER_LEDGER_20260721.md`（含缺陷修复前后对照、周期实测样例、ledger 首批写入统计、回填统计、测试结果）+ `04_AI_TEAM/TASK_INBOX/P0RES017_DONE.json`
