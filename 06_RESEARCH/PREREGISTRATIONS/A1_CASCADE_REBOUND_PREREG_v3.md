# A-1 极端 OI 收缩 + 同窗负收益后条件回弹 预登记 v3

**任务号：** D3-R2（A-1 预登记第二次修订，应对 A1_RISK_REVIEW_v2 五项最小必改）
**状态：** PREREGISTERED DRAFT v3 — 供 Risk Reviewer 第三轮物理盲审
**起草：** Claude（主理人/CTO，thesis owner）｜**日期：** 2026-06-14
**前序：** v1（NOT APPROVED，10 条）→ v2（NOT APPROVED，2/10 闭合）→ 本 v3。v1/v2 均未放行，本 v3 为对失败盲审稿的正常修订。
**禁止动作：** 本 v3 通过第三轮盲审 + Founder 知会 + 主会话人工派发前，不得运行任何 A-1 事件后收益计算，不得读取任何 HOLDOUT。

---

## §0 命题与 v2→v3 关键结构变更

**主理人决断（应对 v2 review 的不可约项）：** v2 review 的三项最难闭合点（方向不能证强平、前置功效门读了事件后方差、小团队无真保管分离）共同指向"A-1 历史事件研究存在结构性识别上限"。v3 的处理原则是**诚实收窄**而非工程粉饰：把命题降到可观测层、把功效降为报告型诊断、把 Holdout 升级为真权限边界。若第三轮仍判不可放行于历史样本，则 A-1 应转为**前向真实强平数据**路径（采集器 2026-06-13 起，见 §13），而非继续扭曲历史设计。

**可证伪命题（v3 最终收窄版）：**
> 在"6h 名义 OI 滚动分位 ≤0.01 **且** 同窗 6h MARK 对数收益 < 0"定义的事件后，事件后 **48h** 平均 CAR 在依赖稳健推断下显著 > 0。
> 强平 / overshooting / 卖压消失仅作**未证实的机制解释**，不写入可证伪命题，不作归因结论。

| v2 review 必改 | v3 处置 | 落点 |
|---|---|---|
| #1 命题收窄 + 方向阈值依据 | 命题降到可观测层（上表）；DIR 改**纯方向 `r6h<0`**（删除无依据的 -2%）；删除"已发生机械强平""已排除被动 beta"等 overclaim | §1,§2 |
| #2 依赖稳健主推断重写 | **circular moving-block bootstrap**，块长=18 根 1H（覆盖 72h 共享窗+缓冲），B=10000，seed=20260614，**零假设重心化**（减样本均值），单侧 p=居中分布中 ≥ 观测统计量比例；算法/加权/CI 全冻结 | §4 |
| #3 功效门真正前置可执行 | 功效降为**报告型诊断**（非硬停机门）：仅用**事件前**收益方差代理 + 冻结保守 ICC 情景 {0,0.2,0.5}（判读用 0.5）；**撤销硬停机句**与无依据效应上限；设计效应只在 n_eff 计一次 | §6 |
| #4 A-2 同口径碰撞 + multiplicity | overlap 用 A-2 **原冻结变量=单个 8H funding 读数滚动 P95**（非 24h 均值）；删除 0.60 与 OR 句；non-overlap 检验**纳入确认 family**（Holm，m=3） | §7,§11 |
| #5 decision table / Protocol / 物理封存 | WF 统一为**裸均值**口径并入 FAIL 清单；Tier A=gross 机制门（**不冒充 Protocol 第五件**）/ Tier B=net 第五件；Holdout 封存文件写到 **Codex workspace-write 沙箱根之外**（执行身份无读权限）的真权限边界 | §8–§12 |

**Protocol v1.4 AI 证据三行：** ①非 LLM 作 alpha 信号；人工机制归纳，Codex 仅盲审。②最可能错处：`OI↓且负收益` 仍混入宏观普跌中段/主动减仓/普通大跌后反转，48h 正 CAR 未必源于强平消失。③不以多 agent 共识为证据。

---

## §1 机制假设（命题已降到可观测层）

A-1 检验**事件后**短周期价格行为；不预测事件何时发生。可证伪命题见 §0（仅含可观测量：OI 收缩、同窗负收益、48h CAR）。

**机制解释（标注为未证实）：** 多头强平/止损链产生机械卖压 → 临时超额供给 → 价格 overshoot → 卖压消失后回归。该解释**不写入判决**；`6h OI↓ + 同窗负收益` 是强制去杠杆的**代理**，无法证明强平方向（历史无真实强平名义额，采集器 2026-06-13 起前向）。结论措辞限定"极端 OI 收缩+同窗负收益后的条件 CAR"，**禁止**写"强制卖压已发生""因果已验证""已排除被动 beta"。被动 beta 对照见 §10，仅作诊断。

---

## §2 触发定义（冻结，自包含）

**数据源：** Binance USDT 本位永续（UM）。OI=`sumOpenInterestValue`（名义 USDT，记 `oi_notional`）。价格=MARK price K 线（与 8 币基线同源）。品种 `BTCUSDT/ETHUSDT/SOLUSDT` 池化。截止 `ts<2024-12-10T00:00:00Z`。

**OI 重采样：** 原始 5M `oi_notional`→1H 取每小时最后观测，**不前向填充**；缺桶则相关判定剔除。

**6h OI 变化：** `d6h_pct(t)=oi_notional(t)/oi_notional(t-6h)-1`，两端桶非缺失方有效。

**滚动分位：** 对 `d6h_pct(t)` 相对严格事件前窗口 `[t-365d, t)`（不含 t）求分位；**有效观测谓词（明确）：** 该窗口内**不同日历日数 ≥180** 且 有效 `d6h_pct` 样本数 ≥720，二者同时满足方产生信号（修正 v2 把 720 重叠小时误当 180 日覆盖）。ties=midrank：`pctl=(rank_avg-0.5)/N_window`。禁全样本分位。

**信号触发（冻结）：**
```text
触发(t) ⟺  (a) d6h_rolling_pctl(t) <= 0.01            （6h OI 极端收缩，下 1% 尾）
        且 (b) r6h_mark(t) < 0                          （同窗负收益，纯方向；r6h_mark=log(mark_close(t)/mark_close(t-6h))）
```
**v3 改纯方向 `r6h<0`：** 仅排除价格上涨型（空头回补型）事件，不引入幅度自由度；失败后禁改为任何幅度阈值。

**Episode（24h refractory）：** 同品种触发按时排序；首触发开 episode，`event_time`=首触发 1H 时点；其后 24h 内触发忽略；24h 后下一触发开新 episode。**严重度/funding/regime 一律取 event_time 值。**

**价格对齐：** 入场=第一个 `mark_close_timestamp > signal_available_timestamp` 的 1H MARK close；`signal_available_timestamp`=event_time 所在 1H 桶收盘后。全品种/horizon 一致。

**工作集：** §12 保管方一次性切分；n 由 work 文件唯一确定（落盘记入 §12 清单）。

---

## §3 Regime Gate（继承 P1-06，仅分层不作触发过滤）

bull=前一完整 UTC 日收盘 > 日线 SMA200；bear=≤；unknown=预热不足单独标注；无前视。子样本仅辅助解释，**正式通过不允许事后剔除 regime 达成**。

---

## §4 检验设计 + 依赖稳健主推断（v2 review #2 重写）

**观测单位：** 每 work episode 一条，池化。
**CAR（冻结）：** 1H MARK close 对数收益，事件前基准 `[event_time-72h, event_time-1h]`：
```text
baseline_mu_i = mean(log(close_tau/close_{tau-1h})) over hourly returns ending in [event_time-72h, event_time-1h]
raw_return_i,h = log(close_{align+h}/close_{align})          （align=§2 入场对齐 bar）
CAR_i,h = raw_return_i,h - h*baseline_mu_i
```
**Horizon 角色：** 主=**48h（唯一）**；次=24h（Holm，见 §11 family）；72h=仅探索，p 值不改判决。

**主推断（circular moving-block bootstrap，全冻结）：**
- 把全部 work episodes 按 `event_time` 升序排成时间序列 `{CAR_i,48h}`。
- **块=circular moving-block，块长 L=18**（18 根 episode 序？不——见下），**修正定义：** 因 episode 非等距，块以**时间宽度**定义：块长 = 连续 **96 小时**时间窗（覆盖 72h 收益窗 + 24h 缓冲），即每个 bootstrap 重抽以随机起点取此后 96h 内的全部 episodes 为一块，circular wrap；重抽块数使总 episode 数 ≈ n。
- B=10000，seed=20260614。
- **零假设重心化：** 检验统计量=样本均值；bootstrap 时对每个重抽样本减去**全样本均值**以在 H0(mean≤0) 边界重心化；单侧 p = 居中 bootstrap 均值 ≥ (观测均值 − 0) 的比例。
- cluster 加权=等 episode 权（非等块权）。95% CI=居中分布的 percentile 区间平移回观测均值。
- 普通 t-test 仅描述性，不入判决。
- 24h 次检验同法，Holm 校正阈值。

**确认性检验 family（v2 review #4，全部纳入）：** {48h 主 CAR、24h 次 CAR、§5 单调性方向检验、§7 non-overlap 48h CAR}，**m=4，Holm 控 FWER@0.05**。72h 不入 family（仅探索）。无其他确认性检验。

---

## §5 辅检验：OI 收缩幅度单调性（冻结实现）

按 `d6h_rolling_pctl` 固定档：Severe `[0,0.0033]` / Medium `(0.0033,0.0067]` / Mild `(0.0067,0.01]`（禁全样本重切）。
**单一冻结统计量：** severity 编码 Severe=2/Medium=1/Mild=0；对 48h CAR 算 **Spearman 秩相关**（severity 序 vs CAR），**预期符号为正**（severity 越高 CAR 越大），单侧；同 §4 moving-block bootstrap、同 seed、ties=midrank。计入 §4 family。

---

## §6 功效（v2 review #3：降为报告型诊断，前置可执行）

**撤销 v2 的硬停机门与无依据效应上限。** 功效仅作**预登记的报告型诊断**，不决定是否立项：
- 方差代理**仅用事件前数据**：取各 episode 事件前 `[-72h,-1h]` 1H 收益方差的池化中位数外推到 h，记 `sigma_pre_h`（不读任何事件后 CAR）。
- ICC 用**冻结保守情景** {0, 0.2, 0.5}，判读参照 **0.5**（最保守）；`n_eff_h = n/[1+(m_bar-1)*ICC]`，设计效应**只在 n_eff 计一次**（sigma 不再二次膨胀）。
- 报告 80%-power MDE：`(z_{0.95}+z_{0.80})*sigma_pre_h/sqrt(n_eff_h)`，给出 ICC∈{0,0.2,0.5} 三档。
- **不设硬停机句**；功效仅供事后解读检验灵敏度。实验是否值得执行由 Founder/CTO 在 Tier A 放行时人工裁量，不由本节自动门控。

---

## §7 A-2 碰撞门（v2 review #4：A-2 原冻结变量）

**a2_overlap（冻结，严格取 A-2 原口径）：** A-2 冻结的是**单个 8H funding 读数**相对其**此前 365 天（最少 180 天，midrank）**分布的滚动分位，正极端=**P95**。对每个 A-1 episode：取 event_time **之前最近一个已结算的 8H funding 读数**，计算其滚动分位；`>=0.95` 标 `a2_overlap=1`。**不使用 24h 均值，不另选阈值。**

**预登记报告与判决（冻结，纳入 §4 family）：**
1. 报告 overlap 比例 `p_overlap`、overlap/non-overlap 子样本 48h CAR（moving-block bootstrap）。
2. **机制独立性硬门：** non-overlap 子样本 48h CAR 在 §4 family Holm 校正后显著为正。该检验是 family 第 4 项确认性检验。
3. 删除 v2 的 `0.60` 阈值与"交互不显示可替代"OR 句。若 non-overlap 子样本经冻结方差/ICC 诊断（§6）灵敏度过低，则在报告中**标注"non-overlap 功效不足，机制独立性未确证"**，并按 family 实际显著性判 PASS/FAIL（不显著即该项 FAIL，不得以功效不足为由豁免）。
4. "不显著为负"不构成任何通过证据。

---

## §8 成本（完整公式，每边口径冻结）

```text
round_trip_cost = 2*fee_per_side + 2*slippage_per_side + holding_funding
fee_per_side=0.10%（每边）；slippage_per_side_base=0.10%（每边）；holding_funding=持有期真实 8H funding 现金流
事件类滑点压力档（每边）：0.30% / 0.50% / 1.00%
```
Tier A 仅报告 48h 在 base/0.30% 的 net CAR 作**诊断**，不构成 Tier A 通过门。

---

## §9 验收：两级门

**Tier A 机制事件研究门（本 v3 判定）：** gross CAR 机制门，过=机制成立（探索级），**不等于策略晋级，也不等于已满足 Protocol 第五件**。
**Tier B 交易策略门（另案预登记）：** Tier A 过后另立，冻结入场/持仓/杠杆/funding/退出/重叠/资本占用后，才检验**净收益**四件套、爆仓、几何增长、1.00% 压力、Protocol 第五件（net）。v3 不对 Tier B 下结论。

---

## §10 被动基准（诊断，非 Tier A 硬门）

A-1 48h gross CAR > 0 的现金零（不持仓=0）由 §4 主检验表达。同 regime 同品种被动 buy-and-hold mean CAR **仅作诊断**报告（A-1 是否亦跑赢被动 beta），**不作 Tier A 硬门**（避免被动基准定义争议阻断机制判定）。**Protocol v1.4 第五件（net 收益 > 现金零）归 Tier B**，v3 不冒称已满足。

---

## §11 唯一闭合 Decision Table（v2 review #5）

**所有"CAR>0"=§4 moving-block bootstrap 单侧 Holm 校正后显著（点估计>0 且依赖稳健显著）。** family={48h, 24h, 单调性, non-overlap}，m=4 Holm。

**Tier A PASS（全满足）：**
- [ ] 48h CAR：family Holm 后显著（主项）。
- [ ] 单调性：Spearman 正、family Holm 后显著。
- [ ] A-2 碰撞：non-overlap 48h CAR family Holm 后显著为正。
- [ ] WF 稳定性（**裸均值口径，冻结**）：按 work episode 时间序切 3 段，48h mean CAR（裸均值，不做显著性）在 **≥2 段 > 0**；同一 moving-block cluster 不跨段切分点。
- [ ] 未发现任何 Holdout 读取/全样本分位/触发或 episode 规则重设/cutoff 后行情补齐。

**Tier A FAIL（任一即 FAILED）：**
- 48h CAR family Holm 后不显著。
- 单调性不显著（或符号为负）。
- non-overlap 48h CAR family Holm 后不显著。
- **WF 稳定性 <2 段 > 0**（v3 新增入 FAIL 清单）。
- 发现 Holdout 读取/全样本分位/规则重设/cutoff 后补齐。

**判读纪律：** 主 horizon 唯一=48h，禁 24h/48h 事后择优（24h 仅 family 次项与稳健性参考）；72h 仅探索不入判定；任一必要项 N.A.→整体 FAIL；不显著正点估计只写"未拒绝 H0/未验证"。

---

## §12 Holdout 物理封存（v2 review #5：真权限边界）

1. **保管进程**（独立脚本，由主会话身份运行，非 Codex 执行身份）一次性生成全部 pooled episodes，按 `(event_time_utc, symbol)` 排序 deterministic 每第 5 个预留 sealed，其余 work。
2. **真权限边界：** `work_episodes.csv` 写入 Codex workspace-write 沙箱根内（`06_RESEARCH/DATA/A1_WORK/`）；`sealed_holdout_episodes.csv` 写入**沙箱根之外**的路径（`~/.aiquant_sealed/a1/`，Codex `-C` workspace-write 不授予读权限），执行身份物理无法读取。
3. 产出 `A1_HOLDOUT_MANIFEST.json`（落 work 侧，可见）：work/sealed 各行数、schema、生成代码 git hash、两文件 SHA-256、生成时间、保管人=主会话、解封条件（Tier A 通过+Founder 批）、一次性使用记录字段。封存**内容**不可见，仅清单可见。
4. 研究执行入口对任何 sealed/holdout 路径硬 assert 拒绝（防误操作，二重保险）。
5. 有效 n 仅由 work 文件计算。违反即纪律违规、研究作废。
6. A-2 holdout（`a2_events_holdout.csv` 218 条）完全独立，禁读。

---

## §13 失败后禁止行为 + 前向路径（锁死）

Tier A FAILED 后禁止：改 OI 阈值/方向规则/episode 规则/分位窗口后重测；排除年份/品种/regime/funding 后重测；72h 或 24h 单独显著改写为通过；全样本分位；cutoff 后补 horizon；读 Holdout"确认"失败。

**前向路径（主理人议程，rule8）：** 若失败为功效不足或历史方向识别不可约（而非方向反证），A-1 应转**前向真实强平名义额**路径——用 2026-06-13 起采集器的真实清算数据做方向识别（替代价格代理），积累 3–6 月后另写新预登记重新盲审，明确与本次区别。这是已部署强平采集器的首个明确 alpha 用途。

本 v3 锁定后，对触发/方向规则/成本/分层/horizon/验收/Holdout 的任何修改均视为新假设，不得在 v3 名义下继续。
