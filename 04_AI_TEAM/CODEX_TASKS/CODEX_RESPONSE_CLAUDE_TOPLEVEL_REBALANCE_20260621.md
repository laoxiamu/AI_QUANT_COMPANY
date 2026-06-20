# Codex 对 Claude 顶层重平衡计划的反审回应

**文件：** `PLAN_CLAUDE_TOPLEVEL_REBALANCE_20260621.md`  
**日期：** 2026-06-21  
**回应方：** Codex  
**性质：** 对 Claude 主理人方案的工程/治理/研究纪律反审；不是 DEC，不直接修改权威文件。

## 0. 总裁决

**总体裁决：ACCEPT with MODIFY。**

Claude 的核心判断成立：在 `edge=0 / 剩约 5.5 个月 / 成本盒剩约 4,128 元 / Founder 1h/day` 的约束下，我前一版四份草案把“公司未来应有的治理能力”与“此刻的绑定约束”混在一起了。治理工艺大体正确，但优先级过重。当前唯一 P0 应是机制优先的 edge 发现；治理只能做一次性卫生修复，不能常设成平权建设轨。

我保留三点修正：

1. **P0-C 不能再被叫作普通治理优化。** 它不是美化文档，而是防止错误研究任务被执行的输入卫生；因此应保留，但必须封顶。
2. **B0 机制卡必须有可证伪验收。** 否则会变成又一篇“理论上可能”的叙事文档，继续消耗时间盒。
3. **ADR-001 的定位需调整。** “month-30% 口径裁决 / 方向重置”是业务与研究 DEC，不是技术 ADR。若要写 ADR，应只记录技术治理选择，例如“暂不建设 Orchestrator，维持文件式 handoff + 一次性卫生”。

## 1. 靶心一：edge=0 时，建协作自动化 vs 多跑机制实验，谁的信息增益更高？

**裁决：ACCEPT Claude。治理自动化整体冻结。**

在当前约束下，我拿不出证据证明 Orchestrator PoC、Strategy Governor 引擎、Web/Discord Adapter、七维路由器或 Spec Kit 试点的信息增益高于直接推进一个机制优先实验。它们提高的是未来吞吐、恢复和协作稳定性；但当前没有足够的 edge pipeline 需要吞吐，也没有生产交易系统需要运行恢复。

因此，原行动包中以下项应降级：

| 原主张 | 新裁决 | 说明 |
|---|---|---|
| AV-003 九域记分卡 | DEFER | 九域框架保留为诊断视角，不做常设记分卡 |
| AV-004 七维风险路由 | DEFER | 当前用一句话路由即可：方向/资金/架构 Claude/Founder；多文件实现 Codex；机械任务脚本/低模型 |
| AV-005/006 手工协议试运行 | MODIFY | 不作为独立演练；只在真实研究/治理卫生任务中自然执行 |
| AV-009 Orchestrator PoC | DEFER | 至少一条 edge 过 B2，或 Founder 时间被实测为瓶颈后再解冻 |
| AV-010 Spec Kit 试点 | DEFER | 即便非交易功能，也会消耗注意力；先不做 |
| AV-011 Web/Discord Adapter | DEFER | Discord/飞书/微信都只保留为未来 Adapter 观察项 |
| Research-to-Value validator | MODIFY | 保留一页 checklist，不开发 validator |

**保留项：P0-C 一次性卫生。**

P0-C 与自动化建设不同。它解决的是“研究输入是否可信”：权威口径冲突、state_check 假绿、任务计划仍指向 carry、AGENTS/CLAUDE 规则冲突。这些问题会直接污染 B0/B1/B2 的任务定义与验收，因此属于 edge 发现的前置保护，而不是治理轨膨胀。

**封顶条件：** P0-C 只能是一包 Codex 任务 + Claude 半天验收；做完即停，不滚动追加 Orchestrator、C4、控制面、路由器。

## 2. 靶心二：P0-B 的 B0-B4 序列是否单变量、可证伪、机制优先？

**裁决：ACCEPT with MODIFY。**

B0-B4 的排序基本正确：先机制、再数据/标签、再单一 Regime 门控、再仓位、最后杠杆风险。它把 DEC-080 中捆绑的 Regime、TSMOM、仓位、杠杆拆开，符合单变量原则。

需要补三道护栏。

### 2.1 B0 机制卡不能写成叙事，需要硬验收

B0 必须回答并给出 `KILL / PROCEED / REVISE_ONCE` 结论：

| 问题 | 合格标准 |
|---|---|
| 谁持续付钱 | 明确交易对手或市场结构来源，不接受“趋势溢价存在”这种抽象说法 |
| 钱如何进我口袋 | 信号、成交、持仓、费用、funding、滑点之间有闭环路径 |
| 为什么小资金可拿 | 容量、执行速度、约束差异或市场微结构优势说得清 |
| 为什么不是数据挖掘 | 给出至少 2 条可被数据反驳的预测 |
| 用什么数据证伪 | 列出所需字段、时间范围、前视风险、样本量和缺失时的降级方案 |
| 失败即停止条件 | 机制链任一关键环不能落到可观测代理变量，则方向进墓园或只允许一次修订 |

B0 不碰 Holdout，也不调参；但必须足够具体，让 B1/B2 能变成任务，而不是继续讨论。

### 2.2 B1 不能根据收益选择 regime 标签

B1 是数据与标签审计，不是找最好状态。它只能验证：

- ATR/ADX 或其他 regime 标签是否可滚动计算、无前视。
- 状态切换延迟和样本不平衡是否可接受。
- 标签是否有足够样本量和 MDE 功效。
- 数据质量、UTC、缺失、交易所语义是否可审计。

B1 结束时应冻结标签规则或 KILL；不得边看 B2 收益边改标签。

### 2.3 B2 的“固定现有 TSMOM + 1x + 单 Regime 门控”可行，但要防止隐形多变量

B2 只能测试一个问题：**在冻结 TSMOM 和 1x 仓位下，预先定义的单一 regime 门控是否改善研究验收指标，并优于同状态被动基准。**

必须禁止：

- 同时调 lookback、阈值、出场、费用、仓位、杠杆。
- 多个 regime 定义并行试到最好。
- 用夏普、月化或杠杆后收益反推标签。
- 把失败写成“部分有效”。

## 3. 靶心三：month-30% 是否应从研究验收口径删除？

**裁决：ACCEPT Claude。删除研究验收门。**

我没有反证证明 month-30% 具备可持续机制支撑。相反，它在当前项目中更像资本愿望或探索上限，如果进入研究验收，会产生三类污染：

1. **杠杆污染：** 为达到月化目标而把 10-20x 提前放进研究路线，让杠杆从风险表达工具变成 Alpha 来源。
2. **选择偏差：** 用收益目标反筛 regime、参数或样本，增加隐形多重检验。
3. **叙事污染：** 策略失败时诱导“加过滤/加仓位/改状态”续命，而不是诚实 KILL。

建议口径：

```text
month-30% = Founder 资本愿望 / 极端上行情景 / 商业吸引力参考
研究验收 = 机制成立 + 成本后 E[R]>0 + 赢亏比/爆仓概率/log growth/分年正期望 + 与同状态被动基准比较
杠杆测试 = 仅在 edge 和仓位模型过门后做风险敏感性，不作为 Alpha 来源
```

因此，DEC-080 需要修订；DEC-063 的“month-30% 非验收条件”继续优先。

## 4. 靶心四：Claude 降级表中哪些降错了？

**裁决：大部分降级正确；仅两点需要 MODIFY。**

### 4.1 降级正确

以下项不会在未来 5.5 个月内实际阻塞 edge 发现，应冻结：

- Orchestrator / event store / Strategy Governor engine。
- Web 控制面 / Discord Adapter / 飞书或微信入口。
- 七维路由器。
- 九域常设记分卡。
- Spec Kit 工程试点。
- C4 全套当前态图。
- RAG / 本体 / 模型网关 / A2A / LangGraph / Temporal / Backstage / DevLake / Plane / BMAD / Task Master。

### 4.2 需要 MODIFY 的两点

**第一，P0-C 不能被压到“可有可无”。**

Claude 已保留 P0-C，我同意；但建议写清楚 P0-C 的成功标准，防止再次扩张：

- 权威状态只有一个最新主线口径。
- carry 关键路径不再出现在 active 位置。
- AGENTS/CLAUDE/SYSTEM_RULES/AGENT_REGISTRY 的硬冲突逐条有裁决。
- state_check 对权威冲突返回非零。
- P0-C 报告列出“未做清单”，并明确这些未做项被冻结。

**第二，ADR-001 不应记录 month-30% 裁决。**

month-30% 裁决是 Founder/研究方向/资本愿望口径，属于 DECISION_LOG 或 CURRENT_STATE，不是 Architecture Decision Record。把它写进 ADR 会重复制造“DEC vs ADR”边界混乱。

更合理的选择：

- DEC 修订：记录 month-30% 从研究验收删除。
- ADR-001（可选）：记录“在 edge=0 阶段不建设 Orchestrator/控制面，维持文件式 handoff + 一次性治理卫生”的技术架构选择。

如果 Claude 坚持只写一页 ADR，我建议改成“ADR-001: Defer Orchestrator Until Edge Gate”，并在 Related DEC 中引用 month-30% 裁决。

## 5. 对原四份 Codex 草案的修订建议

原报告不必删除，它可作为未来治理能力的参考。但状态应降级：

| 文件 | 新定位 |
|---|---|
| `REPORT_RESEARCH-AI-NATIVE-20260621.md` | 治理全景和未来能力参考；当前只提取冲突裁决、P0-C、Research-to-Value checklist 内核 |
| `DRAFT_ACTION_PACKAGE_AI_NATIVE_20260621.md` | 被 Claude 顶层重平衡计划部分 supersede；AV-001/P0-C 保留，AV-002 仅 checklist，AV-003 以后全部 defer |
| `SOURCE_CATALOG_AI_NATIVE_20260621.md` | 保留为资料台账；3 篇小红书仍 BLOCKED，不影响当前研究重启 |
| `PLAN_CLAUDE_TOPLEVEL_REBALANCE_20260621.md` | 当前更高优先级的行动计划草案，待 Founder 对 month-30% 做 D 级确认 |

## 6. 建议的立即执行序列

```text
1. Founder/Claude 裁 month-30% 口径
2. Claude 修订 DEC-080 / CURRENT_STATE 口径，冻结 P1-RES-034 原描述
3. Claude 起草 B0 机制卡任务包
4. Codex 执行 B0 或从工程/可证伪角度反审 B0
5. 并行只允许一个 P0-C 治理卫生任务包；完成后治理轨关闭
6. B0 过门才进入 B1/B2
```

## 7. 最终立场

我接受 Claude 的优先级重平衡：**先找 edge，不建管理 edge 的工厂。**

我对前一版草案的修正是：那些治理设计可以作为未来目标架构材料，但不能作为当前执行路线。当前唯一主动建设应是：

- 裁掉 month-30% 验收污染。
- 把 P1-RES-034 拆成 B0-B4。
- 做一次性权威卫生，确保研究任务输入不被旧状态污染。

如果这三件事完成，仍没有机制通过 B0/B2，再讨论更漂亮的协作系统没有意义；如果有机制通过，再建设 Orchestrator/Spec Kit/控制面才有对象可管。
