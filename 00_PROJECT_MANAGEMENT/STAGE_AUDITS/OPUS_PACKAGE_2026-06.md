# OPUS 审计包 2026-06

**生成时间：** 2026-06-07
**生成者：** Claude（自动任务 L1 月审，DEC-022）
**用途：** 由 Founder 打开 Opus 4.8 粘贴本文件，执行独立 L2 深度审计

---

## Opus 审计 Prompt（请连同下方全部文档一起粘贴）

你是 AI Quant Company 项目的独立审查员，不是参与者。
你的职责是找问题、找风险、找偏差，不是肯定现有决策。
以下是项目的完整上下文文档，请按11个维度进行深度审计：
方向一致性 / 假设有效性 / 决策健康度 / 文档一致性 / 进度真实性 /
风险状态 / 资源可持续性 / 技术债务 / 机会成本 / 知识完整性 / 外部依赖风险

输出结构化审计报告，标注 P0/P1/P2 问题，并对 Founder 列出需要决策的事项。

**本月 L1 自审已给出三点待关注（请独立验证勿盲信）：**
1. 成本零跟踪 vs 5000元费用止损阈值；
2. 独立 Alpha 失败 5/8 距止损剩 3 次；
3. P1-04 首个过门槛结果（探索级）是否存在过拟合/选择偏差。

---

# ===== 文档1/6：CURRENT_STATE.md（全文）=====

# CURRENT_STATE.md

**版本：** 3.15  
**最后更新：** 2026-06-07（P1-05两轴归因完成DEC-062:纠正Claude两假设[2022非纯熊市反弹仅64.7%;Sweep非震荡专属],94.4%亏损在宏观熊市;下一步P1-06=P1-04+宏观牛市过滤已预登记出任务,遵循Protocol v1.2规则式状态门控;Sweep列"牛市回调反弹"候选不复活）  
**上版（3.14）：** 2026-06-07（工具调研回灌经Codex 7点评审:报告重写v2.1;三屏障=方向性事件默认基准;手动Meta改"规则式状态门控"去精确率召回率;NautilusTrader=LGPL-3.0/Freqtrade=2026.4;Protocol→v1.2;DC→Codex自动触发护栏）  
**上版（3.12）：** 2026-06-06（P1-04 PASSED/EXPLORATORY=首个过门槛结果,Sharpe1.33/WF全>1,但2022 -23.72%[ADX不分牛熊];不进Holdout;下一步P1-05归因[扩两轴]）  
**更新者：** Claude（CTO）  
**说明：** 本文件记录项目当前真实状态。每次阶段切换或重大变更后必须更新。新对话启动时优先读取本文件恢复运行认知。

---

## 1. 当前阶段

**阶段名称：** Phase 1 — 找到有效赚钱规律（2026-06-06 跨越，DEC-049）  
**上一阶段：** Phase 0A ✅（5/5）→ Phase 0B ✅（研究闭环能力经8个闭环证明，L2 CONDITIONAL GO）  
**Phase 1 目标：** ≥3个假设完整测试，≥1个通过统计验证（扣全部成本含funding正期望、多时段稳定、Sharpe>1、WF+Holdout）  
**首个方向：** 资金费率/基差 carry（DEC-048）；可行性前置完成（`06_RESEARCH/RESULTS/20260606_funding_feasibility.md`）

**失败计数（双轨制，DEC-044/046/047，三数永久并列）：** 历史实验失败 **8次**（v1/v2/v3/v5/v6/v6b/0B17/0B18）｜独立Alpha假设 **4/8**（v1/v2/v3/v5，管辖项目级止损，距8还有4次）｜v4实现变体 **CLOSED**（v6/v6b/0B17/0B18）  
**Holdout 状态：** 全部实验均未读取，封存完整  
**v4信号最终定性（DEC-047）：** 样本内统计边沿真实，但经止损/退出/仓位/恐惧度全维度实现测试，无一可部署 → **降级为"不可部署"归档，实现线CLOSED，永久停止任何v4变体**  
**下一步：** ⏳ **转向全新独立Alpha假设（非Sweep家族）** — 方向待Founder拍板（D级）【等待Founder确认】  
**完成条件：** 五条验收标准全部满足（见 DECISION_LOG DEC-005）

| 验收条件 | 状态 |
|---------|------|
| 1. Memory 恢复能力 | ✅ 满足（Cowork + Chat 双端验证） |
| 2. Research Protocol 存在 | ✅ **2026-06-05 完成**（DEC-023，06_RESEARCH/RESEARCH_PROTOCOL_v1.md）|
| 3. Backtest Framework 可运行 | ✅ **2026-06-04 完成** VectorBT 1.0.0 端到端验证通过 |
| 4. 第一个假设被定义 | ✅ **2026-06-06完成**（DEC-027）|
| 5. 第一个研究闭环完成 | ✅ **2026-06-06完成**（结论：FAILED，Holdout未运行）|

---

## 2. 工具链状态

| 工具 | 状态 | 备注 |
|------|------|------|
| Claude Cowork | ✅ 完全可用 | **主工作区**，Memory恢复正常 |
| Claude Code v2.1.161 | ✅ 已安装 | Cowork 底层依赖 |
| Desktop Commander v0.2.41 | ✅ 完全可用 | **Mac本地执行环境**（start_process可在Mac运行任意命令，2026-06-05确认）|
| Python 3.13.5 + 量化环境 | ✅ 完全可用 | **2026-06-04安装完成**：pandas/numpy/vectorbt/ccxt/matplotlib/scipy/statsmodels |
| VectorBT 1.0.0 | ✅ 已验证 | 端到端回测管线通过，Phase 0A验收条件3满足 |
| x-reader 0.2.0 + Playwright | ✅ 已安装 | **2026-06-05安装**，微信公众号批量抓取已验证（20篇，2分钟）|
| Obsidian + Sync | ✅ 可用 | 被动读取，Claude 写入文件后自动同步 |
| Codex | ✅ 已验证 | **2026-06-05完成0A-6首次真实任务**：信号检测器全量运行及验收通过 |
| Context7 | ⚠️ 已安装未使用 | 本项目中尚未实际调用 |
| Node.js v22.22.0 | ✅ 可用 | openclaw@2026.4.8 全局安装（Phase 2 评估是否使用）|
| 腾讯云轻量（新加坡，2核4G） | ⚠️ 状态未知 | V4基础设施状态待Phase 2验证（P-001修正）|

---

## 3. Memory Core 文件状态

| 文件 | 状态 |
|------|------|
| MEMORY_EXTRACTION_PROTOCOL.md | ✅ 完成 |
| PROJECT_CONTEXT.md | ✅ D10+D34共9条，审计通过 |
| DECISION_LOG.md | ✅ DEC-001~042 |
| CURRENT_STATE.md | ✅ 本次更新（v3.0）|
| SYSTEM_RULES.md | ✅ 完成，审计通过 |
| CLAUDE.md（项目根目录） | ✅ **v2.0，2026-06-05重构**，134行精简至57行 |

**00_PROJECT_MANAGEMENT：**

| 文件 | 状态 |
|------|------|
| AI_CAPABILITY_BASELINE.md | ✅ **v1.1，2026-06-05更新**（量化环境、x-reader、Desktop Commander执行能力）|
| PROJECT_OPERATING_STATE.md | ⚠️ 待更新（内容与CURRENT_STATE部分重叠，需核对）|
| AI_QUANT_COMPANY_ARCHITECTURE_v1.md | 存档，已被v2替代 |
| AI_QUANT_COMPANY_ARCHITECTURE_v2.md | ✅ FROZEN，**2026-06-05修正P-001/P-002（§5.2基础设施状态+§8.2状态机加注）**|
| PROJECT_MASTER_PLAN_v2.md（**v2.2**） | ✅ **2026-06-05升版**，任务验收标准全部补全（B4任务完成）|
| EXTERNAL_RESEARCH_REPORT_v1.md | ✅ 完成（11方向）|
| EXTERNAL_RESEARCH_v2_AI_NATIVE_OPERATING_PATTERNS.md | ✅ **2026-06-05新增**（20篇文章提炼）存于02_KNOWLEDGE_BASE/ |

**02_KNOWLEDGE_BASE（2026-06-05 从空目录变为有内容）：**

| 文件 | 状态 |
|------|------|
| EXTERNAL_RESEARCH_v2_AI_NATIVE_OPERATING_PATTERNS.md | ✅ 新增，AI原生操作模式参考手册 |

**03_RAW_INBOX/WECHAT_ARTICLES（2026-06-05 新增）：**

| 内容 | 状态 |
|------|------|
| 20篇微信公众号文章 | ✅ 已抓取（x-reader + Playwright），存为md文件 |

**99_TEMP：**

| 文件 | 状态 |
|------|------|
| AUDIT_REPORT_HISTORY_CONTAMINATION.md | ✅ **2026-06-05新增**，文档污染审计报告（5个问题，2个严重已修正）|

**Cowork 工作区：**

| 文件 | 状态 |
|------|------|
| /Users/yaomingyu/Documents/Claude/Projects/AI Quant Company/CLAUDE.md | ✅ 完成 |

---

## 4. RAW_INBOX 提炼状态

| 文件 | 提炼状态 | 优先级 |
|------|---------|--------|
| D10：事故报告 | ✅ 已提炼写入 | — |
| D34：决策记录 | ✅ 已提炼写入 | — |
| D35：技术债务登记表 | ✅ 已读取提炼（B1任务，99_TEMP/RAW_INBOX_EXTRACTION_NOTES.md）| — |
| D29：V4.6.2 系统架构文档 | ✅ 已读取提炼（B1任务）| Phase 2 参考 |
| D30：持仓生命周期规格书 | ✅ 已读取提炼（B1任务）| Phase 2 参考 |
| D31：研究协议 | ✅ 已读取参考（B1任务，V5 Research Protocol 独立设计）| — |
| V4.6.2 项目背景摘要 | ❌ 未提炼 | P0 |
| 项目状态记录20260509 | ❌ 未提炼 | P1 |
| MASTER_CONTEXT v2.0（ChatGPT） | ✅ 已读取认知已建立 | — |
| DeepSeek Chronicle v2.0 | ✅ 已读取认知已建立 | — |
| ScienceDirect 论文集 | ❌ 未处理 | P2 |
| ssrn-6816232.pdf | ❌ 未处理 | P2 |

---

## 5. 当前任务队列

### P0（当前阶段核心，直接影响 Phase 0A 完成）

| 任务 | 状态 | 说明 |
|------|------|------|
| 架构 v2 + 计划书冻结 | ✅ 完成 | DEC-020 |
| Research Protocol 建立 | ✅ 完成 | DEC-023 |
| Backtest Framework 选型与验证 | ✅ 完成 | VectorBT 1.0.0，DEC-014 |
| 0A-6 Codex 首次真实任务验证 | ✅ **2026-06-05完成** | 首次输出456条；补齐BTC缺失月份后当前为465条 |
| 0A-NEW2 样本量可行性核查 | ✅ **2026-06-06完成** | BTC 245 + ETH 214 = 459个正风险唯一入场事件，探索级 |
| ETH/USDT 4H样本扩展 | ✅ **2026-06-06完成** | DEC-024；与BTC同语义、同参数、同期数据 |
| 止损与去重规则 | ✅ **2026-06-06确认** | DEC-025：Sweep K线low止损；同品种同signal_time一次入场；保留最近Sweep |
| Regime样本复核 | ✅ **2026-06-06完成** | Daily EMA200多头Regime下BTC+ETH仅244次；加入SOL后315次 |
| SOL纳入首个假设 | ✅ **2026-06-06确认** | DEC-026；Regime过滤后三品种315次，探索级 |
| 第一个假设定义 | ✅ **2026-06-06完成** | `v5_sweep_choch_fvg_bull_v1`正式预登记，DEC-027 |
| 第一个研究闭环 | ✅ **2026-06-06完成** | `v5_sweep_choch_fvg_bull_v1`失败；报告已归档 |
| Phase 0A阶段审计 | ✅ **2026-06-06完成** | P0=0，P1=5；建议CONDITIONAL GO进入Phase 0B |
| 阶段跨越确认 | ⏭️ 下一步 | 等待Founder确认进入Phase 0B |
| 第二候选假设1H可行性 | ✅ **2026-06-06完成** | 前80%数据候选1,012次；跨品种同刻去重889次，确认级数量 |
| 第二假设预登记 | ✅ **2026-06-06完成** | `v5_sweep_choch_fvg_bull_v2`，DEC-029 |
| 回测规则自动测试 | ✅ **2026-06-06完成** | 止损优先、持仓冲突、资金费率3项测试通过 |
| 第二研究闭环 | ✅ **2026-06-06完成** | 1H版本失败；Holdout未访问 |

### 0A-6 实验产物

| 产物 | 状态 |
|------|------|
| `06_RESEARCH/CODE/signal_detector.py` | ✅ 完成，全量运行约0.62秒 |
| `06_RESEARCH/CODE/output/triple_signals_BTCUSDT_4H.csv` | ✅ 完成，当前465条记录（数据补齐后） |
| `04_AI_TEAM/CODEX_TASKS/REPORT_0A6_SIGNAL_DETECTOR.md` | ✅ 完成并验收 |

**已确认研究口径（DEC-025）：** 止损采用Sweep K线最低价；同一品种同一 `signal_time` 只入场一次；多个Sweep重叠时保留最近Sweep。

### 0A-NEW2 核查结论

| 口径 | 数量 | DEC-018档级 |
|------|-----:|-------------|
| BTC原始结构序列（数据补齐后） | 465 | 探索级，但存在伪重复计数 |
| BTC正风险唯一入场事件 | 245 | 不成立 |
| ETH正风险唯一入场事件 | 214 | 不成立 |
| **BTC+ETH正风险唯一入场事件** | **459** | **探索级（300-499）** |
| 跨品种同刻再次去重 | 398 | 探索级 |

最新报告：`06_RESEARCH/RESULTS/0A_NEW2_ETH_EXTENSION_REPORT.md`

**当前结论：** 样本扩展路径已由Founder确认并执行（DEC-024）。459次仅为探索级，可启动第一个研究闭环，但禁止作为实盘依据。

### 0A-5 Regime前置复核

Research Protocol 禁止无 Regime 过滤直接运行策略。采用“前一完整日收盘价 > Daily EMA200”的多头 Regime 后：

| 品种范围 | 合规事件数 | DEC-018档级 |
|----------|-----------:|-------------|
| BTC+ETH | 244 | 不成立 |
| BTC+ETH+SOL（DEC-026已确认范围） | 315 | 探索级 |
| BTC+ETH+SOL跨品种同刻去重 | 279 | 不成立（相关性压力口径） |

报告：`06_RESEARCH/RESULTS/0A5_REGIME_SAMPLE_GAP_REPORT.md`

### 研究闭环汇总

**v1（4H三重确认，做多）**
- Sharpe 0.60，MaxDD 33.14%，交易158次 → **FAILED**（1/8）

**v2（1H三重确认，做多）**
- Sharpe 0.90，MaxDD 36.61%，WF严重衰减 → **FAILED**（2/8）

**v3（Sweep单事件收益分布，做多）**
- 效应集中2021，跨时期不稳定 → **FAILED**（3/8）

**v4（双层Regime：EMA200 + BTC 30日动量，做多）**
- 事件研究：425事件，t+6/12/24全部显著，Bootstrap三层校验通过 → 事件研究 **PASSED**
- 策略回测：Sharpe 0.31，MaxDD 19.08%，净收益+20.11%，Expectancy +0.032R
  - WF衰减：0.85→0.34→0.11；2022亏损-6.51%；SOL亏损-5.65%
  - 成本侵蚀：手续费+资金费率吃掉毛利润54.64%
  - 根因：固定止损+1R/2R止盈与t+24统计信号周期错位
  - 策略 → **FAILED**（不另计失败计数，视为同一闭环追加步骤）

**v5（Bearish Sweep + 双层熊市Regime，做空）**
- 344事件，t+24不显著；非重叠152事件三窗口全部失败
- 效应依赖2022（占53.2%），WF仅第二段通过
- 结论：不支持双向策略 → **FAILED**（4/8）

**0B8：时间退出敏感性分析（诊断，不计失败）**
- 同口径测试 t+6 / t+12 / t+24 × 三品种 / BTC+ETH 共六组
- 最优：t+24 三品种 Sharpe 1.31 / MaxDD 37.63%；BTC+ETH Sharpe 1.11 / MaxDD 27.26%
- 联合门槛（Sharpe>1 AND MaxDD<25%）均未通过
- 止损率随窗口增加：t+6 约52%，t+12 约60%，t+24 约68%；止损触发中位始终偏早
- 关键发现：t+24方向最优，但回撤控制是瓶颈；成本占毛利率从54%降至20%（t+24改善显著）

**0B9：止损触发诊断（诊断，不计失败）**
- 基于v4策略 trades.csv（360笔）
- 止损率58.33%；中位触发时机：第1根K线
- 80%止损在t+6（24小时）前发生；88.57%在t+12前发生
- SOL止损率67.09%（vs BTC 57%, ETH 54%），平均R为负
- 2022年10/11笔止损，全部在t+6前触发
- 核心诊断：**止损过早是主因**。现有止损在事件研究有效窗口（t+24）前大量截断盈利空间

**v6（sweep_low + t+12时间退出，在0B10中运行）**
- 三品种 Sharpe 0.87 / MaxDD 36.32%；BTC+ETH Sharpe 0.86 / MaxDD 26.65%
- 均FAILED → **FAILED**（5/8）

**v6b（ref_low + t+12，在0B10中运行）**
- ⚠️ 语义纠错：ref_low 对多头来说是更紧止损（sweep_low < ref_low，止损更靠近入场价）
- 三品种 Sharpe 1.22 / MaxDD 28.45%（MaxDD超门槛）；BTC+ETH Sharpe 0.92 / MaxDD 22.57%（Sharpe未达标）
- SOL独立：Sharpe 1.34 / MaxDD 17.62%（不构成新假设，禁止据此查看Holdout）
- 均FAILED → **FAILED**（6/8）⚠️ 接近止损线

**v7（第三层Regime，在0B11中运行）—— 事件研究**
- 411事件（v4为425），三窗口主检验通过，非重叠208事件通过
- 2022年事件数：12 → 12（无变化），WF第二段p=0.1251（无改善）
- 结论：**主检验PASSED / 增量目标FAILED**（不计入失败计数）
- 不安排v7策略回测；第三层Regime方向无效

**Bootstrap校验（v4附加）**
- N=10000，同步日历block bootstrap，三窗口p=0.0058/0.0020/0.0003
- v4样本内统计信号三层稳健性校验通过（t检验/非重叠/Bootstrap一致）

**回测单测（P1-4）**
- pytest 9/9通过，止损优先/持仓冲突/资金费率三规则验证完整

**0B12：无止损t+24诊断（诊断，不计失败）**
- 固定10%名义仓位，完全删除止损，持有满24根K线后退出
- 三品种：Sharpe 1.28 / MaxDD 12.06%（217笔）；BTC+ETH：Sharpe 1.06 / MaxDD 7.38%（172笔）
- ⚠️ 仓位不可比：固定10%名义 ≠ 风险定仓，MaxDD偏低因仓位较小
- WF2：三品种Sharpe -0.44，BTC+ETH -0.26（稳定性缺口依然存在）
- 关键纠错：0B8的t+24实际保留sweep_low止损（止损率68.22%），本任务才是真正无止损
- 核心结论：**移除止损不能显著提升Sharpe（1.28≈1.31），WF2稳定性缺口是更根本的问题**

### 诊断结果（三项，不计失败）

**0B14：MAE分析**
- 盈利交易MAE 80th：**4.38%（= 1.87x ATR）**
- sweep_low平均2.33%：47.58%盈利交易MAE超过；ref_low平均1.38%：63.71%超过
- 品种MAE 80th：BTC 3.32% / ETH 4.02% / SOL 7.68%
- 2022（5笔）：MFE均值0.87%，方向失效，止损放宽无法解决

**0B15：波动率压缩分组**
- 方案A（ATR）p=0.5320，方案B（BBW）p=0.9134——两方案均不显著
- **结论：不建议增加波动率压缩过滤层**；V4历史IC因子在双层Regime下不复现

**0B16：ATR止损诊断**
- ATR×1.9：覆盖81.45%盈利MAE（≈80th percentile），理论避免61.43%历史止损
- ATR×3.5过宽（8.69%），max(ref_low,ATR×3.5)退化为纯ATR×3.5
- **推荐：ATR×1.9为策略止损参数**

**0B17（ATR×1.9止损+t+24+1%风险定仓）—— 策略回测，FAILED**
- ATR×1.9：Sharpe 0.86 / MaxDD 24.80%（止损率47.74%，287笔，净收益+75.08%）→ MaxDD达标，Sharpe差0.14
- ATR×3.5压力测试（不另计失败）：Sharpe 0.95 / MaxDD 14.93%（止损率22.46%）→ 仍未达Sharpe门槛
- WF：2.21 → -0.22 → 0.63（WF2为负，WF3低于通过线）
- 2022：9笔7止损，Sharpe -1.77，方向性失败依旧
- 品种：BTC 0.25 / ETH 0.89 / SOL 0.93（BTC为最大拖累）
- 均FAILED → **FAILED**（7/8）⚠️ 仅剩1次机会
- 报告：`04_AI_TEAM/CODEX_TASKS/REPORT_0B17_ATR_STRATEGY.md`、`06_RESEARCH/RESULTS/20260606_atr_strategy.md`

### 当前研究结论与下一方向

**结论（Claude判断，2026-06-06 v3.1更新）：**  
止损/退出维度已被充分探索并收敛（v6/v6b/0B12/0B17）：收紧风险→MaxDD优秀但Sharpe下降；放宽→Sharpe改善但MaxDD恶化；有效前沿稳定坐落于联合门槛下方。  
**瓶颈已从「止损过紧」转移到「信号跨时期稳定性」**（WF2/2022方向失效在所有版本中始终为负，非止损可解）。  
继续微调止损倍数边际价值有限。**不消耗最后一次机会于又一个止损变体（DEC-043）。**

**L3紧急审计：已完成 + Codex复核修正（DEC-046）** 报告 `00_PROJECT_MANAGEMENT/STAGE_AUDITS/L3_EMERGENCY_2026-06-06.md`（§9为修正节）  
结论：项目不暂停；停止止损微调；失败计数双轨化（DEC-044），三数永久并列（DEC-046）。

**Founder决策（2026-06-06）：** 计数口径委托Claude裁决（→双轨）；方向选A=波动率缩仓。

**Codex复核已采纳（DEC-046，5项）：** ①v4降级为"样本内统计边沿"非"真Alpha" ②有效前沿仅示意非同轴 ③三数永久并列防熔断绕过 ④0B18为Phase 1+缩仓的阶段例外 ⑤仓位公式纠错（quantity→notional）。0B18定位收紧为机制检验，通过仅为Holdout候选。

**0B18 波动率缩仓策略（DEC-045）—— 策略回测，FAILED/机制无效（DEC-047）**
- Sharpe 0.78 / MaxDD 14.03%（236笔，净收益+32.26%）→ Sharpe未过，联合门槛FAILED
- 机制无效：2022高恐惧0/12，WF2标准化收益完全不变；高恐惧成交35/53在2021，缩仓削的是优质交易
- WF1 Sharpe 2.84→2.58（被削弱），2021收益27.92%→16.56%
- 验证了Codex的WF1预警：波动率百分位标错对象（标2021牛市而非2022熊市）
- → **FAILED**，历史失败计数 7→8；独立Alpha仍4/8
- 报告：`04_AI_TEAM/CODEX_TASKS/REPORT_0B18_VOLPOS_STRATEGY.md`、`06_RESEARCH/RESULTS/20260606_volpos_strategy.md`

### v4 实现线闭幕（DEC-047）

v4信号（Bullish Sweep+双层Regime）止损/退出/仓位/恐惧度**全维度测试完毕，无一可部署**：
止损 sweep_low→ref_low→ATR×1.9→ATR×3.5；退出 1R2R→t+12→t+24；仓位 1%风险→无止损固定→波动率缩仓。
有效前沿稳定坐落联合门槛下方；WF2（2022）始终方向失效，非实现层可解。
**v4降级为"样本内统计边沿、不可部署"归档，实现线CLOSED，永久停止任何变体。**

**当前阶段决策点：** 项目级止损未触发（独立Alpha 4/8）。

**Founder决策（2026-06-06）：** 先做L2审计再定阶段。新方向初选截面动量，**经股票偏向复盘后修正为资金费率/基差家族（DEC-048）**。

**L2阶段审计已完成（DEC-022）：** 报告 `00_PROJECT_MANAGEMENT/STAGE_AUDITS/L2_AUDIT_PHASE_0B_2026-06-06.md`
- 结论：**CONDITIONAL GO → Phase 1**（P0=0，P1=5）
- 核心判断：Phase 0B能力目标（证明研究闭环）已被8个闭环远超完成；"找到可部署信号"本属Phase 1目标
- P1前置（截面动量预登记前必清）：①品种宇宙扩展至8~10个流动性永续 ②成本可行性前置测算 ③双轨计数平移 ④治理节奏控制 ⑤目录重构(DEC-017)

**方向修正（DEC-048，股票偏向复盘）：** 截面动量是股票旗舰因子，依赖大广度+低相关，加密两者皆不满足（BTC/ETH/SOL对BTC相关0.7~0.9，横向排序塌缩为BTC-beta）→ 改为**资金费率/基差家族**（永续最原生、与价格结构正交）。L2 P1-01（扩品种）对此方向不再阻塞。

**数据盘点：** 有 BTC/ETH/SOL 4H永续K线 + 8H资金费率（`06_RESEARCH/DATA/FUTURES/`，2020起）；**无现货**。
**设计岔口（待可行性前置定）：** 纯永续方向性（不补数据/不改范围） vs delta中性carry（需补现货+超DEC-019范围=D级）。

**资金费率可行性前置已完成（2026-06-06）：**
- BTC/ETH资金费率~88%为正，年化carry 14~17% → **真边在delta中性carry（现货多+永续空），价格中性高胜率**
- SOL无稳定carry（肥尾），排除；纯永续无法捕获carry（扛满价格风险）
- 极值事件train合计~1300（确认级），样本充足
- 报告：`06_RESEARCH/RESULTS/20260606_funding_feasibility.md`

**P1-01 TSMOM 已执行，FAILED / COST-LIMITED（DEC-051）：**
- 净Sharpe 0.720 / MaxDD 68.38% → FAILED；零成本毛Sharpe 1.043（>1）→ COST-LIMITED（信号有边沿，非无效）
- ✅ 正面：毛边沿存在（项目至今最接近edge）；2022 +14.65%（顺势+做空在熊市转正，正交论点部分成立）
- ⚠️ 真问题（比成本更重）：MaxDD 68%（三段WF 56~68%，零成本也不可投资）；资金费率175k为最大成本项（多头长持被结构性抽血）；空头侧全样本净亏-205k（非两侧edge）
- 1x口径固化：每根4H开盘检查并按比例校正（K线内浮动允许，峰值1.144x）；不追溯改v1
- 报告：`06_RESEARCH/RESULTS/20260606_tsmom_trend.md`、`04_AI_TEAM/CODEX_TASKS/REPORT_P1_01_TSMOM.md`

**双轨计数：历史9 / 独立Alpha 5/8（距止损还有3次） / TSMOM家族开放（COST-LIMITED允许v2+细化，按v4家族同规则不增独立Alpha）**

**P1-02 TSMOM v2（波动率目标定仓）已执行，FAILED（DEC-052）：**
- 净Sharpe 0.505 / 毛Sharpe 0.916（跌破1，已非COST-LIMITED）/ MaxDD 69.70%（未改善）
- inverse-vol按设计工作（SOL压至13%、成本降38%），但**组合回撤纹丝不动**，还砍了v1最强的SOL
- 🔑 **核心诊断：单因子共同回撤**——各品种MaxDD都降了(48/41/44%)但组合没降，因BTC/ETH/SOL高相关同涨同跌，趋势错时三个一起回撤；按品种缩仓无法分散一个共同因子(BTC-beta)的回撤
- 报告：`06_RESEARCH/RESULTS/20260606_tsmom_voltarget.md`、`04_AI_TEAM/CODEX_TASKS/REPORT_P1_02_TSMOM_VOLTARGET.md`

**双轨计数：历史10 / 独立Alpha 5/8（距止损还有3次） / TSMOM家族两连测**

**TSMOM 正式封存（DEC-053）：** 趋势有毛边沿+解决2022，但净Sharpe<1（没过真本事关）+ ~69%单因子共同回撤。不再开v3等变体。

**Founder决策（2026-06-06）：门槛校准（DEC-053）。** 验收标准改为：
- ① 真门槛不变：净Sharpe>1（扣全成本含funding）——绝不下调
- ② 回撤改为"按DEC-015资金档定规模"约束：账户回撤=原始回撤×部署比例≤当档容忍(30%/10%/5%)，回撤大=投得少，不是信号差
- ③ 脆弱性上限：原始MaxDD<50%
- 防搬龙门安全阀：标准现在冻结；★回判TSMOM仍不过(Sharpe<1且DD>50%)，证明非为救它；Sharpe>1不降；Holdout不变

**重大框架更新（DEC-055，源于Founder洞察）：确立 regime-first 自上而下框架。**
- 顺序：①大环境(趋势↑/↓/震荡) → ②方向(多/空/不做) → ③入场 → ④离场/仓位风控
- 过去缺陷：Sweep家族只做③入场点；TSMOM做②方向但缺①趋势/震荡判断 → 震荡期挨打
- ER诊断证实：TSMOM edge集中"趋势期做多"R+0.129；震荡格+做空格为死重/负
- "马后炮"再评估：滞后不可消除但V4确认方法粗劣是主因；带滞后的趋势期做多仍赚→路线可行，方法可改
- **Claude工作方式转为主动量化/交易主理人**（采纳Founder反馈）

**两个并行（Founder决定）：**
1. **regime-first 长偏向TSMOM** 已预登记+出任务（`HYPOTHESES/v6_tsmom_regime_long_v3.md`、`TASK_P1_04_TSMOM_REGIME_LONG.md`）【需要Codex】
   - 仅做多+ADX>25趋势规(刻意用ADX而非诊断的ER,防过拟合);真门槛净Sharpe>1;TSMOM家族不增独立Alpha(仍5/8)
2. **OI/清算数据核查** `TASK_P1_03_DATA_RECON_OI.md`【需要Codex】（清算可能不可得、OI或仅~2023起短样本）

**CTO诚实判断：** 纯永续方向性突破Sharpe>1把握仍不高；regime-first长TSMOM是目前最有依据的一搏；若它与OI都不成，将用数据重新摆上market-neutral carry。

**工具/框架借鉴调研已补做（DEC-056，源于Founder指出缺失）：** `00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v1.md`
- 立即采纳方法论：**Triple Barrier(标准退出框架) + Meta-Labeling(=regime-first学术正名) + 事件采样**；取代手写退出。P1-04即meta-labeling手动实例。
- Phase 2参考：Freqtrade(持仓/风控)、NautilusTrader(事件驱动/对账)；现在不建。
- agent编排自动化(解决手工搬运Codex)：现保持文件式handoff，重型编排(A2A/LangGraph)留Phase 2，避免风险B。
- 原则：不自己发明→先学→借鉴→集成→最后才重写。

**P1-04 regime-first 长TSMOM = PASSED / EXPLORATORY（DEC-060，项目首个过门槛）：**
- 净Sharpe 1.327 / 原始MaxDD 41.31%(<50%) / WF三段1.199/1.374/1.460全>1无衰减 / 392段探索级 / 18-18测试 / Holdout未访问
- ADX过滤真有效(对照无过滤Sharpe1.06/MaxDD67%→ADX+0.265/-26pp)；验证regime-first框架方向对
- ⚠️ 2022 -23.72%/Sharpe-1.67：根因=**ADX只测趋势强度不分牛熊方向**，熊市反弹被误判上升趋势→做多挨打。缺"高周期牛熊方向"轴
- 计数：PASSED不增失败；独立Alpha维持5/8
- 决断：**不进Holdout**(探索级+2022未解)；**不立即加方向层修2022**(那是局部修补)
- 报告：`04_AI_TEAM/CODEX_TASKS/REPORT_P1_04_TSMOM_REGIME_LONG.md`

**P1-03 OI数据核查：通过。** OI/LSR/taker 1,554,269行无缺失；清算不可得。OI属地基后的下一新信号，暂不立项/不耗配额。

**P1-05 两轴归因 = 已完成（DEC-062，诊断/不计失败/未碰Holdout/5-5测试）：**
- 纠正Claude假设1：2022非"几乎全是熊市反弹"(trend_up_bear仅64.7%<80%)；更准确=正edge几乎全在宏观牛市，两宏观熊市格解释**94.4%亏损**
- 纠正Claude假设2：Sweep非"只在震荡有效"(无证据)；其有效格像"牛市回调/震荡后反弹"，但v4带条件选择→保留为候选机制日后单测，不复活
- 全部单格<300=INSUFFICIENT，仅定位用
- 报告：`06_RESEARCH/RESULTS/20260606_regime_attribution.md`

**下一步=P1-04+宏观牛市过滤（数据驱动的铁律第4步，DEC-062）已预登记+出任务：**
- 预登记`HYPOTHESES/v6_tsmom_regime_long_v4.md`、任务`TASK_P1_06_TSMOM_MACRO_BULL.md`
- 唯一新变量=高周期牛熊轴(日线SMA200,无前视)；只在宏观牛市做多、转熊平多；其余继承P1-04冻结
- 预期消除2022 -23.72%；门槛净Sharpe>1 AND 原始MaxDD<50%；遵循Research Protocol v1.2(规则式状态门控[不报精确率/召回率,改覆盖率/保留率/状态间收益差异]/两轴/退出暂不叠三屏障守单变量)
- 过拟合纪律：剔除已知亏损宏观熊市段必然改善样本内=预期非证据；真证据=WF+Holdout；样本约281笔仍探索级，须后续扩品种/历史
- 计数：TSMOM家族细化，失败不增独立Alpha(仍5/8)；通过=探索级不进Holdout
- ⏸️ P1-03 OI仍暂挂(地基后的新信号)；Sweep"牛市回调反弹"列候选
【需要Codex：TASK_P1_06（P1-05已完成）】

**并行支线（DEC-059）：工具/框架/Skill 借鉴集成调研 —— ✅ 已完成并回灌，经 Codex 7点评审修订（DEC-061，2026-06-07）。**
- 产出：`V5_TOOL_INTEGRATION_PLAN_v2`（已**重写为干净 v2.1**：删失效正文+折叠更正+补来源表）
- 回灌结果（Founder 确认 + Codex 评审）：
  - **Research Protocol 升级 v1.2**（第十节）：三屏障（**仅方向性事件策略默认基准**，carry/资金费率按机制失效退出）/ **规则式状态门控**（前身"手动Meta-Label"，指标用覆盖率/保留率/收益差异，**去精确率/召回率**防过拟合）/ Purged-Embargo CV（调参时生效）/ 两轴状态分类标准 / 借鉴前置纪律。
  - **库纪律**：Triple Barrier / Purged CV / 分类器一律**自实现可审计小函数**，借鉴 MLFinPy 作参考，**不引入硬依赖**。
  - **D38 反转**：quant-research-platform、trading-devbox 两 Skill **否决**（ClawHub 脱节+不可审计）。
  - **协作自动化（D级，已确认）**：Claude 经 Desktop Commander 直接调用 Codex CLI；护栏=七问前置/保留文件留痕/成本上限/D级仍人工确认。
  - **事实更正**：NautilusTrader=**LGPL-3.0**（原误 BSL 1.1）；Freqtrade 最新=**2026.4**（原误 2026.1）。
  - **延后/排除**：VectorBT PRO（$20/月）；Mem0/Graphiti 不引入；Freqtrade/Nautilus 维持 Phase 2；分数差分/trend-scanning/MCP/CrewAI/AutoGen 标"主动排除/延后"。
- **与 P1-05 的关系**：工具报告旧稿单轴(DI±)分类器**已否决/删除**；P1-05 按 `TASK_P1_05` §2 两轴规格执行（已完成，见下方 DEC-062）。
- **研究顺序（工具不打断主线）**：P1-05 归因 → edge 地图 → 选下一策略 → 仅方向性事件策略才用三屏障 → purge/embargo + 退出敏感性。本回灌仅改治理文档，与 Codex 的 CODE/RESULTS/REPORT 无冲突；Memory Core 写入串行（DEC-030）。

**下一步：P1-05 归因已完成（DEC-062）→ 跑 P1-06（P1-04+宏观牛市过滤）。**【需要Codex：TASK_P1_06】

### L2阶段审计

- 审计结论：CONDITIONAL GO → Phase 0B
- P0：0
- P1：5（替代Holdout、旧状态文档、避免治理扩张、回测自动测试、失败知识提炼）
- 报告：`00_PROJECT_MANAGEMENT/STAGE_AUDITS/L2_AUDIT_PHASE_0A_2026-06-06.md`

### 第二候选假设1H核查

- BTC：383
- ETH：360
- SOL：269
- 品种事件：1,012
- 跨品种同刻去重：889
- 档级：确认级样本可行性
- 风险：2021与2024占62.35%，2022仅13次
- Holdout：物理截断，未查看1H信号或收益

报告：`06_RESEARCH/RESULTS/V2_1H_SAMPLE_FEASIBILITY_REPORT.md`

知识库：`02_KNOWLEDGE_BASE/STRUCTURE_SETUP_FAILURE_LESSONS_v1.md`（v1/v2）、`02_KNOWLEDGE_BASE/SWEEP_SIGNAL_FAILURE_LESSONS_v2.md`（v3/v4/v5，2026-06-06新增）

---

## 6. 关键约束

- 每月预算：约1000元
- 可用时间：晚9点~2点（有帮带孩子时），约1小时（无帮带时）
- 交易本金上限：30000元
- 用户技术背景：无
- 用户角色：Founder，纯做最终确认
- 首要风险：风险C——长期停留在讨论层，没有真实实验

---

## 7. 工作主场说明

**Cowork（主工作区）：** 日常任务执行、文件读写、调研、文档治理  
**Chat（历史归档）：** 本对话保留作为项目历史记录，不再作为主工作区  
**切换时机：** 已完成，从本次更新后所有新任务在 Cowork 执行

---

## 8. 新对话启动清单

新对话开始时，Claude 必须按顺序读取：

```
1. 01_MEMORY_CORE/CURRENT_STATE.md        ← 当前状态
2. 01_MEMORY_CORE/DECISION_LOG.md         ← 已确认决策
3. 01_MEMORY_CORE/PROJECT_CONTEXT.md      ← 项目背景
4. 00_PROJECT_MANAGEMENT/PROJECT_OPERATING_STATE.md  ← 目录状态
5. 00_PROJECT_MANAGEMENT/PROJECT_MASTER_PLAN_v2.md   ← 任务手册（确认当前任务队列）
```

读完后向用户确认当前阶段和本次目标，再开始工作。

---

# ===== 文档2/6：DECISION_LOG.md（全文）=====

# DECISION_LOG.md

**版本：** 1.0  
**初始化时间：** 2026-06-02  
**写入依据：** MEMORY_EXTRACTION_PROTOCOL v1.0  
**说明：** 本文件记录所有经用户明确确认的决策。对话中的分析、建议、推演不得写入。每条决策标注来源、时间、影响范围。

---

## 格式说明

```
[DEC-XXX]
决策内容：
决策时间：
来源：
影响范围：
状态：ACTIVE / DEPRECATED
```

---

## 本项目自身决策

---

**[DEC-001]**
```
决策内容：工具链选型确认
  主控AI：Claude Desktop
  执行AI：Codex
  本地文件系统访问：Desktop Commander v0.2.41
  知识管理：Obsidian（含Sync）
  文档检索：Context7
决策时间：2026-06-01（Phase 0A 启动时）
来源：用户确认，本项目启动约束
影响范围：所有AI协作任务的工具选择
状态：ACTIVE
```

---

**[DEC-002]**
```
决策内容：项目目录确认
  路径：/Users/yaomingyu/Documents/AI_QUANT_COMPANY
  结构：00~10号目录 + 99_TEMP
决策时间：2026-06-01（Phase 0A 启动时）
来源：用户确认
影响范围：所有文件的存放位置
状态：ACTIVE
```

---

**[DEC-003]**
```
决策内容：MEMORY_EXTRACTION_PROTOCOL v1.0 作为信息提炼协议
  所有历史资料提炼必须遵守该协议
  信息等级：DECISION > FACT > EXPERIENCE > HYPOTHESIS > DEPRECATED > CONFLICT > UNKNOWN
  历史资料默认为 HYPOTHESIS，未经验证不得作为架构依据
决策时间：2026-06-01（TASK 2 完成后）
来源：用户确认
影响范围：所有历史文档的读取、提炼、归档操作
状态：ACTIVE
```

---

**[DEC-004]**
```
决策内容：项目定位升级
  从：AI Quant Company（公司概念）
  到：AI-Native Quant Research Operating System（研发操作系统概念）
  North Star 不变：找到可持续产生Alpha的方法，最终实现自动化量化交易
  当前阶段目标：建立研究能力基础设施，而非直接研发交易系统
决策时间：2026-06-02（三方论证收敛后）
来源：用户确认，ChatGPT + Claude 三方论证结论
影响范围：项目所有阶段规划、优先级判断、资源分配
状态：ACTIVE
```

---

**[DEC-005]**
```
决策内容：Phase 0A 重新定义
  名称：Research Capability Infrastructure（研究能力基础设施）
  验收标准（五条，全部满足方可进入下一阶段）：
    1. Memory恢复能力：新对话能恢复项目上下文
    2. Research Protocol存在：知道如何执行实验
    3. Backtest Framework可运行：能产生可判断的数字
    4. 第一个假设被定义：具体的、可验证的研究对象
    5. 第一个研究闭环完成：无论结论好坏，完整走完一遍
  第5条为最重要条件，前四条是能力，第5条证明能力真实存在
决策时间：2026-06-02（三方论证收敛后）
来源：用户确认，ChatGPT + Claude 三方论证结论
影响范围：Phase 0A 所有工作的方向和优先级
状态：ACTIVE
```

---

**[DEC-006]**
```
决策内容：角色分工确认
  用户：Founder + 最终决策者，纯粹做最终确认，不参与技术判断
  Claude：CTO，负责架构设计、规划、任务分解、阶段判断、文档治理
  Codex：工程执行，负责代码实现、部署、调试
  Claude → Codex 交接：必须包含目标、约束条件、验收标准、禁止事项
决策时间：2026-06-02
来源：用户确认
影响范围：所有任务分配和协作流程
状态：ACTIVE
```

---

**[DEC-007]**
```
决策内容：资源约束确认（影响技术选型和阶段节奏）
  每月预算：约1000元（研发阶段，无利润产出期）
  交易本金路径：模拟盘验证 → 1000元小资金 → 10000元 → 最大30000元
  风险容忍：1000本金最大亏损30%，10000本金最大10%，30000本金最大3%
  服务器：MacBook Pro M1 + Windows i7-11700/16G + 腾讯云轻量2核4G（新加坡）
  终态目标：全自动无人值守实盘，保留手动停止权
决策时间：2026-06-02
来源：用户提供
影响范围：技术选型、策略方向、风控参数设计
状态：ACTIVE
```

---

## 来自历史文档的确认决策（来源：D34 决策记录）

以下决策来自 V4 时期历史文档 D34，经用户在 2026-06-02 逐条确认，升级为当前项目 DECISION。

---

**[DEC-008]**
```
决策内容：PostgreSQL 为唯一权威状态源
  所有巡检、复盘、评估、风控检查必须直接从 PostgreSQL 读取
  _positions 字典降级为缓存，不得作为风控输入
  CSV 文件降级为历史快照，仅供参考
历史决策时间：2026-05-07（D34 AD-1）
当前项目确认时间：2026-06-02
来源：D34：决策记录.md，Ghost Position 事故根因验证
影响范围：所有涉及持仓状态读取的模块
状态：ACTIVE
```

---

**[DEC-009]**
```
决策内容：禁止同向覆盖机制
  新信号到达时，如已有同币种同方向活跃持仓，直接拒绝新信号
  后续通过 REPLACED 状态实现有序替换（先平旧仓→记录PnL→再开新仓）
  完整 Lifecycle Engine 建立前，禁止任何形式的自动持仓替换
历史决策时间：2026-05-08 深夜（D34 AD-4）
当前项目确认时间：2026-06-02
来源：D34：决策记录.md，与 D10 CM-1 互相印证
影响范围：信号处理逻辑、持仓生命周期管理
状态：ACTIVE
```

---

**[DEC-010]**
```
决策内容：持仓唯一标识改用全局唯一 trade_id
  废弃以 symbol_direction 作为持仓唯一标识
  每个持仓必须有全局唯一 trade_id，格式：{symbol}_{direction}_{timestamp}_{hash4}
  log_trade() 改为 WHERE trade_id=? 精确匹配
  废弃 ORDER BY timestamp DESC LIMIT 1 粗粒度匹配
历史决策时间：2026-05-08 深夜（D34 AD-5）
当前项目确认时间：2026-06-02
来源：D34：决策记录.md，与 D10 CM-3 互相印证
影响范围：数据库设计、交易记录函数、持仓查询逻辑
状态：ACTIVE
```

---

**[DEC-011]**
```
决策内容：建立 Reconciliation Loop + Orphan Detection
  每轮 Phase 1 风控检查启动前，强制执行 Reconciliation Loop：
    PostgreSQL 活跃持仓与 _positions 缓存逐笔对账
    发现差异立即触发 CRITICAL ALERT 推送 Telegram
  建立 Orphan Detection：
    持仓超过2轮扫描未被风控检查，自动标记 ORPHANED 并告警
历史决策时间：2026-05-08 深夜（D34 AD-6）
当前项目确认时间：2026-06-02
来源：D34：决策记录.md，与 D10 CM-5/CM-6 互相印证
影响范围：风控引擎设计、告警系统
状态：ACTIVE
```

---

**[DEC-012]**
```
决策内容：PROJECT_MASTER_PLAN_v2.md 作为项目主执行手册
  v1 计划书粒度不足（只有"做什么"，缺少执行人、验收标准、依赖关系）
  v2 包含：全局路线图、16模块全景图、每任务详细规格、10个大节点确认清单
  v2 同时作为 Claude 的任务手册和 Founder 的决策依据
  CLAUDE.md 启动协议已更新为读取5个文件（新增 PROJECT_MASTER_PLAN_v2.md）
决策时间：2026-06-04
来源：Dispatch 对话（Founder 明确要求）
影响范围：所有后续对话启动协议、任务执行依据
状态：ACTIVE
```

---

**[DEC-013]**
```
决策内容：项目协作架构原则确认
  任务隔离原则：每个对话/Agent 只做一类职能，上下文短、成本低、不混乱
  执行顺序原则：先验证策略 → 再建系统 → 再扩团队（不可颠倒）
  多模块概念澄清：开发阶段工具（Claude+Codex已覆盖）vs 系统运行模块（按阶段建设）
  Dispatch 为跨会话协调频道，Project 对话为主工作区，文件为两者共享记忆
决策时间：2026-06-04
来源：Dispatch 对话（Founder 认可）
影响范围：工作方式、对话分工、后期 Agent 扩展时机
状态：ACTIVE
```

---

**[DEC-014]**
```
决策内容：回测框架选用 VectorBT
  主回测引擎：VectorBT（Phase 0A/0B/1 全程使用）
  选型依据：M1 MacBook 上百万级订单70-100ms；适合假设统计验证；外部调研推荐
  补充：Phase 1 后视需要引入 Backtrader 做事件驱动二次验证；NautilusTrader 留至 Phase 2/3
决策时间：2026-06-04
来源：Founder 明确确认（本次对话）
影响范围：所有回测任务的工具选择
状态：ACTIVE
```

---

**[DEC-015]**
```
决策内容：实盘资金阶梯最大亏损阈值（修正版）
  第一档：1,000元本金，最大亏损 300元（30%）
  第二档：10,000元本金，最大亏损 1,000元（10%）
  第三档：30,000元本金，最大亏损 1,500元（5%）
  设计原则：绝对亏损容忍额递增（300→1000→1500），占比递减（30%→10%→5%）
  原900元值（3%）被修正：绝对值低于上一档，不符合资金管理直觉
决策时间：2026-06-04
来源：Claude独立评估（Founder授权Claude决定）
影响范围：Phase 3 实盘风控参数
状态：ACTIVE
```

---

**[DEC-016]**
```
决策内容：操作模式升级——减少Founder参与，提升自动化程度
  Claude直接执行：数据下载、环境安装、回测执行、结果分析（via Bash/Python）
  Codex执行：复杂系统代码，通过文件自动交接，无需Founder中转
  Founder参与：仅D级决策节点（阶段跨越、资金操作、重大架构变更）
  禁止：让Founder充当信息传递中间人
决策时间：2026-06-04
来源：Founder明确授权（减少参与、给Claude最高执行权限）
影响范围：所有后续任务的执行方式和协作流程
状态：ACTIVE
```

---

**[DEC-017]**
```
决策内容：目录结构方案——保持现有结构，新结构为Phase 0B目标
  当前生效结构：00_PROJECT_MANAGEMENT / 01_MEMORY_CORE / 03_RAW_INBOX / 99_TEMP
  架构v2 §14 新结构（00_GOVERNANCE/01_MEMORY/等）降级为「Phase 0B迁移目标，未生效」
  CONSTITUTION.md 暂存于 00_PROJECT_MANAGEMENT（不移动目录，Phase 0B统一执行）
决策时间：2026-06-04
来源：Founder确认（外部评审后决策）
影响范围：架构§14、计划书归档路径、CONSTITUTION存放位置
状态：ACTIVE
```

---

**[DEC-018]**
```
决策内容：样本量门槛——双层制
  ≥500次 = 确认级（可作进实盘候选）
  300–500次 = 探索级（仅初步结论，禁止进实盘，须扩样本后复测升级）
  <300次 = 不成立（换Setup或并品种）
决策时间：2026-06-04
来源：Founder确认（外部评审后决策）
影响范围：架构§7.2/§17、计划书阶段1验收标准、所有假设验证门槛判定
状态：ACTIVE
```

---

**[DEC-019]**
```
决策内容：交易类型——U本位永续合约
  回测/风控/成本/对账全程必须建模资金费率(funding rate，每8小时结算)
  回测/风控必须建模强平价距(liquidation price)和强平风险
  第一个回测建议使用1x杠杆隔离信号纯度，再做杠杆敏感性对比
  杠杆上限为开放参数（Phase 3实盘前由Founder设定，建议初期≤3x）
  任一持仓被强平 = 重大事故，触发系统暂停等Founder指令
决策时间：2026-06-04
来源：Founder确认（外部评审后决策）
影响范围：架构§7.2/§8/§11/§17、计划书阶段2/3、回测脚本设计、风控模块
状态：ACTIVE
```

---

**[DEC-020]**
```
决策内容：架构v2 + 计划书v2.1 正式冻结
  AI_QUANT_COMPANY_ARCHITECTURE_v2.md → 状态: FROZEN 2026-06-04
  PROJECT_MASTER_PLAN_v2.md（v2.1）→ 状态: FROZEN 2026-06-04
  架构文件另存为 CONSTITUTION.md（位于 00_PROJECT_MANAGEMENT，DEC-017）
  下一个交付物：第一个研究闭环结论（非新文档）
决策时间：2026-06-04
来源：Founder授权（两轮独立评审完成后冻结）
影响范围：所有后续工作的执行依据
状态：ACTIVE
```

---

**[DEC-021]**
```
决策内容：Claude/Codex 分工边界——成本驱动，非能力驱动
  背景：Claude（Cowork）和 Codex 在能力上可以相互替代；分工依据是成本和偏向，不是功能差异
  
  核心原则：
    Claude（Cowork/API）：高成本，偏推理/判断/规划；用于高价值、需要深度理解的工作
    Codex（订阅额度高）：低边际成本，偏大量代码生成/迭代；用于执行密集型、重复性高的工作
  
  Claude 直接执行（无需交给 Codex）：
    - 文档读写、架构分析、规划、研究设计
    - 小规模 Python 脚本（≤50行，通过 Desktop Commander 在 Mac 上运行）
    - 数据分析和结果解读（读取文件、输出结论）
    - 任何需要架构判断的工作
    - 一次性验证脚本、环境检查
  
  Codex 执行：
    - 复杂 Python 实现（多文件，>100行，需要大量迭代调试）
    - 回测脚本完整实现（含信号检测器、Walk-Forward框架）
    - 量化环境配置与依赖安装
    - Phase 2 所有生产级系统代码
  
  判断规则（按顺序）：
    1. 任务主要需要「判断和推理」→ Claude
    2. 任务可以用50行以内代码完成且一次性 → Claude（Desktop Commander）
    3. 任务需要大量代码编写+迭代调试，或超过100行 → Codex
    4. 成本敏感的重复性执行（将运行多次）→ 优先 Codex
  
  Desktop Commander 在 Mac 上的执行能力（2026-06-05 确认）：
    - start_process 可在用户 Mac 上执行任意 shell 命令
    - Claude 可通过此能力直接运行 Python 脚本，无需通过 Codex
    - 此能力作为「Codex 失败退路」和「小任务直接执行通道」

决策时间：2026-06-05
来源：Founder 在对话中明确说明原因；Claude 整理为决策
影响范围：所有后续任务的执行人分配；替代 DEC-006/DEC-016 中对分工的模糊描述
关联：补充 DEC-016（操作模式升级），不废弃
状态：ACTIVE
```

---

**[DEC-022]**
```
决策内容：三级项目审计体系（长期制度）

L1 月度轻量审计：
  - 频率：每月1日凌晨4点自动执行（定时任务：ai-quant-monthly-audit）
  - 执行人：Claude（Sonnet，自动）
  - 覆盖：进度真实性/风险状态/资源消耗/决策健康度/文档时效/阶段停滞
  - 输出：09_OPERATIONS/MONTHLY_REVIEW/MONTHLY_AUDIT_[YYYY-MM].md
  - 同时生成：Opus 深度审计包 OPUS_PACKAGE_[YYYY-MM].md

L2 阶段深度审计：
  - 触发：每周一凌晨4点自动检测阶段变化（定时任务：ai-quant-weekly-monitor）
  - 执行人：Claude（Sonnet，自动）+ Opus 4.8（可选，用户打开 Opus 粘贴审计包）
  - 覆盖：11个维度完整审计（方向/假设/决策/文档/进度/风险/资源/债务/机会成本/知识/外部依赖）
  - 输出：00_PROJECT_MANAGEMENT/STAGE_AUDITS/L2_AUDIT_[阶段]_[日期].md
  - 规则：L2 报告是阶段跨越的前提条件，P0 问题未解决不得进入下一阶段

L3 紧急审计：
  - 触发：每周一凌晨4点自动检测风险信号（由 ai-quant-weekly-monitor 兼管）
  - 触发条件（任一）：连续3次假设失败 / 14天无实验执行 / 止损条件接近 / Founder主动要求
  - 输出：00_PROJECT_MANAGEMENT/STAGE_AUDITS/L3_EMERGENCY_[日期].md

关于 Opus 4.8 的使用：
  - 定时任务使用 Sonnet（当前工作模型），无法直接调用 Opus
  - 每次 L1/L2 自动生成「Opus 审计包」文件，用户打开 Opus 粘贴即可（1分钟内完成）
  - 建议在以下场景使用 Opus 审计包：L1 报告评分为🔴时 / 每次阶段跨越时 / L3 触发时

定时任务文件位置：
  - /Users/yaomingyu/Claude/Scheduled/ai-quant-monthly-audit/SKILL.md
  - /Users/yaomingyu/Claude/Scheduled/ai-quant-weekly-monitor/SKILL.md

注意事项：
  - 定时任务需要 Cowork 应用保持运行；应用关闭期间到期的任务在下次启动时执行
  - 审计报告只输出，不自动修改 DECISION_LOG 或 Memory Core

决策时间：2026-06-05
来源：Founder 提出需求，Claude 设计并实施
影响范围：项目长期治理，所有后续阶段
状态：ACTIVE
```

---

**[DEC-023]**
```
决策内容：Research Protocol v1.0 正式确认
  文件位置：06_RESEARCH/RESEARCH_PROTOCOL_v1.md
  Founder 确认内容：
    - 实验版本命名规则（v5_[setup]_[方向]_v[N]格式）✅
    - 数据三分（60训练/20验证/20 Holdout，Holdout封存一次性原则）✅
    - 评估门槛（Sharpe>1.0，触发次数双层门槛 DEC-018）✅
    - Red Team 自查清单（10项，宣布成功前强制执行）✅
  Phase 0A 验收条件2：Research Protocol 存在 → ✅ 满足
决策时间：2026-06-05
来源：Founder 明确确认
影响范围：所有 Phase 0A/0B/1 研究实验
状态：ACTIVE
```

---

**[DEC-024]**
```
决策内容：首个Setup样本扩展优先并入ETH/USDT 4H
  - ETH使用与BTC完全相同的Liquidity Sweep + CHoCH + FVG语义和参数
  - 保持4H周期，不为凑样本降至1H或放宽三重确认条件
  - BTC与ETH单品种结果必须分别报告，合并结果仅用于样本可行性与组合评估
  - 正式回测仍须处理两品种相关性、资金费率和永续合约成本
决策时间：2026-06-06
来源：Founder确认0A-NEW2建议方案A
影响范围：0A-NEW2样本扩展、0A-5首个假设定义、0B首个研究闭环
状态：ACTIVE
```

---

**[DEC-025]**
```
决策内容：首个Setup的止损与重复入场口径
  - 看涨交易止损采用 Sweep K线最低价 low[t_sweep]，不采用此前20根K线的ref_low
  - 同一品种同一signal_time只允许一次入场
  - 多个Sweep汇聚到同一入场时刻时，保留时间上最近的Sweep
  - 样本量与回测统计均按“品种 + signal_time”作为唯一交易事件
决策时间：2026-06-06
来源：Founder明确确认
影响范围：0A-5首个假设定义、0B回测实现、样本量统计口径
状态：ACTIVE
```

---

**[DEC-026]**
```
决策内容：SOL/USDT 4H纳入首个探索级假设候选范围
  - SOL使用与BTC/ETH相同的信号语义、参数、4H周期和Daily EMA200 Regime
  - BTC+ETH在Regime过滤后仅244次，不满足DEC-018最低门槛
  - 加入SOL后按“品种 + signal_time”统计为315次，达到探索级
  - 三品种必须分别报告，组合结果不得掩盖单品种表现和相关性风险
决策时间：2026-06-06
来源：Founder明确确认
影响范围：0A-5首个假设定义、0B首个研究闭环
状态：ACTIVE
```

---

**[DEC-027]**
```
决策内容：首个验证假设v5_sweep_choch_fvg_bull_v1正式预登记
  - 品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多，1x
  - Regime：前一完整UTC日收盘价 > Daily EMA200
  - 信号：Liquidity Sweep → Bullish CHoCH → FVG Retrace
  - 止损：Sweep K线最低价
  - 止盈：50%在1R，剩余50%在2R；首轮不启用跟踪止盈
  - 去重：同品种同signal_time一次入场；重叠Sweep保留最近者
  - 持仓冲突：同品种已有多仓时拒绝后续同向信号
  - 同K线冲突：止损优先于止盈
  - 完整成本：手续费、滑点、历史资金费率，不得按零处理
  - 失效条件与Walk-Forward门槛按预登记文件执行，不得根据结果修改
文件：06_RESEARCH/HYPOTHESES/v5_sweep_choch_fvg_bull_v1.md
决策时间：2026-06-06
来源：Founder明确确认完整预登记方案
影响范围：Phase 0A验收条件4、0B首个研究闭环
状态：ACTIVE
```

---

**[DEC-028]**
```
决策内容：第二个候选假设改用1H周期做独立验证
  - 仅将周期从4H改为1H，信号语义、参数、品种、Daily EMA200 Regime、止损止盈和成本规则保持不变
  - 1H视为新假设版本，不继承4H实验结论
  - 必须先执行1H永续数据样本量与持仓冲突可行性核查，再提交完整预登记
  - 不得为凑样本调整20/10/2/20参数；这些参数在1H代表更短实际时间，是本版本主动测试的单一变化
  - 不使用4H版本已结构性接触的Holdout宣告1H成功
决策时间：2026-06-06
来源：Founder明确确认
影响范围：第二个研究假设、Phase 0B研究任务
状态：ACTIVE
```

---

**[DEC-029]**
```
决策内容：第二个验证假设v5_sweep_choch_fvg_bull_v2正式预登记
  - 唯一变量：周期4H改为1H
  - 信号参数20/10/2/20、三品种、Daily EMA200 Regime、止损止盈、成本与冲突规则全部保持不变
  - 前80%数据候选事件1012次；跨品种同刻去重889次
  - 最后20%在信号计算前物理截断，训练/验证/WF通过前不得访问
  - 成功与失效门槛按预登记文件执行，不得根据结果修改
文件：06_RESEARCH/HYPOTHESES/v5_sweep_choch_fvg_bull_v2.md
决策时间：2026-06-06
来源：Founder确认1H作为第二个独立假设；样本核查达到继续条件
影响范围：第二个研究闭环
状态：ACTIVE
```

---

**[DEC-030]**
```
决策内容：Phase 0A → Phase 0B 正式跨越
  - Phase 0A 五项验收条件全部满足（DEC-005）
  - L2 阶段审计结论：CONDITIONAL GO（P0=0，P1=5）
  - 两个研究闭环均已完成并归档（均 FAILED，符合正常量化研究流程）
  - 连续失败计数：2/8（距止损条件 ≥8 还有充足空间）
  - Phase 0B 目标：第三个研究闭环（降维Sweep单事件研究）+ 目录重构
  - 下一研究方向：停止微调三重确认链，改为验证 Liquidity Sweep 单事件
    在 Daily EMA200 Regime 过滤后，Sweep 后 N 根K线未来收益分布是否显著偏正

  L2 审计 P1 问题（进入 Phase 0B 早期处理，不阻塞跨越）：
    P1-1：替代 Holdout 污染风险的保护机制
    P1-2：旧状态文档存在过期快照
    P1-3：避免治理文档继续扩张
    P1-4：回测自动测试完整覆盖
    P1-5：失败知识系统化提炼

  协作规范补充（Claude/Codex共用目录）：
    - Codex 禁止覆盖写入 Memory Core 文件（DECISION_LOG、CURRENT_STATE、PROJECT_CONTEXT）
    - Codex 的决策性输出写入执行报告，由 Claude 审阅后决定是否升级到 Memory Core
    - Claude 在写入任何共享文件前必须先读取确认当前状态

决策时间：2026-06-06
来源：Founder 明确确认（「是」）
影响范围：所有后续工作进入 Phase 0B 框架
状态：ACTIVE
```

---

**[DEC-031]**
```
决策内容：L3审计结论确认 + 第四个假设方向
  L3审计结论：项目不暂停，继续选项A（精化Regime）
  
  失败模式诊断（来自三次实验）：
    - Sweep信号本身有效（t+6/t+12统计显著）
    - 但效应高度集中于2021年，2019-2020和2022均为负
    - Daily EMA200作为Regime过滤器不足以排除无效时期
  
  第四个假设的唯一变量（单变量原则）：
    在原有「Daily close > Daily EMA200」条件上，
    叠加「BTC 30日滚动收益率 > 0%」作为动量确认条件
    （无需新数据，可从现有价格数据计算）
  
  逻辑依据：
    Liquidity Sweep在持续上涨的市场中才会被主力快速吸收；
    在仅满足EMA200但月度动量为负的环境中，Sweep更容易延续下跌。
    两条件合并后过滤掉2019-2020下跌期和2022熊市的大部分无效信号。
  
  样本预估：
    748个Regime过滤后事件中，额外加入30日正收益过滤，
    预估保留约55-65%（~410-485个事件），探索级或接近确认级。
    
决策时间：2026-06-06
来源：Founder确认选项A，Claude设计具体方案
影响范围：第四个研究闭环（v5_sweep_regime_bull_v4）
状态：ACTIVE
```

---

**[DEC-032]**
```
决策内容：测试做空镜像信号（Bearish Liquidity Sweep）
  背景：此前4次实验全部仅测试做多（Bullish Sweep）。
        永续合约支持双向交易，做空镜像未经测试是研究覆盖缺口。
  
  做空信号定义（Bearish Sweep）：
    价格向上突破近期N根K线的最高价（扫荡上方流动性），
    但收盘价收回该高点下方。
    精确条件：high[i] > max(high[i-20:i-1]) AND close[i] < max(high[i-20:i-1])
  
  熊市 Regime（双层，镜像于v4做多Regime）：
    条件1：各品种前一完整UTC日收盘价 < 该日Daily EMA200
    条件2：BTC前一完整日30日对数收益率 < 0%
  
  研究问题：在Bearish Regime下，Bearish Sweep后第6/12/24根4H K线
    的未来收益率是否显著为负（即做空有正期望）？
  
  单变量变化：相比v4（做多），唯一变化是方向取反（信号+Regime均镜像）。
              这不是参数调整，是独立的新方向假设。
  
  执行人：Codex
  版本号：v5_sweep_regime_bear_v5
决策时间：2026-06-06
来源：Founder确认（「同意」）
影响范围：第五研究闭环，可能影响后续双向策略设计
状态：ACTIVE
```

---

**[DEC-033]**
```
决策内容：v4策略失败根因诊断与下一研究方向确定
  诊断结论（Claude判断，Founder授权CTO日常决策，非D级）：
    - v4事件研究统计信号真实（三层校验全通过）
    - v4策略失败根因：固定止损+1R/2R止盈与t+24信号周期系统性错位
    - 成本侵蚀：手续费+资金费率消耗毛利润54.64%，低Expectancy策略无法覆盖
    - SOL单品种净亏损（-5.65%），但不单独剔除，通过子集对比验证
  
  已确定的下一步研究方向（Claude决定，不需Founder确认）：
    v6：时间退出（t+12）替代固定1R/2R止盈，相同信号+Regime+止损
    v6b：更宽止损（ref_low替代sweep_low），配合t+12时间退出
    v7：第三层Regime（BTC距90日高点回撤<20%），事件研究级
    诊断：止损触发时机分析（v9），持仓期敏感性（t+6/t+24，v8）
  
  不纳入双向策略：
    v5 Bearish Sweep失败（非重叠后三窗口全部不显著），
    明确不将做空腿加入当前候选策略

决策时间：2026-06-06
来源：Claude（CTO）自主判断，基于四份Codex执行报告
影响范围：Phase 0B第6-11轮研究任务
状态：ACTIVE
```

---

**[DEC-034]**
```
决策内容：0B8/0B9/0B10/0B11 结果回收结论
  0B8诊断：t+24最优（三品种Sharpe 1.31，BTC+ETH Sharpe 1.11），但MaxDD均超25%门槛，不计失败
  0B9诊断：止损在第1根K线触发（中位），80%止损在t+6前发生，止损过早是主因，不计失败
  v6（sweep_low+t+12）策略：Sharpe 0.87/0.86，MaxDD 36%/27% → FAILED（5/8）
  v6b（ref_low+t+12）策略：Sharpe 1.22/0.92，MaxDD 28%/23% → FAILED（6/8）
  v7（三层Regime事件研究）：主检验PASSED，但2022事件无改善，WF第二段无改善 → 不计失败
  当前失败计数：6/8，再失败2次触发L3全面审计
决策时间：2026-06-06
来源：Dispatch结果回收（Claude CTO基于4份Codex报告分析）
影响范围：研究方向、失败计数、下一步任务
状态：ACTIVE
```

---

**[DEC-035]**
```
决策内容：ref_low 语义纠错——ref_low 对多头是更紧止损，不是更宽止损
  Bullish Sweep定义：sweep_low < ref_low（sweep低于参考低点才构成扫荡）
  对多头，止损价越高意味着越靠近入场价，风险距离越小 = 更紧
  v6b 使用 ref_low 止损，止损比 v6（sweep_low）更紧，平均风险距离从2.33%缩至1.37%
  后续任何文档、对话、任务规格中，禁止将 ref_low 称为"更宽止损"
决策时间：2026-06-06
来源：Codex REPORT_0B10 明确纠错
影响范围：后续所有止损参数设计与表述
状态：ACTIVE（永久语义约束）
```

---

**[DEC-040]**
```
决策内容：0B13（t+24 + ref_low止损策略回测）明确暂不执行
  判断依据：
    1. MaxDD预期变差：ref_low止损（仓位更大）× t+24持仓（更长）叠加，
       MaxDD大概率高于v6b的28.45%，而非更低。0B13若执行大概率失败（7/8），
       但不能带来新信息。
    2. WF2稳定性缺口未解决：所有版本（v4/v6/v6b/v7/0B8/0B12）Walk-Forward
       第二段均为负，止损设计优化无法解决这个时期性问题。
    3. 资源管理：当前6/8，仅剩2次机会，不应用在尚未经诊断数据支持的变体上。
  
  决定：0B13任务规格保留，但执行时机延后到以下条件满足后：
    a. 0B14 MAE分析完成，确认止损应放在的理论位置
    b. 0B16 ATR止损诊断完成，确认ATR止损是否覆盖MAE 80th percentile
    c. 基于诊断数据，重新设计止损参数，若与0B13完全一致则执行0B13，
       若需要修改则创建新任务规格
决策时间：2026-06-06
来源：Claude（CTO）基于0B12结论分析
影响范围：剩余2次策略测试机会的使用方式
状态：ACTIVE
```

---

**[DEC-036]**
```
决策内容：2022年极端熊市处理方式——改为仓位缩减，不再堆叠Regime过滤器
  背景：v4~v7七种变体，2022年事件全部亏损（最差90.91%止损率）。
        v7三层Regime过滤后2022仍无改善，方向错误。
  外部研究结论：2022年是结构性极端（恐惧指数极高），无法通过信号过滤彻底消除；
               正确处理是在高恐惧环境下缩小仓位（仓位管理问题），而非过滤信号。
  决策：停止为过滤2022而设计新Regime条件；
        Phase 1+阶段在仓位管理模块中引入市场恐惧度/波动率指标调节仓位大小。
        当前Phase 0B：记录2022为已知稳定性缺口，不因此否定信号本身。
决策时间：2026-06-06
来源：Dispatch对话，基于外部调研EXTERNAL_RESEARCH_v3 + v7失败数据
影响范围：后续所有Regime设计、Phase 1仓位管理模块
状态：ACTIVE
```

---

**[DEC-037]**
```
决策内容：短边（做空）研究独立立项，信号重新设计，不沿用Bearish Sweep镜像
  背景：v5 Bearish Sweep在非重叠校正后三窗口全部失败。
  外部研究发现：做空信号失败的根本原因是——牛市里向上突破高点是真正方向性突破，
               不是流动性抓取；镜像做多信号不适用于做空。
  推荐方向：市场中性统计套利（Sharpe 2.1+），需要独立信号设计，与做多研究线完全分离。
  决策：做空研究在多头策略通过或失败计数触发L3审计后，作为独立Phase 0B子课题启动。
        不沿用v5信号。新信号需要独立预登记和研究闭环。
        Phase 0B当前优先：先解决多头策略实现问题。
决策时间：2026-06-06
来源：Dispatch对话，基于v5失败根因分析 + EXTERNAL_RESEARCH_v3方向7
影响范围：短边研究时机和信号设计方向
状态：ACTIVE
```

---

**[DEC-038]**
```
决策内容：当前诊断队列确认（均不计失败次数），0B13暂缓
  诊断队列（按优先级）：
    1. MAE分析（最大逆势运动分析）—— 行业标准，对现有360笔交易直接统计，
       找到覆盖80%盈利交易的MAE位置，确定理论止损应在哪里
    2. 0B12无止损t+24 —— 已完成（Sharpe 1.28，MaxDD 12.06%，固定10%仓位）
    3. 波动率压缩分组分析 —— V4唯一通过IC分析的因子，外部研究验证有效
    4. ATR动态止损诊断 —— 测试3-4倍ATR止损vs结构止损的止损率差异
  
  0B13（t+24+ref_low策略回测）暂缓原因：
    - Codex建议：无止损未明显提升Sharpe，ref_low已使71.85%交易在5.18根内止损
    - 需要先完成MAE分析，确认止损应放哪里，再决定用哪种止损做策略回测
    - 当前失败计数6/8，策略测试机会极其宝贵，不能仓促用在尚未诊断清楚的变体上
决策时间：2026-06-06
来源：Dispatch对话综合判断 + Codex REPORT_0B12建议
影响范围：接下来所有Codex任务安排
状态：ACTIVE
```

---

**[DEC-039]**
```
决策内容：0B12无止损诊断结论确认
  结果：三品种Sharpe 1.28，MaxDD 12.06%（固定10%名义仓位）
         BTC+ETH Sharpe 1.06，MaxDD 7.38%
  重要约束：固定仓位与风险定仓不可直接比较，MaxDD偏低因仓位较小
  关键纠错：0B8的t+24不是"纯时间退出"，实际保留sweep_low止损（止损率68.22%，平均持仓11根）
            0B12才是真正无止损版本
  结论：信号在无止损时Sharpe 1.28 ≈ 0B8的1.31（差异来自实现差异，非信号差异）
        移除止损本身不能显著提升Sharpe；WF2仍为负（-0.44），稳定性缺口未解决
  失败计数：不变，仍为6/8
决策时间：2026-06-06
来源：Codex REPORT_0B12
影响范围：对0B8数据的语义理解修正；0B13决策依据
状态：ACTIVE
```

---

**[DEC-041]**
```
决策内容：0B14/0B15/0B16 三诊断结论归档（均不计失败次数）
  
  0B14 MAE分析结论（FACT）：
    - 盈利交易 MAE 80th percentile：4.38%（= 1.87x ATR(14)）
    - sweep_low 平均距离 2.33%：47.58% 盈利交易 MAE 超过此值 → 止损过早
    - ref_low 平均距离 1.38%：63.71% 盈利交易 MAE 超过此值 → 更严重
    - 品种分层：BTC 3.32% / ETH 4.02% / SOL 7.68%（ATR百分比形式，SOL最大）
    - 2022（5笔）：MFE均值仅0.87%，方向失效不可通过止损优化解决
    - MFE/MAE 中位数 4.30：赢家确实走得更远，止损应给足时间
    - MAE与最终收益相关性 -0.49：不完全负相关，不能凭MAE大就认为必输

  0B15 波动率压缩结论（FACT）：
    - 方案A（ATR14 < ATR50）：压缩247 vs 扩张178，t+24差值-0.06pp，p=0.5320
    - 方案B（BBW < 中位数）：压缩289 vs 扩张136，t+24差值-1.23pp，p=0.9134
    - 两方案均不显著，压缩组前6根K线止损率更高（非更低）
    - 2022事件主要落在压缩组（BBW方案：10压缩/2扩张），压缩过滤不能排除2022
    - 结论：不建议增加波动率压缩过滤层；V4的IC发现在双层Regime框架下未复现
    - 约束：不得将方案B扩张组较高均值（3.17% vs 1.94%）追认为新假设，属事后观察未显著

  0B16 ATR止损诊断结论（FACT）：
    - ATR×3.5 平均距离 8.69%：覆盖盈利MAE 96.77%，但过宽，max(ref_low,ATR×3.5)=纯ATR×3.5
    - ATR×1.9 平均距离 ≈4.1%：覆盖盈利MAE 81.45%（≈MAE 80th percentile）
    - ATR×1.9 理论可避免止损：61.43%历史止损可避免（首根K线止损：61.86%可避免）
    - 2022特征：结构止损/ATR倍数为5.76x（sweep_low）/ 13.70x（ref_low）→ 结构止损与波动完全脱节
    - max(ref_low, ATR×3.5)：在425/425事件中等同纯ATR×3.5，复合止损方案无效
    - 推荐止损方案：ATR×1.9（主测），ATR×3.5（压力测试），不使用max()复合形式

  三诊断核心发现：
    MAE法（1.87x ATR）与ATR诊断法（1.9x ATR）从不同角度收敛于同一止损距离。
    这是迄今对止损位置最强的数据依据。
    
决策时间：2026-06-06
来源：Claude（CTO）基于三份Codex诊断报告综合分析
影响范围：0B17止损参数设计，所有后续策略版本
状态：ACTIVE
```

---

**[DEC-042]**
```
决策内容：0B17策略回测预登记 — ATR×1.9止损 + t+24时间退出
  背景：三诊断完成（DEC-041），止损参数有数据支撑，DEC-040解锁条件满足。
  
  策略规格：
    - 信号：v4（Bullish Liquidity Sweep + 双层Regime：EMA200 + BTC30日动量>0）
    - 止损：entry_price - ATR(14)[t_sweep] × 1.9
             ATR使用Sweep K线可见的14根TR简单均值（无前视偏差）
    - 退出：t+24时间退出（入场后第24根4H K线收盘）
    - 仓位：1%风险定仓，风险距离 = ATR(14)[t_sweep] × 1.9
             名义仓位 = 1% × portfolio / (ATR×1.9)，平均约22.8%
    - 成本：手续费 + 资金费率（同前所有版本，不得省略）
    - 品种：BTC/USDT、ETH/USDT、SOL/USDT，4H，仅做多
    - 压力测试：同时运行ATR×3.5版本（不单独计失败，用于对比）

  预登记通过标准：Sharpe > 1.0 AND MaxDD < 25%（双指标联合门槛）
  
  失败计数：若通过 → 保持6/8；若失败 → 7/8（仅剩1次机会，触发L3全面审计准备）
  
  预期改善逻辑：
    - v6b（ref_low止损，名义仓位≈72%）：Sharpe 1.22，MaxDD 28.45%
    - 0B12（无止损，名义仓位固定10%）：Sharpe 1.28，MaxDD 12.06%
    - 0B17（ATR×1.9，名义仓位≈22.8%）：预期MaxDD 15~22%，Sharpe接近1.28
    - 风险：WF2仍为负，2022仍有方向失效，这两个问题在Phase 0B内不解决
  
  约束：
    - 不得修改信号或Regime参数
    - 不得查看Holdout
    - 仓位下限：单笔不超过100%名义仓位（ATR极小时的安全约束）
    
决策时间：2026-06-06
来源：Claude（CTO）基于DEC-040解锁条件 + DEC-041诊断数据
影响范围：消耗第7次失败机会（若失败），或证实当前策略方向可行
状态：ACTIVE
```

---

**[DEC-043]**
```
决策内容：0B17（ATR动态止损策略）结论确认 — FAILED，失败计数 6/8 → 7/8
  
  实验结果（Codex REPORT_0B17，Claude验收通过）：
    - ATR×1.9 主版本：Sharpe 0.86，MaxDD 24.80%，止损率47.74%，287笔，净收益+75.08%
      → 联合门槛（Sharpe>1 AND MaxDD<25%）未通过：MaxDD达标，Sharpe差0.14
    - ATR×3.5 压力测试（不另计失败）：Sharpe 0.95，MaxDD 14.93%，止损率22.46%
      → 仍未达Sharpe门槛
    - Walk-Forward：2.21 → -0.22 → 0.63（WF2为负，WF3低于通过线）
    - 2022：9笔7止损，Sharpe -1.77，方向性失败依旧
    - 品种分层：BTC 0.25 / ETH 0.89 / SOL 0.93（BTC为最大拖累）
    - Holdout未读取，pytest 9/9通过，未修改Memory Core
  
  核心判断（Claude CTO）：
    瓶颈已从「止损过紧」转移到「信号跨时期稳定性」。
    止损/退出维度已被充分探索并收敛（v6/v6b/0B12/0B17）：
      - 收紧风险（ATR×3.5/小仓位）→ MaxDD优秀但Sharpe下降
      - 放宽/无止损 → Sharpe改善但MaxDD恶化
    有效前沿稳定地坐落在联合门槛下方。继续微调止损倍数边际价值有限。
    WF2（2022方向失效）在所有版本中始终为负，是结构性问题，非止损可解。
  
  失败计数：6/8 → 7/8（仅剩1次机会，第8次失败触发项目级止损：暂停重评Alpha来源）
  
  L3紧急审计触发（DEC-022 触发条件「止损接近」）：
    报告：00_PROJECT_MANAGEMENT/STAGE_AUDITS/L3_EMERGENCY_2026-06-06.md
  
  执行决定（Claude CTO，Founder在对话中已建议同向）：
    不将第8次（最后一次）失败机会消耗在又一个止损/退出变体上。
    下一步方向须由L3审计结论 + Founder确认后再定，候选见L3报告。
  
决策时间：2026-06-06
来源：Codex REPORT_0B17 + Claude（CTO）综合判断；Founder对话中建议进入L3审计准备
影响范围：失败计数、研究方向、是否消耗最后一次机会
状态：ACTIVE
```

---

**[DEC-044]**
```
决策内容：失败计数双轨化 —— 区分「独立Alpha假设失败」与「同一信号实现调参失败」
  背景：L3紧急审计发现，7次失败中v6/v6b/0B17是同一个v4信号的止损调参，
        并非3个独立Alpha假设。原计数口径将实现调参与独立假设混同，
        使「连续8次失败→重评Alpha来源」的熔断被实现调参消耗。
  Founder在对话中将此口径裁决权明确委托给Claude（CTO）。
  
  裁决（Claude CTO）：采用双轨计数。
  
  轨道1 — 独立Alpha假设失败计数（管辖项目级止损「重评Alpha来源」）：
    v1（4H三重确认）、v2（1H三重确认）、v3（Sweep单事件）、v5（Bearish镜像）= 4
    → 当前 4/8。第8个【独立假设】失败才触发「暂停，重评Alpha来源」。
  
  轨道2 — v4信号实现失败子计数（管辖「停止微调单一信号」纪律）：
    v4策略（DEC-034已不另计）、v6、v6b、0B17 = 已耗尽止损/退出维度。
    → v4信号的止损/退出调参【已封顶】，禁止再开同类变体（与L3结论一致）。
  
  裁决依据（措辞经DEC-046修正）：
    v4在事件研究层通过三层【样本内】稳健性校验（t检验/非重叠/Bootstrap，DEC-041），
    即存在【样本内统计边沿】——注意：这不是跨期一致性，WF2从未显著（v7 WF2 p=0.1251）。
    「无法把样本内edge实现成跨期稳定、可部署的策略」是工程/稳定性前沿问题，
    与「8个独立信号都无任何edge→Alpha来源枯竭」是不同性质。
    用同一信号的实现调参失败去触发「否定整个Sweep Alpha来源」是错误归因。
    ⚠️ 不得据此宣称v4「已证明为真Alpha」（DEC-046纠正）。
  
  防漏洞纪律（与裁决同时生效，防止双轨成为逃避熔断的借口）：
    - 双轨不放宽研究纪律；A（仓位管理，DEC-045）是v4的最后一个实现杠杆。
    - 无论A成败，此后不再新增v4的任何止损/退出/仓位变体。
    - A失败 → v4实现线封闭，转入独立新假设；独立计数仍4/8。
    - 轨道2子计数仅用于纪律约束，不参与项目级止损判定。

决策时间：2026-06-06
来源：Founder委托裁决（「你来决定」）+ Claude（CTO）L3审计分析
影响范围：项目级止损触发逻辑、失败计数口径、所有后续假设归类
关联：修正计划书第六部分「连续失败假设数≥8」的口径理解；不改变阈值数值
状态：ACTIVE
```

---

**[DEC-045]**
```
决策内容：最后一个v4实现杠杆 —— 波动率/恐惧度缩仓策略（0B18）预登记，方向A
  Founder确认方向A（L3审计选项A）。
  
  核心：相对0B17 ATR×3.5版本（Sharpe 0.95 / MaxDD 14.93%，离门槛仅差Sharpe 0.05），
        唯一新增变量 = 按市场波动率/恐惧度动态缩仓（DEC-036早已背书、从未实现的杠杆）。
        直接攻击真瓶颈WF2/2022方向失效，而非过滤信号或再调止损。
  
  单变量原则：信号、双层Regime、ATR×3.5止损、t+24退出、成本、品种全部不变，
              仅改仓位定量规则。
  
  预登记文件：06_RESEARCH/HYPOTHESES/v5_sweep_regime_bull_volpos_v1.md
  任务书：04_AI_TEAM/CODEX_TASKS/TASK_0B18_VOLPOS_STRATEGY.md
  执行人：Codex
  
  通过门槛（冻结，不得据结果修改）：Sharpe > 1.0 AND MaxDD < 25%（与0B17一致）
  机制诊断（非门槛）：WF2 Sharpe应由负转正/收敛，验证缩仓确实修复跨时期稳定性。
  
  失败计数处理（依DEC-044双轨）：
    - 若通过 → v4成为首个可部署候选策略，独立计数保持4/8。
    - 若失败 → v4实现线封闭，独立计数仍4/8（不触发8/8）；转入独立新假设。
  
  约束：Holdout继续封存，运行前写死失效条件，不得因MaxDD接近门槛破例查看Holdout。

决策时间：2026-06-06
来源：Founder确认方向A + Claude（CTO）预登记设计
影响范围：第8轮策略实验（0B18），v4实现线收尾
状态：ACTIVE
```

---

**[DEC-046]**
```
决策内容：采纳Codex对L3审计的复核修正（5项），收紧表述与计数记录
  背景：Codex复核L3_EMERGENCY_2026-06-06.md，指出L3/DEC-044存在过度表述与
        一处仓位公式术语错误。Claude（CTO）逐条评估后全部接受，无反驳。
  
  修正1 — v4表述降级（FACT）：
    禁止称v4「已证明为真Alpha」。准确表述：
    「v4存在样本内统计边沿，但跨期稳定性（WF2）与策略可实现性尚未通过。」
    依据：Bootstrap/非重叠均为样本内稳健性检验，非Walk-Forward一致；v7 WF2 p=0.1251。
    已回改DEC-044裁决依据措辞。
  
  修正2 — 「有效前沿」降级为示意性对照（FACT）：
    v6/v6b（止损价成交、旧成本0.04%/0.05%+历史funding）与0B17（low触发收盘成交、
    新成本0.05%/0.1%+固定funding）口径不同，结果差异不能全部归因于止损宽度/仓位。
    L3第3节「有效前沿」表仅作示意，不构成同轴定量前沿。
  
  修正3 — 双轨计数永久三数并列（GOVERNANCE，防熔断绕过）：
    必须在所有状态文档中永久同时保留以下三个数，不得擦除历史7次：
      ① 历史实验失败总数：7（v1/v2/v3/v5/v6/v6b/0B17）
      ② 独立Alpha假设失败：4/8（v1/v2/v3/v5，管辖项目级止损）
      ③ v4信号实现变体：已封顶（v6/v6b/0B17，纪律约束）
    双轨仅用于「项目级止损归因」，不得用于抹去历史失败记录或弱化熔断。
  
  修正4 — 0B18为阶段例外（PROJECT）：
    DEC-036原将仓位管理/缩仓安排在Phase 1+。0B18在Phase 0B提前执行，
    属Founder批准的阶段例外，明确记录在案。
  
  修正5 — 0B18仓位公式术语纠错（FACT）：
    原L3/任务书 `0.01 × portfolio / risk_distance`（risk_distance为价格单位时）
    算出的是【数量】不是名义仓位。须用0B17代码口径：
      risk_budget   = 0.01 × portfolio
      quantity      = risk_budget / risk_distance      # risk_distance=ATR×3.5(价格单位)
      notional      = quantity × entry_price × vol_scalar
    已回改预登记文件与TASK_0B18任务书。
  
  对0B18成功率的修正认知（HYPOTHESIS）：
    高波动不仅覆盖亏损的2022，也覆盖盈利强劲的2021，缩仓可能同时削弱WF1。
    0B18成功概率不如L3原描述乐观；诊断须并列WF1缩仓前后对比。
  
  0B18定位收紧（采纳Codex最终建议）：
    0B18 = v4实现线最后一次、预登记完整的机制检验。
    若通过：仅升级为Holdout候选，不得直接称「可部署策略」，须另行Founder确认才动Holdout。
    若失败：立即封存v4实现线，转入全新独立Alpha研究，不再改仓位/止损/阈值/恐惧度定义。

决策时间：2026-06-06
来源：Codex复核L3 + Claude（CTO）逐条评估接受；Founder转达
影响范围：L3报告、DEC-044措辞、0B18预登记与任务书、所有状态文档计数表述
状态：ACTIVE
```

---

**[DEC-047]**
```
决策内容：0B18 FAILED/机制无效 → v4 实现线正式关闭
  实验结果（Codex REPORT_0B18，Claude验收通过）：
    - Sharpe 0.78（未过1.0）／MaxDD 14.03%（达标）→ 联合门槛 FAILED
    - 机制无效的直接证据：
      · 2022高恐惧候选 0/12，高恐惧成交 0/7，所有2022交易 vol_scalar=1.0
      · WF2/2022标准化收益与Sharpe完全不变（-0.61 / -1.87）
      · 高恐惧成交83个候选中56个在2021，53笔成交35笔在2021
      · 高恐惧组反而胜率71.70%、Expectancy +0.382R（缩仓削的是优质交易）
      · WF1 Sharpe 2.84→2.58，2021收益27.92%→16.56%（被削弱）
    - 结论：BTC波动率百分位不是"方向失效恐惧度"的有效代理；
            缩仓修不了2022，反而牺牲2021。机制假设被拒绝。
    - 单变量PASS、红队8项PASS、pytest 9/9、Holdout未读取。
  
  计数更新（双轨制，DEC-044/046，三数永久并列）：
    ① 历史实验失败总数：7 → 8（v1/v2/v3/v5/v6/v6b/0B17/0B18）
    ② 独立Alpha假设失败：仍 4/8（v1/v2/v3/v5）——0B18是v4实现变体，不增独立计数
    ③ v4信号实现变体：v6/v6b/0B17/0B18，至此【正式CLOSED】
  
  v4实现线关闭（永久约束）：
    - v4信号经止损（sweep_low/ref_low/ATR×1.9/ATR×3.5）、退出（1R2R/t+12/t+24）、
      仓位（1%风险/无止损固定/波动率缩仓）全维度测试，无一实现可部署的跨期稳定策略。
    - 永久停止v4的止损/退出/仓位/恐惧度任何变体（含改180/0.66/0.5/250或换恐惧度定义）。
    - v4不进入Holdout；v4降级为"样本内统计边沿，不可部署"归档。
    - 项目级止损未触发（独立Alpha计数4/8，距8仍有4次）。
  
  下一步（须Founder拍板，D级）：
    转向全新、独立预登记的Alpha假设（非Sweep结构家族）。候选方向见对话/状态文档。

决策时间：2026-06-06
来源：Codex REPORT_0B18 + Claude（CTO）验收；Founder转达治理规则
影响范围：失败计数、v4研究线终结、下一研究方向重置
状态：ACTIVE
```

---

**[DEC-048]**
```
决策内容：股票市场偏向复盘 → 第一个Phase 1方向由"截面动量"修正为"资金费率/基差"家族
  背景：Founder质疑当前思路是否过度偏向股票市场（关键行为规则1：发现方向偏差必须先指出）。
        Claude（CTO）复盘后确认：上一轮Founder基于带偏菜单选的"截面动量"是股票旗舰因子，
        其有效前提（大广度 + 低相关）加密市场不满足——BTC/ETH/SOL及多数山寨对BTC相关0.7~0.9，
        横向排序塌缩为BTC-beta+噪音；扩品种是"假广度"且引入幸存者偏差。属股票思维惯性。
        （注：已失败的v4家族SMC价格行为是币圈/外汇原生，非股票偏向；预登记/WF/Holdout/
         资金费率成本建模等方法论本就贴合或通用，无需推翻。）
  
  Founder将方向选择权委托Claude专业判断（「你站在专业角度上自己选」）。
  
  裁决（Claude CTO）：第一个Phase 1独立Alpha = 资金费率/基差家族（最原生、与价格结构正交）。
    废弃"截面动量"作为首选（高相关/假广度，本阶段不划算；不排除未来大宇宙下再议）。
  
  数据盘点（2026-06-06）：
    - 已有：BTC/ETH/SOL 4H永续K线 + 8H资金费率（2020起至2026-05，格式干净）
    - 缺：现货数据
  
  设计岔口（待可行性前置结果决定，不在本决策定死）：
    - 纯永续方向性（资金费率极值→价格均值回归）：不补数据、不改范围，但带价格风险、单笔edge小
    - delta中性carry（现货多+永续空）：真carry、隔离价格风险，但需补现货数据 +
      超出DEC-019"只做U本位永续"范围 = D级范围扩展，须Founder另行批准
  
  即时下一步（Claude执行，≤50行，非回测、不碰Holdout）：资金费率可行性前置——
    ① 极值事件样本量（对照DEC-018）；② 覆盖双边成本所需最低edge（L2 P1-02）。
    结果决定走纯永续方向性 还是 值得为carry补现货+请Founder批范围。
  
  方法论修正（轻量）：肥尾市场下Sharpe须配尾部/Calmar视角（现有MaxDD联合门槛已部分对冲）；
    IC/因子框架降级为诊断工具，不作Phase 1组织主轴。

决策时间：2026-06-06
来源：Founder方向偏差质疑 + 委托裁决；Claude（CTO）复盘
影响范围：Phase 1首个假设方向；取代DEC前述"截面动量"口头选择；L2 P1-01（扩品种）对资金费率方向不再阻塞
状态：ACTIVE
```

---

**[DEC-049]**
```
决策内容：Phase 0B → Phase 1 正式跨越
  - Founder明确确认（「确认进入 Phase 1」）。
  - 依据：L2阶段审计 CONDITIONAL GO（P0=0，P1=5，报告L2_AUDIT_PHASE_0B_2026-06-06.md）。
  - Phase 0B能力目标（证明研究闭环真实存在）已被8个完整闭环远超完成。
  - Phase 1目标（计划书）：找到有效赚钱规律——至少3个不同假设完整测试，
    至少1个通过统计验证（扣全部成本含funding正期望、多时段稳定、Sharpe>1、WF+Holdout通过）。
  
  承接入Phase 1的状态：
    - 双轨失败计数平移：历史失败8 / 独立Alpha 4/8（管辖项目级止损，距8还有4次）。
    - 首个Phase 1独立Alpha方向：资金费率/基差家族（DEC-048）。
    - L2 P1前置：P1-02成本可行性（资金费率方向首要门槛）；P1-04治理节奏控制（风险B）；
      P1-05目录重构（低优先）；P1-01扩品种对资金费率不阻塞；P1-03计数承接（本决策完成）。
  
  禁止事项（承接）：不进Phase 2系统建设；不重启v4实现线；不打开Holdout；
    数据/成本未核算前不仓促预登记；治理文档增量不得超过实验产出。
  
  即时下一步：Claude执行资金费率可行性前置（已启动）。

决策时间：2026-06-06
来源：Founder明确确认
影响范围：项目进入Phase 1框架；所有后续工作依Phase 1规则
状态：ACTIVE
```

---

**[DEC-050]**
```
决策内容：交易范围保持纯永续（DEC-019不变）；首个Phase 1假设选定 = 时间序列趋势 TSMOM
  Founder决策：不批准范围扩展为现货+永续；保持纯U本位永续（DEC-019重申有效）。
                方向选择委托Claude（「改不改方向你自己看」）。
  
  delta中性carry下线：可行性显示真carry需现货腿（超范围），Founder不批 → carry路线封存，
                       未来若范围政策改变可重启（资金费率数据与可行性结论已归档保留）。
  
  纯永续内方向裁决（Claude CTO）：选 TSMOM（时间序列趋势），不选资金费率方向性。
    理由：
      1. 纯永续无法捕获carry；资金费率方向性只剩"极值赌反转"，小edge逆势/短波动率，
         大概率盖不住0.30%往返成本（v4死因重演），且仍是均值回归味道。
      2. TSMOM与已失败信号全部正交（v1~v5/v4家族均为逆势/抄底入场）。
      3. 加密=强趋势单因子市场，时序趋势证据稳、不需广度、纯永续可做（永续原生支持做空）。
      4. TSMOM在下跌期做空/空仓，绕开"往2022下跌里抄底"这一反复撞的墙。
    资金费率不弃：降级为未来给TSMOM做拥挤度过滤的候选层，不进首个单变量假设。
  
  即时下一步：Claude执行TSMOM换手率/成本可行性（数信号翻转=换手，不测盈亏、不碰Holdout），
              据成本可行性选定单一frozen lookback，再预登记。

决策时间：2026-06-06
来源：Founder（范围决策）+ Claude（CTO，方向裁决）
影响范围：Phase 1首个假设=TSMOM；carry封存；资金费率降级为过滤候选
状态：ACTIVE
```

---

**[DEC-051]**
```
决策内容：P1-01 TSMOM 结论确认 = FAILED / COST-LIMITED；记录关键发现与下一步候选
  实验结果（Codex REPORT_P1_01，Claude验收通过）：
    - 净Sharpe 0.720 / MaxDD 68.38% → 联合门槛FAILED
    - 零成本毛Sharpe 1.043（>1）→ 符合预登记COST-LIMITED定义（信号有边沿，非信号无效）
    - 胜率21.83%（趋势策略正常）；趋势段28.28次/年/品种（≈可行性预估）
    - Holdout未访问；自动测试13/13；对账误差<4e-9
  
  关键发现（评估后认定为FACT）：
    1. 信号有毛边沿（毛Sharpe 1.04）——项目至今最接近有edge的结果。
    2. 2022 +14.65%（Sharpe 0.529）——顺势+可做空在熊市由负转正，
       核心正交论点（相对逆势Sweep家族）部分成立。
    3. ⚠️ MaxDD 68.38%（三段WF 56~68%）——比成本更严重的问题，零成本下也不可投资。
    4. ⚠️ 资金费率成本175,180 > 手续费+滑点(128,701)——最大成本项。
       多头趋势长期持有被资金费率结构性抽血（多头~88%时间付费率），是carry的镜像。
    5. 空头侧全样本净亏-205,361——"多空两侧均有趋势edge"不成立，实为多头驱动+2022靠空头。
    6. 三品种独立均不过门槛（SOL最好Sharpe 0.836）。
  
  1x敞口口径固化（采纳Codex建议，不追溯改v1）：
    "未翻转则持有"与"任意时点≤1x"无法同时严格成立。
    口径定为【每根4H开盘检查并按比例校正】，K线内浮动允许（v1实测峰值1.144x，开盘校正）。
    后续所有组合回测沿用此口径；如需连续/更高频减仓须另行预登记。
  
  计数更新（双轨制，DEC-044/046，三数并列）：
    ① 历史实验失败总数：8 → 9（…/0B18/TSMOM_v1）
    ② 独立Alpha假设失败：4/8 → 5/8（TSMOM为新家族首测，计入；距项目级止损还有3次）
    ③ 实现变体封顶组：v4家族CLOSED；TSMOM家族【开放】——COST-LIMITED非信号无效，
       允许TSMOM v2+实现细化；TSMOM v2/v3失败按"实现变体"计历史数，不增独立Alpha（与v4家族同规则）。
  
  下一步候选（Claude建议，待Founder确认continue-vs-pivot，D级方向）：
    推荐continue TSMOM，但不是"只降成本"。两个真问题须主攻：
      - 68%回撤 → TSMOM v2唯一新变量=波动率目标定仓（vol-targeting，攻回撤，不改信号）
        可参考V4资产B'1/B'2（相关性惩罚Risk Parity + 连续动态仓位）但须独立预登记验证，禁止直接继承。
      - 资金费率抽血 + 空头负贡献 → TSMOM v3候选：用资金费率做过滤/择向
        （封存的carry工作以"过滤层"身份重新进入）。
    单变量纪律：v2只改仓位定量，信号(L=90)与方向规则冻结。
    Red Team提醒（Codex）：不得只优化成本而回避68%回撤与空头负贡献。

决策时间：2026-06-06
来源：Codex REPORT_P1_01 + Claude（CTO）评估
影响范围：失败计数、TSMOM家族后续、1x敞口口径、下一步方向
状态：ACTIVE
```

---

**[DEC-052]**
```
决策内容：P1-02 TSMOM v2（波动率目标定仓）= FAILED；揭示单因子共同回撤为结构性问题
  实验结果（Codex REPORT_P1_02，Claude验收通过）：
    - 净Sharpe 0.505（低于v1 0.720）；毛Sharpe 0.916（低于v1 1.043，已非COST-LIMITED）
    - MaxDD 69.70%（未改善，反高于v1 68.38%）；2022 +2.72%（弱于v1 +14.65%）
    - inverse-vol按设计工作：SOL权重压至13.07%，总成本降37.79%，资金费率降50%
    - 自动测试20/20，Holdout未访问
  
  核心诊断（评估后认定为FACT，本轮最重要结论）：
    组合回撤未降的唯一解释 = 单因子共同回撤。
    单看各品种MaxDD都降了（BTC48%/ETH41%/SOL44%），但组合MaxDD没动（69.70%）——
    因为BTC/ETH/SOL高相关(0.7~0.9)、同涨同跌，趋势信号错时三个一起回撤。
    按品种独立缩仓(inverse-vol)无法分散掉一个共同因子(BTC-beta)的回撤。
    且inverse-vol砍掉了v1最强的SOL，毛Sharpe跌破1。
    → 结论：v2仓位假设被否定；TSMOM ~69%回撤是单因子共同回撤，定仓维度不可解。
  
  对TSMOM前景的含义：
    - 两连测(v1/v2)确认：趋势有毛边沿+解决2022，但~69%回撤是结构性单因子回撤。
    - v3(资金费率择向)无法解决回撤(Codex明确)，且v2毛边沿已<1，成本修复也难达Sharpe>1。
    - 纯永续方向性策略在"BTC/ETH/SOL=一个因子"的宇宙里，难以满足MaxDD<25%。
  
  计数（双轨，DEC-044/046）：历史失败 9→10；独立Alpha 维持 5/8（家族实现细化）。
  
  下一步：TSMOM建议封存，转方向决策（D级），见对话/CURRENT_STATE。
    候选：①转全新独立Alpha(保持纯永续) ②重审market-neutral carry
    （carry是市场中性，结构上免疫此共同因子回撤——v2证据反而抬高了它的相对价值，
     但需现货腿+超DEC-019范围，是Founder此前否决的D级范围决策）。
    纪律警告：MaxDD<25%门槛不得为迁就TSMOM而放宽（防goalpost-moving）；
             正确读法是"方向性趋势不适配该门槛"，故应转向而非改门槛。

决策时间：2026-06-06
来源：Codex REPORT_P1_02 + Claude（CTO）评估
影响范围：TSMOM家族前景、失败计数、下一步方向（含是否重审carry/范围）
状态：ACTIVE
```

---

**[DEC-053]**
```
决策内容：Phase 1 验收标准校准（方向性策略）+ TSMOM 正式封存
  背景：TSMOM v1/v2 揭示三币=单因子，纯永续方向性策略结构上难达原 MaxDD<25% 门槛。
        Founder 选择"按资金档校准回撤 + 保 Sharpe>1，然后找新纯永续信号"。
        Claude（CTO）以防 goalpost-moving 的纪律方式落档。
  
  校准后的 Phase 1 验收标准（方向性策略，冻结）：
    ① 边沿门槛（真门槛，不变）：扣全部成本含funding后 净Sharpe > 1.0。
       —— 这条是"有没有真本事"的判断，绝不下调（下调即放弃判断标准）。
    ② 回撤（由硬门槛改为"按资金档定规模"约束，挂钩DEC-015）：
       策略原始回撤 D 不再作信号好坏的一票否决；实盘按资金比例 φ 部署，
       使 账户级回撤 = D×φ ≤ 当档容忍（1000档30% / 1万档10% / 3万档5%）。
       即"回撤大"=投得少的问题，不是"信号差"的问题。
    ③ 脆弱性上限（防止接受不切实际的高回撤信号）：原始 MaxDD < 50%。
       超过则视为路径脆弱/过拟合风险，拒绝。
  
  防 goalpost-moving 安全阀（强制）：
    a. 本标准现在定死、冻结，不据任何待测策略结果反推。
    b. ★验证：用新标准回判 TSMOM 仍然不过——净Sharpe 0.72/0.50 < 1（②③再宽也救不了①），
       且原始MaxDD 68~70% > 50%。能把要救的策略照样毙掉，证明这是面向未来的合理校准，不是为救TSMOM。
    c. Sharpe>1 边沿门槛不下调；Holdout 一次性/封存不变；成本建模不放松。
    d. ②的资金档挂钩沿用DEC-007/015，未新增风险敞口。
  
  TSMOM 正式封存：方向性趋势线（v1/v2）关闭，不再开 v3 等家族变体。
    历史失败10 / 独立Alpha 5/8（不变）。趋势毛边沿与2022解法记入知识库。
  
  下一步：在校准后的标准下，寻找新的纯永续【方向性】独立Alpha（Sharpe>1为硬指标）。
    Claude将提候选并先做可行性前置；新独立Alpha失败将使独立计数 5/8 → 6/8（仅剩2次），故选择须审慎。

决策时间：2026-06-06
来源：Founder（选定校准方向）+ Claude（CTO，防搬龙门设计）
影响范围：Phase 1所有方向性策略验收口径；TSMOM封存；后续实盘资金部署口径
状态：ACTIVE
```

---

**[DEC-054]**
```
决策内容：下一个纯永续方向性独立Alpha = 持仓量(OI)/清算微结构信号
  Founder选定。加密原生、与趋势/逆势家族正交。
  
  前置（关键，未满足前不预登记）：本信号需OI/清算/多空比数据，当前项目没有（仅OHLCV+funding）。
    第一步 = 数据可得性核查：
      - OI(持仓量)历史、多空比(LSR)、主动买卖量比 → 币安公共仓库(data.binance.vision metrics)可得性与日期范围
      - 清算(liquidation)历史 → 公开渠道很可能不可得（币安已限制）
    须确认：能拿到什么、覆盖区间多长、样本是否够（对照DEC-018）。
  
  已知风险（待核查证实）：
    - 清算历史公开难获取；可能只能用OI/LSR替代。
    - metrics类数据历史可能仅~2023起（短样本→稳健性弱，且未跨2021牛/2022熊完整周期）。
  
  计数：新独立Alpha，失败→独立5/8→6/8（仅剩2次），故数据/可行性不过关则不轻易预登记。
  适用DEC-053校准门槛：Sharpe>1为真门槛，回撤按资金档定规模，原始MaxDD<50%脆弱性上限。

决策时间：2026-06-06
来源：Founder选定信号方向；Claude（CTO）标注数据前置与风险
影响范围：下一研究闭环；可能需新增数据采集任务
状态：ACTIVE
```

---

**[DEC-055]**
```
决策内容：确立 regime-first（自上而下）为 Phase 1 根本研究框架；Claude 工作方式转为主动交易主理人
  缘起：Founder 指出我们一直在"找入场点"，应先判大环境/走势周期，再定方向，再找入场。
        Claude 用 TSMOM 已有交易做事后诊断（效率比 ER 分趋势/震荡）证实：
          - 趋势期净 +449k vs 震荡期 −104k；单调（强趋势>中性>强震荡）
          - edge 高度集中"做多×趋势期"（R +0.129）；做空两格、震荡格均为死重/负
        结论：Founder 直觉正确，过去结构缺陷=跳过"大环境(趋势/震荡)"这一层。
  
  确立框架（Phase 1 所有方向性研究遵循自上而下四层）：
    ① 大环境 regime：趋势↑ / 趋势↓ / 震荡（须量化判定，单独可验证）
    ② 方向偏向：做多 / 做空 / 不做（空仓是合法决策）
    ③ 入场时机：在①②成立前提下找进场
    ④ 离场 + 仓位/风险（仓位按DEC-053资金档定规模）
    —— 不再零散测孤立信号；每个信号须说明它属于哪个 regime、为何在该 regime 有效。
  
  "马后炮"再评估（Claude判定）：
    趋势确认有不可消除的滞后（数学事实），但 V4 当年的确认方法（MA20+ADX收盘）粗劣是主因；
    ER诊断显示带滞后的趋势期做多仍 R+0.129 → 滞后不致命，方法可改进。
    推论：当年把趋势路线判废，很可能是确认方法差，而非路线本身不可行。
  
  工作方式调整（Claude 自我修正，采纳 Founder 反馈）：
    Claude 此前偏"被动研究记录员"，应转为"主动量化/交易主理人"：主动提出专业框架、
    主动结构化研究、主动给出有依据的方向判断，而非等 Founder 拍每个技术细节。
    Founder 保留 D 级确认；技术框架与信号设计由 Claude 主导。
  
  即时落地：两个并行——① regime-first 长偏向 TSMOM 预登记（DEC-056）；② OI数据核查(TASK_P1_03)续。

决策时间：2026-06-06
来源：Founder 框架性洞察 + 反馈；Claude（CTO）数据诊断 + 自我修正
影响范围：Phase 1 全部研究组织方式；Claude 工作模式；趋势路线再评估
状态：ACTIVE
```

---

**[DEC-056]**
```
决策内容：补做 V5 工具/框架借鉴调研，采纳"借鉴成熟方法论"原则与 Triple Barrier/Meta-labeling
  缘起：Founder 指出工具/产品调研缺失 + D38(V4历史)规划的"学习→借鉴→集成"V5从未执行。
        查证：V5 有方向性调研(EXTERNAL_RESEARCH v1/v2/v3)，但"借鉴成熟开源框架而非重造"被忽略，
        与我们手写回测/退出/持仓反复栽跟头直接相关。Claude(CTO)主动补做调研并出计划。
  计划文件：00_PROJECT_MANAGEMENT/V5_TOOL_INTEGRATION_PLAN_v1.md
  
  采纳（立即）：
    - 原则：不自己发明→先学→借鉴→集成→最后才重写。
    - Triple Barrier Method = 标准退出框架（止盈/止损/时间三屏障），取代手写退出。
    - Meta-Labeling = regime-first 的学术正名（主信号+二级"做/不做"模型）；P1-04 即其手动实例。
    - 事件采样 = 减少"马后炮"滞后的采样方法。
    - 三者写入研究方法论；需库时先安全审计(D38纪律:ClawHub恶意Skill风险)。
  
  推迟（不在现在）：
    - Freqtrade/NautilusTrader = Phase 2 系统参考（学架构不搬码）。
    - 重型多智能体编排(A2A/LangGraph) = Phase 2 有可部署策略后再建；现保持文件式 handoff。
    - 理由：先验证 Alpha，避免重蹈 V4/风险B（建系统在前、Alpha 在后）。

决策时间：2026-06-06
来源：Founder 指出调研缺失；Claude（CTO）补做调研 + 决断
影响范围：研究方法论(退出/交易过滤/采样)、工具引入纪律、agent协作自动化时机
状态：ACTIVE
```

---

**[DEC-057]**
```
决策内容：制度化"专业负责人标准"——修复项目至今最严重问题（P0），写入宪法
  问题定性（Founder 提出 + Codex 自审确认，P0）：
    AI（Claude 与 Codex）把"严格执行任务书"置于"先判断任务是否值得执行"之前，
    形成"信号失败→改止损→改退出→改仓位→加过滤"的局部修补搜索；
    把本应由 AI 完成的一阶专业抽象（如 regime-first）转嫁给不专业的 Founder。
    实际损害：浪费 v2 整轮实验、历史失败增至10、研究退化为局部搜索、独立Alpha配额面临系统性浪费。
  
  根因：工作模式错误（非态度）——职责边界被误解成思考边界；可靠的实验执行 ≠ 可靠的研究领导。
  
  制度修复（写入 CLAUDE.md v2.1「专业负责人标准」节，对 Claude+Codex 同时强制）：
    1. 主动领导不做被动执行器；不确定性由AI承担，不转嫁Founder；技术不当选择题丢给Founder。
    2. 职责边界≠思考边界：Codex发现方向有问题须暂停落地、提异议，不机械执行。
    3. 任务执行前强制"专业审查七问"（验证什么机制/证据是否支持/有无更上游问题/
       变量能否作用于目标/失败原因能否区分/有无更高信息增益实验/方向错先提异议）。
    4. 研究顺序铁律：市场状态划分→各状态归因→确认edge存在的状态→状态过滤后信号验证→仓位成本优化；
       禁止局部修补搜索。
    5. 先借鉴后重造（DEC-056）。
    新增「风险D（当前最大威胁）」：被任务队列牵着走的局部修补搜索。
  
  Codex 协作规范补充：Codex 在每个研究任务执行前同样输出"专业审查七问"，
    发现方向问题先在执行报告提异议并暂停，由 Claude/Founder 裁决。
  
  自我认定（Claude CTO）：此前我以"谨慎研究记录员"姿态工作，未尽主动建框架之责，
    该批评成立、非小偏差；作为CTO主动抽象的责任主要在我。此后按本标准执行。

决策时间：2026-06-06
来源：Founder（定性为最严重问题，要求写入宪法）+ Codex自审(P0确认) + Claude(CTO)接受并制度化
影响范围：Claude与Codex全部后续工作模式；宪法CLAUDE.md；研究组织方式
状态：ACTIVE（永久行为约束）
```

---

**[DEC-058]**
```
决策内容：按研究顺序铁律(DEC-057)重排队列——先做"市场状态框架+跨信号归因"，暂挂 P1-04/P1-03
  自我应用七问于 P1-04(Claude CTO)：发现 P1-04 仍是"先包一个过滤(ADX)再测"，略越级；
    更上游问题"edge 活在哪个市场状态、哪个信号在哪个状态有效"从未被系统回答。
    P1-04 若失败无法区分是信号无效还是状态定义错。故 P1-04 越级。
  
  重排（按铁律 市场状态划分→各状态归因→确认edge存在的状态→状态过滤后信号验证→仓位成本）：
    - 新第一步（诊断，不计失败、不碰Holdout、不耗独立Alpha配额）：
      市场状态框架 + 跨信号归因（TASK_P1_05）。
      用标准独立分类器(ADX + 趋势符号/MA, ER交叉校验)划分 趋势↑/趋势↓/震荡；
      把现有 TSMOM v1 交易、以及 Sweep 家族事件前向收益 按状态切分归因；
      产出"信号×状态 edge 地图"——明确 edge 到底活在哪。
      关键假设之一：**Sweep 家族可能只在震荡期有效**（当年只在EMA200多头regime测过，从未按趋势/震荡隔离）→ 可能被误杀。
    - 暂挂 P1-04（regime长TSMOM）：归因确认状态定义后，它很可能成为"状态过滤后信号验证"的第4步策略。
    - 暂挂 P1-03（OI数据核查）：属"下一个新信号"，在状态基础打好前越级；归因后再定是否需要。
  
  归因结果将决定下一个预登记策略的设计（信号、状态过滤、方向），从根上停止"信号失败就改参数"的局部搜索。

决策时间：2026-06-06
来源：Founder 追问研究顺序 + Claude(CTO)按DEC-057自我应用七问
影响范围：Phase 1 研究队列重排；P1-04/P1-03 暂挂；新增归因诊断为第一步
状态：ACTIVE
```

---

**[DEC-059]**
```
决策内容：设立"工具/框架/Skill 借鉴集成调研"为独立并行支线，在新对话执行
  Founder 计划把工具调研放到新对话单独执行。Claude(CTO)出自包含任务书。
  任务书：00_PROJECT_MANAGEMENT/TOOL_RESEARCH_BRIEF_v1.md
  
  关键设定：
    - 并行支线，**不得阻塞主线**（P1-05 归因 + Alpha 研究）——风险B护栏。
    - 产出=集成决策矩阵(V5_TOOL_INTEGRATION_PLAN_v2)+落地说明+回灌建议，非装工具/写代码。
    - 分层：Tier1 Phase1方法论(Triple Barrier/Meta-labeling/状态分类/AFML，立即可用)；
      Tier2 系统参考(Freqtrade/Nautilus，Phase2)；Tier3 编排/记忆/治理(多Phase2，含"Claude↔Codex自动化最小路径"评估)；
      Tier4 Skill；TierX 携带D38否决清单不重论证。
    - 时间盒1~2工作单元；每候选先过七问"该不该碰"。
    - 安装类Skill须安全审计(D38)。
    - 回灌：新对话不改Memory Core，产出经主对话Claude审阅后升级DECISION_LOG/Research Protocol；
      "改方法论/改交易标的或资金"的引入属D级须Founder确认。

决策时间：2026-06-06
来源：Founder（计划新对话执行）+ Claude(CTO)设计任务书
影响范围：新增并行调研支线；不影响主线研究顺序
状态：ACTIVE
```

---

**[DEC-060]**
```
决策内容：P1-04 结论 = PASSED / EXPLORATORY（项目首个通过校准门槛的结果）；不进 Holdout；下一步仍是 P1-05 归因（扩范围）
  结果（Codex REPORT_P1_04，Claude验收）：
    - 净 Sharpe 1.327 / 原始 MaxDD 41.31%（<50%脆弱上限）→ 通过 DEC-053 校准门槛。
    - WF 三段 Sharpe 1.199 / 1.374 / 1.460，全 >1 且无衰减 ← 项目首次跨期稳定。
    - ADX 过滤真有效：对照无过滤长偏向(Sharpe 1.062/MaxDD 67.42%)，ADX +0.265 Sharpe、-26pp 回撤。
    - 392 段 = 探索级(DEC-018)；毛 Sharpe 1.652；自动测试18/18；Holdout未访问。
    - ⚠️ 2022 收益 -23.72%、Sharpe -1.670，严重反证。
    - 机制澄清(Codex)：改善非"过滤掉亏损段"(被过滤段无成本累计仍为正)，而是缩短暴露/降funding/改回撤路径。
  
  计数：PASSED → 不增失败计数；独立 Alpha 维持 5/8。
  
  关键判断（Claude CTO，按专业审查）：
    - 这是 regime-first / meta-labeling 框架方向正确的首个积极证据，但不是终局。
    - 2022 根因精确定位：**ADX 只测趋势强度，不分牛熊方向**；熊市反弹被误判为上升趋势→做多挨打。
      缺口=独立的"高周期牛熊方向"层（强度与方向是两个不同的轴，我们一直只用了强度轴）。
    - 不进 Holdout（探索级 + 2022 未解释，Codex 同此建议）。
    - 不立即加方向层"修"2022（那又是局部修补搜索，违反DEC-057）。
  
  下一步（重申研究顺序铁律）：先跑 P1-05 归因，并扩范围：
    将"状态"显式拆为 强度(ADX/效率比) × 方向(牛/熊,高周期) 两轴；
    用两轴状态归因 P1-04 交易，确认 2022 -23.72% 是否全来自熊市反弹误判；
    顺带验证 Sweep 家族是否在震荡态被误杀。归因结果 → Claude 设计下一策略(P1-04+方向层+扩样本)。
  
  附带修正：v6_tsmom_regime_long_v3 预登记 §5"<300才探索级"与 DEC-018"300-499探索级"冲突，
    以 DEC-018 为准，392=探索级；文档口径以 DEC-018 为唯一标准。
  
  P1-03：OI/LSR/taker 数据到位(1,554,269行,无缺失)，清算不可得；OI 信号属地基打好后的下一新信号，暂不立项、不耗配额。

决策时间：2026-06-06
来源：Codex REPORT_P1_04/P1_03 + Claude(CTO)专业评估
影响范围：首个通过结果的处理；Holdout 纪律；P1-05 扩范围；OI 延后
状态：ACTIVE
```

---

**[DEC-061]**
```
决策内容：工具调研（DEC-059）回灌 —— 方法论采纳、库纪律、Skill 反转、协作自动化、分类器方向轴定调
  来源：并行支线产出 V5_TOOL_INTEGRATION_PLAN_v2.md，经主对话 Claude(CTO) 审阅；
        Founder 2026-06-07 确认"全部执行"（含下列 D 级项）；
        **2026-06-07 经 Codex 评审（7点）修订，Founder 转发认可** → 本条已纳入修订。
  关系：本条是 DEC-056 的落实与细化 + 对 v2 报告的纠偏；报告重写为干净 v2.1。

  立即采纳（已写入 Research Protocol v1.2 第十节）：
    1. 三屏障(Triple Barrier)为**方向性事件策略**的默认基准退出框架（波动率动态设障，对应0B16 ATR×1.9）。
       **非方向性机制（carry/资金费率/做市/跨市套利等）按"机制失效条件"设计退出**，
       预登记须说明为何不适用三屏障。（Codex 评审②；carry 正是 DEC-048 的下一候选方向）
    2. **规则式状态门控（rule-based state gating）= Phase 1 状态过滤的正式名称**；
       "Meta-Labeling"仅作方法论来源（严格 Meta-Label 含独立二级模型，本阶段不做）。
       报告指标用 **覆盖率/保留率/状态间收益差异**（描述性，不诱导按事后盈利标签调参）；
       **精确率/召回率 + Purged/Embargo CV 仅在真正训练二级模型时强制**。（Codex 评审③，防过拟合回流）
    3. Purged/Embargo 交叉验证写入硬纪律：参数优化禁用朴素KFold，标签重叠时加 purge+embargo。
       （当前 P1-05 为归因诊断，不涉参数优化，暂不触发；下一策略验证时生效）
    4. 借鉴前置纪律(DEC-056)：新信号/策略预登记前须先答"有无成熟方案可借鉴"。
    5. 报告新增必填字段：三屏障触发分布（仅方向性事件策略）、覆盖率/保留率/状态间收益差异、两轴状态归因。

  研究顺序（工具方法不得打断主线，Codex 评审④）：
    ① 先完成 P1-05 两轴归因（禁改信号/退出，TASK_P1_05 §5）→ ② 据 edge 地图选下一策略
    → ③ **仅当下一策略属方向性事件策略时**才引入三屏障 → ④ 再做 purge/embargo 与退出敏感性。
    **P1-05 才是当前最高价值动作，三屏障不是。**

  库引入纪律（纠偏①，对 v2 §1.1）：
    - Triple Barrier / Purged CV / 状态分类器一律**自实现可审计小函数(≤50行)**，
      借鉴 MLFinPy/López de Prado 实现作参考；**不引入 MLFinPy 运行时硬依赖**。
    - 理由：与"否决不可审计 Skill"(下条)逻辑自洽；MLFinPy 为单维护者年轻包，
      逻辑简单无需硬依赖；确需第三方库先 pip show + 源码 grep 审计并 pin 版本。

  状态分类器方向轴定调（纠偏②，对 v2 §1.6/§6.3）：
    - v2 报告 §6.3 用 ADX+ER+同周期 DI± 的单轴分类器**不采纳**——DI± 同周期同源，
      无法区分高周期牛熊，会复现 P1-04 的 2022 盲点。
    - 以 TASK_P1_05_REGIME_ATTRIBUTION.md §2 与 DEC-060 的**两轴**为准：
      轴1 强度(ADX/ER) × 轴2 独立高周期牛熊方向。Research Protocol §10.3 已固化。
    - 重要：TASK_P1_05 现有规格本就正确(两轴)，P1-05 可按现任务书执行，无需因本次回灌返工。

  D38 Skill 反转否决（Founder 确认）：
    - quant-research-platform、trading-devbox 两 Skill **从"采纳(待装)"反转为否决**：
      ClawHub 生态与 Cowork 工具链脱节、V5 无法安全审计；功能已被
      MLFinPy(借鉴)+Desktop Commander+VectorBT 组合覆盖。
    - market-sentiment 维持 Phase 2 候选；binance-pro/self-improving-agent/taskmaster/
      onchain/crypto-cog/trading-research 维持否决。

  协作自动化（D级，Founder 确认）：
    - 近期最小路径 = Claude 经 Desktop Commander 直接调用 Codex CLI，免 Founder 手搬文件。
    - 护栏（强制）：①派发前必过"专业审查七问"(DEC-057)，防风险D局部修补搜索被自动化加速；
      ②保留 TASK_*/REPORT_* 文件作审计留痕(不取消文件式记录)；③设成本/迭代上限；
      ④D级决策仍保留 Founder 人工确认。
    - A2A/LangGraph/Claude Agent SDK 维持 Phase 2（DEC-056）。

  延后/不引入：
    - VectorBT 继续用开源版；PRO($20/月)延后，需大规模参数扫描或内置Purged CV时再评估(属付费D级)。
    - Mem0/Graphiti 不引入(现 Markdown Memory Core 已够，无状态漂移风险)。
    - Freqtrade/NautilusTrader 维持 Phase 2 参考(学架构不搬码)。

  文档治理（Codex 评审①⑤⑥⑦）：
    - 报告重写为干净 **v2.1**（删失效正文/折叠更正/不靠顶部补丁），防后续 Agent 只读正文执行错误方案。
    - 事实更正：**NautilusTrader 许可证 = LGPL-3.0**（原写 BSL 1.1 错误，2026-06-07 核实）；
      **Freqtrade 撰写时最新 = 2026.4（2026-04-30）**（原写 2026.1 过时）。补来源表 + 访问日期。
    - 任务书要求但未逐项评估的项（分数差分/trend-scanning/HH-HL/MCP/CrewAI/AutoGen）
      明确标为"主动排除/延后"，不再声称 Tier1~4 全覆盖。
    - 同轮更新 CURRENT_STATE（治理规则：写文件后同轮同步）。

决策时间：2026-06-07（当日经 Codex 评审修订）
来源：Claude(CTO) 审阅 V5_TOOL_INTEGRATION_PLAN_v2 + Founder 确认全部执行 + Codex 7点评审（Founder转发认可）
影响范围：Research Protocol v1.2；研究方法论；库/Skill 引入纪律；Claude↔Codex 协作流程；P1-05 状态分类口径；工具计划 v2.1
关联：落实 DEC-056；纠偏并重写 v2 报告为 v2.1；与 DEC-060/TASK_P1_05 两轴口径一致；研究顺序服从 DEC-057/058
状态：ACTIVE
```

---

**[DEC-062]**
```
决策内容：P1-05 两轴归因结论确认；纠正 Claude 两个假设；据归因设计下一步 = P1-04 + 宏观牛市过滤
  归因结果（Codex REPORT_P1_05，Claude验收；诊断不计失败、未访问Holdout、5/5测试）：
  
  纠正1（Claude假设被部分否定，诚实记录）：
    "2022 几乎全是趋势上涨·熊市反弹陷阱"未达预设80%标准——trend_up_bear 仅占2022负向状态格亏损 64.7%。
    更准确：P1-04 正edge几乎全在宏观牛市（trend_up_bull +$1,085,554/135笔；trend_down_bull +$330,917/146笔）；
    两个宏观熊市格合计解释 94.4% 亏损。问题=在宏观熊市继续做多，不是仅熊市反弹。
  
  纠正2（Claude假设被否定）：
    Sweep 无证据"只在震荡态有效"。v4有效格更像"牛市中下跌/震荡后反弹"
    （trend_down_bull t+24 +2.56% p=5.5e-6；range_bull +2.32% p=4.5e-4），
    但 v4 输入已带双regime筛选=条件选择，不能算独立edge证据。
    → Sweep 不复活，保留为"牛市回调反弹"候选机制，日后单独预登记验证。
  
  全部单格 <300 = INSUFFICIENT(DEC-018)，仅定位用。ADX/ER一致率37.4%因ER>0.5阈值在4H过严，不否定ADX。
  
  据此决断（数据驱动的铁律第4步，非局部修补）：
    下一策略 = P1-04(regime-first长TSMOM) + 宏观牛市过滤（唯一新变量）。
    宏观定义=各品种前一完整日收盘 > 日线SMA200（无前视，标准值，与归因/Research Protocol §10.3 两轴口径一致）；
    宏观熊市不做多、不持多。预期2022亏损大幅消除；须验证 Sharpe 仍>1、WF稳定。
    与 v1.2 合规：本策略 = **规则式状态门控**（非 ML，**不报精确率/召回率**；
    报告用 覆盖率/保留率/状态间收益差异 + 两轴状态归因）；
    退出暂保持 P1-04 口径(单变量纪律)，三屏障作为后续候选变量另测，不在本轮叠加。
    （口径对齐：2026-06-07 经 Codex 评审，DEC-061/Protocol v1.2 已将"手动Meta-Label+P/R"
     改为规则式门控+描述性指标；与本条对话最终结论及 TASK_P1_06 一致。原措辞为早一版残留。）
  
  过拟合纪律（强制）：
    剔除"样本内已知亏钱的宏观熊市段"必然改善样本内结果——预期内、不算证据。
    真证据=WF稳定 + 最终Holdout；SMA200用标准值不调参；样本进一步缩小(宏观牛市约281笔)仍探索级，
    须后续扩品种/扩历史升确认级。参数若需优化用 Purged/Embargo CV。
  
  计数：TSMOM家族细化，失败不增独立Alpha(仍5/8)；通过=探索级，不进Holdout、不上实盘。

决策时间：2026-06-07
来源：Codex REPORT_P1_05 + Claude(CTO)评估（接受对自身假设的纠正）
影响范围：下一预登记策略(P1-04+宏观过滤)；Sweep候选机制归档；样本扩张需求；遵循 Research Protocol v1.x
状态：ACTIVE
```

---

## 已废弃决策

---

**[DEC-DEPRECATED-001]**
```
决策内容：三方AI协作模式（OpenClaw + DeepSeek + ChatGPT 平权协作）
  原方案：重要方案和诊断结论须经至少两个独立AI交叉验证
  数据由OpenClaw提取，DeepSeek负责整合，ChatGPT负责校核
历史决策时间：2026-05-06（D34 AID-1）
废弃时间：2026-06-02
废弃原因：已被"Claude主脑+Codex执行"的主脑模式替代
  多AI平权协作导致结论冲突、记忆不同步、无裁决机制
  当前架构：Claude为唯一主控AI，Codex为执行层
状态：DEPRECATED
```

---

# ===== 文档3/6：PROJECT_CONTEXT.md（全文）=====

# PROJECT_CONTEXT.md

**版本：** 1.0  
**初始化时间：** 2026-06-01  
**阶段：** Phase 0A · AI能力基础设施建设  
**写入依据：** MEMORY_EXTRACTION_PROTOCOL v1.0  
**说明：** 本文件仅记录经协议分类后、用户明确确认允许写入的内容。所有条目保留原始信息等级，禁止升级等级，禁止重写历史结论，禁止合并条目。

---

## 来源：D10 事故报告

**来源文件：** D10：事故报告.md  
**来源目录：** 03_RAW_INBOX/STATUS_RECORDS/  
**文档撰写时间：** 2026年5月9日  
**写入确认时间：** 2026年6月1日  

---

**[PC-01]**

```
信息等级：FACT
来源文件：D10：事故报告.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：一、事故摘要 / 文档头部元信息
提炼内容：
  本项目历史上存在一套自动化量化交易系统，使用 PostgreSQL 数据库，
  包含风控引擎（Phase 1 止损检查）、持仓管理（_positions 内存字典）、
  交易记录（log_trade()）等组件。系统曾处于"观察期"阶段运行（非实盘）。
可信度说明：
  这些组件名称和系统结构在文档中多处一致性引用，属于客观记录。
  "观察期"表述来自九·经验教训，为文档内部一致信息。
  当前代码库是否仍为此结构，无法从本文档确认。
处理状态：已确认写入
```

---

**[PC-02]**

```
信息等级：FACT
来源文件：D10：事故报告.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：一、事故摘要 / 三、完整时间线
提炼内容：
  2026年5月8日，系统发生 Ghost Position 事故（编号 INC-2026-05-08）：
  ETHUSDT 多头持仓因内存字典同向覆盖从风控检查中消失约1小时，
  期间实际亏损达 -5.47%，超出止损容限（-1.5%）3.65倍。
  同期 BTCUSDT 多头持仓亦受影响，实际亏损 -2.35%。
  两笔合计超损约 5.32%。
可信度说明：
  时间、价格、百分比在文档内部前后一致，属于对已发生事件的记录。
  为历史客观事实，不涉及当前系统状态。
处理状态：已确认写入
```

---

**[PC-03]**

```
信息等级：FACT
来源文件：D10：事故报告.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：一、事故摘要 / 三、完整时间线
提炼内容：
  49笔历史持仓因同向覆盖逻辑，入场记录存于数据库但出场记录永久缺失
  （exit_price 字段为 NULL），文档将其定性为"僵尸持仓"，
  无法回推盈亏。文档建议将其标记为 trade_status = 'INVALIDATED'。
可信度说明：
  49笔和字段状态 NULL 为具体技术描述，内部一致。
  INVALIDATED 标记为文档中的处理建议，执行状态未经独立验证，
  不代表当前数据库已完成此操作。
处理状态：已确认写入
```

---

**[PC-04]**

```
信息等级：EXPERIENCE
来源文件：D10：事故报告.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：四、根因分析 §4.1 / §4.2 / §4.4
提炼内容：
  历史系统存在三项已记录的架构缺陷（撰写时间点状态）：
  ①_positions 字典以 symbol_direction 为 key，同向新信号静默覆盖旧持仓；
  ②Phase 1 风控检查以内存字典为唯一输入源，而非从 PostgreSQL 读取；
  ③log_trade() 用 ORDER BY timestamp DESC LIMIT 1 匹配记录，
  缺乏全局唯一 trade_id，导致平仓记录可写入错误条目。
可信度说明：
  对历史代码逻辑的描述，来自事故根因分析，为经验性记录。
  当前代码库是否仍存在这些缺陷，无法从本文档判断，不得继承为
  当前架构描述。
处理状态：已确认写入
```

---

**[PC-05]**

```
信息等级：EXPERIENCE
来源文件：D10：事故报告.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：四、根因分析 §4.3
提炼内容：
  历史系统（事故发生时）缺失三项风控保障机制：
  ①DB 与内存持仓的 Reconciliation Loop（对账循环）；
  ②超过 N 轮未被检查的 Orphan Position Detection（孤儿检测）；
  ③持仓级别的 last_risk_check_at 时间戳记录。
可信度说明：
  对历史系统能力缺失的描述，有工程参考价值。
  当前系统是否已补充这些机制，文档本身无法证明。
处理状态：已确认写入
```

---

---

## 来源：D34 决策记录

**来源文件：** D34：决策记录.md  
**来源目录：** 03_RAW_INBOX/STATUS_RECORDS/  
**文档撰写时间：** 2026年5月9日  
**写入确认时间：** 2026年6月02日  

---

**[PC-06]**

```
信息等级：FACT
来源文件：D34：决策记录.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：一、架构决策 AD-2
提炼内容：
  V4.6.2 已于 2026年5月8日深夜冻结，停止一切功能开发和代码修改，
  引擎停止运行。基础设施层（PostgreSQL / Redis / Gateway / Grafana）
  保持运行。V4.6.2 的定位为 V5 开发的对照基准（Baseline），
  不再作为活跃开发版本。
可信度说明：
  决策有明确日期，与 D10 事故报告时间线一致，两文档互相印证。
  当前 V4.6.2 实际状态（是否仍处于冻结）无法从文档确认。
处理状态：已确认写入
```

---

**[PC-07]**

```
信息等级：FACT
来源文件：D34：决策记录.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：二、策略决策 SD-3
提炼内容：
  观察期于 2026年5月8日深夜提前终止（原定5月10日）。
  最终数据定格：754笔信号、97笔APPROVED、5笔真实平仓（全止损）、
  49笔僵尸持仓、6笔活跃持仓。文档声明所有数据已归档至 PostgreSQL。
可信度说明：
  具体数字与 D10 中的 49 笔僵尸持仓记录互相印证，内部一致。
  数据库归档状态无法从文档本身验证。
处理状态：已确认写入
```

---

**[PC-08]**

```
信息等级：EXPERIENCE
来源文件：D34：决策记录.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：二、策略决策 SD-1
提炼内容：
  历史系统中 SCORE_A 阈值参数初始值为18分（22分制）。曾于5月2日
  调整至16（HOLD-2），后于5月8日回滚至18。回滚理由：降低门槛在
  22分制预测力不足时只放大噪声，未改善信号质量。观察期97笔APPROVED
  中A级仅2笔，5笔真实平仓全为B级（14-15分）。
可信度说明：
  属于历史参数变更记录，有明确日期和数据支撑。22分制整体预测力
  接近随机（IC≈50%）已通过 IC 分析验证。当前系统参数不得继承。
处理状态：已确认写入
```

---

**[PC-09]**

```
信息等级：EXPERIENCE
来源文件：D34：决策记录.md
来源目录：03_RAW_INBOX/STATUS_RECORDS/
来源位置：二、策略决策 SD-2
提炼内容：
  历史22分制评分中，波动压缩因子是唯一通过IC分析的因子。
  volatile环境下 BTC IC +0.0579，SOL IC +0.0816。当时决策为
  保留该因子作为补充加成项（BTC/SOL +2分，ETH不适用，其他+1分），
  不作为核心评分逻辑。
可信度说明：
  历史统计验证记录，有具体数值。IC数值为历史计算结果，在当前系统
  中是否仍有效须重新验证，不得直接继承为当前参数。
  这是 V4 系统中唯一经过统计验证的 Alpha 信号。
处理状态：已确认写入
```

---

## 来源：V4.6.2 项目背景摘要

**来源文件：** V4.6.2 项目背景摘要.md  
**来源目录：** 03_RAW_INBOX/STATUS_RECORDS/  
**文档撰写时间：** 2026年5月9日  
**写入确认时间：** 2026年6月6日（Claude提炼，与D34/D10一致的客观记录）

---

**[PC-10]**

```
信息等级：FACT
来源文件：V4.6.2 项目背景摘要.md
来源位置：一、项目核心概况 / 七、架构决策记录 AD-3
提炼内容：
  V4.6.2冻结后，V5被定位为独立Research Branch（非V4代码重构）。
  策略范式从「Factor Confirmation（因子确认）」转向「Structure Event（结构事件）」。
  这是项目范式迁移的正式决策记录，对应当前V5研究中使用的
  Liquidity Sweep等价格结构事件作为研究对象。
可信度说明：
  有明确决策日期（5/8深夜）和替代方案记录，属于客观决策事实。
  当前V5研究方向与此一致（Structure Event研究 = Sweep事件研究）。
处理状态：已写入
```

---

**[PC-11]**

```
信息等级：EXPERIENCE
来源文件：V4.6.2 项目背景摘要.md
来源位置：三、Exit体系的推演链
提炼内容：
  V4历史中提出了结构止损方案（未落地）：
  做多方向：swing low + 0.5×ATR 作为止损位
  做空方向：swing high reclaim invalidation 作为止损位
  完整退出体系包含：结构止损+时间退出+浮盈回撤+结构破坏退出+完整状态机
  （七个状态：PENDING→OPEN→ACTIVE→MANAGING→EXITED/INVALIDATED/REPLACED/ORPHANED）
  该方案因观察期内不允许改代码而未实施，不是设计未完成。
可信度说明：
  历史设计方案记录，有明确工程意图。
  当前V5研究止损使用Sweep低点（DEC-025），与此不同。
  若未来需改进止损，结构止损（swing low + ATR）是可参考的历史方案。
处理状态：已写入
```

---

**[PC-12]**

```
信息等级：EXPERIENCE
来源文件：V4.6.2 项目背景摘要.md
来源位置：五、FIX-5：既救了系统也埋了雷
提炼内容：
  FIX-5（5月4-5日Bug修复）修复Bug-4时，将_positions字典的key改为
  symbol_direction复合键，意外引入同向覆盖逻辑，3天后导致Ghost Position事故。
  该变更作为"优化"顺带引入，未做独立风险评估。
  已固化铁律：任何涉及持仓生命周期的代码变更必须单独做风险评估；
  修复后必须验证Phase 1持仓检查覆盖完整性。
可信度说明：
  事故根因经D10/D34互相印证，属于确认事实。
  该铁律对V5系统开发阶段（Phase 2+）有直接参考价值。
处理状态：已写入
```

---

# ===== 文档4/6：AI_QUANT_COMPANY_ARCHITECTURE_v2.md（摘要：前200行 + 止损节）=====

# AI_QUANT_COMPANY_ARCHITECTURE_v2.md

**版本：** 2.0  
**创建时间：** 2026-06-04  
**作者：** Claude（CTO）  
**状态：** v2.0 FROZEN 2026-06-04（已确认 DEC-017/018/019，并经 DEC-020 冻结）  
**更新说明：** 在 v1 基础上整合以下内容：Opus独立审阅A-F修改、组织架构公司视角、控制平面与控制面板分离、成本统计、消息通道、OpenClaw重新定性、多AI辩论工作流、视觉模型定位、项目止损条件、操作模式升级（DEC-016）

---

## 一、项目定性

**项目名称：** AI Quant Company  
**项目本质：** AI-Native Quant Research Operating System  
**North Star：** 找到可持续产生 Alpha 的方法，最终实现自动化量化交易

这不是一个量化交易系统。这是一个能够持续提出假设、验证假设、积累知识、沉淀决策，并最终发现 Alpha 的 AI 原生研究系统。交易系统是这个系统的产出物，不是系统本身。

**成功定义【DEC-020】：** 至少 1 个 Setup 在 Holdout 上 Sharpe>1.0（扣全部成本，含手续费/滑点/funding）且跨牛/熊/震荡稳定，方进入 Phase 2；规模化（本金>3万）须 Phase 4 复盘确认。与 §九 止损条件对称。

**经济性定位【DEC-020】：** 3 万本金规模下，运营成本（订阅约1000元/月）很可能高于交易净收益。本阶段项目目标定义为「验证 Alpha 可持续性 + 建立可复用研究能力」，而非「当前资金规模下盈利」；盈利规模化属 Phase 4 命题。

---

## 二、整体架构分层

```
┌─────────────────────────────────────────────────────┐
│                  HUMAN LAYER                        │
│   Founder：D级决策确认 / 风险批准 / 方向判断         │
│   （日常只看日报5分钟，在大节点拍板）                │
└─────────────────────────────────────────────────────┘
                        ↕ D级决策确认
┌─────────────────────────────────────────────────────┐
│               GOVERNANCE LAYER                      │
│   Claude（CTO）：架构规划 / 任务分解 / 知识治理      │
│   + Red Team（独立质疑者角色，每个重大结论前必过）   │
└─────────────────────────────────────────────────────┘
                        ↕ 任务规格 / 文件交接
┌─────────────────────────────────────────────────────┐
│               RESEARCH LAYER                        │
│   假设定义 → 实验设计 → 数据 → 回测 → 验证 → 归档   │
│   Research Protocol / VectorBT / 知识库             │
└─────────────────────────────────────────────────────┘
                        ↕ 验证通过的策略
┌─────────────────────────────────────────────────────┐
│               EXECUTION LAYER                       │
│   Codex：代码实现 / 系统部署 / 自动化执行            │
│   Trading System / Risk Engine / Data Pipeline      │
└─────────────────────────────────────────────────────┘
                        ↕ 运行数据 / 系统状态
┌─────────────────────────────────────────────────────┐
│             INFRASTRUCTURE LAYER                    │
│   PostgreSQL / Redis / Grafana / Telegram Bot       │
│   腾讯云（新加坡）/ MacBook M1 / Windows i7         │
└─────────────────────────────────────────────────────┘
```

---

## 三、组织架构（公司部门视角）

用"公司运营"而非"技术系统"来理解各角色：

```
Founder（CEO）
├── 职责：方向决策、风险确认、资金管理
├── 日常：看日报（5分钟）+ D级节点拍板
└── 不需要：技术细节、代码、数据分析

Claude（策略总监 / CTO）
├── 职责：规划、架构、研究分析、文档治理、任务分配
├── 直接执行：数据下载、环境初始化、回测运行、结果分析（via Bash/Python）
├── 向上：D级决策提交 Founder 确认
└── 向下：标准化任务规格 → 文件交接 → Codex 自动读取

Codex（工程执行部）
├── 职责：复杂系统代码、生产部署、调试
├── 接收：Claude 写入项目目录的任务规格文件（无需 Founder 中转）
└── 输出：执行报告写回项目目录 → Claude 自动读取验收

验证系统 / Hermes等价物（质检部）
├── 职责：回测、IC分析、Walk-Forward验证、PASS/FAIL标准化输出
├── 实现：Python + VectorBT 验证脚本集合（Phase 0B建立）
└── 原则：任何结论被采信前必须经过独立验证（非提案人）

控制平面（调度室）
├── 职责：任务队列、状态管理、Claude→Codex自动交接、结果回传
├── 实现：轻量Python服务 + 文件监听（Phase 0B建立）
└── 当前替代：文件系统 + Telegram Bot（Phase 0B临时方案）

消息通道（通知系统）
├── 职责：重要事件推送、日报、告警
├── 实现：Telegram Bot（V4已有基础设施，Phase 2正式设计）
└── 原则：只推送需要决策的内容，不淹没Founder
```

---

## 四、角色与职责

### 4.1 Founder（CEO）
- 每天只做一件事：看日报，在 D 级决策节点拍板
- **禁止**作为信息中间人在 Claude 和 Codex 之间传话
- 日常可通过 Dispatch（手机）查看进度

### 4.2 Claude（CTO / 主控AI）
- **直接执行范围**：数据处理、环境安装、脚本运行、回测执行、结果分析、文件读写
- **Codex交接范围**：生产级系统代码、复杂架构实现
- **Red Team 职责**：每个重大研究结论给出前，Claude 先扮演"怀疑者"强制自查清单（前视偏差？样本外做了？参数敏感？多重检验？）
- 所有决策类输出必须标注【Claude继续】/ 【需要Codex】/ 【等待Founder确认】

### 4.3 Codex（工程执行）
- 读取项目目录中的任务规格文件后自主执行
- 执行完毕写入执行报告到项目目录
- **不参与**架构决策；发现架构问题必须写入执行报告，由 Claude 裁决
- **失败退路**：当 Codex 无法完成任务时，Claude 在 Cowork 沙箱通过 Bash/Python 直接执行（Claude 有此能力）

### 4.4 Claude → Codex 交接规范（标准格式）

```xml
<task>
  <target>[明确的可验证产出]</target>
  <inputs>[数据源、文件路径、依赖]</inputs>
  <constraints>[技术限制、兼容性要求]</constraints>
  <acceptance>[验收标准，可量化]</acceptance>
  <forbidden>[明确禁止的行为]</forbidden>
  <references>[相关规格文件路径]</references>
</task>
```

---

## 五、基础设施架构

### 5.1 硬件资源

| 设备 | 当前用途 | 说明 |
|------|---------|------|
| MacBook Pro M1 | 主开发机 / Claude 操作端 | Desktop Commander + Cowork 运行于此 |
| 腾讯云轻量（新加坡，2核4G） | 策略引擎 / 数据库 / 监控 | 可访问 Binance；**Phase 2 前需评估是否升级** |
| Windows i7-11700/16G | 备用 / 回测加速 | 按需使用 |

> ⚠️ **风险提示**：腾讯云 2核4G 运行实时交易系统 + PostgreSQL + 监控的余量较小，Phase 2 实盘前必须做性能评估，决定是否升级配置。

### 5.2 历史基础设施参考（V4，当前状态待验证）

> ⚠️ **审计修正（2026-06-05，P-001）：** 以下组件在 V4 中存在，但 V4 系统于 2026-05-08 冻结后**未重新验证运行状态**。D29（V4架构文档）尚未读取。「✅ 继承」不代表「当前已验证可用」，实际状态为 HYPOTHESIS。Phase 2 系统设计前必须逐项验证实际状态，不得直接继承。

| 组件 | V4 用途 | V4 存在状态 | 当前实际状态 |
|------|------|------|------|
| PostgreSQL | 唯一权威状态源 | HYPOTHESIS（V4有记录） | ❓ 待 Phase 2 验证 |
| Redis | 实时缓存（非权威） | HYPOTHESIS | ❓ 待 Phase 2 验证 |
| Grafana | 可视化监控 | HYPOTHESIS | ❓ 待 Phase 2 验证 |
| Docker Compose | 容器管理 | HYPOTHESIS | ❓ 待 Phase 2 验证 |
| systemd | 进程保活 | HYPOTHESIS | ❓ 待 Phase 2 验证 |
| Telegram Bot（×3） | 告警通知 | HYPOTHESIS | ❓ 待 Phase 2 验证 |
| Gateway 裁决框架 | 风控硬编码 | HYPOTHESIS | ❓ 待 Phase 2 验证（须评估是否改造或重建）|

### 5.3 AI 工具链

| 工具 | 角色 | 状态 | 成本模式 |
|------|------|------|---------|
| Claude（Sonnet 4.6，Cowork） | CTO / 主控 AI | ✅ 完全可用 | 订阅制 |
| Claude Opus | 独立审阅 / 重大决策仲裁 | ✅ 按需启用 | 订阅制 |
| Claude Code v2.1.161 | Cowork 底层 | ✅ 已安装 | 订阅制 |
| Codex | 工程执行 | ⚠️ 已配置，待本项目首次验证 | 订阅制 |
| Desktop Commander v0.2.41 | 文件系统访问 | ✅ 完全可用 | 免费 |
| Context7 | 技术文档检索 | ⚠️ 已安装未实际使用 | 免费 |
| Obsidian + Sync | 知识库可视化查看 | ✅ 可用（被动查看） | 订阅制 |
| OpenClaw | AI Agent框架（参考） | ❓ Phase 2 评估是否引入 | 框架免费/API按量 |
| Hermes Agent | AI Agent框架（参考） | ❓ Phase 2 评估是否引入 | 框架免费/本地运行 |

> **OpenClaw / Hermes 说明**：两者均是开源 AI Agent 框架（非 V4 的交易执行引擎），支持多模型路由、Telegram/Discord 接入、Skills 扩展。引入会带来 API 按量计费成本，Phase 2 评估后决定是否用其替代自建控制平面。

### 5.4 Python 量化环境（2026-06-04 初始化完成）

| 库 | 版本 | 用途 |
|----|------|------|
| pandas | 2.3.3 | 时间序列处理 |
| numpy | 2.4.6 | 矩阵运算 |
| ccxt | 4.5.56 | 交易所API（数据获取） |
| vectorbt | 1.0.0 | **主回测引擎**（已验证） |
| matplotlib | 3.10.9 | 结果可视化 |
| scipy | 1.17.1 | 统计检验 |
| statsmodels | 0.14.6 | 统计模型 |

**BTC/USDT 4H历史数据：** 已下载，14,965条，2019-01-01 至 2025-12-31，存于项目根目录。

**数据更新【DEC-020】：** 每轮研究前用同一脚本（data.binance.vision 月度增量）更新至最近完整月，并记录数据版本号（现数据止于 2025-12-31，需在下一轮研究前刷新）。

---

## 六、信息流架构

```
RAW_INBOX（原始信息）
    ↓ 提炼（MEMORY_EXTRACTION_PROTOCOL）
MEMORY CORE（已验证知识）
    ↓ 支撑

----- [架构 §9 项目止损/相关节，grep 提取] -----
7:**更新说明：** 在 v1 基础上整合以下内容：Opus独立审阅A-F修改、组织架构公司视角、控制平面与控制面板分离、成本统计、消息通道、OpenClaw重新定性、多AI辩论工作流、视觉模型定位、项目止损条件、操作模式升级（DEC-016）
8-
9----
10-
11-## 一、项目定性
12-
13-**项目名称：** AI Quant Company  
--
19:**成功定义【DEC-020】：** 至少 1 个 Setup 在 Holdout 上 Sharpe>1.0（扣全部成本，含手续费/滑点/funding）且跨牛/熊/震荡稳定，方进入 Phase 2；规模化（本金>3万）须 Phase 4 复盘确认。与 §九 止损条件对称。
20-
21-**经济性定位【DEC-020】：** 3 万本金规模下，运营成本（订阅约1000元/月）很可能高于交易净收益。本阶段项目目标定义为「验证 Alpha 可持续性 + 建立可复用研究能力」，而非「当前资金规模下盈利」；盈利规模化属 Phase 4 命题。
22-
23----
24-
25-## 二、整体架构分层
--
317:### 8.4 永续强平监控【DEC-019】
318-
319:选用 U本位永续后，强平（liquidation）成为新的归零风险，必须建模：
320:- 实盘实时计算每个持仓的强平价距；强平价距 < 安全阈值即降杠杆/减仓并告警。
321:- 任一持仓被强平 = 重大事故，系统暂停，等 Founder 指令。
322:- 回测必须按所选杠杆计算强平价，并统计「是否触及强平」，纳入风险评估。
323-
324----
325-
326:## 九、项目止损条件【新增，Opus审阅C项】
327-
328-**这是最重要但之前完全缺失的设计。**
329-
330:以下任意条件触发，必须暂停研究并重新评估整个项目前提：
331-
332-| 条件 | 阈值 | 触发动作 |
333-|------|------|---------|
334:| 连续失败假设数 | ≥ 8 个（含方向调整后） | 暂停，重评Alpha来源 |
335:| 研究阶段总时长 | ≥ 6 个月未找到有效信号 | 暂停，重评可行性 |
336-| 研究阶段总费用 | ≥ 5,000元（工具+服务器） | Founder重新决策继续/停止 |
337:| 实盘连续亏损 | 超过对应档位最大亏损的80%（永续下任一持仓被强平亦即时触发） | 系统自动暂停，等Founder指令 |
338:| 合规/账户风险 | 交易所账户冻结、政策变化或出入金受阻 | 立即暂停实盘，转纯研究并重评可行性 |
339-
340-> **说明**：这不是失败的标志，而是防止无限沉没成本的保护机制。每个成熟的量化研究机构都有明确的"此路不通"判据。
341-
342----
343-
344-## 十、控制面板（前端可视化页面）【新增】
--
349:- 系统运行状态（在线/暂停/异常）
350-- 当前持仓和实时 P&L
351-- 历史交易记录和绩效曲线
352-- 策略表现指标（胜率/Sharpe/回撤）
353-- 研究实验进度和结论
354-- **成本统计面板**（见第十一节）
355-- 告警历史
--
558:止损：结构止损（Swing Low + ATR Buffer）
559-止盈：分批（TP1: 1R / TP2: 2R / TP3: 跟踪止盈）
560-
561-样本量预估（待计算）：
562-  BTC 4H 历史数据 2019-2025 ≈ 14,965 根K线
563-  三重确认触发率预估 ~1%-3%
564-  预估触发次数：150~450次

# ===== 文档5/6：PROJECT_MASTER_PLAN_v2.md（摘要：前120行 + 止损条件节）=====

# 项目完整计划书 v2.2
# AI Quant Company — Founder 任务手册 & Claude 执行依据

**版本：** 2.3  
**更新时间：** 2026-06-06（Phase 0B状态更新，反映实际进展）  
**作者：** Claude（CTO）  
**状态：** v2.2 ACTIVE（基于 v2.1 FROZEN 2026-06-04 的局部补全，核心结构不变）  
**面向读者：** Founder（决策依据）+ Claude（任务手册）+ Codex（任务接收）

---

> **这份文件是什么：**  
> 项目的完整行动手册。Claude 每次对话读取后知道"现在做什么、下一步是什么、谁来做、怎么验收"。Founder 通过这份文件掌握整体进度，只在大节点拍板。

---

## 第一部分：全局视图

### 1.1 项目一句话描述

> 我们在建造一台"赚钱研究机器"——先用历史数据找到真实有效的交易规律，再让机器自动按规律交易，全程用 AI 替代大量重复性工作。

### 1.2 完整阶段路线图

```
[当前位置]
      ↓
┌─────────────────────────────────────────────┐
│  阶段 0A  建好研究实验室          🟡 进行中（1/5验收=20%）│
└─────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────┐
│  阶段 0B  跑出第一个实验结论       ⚪ 未开始     │
└─────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────┐
│  阶段 1   找到有效赚钱规律         ⚪ 未开始     │
└─────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────┐
│  阶段 2   把规律做成自动交易系统    ⚪ 未开始     │
└─────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────┐
│  阶段 3   小钱实盘验证            ⚪ 未开始     │
└─────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────┐
│  阶段 4   稳定运营，持续扩大规模    ⚪ 终态目标   │
└─────────────────────────────────────────────┘
```

**时间参考（非承诺）：**

| 阶段跨越 | 参考时长 | 主要风险 |
|---------|---------|---------|
| 0A → 0B | 2-4周 | Codex 环境问题 |
| 0B → 1 | 1-3个月 | 策略假设可能多次失败 |
| 1 → 2 | 1-2个月 | 系统工程复杂度 |
| 2 → 3 | 1个月（含30天模拟盘） | 模拟盘发现新问题 |
| 3以后 | 持续运营 | 市场变化 |

> ⚠️ 量化研究的正常现象：假设验证失败不是项目失败，而是排除错误路径的进展。

---

### 1.3 最终系统全景图（量化交易系统完整模块）

下表是系统最终形态的完整模块清单。让你看清楚"我们在建什么"以及"现在做到哪里了"。

| # | 模块名称 | 通俗描述 | 建设阶段 | 当前状态 |
|---|---------|---------|---------|---------|
| 1 | **数据采集模块** | 自动下载并存储市场历史数据 | 0A/0B | 🟡 历史一次性下载完成(BTC 4H 14,965条)；生产级实时采集未建 |
| 2 | **数据清洗模块** | 检查数据质量，去除异常值 | 0B | ❌ 未建 |
| 3 | **回测引擎** | 用历史数据模拟交易，验证策略 | 0A/0B | 🟡 研究级已验证(VectorBT 1.0.0，2026-06-04)；生产级未建 |
| 4 | **因子研究模块** | 计算和筛选各类市场指标 | 1 | ❌ 未建 |
| 5 | **策略研究模块** | 组合因子形成完整交易策略 | 1 | ❌ 未建 |
| 6 | **统计验证模块** | 判断策略结论是否可信（防止过拟合）| 1 | ❌ 未建 |
| 7 | **知识库** | 记录每个实验的过程和结论 | 0B起 | 🟡 部分（Memory Core）|
| 8 | **信号生成模块** | 实时分析市场，产生买卖信号 | 2 | ❌ 未建 |
| 9 | **风险控制模块** | 设置止损止盈，防止超额亏损 | 2 | ❌ 未建 |
| 10 | **持仓管理模块** | 追踪当前持有的仓位状态 | 2 | ❌ 未建（V4有缺陷版本）|
| 11 | **订单执行模块** | 向交易所发送买卖指令 | 2 | ❌ 未建 |
| 12 | **对账模块** | 比对数据库记录与交易所实际状态 | 2 | ❌ 未建（V4缺失此模块导致事故）|
| 13 | **监控告警模块** | 异常时自动通知 Founder | 2 | ❌ 未建 |
| 14 | **复盘分析模块** | 定期回顾实盘交易，找改进点 | 3 | ❌ 未建 |
| 15 | **绩效统计模块** | 计算收益率、回撤等关键指标 | 3 | ❌ 未建 |
| 16 | **项目治理系统** | 记忆、规则、文件结构、协作规范 | 0A | 🟡 进行中（约60%）|

**V4 教训：** 模块10（持仓管理）有缺陷 + 模块12（对账）完全缺失，是"幽灵持仓"事故的根因。V5 必须在阶段2中同步建设这两个模块。

---

### 1.4 职能分工与协作架构

```
你（Founder）
├── 职责：最终决策、大节点确认、资金管理
├── 日常：看日报（5分钟）+ 在 ★大节点★ 拍板
└── 不需要懂：代码、数学公式、技术细节

Claude（CTO · 策略总监）
├── 职责：规划、架构、研究分析、文档治理、任务分配
├── 工作方式：每次对话自动读取项目状态，直接开始工作
├── 向上：关键决策向 Founder 提交确认请求
└── 向下：生成结构化任务规格，交给 Codex 执行

Codex（技术执行）
├── 职责：写代码、运行程序、安装环境、调试
├── 接收：Claude 生成的任务规格书（目标+步骤+验收标准）
└── 状态：已配置，待完成本项目第一个实际任务
```

**任务隔离原则（为什么不把所有事情塞在一个对话里）：**
- 每个对话/Agent 只做一类事，上下文短，不混乱
- Claude 和 Codex 分开工作：思考和执行分离，出错容易定位
- 节省 token 成本（上下文越长，费用越高）
- 后期可按需扩展专职 Agent（如专门的回测分析对话、风控审查对话）

---

----- [Master Plan 第六部分 项目止损条件] -----
## 第六部分：项目止损条件（新增，Opus审阅C项）

以下任意条件触发，暂停研究，重新评估整个项目前提：

| 条件 | 阈值 | 触发动作 |
|------|------|---------|
| 连续失败假设数 | ≥ 8 个 | 暂停，重评Alpha来源 |
| 研究阶段总时长 | ≥ 6 个月未找到有效信号 | 暂停，重评可行性 |
| 研究阶段总费用 | ≥ 5,000元 | Founder重新决策 |
| 实盘连续亏损 | 超过当档最大亏损80%（永续下任一持仓被强平亦即时触发） | 系统自动暂停 |
| 合规/账户风险 | 交易所账户冻结、政策变化或出入金受阻 | 立即暂停实盘，转纯研究 |

---

## 第七部分：操作模式（DEC-016 更新）

# ===== 文档6/6：本月 L1 审计报告（MONTHLY_AUDIT_2026-06.md 全文）=====

# 月度健康审计报告 2026年06月

**执行时间：** 2026-06-07
**执行人：** Claude（自动任务 L1）
**审计范围：** 项目自 2026-06-01 启动至本日（首次月审，覆盖全周期）

---

## 总体健康度

🟡 **需关注**

项目高度活跃、治理严谨、实验产出充足，无 P0 级问题。需关注三点：① 成本完全未跟踪而项目设有 5000 元费用止损阈值；② 独立 Alpha 失败计数已达 5/8，距项目级止损剩 3 次；③ 若干治理文档存在状态滞后。均非紧急，但应在本月内处理。

---

## 关键指标

- **当前阶段：** Phase 1 — 找到有效赚钱规律（2026-06-06 跨越，DEC-049/DEC-030），已进行约 **1 天**；项目研究阶段总时长约 **7 天**（远未触及 6 个月时长止损）
- **本月对话次数估算：** 高频（≥30 轮量级）——RESULTS 目录 28 份实验产物 + CODEX_TASKS 23 份 REPORT，集中于 6/5–6/7
- **本月实验执行次数：** **28**（含 P1-01~P1-06 主线 + 0B8~0B18 系列诊断/回测 + 事件研究/Bootstrap 等）
- **资源消耗：** **待记录**（10_COST_TRACKING/ 目录为空，无任何成本台账）

---

## 各维度发现

**维度1 · 进度真实性：** 总体一致，记录诚实。Phase 0A 五项验收、两个早期研究闭环、P1-04 首个过门槛结果均有对应报告文件支撑。亮点：v4 信号被诚实降级为"样本内统计边沿、不可部署"并 CLOSED 实现线（DEC-047）；P1-04 PASSED 后明确**不进 Holdout**（探索级 + 2022 未解，DEC-060），未夸大；失败计数采用双轨制（独立 Alpha vs 实现调参）防止熔断被绕过。**未发现"记录完成但实际存疑"的重大条目。** 唯一瑕疵见维度5（Master Plan 路线图状态滞后）。

**维度2 · 风险状态：**
- **风险A（无治理疯狂研究）：** 未触发。治理持续在线（DEC-057 专业负责人标准、双轨计数、Research Protocol v1.2）。
- **风险B（只建治理无实验）：** 未触发。本月 28 份实验产物，实验产出充足。
- **风险C（停留讨论层）：** 未触发。连续实验执行，**连续无实验对话数 = 0**，远未达 14 天告警线。
- **风险D（CLAUDE.md 标注的当前最大威胁——局部修补搜索）：** 历史上曾触发（v4 止损参数在 v6/v6b/0B17 间反复微调），但项目已通过 DEC-055（regime-first 自上而下框架）+ DEC-057（专业审查七问）完成制度修复，当前研究顺序已转为状态归因优先（P1-05 两轴归因 → P1-06 宏观过滤）。**风险已从触发转为受控，持续监控即可。**
- **项目止损临近指标：** 独立 Alpha 失败 **5/8**（距 ≥8 还有 3 次）——这是当前最接近止损线的指标；费用阈值 5000 元因无跟踪无法评估；时长 6 个月仅用 7 天。

**维度3 · 资源消耗：** 10_COST_TRACKING/ 目录为空，**全项目零成本记录**。无法验证当月 AI 工具成本是否在 1000 元/月预算内，也无法计算距 5000 元费用止损阈值的剩余空间。这是一个治理缺口：止损条件依赖一个不存在的度量。详见 P1。

**维度4 · 决策健康度：** DECISION_LOG 含 DEC-001~062（ACTIVE）+ 1 条 DEPRECATED，内部高度一致，**未发现真实矛盾**。近期决策呈现健康的自我纠正：DEC-061 将 D38 两个 Skill 从"采纳"反转为否决并更正 NautilusTrader 许可证/Freqtrade 版本事实错误；DEC-062 诚实记录并纠正 Claude 自己的两个归因假设。**无超过 30 天未更新的 ACTIVE 决策**（项目启动仅 7 天，全部决策均在窗口内）。决策治理为本项目最强项。

**维度5 · 文档时效性：** CURRENT_STATE.md 更新于 2026-06-07（当日，v3.15），远在 7 天阈值内，状态新鲜。滞后项：① PROJECT_OPERATING_STATE.md 被 CURRENT_STATE §3 自标"待更新（与 CURRENT_STATE 部分重叠，需核对）"；② PROJECT_MASTER_PLAN_v2 头部已升 v2.3 且声明 Phase 0B，但 §1.2 路线图框图仍显示"阶段0A 🟡进行中（1/5验收=20%）"、页脚仍写"v2.1 (FROZEN 2026-06-04)"，与实际 Phase 1 状态不符。属文档滞后，不影响实际进度判断。

**维度6 · 阶段停滞检测：** Phase 1 于 2026-06-06 跨越，至今约 1 天。Master Plan 参考 0B→1 为 1–3 个月，当前**无停滞迹象，进度反而异常快**（7 天内完成 Phase 0A 全部验收 + 8 个研究闭环 + 跨入 Phase 1 并取得首个过门槛结果）。无超期。

---

## P0 问题（需立即处理）

无。

---

## P1 问题（本月内处理）

1. **成本跟踪完全缺失。** 10_COST_TRACKING/ 为空，项目却设有 5000 元费用止损与 1000 元/月预算。止损条件依赖一个不存在的度量，目前无法判断是否接近触发。建议建立轻量成本台账。

2. **独立 Alpha 失败计数 5/8，距项目级止损（8）剩 3 次。** 本身非问题（量化研究排除错误路径属正常），但已进入需主动监控区间。建议在 P1-06 执行后重估，若升至 6/8 应在 L2 审计中正式评估方向可行性。

3. **治理文档状态滞后。** Master Plan §1.2 路线图与页脚仍停留在 Phase 0A/v2.1；PROJECT_OPERATING_STATE.md 自标待更新且与 CURRENT_STATE 重叠。建议同步至 Phase 1 实况，消除重叠。

---

## 下一步建议

1. **建立成本台账** `10_COST_TRACKING/COST_LOG_2026.md`：每月记录 AI 工具（Claude/Codex 订阅与 API）、数据与其他研发支出，列出累计值并对照 1000 元/月预算与 5000 元止损阈值。这是补齐止损可观测性的最小动作。
2. **执行 P1-06（P1-04 + 宏观牛市过滤）**——当前最高价值动作，已预登记 + 出任务（TASK_P1_06）。严守过拟合纪律：剔除已知亏损熊市段的样本内改善属预期而非证据，真证据为 WF + Holdout。
3. **同步治理文档**：更新 Master Plan §1.2 路线图与页脚至 Phase 1；更新或归并 PROJECT_OPERATING_STATE.md 消除与 CURRENT_STATE 的重叠滞后。

---

## Opus 深度审计建议

**建议触发 Opus L2 深度审计。** 理由：① 项目刚跨入 Phase 1 并出现**首个过门槛结果**（P1-04 PASSED/EXPLORATORY，Sharpe 1.327/WF 三段全 >1），这是方向正确性的关键验证点，适合独立审查确认其非过拟合、非选择偏差；② 独立 Alpha 已 5/8 接近止损，方向一致性与机会成本需第三方校验；③ regime-first 自上而下框架（DEC-055）是项目级方法论转向，值得按 11 维全面复核。本月 L1 评级为 🟡，符合 DEC-022 中"阶段跨越时触发 Opus 审计包"的建议场景。Opus 审计包已同目录生成（OPUS_PACKAGE_2026-06.md）。

---

*本报告仅输出，不自动修改 DECISION_LOG 或 Memory Core 正文（DEC-022）。*
