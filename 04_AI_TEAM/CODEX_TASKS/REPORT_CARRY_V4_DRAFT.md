# CARRY-V4-DRAFT 执行报告

**任务：** 起草 Delta 中性 Carry 预登记 v4，闭合 CARRY-RR3 剩余项与交易小时新堵点
**日期：** 2026-06-14
**状态：** completed（草案完成，待独立 Risk Reviewer 盲审）
**审查结论：** 本轮不作 APPROVED/NOT APPROVED 自审裁决

## 交付

- v4 草案：`06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md`
- 完成事件：`04_AI_TEAM/TASK_INBOX/CARRY_V4_DRAFT_DONE.json`

## 任务前自查

1. **验证机制：** 不改 funding carry 命题，只把 USDT 资本、逐 1H 保证金路径、交易小时损益和事件风险冻结为唯一可执行口径。
2. **量化验收：** 四组要求均可由固定资本、公式、bar 顺序、路径递推、完整 bracket 选档、固定 seed 和二元失败条件核对。
3. **更便宜等效实现：** 以 v3 为基线完成文档级闭合，不运行回测、bootstrap、收益计算或参数搜索。
4. **禁止项：** 未读取 Holdout/`01_MEMORY_CORE/`，未改历史预登记或 RR3 审查，未改 §0 核心重构，未简化成本模型。

## 四项闭合映射

1. **资本 / USD-USDT 计价账：** 全程统一为 USDT，冻结 `C0=100,000 USDT`、80/10/10 分配、初始预留现金、开仓成本来源和固定收益率分母。现货、wallet、funding、basis、强平及负债均在同一 USDT NAV 中只计一次。USDT/USD 不进入策略 PnL，只按机械规则进入事件风险硬门。
2. **1H 合成强平路径：** 冻结 PCG64 `seed=20260614`、2000 路径、105 个 168h 同步块、固定合成时钟与 BTC/ETH 价格基准、gap/body/OHLC 精确递推、365 日 warm-up 和后 365 日评价。完整历史 bracket 表随块移动，再按合成 USDT 名义重新选档。
3. **交易小时 PnL：** 定义 `A_t` 为 funding 后、open 交易前检查点；open 交易归属新小时，右边界 funding 归属结束小时。固定 UTC 8h interval 由八个小时 NAV 差求和。交易小时用 pre-open/post-open 数量拆分，并强制 NAV、wallet realized/unrealized 和机制归因逐小时对账。
4. **其余 RR3 歧义：** 唯一化边界 close 强平/funding/补款/交易顺序、buffer breach 与 liquidation 两级状态、负 wallet 重分类、强平滑点只扣一次、小时内强平归因、非整点 funding 失败条件、事件 membership 在合成路径中的来源及零基小时索引。

## 保留项

- Protocol v1.4 AI 证据三行保留。
- 日期冻结为 2026-06-14。
- §0 历史=FEASIBILITY-LOCK、不耗独立计数；前向 shadow=真确认；证据等级决定上线的核心重构未改。
- OI 只能双腿同步减至 50%，事件 0.3%/0.5%/1.0% 滑点压力档、Holdout 物理封存和前向一次性确认门保留。

## 边界

- 未运行历史复核、回测、bootstrap、事件研究、收益统计或参数搜索。
- 未读取 Holdout、sealed 内容或 `01_MEMORY_CORE/`。
- 未修改 v3 和 `CARRY_RISK_REVIEW_v3.md`。
- 工作区既有 `CARRY_V4_DRAFT_RUN.log`、`FIX_COLLECTOR_URL_RUN.log` 修改未回退、未改写、未纳入本任务。
- 本报告只确认草案交付，不代表风险审查通过。

## 静态验收

- [x] `C0=100,000 USDT`，现货/永续/现金/funding/basis/强平统一 USDT。
- [x] USDT 脱锚明确为事件风险，不重复进入 USDT PnL。
- [x] 2000 条路径、PCG64 seed、固定基准、逐 bar 递推和完整 bracket 选档均显式冻结。
- [x] funding、open 交易、强平及 8h interval 归属唯一。
- [x] buffer breach 与 liquidation 分级、次小时补款和禁止外部补资明确。
- [x] 无占位符、无全样本分位、无 60/20/20 事件切分。
- [x] 文档状态明确为待独立盲审，不构成本轮自审通过。

## 验证证据

- 12 个关键文本标记检查通过：绝对 `C0`、预留现金、funding 公式、两级风险、PCG64、2000 路径、固定价格基准、bracket 选档、NAV 差、8h interval、USDT 脱锚和非自审声明均存在。
- Markdown code fence 共 54 个且成对；主文无 `TBD/TODO/待补/待定`。
- 路径长度校验：`105*168=17,640h`，截取 `8,760h+8,760h=17,520h`。
- 数值代入验证：pre-open/post-open 价格归因恒等式通过；永续 `ledger price PnL = realized PnL + ΔUPNL` 通过。
- §0 与 v3 除版本号外逐行一致；v3 和 RR3 审查文件 `git diff --quiet` 通过。

## Git

已仅针对 v4 与本报告执行 `git add`/`git commit`，提交信息为
`CARRY_V4_DRAFT: close RR3 accounting blockers`。环境拒绝创建
`.git/index.lock`，返回 `Operation not permitted`，因此未能创建任务 commit。
并行出现的采集器代码、报告、运行日志和完成事件均未暂存、回退或改写。
