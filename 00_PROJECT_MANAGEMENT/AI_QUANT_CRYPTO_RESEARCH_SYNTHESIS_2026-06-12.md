# 量化策略 / AI量化 / 加密合约策略 / 加密投研综合调研

**日期：** 2026-06-12  
**定位：** 对前序审计和能力调研的策略研究补强；服务于剩余 2 条独立 Alpha 命的机会地图重排。  
**边界：** 只读公开资料与项目已有报告；未运行实验/回测；未读取 Holdout；未审计不可公开访问的 GitHub 仓库代码。  
**证据等级：** A=同行评审/官方文档/交易所 API；B=arXiv/工作论文/高质量开源文档；C=博客/行业文章/经验线索；D=不可访问或未核验。

## 执行摘要

1. **AI 量化最危险的错觉是把 LLM 产生的策略叙事当成 alpha 证据。** arXiv:2605.16895 明确提出：端到端 LLM trading agent 的 reported alpha 不应被视为可部署证据。
2. 对本项目，AI 应定位为研究放大器：资料抽取、假设生成、代码实现、反方审计、报告生成；最终交易信号、仓位和风险不能由未校准 LLM 直接决定。
3. 加密永续文献支持一个关键重评：funding/open interest 是市场状态变量，不天然指向反转。A-2 首测“极端拥挤=延续”并不意外。
4. 当前机会地图应从“拥挤反转”重排为：TSMOM/regime baseline；A-1 强制流/清算级联两相位；A-4 新上市/新永续错位；carry/funding/OI 作为状态与成本模块。
5. 剩余 2 条独立 Alpha 命不能让 agent 自动探索消耗；第 7 命只应在 A-1 数据门通过后使用，第 8 命保留给独立机制，默认 A-4 或后续新候选。
6. 任何 AI 生成策略进入研究队列前，应新增 `AI_ALPHA_EVIDENCE` 小节，显式回答 P1-P6：时序完整、动态 universe、反事实稳健、校准、真实摩擦、多 agent 分解。

## 资料索引

| 来源 | 主题 | 等级 | 本项目用法 |
|---|---|---:|---|
| The Alpha Illusion, arXiv:2605.16895 | LLM trading agent reported alpha 证据不足 | B | AI Alpha Evidence Gate |
| GitHub `hj1650782738/Trading` | 论文声称复现 harness | D | 当前 404，不作为代码证据 |
| Fundamentals of Perpetual Futures, arXiv:2212.06888 | 永续合约定价、funding、套利边界 | B | funding 是锚定机制/状态变量 |
| Reconciling Open Interest with Traded Volume in Perpetual Swaps, Ledger/arXiv:2310.14973 | OI/强平数据质量与交易所误报风险 | A/B | A-1/OI 数据必须打质量标签 |
| BIS Working Paper 1087 / Crypto carry | crypto carry / futures-spot 基差 | A/B | carry 是基准/状态/低杠杆候选 |
| Risk Premia in the Bitcoin Market, arXiv:2410.15195 | BTC 风险溢价、波动状态 | B | regime/volatility 应进入状态分层 |
| Freqtrade / Jesse / Nautilus / Qlib / RD-Agent / Hummingbot 文档 | 同类项目工程实践 | A/B | 无前视、实验记录器、事件日志、AI harness |
| Binance USD-M Futures API | funding/OI/强平流可得性 | A-Data | 采集器和数据契约 |

## 一、AI量化：从“端到端 agent”退回“模块化证据链”

### 1. LLM trading agent 的 alpha 幻觉

`The Alpha Illusion` 的核心不是“LLM 不能做金融”，而是“reported alpha 不能直接当部署证据”。论文把端到端 LLM 交易系统的问题拆成两类：

| 类型 | 风险 | 项目映射 |
|---|---|---|
| 证据来源污染 | pretraining/retrieval/memory 偷看未来、幸存者样本、短窗口搜索 | 项目必须继续坚持 Holdout 封存、point-in-time、墓园 |
| 证据到决策映射污染 | 语言信心不是概率、毛收益不是净收益、多 agent 共识不是独立专家 | AI 不能控制 sizing；多 agent 要有分歧率和单 agent baseline |

**对项目的硬要求：**

```text
AI-generated alpha = hypothesis only
AI-generated code/report = implementation artifact only
AI-generated confidence = no sizing authority
AI multi-agent consensus = not independent evidence unless disaggregated
```

### 2. P1-P6 映射为本项目 AI Alpha Evidence Gate

| Gate | 本项目必须记录 |
|---|---|
| P1 Temporal integrity | 模型版本、知识截止、外部资料时间戳、数据窗口、是否 post-cutoff |
| P2 Dynamic universe | 当时可交易 universe、上市/下架、流动性、交易规则、是否幸存者偏差 |
| P3 Counterfactual robustness | 反向证据、方向翻转、参数扰动、风格/行业/币种中性化 |
| P4 Epistemic calibration | 若有概率/置信度，必须 ECE/可靠性曲线/样本外校准；否则不得用于仓位 |
| P5 Realistic implementation | 价差、手续费、滑点、冲击、延迟、funding、token/API 成本 |
| P6 Multi-agent disaggregation | 单 agent baseline、分歧率、角色相似度、协调成本、净收益增量 |

### 3. AI 在量化研究里的正确角色

| 阶段 | AI 可以做 | AI 不该做 |
|---|---|---|
| 机会发现 | 文献归纳、机制假设、反方清单、数据源盘点 | 直接宣布 alpha 存在 |
| 数据工程 | 写采集器、hash、schema、数据质量检查 | 根据全样本结果挑窗口 |
| 实验实现 | 写预登记实现、测试、无前视检查 | 改预登记门槛适配结果 |
| 结果解释 | 汇总证据、找矛盾、生成墓园标签 | 把事后发现包装成新先验 |
| 风控 | 构造风险清单、爆仓路径、成本瀑布 | 用语言置信度定杠杆 |
| 生产 | 做日志解释、异常摘要、operator copilot | 持有交易密钥或自动放大仓位 |

## 二、加密永续策略机会地图

### 1. TSMOM / regime continuation

**证据状态：** 本项目内部 TSMOM 新口径复读四件套已过；A-2 方向相反也支持“极端状态可能延续”。外部上，时间序列动量在传统多资产有深厚文献基础，加密市场需重新验证，但它是当前最强内部候选。

**策略含义：**

- TSMOM 应升级为 baseline，不再只是“旧主线复读”。
- 不能因 “不是新机制” 就低估它；对 30k 小资金而言，低复杂度、可控容量、低数据要求本身是优势。
- 只能低杠杆表达；项目内已显示 2x 爆仓概率过高。

**下一步不耗命：**

- 扩多币种/更新数据/成本敏感性；
- regime 分层：高/低波动、funding 符号、OI 变化、趋势强度；
- 不碰 Holdout。

### 2. Funding / carry / basis

**外部证据：** 永续合约论文显示 funding 是 tether perpetual to spot 的机制，偏离会受套利边界和交易成本约束；crypto carry 文献表明基差/期货-现货 carry 可形成风险溢价，但不是无风险午餐。

**项目重评：**

| 旧理解 | 新理解 |
|---|---|
| 极端 funding = 拥挤后反转 | 极端 funding = 拥挤状态，方向依赖趋势/流动性/清算相位 |
| funding 可直接做方向信号 | funding 更适合作为状态变量、成本变量、carry 候选 |
| A-2 失败是单实验失败 | A-2 反转机制被实证重击，不应继续派生 |

**建议：**

- funding 作为 TSMOM/A-1 的状态分层；
- carry 可做低杠杆基准候选，但要计算资金费、基差、交易成本、交易所风险；
- 不再把 “funding 极端反向” 作为独立主线。

### 3. Open interest / liquidation / forced flow

**外部证据：** OI 文献指出一些大型衍生品交易所的 OI 报价存在系统性不一致，甚至强平消息可能延迟。这对 A-1 是直接警告：OI/强平不是干净真相。

**A-1 必须拆成两相位：**

| 相位 | 机制 | 观察窗口 | 数据要求 |
|---|---|---|---|
| 级联进行中 | 强制卖/买推动趋势延续 | 分钟到数小时 | 1m/5m price, volume, OI delta, liquidation stream |
| 级联耗竭后 | 强平压力释放后反弹/均值回归 | 数小时到数日 | 强平密度衰减、深度恢复、价格不再创新低/高 |

**A-1 数据门：**

- 不可只用 1H mark price + 5m OI 代理直接消耗第 7 命；
- 必须有数据质量标签：exchange, symbol, timestamp, delay, missingness, forced-trade coverage；
- 若历史强平数据不完整，则只能做“状态收益研究”，不能宣称“清算级联可交易 edge”。

### 4. New listings / new perpetuals / market structure gaps

**为何适合小资金：**

- 机构覆盖少，容量小，30k 资金劣势较小；
- 新上市/新永续的 funding、OI、流动性、做市结构有过渡期；
- 数据事件边界清晰，便于预登记和墓园管理。

**主要风险：**

- 数据可得性差；
- 手续费/滑点/风控限制高；
- 样本数量可能少，容易过拟合；
- 上市公告和可交易时间需 point-in-time。

**建议：** 作为第 8 命默认候选之一，但先做不耗命的数据可行性普查。

### 5. Volatility / VRP / options-informed regime

BTC 风险溢价文献显示风险溢价与波动状态相关，低/高波动 regime 的收益分解不同。项目当前不应直接做期权 VRP 主线，但应该把波动 regime 作为所有方向的状态维度。

**建议：**

- TSMOM：按 realized vol 分层；
- A-1：按事件前 vol 和 intraday range 分层；
- funding/carry：按 vol regime 评估爆仓和资金费持续性。

### 6. Cross-exchange/stat-arb/market making

这类策略理论上适合小 alpha，但当前不适合作为 Phase 1 主线：

| 原因 | 解释 |
|---|---|
| 工程先行 | 需要低延迟、交易所连接、对账、风险控制 |
| 资金分散 | 小资金跨所效率低，提现/风控/稳定币风险复杂 |
| 运维重 | Founder 1h/天不适合先上 |

可作为 Phase 2/3 架构参考，不消耗剩余 2 命。

## 三、量化投研方法重评

### 1. 机会地图的新排序

| 排名 | 方向 | 状态 | 理由 |
|---:|---|---|---|
| 1 | TSMOM/regime baseline | Baseline candidate | 当前唯一较强内部正证据，复杂度低 |
| 2 | A-1 forced-flow two-phase | Conditional candidate | 机制合理但数据门未过 |
| 3 | A-4 new listing/new perp | Candidate | 小资金友好，独立于拥挤反转 |
| 4 | carry/funding/basis | Benchmark/state/sleeve | 外部证据存在，但收益/风险/容量要谨慎 |
| 5 | LLM sentiment/news agent | Research feature only | 只能作上游特征，不作端到端交易 agent |
| Dead | A-2 funding extreme reversal | Dead | 内部首测方向相反，不得派生复活 |

### 2. “机制优先”范式哪里对，哪里错

**对的：**

- 不从指标形态出发，而从交易者行为/市场微结构出发；
- 先做小样本事件研究，不急于上实盘；
- 失败进墓园，防止反复复活。

**错的：**

- 对 A-2 的机制审查没有先问：为什么拥挤一定反转而不是延续？
- 对 funding/OI 的变量角色定义不清，把状态变量当因果方向变量；
- 没有把内部 TSMOM 正证据作为机制先验冲突项写进 A-2 预登记；
- 对 AI 生成/整理的策略叙事缺少独立 evidence gate。

### 3. 剩余 2 条独立 Alpha 命的使用原则

1. 不因“已经投入很多文档”而给 A-1 自动排队。
2. 不因“TSMOM 是旧线”而忽略它；TSMOM 扩样本不耗新命。
3. 第 7 命只给通过数据门的 A-1 两相位研究。
4. 第 8 命保留，默认给 A-4 或一个与 funding/OI 叙事独立的新机制。
5. AI agent 不得自主触发耗命实验。

## 四、对 Research Protocol 的建议增补

新增 `AI_ALPHA_EVIDENCE` 小节模板：

```markdown
## AI_ALPHA_EVIDENCE

- 是否由 AI 生成假设/代码/特征/结论：
- 模型与工具版本：
- 外部资料时间戳与知识截止：
- P1 Temporal integrity：
- P2 Dynamic universe：
- P3 Counterfactual robustness：
- P4 Calibration：
- P5 Realistic implementation：
- P6 Multi-agent disaggregation：
- 结论声明强度：
  - [ ] research aid
  - [ ] historical prototype
  - [ ] deployable alpha claim
  - [ ] autonomous trading claim
- 本报告允许使用的语言：
```

新增 `CRYPTO_PERP_DATA_QUALITY` 小节模板：

```markdown
## CRYPTO_PERP_DATA_QUALITY

- exchange / market / contract type：
- price grain：
- volume grain：
- funding source and timestamp convention：
- OI source and timestamp convention：
- liquidation source and known throttling/delay：
- survivorship/listing filter：
- missingness / latency / duplicate policy：
- no-lookahead tests：
```

## 五、最终主张

本项目不该追逐“AI 自动交易系统”叙事，而应建设“AI-native quant research OS”：AI 负责把研究流程变快、变可复核、变有反方；Alpha 仍必须来自市场机制、数据证据、成本后收益和风险可承受性。

若用一句话改写机会地图：**用 TSMOM 做可验证基线，用 A-1 数据门寻找强制流 edge，用 A-4 保留独立小资金机会，用 funding/OI 做状态变量，用 AI 做审计加速器而不是 alpha 发生器。**
