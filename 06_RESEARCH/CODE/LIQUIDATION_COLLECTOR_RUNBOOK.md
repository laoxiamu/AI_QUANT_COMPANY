# 强平采集器运行手册（2026-06-10）
**脚本：** `06_RESEARCH/CODE/liquidation_collector.py` ｜ **数据：** `06_RESEARCH/DATA/LIQUIDATIONS/liq_YYYYMMDD.jsonl`
**依赖安装（Mac）：** `pip3 install websocket-client --break-system-packages`
**启动（Mac 前台测试）：** `python3 liquidation_collector.py`（看到 heartbeat 行即正常）
**启动（Mac 常驻）：** `cd 06_RESEARCH/CODE && nohup python3 liquidation_collector.py >> collector.log 2>&1 &`
**健康检查：** 每周看 `DATA/LIQUIDATIONS/` 最新文件行数>0；collector.log 每小时一条 heartbeat。
**注意：** Mac 休眠会断流（数据缺口可接受，按"尽力采集"定位）；长期方案=腾讯云VM（Phase 2 评估）。时间戳统一 UTC。
**待办（Claude）：** 周监控任务加"昨日行数>0"检查；评估顺手加收 Bybit/OKX 强平流。
