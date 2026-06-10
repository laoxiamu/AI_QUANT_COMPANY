# REPORT 0B5 — v4 Bootstrap 稳健性验证

**任务：** `TASK_0B5_V4_BOOTSTRAP_VALIDATION.md`  
**完成时间：** 2026-06-06  
**状态：** COMPLETED  
**Holdout：** 未访问

## 执行摘要

已完成固定种子、N=10,000 的零中心 moving-block bootstrap。

任务原始“重排未来收益后计算均值”方法无效，因为重排不会改变均值，会生成
退化分布或伪 p 值。实现改为统一 4H 日历上的同步 circular block bootstrap：
先按品种零中心，再以 20 根 4H K线为块同步重采样三品种，保留时间依赖和
块内跨品种相关性。普通非零中心版本仅用于 95% bootstrap CI。

## 核心结果

| 窗口 | 观察均值 | Bootstrap p | 95% CI | 结论 |
|------|---------:|------------:|-------:|------|
| t+6 | +0.770% | 0.005799 | [+0.158%, +1.359%] | 通过 |
| t+12 | +1.364% | 0.002000 | [+0.387%, +2.284%] | 通过 |
| t+24 | +2.337% | 0.000300 | [+0.933%, +3.656%] | 通过 |

三窗口均通过单侧 5% 门槛。同步日历块结果比各品种独立事件块对照更保守，
但结论一致。

## 验收核对

| 验收项 | 状态 |
|--------|:----:|
| 有效 Block Bootstrap | 通过 |
| 每个品种先独立零中心 | 通过 |
| 统一时间块保留跨品种同期依赖 | 通过，严于原独立打乱要求 |
| N=10,000 | 通过 |
| 固定随机种子 | 通过，`20260606` |
| 三种方法对比表 | 通过 |
| Null 均值、标准差、百分位、95% CI | 通过 |
| 直方图与观察值位置 | 通过 |
| 明确结论 | 通过 |
| Holdout 未读取 | 通过 |

## 输出文件

- `06_RESEARCH/CODE/v4_bootstrap_validation.py`
- `06_RESEARCH/CODE/output/v4_bootstrap_validation.json`
- `06_RESEARCH/RESULTS/20260606_v4_bootstrap_null_distributions.png`
- `06_RESEARCH/RESULTS/20260606_v4_bootstrap_validation.md`
- `04_AI_TEAM/CODEX_TASKS/REPORT_0B5_V4_BOOTSTRAP.md`

## Claude 待处理事项

1. Bootstrap p 值：
   - t+6：`0.005799`
   - t+12：`0.002000`
   - t+24：`0.000300`
2. 三层校验一致性：普通 t 检验、非重叠子集 t 检验、同步日历 block
   bootstrap 三个窗口均支持正均值，方向一致。
3. DECISION_LOG 建议：可升级为“v4 样本内统计信号三层稳健性校验通过”，
   但必须同时保留“时期稳定性未完全通过、非策略有效、非 Holdout 确认”的限制。
4. CURRENT_STATE 更新草稿：
   - `v5_sweep_regime_bull_v4`：Bootstrap 稳健性校验完成。
   - N=10,000，20 根 4H K线同步 block，固定种子 20260606。
   - p(t+6/t+12/t+24)=0.005799/0.002000/0.000300。
   - 三层样本内统计校验通过；2022 与 WF 第二段稳定性缺口仍存在。
   - Holdout 未读取。

【需要Claude】
