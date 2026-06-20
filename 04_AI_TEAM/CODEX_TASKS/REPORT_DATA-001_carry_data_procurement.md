# REPORT DATA-001 — carry v4 缺失数据采购

**任务ID：** DATA-001  
**状态：** blocked  
**执行时间：** 2026-06-20 UTC  
**执行命令：** `python3 06_RESEARCH/CODE/procure_carry_data.py --output 08_DATA/carry --timeout 5`  

## 摘要

本轮没有完成 8 项数据采购；已完成的是可复跑、带验证测试的官方 Binance 采购脚本，以及能离线落地的模型假设文件。FEASIBILITY-LOCK 现在不能运行。

逐项结论：

| 数据项 | 状态 | 质量结论 |
|---|---:|---|
| 1 Spot 1H open BTC/ETH | blocked | 未下载。`data.binance.vision` 请求被本机代理 `127.0.0.1:7897` 阻断，未生成 parquet，不能用于 v4 entry price。 |
| 2 Perp contract 1H OHLC BTC/ETH | blocked | 未下载。`/fapi/v1/klines` 请求被代理阻断，不能与 spot 对齐。 |
| 3 Index 1H close BTC/ETH | blocked | 未下载。`/fapi/v1/indexPriceKlines` 请求被代理阻断，fair value 基准缺失。 |
| 4 ADL tier 当前状态 | partial | `adl_note.md` 已写入 v4 指定历史 ADL 模型假设；实时 `/fapi/v1/adlQuantile` 是签名端点，本轮缺 `BINANCE_API_KEY/BINANCE_API_SECRET`，未采集当前快照。 |
| 5 Leverage brackets BTC/ETH | blocked | 未采集。`/fapi/v1/leverageBracket` 是签名端点，本轮缺 Binance API key/secret。 |
| 6 强平手续费率历史 | partial | 已写入默认 0.5% 建模值与审计提醒；官方页面/公告历史搜索因网络不可用未完成，不能视为历史变更审计完成。 |
| 7 USDT 脱锚事件 | blocked | 未生成 parquet。`/api/v3/klines?symbol=USDCUSDT&interval=1h` 请求被代理阻断。 |
| 8 提币暂停事件 | allowed-placeholder | 已按任务书允许路径写占位文件，明确需人工补充公告历史；该项不阻塞其他项，但当前其它项仍阻塞。 |

## 执行步骤

新增代码：

- `06_RESEARCH/CODE/procure_carry_data.py`
- `06_RESEARCH/CODE/carry_data_procurement/binance.py`
- `06_RESEARCH/CODE/carry_data_procurement/schemas.py`
- `06_RESEARCH/CODE/carry_data_procurement/events.py`
- `06_RESEARCH/CODE/carry_data_procurement/io_utils.py`
- `06_RESEARCH/CODE/carry_data_procurement/manifest.py`
- `06_RESEARCH/CODE/tests/test_carry_data_procurement.py`

下载/API 端点：

- Spot monthly klines: `https://data.binance.vision/data/spot/monthly/klines/{symbol}/1h/{symbol}-1h-YYYY-MM.zip`
- Perp contract klines: `https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h`
- Index price klines: `https://fapi.binance.com/fapi/v1/indexPriceKlines?symbol={symbol}&interval=1h`
- USDT depeg proxy: `https://api.binance.com/api/v3/klines?symbol=USDCUSDT&interval=1h`
- Leverage brackets: `https://fapi.binance.com/fapi/v1/leverageBracket?symbol={symbol}` with signed request
- ADL quantile: `https://fapi.binance.com/fapi/v1/adlQuantile?symbol={symbol}` with signed request

幂等性：

- parquet/json/text/yaml 均通过临时文件写入后 `replace()` 原子替换。
- 下载数据先 schema/range 校验，校验失败不写目标 parquet。
- parquet writer 缺 `pyarrow` 或 `fastparquet` 时失败关闭，不将 CSV 冒充 parquet。

## 数据质量检查

已实现但因下载阻塞未能应用到真实数据：

- schema：OHLCV 必须为 `timestamp, open, high, low, close, volume`；index 必须为 `timestamp, close`。
- 类型：timestamp 统一 UTC；价格/成交量转数值，无法转换计入空值率。
- 时间范围：2020-01-01 00:00:00Z 至 2024-12-31 23:00:00Z。
- 连续性：1H 频率完整性检查，报告 `missing_hours` / `extra_hours`。
- 空值率：默认 `max_null_rate=0.0`，任何价格/成交量空值均失败。

本轮实际产物质量：

- `08_DATA/carry/data_manifest.yaml` 存在，状态为 `blocked`，只记录已真实写入的 3 个说明文件及 SHA256。
- `08_DATA/carry/procurement_failures.log` 存在，记录每个官方端点失败原因。
- 未生成任何行情 parquet，因此行数、时间范围、空值率验收不能通过。

## 模型假设记录

ADL：

- 已写入 `08_DATA/carry/metadata/adl_note.md`。
- 历史假设：极端市场（日内波动 > 15%）期间，0.5% 持仓发生 ADL；最大减仓 50%。
- 前向门：shadow 期间接入 `/fapi/v1/adlQuantile` 实时监控。

提币暂停：

- 已写入 `08_DATA/carry/events/withdrawal_suspension_events.md` 占位。
- 质量判断：任务书允许抓取失败时占位；但正式 FEASIBILITY 报告必须把该历史事件表标为人工待补。

强平费率：

- 已写入 `08_DATA/carry/metadata/liquidation_fee_history.md`。
- 建模默认值：0.5%。
- 质量判断：默认值可作为保守建模占位，但官方公告历史变更审计未完成，不能作为最终历史费率证明。

杠杆档位：

- 未写入 `leverage_brackets_{symbol}.json`。
- 原因：当前 Binance endpoint 需要签名请求，环境缺 `BINANCE_API_KEY/BINANCE_API_SECRET`。
- 质量判断：v4 强平路径模型仍缺 mmr 档位输入。

## 对CARRY_KNOWLEDGE.md的更新建议

建议更新 `02_KNOWLEDGE_BASE/CARRY_KNOWLEDGE.md §三 当前阻塞状态`：

- 将阻塞2细分为三个外部前置条件：网络可达 Binance 官方域名、安装 parquet engine（`pyarrow` 或 `fastparquet`）、提供只读 Binance futures API key/secret 用于 signed endpoints。
- 将 `ADL official execution records` 改成：历史执行记录官方不可得；当前 `adlQuantile` 仅用于前向监控且需要签名。
- 将 `Historical leverage brackets` 改成：历史档位不可由公开 REST 完整恢复；当前档位需 signed endpoint，历史变更需公告人工/半自动审计。

## 验收结果

- [x] `08_DATA/carry/data_manifest.yaml` 存在，含已写入文件的路径、行数、SHA256；但状态为 `blocked`，不含未生成行情文件。
- [ ] Spot 1H open BTC+ETH 2020-2024 未下载。
- [ ] Perp 1H OHLC 未下载，不能与 spot 对齐。
- [ ] USDT 脱锚事件 parquet 未生成；只记录了失败原因。
- [x] ADL 假设已书面化在 `adl_note.md`。
- [x] 本报告含模型假设记录，逐项写明来源状态和假设值。
- [x] 本报告含建议下一步，并明确 FEASIBILITY-LOCK 现在不能运行。
- [x] 下载脚本有 pytest 验证测试：`python3 -m pytest 06_RESEARCH/CODE/tests/test_carry_data_procurement.py -q` 通过。

## 未解决问题

1. 当前 shell 网络被 `HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:7897` 接管，但沙箱对该端口连接失败；禁用代理后也无法解析/访问外网。
2. signed endpoints 缺 `BINANCE_API_KEY` 和 `BINANCE_API_SECRET`。
3. 本 Python 环境缺 parquet writer：`pyarrow=False`、`fastparquet=False`。网络修复后仍需安装其一，否则脚本会在写 parquet 阶段失败关闭。
4. Binance 公告历史搜索未完成；提币暂停历史和强平费率变更审计仍需网络或人工补充。
5. 本轮无法创建 git commit：沙箱对 `.git/index.lock` 写入返回 `Operation not permitted`，因此只保留工作区文件变更。

## 建议下一步

FEASIBILITY-LOCK 现在不能运行；仍缺 Spot/Perp/Index/USDT depeg parquet 与 leverage bracket JSON。

恢复条件：

1. 修复外网访问，或启动可用代理并确保 Codex shell 可连接 `127.0.0.1:7897`。
2. 安装 parquet engine：`pyarrow` 或 `fastparquet`。
3. 提供权限最小化的 Binance API key/secret，用于 futures signed read endpoints。
4. 重新运行：`python3 06_RESEARCH/CODE/procure_carry_data.py --output 08_DATA/carry --timeout 30`。
5. 若第 8 项公告抓取仍失败，保持占位文件并由人工补齐；不要因此阻塞其它 7 项。
