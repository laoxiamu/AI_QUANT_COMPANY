# 工具路由表 v1（2026-06-10）
| 活的类型 | 走哪 | 理由/禁区 |
|---|---|---|
| 判断/设计/研究主张/验收 | Claude 主会话 | 唯一判断层；禁被动执行 |
| 复杂实现（>100行/多文件/长迭代）| Codex | 文件式handoff+任务规格；R1起经直调通道 |
| 机械批量（索引/横幅/搬运/格式化）| 低模型会话 | 按 LOW_TIER_CHARTER；Claude验收 |
| ≤50行分析脚本 | Claude 沙盒 bash | 一次性、可丢弃 |
| 常驻进程（采集器等）| Mac launchd / 云VM | **沙盒禁**（会话结束即死）|
| 定时巡检/月审/周监控 | scheduled task | SKILL与现行口径同步是Claude责任 |
| 独立复核/红队 | 隔离子会话 | 只给Context Pack（见04_AI_TEAM/CONTEXT_PACKS）|
| 外部知识摄取 | WebSearch/x-reader | 按可信源清单；交易所博客=最低档证据 |
