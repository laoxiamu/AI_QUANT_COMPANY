# PB1：路径B 强平数据解析器 + 就绪门计数器（自包含，先写后用）

**定位：** 路径B（前向真实强平数据机制确证，见 `06_RESEARCH/PREREGISTRATIONS/A1_FORWARD_LIQUIDATION_PATH.md`）第一步的**离线工具**。采集器在腾讯云SG VM 持久化完整 Binance `!forceOrder@arr` 原始 JSONL。本任务**不依赖能否 SSH**：用合成 + 任何本地样本把解析器与就绪门计数器写好并单测，待能拉到真实 LIQUIDATIONS 后直接指向真实路径运行。
**计数定性：** 纯工具/监控，不耗 Alpha 计数、不下任何 edge 结论、不读 HOLDOUT。
**输出：** `06_RESEARCH/CODE/forward_liq/liq_parser.py` + `forward_event_counter.py` + `tests/` + 一份 `06_RESEARCH/RESULTS/20260615_pb1_harness_selftest.md`。

## 背景：Binance forceOrder 原始消息 schema
单条强平消息形如 `{"e":"forceOrder","E":<eventMs>,"o":{"s":"BTCUSDT","S":"SELL","o":"LIMIT","f":"IOC","q":"0.014","p":"...","ap":"<avgPrice>","X":"FILLED","T":<tradeMs>,...}}`。
- `o.S=SELL` = **多头被强平→卖压**（路径A 历史代理想识别却识别不了的方向，这里是真实的）；`o.S=BUY` = 空头被强平→买压。
- 清算名义额 ≈ `float(o.ap or o.p) * float(o.q)`。`o.T`=成交毫秒(UTC)。`o.s`=品种。

## 任务
### 1. `liq_parser.py`（解析器）
- 输入：JSONL 文件路径（每行一条原始消息；容忍坏行→跳过并计数）。
- 输出：规整 DataFrame，列 `ts_utc(datetime), symbol, side(SELL/BUY), qty, price(ap优先否则p), notional_usdt`。
- 健壮性：缺字段/空值/重复行处理；全程 UTC；坏行比例报告。

### 2. `forward_event_counter.py`（就绪门计数器，对齐 A1_FORWARD_LIQUIDATION_PATH §2/§3）
- 仅 BTCUSDT/ETHUSDT/SOLUSDT。
- 候选"多头强平卖压脉冲"占位口径（**参数化、可调，不冻结**——真正冻结值留给路径B正式预登记）：滚动短窗(默认1h)内 `side=SELL` 清算 `notional_usdt` 之和达到该品种历史滚动分位 ≥ 阈值(默认0.99，参数)。
- 产出：按品种/按月候选事件计数、累计 n、首末时间、外推达到目标 n_min(参数，默认 120) 的预计日期 → 写/更新 `06_RESEARCH/RESULTS/A1_FORWARD_EVENT_COUNT.md`。
- **只计数，不算事件后收益、不下结论**。

### 3. 单元测试（`tests/`）
- 解析：正常行/坏行/缺字段/SELL与BUY/notional 计算 至少各 1 例。
- 计数：合成一段已知 JSONL，断言候选事件数符合手算预期；分位阈值边界。
- 用合成数据自测全绿即可（无需真实数据）。

### 4. 自测报告
`20260615_pb1_harness_selftest.md`：模块用途、参数默认值、单测结果、"如何指向真实 LIQUIDATIONS 运行"的一行命令示例、以及**明确声明所有触发参数为占位、待路径B正式预登记冻结**。

## 工程
- 七问前置已由 Claude 完成。机制：为路径B 提供方向真实的事件识别地基与就绪门倒计时。
- 不读 HOLDOUT、不碰路径A 的 A1_WORK/sealed、不改任何预登记。
- 完成写 `04_AI_TEAM/TASK_INBOX/PB1_DONE.json`(task_id=PB1,status,output_files,notes)。可 commit（Claude 复核）。
