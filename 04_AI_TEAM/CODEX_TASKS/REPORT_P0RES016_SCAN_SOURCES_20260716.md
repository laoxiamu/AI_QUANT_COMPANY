# REPORT P0-RES-016：投研扫描源拓宽

任务：`P0-RES-016`  
执行时间锚：2026-07-16，实测样例截至 `2026-07-16 06:14 UTC`（Asia/Singapore 14:14）  
状态：completed

## 结论

已将 `06_RESEARCH/CODE/thesis_hf_scan.py` 从单一 funding/OI 源扩展为四源合并候选扫描器：

- `funding_oi_squeeze`：保留原 funding/OI/24h price 异动逻辑。
- `binance_announcement`：Binance 公告流，覆盖新上永续、期货退市、KORU 类合约尺寸调整、一般 removal notice。
- `token_unlock_cryptorank`：CryptoRank 公开 token unlock 页面解析 upcoming unlock。
- `depeg_coingecko`：CoinGecko simple price 监控主要稳定币/锚定资产偏离锚。

扫描器仍然只输出候选清单，不登记 thesis，不读取 Holdout，不做量化实验，不改闸口判据或模板。

## 代码改动

- `06_RESEARCH/CODE/thesis_hf_scan.py`
  - 新增独立小函数：`scan_binance_announcements()`、`scan_token_unlocks()`、`scan_depeg_assets()`。
  - 将旧逻辑迁入 `scan_funding_oi()`，并新增 `build_legacy_funding_output()` 保存旧输出形态。
  - 新增源开关：`--sources funding_oi,binance_announcements,token_unlocks,depeg` 与 `--skip-sources`。
  - 新增通道B开关：`--fetch-via-ssh-sg`，默认仍是 Mac 直连并 unset proxy env。
  - 输出 JSON 顶层新增 `schema_version`、`sources_requested`、`legacy_funding_oi`、`source_errors`、合并 `candidates`。
  - 控制台输出改为候选表格。

- `06_RESEARCH/CODE/tests/test_thesis_hf_scan.py`
  - 覆盖旧 funding/OI 回归、Binance 公告分类、CryptoRank unlock 解析、CoinGecko depeg、SSH curl timeout、公告符号抽取。

## 回归对照

对照方式：从 `git show HEAD:06_RESEARCH/CODE/thesis_hf_scan.py` 读取改动前脚本到内存，用同一组固定假数据跑旧 `main()`，再用新 `scan_funding_oi()` + `build_legacy_funding_output()` 生成 legacy 输出。

结果：

```text
old_equals_new True
old_output {"candidates": [{"chg24h_pct": 4.0, "funding_8h": 0.004, "oi_24h_ago_usdt": 100.0, "oi_24h_ratio": 2.0, "oi_now_usdt": 200.0, "quote_vol_usdt": 1000000.0, "symbol": "AAAUSDT"}, {"chg24h_pct": -30.0, "funding_8h": 0.001, "oi_24h_ago_usdt": 50.0, "oi_24h_ratio": 0.5, "oi_now_usdt": 25.0, "quote_vol_usdt": 6000000.0, "symbol": "BBBUSDT"}], "n_prescreen": 2, "scan_utc": "20260716_0611"}
new_output {"candidates": [{"chg24h_pct": 4.0, "funding_8h": 0.004, "oi_24h_ago_usdt": 100.0, "oi_24h_ratio": 2.0, "oi_now_usdt": 200.0, "quote_vol_usdt": 1000000.0, "symbol": "AAAUSDT"}, {"chg24h_pct": -30.0, "funding_8h": 0.001, "oi_24h_ago_usdt": 50.0, "oi_24h_ratio": 0.5, "oi_now_usdt": 25.0, "quote_vol_usdt": 6000000.0, "symbol": "BBBUSDT"}], "n_prescreen": 2, "scan_utc": "20260716_0611"}
```

结论：同输入下，旧 funding/OI 产出与新 `legacy_funding_oi` 完全一致。

## 网络预检与通道

Mac 直连预检：

- `www.binance.com`、`public-api.dropstab.com`、`api.coingecko.com`、`fapi.binance.com` 均在本机直连出现 `LibreSSL SSL_connect: SSL_ERROR_SYSCALL`，未拿到 HTTP 状态。

通道B预检：

- Binance CMS catalog 48：HTTP/2 200。
- Binance CMS catalog 161：HTTP/2 200。
- CryptoRank `/token-unlock`：HTTP/2 200。
- CoinGecko simple price API：HTTP/2 200。
- DropsTab public API：HTTP/2 401，返回 `API key is not provided`，未使用为核心数据源。
- DropsTab `/vesting` 页面：HTTP/1.1 200，但页面结构不如 CryptoRank `__NEXT_DATA__` 稳定，本版优先 CryptoRank。

## 实测样例

命令：

```bash
python3 06_RESEARCH/CODE/thesis_hf_scan.py --fetch-via-ssh-sg --table-limit 15
```

输出文件：

```text
06_RESEARCH/CODE/output/thesis_hf_scan_20260716_0614.json
```

总体统计：

```text
scan_utc 20260716_0614
sources_requested ['funding_oi', 'binance_announcements', 'token_unlocks', 'depeg']
source_errors []
n_prescreen 7
candidate_count 88
by_source {'depeg_coingecko': 1, 'binance_announcement': 77, 'token_unlock_cryptorank': 3, 'funding_oi_squeeze': 7}
by_event {'peg_deviation': 1, 'new_perp_listing': 26, 'futures_contract_size_adjustment': 3, 'binance_removal_notice': 44, 'futures_delist': 4, 'upcoming_unlock': 3, 'funding_oi_price_anomaly': 7}
```

样例：

- Depeg：`MIM`，CoinGecko price `0.137416`，偏离锚 `-86.2584%`，last_updated_at `2026-07-16T06:16:17+00:00`。
- Unlock：`BOX`，2026-07-16 解锁，约 `$563,639.66`，约 `3.8258%` market cap。
- Unlock：`DRIFT`，2026-07-16 解锁，约 `$182,718.17`，约 `2.2083%` market cap。
- Unlock：`ARB`，2026-07-16 解锁，约 `$8,100,950.13`，约 `1.4558%` market cap。
- Funding/OI：`SKLUSDT` funding `-0.4156%`，24h change `11.752%`，OI ratio `1.298`。
- Funding/OI：`AKEUSDT` 24h change `99.9%`，OI ratio `3.729`。
- Binance announcement：`SKHYUSDT` new perp listing，event date `2026-07-10`。
- Binance announcement：`KORUUSDT` futures contract size adjustment，event date `2026-07-15`。
- Binance announcement：`IPUSDT,IPUSDC` futures delist，event date `2026-06-28`。

## 已知限制

- Binance 标题为 `Multiple ... Contracts` 的公告，标题本身不暴露全部 symbol；本版保留空 `symbols` + article detail API URL 留痕，不伪造 symbol。
- CryptoRank unlock 使用公开页面 `__NEXT_DATA__` fallbackData，不是官方承诺稳定 API；页面结构变化时会进入 `source_errors`。
- DropsTab public API 当前要求 API key，按免费源纪律未接入；DropsTab HTML 可达但未作为主解析源。
- CoinGecko depeg 监控是固定资产清单，不是全网自动发现所有锚定资产。
- 通道B为逐请求 SSH + curl，完整全源扫描约 2 分钟；默认仍是 Mac 直连。

## 验证

```text
pytest 06_RESEARCH/CODE/tests/test_thesis_hf_scan.py
6 passed in 0.06s
```

```text
python3 -m py_compile 06_RESEARCH/CODE/thesis_hf_scan.py
exit 0
```

```text
python3 06_RESEARCH/CODE/thesis_hf_scan.py --sources depeg --skip-sources depeg --table-limit 5 --output-dir /tmp
exit 0
```

## 护栏自检

- 未读取 Holdout。
- 未做量化实验。
- 未新增付费源或 API key 依赖。
- 未引入黑箱依赖；仅使用 Python 标准库。
- 未自动登记 thesis。
- 未修改 thesis 判据、模板或预登记文档。
- 失败/不稳定源已写入限制，不把抓不到的数据伪造成候选。
