# A-1 强制流两相位 / 清算级联后回弹预登记 v1

**任务号：** D3  
**状态：** PREREGISTERED DRAFT - 供 Risk Reviewer 物理盲审  
**起草日期：** 2026-06-14  
**研究对象：** A-1 cascade rebound conditional alpha candidate  
**禁止动作：** 本预登记完成前不得运行 A-1 事件研究，不得读取任何 HOLDOUT 目录或文件，不得据结果修改触发、分层、成本或验收口径。

**依据文件：**
- `06_RESEARCH/RESULTS/20260612_a1_mde_precheck.md`
- `06_RESEARCH/RESULTS/20260613_a1_vs_a2_mechanism_diff.md`
- `06_RESEARCH/RESULTS/20260613_a1_framework_report.md`
- `06_RESEARCH/CODE/a1_event_study_framework.py`
- `01_MEMORY_CORE/CURRENT_STATE.md`
- `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`

**Protocol v1.4 AI 证据三行：**
1. 本假设不是由 LLM 作为 alpha 信号生成；它来自项目当前机会地图与 Claude 对强制流机制的人工归纳，Codex 本次只起草预登记。
2. 最可能错处：OI 骤降可能不是清算结束后的过度卖出，而是持续去杠杆或宏观熊市下跌的中段信号，导致事件后没有正 CAR。
3. 本预登记不以多 agent 共识作为证据；A-2 碰撞门仅作为机制隔离与风险审查材料。

---

## §1 机制假设

A-1 检验的是已经发生的机械性强制事件之后是否存在短周期价格回归，而不是预测强制事件何时发生。

冻结因果链如下：

```text
强制平仓 / 清算级联已经发生
    -> 6h OI 极端骤降
    -> 机械平仓订单在短时间内冲击市场
    -> 临时超额供给形成
    -> 价格相对短期均衡 overshooting
    -> 主动买方回归或被动卖压消失
    -> 24h / 48h / 72h 均值回归，表现为正向 CAR
```

核心可证伪命题：在清算级联代理事件发生后，事件后 24h 或 48h 的平均 CAR 显著大于 0，且该超额不能仅由同 regime 的被动 beta 暴露解释。

本研究不检验、也不声称可以预测清算级联何时发生；触发只在 OI 骤降已经被观测到后生效。

## §2 触发定义（冻结，不可修改）

触发条件冻结如下，正式检验不得修改：

- **信号：** 6h OI 骤降，`d6h_rolling_pctl <= 0.01`。
- **滚动分位口径：** 365 天滚动窗口，最少 180 天，midrank；只使用事件时点之前历史样本，禁止全样本分位。
- **品种：** `BTCUSDT`, `ETHUSDT`, `SOLUSDT`，池化检验。
- **截止：** `ts < 2024-12-10T00:00:00Z`。
- **Episode 合并：** 同品种触发按时间排序，距上一触发 `<= 24h` 归为同一 episode。
- **工作集：** 池化 203 个 episodes；按第 5 个 episode 预留 Holdout `floor(203 / 5) = 40` 个；正式工作集 `n = 163`。

价格与 funding 对齐约束：

- 任何 baseline、事件后 horizon、funding 分层或被动基准计算均不得读取 `2024-12-10T00:00:00Z` 及之后数据。
- 若某 episode 在某 horizon 上没有完整的事件前 baseline 或事件后 endpoint，则该 episode 仅在该 horizon 的检验中剔除，不得替换 horizon 或补读 cutoff 后行情。

## §3 Regime Gate

A-1 继承 P1-06 验收口径中的高周期牛熊状态定义，用于分层与第五件基准对照，不作为新增触发过滤器。

冻结 regime 定义：

- **宏观牛市（bull）：** 该品种前一完整 UTC 日收盘价 `>` 该品种日线 SMA200。
- **宏观熊市（bear）：** 该品种前一完整 UTC 日收盘价 `<=` 该品种日线 SMA200。
- **unknown：** SMA200 预热不足或日线数据不足；unknown 不强行归为 bear，主检验可保留但 regime 子样本与 regime 基准需单独标注。
- **无前视：** regime 在事件时点只使用已完成 UTC 日数据。

A-1 在熊市 regime 下可能表现为持续去杠杆而非回弹，效应方向和幅度可能与牛市不同。因此，bull / bear / unknown 的子样本结果只作为辅助解释和风险识别；正式通过条件不允许通过事后剔除某一 regime 达成。

## §4 检验设计（主检验 + 辅检验）

### 主检验

**观测单位：** 每个 work-sample episode 一条观测；BTC/ETH/SOL 池化。

**指标：** Cumulative Abnormal Return（CAR），使用 1H MARK close 的对数收益，事件前基准期为 `-72h ~ -1h`。

对 episode `i` 与 horizon `h`：

```text
baseline_mu_i = mean(log(close_tau / close_{tau-1h})) for hourly returns ending in [event_time-72h, event_time-1h]
raw_return_i,h = log(close_{event_time+h} / close_{event_time})
CAR_i,h = raw_return_i,h - h * baseline_mu_i
```

若事件时点无法精确落在 1H bar 上，使用事件时点后第一个可用 1H close 作为 `event_time` 对齐点；该规则必须在全部品种和 horizon 上一致。

**Horizons：** 24h, 48h, 72h。

**统计检验：**

- `H0: mean(CAR_h) <= 0`
- `H1: mean(CAR_h) > 0`
- 单侧 t-test，`alpha = 0.05`
- 24h 与 48h 是主通过 horizon；72h 为延展 horizon 与机制形态观察。

### 辅检验 1：OI 骤降幅度单调性

按 `d6h_rolling_pctl` 固定区间分三档，禁止用工作集全样本重新切分分位数：

- **Severe：** `0 <= d6h_rolling_pctl <= 0.0033`
- **Medium：** `0.0033 < d6h_rolling_pctl <= 0.0067`
- **Mild：** `0.0067 < d6h_rolling_pctl <= 0.0100`

预期方向：OI 骤降越剧烈，回弹幅度越大，即 `CAR_Severe >= CAR_Medium >= CAR_Mild`。若直接用 `d6h_rolling_pctl` 排序，则预期是 CAR 随 percentile 上升而下降；报告必须按 severity 方向呈现，避免符号误读。

### 辅检验 2：A-2 碰撞门分层

将 episode 按事件前 24h funding 状态分为高 funding / 低 funding 两组。

分层口径冻结如下：

- 对每个 episode，计算事件前 `-24h ~ -1h` 的平均 funding rate 或累计 funding cash-flow proxy。
- 将该值相对同品种事件前历史 funding 分布转为滚动历史分位；窗口 365 天、最少 180 天、midrank，只使用事件前数据。
- **High funding：** funding rolling percentile `>= 0.50`。
- **Low funding：** funding rolling percentile `< 0.50`。

分别计算两组 24h / 48h / 72h CAR。预期：无论 funding 高低，CAR 方向均为正，或至少不存在高 funding 子样本显著为负。该检验是本预登记对 A-2 尸检碰撞门的操作化响应。

### 辅检验 3：成本压力档

任务书指定成本网格：

- 0.05%
- 0.10%
- 0.20%

对每个 horizon 报告：

```text
net_CAR_h,cost = CAR_h - round_trip_cost
```

主成本验收：`0.10%` 档下 24h 或 48h 的 mean net CAR 仍为正，且对应 horizon 的单侧 t-test 仍满足 `p < 0.05`。

Protocol v1.3 对事件类策略另有更严格压力档，必须追加报告：

- 基准滑点外，报告 `0.30% / 0.50% / 1.00%` 三档敏感性。
- 事件类通过线：`0.30%` 档四件套仍成立。
- A-1 额外硬约束：`1.00%` 档 `E[R] > 0`。

正式判定以任务书成本门与 Research Protocol v1.3 中更严格者为准；不得只报告 0.05% / 0.10% / 0.20% 后跳过 v1.3 压力档。

## §5 功效段（MDE）

B4 MDE 预检结果作为正式功效段输入，不构成事件研究结果。

功效口径：

- 公式：`MDE_h = z_(1-alpha) * sigma_h / sqrt(n)`
- `alpha = 0.05` 单侧，`z_(0.95) = 1.6448536269514715`
- 正式检验采用 alpha-only 口径，不加入 power 项。
- `n = 163`
- 方差来自 BTC/ETH/SOL 1H MARK close 的无条件 `log(close[t+h] / close[t])`，不按事件条件筛选。

| Horizon | n | MDE alpha-only | 功效门 |
|---:|---:|---:|---|
| 24h | 163 | 0.625% | 通过 |
| 48h | 163 | 0.872% | 通过 |
| 72h | 163 | 1.073% | 通过 |

机制合理效应区间下沿为 1.5%。alpha-only 口径下，24h / 48h / 72h 均低于 1.5%，功效门预判通过。

补充说明：若采用 alpha+beta（80% power）口径，72h MDE 为 `1.622%`，高于 1.5% 下沿；24h 与 48h 仍通过。因此正式通过条件以 24h 或 48h 为主，不把 72h 单独作为必要通过 horizon。

## §6 第五件：被动基准对照

第五件用于防止 A-1 的 CAR 只是同 regime 市场 beta 暴露。

**基准定义：** 在同一品种、同一 P1-06 macro regime 条件下，不使用 OI 信号的被动 buy-and-hold。

计算方式冻结如下：

1. 对每个 A-1 work-sample episode 标注其品种与事件时点的 P1-06 macro regime（bull / bear / unknown）。
2. 在该品种、该 regime、cutoff 前的所有可用 1H 起点中，构造与 A-1 相同 horizon 的被动持有收益。
3. 对被动起点使用与主检验一致的 event-before baseline CAR 公式；起点没有完整 baseline 或 horizon endpoint 时剔除。
4. 分 horizon 报告 A-1 mean CAR 与 matched passive mean CAR。

验收要求：A-1 24h 或 48h 的 mean CAR 必须大于同 horizon、同 regime 条件下的被动基准 mean CAR。若 A-1 CAR 不高于被动基准，则第五件失败，即使主检验 p 值显著也不得判定通过。

## §7 A-2 碰撞门声明

A-2 已失败机制：funding rate 极端高值代表多头拥挤，假设未来会发生多头解仓并导致价格反转下行。失败根因不是单纯 n=91 功效不足，而是 timing 问题：拥挤状态可以持续数天到数周，模型不能给出可交易的解仓时间窗口。

A-1 机制：OI 在 6h 内已经发生极端骤降，代表机械性强制事件已经发生；研究对象是事件后 24h / 48h / 72h 是否存在价格均值回归。这是 magnitude / post-event reversion 问题，不是预测主动多头何时解仓的问题。

两者核心差异：

| 维度 | A-2（已失败） | A-1（本预登记） |
|---|---|---|
| 触发变量 | funding rate level | OI 6h 极端骤降 |
| 时间性质 | 持续状态 | 已发生点事件 |
| 行为来源 | 主动多头是否解仓 | 被动机械强平 / 去杠杆 |
| 主要失败模式 | timing 不可定位 | 级联后继续单边下跌 |
| 本研究响应 | 不复活 A-2 | 用 funding 分层验证机制独立性 |

碰撞门处理方案：§4 辅检验 2 的 funding 分层是本预登记对 A-2 碰撞门的操作化响应。若 high funding 与 low funding 子样本 CAR 方向一致，则 A-2 失败不直接否定 A-1。若 high funding 子样本 CAR 显著为负，则说明 A-1 可能只是 A-2 拥挤状态的延迟失效表现，碰撞门失败。

## §8 Holdout 声明

本研究必须遵守物理盲审与 Holdout 隔离。

- **A-2 Holdout：** `a2_events_holdout.csv`，218 条；与本研究完全独立，本研究不得读取、引用或派生使用。
- **A-1 Holdout：** 从 203 个 A-1 pooled episodes 中按每第 5 个 episode 预留，`floor(203 / 5) = 40` 个。
- **A-1 work sample：** 203 - 40 = 163 个 episodes。
- **隔离方法：** 先按冻结规则生成 episode，再按 pooled episodes 的 deterministic index 每第 5 个预留；pooled index 按 `(event_time_utc, symbol)` 排序后生成。该方法不是按时间前后切分，避免 regime 偏差。
- **禁止动作：** 在 Risk Reviewer 审核通过、Founder 知会、Claude 主会话人工派发之前，任何分析步骤不得读取 A-1 或 A-2 Holdout。

若代码、脚本、notebook 或人工操作中出现 `HOLDOUT` 路径读取，本预登记下的研究作废，必须记录为纪律违规，不得继续解释结果。

## §9 验收标准（明确量化）

本 §9 判定的是 A-1 事件研究是否通过预登记验证，并不等同于完整交易策略晋级。若事件研究通过，后续交易化仍须另行满足 Research Protocol v1.3 四件套、成本、爆仓、几何增长、相关性门槛与第五件。

通过条件（全部满足）：

- [ ] 主检验：24h 或 48h CAR `> 0`，且单侧 t-test `p < 0.05`。
- [ ] 任务书成本门：0.10% 成本档下 24h 或 48h net CAR `> 0`，且对应单侧 t-test `p < 0.05`。
- [ ] Protocol v1.3 事件压力门：0.30% 滑点档下事件策略四件套仍成立；A-1 额外要求 1.00% 档 `E[R] > 0`。
- [ ] 第五件：A-1 24h 或 48h CAR `>` 同品种、同 regime 的被动基准 CAR。
- [ ] A-2 碰撞门：high funding / low funding 子样本 CAR 方向一致，定义为均正，或均不显著为负。
- [ ] WF 稳定性：按 work-sample episode 时间顺序切为 3 段，至少 2 段 24h 或 48h mean CAR `> 0`。该 WF 只作稳定性检验，不用于调参。

失败条件（任一满足即 FAILED）：

- 主检验 24h 与 48h CAR 均不显著：两者单侧 `p >= 0.05`。
- 第五件失败：A-1 24h 与 48h CAR 均 `<=` matched passive benchmark CAR。
- A-2 碰撞门失败：high funding 子样本 24h 或 48h CAR 显著为负。
- Protocol v1.3 成本压力失败：0.30% 档四件套不成立，或 A-1 1.00% 档 `E[R] <= 0`。
- 发现任何 Holdout 读取、全样本分位、触发阈值重设、episode 合并规则重设或 cutoff 后行情读取。

报告要求：

- 必须逐项给出上述 checkbox 的 PASS / FAIL / N.A. 判定。
- 不显著结果不得写成"有一定效果"、"方向正确"或"部分成功"。
- 若只有 72h 显著而 24h / 48h 不显著，本预登记判定为 FAILED，不得改称通过。

## §10 失败后禁止行为（预登记锁死）

若本预登记 FAILED，以下行为禁止：

- 禁止修改 OI 骤降阈值后重测，例如从 P1 改为 P2 或 P5。
- 禁止更换 episode 合并规则后重测，例如把 `<=24h` 改成 12h、48h 或按价格波动合并。
- 禁止排除特定年份、特定品种、特定 regime 或特定 funding 状态后重测。
- 禁止把 72h 单独显著改写为 24h / 48h 机制通过。
- 禁止用全样本分位重算触发、severity 桶或 funding 桶。
- 禁止用 cutoff 后行情补齐 horizon。
- 禁止读取 Holdout 来"确认"失败是否只是样本噪音。

允许行为：

- 若失败原因是功效不足而非方向反证，可等待前向强平采集数据 3-6 个月，以更大 n 重新立项。
- 重新立项必须新写预登记、重新过 Risk Reviewer 物理盲审门，并明确说明与本次 FAILED 的区别。

本预登记锁定后，任何对触发、成本、分层、horizon、验收门或 Holdout 切分的修改均视为新假设，不得在 A-1 v1 名义下继续。
