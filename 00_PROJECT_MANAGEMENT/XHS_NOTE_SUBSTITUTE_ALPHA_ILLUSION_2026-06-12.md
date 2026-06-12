# 小红书笔记替代来源摘要：AI交易系统的 Alpha，可能全是幻觉

**日期：** 2026-06-12  
**来源状态：** 原小红书链接因登录/风控未能读取；用户提供截图，要求以截图中两条链接替代原笔记内容。  
**替代来源：**

1. 论文：Yuxuan Ye et al., **The Alpha Illusion: Reported Alpha from LLM Trading Agents Should Not Be Treated as Deployment Evidence**, arXiv:2605.16895v1, 2026-05-16.  
   链接：https://arxiv.org/abs/2605.16895
2. 代码/复现仓库：`https://github.com/hj1650782738/Trading`。  
   访问状态：2026-06-12 公开访问返回 GitHub 404；`git ls-remote` 需要凭据/不可公开读取。因此本项目只能引用论文对该仓库的描述，不能审计代码实现。

## 一句话结论

这篇材料对本项目是 P0 级提醒：**LLM/多 agent 交易系统的 reported alpha 不能当作可部署交易能力证据；AI 只能生成假设、提取信息、加速复核，不能越过无前视、成本、样本外、校准、独立性和执行摩擦证据门。**

## 论文主张摘要

论文不是否定 LLM 在金融中的价值，而是反对一个危险迁移：把端到端 LLM trading agent 在短窗口回测里的高 Sharpe，直接讲成“LLM 能交易”或“系统有可部署 alpha”。

作者指出，当前公开证据往往无法区分以下几类情况：

| 可能真实来源 | 对项目的含义 |
|---|---|
| robust predictive ability | 可以继续验证，但仍要过成本/风险/样本外 |
| temporal contamination | 模型训练语料、检索、记忆可能偷看未来 |
| unmodeled frictions | 毛收益被手续费、滑点、价差、冲击、延迟、token 成本吃掉 |
| short-window Sharpe uncertainty | 短样本高 Sharpe 可能只是噪声 |
| narrative fitting | 解释漂亮，但不是可执行概率 |
| parametric priors | 模型权重内隐含行业/风格/方向偏见 |

## P1-P6 最小证据协议

论文提出 P1-P6 作为部署强度声明的最小报告协议。对本项目可直接翻译为 Research Protocol 增补：

| 协议 | 论文含义 | 本项目翻译 |
|---|---|---|
| P1 Temporal integrity | 防 pretraining/retrieval/memory future leakage | 所有 AI 生成假设必须记录模型版本、知识截止、外部资料时间戳；实验窗口必须 point-in-time |
| P2 Dynamic universe | 防幸存者偏差和事后清洗样本 | 加密 universe 必须按当时可交易、流动性、下架/停牌/上市时间构造 |
| P3 Counterfactual robustness | 防模型先验锁定和反证无效 | AI 提案必须做反向证据/方向翻转/中性化测试；不能只问“为什么它对” |
| P4 Epistemic calibration | 语言信心不是交易概率 | LLM 置信度不得直接控制仓位；若使用，必须校准 ECE/可靠性曲线 |
| P5 Realistic implementation | 防 gross alpha illusion | 必须逐层扣价差、手续费、滑点、冲击、延迟、资金费、token 成本 |
| P6 Multi-agent disaggregation | 防多 agent 共识幻觉 | 多 agent 结论必须有单 agent baseline、分歧率、角色相似度、协调成本、净收益增量 |

论文还把声明强度分层：

| 声明强度 | 最低要求 | 本项目允许语言 |
|---|---|---|
| LLM 文本抽取/研究助手 | P1/P3 light | “改进信息抽取/提出候选特征” |
| 历史回测/原型 | P1 + P2 + P5 | “该窗口有正收益轨迹”，不得称部署 |
| 可部署 alpha | Full P1-P5 | “结构检验后保留净收益” |
| 自主交易能力 | Full P1-P6 | “多 agent 分解后仍保留净收益” |

## 对 AI Quant Company 的直接吸收

1. **禁止把 AI 生成策略本身计为 evidence。** Claude/Codex/低模型产出的策略想法只算 hypothesis，不算 alpha 证据。
2. **AI agent 不能做最终交易决策权威。** LLM 最适合做上游信息接口：资料抽取、假设生成、代码实现、反方审计、报告总结。
3. **Research Protocol 应新增 AI Alpha Evidence Gate。** 任何含 “AI trading agent / AI generated strategy / LLM signal” 的报告，必须显式回答 P1-P6。
4. **多 agent 不等于独立专家。** 本项目四层组织有用，但只有在 context 隔离、读路径白名单、反向审查和 trace 存在时，才有“独立复核”意义。
5. **TSMOM/A-1/A-4 都不能用 AI 叙事加分。** 只能用时序完整、成本完整、样本外和风险完整的结果加分。
6. **剩余 2 条 Alpha 命不能给 AI 自动探索消耗。** AI 可以准备数据、做普查、写预登记，但是否耗命必须由 Founder/Claude 在证据门后明确批准。

## 与当前项目冲突点

| 当前倾向 | 冲突 | 改法 |
|---|---|---|
| Codex/Claude 能快速产出策略研究 | 速度提高会放大 alpha 幻觉速度 | 每个研究任务新增 `AI_ALPHA_EVIDENCE` 小节 |
| 多角色复核带来信心 | 同模型家族/同上下文可能形成共识幻觉 | 强制单 agent baseline + 反方路径隔离 |
| 端到端 AI 交易系统是长期愿景 | 论文反对 LLM 做最终交易权威 | 长期系统应是 modular：LLM upstream, calibrated model/risk/execution downstream |
| 高 Sharpe 结果容易激励继续 | 短窗口/多试验高 Sharpe 可能无部署意义 | 高 Sharpe 必须配 DSR/PBO、成本瀑布、regime 分层 |

## 证据等级

- arXiv 论文：B（工作论文/预印本；作者给出明确协议和可审计论点，但代码链接当前不可公开审计）。
- GitHub 仓库：D/不可用（论文声称有 reproduction harness；本次访问 404，不能作为已审代码证据）。
- 小红书原笔记：未读取；本文件不声称总结了小红书正文，只吸收用户截图中的替代链接内容。
