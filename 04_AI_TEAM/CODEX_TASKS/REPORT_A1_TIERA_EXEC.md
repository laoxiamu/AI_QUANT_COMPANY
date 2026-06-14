# REPORT_A1_TIERA_EXEC

**状态：** completed  
**判决：** FAILED  
**完成时间：** 2026-06-14T09:09:10Z

## 执行摘要

按唯一规格 `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v5.md` 完成独立 executor 执行。负向权限测试退出码为 0，正式 executor 退出码为 0；固定参数为 `B=10000`、`seed=20260615`、`W=144h`、Holm family `m=4`。

最终判决为 **FAILED**。48h CAR 点估计为 `1.3225%`，raw p=`0.115988`，Holm 后 p=`0.315568`，basic 95% CI=`[-0.9528%, 3.2674%]`，未通过主硬门。

## §11 验收逐项

| 项目 | 状态 | 数值 |
|---|---:|---|
| 48h CAR | FAIL | mean=1.3225%；Holm p=0.315568；CI=[-0.9528%, 3.2674%]；n=152；n_eff=131.58 |
| 24h CAR | FAIL | mean=1.1425%；Holm p=0.172383；CI=[-0.1864%, 2.2579%]；n=154；n_eff=132.97 |
| severity Spearman | FAIL | rho=0.082679；Holm p=0.315568；CI=[-0.073459, 0.239576]；n=152 |
| A-2 non-overlap 48h | FAIL | mean=1.4930%；Holm p=0.315568；CI=[-0.9932%, 3.5404%]；n=137；n_eff=120.16 |
| WF 稳定性 | PASS | 2/3 段为正；段均值=-0.9167%/2.5103%/2.4427% |
| 权限与口径完整性 | PASS | work=156；sealed=38；manifest/work SHA 一致；cutoff 前停止 |

## 边界自检

- PASS：正式 executor 无 `sealed_holdout.enc`、密钥、`~/.aiquant_sealed` 或解密访问路径。
- PASS：权限测试记录 manifest 可读，密钥打开失败，退出码 17，未尝试解密，`overall=PASS`。
- PASS：仅 work episodes 进入 CAR 计算；manifest 与权限日志仅作边界元数据校验。
- PASS：未读取封存样本，未补 cutoff 后行情，未改预登记、阈值、episode 或成本口径。
- PASS：报告中除任务书强制末句外，结论保持关联层。

## 产出

- `06_RESEARCH/RESULTS/20260615_a1_tierA_screen.md`
- `06_RESEARCH/CODE/output/a1_tiera_screen_results.json`
- `06_RESEARCH/DATA/A1_WORK/A1_HOLDOUT_PERMTEST.log`
- `04_AI_TEAM/TASK_INBOX/PROCESSED/A1_TIERA_EXEC_DONE.json`

完成事件先写入 `TASK_INBOX/A1_TIERA_EXEC_DONE.json`，随后由 Claude 调度器即时移入 `PROCESSED/`。无剩余执行步骤，等待 Claude 验收。
