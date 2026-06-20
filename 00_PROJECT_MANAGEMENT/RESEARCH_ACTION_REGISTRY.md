# 调研行动登记表（RESEARCH_ACTION_REGISTRY）

**用途：** 把所有调研/审计/Founder提供的参考文章的行动结论集中登记，强制追踪执行状态。
**规则：** 每次新调研完成后，当轮写入本表。每次研究/系统任务开工前，必须先查本表有无相关结论。
**维护者：** Claude（主理人）；Codex任务产出中有调研结论时，通过任务报告回传。
**最后更新：** 2026-06-20

---

## 一、策略/研究方向结论

| ID | 来源 | 核心结论 | 对应行动 | 状态 | 优先级 |
|---|---|---|---|---|---|
| RA-001 | AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12 §BIS | Crypto perp funding carry是"锚定机制"形成的状态变量，不是天然正期望策略；正期望条件：小资金/非机构/低容量/市场结构允许 | carry预登记需补充"在什么市场状态下carry为正"假设，不能只说"carry存在" | ❌未执行 | P1 |
| RA-002 | AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12 §AI Alpha Gate | P1-P6六道AI Alpha Evidence Gate必须在任何AI生成假设进入执行前过完 | carry v4预登记补充P1-P6核查节（时间完整性/动态universe/反事实/成本摩擦/多agent分解） | ❌未执行 | P1 |
| RA-003 | PEER_PROJECTS_BENCHMARK_2026-06-12 §Freqtrade | Freqtrade提供lookahead-analysis命令，可检测回测脚本是否有前视偏差 | carry feasibility Codex任务须包含lookahead检测步骤，或自研lookahead_check.py | ❌未执行 | P1 |
| RA-004 | PEER_PROJECTS_BENCHMARK_2026-06-12 §结论 | 最值得学的4个工程能力：无前视检查、实验记录器、数据层契约、backtest-to-live parity | 数据契约=P1-OSS-001（已有任务）；其余三项未建任务 | ⚠️部分 | P2 |
| RA-005 | EXTERNAL_RESEARCH_v3_STRATEGY_DIRECTION §SMC | SMC/ICT方法论有系统性"后验幻觉"——回测时知道哪个swing是真的，实时不知道 | "猎机制不猎形态"已写入CLAUDE.md；但carry的机制验证（"谁在付钱/为什么"）是否真正回答了 | ⚠️部分 | P1 |
| RA-006 | AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS_2026-06-12 §数据质量 | OI/强平数据有已知交易所误报风险，需打质量标签 | CAPABILITY_ENV_REGISTRY已记录数据边界；但carry回测的数据质量标注未做 | ⚠️部分 | P2 |

---

## 二、AI协作/工程能力结论

| ID | 来源 | 核心结论 | 对应行动 | 状态 | 优先级 |
|---|---|---|---|---|---|
| RA-010 | AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12 §Claude hooks | Claude hooks的PreToolUse可把"禁止读Holdout"从软规则变成硬门控 | 在项目根.claude/hooks/建PreToolUse hook，检测file read路径含Holdout时拦截 | ✅已执行（2026-06-20）`.claude/hooks/protect-holdout.py` | P1 |
| RA-011 | AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12 §8个技能 | 应建8个项目级Skill：预登记、证据分级、数据契约、Codex任务书、独立复核、结果intake、state-sync、成本runway | ⚠️部分（2026-06-20）：result-intake/codex-task-spec/research-harvest 3个已建；hypothesis-preregister/state-sync 2个待建 | ⚠️部分 | P2 |
| RA-012 | AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12 §subagents | Claude subagents适合把"会淹没主上下文的搜索/日志/文件读取"放独立窗口 | 超长对话（本项目常态）导致漂移问题，subagent可解；未部署任何subagent | ❌未执行 | P2 |
| RA-013 | AI_CAPABILITY_OPTIMIZATION_RESEARCH_2026-06-12 §CLAUDE.md | 单个CLAUDE.md建议≤200行；重复性流程移入Skill；长参考移入Context Pack | CLAUDE.md当前为内联所有规则的长文档；Skill化未做 | ❌未执行 | P3 |
| RA-014 | EXTERNAL_RESEARCH_v2_AI_NATIVE_OPERATING_PATTERNS §闭环 | 研究循环必须是"闭环"：回测结果→调整假设→再验证；不能开环执行 | 项目一直是开环：结论写入文档后没有系统触发"重新验证"机制 | ❌未执行 | P1 |
| RA-015 | EXTERNAL_RESEARCH_v1 §Claude→Codex冲突 | 需要为Claude→Codex冲突场景设计明确裁决规则 | CLAUDE.md有原则，无具体冲突处理流程；两者分歧时谁拍板从未明确 | ❌未执行 | P3 |
| RA-016 | PEER_PROJECTS_BENCHMARK §RD-Agent | RD-Agent的R/D分工值得学：Research(假设/协议)和Development(实现)分开，有trace/eval | 本项目Claude和Codex的分工不清晰：Claude有时做实现spec，Codex有时给研究建议 | ❌未执行 | P2 |

---

## 三、系统/工具结论

| ID | 来源 | 核心结论 | 对应行动 | 状态 | 优先级 |
|---|---|---|---|---|---|
| RA-020 | PEER_PROJECTS_BENCHMARK §Freqtrade | Freqtrade的hyperopt容易诱导过拟合；Phase 1只用它学无前视检测和控制面，不作执行内核 | Freqtrade评估任务（P1-OSS-002）已建，但评估边界未明确排除hyperopt | ⚠️部分 | P1 |
| RA-021 | PEER_PROJECTS_BENCHMARK §NautilusTrader | NautilusTrader是Phase 2/3最好架构参照，Phase 1引入太重 | 已记录在CAPABILITY_ENV_REGISTRY（Phase 2候选） | ✅已记录 | — |
| RA-022 | AI_QUANT_CRYPTO_RESEARCH_SYNTHESIS §OSS | CCXT统一交易所适配器；Freqtrade干运行层；vectorbt研究层 | OSS调研（OSS_BUILD_VS_BUY）已完成，Freqtrade/CCXT方向已决策 | ✅已执行 | — |
| RA-023 | AI_CAPABILITY_OPTIMIZATION §MCP | MCP只连"外部系统/结构化数据/共享状态"；Phase 1禁装交易执行类MCP | 已在CLAUDE.md体现；CoinGlass MCP（研究数据）未建 | ⚠️部分 | P2 |

---

## 四、Founder提供的参考文章（待补全）

**⚠️制度缺口：** Founder历次提供的参考文章/资料从未被系统记录。以下为已知的，但可能不完整。

| ID | 资料 | 提供时间 | 核心结论 | 是否落地 |
|---|---|---|---|---|
| RA-030 | 20篇微信公众号文章（AI原生运营） | 2026-06-05前后 | 见EXTERNAL_RESEARCH_v2 | ❌多数未落地 |
| RA-031 | （其他文章/资料——需Founder补充确认） | — | — | — |

---

## 五、立即行动清单（P1级，不等下次调研）

按价值排序：

1. **carry feasibility 任务加 lookahead检测**（RA-003）——carry FEASIBILITY-LOCK解除后，Codex任务书必须包含前视偏差检查，否则结果不可信
2. **carry预登记补P1-P6 AI Alpha Evidence Gate**（RA-002）——补充"时间完整性/真实摩擦成本"两节核查
3. **carry设计补"在什么状态下为正期望"假设**（RA-001）——carry不是无条件的，预登记必须显式说明trigger条件
4. **Holdout hook**（RA-010）——把软规则变硬门；这是安全边界，不应依赖Claude自觉

---

*本表为行动追踪，不是知识存储。调研全文见原文件。*
*下次调研完成后，当轮更新本表。Founder提供新参考资料后，当轮在RA-03x补充条目。*
