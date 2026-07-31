# forced-flow 阶段A 功效反推脚本（2026-07-31 一次性核算）

结论见 `06_RESEARCH/RESULTS/20260731_forced_flow_stageA_power_precheck.md`。

| 脚本 | 作用 |
|---|---|
| `scan_liq.py` | 流式扫 43 个 liq_*.jsonl（147万条），聚合 (symbol,5min) 与 (symbol,4H) 强平 notional，落 pickle |
| `mde.py` | 算重叠窗、next-4H 收益 σ、各簇阈值下的 MDE 与所需天数反推 |
| `burst.py` | 测簇内时间集中度（机制寿命）→ 证实 4H 仪器与 25min 机制的分辨率失配 |

跑法：`python3 scan_liq.py && python3 mde.py && python3 burst.py`（路径写死为项目 DATA 目录）。

**注意**：本核算不看任何收益方向、不碰 Holdout、不构成预登记（反 A-1 单一方向冻结纪律仍在 B1 执行）。
