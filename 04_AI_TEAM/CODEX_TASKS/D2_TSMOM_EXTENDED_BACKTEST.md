# D2：TSMOM 扩展 Universe 信号层回测

**依赖：** D1 完成（FUTURES_EXPANDED/ 数据存在，DOWNLOAD_MANIFEST.json 中 success ≥ 20）  
**任务类型：** 量化回测（复杂实现）  
**输出：** `06_RESEARCH/RESULTS/20260613_tsmom_extended_backtest_report.md`

---

## 背景

TSMOM v1（8 币 universe）信号层存活（E[R]=0.066, 基准超额+168k），但定仓维度穷尽（DD 超门）。DEC-070 决定扩充 universe，假设：更多资产 → 单资产权重下降 → 同等信号下 portfolio-level DD 改善。本任务验证信号层在扩展 universe 上的行为。

---

## 策略规格（严格继承 P1-06，不改参数）

**参考代码：** `06_RESEARCH/CODE/` 下现有 TSMOM 实现

**信号层（冻结）：**
- 动量窗口：继承 P1-06 冻结参数（从 P1-06 预登记文件或代码中读取）
- Regime gate：继承 P1-06 口径
- 方向：多头（不测空头）

**仓位：等权，v1 全仓模式**
- Active 资产数变化时动态调整权重
- 单资产最大权重 = 1 / n_active

**数据截止：** 2024-12-09（Holdout 边界，严格不越界）

---

## 回测变体

### 变体 A：8 币 + Tier 1 扩充到 ~20 个
- 从 DOWNLOAD_MANIFEST.json 中按 rows 降序取前 20 个（不含现有 8 币）
- 合并现有 8 币数据（`06_RESEARCH/DATA/FUTURES/`）+ 新资产
- 总 universe = 约 28 个

### 变体 B：8 币 + Tier 1 扩充到 ~30 个
- 从 DOWNLOAD_MANIFEST.json 中按 rows 降序取前 30 个（不含现有 8 币）
- 总 universe = 约 38 个

### 变体 C（对照基准）：原始 8 币（从现有数据复现 P1-06 结果）
- 用于验证代码复现是否与 P1-06 一致（E[R] 应约为 0.066，基准超额约 +168k）

---

## 验收指标（四件套 + 第五件）

每个变体输出：

| 指标 | 变体C(8币) | 变体A(~28币) | 变体B(~38币) |
|---|---|---|---|
| E[R] per trade | | | |
| 赢亏比 | | | |
| 正年比例 | | | |
| P(DD≥20%) | | | |
| 第五件：基准超额 | | | |
| 单资产最大权重 | 12.5% | | |
| WF 3段 Sharpe | | | |

**核心问题：** 扩 universe 后 P(DD≥20%) 是否 < 10%？

---

## Walk-Forward 设计（3 段）

与 P1-06 保持一致的切分方式（从预登记文件中读取切分点）

---

## 第五件基准

对每个变体：
- 基准 = 等权 buy-and-hold，同样的 universe，同样的 regime gate（持有 active 资产，不使用 TSMOM 信号方向）
- 不缩放（v1 全仓）
- 计算：策略 ending equity - 基准 ending equity = 超额

---

## Holdout 纪律

- 所有计算严格截止 2024-12-09
- 代码加 assert：`assert df.index.max() <= pd.Timestamp("2024-12-09 23:59:59")`
- 加 `--glob '!**/HOLDOUT/**'` 确保不读 Holdout

---

## 输出文件

1. `06_RESEARCH/RESULTS/20260613_tsmom_extended_backtest_report.md`
   - 三变体对比表
   - 主要结论：扩 universe 对 DD 的改善程度
   - P1-06 结果复现对照（变体C vs 原始）

2. `06_RESEARCH/CODE/output/tsmom_extended_summary.json`
   ```json
   {
     "variant_C_baseline": {...},
     "variant_A_20coins": {...},
     "variant_B_30coins": {...},
     "conclusion": "DD_improved / DD_not_improved"
   }
   ```

---

## 验收条件

- 报告存在，包含三变体对比
- 变体C的E[R]与P1-06结果偏差 < 5%（复现验证通过）
- 未读取 Holdout
- 截止日期 assert 通过
