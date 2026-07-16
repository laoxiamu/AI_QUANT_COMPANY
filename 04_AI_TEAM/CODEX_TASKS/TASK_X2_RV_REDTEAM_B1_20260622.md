# Codex 任务书 —— #X2 跨链相对价值：方向红队 + B1-KILLCARD 三门

**任务 ID：** P1-RES-037-B1 ｜ **派发：** Claude（主理人）2026-06-22
**上位卡：** `06_RESEARCH/PREREGISTRATIONS/CROSS_ASSET_RV_B0_MECHANISM_CARD.md`（B0 判 PROCEED，默认 KILL 基线）
**依据：** DEC-082（拆 B0-B4 单变量序列）/ DEC-084（非资金费，合规）/ DEC-063（目标函数）/ DEC-061（自实现可审计、禁虚构文献号）
**铁律：** 读项目根 `AGENTS.md`，遵守 Protocol；默认 KILL 基线，任一门不过即 KILL，**禁止加配对数/改 z 阈值/改持有窗续命**（防局部修补，风险D）。

---

## 阶段 0：方向红队（先做，未过不进 B1）

对 B0 卡机制提出最强反驳，逐条给证据或推理，不要附和：

1. **payer 是否太软、已被竞争吃掉。** B0 卡自承 payer=行为拥挤（过度反应），比"强制清算流"软。质疑：crypto 主流币配对的均值回复 edge 是否早被做市/套利机器人压平到 0？给出你对"残余 edge 是否还够覆盖两腿成本"的判断。
2. **crypto 协整稳定性。** 股票配对交易依赖协整；crypto 叙事轮动/脱钩频繁，协整关系是否足够稳到可交易？脱钩→价差趋势化、两腿齐亏的尾部有多胖？
3. **两腿成本是否是结构性死刑。** 进出各两腿=4 次成交，taker ~0.8% 来回；均值回复高换手。给出"合理价差回归幅度上限 vs 4 腿全成本"的量级对比——若回归幅度的现实上限 < 成本，本线在 B1 前就该 KILL。

**阶段 0 产出：** PROCEED / REVISE_ONCE / KILL 三选一 + 理由。判 KILL 则停，不跑 B1，直接写报告。

---

## 阶段 1：B1-KILLCARD 三门（仅当阶段 0 非 KILL）

数据：Binance 免费全量 K 线，127 parquet（已在 `06_RESEARCH/DATA/`，核实路径）。**不碰 Holdout、不调参、不耗独立计数。** 一律自实现可审计小函数，禁不可审计黑箱。

- **门1 两腿成本门（第一杀手）：** 4 腿全成本 break-even 分析；含 maker↔taker 敏感带 + 逆向选择折扣（挂单专挑你错时成交，禁理想成交假设）。扣成本后净回归 ≤ 0 或回归幅度上限 < 成本 → KILL。
- **门2 协整稳定门：** 样本外协整/相关稳定性；**必须建模脱钩→价差趋势化两腿齐亏的尾部**，不得假设总回归。脱钩频率高到吃掉回归收益 → KILL。
- **门3 防过拟合门：** 配对须先验/机制驱动选取（同生态/同 beta），**禁全配对扫到最好**；z 阈值、持有窗预登记冻结，禁三处同时搜。
- **被动基准对照：** 扣成本后净收益须超同期市场中性被动基准，否则不成立。

任一门不过 → KILL，回墓园，建议取 #X3 横截面动量或其他候选。

---

## 文献核实（DEC-061 强制）

B0 卡引用 `2602.23762`（跨链负溢出）标注**待核实**。引用前必须先核实该 arXiv 号真实存在且内容相符；**核实不到即不引用、不要编造替代号**，在报告中标"未找到对应文献"。

---

## 产出与回写

1. 报告写 `04_AI_TEAM/CODEX_TASKS/REPORT_X2_RV_REDTEAM_B1_20260622.md`，含：阶段0裁决、三门各自结论与关键数字、文献核实结果、最终 PROCEED-to-B2 / KILL 裁决 + 理由。
2. 末步写 TASK_INBOX：
```python
import json, datetime, pathlib
inbox = pathlib.Path("04_AI_TEAM/TASK_INBOX"); inbox.mkdir(exist_ok=True)
done = {
  "task_id": "P1-RES-037-B1",
  "completed_at": datetime.datetime.utcnow().isoformat()+"Z",
  "status": "completed",  # completed/blocked/failed
  "output_file": "04_AI_TEAM/CODEX_TASKS/REPORT_X2_RV_REDTEAM_B1_20260622.md",
  "next_task": None,
  "notes": "<阶段0裁决 + 三门是否全过 + 最终裁决一句话>"
}
(inbox / "P1-RES-037-B1_DONE.json").write_text(json.dumps(done, ensure_ascii=False, indent=2))
```

**诚实基线（Claude 预判）：** 免费数据 + 两腿成本，本线很可能死在门1成本门或门2协整门——这是预期内的高信息结果（廉价、不耗计数、死得快）。不要为了"活下来"放松成本/协整假设。若你判 PROCEED，必须给出 edge 量级 > 4 腿成本的硬证据。
