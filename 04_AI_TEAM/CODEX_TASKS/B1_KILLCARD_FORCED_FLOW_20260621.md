# Codex 任务：B1-KILLCARD 强制/激进流 数据-功效门（含 Founder maker 挂单变量）

**ID：** P1-RES-036-B1 ｜ **类型：** 数据/功效审计（可读数据、算成本/功效；**不碰 Holdout、不耗失败计数、不调参做 alpha**）。
**目标：** 尽快"杀死不可交易路径"，不是选最顺眼子机制。任一门不过=回墓园/休眠，不进 B2。
**上位：** DEC-085（方向）、B0 卡 §5（REVISE_ONCE+四门）、Codex 红队报告、DEC-086（治理边界）。

## 必读
1. `06_RESEARCH/PREREGISTRATIONS/FORCED_FLOW_ORDERFLOW_B0_MECHANISM_CARD.md`（§5 四门）。
2. `04_AI_TEAM/CODEX_TASKS/REPORT_REDTEAM_FORCED_FLOW_20260621.md`（你自己的红队结论）。
3. `06_RESEARCH/RESEARCH_PROTOCOL_v1.4_A1SCREEN_ADDENDUM.md`（功效/成本档/第五件）。
4. `06_RESEARCH/GRAVEYARD_INDEX.md`（A-1 条）。

## 四道门（逐门给 PASS/KILL + 依据；含 Founder 新变量）

### 门1：成本可交易门（含 maker↔taker 敏感带，Founder 输入）
- 对每个候选子机制给"全成本 break-even drift"。
- **Founder 变量**：成本不要只算最坏 taker。给一整条带：
  - 最坏：taker 进 + taker 出（≈0.04-0.05%/边×2 + 滑点）。
  - 最好：maker 限价进 + maker 限价出（≈0.02%/边，挂单零滑点）。
  - **但 maker 必须扣"成交概率 + 逆向选择"折扣**：挂单偏向你错时成交，禁理想成交假设；给出在合理成交率/逆选下的有效成本，而非名义 maker 费。
- 判据：若"合理毛效应上限 > 有效全成本（含 maker 最好情形+逆选折扣）"都不成立 → 该子机制 KILL。

### 门2：数据完整门
- 清算流：证 Binance 免费 forceOrder 缺失是否可界定（极端窗系统性缺失？）；不能界定→清算路径只可数据积累不可确证。
- 订单流：证 aggTrades taker 方向字段一致性 + L2 book 连续重建（snapshot/updateId 连续/gap repair/到达时间≠撮合时间）。不可靠→KILL。

### 门3：反 A-1 门（清算路径）
- 看任何收益前**冻结单一方向命题**（清算延续 或 清算后耗尽，二选一预登记），禁两头测择优。
- 证与 A-1（OI proxy 48h 回弹，FAILED）的真实区分；不能区分=换皮 KILL。

### 门4：反 Sweep 白名单门
- 入组/方向/分层只许用流变量（清算 notional、signed taker volume、OFI/MLOFI、深度不平衡、spread、RV/OI 控制）。
- **任何价格形态（支撑阻力/突破回踩/插针/sweep/结构位/均线/在某价位挂单赌反转）入组=Sweep 复活 KILL。** 价格只作结果/成本/基准变量。Founder 的"挂单价位"必须由流变量定位，不由图上点位。

## 子机制处理（红队定）
- **OFI 先过门1**：分钟级、非共置、扣有效成本后毛效应上限是否>0。过不了直接判 `OFI KILL_AS_TRADABLE`。
- **清算流**：免费数据下只做门2/门3 readiness，不进 B2；需付费全量源或 3-6 月前向采集。
- **第三候选 lead-lag（现货-永续激进流）**：若 OFI/清算都悬，评估它过门1/门2 的可行性（限秒-分钟非共置、全成本、反延迟竞速）。

## 交付
- 报告 `04_AI_TEAM/CODEX_TASKS/REPORT_B1_KILLCARD_FORCED_FLOW_20260621.md`：四门逐门结论 + 每个子机制 PASS/KILL + 总建议（进 B2 哪个 / 全 KILL 回 #X2 / 取 lead-lag）。
- 写 TASK_INBOX DONE.json。
- **边界**：可读公开数据/历史样本算成本与功效；不碰 Holdout、不改 Claude 独占权威文件、不下单、不耗失败计数。诚实基线=默认 KILL，过门才放行。
