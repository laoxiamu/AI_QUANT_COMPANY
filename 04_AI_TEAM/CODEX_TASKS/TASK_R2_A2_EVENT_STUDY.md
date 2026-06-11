# TASK_R2_A2_EVENT_STUDY —— A-2 机制验证（事件研究）

**发包：** Claude 2026-06-11 ｜ **执行：** Codex（直调）｜ **口径权威：** 预登记 `06_RESEARCH/HYPOTHESES/a2_funding_extreme_reversal_v1.md`（含勘误）。本任务=投研OS第⑤步：**只验机制，不构建信号、不调参、不回测策略**。

## 输入

- 事件：`06_RESEARCH/CODE/output/a2_events_work.csv`（仅工作集；**严禁读取 06_RESEARCH/DATA/HOLDOUT/ 任何文件**）。
- 价格：`06_RESEARCH/DATA/FUTURES/{SYM}_MARK_1H.csv` 收盘价。

## 计算（全部按预登记，复述要点）

1. 每事件：t0=event_time 后首个可用 1H 收盘为基准，计算 t+24h/t+48h/t+72h 对数收益（数据末端不足72h的事件按可用窗口计，缺窗口记NA）。
2. **主检验（3次）**：neg/P5 池化，三窗口均值>0：t 检验 + 块 bootstrap（块=168个1H bar，N=5000，seed=20260611）。
3. **辅证（3次）**：pos/P95 池化，三窗口均值<0，同法。
4. **多重检验**：Bonferroni m=6，报告原始 p 与贴现后 p。
5. **非重叠复核**：同侧事件若 72h 窗口重叠，保留先发事件，重算主检验（描述性复核）。
6. **单调性（描述性）**：neg P5/P2.5/P1 与 pos P95/P97.5/P99 各窗口均值效应排布。
7. **状态分解（描述性）**：按 BTC 日线 SMA200（事件前一完整日收盘，无前视）分宏观牛/熊两格报告均值与计数。不作通过依据。
8. **结论判定**：严格按预登记"失效判断/通过标准"输出 PASSED（机制存在/探索级）或 FAILED，禁止模糊表述。

## 交付物

- `06_RESEARCH/CODE/a2_event_study.py`（自实现可审计小函数；t检验可用手写或scipy缺则stdlib正态近似，注明）
- `06_RESEARCH/CODE/output/a2_event_study_results.json`（全部数字）
- `06_RESEARCH/RESULTS/20260611_a2_event_study.md`（结论报告：表格化六检验+单调性+状态分解+判定+与预登记口径的逐条对照）
- `04_AI_TEAM/CODEX_TASKS/REPORT_R2_A2_EVENT_STUDY.md`（执行报告+验收自检）
- pytest：窗口收益计算无前视（t0 之前价格不参与）、重叠剔除规则、bootstrap 可复现（seed 固定两次运行同结果）

## 验收标准

pytest 全绿；seed=20260611 写死；六检验 p 值齐全（原始+贴现）；结论二值明确；未读 Holdout（代码中不得出现 HOLDOUT 路径字符串）；UTC。

## 禁止

调阈值/窗口/合并参数；增删过滤条件；读 Holdout；报 Sharpe 或任何策略指标；把"不显著"写成"接近显著"。
