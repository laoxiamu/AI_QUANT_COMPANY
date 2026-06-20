# REPORT_OSS-001_oss_tool_synthesis

**任务ID：** OSS-001  
**生成时间：** 2026-06-20T09:22:32Z  
**执行边界：** 只读扫描指定文件；未读取 `~/.aiquant_sealed/`；未修改既有文件。  
**技能说明：** 任务书指定 `research-harvest` + `diagnose`。当前 Codex 技能列表未暴露 `research-harvest`，仅按 `diagnose` 做遗漏/矛盾检查；该工具链缺口已写入更新建议。

## 执行摘要

1. DEC-076 的主线未被推翻：1个月 carry 实盘路线仍应围绕 **Freqtrade + CCXT + Binance 官方 REST/data.binance.vision + 项目自写数据/风控/对账薄层**。
2. carry 开源参考只有一个明确遗漏：`PEER_PROJECTS_BENCHMARK` 记录 Hummingbot 生态列出 **Funding Rate Arbitrage** 原型，但本批文件没有给 entry/exit/参数源码级细节，不能直接照搬。
3. 最高价值立即行动不是换框架，而是补三件轻量能力：Freqtrade futures dry-run 模板、lookahead/slice-check、Jesse式路径 Monte Carlo + Qlib式 experiment registry。
4. 发现两类补充：Nautilus 的 event log/backtest-live parity 应作为 Phase 2 架构闸；Hummingbot/Jesse MCP 只可作为 Phase 2 只读/仿真控制面参考。
5. 发现一个口径冲突：旧文档曾建议 CoinGlass 小套餐；本任务明确禁止付费工具，故所有付费数据商本报告列为跳过，不纳入当前路线。

## 文件扫描汇总

| 文件 | 文件性质 | 主要发现 | 相关性 | 覆盖状态 |
|---|---|---|---|---|
| `00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_REPORT_v1.md` | 早期外部研究报告 | 推荐 `ccxt`、`vectorbt`、Backtrader、Nautilus；强调实盘失败根因是过拟合/滑点低估/制度变迁 | 中 | 部分：CCXT/vectorbt/Nautilus 已覆盖；Backtrader 已被后续否决 |
| `00_PROJECT_MANAGEMENT/EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION.md` | 策略方向外部调研 | 提到资金费率套利/市场中性可回避方向判断；指出 Freqtrade 回测下一根K线执行可防前视 | 高 | 部分：carry方向被 CARRY 系列吸收；Freqtrade 执行纪律已覆盖 |
| `00_PROJECT_MANAGEMENT/AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12.md` | AI能力/工具治理调研 | 建议 `aiq-data-contract`、只读 Data Catalog MCP、Binance/Exchange Data MCP、Hummingbot/Jesse MCP Phase 2 | 中 | 部分：数据契约思想已出现，MCP不进交易闭环已覆盖 |
| `00_PROJECT_MANAGEMENT/AI_CAPABILITY_TOOLING_AUDIT_v1.md` | 工具审计 | CoinDesk/LunarCrush 低优先；永续/funding/OI 继续用自有 Python 管线；自研 skill 最高杠杆 | 中 | 部分：外部数据 MCP 已覆盖，skill 可见性仍有缺口 |
| `00_PROJECT_MANAGEMENT/AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12.md` | 加密策略综合研究 | funding/carry/basis 是状态/成本/低杠杆候选；不得把极端 funding 当反转主线 | 高 | 部分：carry机制已覆盖；状态变量纪律应在 carry 报告中继续显式化 |
| `00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v1.md` | 已降级历史计划 | 曾主张 Triple Barrier/Meta-Labeling，并把 Freqtrade/Nautilus 放 Phase 2 | 中 | 部分/冲突：方法论已被 v2 修正；Freqtrade Phase 2 口径被 DEC-076 Phase 1 采用取代 |
| `00_PROJECT_MANAGEMENT/CAPABILITY_ENV_REGISTRY.md` | 环境/能力登记 | 明确 Binance 数据边界：funding REST 分页、OI REST 仅近1月、data.binance.vision metrics、强平 snapshot 非完整 | 高 | 已覆盖：与 DEC-076 数据路线一致 |
| `00_PROJECT_MANAGEMENT/FRONTIER_AI_OPC_AGENT_GOVERNANCE_RESEARCH_2026-06-12.md` | AI治理/agent harness调研 | 推荐 trace schema、no-lookahead eval、data contract、result-intake；不做重编排 | 低-中 | 部分：对1个月实盘的审计/交接有用，但非交易工具 |
| `00_PROJECT_MANAGEMENT/BPR_TOP_LEVEL_FRAMEWORK_REFERENCE_2026-06-15.md` | 顶层流程方法评审 | 强调“证据到部署”“信号到结算”“异常到恢复”等价值流；不要把完整框架变长期治理项目 | 低 | 部分：提供路线治理边界，不新增交易工具 |
| `03_RAW_INBOX/STATUS_RECORDS/D38：工具集成评估报告.md` | 历史工具集成报告 | Freqtrade/Nautilus/vectorbt/Triple Barrier/CCXT 已被早期识别；binance-pro 与 ClawHub skill 风险高 | 中 | 部分：多数已覆盖；binance-pro 否决仍有效 |
| `00_PROJECT_MANAGEMENT/TOOL_ROUTING.md` | 工具路由表 | 明确复杂实现走 Codex，判断/验收走 Claude，≤50行分析脚本可 Claude 直接跑 | 低 | 已覆盖：不新增 carry 工具 |
| `00_PROJECT_MANAGEMENT/AI_CAPABILITY_BASELINE.md` | 能力基线 | 本地已验证 vectorbt、ccxt、data.binance.vision 历史数据；Codex 可完成复杂实现 | 中 | 已覆盖：支持当前免费工具链 |
| `02_KNOWLEDGE_BASE/TOOLS_KNOWLEDGE.md` | 工具知识库/对照权威 | 已收录 Freqtrade/CCXT/vectorbt/Binance REST/Nautilus；标记 Freqtrade lookahead-analysis 从未使用、Jesse/Qlib待评估 | 高 | 对照文件：发现 Jesse/Qlib/Hummingbot 仍需补具体条目 |
| `00_PROJECT_MANAGEMENT/STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md` | DEC-076 依据 | 采用 Freqtrade Phase 1、CCXT薄适配、Binance官方数据、vectorbt研究、Nautilus Phase 2；MCP不进交易闭环 | 高 | 对照文件：主线成立 |
| `00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v2.md` | 工具集成矩阵v2.1 | 修正三屏障边界：carry/套利类退出由机制失效决定；Backtrader/vn.py不采纳；付费/ClawHub工具谨慎 | 高 | 对照文件：补充 carry 不适用三屏障的纪律 |
| `00_PROJECT_MANAGEMENT/PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12.md` | 同类项目对标 | Freqtrade lookahead/dry-run；Jesse Monte Carlo；Hummingbot Funding Rate Arbitrage 原型；Qlib recorder；Nautilus event log | 高 | 对照文件：本任务最主要遗漏来源 |

## carry策略开源参考

### 1. Hummingbot Funding Rate Arbitrage

**来源：** `PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12.md` §Hummingbot。  
**扫描结论：** 文件明确说 Hummingbot 官方/社区页面列出 `Funding Rate Arbitrage`，说明 funding/carry 方向在 Hummingbot 生态中有实践原型。但本批文件没有给策略源码、参数、entry/exit、仓位公式或风控触发细节。

**可提取的设计信息：**

- Hummingbot 的可借鉴层不是 Phase 1 执行，而是 **Client / Gateway / API / 控制面 / MCP / Skills** 分层。
- 与 carry 相关的价值是多交易所 connector、状态查询、bot 控制面和套利原型索引。
- 本项目 Phase 1 不应接 Hummingbot 执行；MCP/Skills 不得给交易权限。

**缺失的具体策略细节：**

- 未提取到 entry 条件，例如 funding 阈值、净年化门槛、跨所价差阈值。
- 未提取到 exit 触发，例如 funding 翻负、basis 收敛、对冲偏离、强平距离不足。
- 未提取到对冲结构，例如 spot/perp 同所或跨所、rebalance 频率、手续费/滑点模型。
- 未提取到已知风险清单，例如 borrow/transfer/latency、API故障、资金划转、保险基金/ADL、交易所风险。

**建议：Phase2。** 当前只把它登记为“存在可复核 OSS 原型”，不直接采用。Claude 若验收后要深挖，应单独发 Hummingbot 源码/文档审计任务，只读提取参数和状态机，不接交易权限。

### 2. Jesse

**来源：** `PEER_PROJECTS_BENCHMARK_RESEARCH_2026-06-12.md` §Jesse。  
**与 carry 的关系：** 未发现 Jesse 内置 funding/carry 策略实现；价值在研究 UX、无前视、多品种多周期、Monte Carlo、MCP。

**可借鉴设计：**

- 用 trade-order shuffling 与 candle simulation 做路径稳健性。
- 将 Monte Carlo/路径重排纳入 carry 四件套中的爆仓概率与路径风险。
- 只借鉴方法，不使用 Jesse Optimize/AI fine-tune。

**建议：立即用。** 自实现 Monte Carlo / block bootstrap / 路径重排小函数，不引入 Jesse 框架。

### 3. Freqtrade

**来源：** `OSS_BUILD_VS_BUY`、`PEER_PROJECTS_BENCHMARK`、`TOOLS_KNOWLEDGE`。  
**与 carry 的关系：** 不提供 scanned-file 级别的 carry 策略模板，但直接加速 dry-run/live/DB/控制面。

**可借鉴设计：**

- `dry-run/live` 分离，先纸面仿真再小额。
- DB 持久化作为状态权威，避免 V4 内存状态事故。
- futures 需 `trading_mode="futures"` 和 margin mode 配置。
- `lookahead-analysis` 可作为 Freqtrade 策略前视检测；非 Freqtrade 研究脚本应做等效切片复算。

**建议：立即用。** 用它承载 dry-run、live、DB、UI/API、基本订单管理；策略信号、研究验收、风险守门和对账仍项目自写。

### 4. Binance 官方 REST/data.binance.vision + CCXT

**来源：** `OSS_BUILD_VS_BUY`、`CAPABILITY_ENV_REGISTRY`。  
**与 carry 的关系：** 这是 carry 核算的事实源和薄适配层。

**可借鉴设计：**

- funding history 用 `/fapi/v1/fundingRate`，分页，保留 `fundingRate/fundingTime/markPrice`。
- mark price kline 与 contract kline 分开，不能把 contract close 当 mark。
- OI REST 历史只有近1月，长期依赖 data.binance.vision metrics 或后续第三方；本任务禁止付费，故先用官方可得口径。
- CCXT 用于统一 exchange adapter，不裸用作研究事实源；Binance 特有字段必须 schema 校验。

**建议：立即用。** 这是 DEC-076 已决策项。

## 1个月实盘路线加速器

### 立即用

| 加速器 | 具体用法 | 验收点 |
|---|---|---|
| Freqtrade futures dry-run | 部署 Binance USDT-M futures dry-run，DB 落盘，单策略单账户低杠杆 | dry-run 能连续记录信号、订单、费用、funding、余额 |
| Freqtrade `lookahead-analysis` 或等效切片复算 | 若策略落入 Freqtrade，跑 `freqtrade lookahead-analysis --strategy YourStrategy`；否则自实现逐切片复算 | 无全样本分位、无未来 shift、信号在 t 后执行 |
| Binance 官方 funding/mark/OI 数据契约 | 用 `requests/httpx + checksum + UTC + schema` 固化字段 | funding、mark、contract、OI 字段不混用 |
| CCXT 薄适配 | 只封装 read-only/执行必需公共接口，Binance 专用字段保留 params 和原始响应 | 字段级测试通过，不替代官方历史源 |
| Jesse式 Monte Carlo/路径重排 | 自实现 trade-order shuffling、block bootstrap、爆仓路径压力 | 四件套中爆仓概率可复算，seed 固定 |
| Qlib式 experiment registry | 轻量 `experiment_registry.json/csv`，记录 hypothesis、data_hash、code_hash、metrics、decision | 每次 carry 变体可审计、可追踪 |
| RD-Agent式 trace | CODEX 报告加入 input_files/output_files/tools/tests/决策 | Claude 验收可机器检查 |
| Nautilus式 event_id/hash | 数据 catalog 对 market/funding/signal/order/reconcile 事件记录 event_time/source/hash | Phase 2 replay 不从零补账 |

### Phase2

| 加速器 | 何时用 | 理由 |
|---|---|---|
| Hummingbot Funding Rate Arbitrage 源码审计 | Freqtrade dry-run 跑通后 | 需要提取具体资金费套利状态机，但不该先接执行 |
| Hummingbot/Jesse MCP | 只读/仿真控制面稳定后 | AI 可查状态，但不能持交易权限 |
| NautilusTrader | Freqtrade 暴露真实 parity/对账痛点后 | 生产级事件驱动与 replay 成本高，不适合1个月第一地基 |
| LEAN / ResultHandler 思路 | 结果 schema 需要统一时 | 借鉴边界，不引完整平台 |
| OpenBB dashboard | data catalog 稳定后 | 做 Founder-facing 状态页，不做权威数据源 |

### 明确跳过

| 工具/方法 | 跳过原因 |
|---|---|
| Freqtrade Hyperopt / Jesse Optimize / AI fine-tune | 与禁止参数搜索、剩余实验命稀缺冲突 |
| Backtrader / vn.py | 后续 v2 已明确不采纳；维护/社区/重复价值不合适 |
| binance-pro / ClawHub交易类 skill | 交易权限与恶意 skill 供应链风险；Phase 1 禁 |
| CoinGlass / CoinAPI / Kaiko / Amberdata | 付费或机构数据；本任务约束免费 OSS 路线，不建议纳入 |
| Binance/CCXT 交易 MCP | LLM 调交易接口不可作为核心系统；最多只读且无资金账户 |
| Qlib/RD-Agent 框架本体 | 方向偏股票/ML或自动 alpha 工厂；只借鉴 recorder/trace |

## 决策矩阵

| 工具/方法 | 来源文件 | 与carry/实盘相关性 | DEC-076状态 | 建议 | 理由 |
|---|---|---|---|---|---|
| Freqtrade | OSS_BUILD_VS_BUY; PEER_PROJECTS; TOOLS_KNOWLEDGE | 高 | 已覆盖 | 立即用 | Phase 1 dry-run/live/DB/control plane 地基，最快缩短 FEASIBILITY→dry-run |
| Freqtrade lookahead-analysis | PEER_PROJECTS; TOOLS_KNOWLEDGE | 高 | 遗漏/部分 | 立即用 | 已登记但从未执行；carry上实盘前必须有前视检测或切片复算 |
| Freqtrade Hyperopt | PEER_PROJECTS; TOOLS_KNOWLEDGE | 中 | 已覆盖 | 跳过 | 参数优化诱导过拟合，违反研究纪律 |
| CCXT | OSS_BUILD_VS_BUY; CAPABILITY_ENV_REGISTRY; D38 | 高 | 已覆盖 | 立即用 | 统一交易所薄适配；不裸替代 Binance 官方事实源 |
| Binance 官方 REST/data.binance.vision | OSS_BUILD_VS_BUY; CAPABILITY_ENV_REGISTRY; AI_CAPABILITY_BASELINE | 高 | 已覆盖 | 立即用 | carry 必需 funding/mark/OI/klines 数据源，免费且可审计 |
| vectorbt 开源 | OSS_BUILD_VS_BUY; V5 v1/v2; D38 | 中 | 已覆盖 | 立即用 | 研究加速和批量扫描可用；不做实盘/风控 |
| Hummingbot Funding Rate Arbitrage | PEER_PROJECTS | 高 | 遗漏 | Phase2 | 只发现原型存在，缺 entry/exit/对冲细节；需源码审计后再借鉴 |
| Hummingbot Client/Gateway/API/MCP | PEER_PROJECTS; AI_CAPABILITY_OPTIMIZATION | 中 | 部分 | Phase2 | 控制面/connector 可学，但 Phase 1 不接执行、不授交易权限 |
| Jesse Monte Carlo | PEER_PROJECTS; TOOLS_KNOWLEDGE | 高 | 遗漏 | 立即用 | 用路径重排/仿真增强爆仓概率，不引 Jesse 框架 |
| Jesse MCP/策略UX | PEER_PROJECTS; AI_CAPABILITY_OPTIMIZATION | 低-中 | 部分 | Phase2 | 只读/仿真接口可参考，当前不接交易执行 |
| Qlib Recorder / experiment registry | PEER_PROJECTS; TOOLS_KNOWLEDGE | 中 | 遗漏 | 立即用 | 轻量记录 hypothesis/data_hash/code_hash/metrics/decision，直接提升可审计性 |
| Qlib框架本体 | PEER_PROJECTS | 低 | 遗漏 | 跳过 | 偏股票/ML，不能直接搬 crypto perp carry |
| RD-Agent trace/eval | PEER_PROJECTS; FRONTIER_AI_OPC | 中 | 遗漏 | 立即用 | 借鉴 trace/eval，不自动生成 alpha |
| RD-Agent自动实验 | PEER_PROJECTS | 低 | 已覆盖/否决 | 跳过 | 自动 factor/alpha 工厂与剩余实验命纪律冲突 |
| NautilusTrader event log/parity | OSS_BUILD_VS_BUY; PEER_PROJECTS; V5 v2; D38 | 中 | 已覆盖 | Phase2 | 事件驱动和 replay 是 Phase 2 架构闸，1个月内不迁移 |
| Triple Barrier Method | V5 v1/v2; D38; TOOLS_KNOWLEDGE | 中 | 部分 | Phase2 | v2 明确 carry/套利退出由机制失效决定；不作为 carry 默认退出 |
| Purged/Embargo CV | V5 v2; TOOLS_KNOWLEDGE | 中 | 部分 | Phase2 | 调参/重叠标签时启用；当前 carry固定验收先不扩范围 |
| Event-based sampling/CUSUM | V5 v2 | 低-中 | 部分 | Phase2 | 新 funding 信号可评估；当前不打断 FEASIBILITY |
| Data contract/schema validation | AI_CAPABILITY_OPTIMIZATION; OSS_BUILD_VS_BUY; FRONTIER_AI_OPC | 高 | 部分 | 立即用 | carry 数据字段复杂，schema/UTC/hash 是上实盘前置 |
| Result schema / LEAN ResultHandler | PEER_PROJECTS; FRONTIER_AI_OPC | 中 | 遗漏 | 立即用 | 统一报告与运行结果字段，便于 Claude 验收和 TASK_INBOX intake |
| QuantConnect LEAN | PEER_PROJECTS | 低 | 遗漏 | 跳过 | 完整平台过重；只借鉴模块边界 |
| OpenBB dashboard | PEER_PROJECTS | 低 | 遗漏 | Phase2 | 做研究状态页可用，不做数据权威或交易内核 |
| Backtrader / vn.py | EXTERNAL_RESEARCH_REPORT_v1; V5 v2 | 低 | 已覆盖 | 跳过 | 后续文件已明确不采纳；当前 vectorbt/Freqtrade 足够 |
| CoinGlass/CoinAPI/Kaiko/Amberdata | OSS_BUILD_VS_BUY; AI_CAPABILITY_TOOLING_AUDIT | 中 | 冲突 | 跳过 | 付费或机构数据；本任务禁止建议付费工具 |
| CoinDesk/LunarCrush/Exa | AI_CAPABILITY_TOOLING_AUDIT | 低 | 已覆盖/部分 | 跳过 | 非 carry 实盘关键路径；社交/现货/搜索不解决当前瓶颈 |
| Binance/CCXT交易MCP | OSS_BUILD_VS_BUY; AI_CAPABILITY_OPTIMIZATION | 中 | 已覆盖 | 跳过 | MCP 不进交易闭环；尤其不能持交易 key |
| binance-pro/ClawHub交易skill | D38; V5 v2 | 中 | 已覆盖 | 跳过 | 交易权限、供应链恶意 skill 风险、阶段不匹配 |
| research-harvest Skill | TOOLS_KNOWLEDGE | 中 | 遗漏 | 立即用 | Claude侧已建但当前 Codex 未暴露；需修技能可见性/路由 |

## 对TOOLS_KNOWLEDGE.md的更新建议

建议新增或修订以下条目，由 Claude 验收后写入：

1. **Hummingbot Funding Rate Arbitrage**：状态为“Phase2源码审计候选”。说明：已知 Hummingbot 生态存在 funding arbitrage 原型，但当前文件未提取 entry/exit/对冲参数；Phase 1 不接执行，不给 MCP 交易权限。
2. **Jesse Monte Carlo**：从“待评估”升级为“立即自实现方法”。说明：不引 Jesse 框架，只实现路径重排/交易顺序打乱/block bootstrap，服务 carry 爆仓概率与路径风险。
3. **Qlib Recorder**：从“待决策”升级为“立即自实现轻量 experiment registry”。字段建议：`task_id/hypothesis/data_hash/code_hash/config_hash/seed/metrics/decision/report_path`。
4. **Freqtrade lookahead-analysis**：保持高优先级，并补充“若策略不在 Freqtrade 内运行，必须做等效 slice recompute”。
5. **research-harvest 可见性缺口**：TOOLS_KNOWLEDGE 说 `.claude/skills/research-harvest` 已建，但当前 Codex 技能列表不可用；需要明确它是 Claude skill 还是 Codex skill，避免任务书指定后无法执行。
6. **付费数据商口径**：CoinGlass/CoinAPI/Kaiko/Amberdata 在免费工具链任务中默认跳过；只有 Founder D级批准预算后才可重启评估。

## 与DEC-076的冲突或补充

**无硬冲突。** DEC-076 的 Freqtrade + CCXT + data.binance.vision 最小借力闭环仍是当前最优路线。

补充点：

1. `PEER_PROJECTS_BENCHMARK` 的 Hummingbot Funding Rate Arbitrage 是 DEC-076/TOOLS_KNOWLEDGE 未充分吸收的 carry OSS 原型，但只够登记，不够直接采用。
2. `Jesse Monte Carlo` 与 `Qlib Recorder` 是低成本遗漏项，能加强 carry 验收和审计，不改变主线工具栈。
3. `V5_TOOL_INTEGRATION_PLAN_v1/v2` 中“Freqtrade Phase 2 参考”的旧口径已被 DEC-076 覆盖；本报告按 DEC-076 将 Freqtrade 作为 Phase 1 dry-run/live 地基。
4. `OSS_BUILD_VS_BUY` 曾列 CoinGlass 小套餐；本任务禁止建议付费工具，故本报告把 CoinGlass 类数据商列为跳过。
5. `V5_TOOL_INTEGRATION_PLAN_v2` 明确 carry/套利类退出由机制失效条件决定，补充了“不要把 Triple Barrier 机械套到 carry”的边界。

## 建议下一步

1. **建立 carry → Freqtrade dry-run 最小适配任务**：只做一个已通过研究验收的 carry 信号模板、Binance futures dry-run 配置、DB落盘、只读/交易 key 分离、每日对账字段清单；禁止 Hyperopt。
2. **补 carry 上实盘前验证闸**：实现等效 `lookahead/slice_check`、数据契约校验、Jesse式 Monte Carlo/block bootstrap、固定 seed 爆仓概率输出。
3. **发 Hummingbot Funding Rate Arbitrage 只读源码审计任务**：仅提取 entry/exit/对冲/再平衡/风险状态机；不安装、不运行、不接 API key；审计后决定是否把参数设计折入 Phase 2。

