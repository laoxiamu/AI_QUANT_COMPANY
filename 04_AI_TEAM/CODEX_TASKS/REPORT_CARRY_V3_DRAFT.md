# CARRY-V3-DRAFT 执行报告

**任务：** 起草 Delta 中性 Carry 预登记 v3，闭合 CARRY-RR2 六项开口
**日期：** 2026-06-14
**状态：** completed（起草完成，待独立 Reviewer 盲审）
**审查结论：** 本轮不作 APPROVED/NOT APPROVED 自审裁决

## 交付

- v3 草案：`06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v3.md`
- 完成事件：`04_AI_TEAM/TASK_INBOX/CARRY_V3_DRAFT_DONE.json`

## 任务前自查

1. **验证机制：** 未改写 funding carry 命题；只把资本、双腿状态、保证金、事件和前向确认变成唯一可执行口径。
2. **量化验收：** 六项开口均可用公式、固定时间、固定 seed、固定样本量和二元状态逐条核对。
3. **更便宜等效实现：** 以 v2 为基线重写完整自包含 v3；不运行数据、不新增回测或黑箱依赖。
4. **禁止项：** 未读取 Holdout/`01_MEMORY_CORE/`，未运行回测，未修改 v2，未改变 §0 核心重构或机制命题。

## 六项闭合

1. **资本/N 恒等式：** 固定 `C0=S0+M0+B0+E0`，缓冲/事件现金各 10%，其余 80% 按 70/30 分给 BTC/ETH 配对预算；用现货/永续开盘价联立求等数量双腿和 1.0 倍初始保证金，并给资本占用表和唯一收益率分母。
2. **OI 双腿减仓：** 减仓和恢复均交易现货与短永续，冻结 50%/100% 数量、次一根 1H open、减仓/恢复腿序、60 秒第二腿门、失败撤销及 24h refractory。
3. **1H 强平 bootstrap：** 同步抽样完整 1H 状态向量，730 天路径前 365 天 warm-up、后 365 天评价；2000 条路径逐小时重跑 cross-margin、维持保证金、次小时补款、强平及事件压力账本。
4. **事件冻结：** Merge、LUNA、3AC、FTX 均写为半开 UTC 窗口；永续脱锚和 Binance 提现暂停使用机械扫描规则，冻结脱锚退出/恢复动作和事件 manifest SHA。
5. **前向 shadow：** 历史 baseline PASS 后，从下一个 UTC 月首开始；最少 18 个完整前向月、`n>=1620`、最多 24 月，只检验一次；30 天块、10000 次、`seed=20260614`、单侧 5%，并冻结小额真金申请上限。
6. **RR2 其余歧义：** 唯一化 venue/合约/账户模式/价源/再平衡腿/费率；分离基础 carry 与 OI 模块判决；补 PnL 去重、CI/零假设、WF 结算、历史保证金阶梯、清算费、ADL/破产/USDT 折价和 Holdout 固定引用。

## 边界

- v3 状态明确为 `PREREGISTERED DRAFT v3`，须由 CTO 另派独立 Reviewer 盲审。
- 未读取任何 Holdout、sealed 数据或 `01_MEMORY_CORE/`。
- 未运行策略回测、收益统计、事件研究或参数搜索。
- 未改 `CARRY_DELTA_NEUTRAL_PREREG_v2.md` 和 `CARRY_RISK_REVIEW_v2.md`。
- 工作区已有的 `CARRY_V3_DRAFT_RUN.log`、`FIX_COLLECTOR_V2_RUN.log` 修改未回退、未改写、未纳入本任务提交。

## 静态验收自检

- [x] 日期为 2026-06-14，Protocol v1.4 AI 证据三行保留。
- [x] §0 历史 feasibility-lock / 前向 shadow / 证据等级核心重构保留。
- [x] 六项任务开口均有显式章节、公式或算法。
- [x] 无占位符；无全样本分位；无 Holdout 读取或回测产物。
- [x] 文档明确不构成本轮自审通过。

## 验证证据

- `jq -e`：完成事件字段、`items_closed=6` 和输出路径通过。
- 14 个关键文本标记检查：资本恒等式、双腿 50%、1H 路径、四个事件、18 月/`n>=1620`/seed 均存在。
- 示例价格代入：六个资本桶合计 `1,000,000.00`，严格等于示例 `C0`。
- 路径长度：`105*168 >= 17,520`，warm-up `8,760h` + 评价 `8,760h` = `17,520h`。
- OI §3 独立扫描：存在双腿同步减仓，未发现单腿减仓措辞。
- v2 基线和 RR2 review 的 `git diff --name-only` 为空。

## Git 状态

已尝试仅暂存 v3、执行报告和完成事件，并创建
`CARRY_V3_DRAFT: draft carry preregistration v3` 提交。环境拒绝创建
`.git/index.lock`，返回 `Operation not permitted`，因此未能创建任务 commit。
未改动、暂存或回退工作区已有的两份运行日志。
