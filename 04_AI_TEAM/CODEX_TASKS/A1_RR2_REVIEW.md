# A1-RR2：A-1 预登记 v2 第二轮独立风险审查（盲审）

**任务类型：** 文档审查 + 专业评估（独立 Risk Reviewer，与 thesis owner 分离）
**审查对象：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v2.md`
**对照基线：** 你（或前序 Reviewer）在 `06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v1.md` 给出的 NOT APPROVED 与十项最低条件。
**输出：** `06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v2.md`
**角色：** 你是独立 Risk Reviewer，不是策略设计者。你不知道实验结果（实验未跑），只审查设计是否满足物理盲审放行条件。

---

## 审查任务

A-1 预登记 v1 被判 NOT APPROVED，列出十项最低条件。起草者（Claude/CTO）已产出 v2。
你的任务：判断 v2 是否**真正闭合**了这十项条件，而非表面措辞修补。

### 第一部分：十项条件逐条裁决（核心）

对 `A1_RISK_REVIEW_v1.md` 最终结论中的 10 项最低条件，逐条给出：
`CLOSED / PARTIALLY_CLOSED / NOT_CLOSED` + 证据（引 v2 具体 §/行）+ 若未闭合，仍缺什么。

特别严格审查以下高风险点（v1 评为 C/D 的维度）：
1. **方向识别（v1 维度1, D 级隐患）**：v2 用"6h 并发负价格冲击 `r6h<=-2%`"作强制卖压方向代理。判断：(a) 该代理是否在看事件后收益前冻结？(b) 是否仍存在未排除的混淆（如宏观普跌中段、价格下行但实为空头主导减仓）？(c) v2 把因果命题降格为"proxy 识别"是否足够诚实、措辞是否仍有 overclaim 残留？(d) `DIR_THRESHOLD=-2%` 这个具体值是否本身构成一个未论证的研究者自由度（为何 -2% 而非 -1%/-3%）？这是新引入的自由度，必须评估。
2. **多重检验/依赖（v1 维度3, D）**：v2 设唯一主 horizon=48h + 24h Holm + 72h 仅探索 + global-event-cluster 块 bootstrap。判断：cluster 定义（同 UTC 日跨品种）是否足够吸收依赖？确认性检验预算=3 是否真的封闭，§5 单调性与 §7 碰撞是否仍有隐藏的多重比较？
3. **功效（v1 维度3/4, D）**：v2 改 80% power + n_eff（设计效应折算，ICC_proxy=0.3 保守）+ 保守方差，撤销 1.5–3.0% 硬门。判断：n_eff 折算与 ICC_proxy=0.3 是否有依据、是否可能仍乐观？停机条件是否可操作？
4. **A-2 碰撞（v1 维度5, C）**：v2 用 a2_overlap := 事前 funding 滚动分位 ≥0.95（A-2 冻结 P95）+ 交互项 + "机制不可区分"判决（overlap≥0.60 或 non-overlap 欠功效）。判断：是否真正用了 A-2 冻结阈值而非另选？overlap≥0.60 阈值本身是否又是一个新自由度？
5. **验收闭合（v1 维度6, D）**：v2 §11 decision table 是否唯一二元、无 OR 择优、N.A.→FAIL？是否仍有 §9/§10/§11 之间的口径冲突？
6. **现金零基准（v1 §7 协议冲突）**：v2 §10 主理人裁决"以 Protocol v1.4 现金零基准为硬门，被动 buy-and-hold 降诊断"。判断：该裁决是否与 Protocol v1.4 实际条款一致？（读 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` 核对事件类第五件口径）。
7. **Holdout 物理封存（v1 维度4, B）**：v2 §12 保管方一次性切分+SHA-256+一次性使用记录+路径拒绝是否构成可执行的封存流程（而非又一个逻辑切分）？

### 第二部分：是否引入新缺陷

v2 为闭合旧条件引入了新结构（方向代理过滤、refractory window、cluster bootstrap、两级门、n_eff 折算）。逐一判断这些新结构是否**自身**引入新的 HARKing 路径或方法缺陷。

### 第三部分：最终结论

`APPROVED（可放行执行 Tier A 事件研究）` / `NOT APPROVED（仍需修改，列出第二轮必改清单）`。
若 APPROVED，明确"放行执行 Tier A"的前提与边界。若 NOT APPROVED，给出**最小**第二轮必改清单（避免无限加码）。

---

## 输出格式（`A1_RISK_REVIEW_v2.md`）

```markdown
# A-1 预登记 v2 独立风险审查报告（第二轮）
**审查者：** Codex（独立 Risk Reviewer）｜**日期：** 2026-06-14｜**对象：** A1_CASCADE_REBOUND_PREREG_v2.md
**结论：** APPROVED / NOT APPROVED

## 执行摘要（3 行）

## 十项条件闭合裁决表
| # | 条件 | CLOSED/PARTIAL/NOT | 证据(§/行) | 仍缺 |

## 高风险点专项（方向代理/多重检验/功效/碰撞/验收/现金基准/Holdout）

## v2 新引入结构的缺陷评估

## 最终结论 + （若 NOT APPROVED）最小第二轮必改清单
```

---

## 重要约束（铁律）
- **禁止**读取任何 HOLDOUT（`06_RESEARCH/DATA/HOLDOUT/`、任何含 `holdout`/`sealed` 路径）。
- **禁止**读取 `01_MEMORY_CORE/` 下任何文件。
- **禁止**修改预登记文档本身（你是审查者）。
- **禁止**提前执行任何事件研究代码 / 计算事件后收益。
- 允许读取：`A1_CASCADE_REBOUND_PREREG_v2.md`、`A1_RISK_REVIEW_v1.md`、`A1_CASCADE_REBOUND_PREREG_v1.md`、`RESEARCH_PROTOCOL_v1.3_ADDENDUM.md`、A-2 公开假设/特征代码（不含 holdout）。
- 七问前置已由 Claude 完成；你专注盲审。
- 完成后写 `04_AI_TEAM/TASK_INBOX/A1_RR2_DONE.json`：

```python
import json, datetime, pathlib
inbox = pathlib.Path("04_AI_TEAM/TASK_INBOX"); inbox.mkdir(exist_ok=True)
(inbox / "A1_RR2_DONE.json").write_text(json.dumps({
  "task_id": "A1_RR2",
  "completed_at": datetime.datetime.utcnow().isoformat()+"Z",
  "status": "completed",
  "output_file": "06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v2.md",
  "review_conclusion": "APPROVED / NOT APPROVED",
  "conditions_closed": "x/10",
  "notes": "最重要发现"
}, ensure_ascii=False, indent=2))
```
