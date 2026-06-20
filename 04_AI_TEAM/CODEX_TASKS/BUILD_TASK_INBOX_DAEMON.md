# Codex 任务：构建 TASK_INBOX 文件监听 Daemon

**任务 ID：** BUILD-INBOX-DAEMON-001  
**状态：** 待 Founder 确认后派发  
**负责人：** Codex（`--sandbox danger-full-access`，需本地文件监听能力）  
**预估时间：** 30-60 分钟  
**优先级：** P2（协作效率，不阻塞研究主线）

---

## 问题背景

Codex 完成任务后，结果写入 `04_AI_TEAM/TASK_INBOX/{ID}_DONE.json`，但没有人自动拾取——Founder 需要手动把结果复制给 Claude，Claude 再决定下一步。这条传话链是主要协作摩擦来源。

---

## 任务目标

在 Mac 本地运行一个轻量 Python daemon，监听 `TASK_INBOX/` 目录：
- 发现新的 `*_DONE.json` → 自动处理（更新状态/触发通知）
- 不需要 Founder 手动传话

---

## 技术规格

### 目标文件结构

```
04_AI_TEAM/TASK_INBOX/
├── README.md          （已有）
├── {ID}_DONE.json     （Codex 写入）
├── {ID}_PROCESSED.json（daemon 处理后标记）
└── INBOX_DAEMON/
    ├── daemon.py      （主程序）
    ├── requirements.txt
    ├── daemon.log     （运行日志，不入git）
    └── start.sh       （一键启动脚本）
```

### DONE.json 格式（Codex 写入）

```json
{
  "task_id": "REORGANIZE-ARCHIVE-001",
  "status": "DONE",
  "completed_at": "2026-06-20T14:30:00",
  "summary": "归档完成，移动了25个文件，state_check零报错",
  "next_suggested": "dispatch: P1-OSS-001",
  "artifacts": ["path/to/file1", "path/to/file2"]
}
```

### daemon.py 核心逻辑

```python
# 伪代码，Codex 实现
watch_dir = PROJECT_ROOT / "04_AI_TEAM/TASK_INBOX"
poll_interval = 60  # 秒

while True:
    for done_file in watch_dir.glob("*_DONE.json"):
        processed_marker = done_file.with_suffix("").with_suffix("_PROCESSED.json")
        if processed_marker.exists():
            continue
        
        data = json.load(done_file)
        
        # 1. 写入 CURRENT_STATE §1b（追加完成记录）
        append_to_state(data)
        
        # 2. 写摘要到 TASK_INBOX/DIGEST.md（Claude 下次开局读）
        append_to_digest(data)
        
        # 3. 标记已处理
        processed_marker.write_text(json.dumps({"processed_at": now()}))
        
        log(f"Processed: {data['task_id']}")
    
    sleep(poll_interval)
```

### DIGEST.md 格式（daemon 追加，Claude 开局读）

```markdown
## 2026-06-20 14:30 — REORGANIZE-ARCHIVE-001 完成
- 状态：DONE
- 摘要：归档完成，移动了25个文件，state_check零报错
- 建议下一步：dispatch P1-OSS-001
- 产物：[查看任务书]
```

---

## 验收标准

1. `start.sh` 一键启动，后台运行，写 `daemon.log`
2. 手动写一个测试 `TEST-001_DONE.json` → 60秒内 `DIGEST.md` 新增条目
3. 重复运行不重复处理（`_PROCESSED.json` 标记有效）
4. daemon 崩溃后重启不丢失已处理记录
5. `daemon.log` 包含时间戳和处理记录

---

## 执行约束

- 不需要网络
- 不修改任何已有文件（只追加 DIGEST.md 和写 _PROCESSED.json）
- 不自动派发 Codex 任务（只写摘要，Claude 决定下一步）
- 日志文件加入 `.gitignore`

---

**派发前确认：** Founder 确认后在新会话派 Codex，传本文件路径。  
**注：** 定时任务方案已被Founder否决（两次夜间事故，Cowork需保持运行）。本daemon走文件监听触发，不是定时调度，不受该限制。
