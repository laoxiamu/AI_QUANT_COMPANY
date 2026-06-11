# TASK_R1_A2_FEATURES —— A-2 特征库与事件表（R1 数据层 + R2 前置）

**发包：** Claude（主理人/CTO）2026-06-11 ｜ **执行：** Codex（直调通道）｜ **规格依据：** 预登记 `06_RESEARCH/HYPOTHESES/a2_funding_extreme_reversal_v1.md`（口径以它为准，本文不复述处见该文件）+ AGENTS.md（项目根，铁律）

## 目标

把预登记的事件定义实现为可复算代码 + 产出事件表，并完成 Holdout 事件级封存。**不做任何收益/价格反应分析**（那是 R2 下一任务）——本任务只产出"事件何时发生"。

## 交付物

1. `06_RESEARCH/CODE/features/a2_funding_features.py`：
   - 读 `06_RESEARCH/DATA/FUTURES/{SYM}_FUNDING_8H.csv`（BTC/ETH/SOL）。
   - 计算每个 funding 读数相对**此前 365 天窗口**的滚动分位（首年扩张窗口，样本 <180 天的读数标记 warmup 不参与事件判定）。**严禁前视**：t 时刻分位只用 < t 的数据。
   - 事件提取：负侧 P5/P2.5/P1、正侧 P95/P97.5/P99 六档；同方向间隔 <24h 合并（事件时间=首次触发）；跨品种池化输出。
2. `06_RESEARCH/CODE/output/a2_events_work.csv`（工作集 80%）与 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv`（每第 5 个事件，序号 mod 5==4，按全池化时间排序）。列：event_time(UTC), symbol, side(neg/pos), tier(P5/P2.5/P1/...), funding_value, rolling_pctl。**Holdout 文件写完即不得再读。**
3. `06_RESEARCH/CODE/features/test_a2_features.py`（pytest）：①无前视测试（人工构造序列验证 t 分位不含 ≥t 数据）；②合并规则测试（23h/25h 间隔用例）；③Holdout 切分确定性测试（mod 规则）。
4. 报告 `04_AI_TEAM/CODEX_TASKS/REPORT_R1_A2_FEATURES.md`：各档事件计数（与普查 `06_RESEARCH/RESULTS/20260611_event_census.md` 的全样本分位计数对比并解释差异方向——滚动分位应使计数下降）、warmup 排除量、测试结果、复算命令。

## 验收标准（Claude 按此验收）

- pytest 全绿；无前视测试真实有效（不是恒真断言）。
- 负侧 P5 池化事件数在 150~350 区间（普查锚 324，滚动分位应偏低；显著出界须解释）。
- 工作集+Holdout 计数比 ≈ 4:1；Holdout 文件存在且 git 提交。
- 全 UTC；seed 不适用（无随机）；git commit message 带 R1_A2。

## 禁止

读 MARK 价格文件（防顺手做收益分析）；改预登记任何口径；引第三方 TA/事件库（自实现小函数，DEC-061）；碰既有 CODE/ 下其他实验文件。
