# Community Strategy Research Workflow

用途：把社区里的交易策略、GitHub 项目、论坛帖子、小红书/B站内容转成 AI Quant Company 可审计的候选研究假设。

## 一句话触发

```text
按 community_strategy_research_workflow 跑：搜索社区策略，抽取策略逻辑，按项目研究纪律筛选，只输出可验证候选假设。
```

## 默认输入

可接受任一输入：

- GitHub 仓库链接
- 小红书/B站/网页链接
- 搜索关键词，例如 `hyperliquid market making strategy`
- 社区来源范围，例如 `GitHub + Reddit + 小红书`

## 默认输出目录

```text
06_RESEARCH/CODE/output/community_strategy_research/<UTC_TIMESTAMP>/
```

## 输出文件

- `SOURCES.md`：来源清单、链接、基础元数据、是否可访问
- `CANDIDATES.json`：候选策略结构化列表
- `STRATEGY_BRIEFS.md`：每个策略的人类可读摘要
- `SCREENING.md`：按项目研究纪律筛选结果
- `NEXT_TASKS.md`：建议拆出的正式研究任务

## 候选策略字段

```json
{
  "source_url": "",
  "source_type": "github|web|xhs|twitter|reddit|bilibili|rss|other",
  "strategy_name": "",
  "asset_universe": "",
  "market": "spot|perp|futures|options|unknown",
  "timeframe": "",
  "strategy_family": "trend|mean_reversion|breakout|market_making|grid|factor|event|ml|other",
  "entry_logic": "",
  "exit_logic": "",
  "stop_loss": "",
  "take_profit": "",
  "position_sizing": "",
  "leverage_or_margin": "",
  "add_position_rules": "",
  "risk_controls": "",
  "data_requirements": "",
  "cost_assumptions_seen": "",
  "backtest_claims_seen": "",
  "implementation_language": "",
  "license": "",
  "red_flags": [],
  "project_usefulness": "high|medium|low|reject",
  "recommended_next_step": ""
}
```

## 筛选规则

直接拒绝：

- 读 holdout 或要求读取封存数据
- 全样本分位、全样本阈值
- 未计手续费/滑点/funding
- 只给收益截图，无可复跑逻辑
- 黑箱依赖，不可审计
- 策略目标是刷量、返佣、规避交易所限制

进入人工复核：

- 规则描述清楚但参数多
- 形态识别主观，需要机械化定义
- 涉及 LLM 自动决策
- 依赖链上/订单流/社媒数据，需要确认数据源可得

可进入正式任务书：

- 机制明确
- 单变量可拆
- 输入数据可得
- 成本可完整建模
- 可定义入场、出场、止损、仓位
- 可按 v1.3 验收标准验证

## 评分表

| 维度 | 0 分 | 1 分 | 2 分 |
|---|---|---|---|
| 机制清晰度 | 看不懂为何有效 | 有直觉但边界模糊 | 可写成明确机制 |
| 可执行性 | 只讲概念 | 需要大量人工解释 | 可机械化实现 |
| 数据可得性 | 数据不可得 | 数据可得但成本高 | 项目已有或容易获取 |
| 成本完整性 | 未提成本 | 成本可补 | 已能完整建模 |
| 前视风险 | 明显前视 | 需人工检查 | 可避免前视 |
| 风控完整性 | 无风控 | 有止损但不完整 | 仓位/止损/熔断清楚 |
| 研究价值 | 与项目无关 | 可做参考 | 可立研究任务 |

建议：

- 总分 11-14：可进入任务书草案
- 总分 7-10：保留为候选，先补定义
- 总分 0-6：拒绝或仅作背景资料

## 推荐 agent 分工

- 搜索 agent：只负责找来源和元数据
- 逻辑 agent：只负责抽取策略规则
- 风险 agent：只负责找前视、成本、黑箱、合规风险
- 研究 agent：只负责把通过筛选的候选改写成可验证任务书

## 注意

该流程只生成候选假设，不证明策略有效。任何策略进入项目研究前，必须由 Claude 给出正式任务书并预登记验收标准。
