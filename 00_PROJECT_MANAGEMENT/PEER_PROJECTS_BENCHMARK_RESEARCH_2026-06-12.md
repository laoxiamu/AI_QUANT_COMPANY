# 同类型优质项目调研：AI 量化研究/交易系统对标

**日期：** 2026-06-12  
**目的：** 为 AI Quant Company 找到可借鉴的优秀项目形态，明确“学什么、暂不学什么、不要照搬什么”。  
**范围：** 开源/公开文档项目，覆盖加密交易 bot、交易引擎、AI 量化研究平台、研究工作台。  
**结论口径：** 本项目当前仍是 Phase 1 研究期，不应直接复制实盘系统；优先复制研究纪律、数据契约、回测-实盘一致性设计和控制面。

## 结论摘要

1. **最值得学的不是某个策略库，而是四种工程能力：无前视检查、实验记录器、数据层契约、backtest-to-live parity。**
2. Freqtrade/Jesse 适合学习“个人友好的 crypto bot 工作流”，但它们的 hyperopt/AI optimize 容易诱导过拟合。
3. Hummingbot 适合学习“交易连接器 + 控制面 + AI/MCP 接口”，但市场做市不是本项目当前主线。
4. NautilusTrader 是未来 Phase 2/3 的最好架构参照：事件驱动、durable event log、backtest/sandbox/live 同核；但现在引入太重。
5. QuantConnect LEAN 的模块化 datafeed/result handler/portfolio modeling 值得学，整套引擎不适合 30k 小资金研究期。
6. Qlib 值得学习“实验 recorder、workflow、数据层、任务管理”，但它偏股票/ML 因子，不能直接搬到 crypto 永续事件研究。
7. RD-Agent 值得学习 R/D 分工、trace/eval 和自动实验循环，但不能让 agent 自主消耗独立 Alpha 命。
8. OpenBB 适合做外部市场研究和 dashboard，不适合做交易系统内核。

## 对标项目总览

| 项目 | 类型 | 对本项目价值 | 现在是否采用 |
|---|---|---|---|
| Freqtrade | Python crypto trading bot | dry-run、backtest、lookahead-analysis、WebUI/Telegram 控制 | 学纪律，不引整套 |
| Jesse | Python crypto trading framework | 简单策略语法、无前视、多品种多周期、Monte Carlo、MCP | 学研究 UX，暂不接执行 |
| Hummingbot | Crypto market making/agent framework | 连接器、Gateway/API、MCP/Skills、控制面 | 学架构，Phase 2 再评估 |
| NautilusTrader | 生产级事件驱动交易引擎 | backtest/sandbox/live 同核、事件日志、ports/adapters | Phase 2/3 架构参照 |
| QuantConnect LEAN | 多资产算法交易引擎 | datafeed/result handler/portfolio 模型、云/本地生态 | 学模块边界，不引整套 |
| Qlib | AI quant research platform | 数据层、workflow、experiment recorder、PIT/缓存 | 学研究 OS，不搬模型 |
| OpenBB | 投资研究工作台 | 外部数据/研究展示/看板 | 可作为 research UI 参考 |
| RD-Agent | R&D/Quant multi-agent | R/D 分工、自动实验 loop、trace/eval | 学流程，不给自主花命 |

## 项目详解

### 1. Freqtrade

**项目定位：** 免费开源 Python crypto trading bot，支持主流交易所，包含数据下载、回测、参数优化、dry-run/live、Telegram/WebUI 控制、资金管理等。官方明确建议先 dry-run，不要在理解预期盈亏前真钱交易。来源：[Freqtrade docs](https://www.freqtrade.io/en/stable/)。

**可借鉴：**

1. **Lookahead analysis。** Freqtrade 专门提供 lookahead bias 检测命令，通过基准回测与切片回测对比指标/信号差异来发现前视偏差；这与本项目“无前视纪律”高度一致。来源：[Freqtrade lookahead-analysis](https://docs.freqtrade.io/en/stable/lookahead-analysis/)。
2. **Dry-run/live 分离。** 适合本项目 R4 小额前的仿真层。
3. **控制面。** Telegram/WebUI 的 start/stop/status 思路适合 Founder 1h/天。
4. **交易所支持。** Futures 支持 Binance/Bybit/OKX/Gate/Hyperliquid 等，可作为后续交易所兼容性参考。

**不要照搬：**

1. Hyperopt 很容易把本项目重新拉回“找信号→调参数→回测”的旧病。
2. Freqtrade 策略语法更适合 candle 策略，不适合 A-1 分钟级事件微结构。
3. 不要在 Phase 1 把它作为实盘执行内核；现在只学无前视检测和控制面。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| 自研 `lookahead_check.py`，对研究脚本检测全样本统计、shift/rolling 错误 | P1 |
| 在 Research Protocol 增加“切片复算”作为前视偏差测试候选 | P1 |
| R4 前设计 Founder 控制面：status/stop/daily report | P2 |

### 2. Jesse

**项目定位：** Python crypto trading framework，强调 self-hosted/privacy-first、简单语法、多周期多品种、无前视、风险管理、debug、优化、期货/做空、Monte Carlo、MCP。来源：[Jesse docs](https://docs.jesse.trade/)。

**可借鉴：**

1. **研究 UX。** 策略表达要简洁，减少 Founder/AI 之间的翻译成本。
2. **Monte Carlo。** 用 trade-order shuffling 与 candle simulation 做稳健性评估，适合四件套中的爆仓概率/路径风险。
3. **Rule significance testing。** 在完整回测前先测试 entry 规则是否显著，类似本项目 R2 机制验证。
4. **Jesse MCP 思路。** AI 通过 MCP 读取策略、回测、数据和设置，适合未来 Phase 2 的本地控制。

**不要照搬：**

1. “Optimize Mode / AI fine-tune”对当前剩余 2 命是危险诱惑。
2. Jesse 是交易框架，不是研究 governance 系统；不能替代预登记和墓园。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| 在结果报告中加入 Monte Carlo/路径重排作为策略化后的稳健性模块 | P1/R3 |
| 参考 Jesse MCP，为未来本地交易系统暴露只读状态资源 | P2 |
| 不使用 Optimize Mode 风格的自动调参 | 禁 |

### 3. Hummingbot

**项目定位：** 开源 Python crypto market making framework，可在 CEX/DEX 运行自动交易策略。生态包含 Client、Gateway、API、Condor、MCP、Skills、Quants Lab 等。来源：[Hummingbot](https://hummingbot.org/)。

**可借鉴：**

1. **组件化生态。** Client/Gateway/API/控制面/MCP 分层清楚，适合本项目 Phase 2 设计。
2. **AI 接口方向。** Hummingbot MCP 让 Claude/Gemini 调用 Hummingbot API；Hummingbot Skills 用于部署 bot、找套利机会、查状态。这是“交易系统暴露给 AI”的成熟形态，但必须只读/仿真先行。
3. **连接器资产。** 多交易所连接器、Gateway/DEX 思路可作为未来执行层参考。
4. **社区策略例子。** 官方页面列出 Binance Futures Liquidation Sniper、Funding Rate Arbitrage 等，说明本项目关注的 A-1/funding 方向在生态中有实践原型。

**不要照搬：**

1. Market making 与当前“机制验证 + 小资金方向性/事件 edge”不是同一阶段。
2. Hummingbot 连接器复杂度高，过早引入会变成系统建设先行。
3. MCP 不能给交易权限；最多先给只读状态和仿真控制。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| Phase 2 架构参考 Hummingbot 的 API/control-plane 分层 | P2 |
| 前向 collector 可参考多交易所连接器思路 | P1 |
| 不在 Phase 1 接 Hummingbot 执行 | 禁 |

### 4. NautilusTrader

**项目定位：** 高性能、生产级、开源交易引擎；Rust core + Python edge；多资产多场所；核心卖点是 backtest/live 同核、确定性事件驱动、nanosecond clock、durable event log、message bus、portfolio、actors。来源：[NautilusTrader](https://nautilustrader.io/) 与 [Nautilus overview](https://nautilustrader.io/docs/latest/concepts/overview/)。

**可借鉴：**

1. **Backtest/sandbox/live parity。** 本项目 Phase 2 必须避免“研究脚本一套、实盘系统另一套”的 V4 风险。
2. **事件日志。** 每个市场数据、信号、订单、成交、风控事件都可 replay，是审计和 debug 的核心。
3. **Ports and adapters。** 数据源、交易所、策略、风控解耦。
4. **确定性 replay。** 对 A-1 这类事件策略尤其重要。

**不要照搬：**

1. 当前资金和阶段不适合上生产级交易引擎。
2. Nautilus 的复杂度会消耗研究注意力。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| R1 数据层开始记录 event log 概念：event_id、event_time、source、hash | P1 |
| Phase 2 系统蓝图以 backtest/sandbox/live 同核为硬要求 | P2 |
| 不现在迁移到 Nautilus | 禁 |

### 5. QuantConnect LEAN

**项目定位：** 开源多资产算法交易引擎，支持本地/云，Python/C#，用于研究、回测、实盘。来源：[QuantConnect LEAN](https://www.quantconnect.com/docs/v2/lean-engine/getting-started)。

**可借鉴：**

1. **模块边界。** DataFeed、ResultHandler、Portfolio/Risk/Execution 等职责清晰。
2. **本地/云双形态。** 本项目未来可以本地研究 + 云端采集/执行。
3. **多资产 portfolio modeling。** 未来从单策略到组合时有参考价值。

**不要照搬：**

1. LEAN 是完整平台，非小资金研究期工具。
2. 数据源/经纪商生态偏传统多资产，crypto perp 微结构还需自建。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| Phase 2 设计采用 DataFeed / ResultHandler / Portfolio / Risk / Execution 命名边界 | P2 |
| 研究报告加入 ResultHandler 类似的标准输出契约 | P1 |
| 不引 LEAN 作为当前回测框架 | 禁 |

### 6. Qlib

**项目定位：** AI-oriented quantitative investment platform，覆盖数据层、workflow、forecast model、portfolio/backtest、experiment recorder、analysis、online serving 等。来源：[Qlib introduction](https://qlib.readthedocs.io/en/latest/introduction/introduction.html)。

**可借鉴：**

1. **Workflow / Recorder。** 每个实验有参数、指标、artifact、tag、record，正好补本项目“报告多、机器索引弱”的问题。
2. **Data layer。** DataServer/Feature/Cache/Dataset 的分层值得借鉴到 R1 data catalog。
3. **Task management。** 对多实验、多模型、多数据切片有结构化管理。
4. **PIT 数据意识。** 对无前视尤其重要。

**不要照搬：**

1. Qlib 偏股票和 ML 因子，不能直接套 crypto 永续事件研究。
2. 强 ML/RL 框架不适合剩余 2 命阶段。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| 建轻量 `experiment_registry.csv/json`：hypothesis、data_hash、code_hash、metrics、decision | P1 |
| 数据 catalog 采用 Qlib 式分层：raw / normalized / features / records | P1 |
| 不上 Qlib 框架本体 | 禁 |

### 7. RD-Agent

**项目定位：** Microsoft R&D-Agent 试图自动化数据和模型 R&D；RD-Agent(Q) 称为 data-centric multi-agent quant framework，强调 Research Agent / Development Agent 分工、trace/eval、factor-model co-optimization。来源：[RD-Agent GitHub](https://github.com/microsoft/RD-Agent)。

**可借鉴：**

1. **R/D 分工。** Research 提想法、Development 实现，与本项目 Claude/Codex 分工相似。
2. **Trace / eval。** 每轮自动实验必须有轨迹、评估和成本，适合本项目 Codex 直调记录。
3. **成本意识。** RD-Agent(Q) 强调低成本实验，符合项目预算约束。

**不要照搬：**

1. 自动 factor-model co-optimization 与本项目“剩 2 独立命”冲突。
2. 股票因子自动挖掘范式可能把项目带回猎因子，不符合 DEC-064 机制优先。
3. 不能让 agent 自主决定消耗独立 Alpha 命。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| Codex 直调记录加入 trace_id、prompt_hash、input_files、output_files、token_cost | P1 |
| 对每个 R/D 循环做 eval：是否提高信息增益，而非是否跑出正收益 | P1 |
| 禁止自动生成并测试新 Alpha 队列 | 禁 |

### 8. OpenBB

**项目定位：** 投资研究与数据平台/workspace，适合把多源金融数据和图表整合到研究工作台。来源：[OpenBB Workspace](https://www.openbb.co/products/platform)。

**可借鉴：**

1. Founder-facing dashboard 思路：研究状态、成本、候选机制、风险闸。
2. 外部市场/宏观/资产数据查询入口。
3. 报告和图表工作台体验。

**不要照搬：**

1. OpenBB 不是交易执行内核。
2. 外部数据多而杂，可能增加噪声和订阅成本。

**对本项目动作：**

| 动作 | 优先级 |
|---|---|
| 等 data catalog 稳定后，建 Founder 研究状态 dashboard | P2 |
| 外部研究需要时用 OpenBB/同类作为补充，不作为权威数据源 | P2 |

## 横向能力矩阵

| 能力 | 最佳参照 | 本项目现在怎么学 |
|---|---|---|
| 无前视检测 | Freqtrade | 自研 lookahead/slice check |
| 简洁策略 UX | Jesse | R3 策略 DSL 不要复杂 |
| 控制面 | Freqtrade/Hummingbot | Founder 日报 + 急停 + status |
| 连接器生态 | Hummingbot | Phase 2 参考，不现在接 |
| Backtest-live 同核 | NautilusTrader | Phase 2 硬要求 |
| 事件日志/replay | NautilusTrader | R1 开始记录 event_id/hash |
| 多资产引擎边界 | LEAN | 借鉴模块命名 |
| 实验管理 | Qlib | 轻量 experiment registry |
| AI R/D loop | RD-Agent | trace/eval，不自动花命 |
| Research dashboard | OpenBB | P2 可视化 |

## 对本项目的路线建议

### 现在立刻借鉴

1. **Freqtrade lookahead-analysis → 本项目 `lookahead_check.py`。**
2. **Qlib Recorder → 本项目 `experiment_registry`。**
3. **RD-Agent trace → Codex 直调报告增强。**
4. **Nautilus event log → R1 data catalog 加 event_id/hash。**

### R3/R4 前借鉴

1. Jesse Monte Carlo → 策略稳健性。
2. Freqtrade dry-run/WebUI 思路 → Founder 控制面。
3. Nautilus backtest/sandbox/live parity → Phase 2 架构闸。

### Phase 2 后再评估

1. Hummingbot connector/Gateway/API。
2. NautilusTrader 作为正式交易引擎候选。
3. Jesse/Hummingbot MCP 作为只读控制与仿真接口。
4. OpenBB dashboard 作为外部市场研究工作台。

## 不应该学的东西

1. **不要学 Freqtrade/Jesse 的快速优化诱惑。** 本项目剩余实验命稀缺，不能变成参数搜索。
2. **不要学 Hummingbot 的 market making 方向。** 它是另一类商业模式，不是当前主线。
3. **不要现在学 Nautilus/LEAN 的完整系统化。** 当前应继续证明 edge，不建重引擎。
4. **不要学 RD-Agent 的自动 Alpha 工厂。** 对本项目会放大过拟合与配额焦虑。
5. **不要把 OpenBB 当权威数据源。** 它适合展示和调研，不适合替代交易所原始数据。

## 建议落地包

### P0：不做会拖累研究质量

| 动作 | 借鉴对象 | 产物 |
|---|---|---|
| 建实验注册表 | Qlib Recorder | `06_RESEARCH/EXPERIMENT_REGISTRY.md/json` |
| 建前视偏差检查 | Freqtrade | `06_RESEARCH/CODE/tests/test_no_lookahead.py` |
| Codex trace 标准 | RD-Agent | CODEX report 新字段 |
| A-1 event_id/hash | Nautilus event log | data catalog schema |

### P1：本阶段可显著优化

| 动作 | 借鉴对象 | 产物 |
|---|---|---|
| Founder 研究状态页 | OpenBB/Freqtrade control | markdown 或 dashboard |
| Monte Carlo 路径稳健性 | Jesse | R3 验收模块 |
| backtest-live parity 设计 | Nautilus/LEAN | Phase 2 架构补丁 |
| 数据/结果标准输出 | LEAN ResultHandler | result schema |

### P2：观察与未来候选

| 动作 | 借鉴对象 | 产物 |
|---|---|---|
| 多交易所 connector 评估 | Hummingbot/Nautilus | Phase 2 技术调研 |
| 本地交易 MCP | Hummingbot/Jesse MCP | 只读/仿真优先 |
| 策略 DSL | Jesse | R3 后再设计 |
| 完整 engine 选型 | Nautilus/LEAN | Phase 2 L2 审计 |

## 最终判断

本项目已经在“研究治理”上超过大多数个人 crypto bot 项目，但在“机器可检索的实验注册、数据契约、前视检测、事件日志”上还不如成熟开源项目。正确路线不是迁移到某个框架，而是把这些成熟项目的关键机制拆出来，用最小实现嵌入当前 OS。

**一句话：** 现在学 Qlib/Freqtrade/RD-Agent 的研究纪律；R3 学 Jesse 的稳健性；Phase 2 学 Nautilus/LEAN/Hummingbot 的交易系统架构。

