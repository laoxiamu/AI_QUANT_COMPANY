# EVENT_LEDGER_V1 —— 前向事件账本字段表（冻结版）

**状态：** v1 冻结于 2026-07-21（Claude 设计，权威语义不下放；实现见 P0-RES-017）
**来源：** 外部审计 R2-B1。**要解决的问题：** 现状每天扫描/判断/拒绝大量候选，只对入选的极少数 thesis 提取二元结局，**被拒与近阈值候选的未来结果全部丢弃**——没有对照组，因此无法区分"判断力"与"运气"，也无法回答"人工/AI 选择器是否优于原始触发器"。
**边界：** 本账本是**测量基础设施**，不是策略、不是交易系统、不占重量化验证线 WIP、不产生交易建议、不碰 Holdout。

---

## 0. 四个被分开测量的对象（设计核心）

| 对象 | 问的问题 | 对应基线 |
|---|---|---|
| ① 候选生成器 | 触发条件本身有没有边沿 | 市场无条件基线 |
| ② 选择器（Claude/巡检的取舍） | 人选的比机器全量、比近阈值的更好吗 | raw 全候选 / near-miss 对照组 |
| ③ 概率预测 | 事前给的把握是否校准 | Brier / log score vs 条件基线 |
| ④ 可执行规则 | 冻结的入场退出规则扣成本后是否正期望 | 费后净 R，含滑点档 |

**默认基线不是 50%。** 每个 outcome 必须同时对照"同 scanner 条件全候选"与"差一条腿的 near-miss"。

## 1. 记录粒度与主键

- 一条记录 = 一个 `(symbol, source, decision_ts)` 判断事件。
- `event_id` = `sha256(symbol|source|decision_ts_utc|scanner_version)[:16]`
- **cluster_id**：同 symbol 48h 内重叠事件、或同一市场冲击（同日 BTC 4h 波动 >5% 时段）归同一簇。**统计一律按 cluster 做 block，不按行数当独立样本**（防 196 行当 196 个样本）。

## 2. 冻结字段（缺一不可，均在判断当刻写入，禁止事后回填）

**A. 溯源**
`event_id` / `decision_ts_utc`（绝对UTC）/ `data_asof_utc`（数据可见截止）/ `scanner_version` / `raw_response_sha256` / `source`（funding_oi_squeeze | binance_announcement | token_unlock | depeg）

**B. 状态量（机制）**
`funding_per_settlement`（每期实结）/ `interval_hours`（1/4/8，**必须实测，禁止假设**）/ `funding_per_day`（=每期×24/interval，**跨档唯一可比量**）/ `funding_est_next` / `funding_seq_n_periods_over_threshold`
`oi_usd_now` / `oi_1h_ago` / `oi_4h_ago` / `oi_24h_ago` / `d_oi_1h_pct` / `d_oi_4h_pct` / `d_oi_24h_ratio`
`price_now` / `chg_1h/4h/24h_pct` / `dist_from_peak_pct` / `quote_vol_24h_usd` / `spread_bp`（可得时）
`price_oi_quadrant`（价↑OI↑ / 价↑OI↓ / 价↓OI↓ / 价↓OI↑ —— 库存仍在积累 / 挤压兑现中 / 空头有序退出 / 新多头被困）

**C. 决策（事前，不可改）**
`decision`（selected | watch | near_miss | rejected）/ `decision_reason`（≤1句）/ `gate0_capacity_pass` / `gate1_payer_pass` / `legs_passed`（n/3）
`p_up`（0-1，事前概率，**必填**——没有概率就无法测校准）/ `expected_direction` / `expected_horizon_h`
`entry_rule` / `exit_rule` / `invalidation_rule`（唯一、可机械执行、含绝对价位或条件）

**D. 结局（由结算器按时间自动补，禁止人工填）**
`ret_1h/2h/4h/8h/24h/48h_pct`（自 decision_ts 后首个可成交价起算）/ `mae_pct` / `mfe_pct`（最大不利/有利偏移）
`oi_path_json` / `funding_path_json`（结局窗内路径，用于事后机制诊断）
`net_r_at_cost`（按冻结 entry/exit 规则+成本档 0.15%/0.3%/0.5%/1.0% 分别计）
`invalidation_hit_ts`（若触发）/ `resolver_version` / `resolved_at_utc`

## 3. 硬纪律（违反=该批次数据作废）

1. **决策必须早于第一个 outcome 时间戳**，机器校验，不合格标 `INVALID_LOOKAHEAD`。
2. **near_miss 组必须自动生成**：差且仅差一条腿的候选全部入账（这是对照组，不是可选项）。
3. **结算器只按时间补数**，不看理由、不读决策文本；评分者只看冻结字段与结局，**不看事后故事**。
4. **版本变更后从下一个事件起记分**，禁止回涂旧样本；旧版本记录保留原样。
5. **不为提高样本量放宽 decision 标准**——凑数会同时污染分子分母。
6. 本账本产生的任何"规律"若要成为策略，须另立预登记（含延迟入场设计），**不得用同一批数据既发现又验证**。

## 4. 输出与验收（14 天后）

- 存储：SQLite（`06_RESEARCH/DATA/EVENT_LEDGER/ledger.db`）+ 每日 parquet 快照。数据量小，禁止为此建服务。
- **14 天验收门**：①快照持久化率 ≥95%；②eligible 候选 outcome 补齐率 ≥90%；③四组（raw / near_miss / watch / selected）必须同时报告，禁止只报 selected；④按 48h cluster 做 block bootstrap；⑤**若 selected 的 ΔBrier ≤0 且费后 ΔR ≤0 → "AI/人工选择器有增值"被证伪**，据此调整投研线定位。
- 结算报告口径：样本不足只报区间，禁止用定性亮点覆盖定量失败（与 DEC-096 一致）。
