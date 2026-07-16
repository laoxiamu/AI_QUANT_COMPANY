# Codex 任务书 —— #X3 横截面动量：方向红队 + B1-KILLCARD 三门

**任务 ID：** P1-RES-038-B1 ｜ **派发：** Claude（主理人）2026-06-22
**上位卡：** `06_RESEARCH/PREREGISTRATIONS/CROSS_SECTIONAL_MOMENTUM_B0_MECHANISM_CARD.md`（B0 判 PROCEED，默认 KILL 基线）
**依据：** DEC-082（拆 B0-B4 单变量序列）/ DEC-084（非资金费）/ DEC-063（目标函数）/ DEC-061（自实现可审计、禁虚构文献号）
**铁律：** 读项目根 `AGENTS.md`，遵守 Protocol；默认 KILL 基线，任一门不过即 KILL，**禁止靠改 L 窗/改分位/改再平衡频率到最优续命**（防局部修补，风险D）。

---

## 数据（路径已核实，勿再误指）
- 主数据：`06_RESEARCH/DATA/FUTURES_EXPANDED/*_4H.csv`，**35 个 alt 资产 ×4H OHLCV**，列=`datetime,open,high,low,close,volume`，2020-10 至 2024-12，每个 8885-10738 行。
- ⚠️**不是** `127 parquet`（那是 `08_DATA/carry/spot_1h/` 的 carry 遗产 BTC/ETH 1h，与本线无关）；`06_RESEARCH/DATA/` 根下无 parquet。
- 基准腿：BTC 或自构等权 alt 指数（本数据集无 BTC/ETH，需自取或用等权 alt 组合作市场中性基准）。
- **不碰 Holdout、不调参、不耗独立计数。** 一律自实现可审计小函数。

---

## 阶段 0：方向红队（先做，未过不进 B1）
对 B0 卡机制提出最强反驳，逐条给证据/推理，不附和：
1. **低频能否真把成本压到 top−bottom 幅度以下。** alt 多空两端 ~24 币、单边成本保守 0.15-0.30%。质疑：要把换手成本压到截面动量价差之下，需要多低的再平衡频率？该频率下截面动量信号是否还活（动量衰减 vs 成本）？给出量级。
2. **幸存者偏差是否在伪造 edge。** 35 币是活到 2024-12 仍在样本的（含已下架如 REN）。质疑：截面动量的 top−bottom 有多少来自"我们事后知道哪些币没死"？去偏后还剩多少？
3. **截面动量 vs TSMOM 是否正交。** 质疑：本信号是否只是 TSMOM（时序）的截面投影换皮？给相关性判断。

**阶段 0 产出：** PROCEED / REVISE_ONCE / KILL 三选一 + 理由。判 KILL 则停，不跑 B1。

---

## 阶段 1：B1-KILLCARD 三门（仅当阶段 0 非 KILL）
- **门1 成本门（第一杀手）：** 在能压住换手的最低可行频率（日/周）下，多空两端 4 腿全成本 break-even；含 alt maker↔taker 带 + 逆选折扣 + 换手上限。top−bottom 现实价差上限 < 周期成本 → KILL。
- **门2 截面单调门：** 按过去 L 窗回报分组，未来回报单调性 + top−bottom 显著性（预登记 MDE 功效段）。非单调或不显著 → KILL。
- **门3 幸存者偏差门：** 量化"仅存活样本"对 edge 的贡献；去偏后 edge 消失 → KILL。L 窗/分位/频率须先验冻结，**禁三处同时搜到最优**。
- **被动基准对照：** 扣成本后 top−bottom 净收益须超等权 alt 被动基准，否则不成立。

任一门不过 → KILL，回墓园，并在报告标注**议程升级条款已触发**（免费价格软-payer 家族连灭同一成本门 → 建议停循环免费价格线、转 DEC-085 机械流等数据攒够）。

---

## 产出与回写
1. 报告 `04_AI_TEAM/CODEX_TASKS/REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md`：阶段0裁决、三门各自结论与关键数字、最终 PROCEED-to-B2 / KILL 裁决 + 理由；KILL 则标注议程升级条款是否触发。
2. 结果摘要 `06_RESEARCH/RESULTS/X3_MOMENTUM_REDTEAM_B1_20260622.md`；复现脚本 `06_RESEARCH/CODE/x3_momentum_redteam_b1_audit.py`。
3. 末步写 TASK_INBOX：
```python
import json, datetime, pathlib
inbox = pathlib.Path("04_AI_TEAM/TASK_INBOX"); inbox.mkdir(exist_ok=True)
done = {
  "task_id": "P1-RES-038-B1",
  "completed_at": datetime.datetime.utcnow().isoformat()+"Z",
  "status": "completed",
  "output_file": "04_AI_TEAM/CODEX_TASKS/REPORT_X3_MOMENTUM_REDTEAM_B1_20260622.md",
  "next_task": None,
  "notes": "<阶段0裁决 + 三门是否全过 + 最终裁决一句话>"
}
(inbox / "P1-RES-038-B1_DONE.json").write_text(json.dumps(done, ensure_ascii=False, indent=2))
```

**诚实基线（Claude 预判）：** 横截面动量是 crypto 最强免费因子之一、payer 比 #X2 硬，但 alt 高换手成本是真实威胁。若日/周低频能把成本压住、且去幸存者偏差后截面单调仍显著超基准，则 PROCEED；否则诚实 KILL，不靠调 L 窗/分位/频率续命。判 PROCEED 必须给 top−bottom 净幅度 > 周期全成本的硬证据。
