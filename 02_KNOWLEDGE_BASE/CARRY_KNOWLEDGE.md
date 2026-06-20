# Carry 策略知识库

**定位：** 项目所有 carry 相关研究、审查、实验的综合"已知结论"。  
**使用规则：** 任何 carry 相关任务开工前必读本文件。新结论当轮写入，不存在"下次补"。  
**信息来源：** CARRY_RR1~RR4、CARRY_V3_DRAFT、CARRY_V4_DRAFT、CARRY_SCAFFOLD、CARRY_FEASIBILITY 报告 + 外部文献调研  
**最后更新：** 2026-06-20

---

## 一、机制假设（当前研究主张）

**核心论点：** 加密永续合约 funding rate 由多空力量失衡产生，长期偏正（多头付钱给空头），形成可采集的 carry。通过 long spot / short perp delta-neutral 结构，在对冲价格风险的同时收取 funding。

**机制来源：** BIS Working Paper 1087 + arXiv:2212.06888  
- Funding 是"锚定机制"——永续合约价格通过 funding 被锚定到 spot，不是无条件正期望
- 正期望条件：小资金优势（容量限制使大资金无法套平）、市场结构允许（交易所维持多空失衡）、总成本（资金成本+手续费+滑点+强平风险）低于 funding 收入
- **关键限制：** carry 不是稳定的"状态变量"，在市场情绪转向时 funding 可负，造成双腿亏损

**尚未回答的机制问题（必须在解释可行性结果前回答）：**
1. 当前 BTC/ETH funding rate 的历史分布是什么？正负占比？
2. 什么 regime 下 funding 系统性为负？（熊市？去杠杆期？）
3. 小资金（3万美元）的容量优势在何时失效？

---

## 二、预登记演化（v1→v4）

### v1：NOT APPROVED（RR1，2026-06-14）
主要问题：
- 构造：D 级——同一工作集既选标的/权重又做检验，HARKing风险
- 触发器：D 级——OI 触发定义不清
- 成本：D 级——未量化全成本
- 验收：D 级——四件套（赢亏比/正年份/对数增长/零基准）未冻结
- MDE 功效门未通过（约4个独立年度，单侧5%、80%功效，最小可检测均值≈年度收益标准差×1.65）

### v2：NOT APPROVED（RR2，2026-06-14，2/8闭合）
主要剩余问题：
- 资本分母 N 与 C0 矛盾
- OI 触发只交易现货腿 → 净空头
- 8H bootstrap 无法重建 1H 强平路径
- 事件窗口与前向 shadow 门未唯一化

### v3→v4：APPROVED（RR4，2026-06-15，3/3条件闭合）
v4 冻结的关键设计决策（不得擅自修改）：
- **资本：** C0=100,000 USDT，现货/永续/现金/funding/basis/强平统一 USDT 计价，80/10/10分配
- **强平路径：** PCG64 seed=20260614，2000条路径，105个168h同步块，fixed BTC/ETH基准
- **交易小时PnL：** A_t=funding后、open交易前检查点；右边界funding归属结束小时；逐小时对账
- **OI触发：** 双腿同步减至50%
- **事件压力：** 0.3%/0.5%/1.0%三档滑点压力
- **验收四件套：** 净期望收益bootstrap p、赢亏比≥1.5、正年份严格多数、对数增长>0、现金零基准、MDD≤15%、WF≥2正段
- **身份：** 历史=FEASIBILITY-LOCK（不耗独立计数）；前向shadow=真确认；上线需证据等级决定

---

## 三、当前阻塞状态（FEASIBILITY-LOCK，2026-06-20）

**双重阻塞——不是单一阻塞：**

### 阻塞1：Custodian 封存（主会话操作项）
- 需在主会话执行 chmod-000 封存 Holdout 到 `~/.aiquant_sealed/carry/`
- Codex 沙箱无权写项目目录外文件
- 操作参考：A1_RISK_REVIEW_v5 §12

### 阻塞2：8个数据输入缺失（⚠️ 比阻塞1更根本）
REPORT_CARRY_FEASIBILITY 明确列出 v4 运行所需但当前缺失的数据：

| 缺失数据 | 获取方式 |
|---|---|
| Spot 1H open（只有close，缺open） | data.binance.vision 下载 |
| Perpetual contract 1H OHLC（独立于mark price） | `/fapi/v1/klines` 分页拉取 |
| Binance index 1H close | `/fapi/v1/indexPriceKlines` |
| Historical leverage brackets（floor/cap/mmr/cum） | Binance 官方文档 or 历史快照 |
| Historical liquidation clearance fee rate | Binance 公告历史 |
| Binance withdrawal status / USDT depeg event source | 公告日志 or CoinGlass |
| ADL official execution records | Binance API `/fapi/v1/adlQuantile` |

**结论：** 即使完成 custodian 封存，缺失数据不解决，v4 可行性仍无法运行。**数据采购应与 custodian 封存并行启动，不是串行等待。**

---

## 四、从研究报告提取的 carry 专项教训

### 教训C-001：同一工作集不能既选标的又做验证
来源：RR1。预登记阶段就确定标的池，验证阶段不得修改 → v4 已修复

### 教训C-002：bootstrap 窗口必须匹配持仓周期
来源：RR2。8H bootstrap 窗口无法重建 1H 强平路径 → v4 改为 1H 合成路径

### 教训C-003：delta-neutral 不等于零风险
来源：RR1+外部文献。强平路径、basis 尾部、USDT 脱锚、ADL 执行都是真实尾部风险 → v4 有事件压力档

### 教训C-004：OI 触发定义必须两腿同步
来源：RR2。只收紧现货腿会产生净空头暴露 → v4 已修复为双腿同步减仓50%

### 教训C-005：前向 shadow 的"达到后晋级"存在 optional stopping 风险
来源：RR2。前向 shadow 需另立确认级预登记，不能用历史身份的"解锁就升级"逻辑

---

## 五、下一步研究方向

**解除阻塞的正确顺序（并行不串行）：**
1. 主会话执行 custodian 封存（Claude 操作）
2. **同时** 派 Codex 任务采购缺失数据（8项清单见§三）
3. 两项完成后，重新派 CARRY_FEASIBILITY 任务

**可行性通过后的研究方向：**
- 历史可行性 PASS → 前向 shadow（几个月纸面，待 Founder 确认严谨度下调 §1c②）
- 同时评估 A-1×Carry 交互效应（交叉策略）
- carry 在不同 regime 下的表现归因（funding 正负与市场状态的关系）

---

## 六、外部文献摘要

| 文献 | 关键结论 | 对本项目的含义 |
|---|---|---|
| BIS WP 1087（Crypto Carry） | Futures-spot basis 存在但受制度摩擦约束 | Carry 有机制基础，不是纯噪声 |
| arXiv:2212.06888（Perpetual Futures Fundamentals） | Funding 是锚定机制，不是稳定收入流 | 不能假设 funding 永远正，需 regime 分层 |
| arXiv:2410.15195（BTC Risk Premia） | 波动状态影响风险溢价结构 | Carry + regime filter 有理论支撑 |

---

*CARRY_KNOWLEDGE.md 是活文件。每次新 carry 实验完成，当轮更新 §四（教训）和 §五（下一步）。*
