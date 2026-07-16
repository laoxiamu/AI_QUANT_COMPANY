# Codex 自主任务链：P1 解锁数据管线 + B1-KILLCARD 分析（Claude 离线期间连续推进）

**任务 ID：** P1-RES-039-PIPELINE｜**派发：** Claude（主理人）｜**日期：** 2026-06-22
**背景：** Claude 主会话未来数天无额度离线。本任务链让 Codex 把"喂给 Claude 未来裁决"的数据/分析尽量推完，**结果全部写报告 + TASK_INBOX 等 Claude 回来裁决**。
**上位：** DEC-088（P1=事件×结构资金流）/ DEC-089（funding 触发器边界）/ DEC-090（carry 口径）/ 机制卡 `06_RESEARCH/PREREGISTRATIONS/EVENT_STRUCTURAL_FLOW_B0_MECHANISM_CARD.md`（P1-RES-039-B0）/ RUNBOOK「数据采集/出网通道」。

## 🚧 硬护栏（违反即停，这些是 Claude 回来才做的权威动作）
1. **绝不碰 Holdout**（含 a2 事件级 218 条 sealed）。事件级 Holdout 只可"预切 + 物理封存"，**不得读取/不得用于任何统计**。
2. **不耗独立计数**：只做到 B0/B1-KILLCARD（廉价证伪 + 描述统计）。**绝不进 B2 单变量实验**（B2 耗计数，须预登记→盲审→Founder 知会→Claude 派发，增补件九）。
3. **不下最终 KILL/PROCEED 裁决**（权威语义，DEC-069 不下放）。你只给"带理由的推荐"，Claude 回来裁决。
4. **不花钱**（禁付费数据/API）。只用免费 + 本地。
5. **不调参、不回测寻优、不择优方向**（反 A-1：方向二选一须预登记冻结，两侧都报不择优）。
6. 每步独立写报告 + `TASK_INBOX/{step_id}_DONE.json` 检查点；某步闸门不过就**停在该步并如实报告**，不要往下硬推或换法继续搜（反风险 D）。
7. 联网取数按 RUNBOOK：直连/TUN（代理 env 已由调用层处理），预检 HTTP 4xx=可达；分页+限速，禁热循环。

## 步骤（顺序执行，每步一份报告）

### Step 1 — 面板完整性核对（report: REPORT_P1PIPE_S1_PANEL.md）
核 `06_RESEARCH/DATA/FUTURES_EXPANDED_2026/` 31+ symbol：每个止点是否到 2026-06；缺哪些（已下架/Binance 无合约，如实列）；与旧 `FUTURES_EXPANDED/` 接缝是否连续（无重复/无跳空 bar）。给可用 universe 清单。

### Step 2 — OI/funding 回填到 2026（report: REPORT_P1PIPE_S2_OIFUNDING.md）
免费回填 universe 的 OI + funding 到 2026：优先 Binance Data Vision 月/日压缩包（`data/futures/um/.../metrics`、`fundingRate`），写 checksum/manifest，避免热循环；REST 补近端。写到 `06_RESEARCH/DATA/` 下新目录（不覆盖旧）。报覆盖区间/缺口。失败的源如实标注，不伪造。

### Step 3 — 解锁日历拉取 + overlap 普查（report: REPORT_P1PIPE_S3_UNLOCK.md）
免费拉 post-2025 解锁事件（api.llama.fi 已验证可达 200 / DefiLlama unlocks / Tokenomist 免费页），限 universe symbol，字段尽量含 `symbol, unlockDate, 规模, 流通占比, allocation`。与刷新后价格面板做时间重叠，报：①overlap episode 数 ②≥100? ③≥300 可 60/20/20? ④规模档分布。**只用免费边界，不伪造、不拿文章样本冒充全量。**

### Step 4 — P1 解锁 B1-KILLCARD 分析（**仅当 Step 3 overlap episode ≥ 50 才做**；否则停，报"数据不足，等 Claude 决定补数据方向"）（report: REPORT_P1PIPE_S4_B1KILLCARD.md）
按机制卡 §2/§3 + 增补件四做**描述统计级**证伪（不耗计数、不碰 Holdout，只预切封存）：
- **事件普查**：episode 计数、规模分档；episode<100 用跨币种池化。
- **反 price-in（最大死亡门）**：前窗 `[-7d,0]` vs 后窗 `[0,+1d/+3d/+7d]` 分开报漂移；若前窗已吸收大部分方向漂移→后窗无可交易→建议 KILL。
- **分档单调**：解锁规模/流通占比越大，（向下）漂移是否单调；**方向中立：向下与向上两侧都报，不择优**。
- **成本门**：毛漂移上限 vs 80/120/220bp 硬口径；跨 funding 结算须 ex-funding 拆账（DEC-089/090）。
- **MDE 功效段**：给 n、方差、α=0.05 下 MDE，判 MDE ≤（毛效应上限−全成本）是否成立。
- **事件级 Holdout**：只"预切 + 封存"，写明切法，**不读取**。
- 产出**带理由推荐**：B1 该冻结哪个方向 / 还是判 KILL / 还是数据仍不足——**不下最终裁决**。

## 输出与回写
- 每步报告写 `04_AI_TEAM/CODEX_TASKS/REPORT_P1PIPE_S{n}_*.md` + 复现脚本/JSON。
- 每步回写 `04_AI_TEAM/TASK_INBOX/P1-RES-039-PIPELINE-S{n}_DONE.json`（status / 报告路径 / 一句话结论 / 是否触发下一步闸门）。
- 全链末尾写一份 `REPORT_P1PIPE_SUMMARY.md`：四步结论 + 给 Claude 的"回来后第一步该裁什么"清单。
- 文献核实按 DEC-061（禁引不可审计来源，虚构号标注）。

【Claude离线】结果留档等 Claude 回来裁决；遇硬护栏任一触发即停并报告。
