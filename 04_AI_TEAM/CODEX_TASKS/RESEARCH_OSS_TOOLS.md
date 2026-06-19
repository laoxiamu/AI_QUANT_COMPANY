# RESEARCH-OSS-TOOLS：第三方/开源工具 build-vs-buy 调研（落实 Founder 早前指令）
调用：`--sandbox danger-full-access`（需联网调研/web）。
背景：Founder 早就要求调研三方工具/开源、不重复造轮子；项目却在手搓脆弱 WS 采集器、计划从零建交易系统。本任务给出务实的 build-vs-buy 方案。约束：3万本金/1人/月1000元/想1-2月出最小可跑系统/币安为主。
## 调研并给结论（每项：能力/成熟度/成本/接入难度/是否推荐+理由）
1. **CCXT**：统一交易所接口，能否覆盖我们的 行情/历史K线/funding/OI/下单/账户 需求？能否取代自建采集器？
2. **Freqtrade / NautilusTrader / vectorbt 生态**：哪个最适合做我们的"回测+纸面+实盘"地基？能白送多少（执行/风控/对账/监控）？我们只需自己写什么？
3. **币安官方 SDK**（binance-connector / python-binance）+ **历史数据**（data.binance.vision）：mark vs contract、funding、OI 的正确取法，避免我们踩过的 contract/mark、base/quote volume 坑。
4. **强平/衍生品数据商**：Coinglass / CoinAPI / Kaiko / Amberdata —— 谁有强平(liquidation)、funding、OI 历史+实时，价格/免费额度？能否直接取代我们那个反复出问题的自建强平采集器？
5. **交易所 MCP/插件** 现状与可靠性，是否值得用。
## 输出 `00_PROJECT_MANAGEMENT/STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md`：一张"自建 vs 采用"对照表 + 推荐技术栈（最小可跑系统该用哪几个现成件、只自写哪层）+ 1-2 月落地路线。写 `04_AI_TEAM/TASK_INBOX/RESEARCH_OSS_DONE.json`。禁读HOLDOUT,不改研究文件。
