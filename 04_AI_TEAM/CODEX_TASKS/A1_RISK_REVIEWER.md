# A1-RR：A-1 预登记独立风险审查（Risk Reviewer 盲审）

**任务类型：** 文档审查 + 专业评估  
**依赖：** D3 完成（`06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v1.md` 存在）  
**输出：** `06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v1.md`  
**优先级：** 高，与 D2 并行  
**执行者角色：** 独立风险审查员（Risk Reviewer），不是策略设计者

---

## 角色说明

你扮演的是项目**独立 Risk Reviewer**，与策略设计者（Claude/Codex）完全分离。  
你的任务：**在实验执行前**，从风险管理和方法论角度审查预登记文档的质量，判断它是否满足物理盲审门的要求。  
**你不知道实验结果**（实验还没跑），你只审查设计。

---

## 审查对象

文件：`06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v1.md`

---

## 必须覆盖的七个审查维度

### 维度 1：机制假设可信度
- 因果链是否完整且可信？（强制平仓 → 超额供给 → overshooting → 回归）
- 假设在理论上是否有支撑？是否有已知反例或竞争机制？
- 机制是否与 A-2 的原理清晰区分（A-2=funding 拥挤，A-1=强制清算）？

### 维度 2：触发定义的可操作性与封闭性
- 触发条件是否完全参数化（无模糊量）？
- 6h OI 骤降 + 分位 ≤ 0.01 的定义是否可被独立复现？
- Episode 合并规则（≤24h 归并）是否合理，有无操纵弹性？

### 维度 3：检验设计的统计严格性
- 主检验（CAR 单侧 t-test）是否合理？
- n=163 是否满足功效要求（对照 B4 结论，MDE vs 预期效应量）？
- 三个辅检验是否独立于主检验，还是内嵌的 HARKing 机会？
- 多重检验问题：三个 horizon（24/48/72h）是否需要 Bonferroni 校正？

### 维度 4：Holdout 纪律
- 工作集 n=163 的边界是否清晰（< 2024-12-10）？
- Holdout 40 条的隔离是否在文档中明确声明？
- 是否存在任何预登记条款依赖 Holdout 内数据的风险？

### 维度 5：A-2 碰撞门处理
- 文档是否明确处理了 A-2 尸检的教训？
- 辅检验 2（funding rate 分层）是否真正解决了 A-2 问题（funding 拥挤可能驱动 OI 骤降），还是仅做了表面分层？
- 若 A-1 事件与 A-2 信号高度重叠，文档是否有预备处理方案？

### 维度 6：验收标准的可证伪性
- 通过/失败标准是否在实验前完全固定？
- 是否存在"事后选择"的弹性（如选择最佳 horizon 汇报）？
- 结论是否有可能被模糊解读（不显著但点估计为正）？

### 维度 7：整体 HARKing 风险
- 预登记文档整体上是否已消除事后选择的主要路径？
- 作为 Risk Reviewer，你会要求修改哪些条款才能通过盲审？

---

## 输出格式

### 文件：`06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v1.md`

```markdown
# A-1 预登记独立风险审查报告 v1

**审查者：** Codex（独立 Risk Reviewer 角色）  
**审查日期：** [日期]  
**审查对象：** A1_CASCADE_REBOUND_PREREG_v1.md  
**审查结论：** [通过 / 需修改后通过 / 不通过]

---

## 执行摘要（3行以内）

[最重要的发现 + 结论]

---

## 七维度逐项评分与发现

| 维度 | 评级（A/B/C/D） | 主要发现 | 必须修改项 |
|------|----------------|---------|-----------|
| 1 机制假设 | | | |
| 2 触发定义 | | | |
| 3 统计设计 | | | |
| 4 Holdout纪律 | | | |
| 5 A-2碰撞门 | | | |
| 6 验收标准 | | | |
| 7 HARKing风险 | | | |

---

## 具体问题与修改建议

[每个 B/C/D 级维度写详细问题和修改要求]

---

## 最终结论

[通过条件 / 修改清单 / 审查员签字]
```

---

## 重要约束

- **禁止**读取 Holdout 数据（`06_RESEARCH/DATA/HOLDOUT/`）
- **禁止**读取 `01_MEMORY_CORE/` 下任何文件
- **禁止**修改预登记文档本身（你是审查者，不是起草者）
- **禁止**提前执行实验代码
- 完成后在 `04_AI_TEAM/TASK_INBOX/` 写入 `A1_RR_DONE.json`

---

## TASK_INBOX 完成通知

```python
import json, datetime, pathlib
inbox = pathlib.Path("04_AI_TEAM/TASK_INBOX")
inbox.mkdir(exist_ok=True)
done = {
    "task_id": "A1_RR",
    "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
    "status": "completed",
    "output_file": "06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v1.md",
    "review_conclusion": "通过 / 需修改后通过 / 不通过",
    "notes": "填写最重要发现"
}
(inbox / "A1_RR_DONE.json").write_text(json.dumps(done, ensure_ascii=False, indent=2))
```
