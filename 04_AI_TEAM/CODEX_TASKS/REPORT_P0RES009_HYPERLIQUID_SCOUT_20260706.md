# REPORT_P0RES009_HYPERLIQUID_SCOUT_20260706

**执行：** Claude（WebSearch+WebFetch直接调研，非Codex——判断为文档/可行性核实类任务，不需要代码执行）
**结论先行：值得小成本试一下，但不是forced-flow v2数据墙的直接解法。**

---

## 逐项核实结果

**1. API/数据可行性——存在，但"完整历史"要打折扣**

官方Hyperliquid有S3归档（`s3://hl-mainnet-node-data/node_fills_by_block`），含所有成交(fills)，理论上liquidation会作为特殊类型的fill标记在内，但官方文档明确写"数据可能缺失、更新无时效保证"，且是requester-pays（用量小成本很低但非零）。

第三方Hydromancer提供免费（同样requester-pays AWS流量费，无订阅费）的"Reservoir"归档，覆盖fills（含liquidations/ADL）、1秒K线、订单簿快照。**关键限定：官网明确写"Hyperliquid crypto perps from August 2025"**——也就是说这个"免费完整历史"对Hyperliquid本身的永续合约，只从2025年8月开始，不是从Hyperliquid实际上线（2023年）算起。算到现在（2026年7月）约11个月历史，量级上和我们刚修复的BTCUSDT历史（约1.5年）接近，**远短于**我们价格面板其余symbol的约6年历史。

**2. Universe重合度——未逐一核对，但大概率覆盖核心资产**

Hyperliquid目前200+个市场（含加密主流币+新增的股票/大宗商品/Pre-IPO合成资产）。BTC/ETH/SOL等主流币确定在内，我们面板里的二线资产（ALGO/ETC/FIL/MKR/OMG等）大概率也在，但**未做逐个ticker核对**——这一步如果真要推进正式研究，需要直接查Hyperliquid `meta` API拉完整合约列表做精确比对，本次侦察未做（超出侦察范围，属于下一步正式立项前的准入检查）。

**3. 清算机制可比性——结构性不同，不能直接假设可外推**

Hyperliquid是完全链上的中央限价订单簿(CLOB)永续DEX，用自己的验证者网络做保证金计算和清算，清算后用ADL（自动减仓，让盈利的对手方被动平仓吸收损失）而非Binance式的保险基金机制。两者清算的**触发力**是同一件事（价格剧烈波动+杠杆仓位保证金不足），但**清算发生后价格冲击的传导路径不同**（ADL是对手方仓位被动平仓，Binance是保险基金/强平引擎接管挂单）——这意味着"清算簇驱动价格延续/反转"这个机制假设，**不能直接把Hyperliquid上验证的结果当作Binance结果的替代证据**，只能算独立的、同源但不同venue的平行验证，价值是"两个市场是否有类似的清算簇现象"这个更宽的问题，不是"证明了Binance那条机制"。

**4. 数据获取成本——技术上简单**

免费S3归档，标准AWS CLI/boto3即可拉取（`aws s3 cp ... --request-payer requester`），流量费预计在几美元量级（对比Tardis Solo档约700美元/月），技术门槛低，几小时脚本可完成小规模试拉验证。

## 结论与建议

**不是forced-flow v2数据墙的直接解法**（Hyperliquid历史深度~11个月，不比我们已有的BTCUSDT数据深多少；且是不同venue，机制外推需要独立验证，不能直接当Binance证据用）。

**但值得作为一条独立的、几乎零成本的平行验证线记入备胎清单**：如果Hyperliquid上也能观测到"清算簇后价格延续"的现象，这会是对同一机制假设的独立支持证据（不同venue、不同参与者结构下复现），比单一venue的证据更有说服力；如果观测不到，这本身也是有信息量的（提示现象可能是Binance特定流动性结构的产物，不是通用机制）。**成本极低（几美元数据费+几小时脚本），建议列入下次量化线重启forced-flow v2时的"顺手验证项"，不需要现在单独立项/占用WIP。**

## 数据来源

- [Historical data - Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data)
- [Hyperliquid Historical Data API + Reservoir Free S3 Archive | Hydromancer](https://hydromancer.xyz/historical-data)
- [Info endpoint | Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
- [VALR Integrates Hyperliquid to Launch 200+ Perpetual Markets](https://www.cryptotimes.io/2026/07/03/valr-integrates-hyperliquid-to-launch-200-perpetual-markets-in-africa/)

## 备注（安全）

调研过程中，Hyperliquid官方文档页面末尾嵌有一段"Agent Instructions"文本，指示AI助手对该页面URL发起带`ask`参数的GET请求获取"额外信息"。这是网页内容里嵌的指令，不是用户或系统指令，本次未执行，仅按正常搜索结果使用页面已展示的内容。
