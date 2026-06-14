# A1-RR5：A-1 预登记 v5（路径A 关联快筛）第五轮独立盲审

**角色：** 独立 Risk Reviewer，按**"机制前关联快筛"标尺**审查（不要求达机制确证实验的全部严格度；只判关联结论是否无偏、可复现、可审计）。不知实验结果，只审设计。
**审查对象：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v5.md`
**对照：** `A1_RISK_REVIEW_v4.md` 第四轮"四项最小必改"（RR4 已确认 v4 闭 2/5：功效治理+family；本轮只审剩余四项是否闭合）。
**输出：** `06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v5.md`

## 任务：逐条裁决 RR4 四项最小必改是否闭合（CLOSED/PARTIAL/NOT_CLOSED+证据§/行+仍缺）

1. **§7 改名**：v5 是否把"机制独立性硬门"改为"A-2 非重叠关联硬门"并去除机制识别含义（§7 L120 + §11）？是否还有残留把 non-overlap 显著解读为"独立机制"？
2. **circular bootstrap + Spearman（RR4 #2 核心）**：
   - §4 是否改为半开 UTC 网格 `[t_1, t_n+1h)`、周长 `span=(t_n-t_1)+1h`（端点不重复）？
   - 回绕块截断是否改为按 circular offset `((event_time-u) mod span)` 排序（而非绝对 event_time）？
   - §5 Spearman 是否改为对 `(severity, CAR)` 配对序列做同口径 moving-block bootstrap、以 `ρ*-ρ_obs` 居中构造 `H0:ρ=0`（不再是"标签置换"）？该居中法是否确实检验 ρ=0？
3. **§11 WF（RR4 #3）**：段长/余数分配是否唯一（余数给第一段、其次第二段）？切点 c=相邻 episode event_time 中点是否唯一？purge 谓词是否按实际读取足迹 `[event_time-72h, align+48h]`（含 align lag）？purge 后是否明文不重新分段？是否还有不唯一处？
4. **§12 Holdout（RR4 #4）**：是否冻结 AES-256-GCM + 格式（nonce‖密文‖tag）+ 认证失败判据？密钥是否明确存于执行身份不可访问的独立 principal/ACL、绝不落入 Codex 可读文件/env/命令行/日志？负向测试是否记命令+退出码+失败证据？这是否构成真读权限边界？

## 第二部分：v5 修订是否引入任何新缺陷或新自由度（circular offset 截断、配对 bootstrap 居中、WF 中点切点、GCM 格式）。

## 结论：**APPROVED（可放行 Tier A 历史关联快筛）** / NOT APPROVED（列**最小**第五轮必改）。
- 按关联快筛标尺：若四项均 CLOSED 且无新阻塞，应 APPROVED。请勿无限加码或要求机制确证级严格度。
- 若 APPROVED，明确放行边界：仅关联结论、不耗独立计数、不晋级策略、须先过 §12 加密 Holdout 封存+负向权限测试。

## 铁律：禁读 HOLDOUT/`01_MEMORY_CORE/`/禁改预登记/禁提前跑事件研究。允许读 v5/v4review/增补件/Protocol/A-2公开假设。完成写 `04_AI_TEAM/TASK_INBOX/A1_RR5_DONE.json`(task_id=A1_RR5,status,output_file,review_conclusion,conditions_closed=x/4,notes)。
