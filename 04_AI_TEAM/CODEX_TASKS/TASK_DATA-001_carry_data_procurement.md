# Codex任务书：carry v4 缺失数据采购

**任务ID：** DATA-001  
**对应项目任务：** P1-RES-030A  
**优先级：** P1（最高，解除FEASIBILITY-LOCK阻塞②）  
**创建时间：** 2026-06-20  
**预估规模：** 5-8个脚本文件，数据输出到 `08_DATA/carry/`  
**指定Codex Skill：** `PlanToDelivery`（多步骤交付，需完整闭环）+ `tdd`（数据下载脚本必须有验证测试）

---

## 背景与目的

carry v4 预登记（CARRY_DELTA_NEUTRAL_PREREG_v4.md）已通过第四轮独立盲审（APPROVED），custodian 封存已完成（2026-06-20，预登记文件已chmod-000）。

**当前阻塞：** 历史 FEASIBILITY-LOCK 无法运行，因为 v4 计算引擎需要的 8 个数据输入目前缺失。本任务采购这 8 个输入。

完成本任务后，双重阻塞的阻塞②即解除，carry FEASIBILITY-LOCK 可立即运行（P1-RES-030）。

---

## 研究约束（强制继承）

- 禁止读取 `~/.aiquant_sealed/` 下任何文件（carry v4 预登记已封存于此）
- 数据必须有 schema 验证：字段名、类型、时间范围、空值率检查
- 所有下载脚本必须有幂等性：重复运行不损坏已有数据
- 数据来源只用官方 API，不用第三方聚合（除非官方 API 无法获取）

---

## 具体目标（8项数据，按优先级）

### 第一批：Binance 官方 REST API（高置信度，优先完成）

**1. Spot 1H open价格（BTC/USDT, ETH/USDT）**
- 问题：现有数据只有 close，缺 open（v4 entry price 用 open）
- 来源：`data.binance.vision/data/spot/monthly/klines/{symbol}/1h/`
- 时间范围：2020-01-01 至 2024-12-31（历史 FEASIBILITY-LOCK 区间）
- 输出字段：timestamp, open, high, low, close, volume
- 输出路径：`08_DATA/carry/spot_1h/{symbol}_1h_YYYYMM.parquet`

**2. Perpetual Contract 1H OHLC（BTC独立于mark price）**
- 问题：现有数据是 mark price，缺 contract price（影响实际持仓 PnL）
- 来源：`/fapi/v1/klines?symbol=BTCUSDT&interval=1h` 分页拉取
- 时间范围：同上
- 输出路径：`08_DATA/carry/perp_1h/{symbol}USDT_contract_1h.parquet`

**3. Binance 永续合约 Index 1H close（BTC, ETH）**
- 问题：v4 需要 index price 作为 fair value 基准
- 来源：`/fapi/v1/indexPriceKlines?symbol=BTCUSDT&interval=1h`
- 输出路径：`08_DATA/carry/index_1h/{symbol}USDT_index_1h.parquet`

**4. ADL tier 当前状态记录（BTC, ETH perp）**
- 问题：历史 ADL 执行记录不可得（Binance 不开放历史 ADL 数据）
- 来源：`/fapi/v1/adlQuantile?symbol=BTCUSDT`（当前 tier 快照）
- 处理方式：**历史期间 ADL 按模型假设处理**（见下方"ADL模型假设"节）；当前接口只用于验证接口可用性
- 输出：在 `08_DATA/carry/metadata/adl_note.md` 写明假设并存档

**5. 历史 Leverage Brackets（floor/cap/mmr/cum，BTC, ETH）**
- 问题：v4 强平路径模型需要 mmr 参数
- 来源：`/fapi/v1/leverageBracket?symbol=BTCUSDT`（当前值）
- 注意：Binance 不开放历史杠杆档位变更记录。**处理方式：采集当前值 + 查 Binance 公告历史有无重大修改（搜索"leverage bracket" site:binance.com/support/announcement）**
- 输出路径：`08_DATA/carry/metadata/leverage_brackets_{symbol}.json`

### 第二批：事件数据（需人工+自动化结合）

**6. 历史强平手续费率**
- 问题：v4 强平成本模型需要清算手续费率（通常为仓位 0.5%）
- 来源：Binance 费率说明页面 + 公告历史
- 处理方式：以 0.5% 作为默认值（符合 Binance 文档），搜索 2020-2024 是否有变更公告
- 输出路径：`08_DATA/carry/metadata/liquidation_fee_history.md`（记录来源、日期、费率值）

**7. USDT 脱锚事件时间表**
- 问题：v4 事件压力档需要 USDT 脱锚历史（影响 cross-margin 实际亏损）
- 来源：Binance spot `USDT/BUSD` 或 `TUSD/USDT` 价格数据中异常偏离检测（偏离 > 0.3% 持续 > 1h）
- 替代来源：`/api/v3/klines?symbol=USDCUSDT&interval=1h`（USDC/USDT 对，稳定币之间偏离=USDT脱锚信号）
- 输出路径：`08_DATA/carry/events/usdt_depeg_events.parquet`（timestamp, deviation_pct, duration_h）

**8. Binance 提币暂停事件时间表**
- 问题：v4 需要标记"无法执行 spot 腿退出"的时段（提币暂停 = 期货腿被迫持仓）
- 来源：Binance 公告历史（自动抓取 `https://www.binance.com/en/support/announcement/c-49` 类别）
- 处理方式：搜索标题含 "withdrawal", "maintenance", "suspend" 的公告，提取时间范围
- 输出路径：`08_DATA/carry/events/withdrawal_suspension_events.md`（日期、持续时间、涉及币种）
- **注：如果公告页面抓取失败，写占位文件并注明"历史提币暂停记录需人工补充"，不阻塞其他7项**

---

## ADL模型假设（必须写入报告）

由于 Binance 不开放历史 ADL 执行记录，v4 历史 FEASIBILITY-LOCK 期间采用以下保守假设：
- ADL 触发概率：在极端市场（日内波动 > 15%）期间，假设 0.5% 的持仓在 ADL 中被减少
- ADL 减仓幅度：假设最大减仓 50%（最坏情况，与 OI 触发规则对齐）
- 实证验证门：前向 shadow 期间接入 `/fapi/v1/adlQuantile` 实时监控

---

## 输入文件

- `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md` — **只读**（-r--r--r--），不得修改
- `02_KNOWLEDGE_BASE/CARRY_KNOWLEDGE.md §三` — 数据需求清单
- `02_KNOWLEDGE_BASE/TOOLS_KNOWLEDGE.md §一` — 工具使用规范（CCXT/Binance REST）

---

## 输出产物

- `08_DATA/carry/spot_1h/` — spot 1H OHLC（BTC, ETH）
- `08_DATA/carry/perp_1h/` — perp 合约 1H OHLC（BTC, ETH）
- `08_DATA/carry/index_1h/` — index 1H close（BTC, ETH）
- `08_DATA/carry/metadata/leverage_brackets_{symbol}.json` — 杠杆档位
- `08_DATA/carry/metadata/liquidation_fee_history.md` — 强平手续费历史
- `08_DATA/carry/metadata/adl_note.md` — ADL 假设备忘
- `08_DATA/carry/events/usdt_depeg_events.parquet` — USDT 脱锚事件
- `08_DATA/carry/events/withdrawal_suspension_events.md` — 提币暂停事件
- `08_DATA/carry/data_manifest.yaml` — 数据清单（文件路径、时间范围、行数、SHA256、来源）
- `04_AI_TEAM/CODEX_TASKS/REPORT_DATA-001_carry_data_procurement.md` — 任务报告（必须）

---

## 报告格式（REPORT_DATA-001必须包含）

```
## 摘要（含：8项数据哪些完整、哪些用替代、哪些缺失+原因）
## 执行步骤（含：每项数据的下载命令/API端点）
## 数据质量检查（schema、时间范围、空值率、异常值）
## 模型假设记录（ADL + 提币暂停 + 强平费率 + 杠杆档位）
## 对CARRY_KNOWLEDGE.md的更新建议（具体指出更新哪一节）
## 验收结果（逐项核对下方验收标准）
## 未解决问题
## 建议下一步（如：哪项数据需要人工补充，何时可运行FEASIBILITY-LOCK）
```

---

## 禁止项

- 禁止读取 `~/.aiquant_sealed/` 下任何文件
- 禁止使用 Hyperopt 或任何参数优化
- 禁止在报告里只给数字不给判断（每项数据必须有"质量结论"）
- 禁止因第8项（提币暂停）抓取失败而阻塞其他7项
- 禁止修改 CARRY_DELTA_NEUTRAL_PREREG_v4.md（只读保护）

---

## 验收标准（Claude验收时逐项核对）

- [ ] `08_DATA/carry/data_manifest.yaml` 存在，含所有文件的路径、行数、SHA256
- [ ] Spot 1H open 已下载：BTC+ETH，2020-2024，行数与预期月份匹配（约43800行/symbol）
- [ ] Perp 1H OHLC 已下载：与 spot 时间范围对齐
- [ ] USDT 脱锚事件文件存在（即使0事件也要有文件+说明）
- [ ] ADL 假设已书面化在 `adl_note.md`
- [ ] 报告含"模型假设记录"节，逐项写明来源和假设值
- [ ] 报告含"建议下一步"，明确写出"FEASIBILITY-LOCK 现在是否可运行/还缺什么"
- [ ] 所有下载脚本有验证测试（pytest 或 assert 检查行数/schema/时间范围）

---

## Founder执行命令

```bash
cd /Users/yaomingyu/Documents/AI_QUANT_COMPANY
codex --approval-mode auto-edit "读取并执行 04_AI_TEAM/CODEX_TASKS/TASK_DATA-001_carry_data_procurement.md 中的任务"
```
