# C1 / C2 批次结果速记

**执行日期：** 2026-06-13  
**执行方式：** VM 直跑（43.160.200.224），Mac Codex 批次因代理不可达失败后改 SSH 直连  

---

## C1：TSMOM Universe 扩充可行性探针

**目标：** 检验 TSMOM universe 能否从当前 8 币扩充至 ≥20 币。

**筛选条件：**
- onboard_date ≤ 2021-06-30（样本内上线，有足够历史）
- USDT 永续合约，非当前 8 币
- 未退市 or 退市日 ≥ 2024-06-01

**结果：**

| 指标 | 数值 |
|---|---|
| 总候选数 | 88 |
| **可构建（双 HEAD 通过）** | **83** |
| head_first_ok only | 83 |
| head_recent_ok only | 88（全部通过） |
| 不可构建（early archive 缺失）| 5（BCHUSDT, SKLUSDT, REEFUSDT, GTCUSDT, OGNUSDT）|

**估算 bar 数分布：** 7,250–10,362 根 4H bar（中位约 8,700，相当于 4.8 年数据）

**D级决策输入：** universe 扩充至 20 币无任何数据障碍；83 个候选足够支撑多档规模测试（20 / 30 / 50 币）。

---

## C2：Carry Spot-Perp Basis 数据（4H）

**目标：** 采集 BTC / ETH spot 1H + futures 4H，计算现货-永续价差（basis_pct）。

**数据范围：** 2020-01 ~ 2024-12-09（月度 ZIP，monthly archive）

**结果：**

| Symbol | rows | mean(%) | median(%) | p5(%) | p95(%) | n(<-2%) |
|---|---|---|---|---|---|---|
| BTCUSDT | 10,829 | -0.0027 | -0.0284 | -0.0658 | +0.1123 | 0 |
| ETHUSDT | 10,829 | +0.0054 | -0.0227 | -0.0672 | +0.1331 | 1 |

**解读：**
- spot-perp 价格基差极小（±0.07~0.13%量级），说明 Binance perp 通过资金费率机制与现货高度锚定。
- basis_pct 右偏（median < mean）：偶发 contango 溢价（多头杠杆旺盛时 perp > spot）。
- **此 basis 非资金费率本身**——实际 carry 收益来自每 8h 支付的资金费率，项目已有 FUNDING_8H 数据。本 C2 数据可作为资金费率信号的辅助（price basis 正→多头拥挤→funding rate↑ 预期）。

**文件产出：**
- `06_RESEARCH/DATA/carry_basis_4H.csv`（BTC+ETH 合并，21,658 行）
- `06_RESEARCH/DATA/BTCUSDT_SPOT_1H.csv`
- `06_RESEARCH/DATA/ETHUSDT_SPOT_1H.csv`
- `06_RESEARCH/DATA/c2_basis_stats.json`

---

## 下游行动

- **C1 → TSMOM D级讨论**：数据可行性已确认，推荐 Option A（universe 扩充 ≥20 币）提报 Founder。
- **C2 → Carry sleeve**：price basis 极小，carry sleeve 的核心边际来自 funding rate 而非 basis；后续研究应以 FUNDING_8H 为主数据，本 C2 作辅助。
