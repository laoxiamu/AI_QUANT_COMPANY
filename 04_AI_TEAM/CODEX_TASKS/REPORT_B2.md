# REPORT B2

**任务：** BATCH_20260612N / B2 P1-04/P1-06 第五件追溯复算
**状态：** COMPLETED
**结论：** P1-04 第五件失败；P1-06 第五件通过。昨日 P1-06 大额负超额是追溯口径差，不是 P1 冻结窗口结论。

## 七问自查

1. 机制：验证策略是否超过同状态门控被动买入持有基准，排除 beta 伪装。
2. 验收：可量化，输出策略终值、基准终值、超额、根因解释和报告。
3. 更便宜实现：有，独立小脚本复算；无需重跑其他批次或动 Holdout。
4. 禁止项：未改预登记，未读 HOLDOUT 内容，未用全样本分位，未引黑箱依赖，未提交 git。

## 结果

| experiment | strategy ending | benchmark ending | excess | pass |
|---|---:|---:|---:|---|
| P1-04 | 1413672.48 | 1694715.61 | -281043.13 | False |
| P1-06 | 954160.04 | 703090.24 | 251069.80 | True |

## 验收自检

- CODE：`06_RESEARCH/CODE/b2_fifth_criterion_verification.py` 可复跑；无随机过程。
- RESULTS：`06_RESEARCH/RESULTS/20260612_fifth_criterion_verification.md` 已写入。
- 执行报告：本文件。
- 数据边界：pre-Holdout `nrows`；未读 `*_2026H1`；未读 HOLDOUT 内容。
- git：遵守批次书“全程禁 git commit”，未提交。
