# A-1 极端 OI 收缩 + 同窗负收益后条件回弹【关联】事件研究 预登记 v5

**任务号：** D3-R4（A-1 预登记第四次修订，应对 A1_RISK_REVIEW_v4 四项最小必改）
**状态：** PREREGISTERED DRAFT v5 — 供 Risk Reviewer 第五轮物理盲审
**起草：** Claude（主理人/CTO）｜**日期：** 2026-06-15
**依据决策：** DEC-075（Founder "按推荐继续" 确认两段式路径）。**本 = 路径A（历史关联快筛）**：Tier A 严格定义为"可观测条件回弹【关联】（探索级）"，**不声称强平/overshooting 机制成立，不耗独立 Alpha 计数**（非机制确证实验）。强平机制确证归路径B（前向真实强平数据，另立预登记），见 §13 与 `A1_FORWARD_LIQUIDATION_PATH.md`。
**前序：** v1→v2→v3→v4 全 NOT APPROVED。RR4：v4 闭 2/5（功效治理 CLOSED、family CLOSED），余 4 项判为"文字与算法冻结、不要求达机制确证严格度"。本 v5 逐条闭合 RR4 四项。
**v5 对 RR4 四项最小必改的处置：** ①§7 "机制独立性硬门"→"A-2 非重叠关联硬门"（去机制识别含义）；②§4 circular 改半开 UTC 网格 `[t_1,t_n+1h)`+回绕按 circular offset 截断，§5 Spearman 改**配对 moving-block bootstrap 对 ρ 居中**（真检验 ρ=0）；③§11 WF 冻结唯一段长/余数分配/切点 c=相邻中点/按实际读取足迹 purge/purge 后不重分段；④§12 冻结 **AES-256-GCM**（nonce‖密文‖tag 格式+认证失败判据）+密钥独立 principal 不可读+负向测试留命令/退出码/失败证据。
**禁止动作：** 本 v5 通过第五轮盲审 + Founder 知会 + 主会话人工派发前，不得运行任何事件后收益计算，不得读取任何 HOLDOUT。

---

## §0 命题、计数定性、与 v3→v4 五项闭合对照

**研究计数定性（DEC-075）：** 本研究是**机制前的可观测条件关联快筛**，**不耗独立 Alpha 计数**；结论上限=关联层。其唯一允许结论是"在冻结的可观测条件后，48h 平均 CAR 在依赖稳健推断下是否显著>0"。**禁止**任何"强平/overshooting/卖压消失机制成立/已验证"措辞。

**可证伪命题（关联层，最终）：**
> 在"6h 名义 OI 滚动分位 ≤0.01 **且** 同窗 6h MARK 对数收益 < 0"定义的事件后，事件后 **48h** 平均 CAR 在依赖稳健推断（§4 moving-block bootstrap，Holm family m=4）下显著 > 0。

| RR3 第三轮必改 | v4 处置 | 落点 |
|---|---|---|
| #1 消除残留因果 overclaim | 全文 Tier A 改"可观测条件回弹**关联**（探索级）"；§9 删"机制成立"；命题/结论仅关联层；强平/overshooting 仅列为路径B待验证解释 | §0,§1,§9 |
| #2 一次性闭合依赖推断 | block 宽 **W=144h**；非等距时间块**半开 UTC 网格 `[t_1,t_n+1h)` 均匀起点**+circular offset 抽样/空块跳过/回绕按 offset 截断/episode 等权/`+1` p 值/basic CI；Spearman 改 **配对 moving-block bootstrap 对 ρ 居中**（RR4 #2 修正，真检验 `H0:ρ=0`） | §4,§5 |
| #3 正式解决功效治理 | 依 DEC-075：本研究不耗独立计数→Protocol §六硬门不强制约束；功效=报告型诊断；以 **Protocol 增补件**留痕（`RESEARCH_PROTOCOL_v1.4_A1SCREEN_ADDENDUM.md`）；定义 `sigma_pre_h`、`m_bar` | §6 |
| #4 统一 family | 全文 Holm **m=4**（§0/§4/§11 一致，删除 v3 残留 m=3） | §4,§11 |
| #5 闭合 WF 与真封存 | WF 冻结**按 episode 数等分三段+切点 120h purge**；sealed holdout **加密存储**（主会话持密钥，执行身份无密钥不可解），留**负向权限测试**记录 | §11,§12 |

**Protocol v1.4 AI 证据三行：** ①非 LLM 作 alpha 信号；人工机制归纳，Codex 仅盲审。②最可能错处：`OI↓且负收益` 仍混入宏观普跌中段/主动减仓/普通大跌后反转，48h 正 CAR 未必有可交易关联。③不以多 agent 共识为证据。

---

## §1 假设（关联层，机制仅作路径B待验证解释）

A-1 路径A 检验**事件后**短周期价格行为，命题见 §0（仅含可观测量）。

**机制解释（标注为路径B待验证，不写入本研究判决）：** 多头强平/止损链 → 机械卖压 → 临时超额供给 → overshoot → 卖压消失后回归。历史无真实强平名义额（采集器 2026-06-13 起前向），`6h OI↓+同窗负收益` 仅为**强制去杠杆代理**，**无法识别强平方向**（RR3 不可约裁定）。本研究结论严格限"极端 OI 收缩+同窗负收益后的条件 CAR 关联"，**禁止**写"强制卖压已发生""因果已验证""机制成立""已排除被动 beta"。

---

## §2 触发定义（冻结，自包含）

**数据源：** Binance USDT 本位永续（UM）。OI=`sumOpenInterestValue`（名义 USDT，`oi_notional`）。价格=MARK price K 线。品种 `BTCUSDT/ETHUSDT/SOLUSDT` 池化。截止 `ts<2024-12-10T00:00:00Z`。

**OI 重采样：** 5M `oi_notional`→1H 取每小时最后观测，不前向填充；缺桶相关判定剔除。

**6h OI 变化：** `d6h_pct(t)=oi_notional(t)/oi_notional(t-6h)-1`，两端桶非缺失方有效。

**滚动分位：** `d6h_pct(t)` 相对严格事件前窗口 `[t-365d, t)`（不含 t）求分位。**有效观测谓词：** 窗口内不同日历日数 ≥180 且 有效 `d6h_pct` 样本数 ≥720，二者同时满足。ties=midrank：`pctl=(rank_avg-0.5)/N_window`。禁全样本分位。

**信号触发（冻结）：** `触发(t) ⟺ d6h_rolling_pctl(t) <= 0.01 且 r6h_mark(t) < 0`，其中 `r6h_mark=log(mark_close(t)/mark_close(t-6h))`（纯方向，无幅度自由度；失败后禁改为任何幅度阈值）。

**Episode（24h refractory）：** 同品种触发按时排序；首触发开 episode，`event_time`=首触发 1H 时点；其后 24h 内触发忽略；24h 后下一触发开新 episode。严重度/funding/regime 取 event_time 值。

**价格对齐：** 入场=第一个 `mark_close_timestamp > signal_available_timestamp` 的 1H MARK close；`signal_available_timestamp`=event_time 所在 1H 桶收盘后。全品种/horizon 一致。

**工作集：** §12 保管方一次性切分；n 由 work 文件唯一确定。

---

## §3 Regime Gate（继承 P1-06，仅分层不作触发过滤）

bull=前一完整 UTC 日收盘>日线 SMA200；bear=≤；unknown=预热不足单独标注；无前视。子样本仅辅助解释，正式通过不允许事后剔除 regime 达成。

---

## §4 检验设计 + 依赖稳健主推断（RR3 #2 闭合）

**观测单位：** 每 work episode 一条，池化。
**CAR（冻结）：** 1H MARK close 对数收益，事件前基准 `[event_time-72h, event_time-1h]`：
```text
baseline_mu_i = mean(log(close_tau/close_{tau-1h})) over hourly returns ending in [event_time-72h, event_time-1h]
raw_return_i,h = log(close_{align+h}/close_{align})          （align=§2 入场对齐 bar）
CAR_i,h = raw_return_i,h - h*baseline_mu_i
```
**Horizon 角色：** 主=**48h（唯一）**；次=24h（Holm family）；72h=仅探索，p 值不改判决。

**主推断：circular moving-block bootstrap（时间轴，全冻结，RR3 #2）：**
- 把 work episodes 按 event_time 升序成时间序列；**时间轴=半开 UTC 小时网格 `[t_1, t_n+1h)`，周长 `span=(t_n - t_1)+1h`**（端点不重复，`t_1` 与 `t_n` 为环上不同点，RR4 #2 修正）。
- **块宽 W=144h**（6 天，> `72h baseline + 2h 对齐 lag + 48h outcome` 共享数据足迹，含缓冲）。
- 每个 bootstrap 复制：重复抽块直到累计 episode 数 ≥ n——
  - 抽块：从半开区间 `[t_1, t_n+1h)` **均匀抽随机起点 u**；定义每 episode 的 **circular offset `off_i(u)=((event_time_i - u) mod span)`**（mod 取非负，把时间轴视为周长 span 的环）；块=`off_i(u) ∈ [0, W)` 的全部 episodes。
  - **空块**（窗口内无 episode）跳过、重抽，不计入。
- 累计达到 ≥ n 后，对**最后一块**按**块内 circular offset `off_i(u)` 升序**截断多余 episode（按距随机起点 u 的环上距离，非绝对 event_time，保证顺序从 u 出发，RR4 #2 修正），使每个复制恰好 n 条。episode **等权**。
- 统计量=均值。**零假设重心化（H0: mean=0）**：对每个复制均值减去观测样本均值得居中分布。
- 单侧 p = `(#{居中复制均值 ≥ 观测均值} + 1) / (B + 1)`。**basic-bootstrap 95% CI** = `[2*obs_mean - q_{0.975}, 2*obs_mean - q_{0.025}]`，q 为**未居中**复制均值分布分位。
- `B=10000`，`seed=20260615`。普通 t-test 仅描述性，不入判决。
- 24h 次检验同法、同 seed，Holm 校正。

**确认性检验 family（Holm，m=4，全文一致）：** {48h 主 CAR、24h 次 CAR、§5 单调性、§7 non-overlap 48h CAR}。72h 不入 family。无其他确认性检验。

---

## §5 辅检验：OI 收缩幅度单调性（RR3 #2 Spearman 零假设冻结）

档：Severe `[0,0.0033]`/Medium `(0.0033,0.0067]`/Mild `(0.0067,0.01]`（禁全样本重切）。severity 编码 Severe=2/Medium=1/Mild=0。
**统计量：** severity 序 vs 48h CAR 的 **Spearman 秩相关**（midrank ties），预期符号为正，单侧。
**`H0: ρ=0` 检验（冻结，配对 moving-block bootstrap 居中，RR4 #2 修正）：** 因减 CAR 均值不改秩（RR3）、有放回抽块亦非真置换（RR4），改用对 **`(severity_i, CAR_48h_i)` 配对序列**做 §4 同口径 W=144h circular moving-block bootstrap：每个复制重抽配对块计算 `ρ*`，`B=10000`、`seed=20260615`；以 **`ρ* - ρ_obs`** 构造 `H0: ρ=0` 居中分布，单侧 p=`(#{ρ* - ρ_obs ≥ ρ_obs}+1)/(B+1)`（等价 `(#{ρ* ≥ 2ρ_obs}+1)/(B+1)`）。该法保持时间依赖且检验 ρ=0。计入 §4 family。

---

## §6 功效（报告型诊断，DEC-075 治理闭合，RR3 #3）

**治理定性（DEC-075）：** 本研究**不耗独立计数**（机制前关联快筛），故 Protocol v1.4 §六"耗独立计数实验须预设 MDE 硬门高于合理效应上限"**不强制约束**之；以 **Protocol 增补件 `RESEARCH_PROTOCOL_v1.4_A1SCREEN_ADDENDUM.md` 留痕**（不私自废止上位规则）。功效=**预登记报告型诊断**，不门控立项。

**诊断口径（冻结，仅事件前数据）：**
- `s_i^2` = episode i 事件前 `[-72h,-1h]` 1H 对数收益方差。
- `sigma_pre_h = sqrt(h * median_i(s_i^2))`（h 小时聚合，独立同分布近似；明确为保守诊断非真实自相关方差）。
- `m_bar` = `n / (含≥1 episode 的 UTC 日历日数)`（设计效应用 cluster=UTC 日）。
- `n_eff_h = n / [1 + (m_bar - 1) * ICC]`，设计效应**只在 n_eff 计一次**；ICC 冻结情景 `{0, 0.2, 0.5}`，判读参照 0.5。
- 报告 80%-power MDE：`(z_{0.95}+z_{0.80}) * sigma_pre_h / sqrt(n_eff_h)`，三档 ICC。non-overlap 诊断用其子样本自身 n 与同口径 sigma_pre。
- **不设硬停机句**；功效仅供事后解读灵敏度。是否值得执行由 CTO 在放行时人工裁量（已由 DEC-075 授权路径A 快筛）。

---

## §7 A-2 碰撞门（A-2 原冻结口径，RR3 #4 已认可，仅统一 family）

**a2_overlap（冻结，A-2 v1 原口径）：** 取 event_time **之前最近一个已结算的单次 8H funding 读数**，相对其**此前 365 天（最少 180 天，midrank）**滚动分布求分位，正极端 **P95**；`>=0.95` 标 `a2_overlap=1`。不用 24h 均值、不另选阈值。

**判决（纳入 §4 family，Holm m=4 第 4 项）：**
1. 报告 `p_overlap`、overlap/non-overlap 子样本 48h CAR（moving-block bootstrap）。
2. **A-2 非重叠关联硬门：** non-overlap 子样本 48h CAR family Holm 后显著为正（family 第 4 项）。**注（RR4 #1）：** 本项仅证明 A-1 关联**不完全由 A-2 正极端 funding 重叠承载**，**不识别独立机制**（关联层，不含机制识别含义）。
3. 删除 0.60 与 OR 句。non-overlap 若经 §6 诊断灵敏度过低，报告标注"non-overlap 功效不足"，但**仍按 family 实际显著性判 PASS/FAIL**（不显著即该项 FAIL，不以功效不足豁免）。
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

## §9 验收：两级门（Tier A=关联门，RR3 #1 去 overclaim）

**Tier A 可观测条件回弹【关联】门（本 v4 判定）：** gross CAR 关联门，过=**"可观测条件回弹关联成立（探索级）"**，**不等于机制成立、不等于策略晋级、不等于满足 Protocol 第五件、不耗独立计数**。
**Tier B 交易策略门（另案预登记）：** Tier A 过后另立，冻结入场/持仓/杠杆/funding/退出/重叠/资本占用后，检验**净收益**四件套、爆仓、几何增长、1.00% 压力、Protocol 第五件（net）。v4 不对 Tier B 下结论。
**机制确证（路径B）：** 强平机制成立仅能由路径B（前向真实强平数据）声称，见 §13。

---

## §10 被动基准（诊断，非 Tier A 硬门）

A-1 48h gross CAR>0 的现金零（不持仓=0）由 §4 主检验表达。同 regime 同品种被动 buy-and-hold mean CAR **仅作诊断**报告，不作 Tier A 硬门。Protocol v1.4 第五件（net>现金零）归 Tier B，v4 不冒称已满足。

---

## §11 唯一闭合 Decision Table（RR3 #4/#5）

**所有"CAR>0"=§4 moving-block bootstrap 单侧 Holm（family m=4）后显著（点估计>0 且依赖稳健显著）。** family={48h, 24h, 单调性, non-overlap}。

**Tier A PASS（全满足）：**
- [ ] 48h CAR：family Holm 后显著（主项）。
- [ ] 单调性：Spearman 正、§5 配对 bootstrap 检验 family Holm 后显著。
- [ ] A-2 非重叠关联：non-overlap 48h CAR family Holm 后显著为正。
- [ ] WF 稳定性（**裸均值，冻结切分，RR4 #3**）：work episodes 按 event_time 升序分三段，**段长 = `⌈n/3⌉, ⌈(n-⌈n/3⌉)/2⌉, 余下`（余数全部分给第一段，其次第二段）**；**切点 `c_k` = 相邻两 episode event_time 的算术中点**（k=1,2）；每个 episode 的实际数据足迹 = `[event_time-72h, align+48h]`（baseline 起点到 outcome 终点，含对齐 lag）；**purge** 足迹跨越任一 `c_k` 的边界 episode（从其原所在段剔除，**purge 后不重新分段、不重新等分**）；3 段各自 48h mean CAR（裸均值）**≥2 段 > 0**。
- [ ] 未发现任何 Holdout 读取/全样本分位/触发或 episode 规则重设/cutoff 后行情补齐。

**Tier A FAIL（任一即 FAILED）：** 48h CAR family Holm 后不显著｜单调性不显著或符号为负｜non-overlap 48h CAR family Holm 后不显著｜**WF <2 段 >0**｜发现 Holdout 读取/全样本分位/规则重设/cutoff 后补齐。

**判读纪律：** 主 horizon 唯一=48h，禁 24h/48h 事后择优；72h 仅探索不入判定；任一必要项 N.A.→整体 FAIL；不显著正点估计只写"未拒绝 H0/未验证"，**且不得写"机制"二字**。

---

## §12 Holdout 物理封存（加密真权限边界，RR3 #5）

1. **保管进程**（独立脚本，主会话身份运行，非 Codex 执行身份）一次性生成全部 pooled episodes，按 `(event_time_utc, symbol)` 排序 deterministic 每第 5 个预留 sealed，其余 work。
2. **真权限边界=认证加密（RR4 #4 冻结）：** `work_episodes.csv` 明文写入 `06_RESEARCH/DATA/A1_WORK/`（执行身份可读）；`sealed_holdout_episodes.csv` 以 **AES-256-GCM**（认证加密）加密为 `sealed_holdout.enc`——**格式冻结**：文件 = `12B 随机 nonce ‖ 密文 ‖ 16B GCM tag`；解密须 GCM tag 认证通过，**tag 认证失败即判读取失败**（杜绝 ECB/CBC 等无认证实现分叉）。**密钥仅主会话持有**：存于执行身份（Codex workspace-write）**不可访问的独立位置**（主会话 secret / 独立 OS principal / ACL 限定目录），**绝不**落入 Codex 可读文件、环境变量、命令行参数或日志。执行身份即便读到密文，无密钥且无法通过 GCM 认证，**物理不可解密**（解决 RR3/RR4 指出的"移出 workspace≠不可读"）。
3. `A1_HOLDOUT_MANIFEST.json`（落 work 侧可见）：work/sealed 各行数、schema、生成代码 git hash、明文与密文 SHA-256、生成时间、保管人=主会话、解封条件（Tier A 通过+Founder 批）、一次性使用记录。
4. **负向权限测试（冻结，须留痕，RR4 #4）：** 放行执行前，在**正式执行身份（Codex workspace-write）**下运行一次测试并记录入 `A1_HOLDOUT_PERMTEST.log`：(a) 读 `A1_HOLDOUT_MANIFEST.json` **成功**（记命令+退出码 0）；(b) 尝试解密 `sealed_holdout.enc` **失败**——记录所执行命令、非零退出码、以及失败原因证据（"密钥文件不可访问/读取被拒" 或 "GCM tag 认证失败"）。两条均留痕方可放行。
5. 路径 assert 拒绝任何 sealed/holdout 路径（误操作二重保险）。有效 n 仅由 work 文件计算。违反即纪律违规、研究作废。A-2 holdout（218 条）完全独立禁读。

---

## §13 失败后禁止行为 + 路径B（锁死）

Tier A FAILED 后禁止：改 OI 阈值/方向规则/episode 规则/分位窗口后重测；排除年份/品种/regime/funding 后重测；72h 或 24h 单独显著改写为通过；全样本分位；cutoff 后补 horizon；读 Holdout"确认"失败；**任何"机制成立"改写**。

**路径B（DEC-075，并行）：** 无论 Tier A 通过与否，强平机制的确证走 `A1_FORWARD_LIQUIDATION_PATH.md`：用 2026-06-13 起采集器真实清算名义额做方向识别，累积 3-6 月后另立新预登记重新盲审；该路径才允许声称强平机制并耗独立计数。Tier A 平→直接毙历史 A-1 并据此决定是否仍投路径B；Tier A 正→关联存在，强化投路径B 确证机制的价值。

本 v4 锁定后，对触发/方向规则/成本/分层/horizon/验收/Holdout 的任何修改均视为新假设，不得在 v4 名义下继续。
