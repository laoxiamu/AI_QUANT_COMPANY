# REPORT_RESEARCH_OSS

完成时间: 2026-06-19 UTC+08  
任务: RESEARCH-OSS-TOOLS 第三方/开源工具 build-vs-buy 调研

## 产出

- 主报告: `00_PROJECT_MANAGEMENT/STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md`
- 完成事件: `04_AI_TEAM/TASK_INBOX/RESEARCH_OSS_DONE.json`

## 验收自检

| 要求 | 状态 |
|---|---|
| 调研 CCXT 能力/成熟度/成本/接入难度/推荐结论 | 完成 |
| 调研 Freqtrade / NautilusTrader / vectorbt 生态并给地基建议 | 完成 |
| 调研 Binance 官方 SDK + data.binance.vision + mark/contract/funding/OI 正确取法 | 完成 |
| 调研 Coinglass / CoinAPI / Kaiko / Amberdata 强平、funding、OI 覆盖与成本 | 完成 |
| 调研交易所 MCP/插件现状与可靠性 | 完成 |
| 输出自建 vs 采用对照表 | 完成 |
| 输出推荐技术栈和 1-2 月落地路线 | 完成 |
| 禁读 Holdout、禁改研究文件 | 已遵守 |

## 核心结论

推荐 Phase 1 采用 `Freqtrade + Binance 官方历史/REST + CCXT 薄适配 + CoinGlass 小套餐（如强平是核心变量）`。  
NautilusTrader 暂列 Phase 2 生产级迁移候选；vectorbt 只做研究加速；MCP/插件只读查询，不进入交易闭环。

## 未完成或风险

- 未实际申请 CoinGlass/CoinAPI/Amberdata/Kaiko API key，因此价格与覆盖以公开页面为准，接入前仍需用真实 key 做 1 天数据抽样。
- 未修改任何交易代码或采集器，本任务仅为 build-vs-buy 决策报告。
