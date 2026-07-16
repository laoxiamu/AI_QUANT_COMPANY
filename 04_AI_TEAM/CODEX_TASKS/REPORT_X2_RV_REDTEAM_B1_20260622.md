# [专业异议] REPORT_X2_RV_REDTEAM_B1_20260622

**任务 ID:** P1-RES-037-B1  
**生成时间:** 2026-06-22 UTC  
**最终裁决:** **KILL**  
**B1 是否执行:** 否。按任务书要求，阶段 0 判 KILL 后停止，不进入 B1 三门。

## 0. 执行前自查

- 机制验证对象：同 beta / 同生态 crypto 配对的价差均值回复是否存在可交易剩余 edge。
- 验收标准是否可量化：阶段 0 为 PROCEED / REVISE_ONCE / KILL；若进 B1，则三门任一不过即 KILL。
- 更便宜等效实现：先做方向红队 + 四腿成本量级审计；未过不跑统计门，避免消耗独立计数。
- 禁止项检查：未读取 Holdout；未改预登记；未调参；未扫全配对；未引入黑箱依赖。

## 1. 阶段 0 方向红队

### 裁决

**KILL。** 理由不是“没有可能出现回归”，而是 B0 机制在进入 B1 前没有给出足够硬的付款方与幅度证据，无法承担两腿四次成交的结构性成本。默认 KILL 基线下，不能用“也许能调出一组配对”来进入统计门。

### 1.1 payer 太软，且高度可竞争

B0 的 payer 是“拥挤交易者/局部冲击方”，不是强制清算、指数再平衡、到期交割这类机械付款方。主流 crypto perp/spot 的同 beta 配对是做市与低延迟 stat-arb 的天然目标：价差一旦具有稳定、低风险、可重复的 >0.8% 捕获空间，就会被市商库存管理、跨品种对冲和简单比值套利持续压缩。

我的判断：**残余 edge 不足以预设覆盖两腿成本。** 若要 PROCEED，必须先看到扣四腿成本后仍显著为正的硬证据；B0 只给机制叙述，没有给出“可捕获回归幅度 > 成本”的证据。

### 1.2 crypto 协整稳定性不足以当作先验

股票配对交易的核心假设是经济约束或资本结构带来的相对稳定协整关系；crypto 叙事轮动、协议事件、监管/交易所事件、代币解锁、生态迁移都会让原先“同 beta”关系断裂。断裂时价差不会均值回复，而会趋势化；多落后腿、空领先腿可能变成多端继续跌、空端继续涨，出现两腿同亏。

已核实的 arXiv `2602.23762` 题为 **“One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets”**，提交日期 2026-02-27，主题与 B0 所称“跨链负溢出”相符。该文献能支持“链间冲击会跨市场传播/外溢”，但**不支持可交易价差必然回归**；相反，它加强了脱钩/负外溢会把价差推成趋势尾部的风险。

### 1.3 两腿四成交成本是结构性死刑

复现脚本：`06_RESEARCH/CODE/x2_rv_redteam_b1_audit.py`  
输出：`06_RESEARCH/CODE/output/x2_rv_redteam_b1_audit.json`

四腿成本按任务书口径，即 long/short 两腿进出共 4 次成交，换算为 spread-return hurdle：

| 成本情景 | spread-return break-even | gross pair capital break-even |
|---|---:|---:|
| maker 下界 + 逆向选择 0.10%/fill | 0.48% | 0.24% |
| protocol base taker：fee 0.10% + slip 0.10%/fill | 0.80% | 0.40% |
| 压力：slip 0.30%/fill | 1.60% | 0.80% |
| 压力：slip 0.50%/fill | 2.40% | 1.20% |
| 压力：slip 1.00%/fill | 4.40% | 2.20% |

这意味着每次配对交易必须先跨过 **0.48% 到 0.80%** 的正常成本门，压力下是 **1.60% 到 4.40%**。对于高流动性主流币同 beta 配对，现实中可持续、可捕获、未被竞争吃掉的均值回复空间不应被预设为高于 0.8%；若实际偏离经常大于此，先进入的一般是做市/套利库存而不是慢速研究策略。

因此阶段 0 直接 KILL：合理回归幅度上限没有硬证据超过四腿成本，而成本是确定的。

## 2. B1 三门状态

阶段 0 已 KILL，以下三门按任务书不执行：

| B1 门 | 结论 | 关键数字 / 原因 |
|---|---|---|
| 门1 两腿成本门 | **未执行；阶段 0 已被成本逻辑 KILL** | base taker break-even 0.80%；maker+逆选下界 0.48%；压力 1.60% / 2.40% / 4.40%。 |
| 门2 协整稳定门 | 未执行 | 不假设总回归；阶段 0 已判断 crypto 协整/相关关系不具备足够强先验，且负外溢文献更像脱钩/趋势尾部证据。 |
| 门3 防过拟合门 | 未执行 | 若继续，必须先验配对 + 冻结 z 阈值/持有窗；但阶段 0 已 KILL，禁止通过加配对数、改 z、改持有窗续命。 |
| 被动基准对照 | 未执行 | 未进入 B1，不做扣成本收益与市场中性被动基准比较。 |

## 3. 数据与 Holdout

- `06_RESEARCH/DATA/` 下未发现任务书所称 `127 parquet`；复现脚本记录为 `parquet_files = 0`。
- 当前可见数据为 `total_files = 93`，其中 `csv_files = 73`；`06_RESEARCH/DATA/FUTURES_EXPANDED/` 有 `35` 个 `*_4H.csv`，行数范围 `8885` 到 `10738`。
- 检测到但未读取的 Holdout/密封类文件：
  - `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv`
  - `06_RESEARCH/DATA/A1_WORK/sealed_holdout.enc`
  - `06_RESEARCH/DATA/A1_WORK/A1_HOLDOUT_PERMTEST.log`
  - `06_RESEARCH/DATA/A1_WORK/A1_HOLDOUT_MANIFEST.json`
  - `06_RESEARCH/DATA/CARRY_WORK/CARRY_HOLDOUT_PERMTEST.log`

## 4. 文献核实

- `2602.23762`：**已核实存在**。
- 标题：**One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets**
- arXiv 页面：`https://arxiv.org/abs/2602.23762`
- 内容相符性：与“跨链负溢出”相符；不应被引用为“均值回复可交易 edge”的支持证据。
- 备注：agent-reach 的 Exa/Jina shell 路由因本地网络/proxy 失败；改用浏览器侧 primary arXiv 页面核实。

## 5. 最终结论

**KILL，不进入 B2。**  

建议回墓园并转看 #X3 横截面动量或其他候选。#X2 若未来重开，必须先给出低成本执行结构或强制性 payer 证据；不能靠扩大配对池、调 z 阈值、调持有窗来续命。

