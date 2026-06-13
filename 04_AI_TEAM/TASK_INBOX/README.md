# TASK_INBOX — Codex→Claude 事件通知收件箱

**设计**：事件驱动写入 + 高频调度检查（DEC-071 扩展，2026-06-14）

## 协议

### Codex 侧（写入）
每个Codex任务最后一步必须执行：
```python
import json, datetime, pathlib
inbox = pathlib.Path("04_AI_TEAM/TASK_INBOX")
inbox.mkdir(exist_ok=True)
done = {
    "task_id": "D1",
    "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
    "status": "completed",   # completed / blocked / failed
    "output_file": "04_AI_TEAM/CODEX_TASKS/REPORT_D1.md",
    "next_task": "D2",       # 建议的下一步（Claude有权不采纳）
    "notes": "35资产全部下载完成，DOWNLOAD_MANIFEST.json已生成"
}
(inbox / f"{done['task_id']}_DONE.json").write_text(json.dumps(done, ensure_ascii=False, indent=2))
```

### Claude 侧（读取）
调度任务每15分钟检查TASK_INBOX/，发现未处理的_DONE.json文件：
1. 读取完成记录
2. 验收输出（读REPORT文件，给出主理人判断）
3. 按next_task映射表派发下一个Codex任务
4. 将_DONE.json移至PROCESSED/（防止重复处理）

## 当前next_task映射表

| 完成任务 | 触发条件 | 自动下一步 |
|---|---|---|
| D1 | status=completed | 验收D1 → 派发D2 |
| D2 | status=completed | 验收D2 → 更新CURRENT_STATE TSMOM结论 |
| D3 | status=completed | 验收D3预登记 → 提醒Founder进行Risk Reviewer盲审 |
| DR-E2 | status=completed | 读critique → 更新E2任务规格 → 派发E2 |
| E1 | status=completed | 验收E1 |
| E2 | status=completed | 验收E2 → 触发Phase 2蓝图最终整合 |
| E3 | status=completed | 验收E3 |
| E4 | status=completed | 验收E4 → 检查[专业异议] |

## 文件生命周期

```
创建：04_AI_TEAM/TASK_INBOX/{TASK_ID}_DONE.json
处理后移至：04_AI_TEAM/TASK_INBOX/PROCESSED/{TASK_ID}_DONE_{date}.json
```

## 与AGENTS.md的关系

AGENTS.md已包含§1b中断机制和专业异议升级路径。
本协议是其通知通道的具体实现，Codex任务书中必须包含TASK_INBOX写入步骤。
