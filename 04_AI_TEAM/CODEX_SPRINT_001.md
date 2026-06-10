# Codex Sprint 001
# 标题：诊断全套 + 数据基础设施

**创建时间：** 2026-06-06  
**创建人：** Claude（CTO）  
**状态：** READY — 等待 Founder 触发  
**背景：** 失败计数 6/8，使用剩余2次策略机会前，先跑完所有诊断获取数据依据

---

## Sprint 目标

在消耗任何策略测试机会之前，通过4个诊断任务回答以下问题：
1. 止损应该放在哪里？（MAE分析）
2. 信号的Sharpe天花板是多少？（无止损回测）
3. 波动率压缩过滤有没有用？（分组分析）
4. ATR止损能把止损率降到多少？（模拟分析）

---

## 任务队列（按顺序执行，每个任务独立，无需等待Claude分析）

### 第一批：诊断分析（可独立顺序执行）

| 顺序 | 任务文件 | 预计耗时 | 优先级 |
|-----|---------|---------|--------|
| 1 | TASK_0B12_MAE_ANALYSIS.md | 10-15分钟 | 🔴 最高 |
| 2 | TASK_0B13_T24_NO_STOP.md | 10-15分钟 | 🔴 最高 |
| 3 | TASK_0B14_VOL_COMPRESSION.md | 10-15分钟 | 🟡 高 |
| 4 | TASK_0B15_ATR_STOP_DIAGNOSTIC.md | 10-15分钟 | 🟡 高 |

### 第二批：基础设施（可与第一批并行或在第一批完成后执行）

| 顺序 | 任务文件 | 预计耗时 | 说明 |
|-----|---------|---------|------|
| 5 | TASK_INF01_1H_DATA.md | 20-30分钟 | 下载1H数据，耗时但无风险 |
| 6 | TASK_INF02_RESULTS_DASHBOARD.md | 10分钟 | 生成结果看板，最后做 |

---

## 执行规则

1. **每个任务独立执行**，不需要 Claude 在任务之间介入
2. **全部任务均为诊断或基础设施**，不消耗失败计数
3. **禁止查看 Holdout**（所有任务都明确标注了这一点）
4. 每个任务完成后，报告写入对应的 `REPORT_xxxx.md` 文件
5. **全部完成后通知 Claude**：Claude 会一次性分析所有报告，然后再决定下一次策略测试用什么方案

---

## Sprint 完成标志

以下文件全部存在：
- [ ] REPORT_0B12_MAE_ANALYSIS.md
- [ ] REPORT_0B13_T24_NO_STOP.md
- [ ] REPORT_0B14_VOL_COMPRESSION.md
- [ ] REPORT_0B15_ATR_STOP_DIAGNOSTIC.md
- [ ] REPORT_INF01_1H_DATA.md
- [ ] REPORT_INF02_DASHBOARD.md

---

## Sprint 完成后 Claude 要做什么

Claude 读取全部6份报告，综合分析后：
1. 确定最优止损结构（基于MAE分析 + ATR诊断）
2. 确定2次策略测试的具体方案（最高成功概率的配置）
3. 更新 RESEARCH_SNAPSHOT_0B.md 和 CURRENT_STATE.md
4. 向 Founder 提交决策请求（需要拍板哪个配置）

---

*本 Sprint 不需要 Founder 在执行期间做任何决策。执行完成后 Claude 会汇报。*
