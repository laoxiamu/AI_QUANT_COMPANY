# Codex 直调配方（DEC-061 落地，2026-06-11 验证通过）

**通道：** Claude 经 Desktop Commander 调 Codex CLI（v0.139.0，npm @openai/codex；与桌面客户端共享 ~/.codex/auth.json，免登录）。

## 标准调用（三要素缺一卡死）

```bash
cd <项目根> && export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 && \
codex exec --skip-git-repo-check -C /Users/yaomingyu/Documents/AI_QUANT_COMPANY \
  --sandbox workspace-write \
  "$(cat 04_AI_TEAM/CODEX_TASKS/TASK_XXX.md)" < /dev/null
```

1. **代理 env 必须显式给**（CLI 不走系统代理，缺了无输出卡死）。
2. **`< /dev/null` 必须加**（否则等 stdin 卡死）。
3. 写文件任务用 `--sandbox workspace-write`；纯分析可用默认 read-only。

## 护栏（DEC-061 原定，不变）
- 任务书先落文件（04_AI_TEAM/CODEX_TASKS/），调用引用文件——保留文件留痕。
- 七问前置由 Claude 在出任务书时完成；D 级仍人工确认；执行报告回 CODEX_TASKS/REPORT_*.md。
- 项目根已部署 AGENTS.md（Codex 自动读取，含 Protocol 铁律/禁止项）。
- 成本：每次调用 token 用量记入观察（首测 10.8k tokens）；大任务优先夜间。

## 验证记录
2026-06-11：smoke test 返回 CODEX_DIRECT_CALL_OK（model gpt-5.5，session 019eb623）。
