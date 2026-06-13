# DEC070-AUDIT：TSMOM 扩展 universe DEC-070 过滤器可审计性审计

**任务类型：** 数据分析 + 可审计性核查（**纯分析，不改任何策略，不耗独立命数**）
**目的：** D2 阻塞项之一 = `DEC_070_FILTERS_NOT_AUDITABLE`。本任务对现有 `06_RESEARCH/DATA/FUTURES_EXPANDED/` 35 个候选资产，**就现有数据能算的 DEC-070 过滤器逐项计算并产出可审计证据**，并**精确界定哪些过滤器需要外部数据（当前不可得）**。
**输出：** `06_RESEARCH/RESULTS/20260614_dec070_filter_audit.md` + `06_RESEARCH/CODE/output/dec070_filter_audit.json`
**严格边界：** 不读 Holdout；不读 `01_MEMORY_CORE/`；不下载新数据；不构建任何回测；不对 universe 是否扩展下结论（那是 D 级，Founder 决定）。你只产出"哪些资产按可计算过滤器达标 / 哪些过滤器无本地数据可证"的事实证据。

---

## 背景（DEC-070 四项硬过滤器）

DEC-070 要求 TSMOM universe 入选须过四项操盘风险硬过滤：
1. 日均成交量（ADTV）门槛
2. 流通市值比（float_market_cap_ratio，防低流通锁仓操控）
3. OI/市值比（oi_market_cap_ratio，防合约拥挤猎杀）
4. 历史价格异常跳动频率（price_jump_frequency）

现状：`DOWNLOAD_MANIFEST.json` 只证明了历史长度/归档可得/手工黑名单，**未证明这四项**。

---

## 任务步骤

### 第一部分：可从现有 4H K 线计算的过滤器

`FUTURES_EXPANDED/` 每个资产是 4H contract klines（含 OHLCV，volume/quote_volume）。对 35 个资产各计算：

1. **ADTV 代理**：用 quote volume（USDT 计价成交额）按日聚合，报告 cutoff 前全样本的**中位数日成交额**与**最近 180 日中位数日成交额**。给出一个合理 ADTV 门槛建议（如中位数日成交额 ≥ 某量级）并标注哪些资产达标/不达标。门槛值由你提出但须说明依据，并明确这是**可被复算的**。
2. **price_jump_frequency**：定义单根 4H 对数收益 `|r| > JUMP_THRESHOLD`（建议 JUMP_THRESHOLD=15%，并报告对 10%/20% 的敏感性）为异常跳动；报告每个资产 cutoff 前异常跳动**频率**（异常根数/总根数）与绝对次数。给出合理上限门槛建议，标注达标/不达标。

两项均须：公式自包含、阈值冻结说明、产出每资产数值表。

### 第二部分：需外部数据的过滤器（精确界定数据缺口）

3. **float_market_cap_ratio**：需要流通供应量 + 市值（CoinGecko/CMC 级基本面数据），本地 K 线**无法**计算。明确声明不可计算，并列出最小可行外部数据源（如 CoinGecko 历史 supply/mcap API），估计获取成本。
4. **oi_market_cap_ratio**：需要历史 OI（Binance `openInterestHist` 仅近 30 天，历史 OI 难得）+ 市值。明确声明历史不可得的约束（OI 历史窗口限制），列出可行性与替代代理（如近端 OI/成交额比）。

### 第三部分：综合分层

基于**第一部分两项可计算过滤器**，把 35 个资产分为：
- **Tier 1-clean**：两项可计算过滤器都达标。
- **Tier 1-watch**：一项达标一项边缘。
- **排除**：任一项明显不达标（高跳动/低流动性）。

明确声明：该分层**仅基于 2/4 过滤器**，float/OI 两项未验证，故为**部分证据**，不构成 universe 最终确认。

---

## 输出格式（`20260614_dec070_filter_audit.md`）

```markdown
# DEC-070 过滤器可审计性审计（35 候选资产）
**执行：** Codex｜**日期：** 2026-06-14｜**数据：** FUTURES_EXPANDED 4H klines（cutoff<2024-12-10）

## 摘要：4 过滤器可审计性
| 过滤器 | 本地可算? | 结论 |
（ADTV/jump=可算；float_mcap/oi_mcap=需外部数据）

## 第一部分：ADTV + price_jump_frequency 每资产表
| 资产 | 日成交额中位数 | 最近180d | ADTV达标 | jump频率(15%) | jump达标 |

## 第二部分：外部数据缺口（float_mcap_ratio / oi_mcap_ratio）
[数据源 + 可行性 + 成本]

## 第三部分：基于2/4过滤器的分层（部分证据）
Tier1-clean / Tier1-watch / 排除

## 给主理人的一句话事实结论（不下D级结论）
```

完成后写 `04_AI_TEAM/TASK_INBOX/DEC070_AUDIT_DONE.json`（task_id=DEC070_AUDIT, status, output_file, notes=最重要事实发现，如"X/35达标，2过滤器需外部数据"）。

## 调用与七问
- 七问前置已由 Claude 完成。机制：给 D 级 universe 决策提供可审计事实而非猜测。
- 失败关闭：若某资产数据异常无法计算，标 N.A. 并说明，不臆造。
