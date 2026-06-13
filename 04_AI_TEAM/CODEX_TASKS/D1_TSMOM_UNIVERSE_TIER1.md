# D1：TSMOM Universe Tier 1 数据下载

**任务类型：** 数据采集（网络密集型）  
**预计时长：** 30-90 分钟（约 25-30 个资产 × 多个月度 ZIP）  
**输出目录：** `06_RESEARCH/DATA/FUTURES_EXPANDED/`

---

## 背景

C1 探针确认 83 个候选数据可得，DEC-070 决策扩充 TSMOM universe 至 Tier 1 主流资产（DEC-070：流动性过滤 + 操盘风险排除）。本任务下载 Tier 1 资产的完整 4H 历史数据。

---

## 第一步：从 C1 候选中确定 Tier 1 列表

读取 `06_RESEARCH/DATA/c1_candidates.csv`，按以下规则筛选：

**保留条件：**
- `head_first_ok == True AND head_recent_ok == True`
- `est_bars >= 7000`
- symbol 不在黑名单中

**黑名单（操盘风险高 / 低流动性 / 指数合约）：**
```python
BLACKLIST = {
    "REEFUSDT", "OGNUSDT", "COTIUSDT", "BLZUSDT", "SFPUSDT",
    "STMXUSDT", "LINAUSDT", "NKNUSDT", "DENTUSDT", "BTCDOMUSDT",
    "IOTAUSDT", "IOSTUSDT", "QTUMUSDT", "ONTUSDT", "BATUSDT",
    "VETUSDT", "NEOUSDT", "ZILUSDT", "RSRUSDT", "BELUSDT",
    "CHRUSDT", "ALICEUSDT", "ONEUSDT", "HOTUSDT", "MTLUSDT",
    "BAKEUSDT", "ANKRUSDT", "RLCUSDT", "BANDUSDT", "ALPHAUSDT",
    "KAVAUSDT", "FLMUSDT", "ZENUSDT", "TRBUSDT", "SKLUSDT",
    "DEFIUSDT", "BALUSDT", "STORJUSDT", "UNFIUSDT", "XEMUSDT",
    "GTCUSDT", "HBARUSDT", "CELRUSDT"
}
```

**取 Tier 1（过滤后按 est_bars 降序，最多 35 个）：**
期望结果约：LINKUSDT, DOTUSDT, UNIUSDT, AVAXUSDT, ATOMUSDT, NEARUSDT, AAVEUSDT, FILUSDT, COMPUSDT, MKRUSDT, SUSHIUSDT, CRVUSDT, SANDUSDT, MANAUSDT, 1INCHUSDT, AXSUSDT, RUNEUSDT, SNXUSDT, EGLDUSDT, GRTUSDT, 1000SHIBUSDT, TRXUSDT, ETCUSDT, XLMUSDT, XMRUSDT, DASHUSDT, ZECUSDT, XTZUSDT, THETAUSDT, KSMUSDT 等

---

## 第二步：下载 4H 月度 ZIP

对每个 Tier 1 资产：

```python
BASE_URL = "https://data.binance.vision/data/futures/um/monthly/klines"
INTERVAL = "4h"
CUTOFF = pd.Timestamp("2024-12-09 23:59:59", tz="UTC")
OUT_DIR = "06_RESEARCH/DATA/FUTURES_EXPANDED"
```

下载逻辑（与 C1/C2 相同方法）：
1. 从 onboard_date 月份开始，到 2024-12 结束
2. 逐月下载 ZIP，解压 CSV，过滤列（datetime, open, high, low, close, volume）
3. 跳过 header 行（to_numeric + dropna）
4. 合并成单个 CSV，存入 `{OUT_DIR}/{SYM}_4H.csv`
5. 每个资产完成后打印：`{SYM}: {n_rows} rows, {date_start} ~ {date_end}`

**并发控制：** 建议顺序下载（不并发），避免触发 rate limit；每个 ZIP 之间 sleep(0.1)

---

## 第三步：生成下载清单

完成所有下载后，生成 `06_RESEARCH/DATA/FUTURES_EXPANDED/DOWNLOAD_MANIFEST.json`：

```json
{
  "generated": "2026-06-13T...",
  "tier1_assets": [...],
  "downloads": {
    "LINKUSDT": {"rows": 8500, "start": "2020-01-17", "end": "2024-12-09", "ok": true},
    ...
  },
  "failed": [...],
  "summary": {"total": 30, "success": 28, "failed": 2}
}
```

---

## 验收条件

- `DOWNLOAD_MANIFEST.json` 存在
- 成功资产数 ≥ 20
- 每个成功资产 rows ≥ 5000
- 不读取 HOLDOUT 目录
- 不修改 `06_RESEARCH/DATA/FUTURES/` 下的文件（现有 8 币数据）
