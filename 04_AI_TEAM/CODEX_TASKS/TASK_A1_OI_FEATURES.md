# TASK_A1_OI_FEATURES —— A-1 清算级联 OI 特征层（只特征，不事件、不Holdout、不收益）

**发包：** Claude 2026-06-12 ｜ **执行：** Codex（直调）｜ **定位：** A-1 预登记前的可复用数据层。**事件提取/阈值/Holdout 切分一律禁止**——那些必须等 A-1 预登记冻结后另案（A-2 的教训：先冻口径再动手）。

## 交付物

1. `06_RESEARCH/CODE/features/a1_oi_features.py`：
   - 读 `06_RESEARCH/DATA/FUTURES/{SYM}_METRICS_5M.csv`（BTC/ETH/SOL），`sum_open_interest` 重采样到 1H（取每小时最后值）。
   - 计算 Δ6h、Δ24h 百分比变化；各自做**滚动 365 天、最少 180 天起算的无前视分位**（midrank 口径与 `features/a2_funding_features.py` 一致——直接 import 复用 `empirical_percentile`/滚动逻辑，不要复制粘贴）。
   - 输出 `06_RESEARCH/CODE/output/a1_oi_features_{SYM}.csv`：列 = ts(UTC), oi, d6h_pct, d24h_pct, d6h_rolling_pctl, d24h_rolling_pctl, warmup。
2. `06_RESEARCH/CODE/features/test_a1_oi_features.py`（pytest）：①无前视（构造序列验证 t 分位不含 ≥t 数据）②重采样正确性（5M→1H 取最后值，含缺口小时为 NaN 不前向填充）。
3. 报告 `04_AI_TEAM/CODEX_TASKS/REPORT_A1_OI_FEATURES.md`：各品种覆盖区间（注意 ETH/SOL METRICS 始于 2021-12）、warmup 排除量、1H 缺口统计、复算命令、验收自检。

## 验收标准
pytest 全绿且无前视测试非恒真；UTC；输出行数≈各品种 1H 网格；不读 MARK/FUNDING 之外多余数据（funding 不需要）；无任何事件/阈值/Holdout 代码路径。

## 禁止
事件提取、阈值选择、Holdout、读 HOLDOUT 目录、收益计算、git commit（Claude 验收后统一提交）、改 a2 既有模块。
