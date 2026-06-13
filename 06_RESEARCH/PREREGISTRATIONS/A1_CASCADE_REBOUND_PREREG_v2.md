# A-1 强制去杠杆卖压后条件回弹 预登记 v2

**任务号：** D3-R（A-1 预登记修订，应对 A1_RISK_REVIEW_v1）
**状态：** PREREGISTERED DRAFT v2 — 供 Risk Reviewer 第二轮物理盲审
**起草：** Claude（主理人/CTO，thesis owner）｜**起草日期：** 2026-06-14
**前序：** v1（`A1_CASCADE_REBOUND_PREREG_v1.md`）经 `A1_RISK_REVIEW_v1.md` 盲审结论 **NOT APPROVED（需修改后通过）**。v1 从未放行，本 v2 为对失败盲审稿的正常修订，非 §10 锁后改题。
**禁止动作：** 本 v2 通过 Risk Reviewer 第二轮盲审 + Founder 知会 + Claude 主会话人工派发之前，不得运行任何 A-1 事件后收益计算，不得读取任何 HOLDOUT 目录/文件，不得据结果反改触发/分层/成本/验收口径。

---

## §0 审查整改对照表（v2 对 A1_RISK_REVIEW_v1 十项最低条件的逐条响应）

| # | Reviewer 必改项 | v2 处置 | 落点 |
|---|---|---|---|
| 1 | 封闭强制卖压方向识别，或降低因果主张 | 加入**冻结价格方向代理过滤**（OI 骤降窗内并发负价格冲击）；命题改为"proxy 识别的强制去杠杆卖压后条件回弹"；无历史真实强平名义额（采集器 2026-06-13 起前向，历史不可得），明确标注为 proxy 非 proof | §1, §2 |
| 2 | 自包含冻结 OI/分位/episode/event_time/缺失/价格对齐 | §2 给出 `d6h` 公式、OI 来源字段口径、5M→1H 重采样、滚动窗口与 midrank、180d 有效观测门、**24h refractory window 取代 single-linkage 链接**、event_time=首触发、价格对齐严格不等号 | §2 |
| 3 | 唯一主 horizon 或多重校正；依赖稳健主推断 | **主 horizon 唯一=48h**；24h 为预登记次要（Holm 校正）；72h 仅探索不支持通过；**global-event-cluster 块 bootstrap 为主推断**（seed/块/次数冻结），t-test 仅描述 | §4, §5 |
| 4 | 80% power + n_eff + 保守方差重做 MDE；补效应区间依据 | §6 用 `(z_{1-α}+z_{1-β})σ/√n_eff`、power=80%、保守方差、各 horizon 实际 n_eff；B4 降为乐观预检；**撤销 1.5–3.0% 作硬功效上限**（降为启发先验，不作门） | §6 |
| 5 | 用 A-2 冻结极端阈值定义 overlap + 不可区分判决 | §7 `a2_overlap` := 事前 funding 滚动分位 **≥0.95**（A-2 冻结正极端 P95，非另选）；预登记 overlap 率/交互项；高重叠或非重叠欠功效→**"机制不可区分"** | §7 |
| 6 | 分离事件研究门与策略门；完整成本/每边滑点/真实 funding | §8 **两级门**：Tier A 机制事件研究门（本 v2）/ Tier B 交易策略门（另案预登记）；完整成本公式每边口径冻结 | §8, §9 |
| 7 | 事件类现金零基准为硬门，或先正式解决协议冲突 | §10 **以 Protocol v1.4 现金零基准为硬门**（主理人裁决：上位协议优先）；同 regime 被动 buy-and-hold 降为诊断 | §10 |
| 8 | 唯一闭合 decision table + 确认检验预算 | §11 唯一二元 decision table；§4 确认性检验总预算上限=**3**（48h 主 + 24h 次 + 单调性 1）；消除所有 OR 选择 | §4, §11 |
| 9 | （含于 3/6/8） | 同上 | — |
| 10 | Holdout 升级为有保管人/哈希/访问边界的物理封存 | §12 一次性保管方切分：work/sealed 分别落盘 + 行数/schema/代码版本/SHA-256 清单 + 保管人/解封条件/一次性使用记录 + 路径拒绝 | §12 |

**Protocol v1.4 AI 证据三行：**
1. 本假设非 LLM 作为 alpha 信号生成；来自机会地图与人工机制归纳，Claude 起草，Codex 仅独立盲审。
2. 最可能错处：OI 骤降+并发负价代理仍可能由"持续单边去杠杆中段"而非"清算结束 overshoot"产生，导致事件后无正回弹。
3. 不以多 agent 共识为证据；A-2 碰撞门仅作机制隔离材料。

---

## §1 机制假设（命题边界已收窄）

A-1 检验**已发生的机械性强制去杠杆事件之后**是否存在短周期价格回归；不预测强制事件何时发生。

冻结因果链（条件化表述）：

```text
多头强平 / 止损链 已经发生（机械、非自愿卖出）
    -> 6h OI 极端骤降 且 并发负价格冲击（卖压方向代理）
    -> 机械平仓订单短时冲击 -> 临时超额供给 -> 价格相对短期均衡 overshooting
    -> 主动买方回归 / 被动卖压消失
    -> 事件后均值回归，表现为正向 CAR
```

**核心可证伪命题（收窄版）：** 在"OI 6h 极端骤降 **且** 同窗负价格冲击"代理识别的强制去杠杆卖压事件后，事件后 **48h** 平均 CAR 显著大于 0，且该超额不能仅由同 regime 被动 beta 或 A-2 极端正 funding 拥挤状态解释。

**方向识别诚实声明（Reviewer 条件 1）：** 6h OI 下降本身无法区分多头强平卖出 / 空头回补买入 / 主动双边减仓 / 移仓 / 宏观去杠杆。v2 用"同窗负价格冲击"作为**强制卖压方向代理**（多头强平伴随价格下行；空头回补伴随价格上行，被此过滤排除）。该代理在 §2 看任何事件后收益前冻结。本研究**不声称**已直接观测到强平名义额；结论措辞限定为"proxy 识别的强制去杠杆卖压后条件回弹"，不得写"强制卖压已证实发生""因果回归已验证"。真实强平名义额仅 2026-06-13 起前向采集，历史工作集不可得；若未来前向数据足量，另案以真实名义额重做方向识别。

**效应区间（Reviewer 条件 1/4）：** 撤销 v1 的 1.5%–3.0% 作为功效门机制上限。该区间无可核查来源，降级为**启发先验**，仅供事后讨论参照，**不作为任何通过/功效硬门**。功效门改由 §6 保守方差 + 80% power 决定。

---

## §2 触发定义（冻结，自包含，不可修改）

**数据源（冻结）：** Binance USDT 本位永续（UM）。OI 字段=交易所 `sumOpenInterest`（合约张数口径）经 `sumOpenInterestValue`（名义 USDT）二者均落盘；主信号用**名义 USDT OI**（`oi_notional`）以消除张数面值变更影响。价格用 MARK price K 线（与 8 币基线同源，避免 v1 的 contract/mark 混用）。品种：`BTCUSDT, ETHUSDT, SOLUSDT`，池化。截止：`ts < 2024-12-10T00:00:00Z`。

**OI 重采样（冻结）：** 原始 5M `oi_notional` → 1H，取每小时**最后一个**观测值，**缺口不前向填充**；某 1H 桶无观测则该桶 OI 缺失，相关触发判定剔除（不补值）。

**6h OI 变化（冻结公式）：**
```text
d6h_pct(t) = oi_notional(t) / oi_notional(t-6h) - 1
```
要求 `t` 与 `t-6h` 两端 1H 桶 OI 均非缺失，否则该 t 不参与。

**滚动分位（冻结）：** 对每个 `d6h_pct(t)`，相对**严格事件前**窗口 `[t-365d, t)`（不含 t 自身）的历史 `d6h_pct` 分布求分位；窗口内**有效观测数 ≥ 180×24×(1/6)** 实际等价为"≥180 日历日且该窗口有效 d6h 样本数 ≥ 720"（每日约 4 个非重叠 6h 步长的保守下限），不足则该 t 不产生信号。ties 用 **midrank**（平均秩）：`pctl = (rank_avg - 0.5)/N_window`。禁止全样本分位。

**信号触发（冻结）：**
```text
触发(t) 当且仅当：
  (a) OI 条件： d6h_rolling_pctl(t) <= 0.01           （6h OI 极端骤降，下 1% 尾）
  且
  (b) 方向代理： r6h_mark(t) <= DIR_THRESHOLD          （同窗负价格冲击，强制卖压代理）
        其中 r6h_mark(t) = log( mark_close(t) / mark_close(t-6h) )
        DIR_THRESHOLD = -0.02   （冻结：6h 内 MARK 对数收益 ≤ -2%）
```
`DIR_THRESHOLD=-2%` 在看任何事件后收益前冻结，理由：排除 OI 骤降伴随价格上行（空头回补型）的事件，保留价格下行（多头强平型）。该值为结构参数，失败后禁改。

**Episode 定义（冻结，取代 v1 single-linkage）：** 同品种触发按时间排序。采用 **24h refractory window**：首个触发开启 episode，`event_time` = 该首触发的 1H 时点；其后 24h 内的所有触发**忽略**（不延长、不链接）；24h 之后的下一个触发开启新 episode。该规则消除 v1 "每 23h 触发无限链式延长"的弹性。

**Episode 严重度 / funding / regime 取值（冻结）：** 一律取 **event_time（首触发）时点**的值，不取极值、不取末值。

**价格对齐（冻结）：** 事件入场对齐点 = 第一个满足 `mark_close_timestamp > signal_available_timestamp` 的 1H MARK close bar；其中 `signal_available_timestamp` = event_time 所在 1H 桶**收盘后**（即不使用尚未完成的 OI 小时信息入场）。全部品种/ horizon 一致。

**工作集生成（冻结）：** 池化全部 episodes（BTC/ETH/SOL），按 §12 物理保管方一次性切分为 work / sealed-holdout；正式工作集 n 由 work 文件唯一确定（不再在文档中硬编码 163，因加入方向代理过滤后池化总数将变化，实际 n 以保管方落盘行数为准并记入 §12 清单）。

---

## §3 Regime Gate（继承 P1-06，仅分层不作触发过滤）

冻结 regime（与 P1-06 验收口径一致）：
- **bull：** 该品种前一完整 UTC 日收盘 `>` 日线 SMA200。
- **bear：** 前一完整 UTC 日收盘 `<=` 日线 SMA200。
- **unknown：** SMA200 预热不足；不强归 bear，单独标注。
- **无前视：** 仅用已完成 UTC 日数据。

bull/bear/unknown 子样本仅作辅助解释与风险识别；**正式通过条件不允许通过事后剔除某一 regime 达成**。

---

## §4 检验设计（唯一主 horizon + 依赖稳健主推断）

**观测单位：** 每个 work episode 一条；BTC/ETH/SOL 池化。

**指标 CAR（冻结）：** 用 1H MARK close 对数收益，事件前基准期 `[event_time-72h, event_time-1h]`：
```text
baseline_mu_i = mean( log(close_tau / close_{tau-1h}) )   over hourly returns ending in [event_time-72h, event_time-1h]
raw_return_i,h = log( close_{align+h} / close_{align} )      （align = §2 入场对齐 bar）
CAR_i,h = raw_return_i,h - h * baseline_mu_i
```

**Horizon 角色（冻结，Reviewer 条件 3/8）：**
- **主 horizon = 48h（唯一确认性主检验）。**
- **次要 horizon = 24h**：预登记次要确认性检验，与主检验组成 family，用 **Holm 校正**（m=2）控制 FWER@0.05。
- **72h = 仅探索**：报告点估计与形态，**任何 p 值不得改变 PASS/FAIL 结论**。

**确认性检验总预算 = 3：** {48h 主 CAR、24h 次 CAR（Holm）、§5 单调性 1 个方向检验}。A-2 碰撞为隔离诊断（§7），不计入确认预算但有冻结判决。除此之外不得新增确认性检验。

**主推断（依赖稳健，冻结）：**
- `H0: mean(CAR_48h) <= 0`，`H1: mean(CAR_48h) > 0`，单侧。
- **Global-event cluster 块 bootstrap 为主推断**：同一**日历日（UTC）**内跨品种的 episodes 归为同一 cluster；以 cluster 为重采样单位做 block bootstrap，`B = 10000`，**seed = 20260614**，单侧 p 由 bootstrap 分布给出。
- 普通单样本 t-test **仅作描述性对照**，不作通过依据（消除 v1 把 163 当独立观测的问题）。
- 48h/72h 事件后窗口跨 episode 可重叠的依赖，由 cluster 块重采样吸收。

**24h 次检验：** 同一 cluster bootstrap 方法，Holm 校正后阈值。

---

## §5 辅检验：OI 骤降幅度单调性（冻结方向）

按 `d6h_rolling_pctl` 固定区间三档（禁止用工作集全样本重切）：
- Severe：`0 <= pctl <= 0.0033`
- Medium：`0.0033 < pctl <= 0.0067`
- Mild：`0.0067 < pctl <= 0.0100`

**单一冻结统计量：** 对 **48h** CAR，检验 `CAR_Severe >= CAR_Medium >= CAR_Mild` 的单调性，用一个方向性统计量（Spearman 秩相关 between severity 序与 CAR，单侧），cluster 块 bootstrap 同 seed。仅此一个方向检验计入确认预算。报告按 severity 方向呈现避免符号误读。

---

## §6 功效段（80% power + n_eff + 保守方差）

**撤销 v1 alpha-only 口径。** 正式功效：
```text
MDE_h = (z_{1-α} + z_{1-β}) * sigma_eff_h / sqrt(n_eff_h)
α=0.05 单侧, z_{0.95}=1.6448536269514715
power=80%, z_{0.80}=0.8416212335729143
```
- `n_eff_h` = 各 horizon 在 work 集上的**有效样本量**，用 cluster 设计效应折算：`n_eff = n_episodes / (1 + (m_bar-1)*ICC_proxy)`，其中 `m_bar`=平均每 cluster episode 数，`ICC_proxy` 由 cluster 内 CAR 相关的保守上界估计（事前用 0.3 保守值，实际执行用 work 集估计但不读事件后均值方向——仅用方差结构）。
- `sigma_eff_h` = 保守方差：取 max( 无条件 1H MARK 收益方差外推, 事件条件方差 )，并对依赖加设计效应膨胀。
- B4 表（v1 §5）**降级为乐观预检**，不作功效门。
- **停机条件：** 若 48h 的保守 MDE 高于任何有依据的合理效应估计，实验前停止，不跑事件后收益。

报告：48h、24h 的 80%-power MDE 与 n_eff；72h 仅附参考。

---

## §7 A-2 碰撞门（用 A-2 冻结极端阈值）

**a2_overlap 定义（冻结，取自 A-2 v1）：** A-2 极端正 funding（多头拥挤）= 事前 funding 读数滚动分位 **≥ 0.95**（P95），滚动口径与 A-2 一致：每读数对**此前 365 天**（首年扩张窗，最少 180 天）分布比较，midrank，仅用事件前数据。对每个 A-1 episode，计算 event_time 前 `[-24h,-1h]` 平均 funding 的滚动分位；`>=0.95` 标记 `a2_overlap=1`，否则 0。**禁止为 A-1 另选更有利阈值。**

**预登记报告与判决（冻结）：**
1. 报告 overlap 比例 `p_overlap`。
2. 报告 overlap / non-overlap 子样本 48h CAR（cluster bootstrap）。
3. 预登记**交互检验**：CAR_48h ~ a2_overlap，单一交互项，检验回弹效应是否仅由 overlap 驱动。
4. **机制独立性最低要求：** non-overlap 子样本 48h CAR 仍为正、依赖稳健、Holm 后显著；或交互项不显示效应仅由 overlap 驱动。
5. **"机制不可区分"判决：** 若 `p_overlap` 过高（≥0.60）使 non-overlap n_eff 低于 §6 功效门，或 non-overlap 子样本不显著，则判 A-1 与 A-2 极端拥挤**机制不可区分**，碰撞门 **FAIL**（不得写成通过）。
6. **"不显著为负"不单独构成通过证据**（消除 v1 把 absence of evidence 当 independence）。

---

## §8 成本（完整公式，每边口径冻结）

事件研究本体不含交易成本；但事件→策略需完整成本，且 v2 在 Tier A 即报告净额敏感性以防 Tier A 通过后 Tier B 不可行。

**完整往返成本（冻结，每边口径）：**
```text
round_trip_cost = 2*fee_per_side + 2*slippage_per_side + holding_funding
fee_per_side = 0.10%       （手续费，每边）
slippage_per_side_base = 0.10%   （基准滑点，每边）
holding_funding = 事件持有期真实 8H funding 现金流（按 align→align+h 实际结算笔数）
```
**事件类滑点压力档（每边，追加）：** `0.30% / 0.50% / 1.00%`（替换 v1 的 0.05/0.10/0.20 表，后者不满足协议）。

Tier A 报告：48h 在 base、0.30% 两档下的 net CAR（仅诊断，不构成 Tier A 通过门）。**完整四件套/爆仓/几何增长/1.00% 硬档归 Tier B。**

---

## §9 验收：两级门（Reviewer 条件 6）

**Tier A — 机制事件研究门（本 v2 判定对象）。** 通过=机制成立（探索级），**不等于策略晋级**。
**Tier B — 交易策略门（另案预登记）。** 仅在 Tier A 通过后立项，冻结入场成交时刻/持仓名义/杠杆/funding 结算/退出成交/同品种重叠持仓/资本占用后，才检验完整成本四件套、爆仓概率、几何增长、1.00% 压力。**v2 不对 Tier B 下任何结论。**

---

## §10 第五件：现金零基准（硬门，Protocol v1.4）

**主理人裁决（Reviewer 条件 7）：** v1 用"同 regime 全部起点 buy-and-hold"与 Protocol v1.4 事件类**现金零基准**硬门冲突。依文档权威层级（Protocol > 本预登记），**以现金零基准为硬门**：A-1 48h mean CAR 必须显著 > 0（即跑赢"事件后不持仓=0 收益"的现金基准，已由 §4 主检验 `mean(CAR)>0` 表达）。同 regime 同品种被动 buy-and-hold mean CAR **降为诊断**（报告 A-1 是否亦跑赢被动 beta，但不作硬门，避免被动基准定义争议阻断机制判定）。

---

## §11 唯一闭合 Decision Table（Reviewer 条件 8）

**全部为 Tier A 判定。所有"CAR > 0"指 cluster bootstrap 单侧 p < 校正后阈值（点估计为正且依赖稳健显著），不是裸点估计。**

PASS 须全部满足：
- [ ] 主：48h CAR cluster-bootstrap 单侧 `p < 0.05`（Holm family 中 48h 为更强项时阈值 0.025；以 Holm 程序实际给出的拒绝为准），点估计 > 0。
- [ ] 现金零基准硬门：48h mean CAR > 0 且上条显著（§10）。
- [ ] A-2 碰撞门：non-overlap 子样本 48h CAR 依赖稳健显著为正，且未判"机制不可区分"（§7）。
- [ ] 单调性：48h CAR 随 severity 单调性方向检验显著（§5）。
- [ ] WF 稳定性：按 work episode 时间序切 3 段，**同一主 horizon 48h** 至少 2 段 mean CAR > 0（仅稳定性，不调参；同一 global cluster 不跨段）。

FAIL（任一即 FAILED）：
- 48h CAR Holm 后不显著（无论 24h/72h 如何）。
- 现金零基准门不满足。
- A-2 碰撞门 FAIL 或判"机制不可区分"。
- 单调性方向检验不显著。
- 发现任何 Holdout 读取 / 全样本分位 / 触发或 episode 规则重设 / cutoff 后行情补齐。

**判读纪律：**
- 唯一主 horizon=48h；**禁止事后在 24h/48h 间择优**。24h 仅作 Holm family 次项与稳健性参考，不能单独支撑通过。72h 仅探索，不入判定。
- 任一必要项因样本不足为 N.A. → **整体 FAIL**（不自动放行）。
- 不显著正点估计只能写"未拒绝 H0 / 未验证"，不得写"方向正确/部分成功/有一定效果"。
- 24h 与 48h 方向不一致、或 funding 分组负但不显著 → 不得解释为"方向一致"。

---

## §12 Holdout 物理封存（Reviewer 条件 10）

**升级为保管方一次性切分（取代 v1 逻辑切分）：**
1. 由**独立保管脚本**（非研究执行脚本）一次性生成全部 pooled episodes，按 `(event_time_utc, symbol)` 排序后 deterministic 每第 5 个预留为 sealed-holdout，其余为 work。
2. 分别落盘：`work_episodes.csv` / `sealed_holdout_episodes.csv`，二者**不在同一分析进程加载**。
3. 产出冻结清单 `A1_HOLDOUT_MANIFEST.json`：work/sealed 各自行数、schema、生成代码 git commit hash、两文件 **SHA-256**、生成时间、保管人=Claude 主会话、解封条件（Tier A 通过且 Founder 批准）、一次性使用记录字段。
4. 研究执行入口对任何含 `HOLDOUT`/`sealed` 路径的读取**硬 assert 拒绝**。
5. 任一 horizon 的有效 n 仅由 work 文件计算；持有原始特征者虽理论可重建，但封存清单 + 一次性使用记录 + 路径拒绝构成审计边界，违反即记纪律违规、研究作废。

**禁止：** Risk Reviewer 通过、Founder 知会、Claude 主会话派发**之前**，任何步骤不得读取 work 之外数据，不得读取 A-2 holdout（`a2_events_holdout.csv` 218 条，完全独立）。

---

## §13 失败后禁止行为（预登记锁死，承袭 v1 §10 并强化）

若 Tier A FAILED，禁止：改 OI 阈值/方向阈值/episode 规则/分位窗口后重测；排除特定年份/品种/regime/funding 后重测；把 72h 或 24h 单独显著改写为机制通过；用全样本分位重算；用 cutoff 后行情补 horizon；读 Holdout"确认"失败是否噪音。

允许：若失败为**功效不足**而非方向反证，等前向真实强平采集 3–6 个月以更大 n 且**真实强平名义额方向识别**另写新预登记重新盲审，明确与本次区别。

本 v2 锁定后，对触发/方向代理/成本/分层/horizon/验收门/Holdout 切分的任何修改均视为新假设，不得在 A-1 v2 名义下继续。
