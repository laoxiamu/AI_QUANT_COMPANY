# 社区策略工具与两个 GitHub 项目评估

整理时间：2026-06-22

## 结论先行

两个项目对我们都有帮助，但帮助点完全不同：

- `dennisyang1986/opensqt_market_maker`：更像实盘执行/做市/网格系统。可借鉴交易所抽象、订单生命周期、仓位槽位、对账、熔断风控；不应借鉴其单向做多网格作为 alpha。
- `HammerGPT/Hyper-Alpha-Arena`：更像完整 AI 交易平台。可借鉴产品形态、因子挖掘、Program Trader、归因诊断、多 agent 分工；不应直接信任其自动优化结果。
- 本地目前没有一个已经安装的“自动社区策略搜索-策略逻辑研究-策略优化”专用插件。最合适方案是做项目本地 workflow/skill，把已有 `agent-reach`、Chrome/GitHub 读取、并行 agent、回测框架串起来。

## GitHub 连接问题确认

用户本地浏览器可以访问 GitHub。经验证：

- 终端侧 `gh`、`curl`、`git ls-remote`、Jina Reader 访问 GitHub/Raw GitHub 均无有效返回或超时。
- Codex 内置浏览器访问 GitHub 超时。
- Chrome 扩展路线可以正常打开 `github.com` 仓库页面并读取 README/文件页。
- Chrome 访问 `raw.githubusercontent.com` 被拦截，页面显示 `ERR_BLOCKED_BY_CLIENT`。

判断：不是本机整体网络问题，而是 Codex 终端/内置浏览器链路没有复用你本地 Chrome 的可用网络环境；同时 raw 域名被 Chrome 侧扩展或策略拦截。后续 GitHub 调研应默认走 Chrome 的 GitHub 页面，不走 raw/gh/curl。

## 项目一：opensqt_market_maker

仓库：`dennisyang1986/opensqt_market_maker`

读取到的信息：

- Star 约 849，Fork 约 329。
- Go 项目，README 称其为毫秒级高频加密货币做市商系统。
- 策略核心：永续合约市场的单向做多网格/做市。
- 支持交易所：Binance、Bitget、Gate.io，Bybit/backpack beta，另有 EdgeX 配置。
- 模块结构包括：`exchange`、`monitor`、`order`、`position`、`safety`、`logger`、`config`。
- 配置里有 `price_interval`、`order_quantity`、`buy_window_size`、`sell_window_size`、`position_safety_check`、`reconcile_interval`、`risk_control`。
- `risk_monitor.go` 显示其主动风控会加载历史 K 线、订阅 K 线流，并基于监控币种检测市场异常。

### 对我们的帮助

可借鉴：

- 多交易所统一接口层：有助于我们未来拆 execution adapter。
- 订单生命周期管理：挂单、清理、重试、限流、退出撤单。
- 仓位槽位/Super Slot 思路：适合研究“订单状态权威”和“并发冲突防护”。
- 对账机制：本地状态与交易所状态定期同步，这和我们项目禁止以内存字典为最终权威一致。
- 主动风控/熔断：监控市场异常后暂停交易，可转成我们实盘风控闸门。

不建议借鉴：

- 单向做多无限网格作为 alpha。它本质上依赖震荡/上行环境，单边下跌时靠加仓摊成本，路径风险很重。
- “刷交易所 VIP/刷量神器”目标。这个目标和我们的研究/合规/真实 alpha 方向不一致。
- README 里的收益描述不能作为证据，没有看到完整成本、滑点、funding、爆仓概率、分年表现。

项目内定位：

- 作为 execution/risk engineering 参考，不作为 strategy alpha 来源。
- 若后续研究网格，只能作为一个反例/压力测试对象：重点看尾部亏损、保证金占用、资金费率、极端滑点。

## 项目二：Hyper-Alpha-Arena

仓库：`HammerGPT/Hyper-Alpha-Arena`

读取到的信息：

- Star 约 1.1k，Fork 约 268，Apache-2.0 license。
- Docker 部署，服务包含 Postgres 和 app，默认本地端口 `127.0.0.1:8802`。
- 支持 Hyperliquid 与 Binance Futures。
- README 声称包含 86 个内置因子、自定义表达式引擎、因子 IC/ICIR 评分、AI 因子挖掘、AI Trader、Program Trader、Attribution AI。
- 多 agent 分工：Hyper AI、Signal AI、Prompt AI、Program AI、Attribution AI。
- `.env.example` 包含 Hyperliquid 默认参数：最大杠杆 10、最小订单 10、单笔最大仓位价值 1000。
- `docker-compose.yml` 显示 `FACTOR_ENGINE_ENABLED=true`，并包含 backend 子目录：`backtest`、`factors`、`program_trader`、`services`、`repositories` 等。

### 对我们的帮助

可借鉴：

- 产品形态：把 AI 研究、因子挖掘、策略配置、回测、归因诊断放在一个平台里。
- 多 agent 分工：策略搜索、信号设计、代码生成、归因分析可以拆成不同角色。
- Program Trader 思路：固定规则策略用代码表达，AI 只辅助生成/调试，不直接凭感觉下单。
- 因子库和表达式引擎：对我们未来做策略假设库有参考价值。
- Attribution AI：策略失败诊断、按因子/触发类型/时间段归因，这部分很适合我们项目报告模板。

不建议直接采用：

- 自动交易/LLM 直接下单。对我们来说，LLM 可以辅助研究，不能直接成为未验证策略执行者。
- 其因子有效性评分不能直接采信。需要检查是否前视、是否全样本分位、是否封存 holdout、是否完整计入成本。
- 内置优化结果不能替代项目 v1.3 验收标准。
- 若接入外部平台，需要先审查数据口径、成本模型、交易所 funding、滑点、爆仓处理。

项目内定位：

- 可作为“社区策略搜索-因子挖掘-策略配置-归因诊断”产品参考。
- 不建议作为我们核心研究引擎的权威来源。
- 可考虑在隔离环境跑 demo，但输出只能作为灵感，不可直接进入生产策略。

## 是否有现成插件/工具

本地已安装能力：

- `agent-reach`：跨 GitHub、网页、社媒、RSS、小红书/B站等搜索与采集。
- `chrome/browser/playwright`：网页读取、GitHub 页面读取、截图、下载。
- `xiaohongshu`：小红书账号/笔记采集。
- `dispatching-parallel-agents`：并行分工做多源调研。
- `writing-skills` / `skill-creator`：可把稳定流程沉淀成 skill。

未发现：

- 本地没有专门的“自动社区策略搜索-逻辑研究-参数优化”量化策略 skill。
- 在线 `npx skills find` 在终端网络下没有有效返回，暂不能确认 skills.sh 生态中是否存在可用成品。

结论：可以用现有组件拼出流程，但需要我们自己定义项目内工作流，不能依赖一个黑箱优化器。

## 推荐建设：Community Strategy Research Workflow

目标：把外部社区策略变成可审计候选假设，而不是直接相信外部收益。

流程：

1. 策略搜索
   - 来源：GitHub、X/Twitter、Reddit、V2EX、小红书、B站、RSS/博客。
   - 输出：候选策略列表，包含 URL、来源、更新时间、star/fork、license、标的、周期、代码语言、策略类型。

2. 逻辑抽取
   - 固定抽取：入场、离场、止损、止盈、仓位、加仓、过滤器、成本假设、数据周期。
   - 输出：`strategy_logic.json` 与 `strategy_brief.md`。

3. 研究纪律筛选
   - 自动拒绝：无成本模型、全样本分位、读未来、读 holdout、黑箱不可审计依赖、只展示收益图。
   - 输出：`accepted` / `rejected` / `needs_manual_review`。

4. 可执行改写
   - 把外部逻辑改写成我们自己的小函数。
   - Triple Barrier、Purged CV、统计检验等仍按项目规则自实现，外部库仅参考。

5. 验证与优化
   - 单变量原则。
   - 参数阈值滚动/扩张计算。
   - WF 硬门槛。
   - 成本完整：手续费、滑点、真实 funding，事件策略加滑点压力档。
   - 验收按 v1.3 四件套。

6. 输出
   - CODE：可复跑脚本 + 固定 seed。
   - RESULTS：结论 md。
   - CODEX_TASKS：执行报告，逐条验收自检。

## 优先级建议

1. 先不要把 OpenSQT 或 Hyper Alpha Arena 直接引入项目代码。
2. 先把 Hyper Alpha Arena 的 workflow 思路拆出来：因子挖掘、Program Trader、Attribution AI。
3. 把 OpenSQT 的 execution/risk 组件列为工程参考：exchange adapter、order reconciler、risk monitor、slot manager。
4. 立一个内部小任务：实现 `community_strategy_research_workflow` 的模板和评分表。
5. 真正跑策略优化前，必须先由 Claude 出任务书，明确机制、样本、成本、验收标准。

## 专业异议

不建议把“自动策略优化工具”作为短期目标直接接入生产。原因是这类工具天然容易过拟合、偷看未来、忽略成本，且与项目 Research Protocol v1.3 的要求冲突风险很高。更稳妥的路线是：先做“自动发现与结构化”，再做“人工批准的预登记验证”，最后才谈优化。
