# 研究与状态历史归档（2026-06-10 自 CURRENT_STATE v3.18 剥离，内容原样未改）

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
【P1-06已完成，见下方结果块；当前等待Founder裁决4项D级事项】

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

**P1-06 TSMOM+宏观牛市门控 = 已完成（PASSED/EXPLORATORY，未证明全面优于P1-04，未碰Holdout）：**
- 净Sharpe 1.285>1 / 原始MaxDD 38.93%<50% / 309笔探索级（≥300，符合DEC-018探索级；注：Opus估的281偏低）
- 宏观门控把2022从-23.72%改善至-1.37%、MaxDD 25.65%→2.89%，但2022仍未回正（Sharpe-0.557）
- 全样本净Sharpe比P1-04降0.043、净利润减~$552k → 验证"宏观门控控熊市尾部风险"，非"普遍增收益"
- WF三段0.970/1.462/1.390（WF1略<1，P1-04"三段全>1"的强证据被削弱）
- 计数：TSMOM家族细化，PASSED不增失败；独立Alpha维持5/8
- 报告：`06_RESEARCH/RESULTS/20260607_tsmom_macro_bull.md`




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

