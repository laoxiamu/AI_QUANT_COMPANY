# A1-TIERA-EXEC：A-1 Tier A 历史关联快筛执行（按预登记 v5，Founder 已 GO）

**授权：** Founder "可以按你的推荐计划跑"（2026-06-15）+ A1_RISK_REVIEW_v5 = APPROVED(4/4)。主会话(Claude/CTO)人工派发。
**唯一权威规格：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v5.md`（**严格按其冻结口径，禁止偏离/优化/加过滤**）。
**计数定性：** 机制前关联快筛，**不耗独立 Alpha 计数**；结论上限=关联层，**禁止任何"机制成立/因果验证"措辞**（DEC-075 + `RESEARCH_PROTOCOL_v1.4_A1SCREEN_ADDENDUM.md`）。
**输出：** `06_RESEARCH/RESULTS/20260615_a1_tierA_screen.md`（判决报告）+ `06_RESEARCH/CODE/` 下脚本与单测 + `04_AI_TEAM/TASK_INBOX/A1_TIERA_DONE.json`。

---

## 铁律（违反即研究作废）

- **禁止读取任何 HOLDOUT**：A-1 sealed 40 条、A-2 `a2_events_holdout.csv` 218 条，均**不得用于任何事件后收益计算**。
- 事件后 CAR **只在 work 集计算**。
- 全部参数取自 v5 冻结值，**不得调阈值/不得加过滤/不得事后择 horizon/不得改 episode 规则**。seed=20260615。
- 结论措辞只到关联层；不显著只写"未拒绝 H0/未验证"，**禁写"机制"二字**。

## 两阶段结构（custodian / executor 分离，§12）

### 阶段 1：CUSTODIAN（保管：生成+切分+加密，先做）
1. 按 v5 §2 冻结口径用历史数据生成 pooled episodes（BTC/ETH/SOL，`ts<2024-12-10`）：
   - 数据源：复用既有 A-1 OI/价格特征数据与代码（`06_RESEARCH/CODE/features/a1_oi_features.py` 等）；OI=`sumOpenInterestValue` 名义、MARK 价。若现有数据/特征与 v5 口径（纯方向 `r6h<0`、24h refractory、名义 OI、有效观测谓词）不一致，**以 v5 为准重建**，并在报告说明差异。
   - 触发：`d6h_rolling_pctl<=0.01 且 r6h_mark<0`（§2）。Episode：24h refractory，event_time=首触发。
2. 切分：按 `(event_time_utc, symbol)` 排序 deterministic 每第 5 个预留 sealed，其余 work。
3. 加密封存（§12 冻结）：`sealed_holdout_episodes.csv` 用 **AES-256-GCM** 加密为 `06_RESEARCH/DATA/A1_WORK/sealed_holdout.enc`（格式 `12B nonce‖密文‖16B tag`）；**密钥写入 `~/.aiquant_sealed/a1/a1_key.bin`（项目目录之外）**；`work_episodes.csv` 明文写 `06_RESEARCH/DATA/A1_WORK/`；写 `A1_HOLDOUT_MANIFEST.json`（work/sealed 行数、schema、git hash、两文件 SHA-256、解封条件、一次性使用记录字段）。
4. 负向权限测试留痕 `A1_HOLDOUT_PERMTEST.log`：记录"读 manifest 成功(退出码0)"+"解密 sealed 在不提供密钥时失败(非零码+原因)"。
5. **阶段1 结束后，sealed 明文变量须从内存释放，阶段2 绝不重新读取 sealed 明文或 .enc 解密**（代码层 assert + 注释标明）。

### 阶段 2：EXECUTOR（执行：只读 work，算判决）
仅加载 `work_episodes.csv`（assert 不触 sealed/holdout）。按 v5 计算并逐项给 PASS/FAIL：
1. **CAR**（§4）：1H MARK 对数收益，baseline `[-72h,-1h]`，48h 主 / 24h 次 / 72h 仅探索。
2. **主推断**（§4）：circular moving-block bootstrap，半开网格 `[t_1,t_n+1h)`、周长 span=(t_n-t_1)+1h、块宽 W=144h、circular offset 抽块与截断、零假设重心化、单侧 p=`(#{居中均值≥观测}+1)/(B+1)`、basic CI、B=10000、seed=20260615。
3. **单调性**（§5）：severity 三档，对 48h CAR 的 Spearman，配对 moving-block bootstrap 对 `ρ` 居中检验 `H0:ρ=0`。
4. **A-2 非重叠关联硬门**（§7）：a2_overlap=事前最近单个 8H funding 读数滚动 P95；non-overlap 48h CAR。
5. **Holm family m=4**={48h, 24h, 单调性, non-overlap}，控 FWER@0.05。
6. **WF**（§11）：work 按 event_time 分三段(余数给前段/其次第二段)、切点=相邻中点、按实际足迹 `[event_time-72h, align+48h]` purge 跨切点者、purge 后不重分段；3 段 48h 裸均值 ≥2 段>0。
7. **成本诊断**（§8）：48h 在 base/0.30% 的 net CAR（仅诊断）。
8. **Decision Table**（§11）：逐项 PASS/FAIL/N.A.（N.A.→整体 FAIL）；给最终 Tier A 判决=PASS(关联成立,探索级)/FAILED。

## 报告要求（`20260615_a1_tierA_screen.md`）
- 顶部一行结论：Tier A **PASS（可观测条件回弹关联成立，探索级，不声称机制）** / **FAILED**。
- §11 decision table 逐项 PASS/FAIL/N.A. + 数值(均值/p/CI/各 horizon n_eff)。
- work/sealed 行数 + manifest SHA + 负向测试结论。
- 主理人解读留给 Claude：报告只给数值与逐项判决，**附一句"对 CTO 的提示：本结果只支持/不支持继续投路径B 前向确证"**。
- 单元测试：触发逻辑、refractory、moving-block 截断、Holm、AES-GCM 往返 至少各 1 例。

## 工程
- 七问前置已由 Claude 完成。失败关闭：数据缺口标 N.A. 并说明，不臆造、不补 cutoff 后数据。
- 完成写 `04_AI_TEAM/TASK_INBOX/A1_TIERA_DONE.json`(task_id=A1_TIERA,status,verdict=PASS/FAILED,output_file,notes=最重要数值与一句判断)。
- Git：可 commit 代码与报告（验收后推送制，Claude 复核）。
