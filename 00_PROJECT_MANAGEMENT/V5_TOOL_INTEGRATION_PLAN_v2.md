# V5 工具/框架借鉴集成计划 v2.1

**撰写：** 2026-06-07 · Claude（CTO，主理人身份）
**基于：** TOOL_RESEARCH_BRIEF_v1.md（DEC-059）；v2 经 Codex 7 点评审后重写为 v2.1
**调研范围：** Tier 1~4（覆盖范围见第八节，未逐项评估项已显式标注）
**原则（DEC-056）：** 不自己发明 → 先学习 → 借鉴 → 集成 → **最后才重写**
**护栏：** 产出是"集成决策矩阵 + 落地计划"，不是装工具或写代码；**不阻塞主线 P1-05**。
**权威口径：** 本文与 DEC-061 / Research Protocol v1.2 / TASK_P1_05 一致；如有冲突以 Memory Core 为准。

> **v2.1 相对 v2 的修订（Codex 评审 + Founder 认可，2026-06-07）：**
> ① 删除失效正文、把更正折叠进正文（不靠顶部补丁）；② 三屏障从"通用默认"缩为"方向性事件策略默认基准"；
> ③ "手动 Meta-Labeling" 改称"规则式状态门控"，指标去精确率/召回率；④ 状态分类以两轴为准（删单轴/DI±方案）；
> ⑤ 未逐项评估项标"主动排除/延后"（第八节）；⑥ 补来源表 + 修正许可证/版本事实（第九节）；⑦ 同步 CURRENT_STATE。

---

## 一、Tier 1 — 方法论（立即服务 Phase 1）

### 1.1 Triple Barrier Method（方向性事件策略的默认基准退出）

| 字段 | 内容 |
|------|------|
| **来源** | Marcos López de Prado《Advances in Financial Machine Learning》；mlfinlab（商业闭源）；MLFinPy（MIT 开源实现，作参考） |
| **定位** | 退出框架：上轨（止盈）+ 下轨（止损）+ 垂直轨（时间）三屏障，基于波动率动态设障 |
| **适用边界（关键）** | **仅"方向性事件策略"（Sweep/突破/动量入场）的默认基准退出**。carry/资金费率/做市/跨市套利等非方向性机制，退出由**机制失效条件**决定（基差收敛/价差回归/对冲腿失衡），预登记须说明为何不适用三屏障 |
| **借鉴什么** | 设计理念（屏障优先级 + 波动率动态设障）+ 标签逻辑；**代码自实现 ≤50 行**，借鉴 MLFinPy 作参考 |
| **库纪律** | **不引入 MLFinPy 运行时硬依赖**（单维护者年轻包、逻辑简单、与"否决不可审计 Skill"逻辑自洽）；mlfinlab 商业版 £100/月 **不采纳** |
| **决策** | ✅ 采纳方法论，限定适用边界；自实现 |

### 1.2 规则式状态门控（Rule-based State Gating）

| 字段 | 内容 |
|------|------|
| **来源** | Meta-Labeling（López de Prado）作**方法论来源借鉴** |
| **定位** | 主信号产生候选，按**规则式状态判断**（§1.6 两轴）决定"这次做不做"，不改方向 |
| **命名纪律** | 本阶段**不称 "Meta-Labeling"**。严格 Meta-Labeling 含独立训练的二级模型；当前为规则式门控，Phase 1 不训二级模型 |
| **报告指标** | **覆盖率 / 保留率 / 状态间收益差异**（描述性）。**不要求精确率/召回率**——基于事后盈利标签会诱导反调过滤器、引入过拟合；只有真正训练独立二级模型时才强制 精确率/召回率 + Purged CV |
| **决策** | ✅ 采纳为 Phase 1 状态过滤正式框架；P1-05 归因结果将成为门控规则的依据 |

### 1.3 事件采样（Event-based Sampling）

| 字段 | 内容 |
|------|------|
| **来源** | López de Prado；mlfinlab 的 `cusum_filter` 思路 |
| **定位** | 按市场事件采样取代固定时间窗，减少滞后信息泄漏 |
| **决策** | 📋 **理念采纳，当前不落地**。Sweep 信号本身已是事件驱动；开发资金费率 carry 等新信号时再评估 CUSUM 过滤 |

### 1.4 Purged / Embargo 交叉验证

| 字段 | 内容 |
|------|------|
| **来源** | López de Prado 2018；timeseriescv、skfolio |
| **定位** | 防时间序列 CV 前视偏差：训练/测试间 purge 重叠标签 + embargo 缓冲期 |
| **与当前相关性** | ★★★★ 现有 Walk-Forward（时间切割）方向对，但持仓/标签重叠多时未 purge 会高估样本内 Sharpe |
| **触发时机** | **P1-05 为归因诊断，不涉参数优化，暂不触发**；下一策略验证/调参时生效 |
| **决策** | ✅ 方法论采纳，写入 Research Protocol §10.4；实现优先 timeseriescv/skfolio 或自实现 |

### 1.5 VectorBT 进阶能力

| 字段 | 内容 |
|------|------|
| **PRO vs 开源** | PRO（$20/月）：内置 Walk-Forward/Purged CV、Regime 分段、批量扫描；开源：基础完整 |
| **决策** | ✅ **继续用开源版（已验证，够用）**；大规模参数扫描或需内置 Purged CV 时再评估 PRO（付费=D级须 Founder 确认）。近期不升级、不阻塞主线 |

### 1.6 市场状态分类（两轴，强制；与 DEC-060 / TASK_P1_05 §2 一致）

| 字段 | 内容 |
|------|------|
| **铁律** | 状态必须显式拆成**两个独立轴**，缺一不可。P1-04 的 2022 -23.72% 根因正是只用强度轴、把熊市反弹误判为上升趋势（DEC-060） |
| **轴1 强度** | ADX(14)（>25 趋势 / <20 震荡 / 20~25 迟滞）；Kaufman 效率比(ER) 作第二镜头交叉校验，报告一致率 |
| **轴2 牛熊方向** | **独立的高周期方向判定**（日线 close vs 200日MA、或日线 MA 斜率/高低点结构）——P1-04 缺的轴 |
| **禁止** | ❌ 用同周期 DI+/DI−（或任何与强度轴同源同周期的指标）冒充方向轴——无法区分高周期牛熊，会复现 2022 盲点。**v2 旧稿的单轴/DI± 方案已删除** |
| **状态网格** | {趋势↑·牛 / 趋势↑·熊(反弹陷阱) / 趋势↓·牛 / 趋势↓·熊 / 震荡·牛 / 震荡·熊} |
| **可用实现** | `pandas-ta.adx()` + 纯 numpy ER（~10行）+ 高周期方向（纯计算），无需重型依赖 |
| **决策** | ✅ 两轴为 P1-05 标准；**正式规格以 TASK_P1_05 §2 为准** |

---

## 二、Tier 2 — Phase 2 系统框架（学架构，现在不建）

### 2.1 Freqtrade

| 字段 | 内容 |
|------|------|
| **来源/许可** | 开源，github.com/freqtrade/freqtrade，**GPL-3.0** |
| **版本（访问 2026-06-07）** | 最新稳定 **2026.4（2026-04-30）**；年份-月份版本制，月度发布 |
| **核心价值** | Position Lifecycle（adjust_trade_position）；分层止损；动态定仓；Protections（连亏暂停/pair-lock） |
| **决策** | 📋 **Phase 2 参考**，学 Position Lifecycle + Protections；现在不建、不装 |

### 2.2 NautilusTrader

| 字段 | 内容 |
|------|------|
| **来源/许可** | 开源，Rust+Python，**LGPL-3.0**（github.com/nautechsystems/nautilus_trader）。⚠️ v2 误写 BSL 1.1，已更正 |
| **现状（访问 2026-06-07）** | 活跃维护（近期活动 2026-05），持续 Cython→PyO3 迁移；生产级 |
| **核心价值** | 确定性事件驱动（单线程 actor）；回测/实盘同一代码路径；Position reconciliation 防幽灵持仓 |
| **决策** | 📋 **Phase 2 参考**，学事件驱动 + 持仓对账；现在不建（Rust/PyO3 迁移成本高）。LGPL 合规：作为库引用须注意动态链接/分发条款，Phase 2 评估时复核 |

### 2.3 Backtrader / vn.py

❌ **不采纳**。Backtrader 维护停滞；vn.py 中文社区为主，Event bus 可参考但无需专门研究。当前 VectorBT 已够用。

---

## 三、Tier 3 — Agent 编排 / 记忆 / 治理

### 3.1 Claude↔Codex 自动化最小路径

**当前痛点：** Founder 手工传递 TASK/REPORT 文件（信息中转，违反分工原则）。

| 方案 | 评估 |
|------|------|
| A2A / LangGraph | 重型/过度工程，需部署基础设施 → Phase 2 |
| Claude Agent SDK | 官方、可审计性强 → 未来首选，Phase 2 |
| 文件式 handoff（当前） | 够用，但有手搬问题 |
| **Desktop Commander 轻量自动化** | **近期最优：Claude 直接 start_process 执行 Codex CLI** |

**CTO 判断（D级，Founder 已确认，DEC-061）：** 近期最小路径 = Claude 经 Desktop Commander 直接调用 Codex CLI，免 Founder 手搬。
**护栏（强制）：** ① 派发前必过"专业审查七问"（DEC-057），防风险D局部修补搜索被自动化加速；② 保留 TASK_*/REPORT_* 文件作审计留痕；③ 成本/迭代上限；④ D级决策仍人工确认。A2A/LangGraph/Agent SDK 留 Phase 2。

### 3.2 记忆系统（Mem0 / Graphiti / Letta）

❌ **当前不引入**。现有 Markdown Memory Core（CURRENT_STATE/DECISION_LOG）已满足，无状态漂移风险。Mem0/Graphiti 适合多 Agent 大规模场景，当前 1 Claude + 1 Codex 不需要 → Phase 2 再评估。

### 3.3 治理框架（ADR / OODA）

✅ **已采纳，无需新增**。DECISION_LOG 已是 ADR 实质；Research Protocol 已是 OODA 落地。"七问检查表"已在 CLAUDE.md 专业负责人标准中，Research Protocol §七 Red Team 清单与之衔接。

---

## 四、Tier 4 — Skill / 连接器复核（对照 D38）

| Skill | D38 决策 | v2.1 复核结论 |
|-------|---------|--------------|
| **quant-research-platform** | ✅ 采纳（待装） | ❌ **反转为不采纳**：ClawHub 生态与 Cowork 工具链脱节、V5 无法安全审计；功能已被 MLFinPy(借鉴)+Desktop Commander+VectorBT 覆盖 |
| **trading-devbox** | ✅ 采纳（待装） | ❌ **不采纳**：同 ClawHub 问题；现有组合已是快速回测路径 |
| **market-sentiment** | ⚠️ 暂缓 | 📋 维持 P2 候选。Phase 1 无需情绪因子；资金费率已含部分情绪信息 |
| **binance-pro** | ❌ 否决 | ❌ 维持否决，实盘阶段才评估且须代码级审查 |
| **self-improving-agent / taskmaster** | ❌ 否决 | ❌ 维持否决（无可部署 Alpha / 过度工程） |
| **onchain / crypto-cog / trading-research** | ❌ 否决 | ❌ 维持否决 |

---

## 五、决策汇总矩阵

| 候选 | 决策 | 时机 | 成本 |
|------|------|------|------|
| Triple Barrier（自实现，**仅方向性事件策略**） | ✅ 采纳方法论 | 下一方向性策略时 | 零 |
| 规则式状态门控（前身 Meta-Labeling） | ✅ 采纳 | P1-05 后设计策略时 | 零 |
| 事件采样（CUSUM） | 📋 理念采纳，新信号时落地 | 下个信号方向 | 零 |
| Purged/Embargo CV | ✅ 写入 Protocol，调参时生效 | 下一策略验证 | 零 |
| VectorBT 开源 | ✅ 继续用，暂不升级 PRO | 现在 | 零 |
| VectorBT PRO | 📋 大规模扫描时评估（D级付费） | Phase 1 中后期 | $20/月 |
| 两轴状态分类（强度×高周期方向） | ✅ P1-05 标准（以 TASK_P1_05 §2 为准） | 现在（P1-05） | 零 |
| Hurst 指数 | 📋 可选校验 | 按需 | 零 |
| Freqtrade（GPL-3.0） / NautilusTrader（LGPL-3.0） | 📋 Phase 2 参考 | Phase 2 | 零 |
| Desktop Commander → Codex 自动触发 | ✅ 近期最小路径（D级已确认+护栏） | 现在 | 零 |
| A2A / LangGraph / Claude Agent SDK | 📋 Phase 2 编排 | Phase 2 | 中/按量 |
| Mem0 / Graphiti | ❌ 当前不引入 | — | — |
| quant-research-platform / trading-devbox Skill | ❌ 反转否决（不可审计） | — | — |
| market-sentiment | 📋 Phase 2 候选 | Phase 2 | — |
| binance-pro / self-improving-agent / taskmaster / onchain / crypto-cog / trading-research | ❌ 否决 | — | — |

---

## 六、Tier 1 落地说明（接入现有 VectorBT 管线）

### 6.1 Triple Barrier 接入（仅当下一策略属方向性事件策略）

```
CCXT 拉数据 → signal_detector.py 产生信号
    ↓
triple_barrier_labels.py（自实现 ≤50行，借鉴 MLFinPy）
    输入：信号时间戳、OHLCV
    输出：label(+1/-1/0) + 实际退出时间 + 触发屏障类型
    参数：pt_sl 对称 + max_holding（时间屏障，如 24根K）；波动率用滚动 ATR 动态设障
    ↓
backtest.py 用三屏障退出时间作 exit_time
    ↓
报告增加：屏障触发分布（止盈/止损/时间）
```
注意：首次只替换退出逻辑、不改入场（单变量）；预登记为新版本；**非方向性机制策略不走此路径**。

### 6.2 规则式状态门控接入

```
主信号（Sweep 事件 / TSMOM 方向）
    ↓
两轴状态分类器（§6.3）→ 每根K线状态标签
    ↓
规则式门控：趋势↑·牛 + 做多 → 入场；趋势↑·熊 → 跳过；震荡 → 跳过或大幅减仓
    ↓
VectorBT 回测（保留 门控前 vs 门控后 对比）
```
报告指标：**覆盖率 / 保留率 / 状态间收益差异**（不用精确率/召回率，除非已训二级模型）。

### 6.3 两轴状态分类器（P1-05 以 TASK_P1_05 §2 为权威，下为参考骨架）

```python
import pandas_ta as ta
import numpy as np, pandas as pd

def classify_regime(ohlcv_4h, daily_df, adx_period=14, er_period=10):
    # 轴1 强度（4H）：ADX + Kaufman ER 交叉校验
    adx = ta.adx(ohlcv_4h.high, ohlcv_4h.low, ohlcv_4h.close, length=adx_period)
    adx_val = adx[f'ADX_{adx_period}']
    change = (ohlcv_4h.close - ohlcv_4h.close.shift(er_period)).abs()
    vol = ohlcv_4h.close.diff().abs().rolling(er_period).sum()
    er = change / vol.replace(0, np.nan)
    strong = (adx_val > 25) & (er > 0.5)          # 趋势
    choppy = (adx_val < 20)                        # 震荡

    # 轴2 牛熊方向（高周期，独立）：日线 close vs 200日MA（用 ≤t 数据，避免前视）
    daily_ma200 = daily_df.close.rolling(200).mean()
    bull_daily = (daily_df.close > daily_ma200)    # 重采样对齐到 4H 索引、shift 防前视
    bull = bull_daily.reindex(ohlcv_4h.index, method='ffill').shift(1)

    regime = pd.Series('choppy', index=ohlcv_4h.index)
    regime[strong &  bull] = 'trend_up_bull'       # 健康上升
    regime[strong & ~bull] = 'trend_up_bear_trap'  # 熊市反弹陷阱（2022 误判源）
    # …（趋势↓×牛熊、震荡×牛熊 按 TASK_P1_05 §2 网格补全）
    return regime
```
**两轴正交：强度轴(ADX/ER) 与 方向轴(高周期牛熊) 分开判定，禁用同周期 DI± 冒充方向轴。**

---

## 七、回灌主线（已执行，DEC-061 / Protocol v1.2）

**已写入 Research Protocol v1.2 第十节：** 三屏障（方向性事件策略默认基准）、规则式状态门控、两轴状态分类标准、Purged/Embargo CV 纪律、报告新增字段、借鉴前置纪律。

**已记入 DECISION_LOG（DEC-061 修订版）：** 库自实现纪律、D38 Skill 反转否决、Desktop Commander→Codex 自动触发（D级+护栏）、VectorBT PRO 延后、研究顺序（P1-05 优先）。

**研究顺序（不被工具方法打断）：** ① 完成 P1-05 两轴归因（禁改信号/退出）→ ② 据 edge 地图选下一策略 → ③ 仅当属方向性事件策略时引入三屏障 → ④ 再做 purge/embargo 与退出敏感性。

---

## 八、覆盖范围声明（未逐项评估 = 主动排除/延后）

任务书曾列以下候选，本轮**未逐项深评**，按下列定性处理，**不声称 Tier1~4 全覆盖**：

| 项 | 处理 | 理由 |
|----|------|------|
| 分数差分（Fractional Differentiation） | 📋 延后 | AFML 平稳化技巧；当前无 ML 因子建模需求，引入 carry/因子模型时再评估 |
| Trend-scanning labeling | 📋 延后 | 与三屏障同属 AFML 标签法；待方向性策略落地后比较 |
| HH/HL 结构（高低点序列） | 📋 延后并入 P1-05 | 可作"轴2 牛熊方向"的备选实现，归 P1-05/下一策略设计时定 |
| MCP 连接器（行情/数据类） | 📋 延后 | 当前 CCXT + data.binance.vision 已满足；Phase 2 实盘数据再评估 |
| CrewAI / AutoGen（多 Agent 编排） | ❌ 主动排除（现阶段） | 与 A2A/LangGraph 同类重型编排，Phase 2 有稳定流程后统一评估，避免过早固化 |

---

## 九、来源表（访问日期 2026-06-07）

| 主题 | 来源 | 关键事实 |
|------|------|---------|
| Triple Barrier / Meta-Labeling / Purged CV | López de Prado《Advances in Financial Machine Learning》(2018) | 方法论原始出处 |
| MLFinPy | github.com/baobach/mlfinpy ; pypi.org/project/mlfinpy | MIT 开源；单维护者；作参考、不硬依赖 |
| mlfinlab | hudsonthames.org/mlfinlab | 商业闭源，£100/月，不采纳 |
| NautilusTrader | github.com/nautechsystems/nautilus_trader | **LGPL-3.0**；近期活动 2026-05；Rust+Python |
| Freqtrade | github.com/freqtrade/freqtrade/releases | **GPL-3.0**；最新 **2026.4（2026-04-30）** |
| ADX / ER | pandas-ta、ta-lib（ADX）；Perry Kaufman（ER） | 纯计算，无重型依赖 |

> 维护说明：许可证/版本随时间变化，Phase 2 实际引入前须复核来源页并更新本表。

---

## 十、一句话结论

**当前最高价值动作是先跑 P1-05 两轴归因，不是引入工具。** 工具方法论（三屏障/状态门控/Purged CV）在 P1-05 给出 edge 地图、确定下一策略后才按需落地——且三屏障只对方向性事件策略适用。系统建设与 Agent 编排留 Phase 2。这是对"重复造轮"和"手工搬运"的统一答案，且不打断主线。
