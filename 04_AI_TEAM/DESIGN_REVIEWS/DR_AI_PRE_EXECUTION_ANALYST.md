# DR-E2：AI Pre-Execution Analyst 工程可行性评审

**类型：** Claude→Codex 设计评审（新机制，DEC-071）
**发起：** Claude（主理人/CTO），2026-06-14
**要求：** Codex 从工程实现角度独立 critique，输出到 `DR_AI_PRE_EXECUTION_ANALYST_CODEX_CRITIQUE.md`

---

## Claude 的当前设计方案

AI Pre-Execution Analyst 是在 Track A（自动执行）之外的 AI 分析层：

**触发时机：**
1. TSMOM 信号生成后、Decision Gateway 执行前
2. A-1 事件检测触发时（OI 骤降）
3. Carry 仓位调整决策前
4. Founder 主动发起（输入标的名称）

**执行方式：**
- 调用 Claude API（claude-haiku-4-5 或类似轻量模型控制成本）
- 输入：结构化数据 JSON（当前持仓/信号详情/近期市场数据快照）
- 输出：结构化建议（approve / caution / no-trade / needs-human-review + 原因）
- 执行路径：独立于 Track A，不阻塞 Decision Gateway 的规则执行

**当前假设：**
- API 调用耗时 < 3 秒（对我们的日线/4H策略可接受）
- 每天调用次数约 5-20 次
- API 故障时 fallback = 跳过 AI 分析，Track A 正常执行

---

## 需要 Codex 评估的具体问题（不是让你赞同，是让你找问题）

**问题1：API 可靠性**
- 如果 Claude API 在信号发出时挂掉，fallback 逻辑该如何设计？
- timeout 设多少合理？超时后是 approve（默认放行）还是 no-trade（默认拦截）？
- 哪个 fallback 更安全，理由是什么？

**问题2：数据一致性**
- AI 分析用的 PostgreSQL 快照和 Decision Gateway 用的数据之间，如果有时间差（数据竞争），会有什么问题？
- 应该在哪个时间点抓快照？

**问题3：成本估算**
- 以 claude-haiku-4-5 价格估算：每天 20 次调用，每次输入约 2000 tokens + 输出约 500 tokens，月成本大约多少？
- 对于 A-1 事件这类突发场景，一天内可能触发多次，是否需要调用频率限制？

**问题4：系统集成复杂度**
- Track A 是确定性程序（Python），要调用 Claude API 并等待结果，这在异步/同步架构上有什么陷阱？
- 建议用同步调用（简单）还是异步（复杂但不阻塞）？

**问题5：结果存储**
- AI 分析建议需要写日志（可审计）。建议存 PostgreSQL 还是 JSON 文件？格式？

---

## 输出要求

文件：`04_AI_TEAM/DESIGN_REVIEWS/DR_AI_PRE_EXECUTION_ANALYST_CODEX_CRITIQUE.md`

格式：
```
## 工程评审结论

### 问题1：API可靠性
[你的评估]
[具体建议]

### 问题2：数据一致性
...

### 总体判断
[整体方案是否工程可行？有哪些必须修改的地方？]
[评级：可行/需修改后可行/设计缺陷需重新设计]
```

不需要赞同 Claude 的方案，如果有根本性问题直接说。
