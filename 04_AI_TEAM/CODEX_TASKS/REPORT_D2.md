# REPORT_D2

**[专业异议]**

## 状态

**BLOCKED。** 变体 C 复现完成；变体 A/B 未执行，原因是继续执行会违反单变量、完整成本和 DEC-070 universe 约束。

## 七问自查

1. 验证机制：更多经质量过滤且同口径资产是否通过降低单资产权重改善组合 DD。
2. 验收量化：三变体四件套、第五件、WF Sharpe、P(DD≥20%)<10%、C 的 E[R] 偏差<5%。
3. 更便宜等效实现：复用已审计 `tsmom_dual_engine`，先复现 C，再对 A/B 做输入失败关闭。
4. 禁止项：未读 Holdout、未改预登记、未简化成本、未用全样本分位、未引黑箱依赖。
5. 变量能否作用于 DD：能，但只有价格源、成本和 universe 质量固定时才是 universe 单变量。
6. 最可能失败原因：扩展资产高相关/高 beta 使表面分散无效，或低质量小币引入更大尾部；当前输入无法区分。
7. 专业异议：D1 数据层不足以支持 D2 主判定，已暂停 A/B。

## 已完成

- D1 manifest 审计：`success=35`，前 20/30 选择可确定。
- 变体 C：E[R] `0.066073`，相对基线偏差 `0.000000%`，复现通过。
- 变体 C 第五件超额：`$168,664.44`。
- 截止日期 assert：通过。
- Holdout：未读取。
- 新增失败关闭脚本与单元测试。

## 阻塞项

- `PRICE_SOURCE_MISMATCH`：D1 expanded files use contract klines, while the frozen 8-asset baseline uses mark-price klines. Mixing them is not a single-variable universe test.
- `MISSING_REAL_FUNDING`：30/30 selected expanded assets lack pre-cutoff real 8H funding files: ETCUSDT, LINKUSDT, TRXUSDT, XLMUSDT, XMRUSDT, DASHUSDT, XTZUSDT, ATOMUSDT, ZECUSDT, THETAUSDT, ALGOUSDT, ZRXUSDT, KNCUSDT, COMPUSDT, OMGUSDT, SNXUSDT, MKRUSDT, DOTUSDT, CRVUSDT, RUNEUSDT, YFIUSDT, SUSHIUSDT, EGLDUSDT, ICXUSDT, UNIUSDT, AVAXUSDT, ENJUSDT, FTMUSDT, RENUSDT, AAVEUSDT
- `DEC_070_FILTERS_NOT_AUDITABLE`：DOWNLOAD_MANIFEST.json does not prove the DEC-070 hard filters: adtv, float_market_cap_ratio, oi_market_cap_ratio, price_jump_frequency

## 剩余步骤

- 纠正 D1 价格源为 mark-price 4H。
- 补齐入选 30 资产真实 8H funding。
- 补齐并验收 DEC-070 四项 universe 质量过滤证据。
- 恢复运行 A/B，更新 summary 的结论为 `DD_improved` 或 `DD_not_improved`。

## 产物

- `06_RESEARCH/CODE/d2_tsmom_extended_backtest.py`
- `06_RESEARCH/CODE/tests/test_d2_tsmom_extended_backtest.py`
- `06_RESEARCH/CODE/output/tsmom_extended_summary.json`
- `06_RESEARCH/RESULTS/20260613_tsmom_extended_backtest_report.md`
- `04_AI_TEAM/CODEX_TASKS/REPORT_D2.md`

## Git

未 commit。任务处于 blocked，不能按“完成任务”提交。
