# CARRY-FEASIBILITY-RUN：carry 历史可行性复核执行（v4 已 APPROVED）

**授权：** CARRY_RISK_REVIEW_v4 = APPROVED（放行历史 FEASIBILITY-LOCK）。**唯一规格：** `06_RESEARCH/PREREGISTRATIONS/CARRY_DELTA_NEUTRAL_PREREG_v4.md`（严格按冻结口径，禁改/禁优化/禁加过滤）。
**定性（铁律）：** 历史**可行性复核**，**不耗独立计数、不授权核心资本上线**；结论=历史口径下 carry 是否可行（PASS-FEASIBILITY / FAILED）。前向 shadow 才是真确认。
**复用：** carry 回测脚手架 `06_RESEARCH/CODE/carry/`（25 单测已过）。

## 铁律
- **禁读 HOLDOUT**：事件后/收益计算只在 work 集；sealed 加密保留不参与。
- 全参数取 v4 冻结值，seed 一致；禁事后调。结论措辞守纪律：不显著写"未验证"，负 funding/事件期亏损不剔除。

## 两阶段（custodian/executor 分离，v4 §7=A-1 v5 §12 口径）
### 阶段1 CUSTODIAN
1. 按 v4 §2 冻结口径，从 `*_FUNDING_8H.csv`+现货/mark(cutoff<2024-12-10) 生成 BTC/ETH carry 数据集与 interval 序列。
2. deterministic 切分 work/sealed（每第5个 interval 或 v4 指定口径预留）；sealed 用 **AES-256-GCM** 加密为 `06_RESEARCH/DATA/CARRY_WORK/sealed.enc`，**密钥写 `~/.aiquant_sealed/carry/carry_key.bin`（项目外）**；work 明文写 `06_RESEARCH/DATA/CARRY_WORK/`；写 `CARRY_HOLDOUT_MANIFEST.json`（行数/schema/git hash/SHA-256/解封条件）。
3. 负向权限测试留痕 `CARRY_HOLDOUT_PERMTEST.log`（读 manifest 成功 + 无密钥解密失败）。

### 阶段2 EXECUTOR（只读 work）
按 v4 §5 算并逐项给 PASS/FAIL：净E[R](年化,多变量同步块bootstrap+seed)、赢亏比≥1.5、正年比例、年化log growth、现金零基准、**分档爆仓概率(2000路径逐1H短腿保证金账本)**、MDD≤15%、WF≥2段正、A-1×Carry触发器非劣+尾部硬门。**有/无触发器两版对比**。

## 报告 `06_RESEARCH/RESULTS/20260615_carry_feasibility.md`：顶行 PASS-FEASIBILITY/FAILED；§5 decision table 逐项数值；末"对CTO提示:历史可行性是否支持进入前向shadow"。
## 完成写 `04_AI_TEAM/TASK_INBOX/CARRY_FEASIBILITY_DONE.json`(task_id=CARRY_FEASIBILITY,verdict,output_file,notes=净E[R]+爆仓概率+一句判断)。可commit(不commit密钥/sealed明文)。
