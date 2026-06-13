# A1-RR3：A-1 预登记 v3 第三轮独立盲审

**角色：** 独立 Risk Reviewer（与 thesis owner 分离），不知实验结果，只审设计是否满足物理盲审放行。
**审查对象：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v3.md`
**对照：** `A1_RISK_REVIEW_v2.md` 第二轮结论（v2 仅闭合 2/10）+ 其"第二轮最小必改清单"5 项。
**输出：** `06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v3.md`

## 任务
判断 v3 是否**真正闭合** v2 review 的 5 项最小必改，逐条裁决 `CLOSED/PARTIAL/NOT_CLOSED`+证据(§/行)+仍缺。重点核查：

1. **命题+方向阈值**：v3 命题降到"OI 极端收缩+同窗负收益后条件 CAR"、DIR 改纯方向 `r6h<0`（删 -2%）、删除"已发生强平/已排除被动beta"。判断：命题是否仍有 overclaim？纯方向 `r6h<0` 是否消除了幅度自由度？是否还有残留因果归因？
2. **依赖稳健主推断**：v3 用 circular moving-block bootstrap（块=96h 时间窗、B=10000、seed、零假设重心化、单侧 p 定义、CI 定义）。判断：96h 块是否覆盖 72h 共享窗+缓冲？零假设重心化与 p 值算法是否完整可复现？非等距 episode 的时间宽度块定义是否自洽？
3. **功效前置可执行**：v3 把功效降为**报告型诊断**（仅事件前方差代理 sigma_pre + 冻结 ICC∈{0,0.2,0.5} 判读用0.5 + 设计效应只计一次），**撤销硬停机门与效应上限**。判断：是否彻底消除了"读事件后 CAR 才能算功效"的矛盾？降为诊断是否可接受（即放行不再依赖功效门）？
4. **A-2 同口径碰撞**：v3 overlap 改用 A-2 原冻结变量=**单个 8H funding 读数滚动 P95**（删 24h 均值、删 0.60、删 OR 句），non-overlap 检验纳入确认 family（Holm m=4）。判断：是否真用了 A-2 原口径？multiplicity 是否闭合？
5. **decision table/Protocol/物理封存**：v3 WF 统一裸均值并入 FAIL 清单；Tier A=gross 机制门(不冒称Protocol第五件)/Tier B=net 第五件；Holdout sealed 文件写到 **Codex workspace-write 沙箱根之外**(`~/.aiquant_sealed/`，执行身份无读权限)。判断：decision table 是否唯一二元无冲突？Tier 分离是否消除 gross/net 混淆？**沙箱外封存是否构成真权限边界**（核对 Codex `-C` workspace-write 是否确实无法读沙箱根外路径）？

## 第二部分：v3 新结构是否引入新缺陷（moving-block 块定义、family m=4、诊断型功效、沙箱外封存）。

## 结论：APPROVED（可放行 Tier A）/ NOT APPROVED（列**最小**第三轮必改，避免无限加码）。
**特别要求：** 若仍 NOT APPROVED，明确指出**剩余阻塞项是否属"历史样本不可约的识别上限"**（即无论怎么改预登记，历史数据都无法干净识别强平方向/做真功效门/真保管分离）——这对 CTO 判断 A-1 是否应转前向真实强平数据路径至关重要。

## 输出格式：同 RR2（执行摘要 / 5项闭合裁决表 / 高风险专项 / 新结构缺陷 / 结论+最小必改 + 是否不可约判断）。

## 铁律：禁读 HOLDOUT / `01_MEMORY_CORE/` / 禁改预登记 / 禁提前跑事件研究。允许读 v3/v2review/v1/Protocol/A-2 公开假设。完成写 `04_AI_TEAM/TASK_INBOX/A1_RR3_DONE.json`(task_id=A1_RR3,status,output_file,review_conclusion,conditions_closed=x/5,irreducible=yes/no,notes)。
