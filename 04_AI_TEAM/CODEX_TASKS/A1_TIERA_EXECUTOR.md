# A1-TIERA-EXECUTOR：A-1 Tier A 执行器（只读 work，出关联判决）

**前置已完成（主会话 custodian）：** `06_RESEARCH/DATA/A1_WORK/work_episodes.csv`(156条) + `sealed_holdout.enc`(38条,AES-256-GCM) + `A1_HOLDOUT_MANIFEST.json` 已生成；密钥在 `~/.aiquant_sealed/a1/a1_key.bin`（**你无权读、也不要尝试读/解密**）。池化194=work156+sealed38。
**你的身份：** 独立 executor principal，与 custodian 分离。**只读 `work_episodes.csv`**。
**唯一规格：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v5.md`。代码已就绪：`06_RESEARCH/CODE/a1_tiera_executor.py`（+ a1_tiera_core.py）。
**计数定性：** 机制前关联快筛，不耗独立计数，结论只到关联层，**禁写"机制"二字**。

## 任务
0. **先运行负向权限测试** `python3 a1_tiera_permtest.py`（在 `06_RESEARCH/CODE/`）。主会话已把密钥 `~/.aiquant_sealed/a1/a1_key.bin` 临时改为 `chmod 000`（执行身份打不开），故本测试应得 `overall=PASS`（manifest 可读 + 密钥不可访问→未尝试解密），生成 `06_RESEARCH/DATA/A1_WORK/A1_HOLDOUT_PERMTEST.log`。若得 `overall=FAIL`（密钥可被打开），**停下报告，不要继续**（边界未生效）。
1. **再运行** `python3 a1_tiera_executor.py`（在 `06_RESEARCH/CODE/`）。它只加载 work_episodes.csv，按 v5 算：48h 主 CAR（circular moving-block bootstrap，W=144h，半开网格，B=10000，seed=20260615，零假设重心化）、24h 次、单调性（配对 bootstrap Spearman H0:ρ=0）、A-2 非重叠关联硬门、Holm family m=4、WF 三段裸均值、成本诊断。
2. **铁律自检（代码层）：** 断言执行期间从不打开 sealed_holdout.enc、不读 ~/.aiquant_sealed、不读任何 HOLDOUT 路径。若 a1_tiera_executor.py 有任何触碰 sealed/key 的路径，停下报告，不要绕过。
3. **产出报告** `06_RESEARCH/RESULTS/20260615_a1_tierA_screen.md`：顶部一行 **Tier A PASS（可观测条件回弹关联成立，探索级）/ FAILED**；§11 decision table 逐项 PASS/FAIL/N.A. + 数值（各项均值/Holm 后 p/CI/n_eff）；work/sealed 行数 + manifest SHA 引用；**末尾一句"对 CTO 的提示：本结果支持/不支持继续投路径B 确证机制"**。
4. 若代码运行报错或数据 N.A.，如实报告，不臆造、不补 cutoff 后数据、不改预登记。

## 完成
写 `04_AI_TEAM/TASK_INBOX/A1_TIERA_EXEC_DONE.json`(task_id=A1_TIERA_EXEC,status,verdict=PASS/FAILED,output_file,notes=48h均值+Holm后p+一句判断)。可 commit 代码与报告（Claude 复核；不要 commit ~/.aiquant_sealed 或密钥）。
