## 工程评审结论

结论先行：方案工程上可做，但当前设计必须收紧语义边界。AI Pre-Execution Analyst 在第一版只能是 advisory/audit layer，不能成为隐含的执行闸门；否则会把一个非确定性、外部依赖、模型版本会漂移的组件接入 Track A，破坏确定性执行和后续可审计性。

### 问题1：API可靠性

评估：Claude API 故障、超时、429、返回非 JSON、schema 不匹配都必须视为正常运行场景，而不是异常边缘情况。当前的 "fallback = 跳过 AI 分析，Track A 正常执行" 方向正确，但不能在日志或内部状态里伪装成 `approve`。`approve` 是模型给出的建议；API 不可用应记录为 `analysis_status=timeout/api_error/unavailable`，`recommendation=null`，`blocking=false`。

具体建议：
- 第一版采用 fail-open：AI 分析不可用时，Decision Gateway 按确定性规则继续执行。
- fail-open 更安全的前提是：AI 层没有被定义为风控硬闸门。原因是 Track A 的规则、成本、风控才是被研究和审计过的执行主体；API 故障时默认 `no-trade` 会把供应商可用性变成未验证的交易过滤器，直接改变策略期望和样本路径。
- 如果未来要让 AI 拥有 veto/no-trade 权限，必须另立预登记策略：回测或 paper trading 中明确模拟 AI 不可用、schema 错误、延迟、模型升级等状态；未完成前不得进入实盘执行路径。
- inline timeout 建议总墙钟 2.5-3.0 秒，连接超时 0.5-1.0 秒；Founder 主动分析可以放宽到 10-30 秒，因为它不在执行热路径。
- 不建议在执行热路径里做多次 retry。最多一次短退避重试只适用于后台 worker；Gateway 侧应立即继续。
- 加 circuit breaker：例如连续 3 次 timeout/5xx 后暂停自动 AI 调用 15-30 分钟，只写 `skipped_circuit_open`，避免每个信号都卡在同一外部故障上。

### 问题2：数据一致性

评估：AI 分析和 Decision Gateway 如果各自查询 PostgreSQL，会出现 snapshot race。典型问题包括：AI 看到的是旧持仓，Gateway 看到的是新持仓；AI 分析的是上一根 4H bar 的信号，Gateway 执行的是更新后的信号；A-1 事件重复触发时，AI 的 `no-trade` 实际对应的不是最终下单 proposal。结果会造成审计链断裂，甚至出现“AI 反对了 A，但系统执行的是 B”的误读。

具体建议：
- 在“决策提案生成”时一次性冻结 snapshot，并生成 `decision_id` / `decision_context_id`。这个时间点应在信号生成完成、市场数据入库水位确认之后，Decision Gateway 校验和下单之前。
- Decision Gateway 和 AI Analyst 都只读取同一个 `decision_context_id`，禁止各自重新查“当前最新数据”。
- snapshot 至少包含：`as_of_ts_utc`、`data_cutoff_ts_utc`、source watermarks、strategy、symbol、signal payload、position/account version、open orders、risk limits version、input hash。
- PostgreSQL 侧建议把 decision proposal 作为权威对象落库：`decision_requests(id, trigger_type, snapshot_jsonb, snapshot_hash, status, created_at_utc)`。Gateway 和 AI 结果都挂到同一个 id。
- 对 A-1 事件，snapshot 应在事件 episode 创建时冻结；后续同一 episode 的重复触发应更新事件状态或追加 observation，不应生成语义重复的新 AI 决策。

### 问题3：成本估算

按 Anthropic/Claude 官方 pricing 页当前 Haiku 4.5 API 价格估算：input $1/MTok，output $5/MTok（https://claude.com/pricing，2026-06-14 查看）。

单次调用成本：
- 输入 2,000 tokens = 0.002 MTok x $1 = $0.002
- 输出 500 tokens = 0.0005 MTok x $5 = $0.0025
- 合计约 $0.0045 / 次

每天 20 次：
- 日成本约 $0.09
- 30 天月成本约 $2.70

成本本身不是主要约束，主要约束是突发事件下的调用风暴、供应商 rate limit、日志噪声和重复建议污染审计。建议加频率限制：
- 全局 cap：例如自动触发最多 50 次/日，超过记录 `skipped_rate_limited`。
- symbol cap：例如同一 symbol 同一 trigger 每 4H bar 最多 1 次。
- episode cap：A-1 同一 OI crash episode 只允许 1 次初始分析，后续只在关键状态变化时重分析。
- payload cap：输入 token 上限建议 4k-6k，超过时用确定性摘要规则截断，不能让市场快照无界增长。

### 问题4：系统集成复杂度

评估：Track A 是确定性 Python 程序，直接在 Gateway 内同步调用 LLM 会引入几个工程陷阱：外部网络延迟、异常向上传播导致交易任务失败、JSON schema 不稳定、模型版本漂移、重试导致重复日志、异步结果乱序、以及 API key/环境配置故障。更重要的是，它会让“执行是否顺利”依赖 AI 供应商可用性。

建议架构：Gateway 不直接调用 Claude API。Gateway 只做三件事：
- 写入不可变 `decision_request` snapshot；
- 触发或入队一个 AI analysis job；
- 按确定性规则继续执行。

AI worker 可以用同步 HTTP 调用实现，保持代码简单；系统集成层面则是异步的。也就是：不要把 `asyncio` 复杂性塞进 Track A 主流程，而是在独立 worker/process 中做同步调用、严格 timeout、严格 schema parse、落库结果。这样既不阻塞 Gateway，也避免 Python 事件循环和调度器互相干扰。

如果 Claude 明确要求“AI 结果必须在下单前返回”，那是另一种设计：它不再是独立于 Track A 的分析层，而是执行前 gate。该版本需要重新设计验收标准、回测/仿真、降级策略和人工介入流程。当前方案不建议这么做。

### 问题5：结果存储

建议以 PostgreSQL 为权威审计存储，JSON 文件只作为导出或 DB 故障时的临时 append-only fallback。理由：AI 建议必须和 `decision_id`、真实执行结果、订单、持仓版本关联查询；JSON 文件长期会产生文件轮转、并发写、去重和关联困难。

建议表结构字段：
- `id`：UUID
- `decision_id` / `event_id`：关联冻结的 decision snapshot
- `trigger_type`：`tsmom_signal` / `a1_oi_crash` / `carry_rebalance` / `founder_manual`
- `symbol`、`strategy`
- `model`、`model_version`、`prompt_template_version`、`schema_version`
- `request_ts_utc`、`response_ts_utc`、`latency_ms`、`timeout_ms`
- `status`：`success` / `timeout` / `api_error` / `schema_error` / `rate_limited` / `circuit_open`
- `recommendation`：`approve` / `caution` / `no_trade` / `needs_human_review` / null
- `reasons_jsonb`、`risk_flags_jsonb`、`raw_response_jsonb`
- `input_snapshot_hash`，必要时保存 `input_snapshot_jsonb` 或指向 snapshot 表
- `input_tokens`、`output_tokens`、`estimated_cost_usd`
- `error_code`、`error_message_redacted`

日志原则：
- 不记录 API key、账户密钥、完整可用于交易账户接管的信息。
- 模型输出必须先过 JSON schema 校验；校验失败不能进入 recommendation 字段，只能记为 `schema_error`。
- prompt 模板版本必须固定，否则同一模型、同一数据的建议不可复核。

### 总体判断

整体方案“需修改后可行”。

必须修改的地方：
- 明确 AI Analyst 第一版是 advisory/audit，不是 veto gate；`no-trade` 只是建议，不得自动阻断 Track A。
- fallback 语义必须从 `approve/no-trade` 改为 `analysis unavailable + Track A continues`，不能把不可用伪装成模型批准。
- 用单一冻结 snapshot 驱动 Gateway 和 AI 分析，禁止两边各查当前数据库。
- Gateway 不直接等待外部 API；采用 `decision_request` + 后台 worker + PostgreSQL 审计表。
- 加 rate limit、circuit breaker、schema 校验、模型/prompt 版本记录。

评级：**需修改后可行**。
