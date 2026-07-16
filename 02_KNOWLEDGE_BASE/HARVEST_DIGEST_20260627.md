# 历史报告积压 Harvest 权威摘要（P1-GOV-009 判断段）

**日期：** 2026-06-27｜**判断人：** Claude（主理人，DEC-069 权威语义不下放）
**输入：** Codex 提取段暂存 `HARVEST_STAGING_20260627.md`（扫 139 份：84 CODEX_TASKS + 55 RESULTS；分类 Carry15/系统18/工具6/TSMOM29/治理15/其他56；93 处 FAILED/KILL/NOT APPROVED）。
**方法：** verification-before-completion + 不重复已在库的大类结论（Codex 线索#300），只固化非冗余流程门 + 主理人判断。

---

## 一、主理人判断（最高价值，Founder 不会自己从 139 份看到的）

**结论：这 139 份积压里没有埋着被错过的 edge 或机制——全是我们已吸收的负面知识。** harvest 的真实价值＝① 确认范式判定没漏（我们学对了）；② 加固几道流程门。

**反复杀死研究的不是"参数没调好"，是同 5 个流程病：**
1. 数据输入不完整（universe/funding/basis/强平/价格面板缺口）。
2. 状态/口径漂移（冻结快照 vs 追溯包装得出相反结论）。
3. 机制先验弱（a2/A-1/形态：立项就没答清"谁付钱"）。
4. 成本门过不了（Sweep/TSMOM/#X2/#X3/OFI 反复死在这）。
5. 把 scaffold / 诊断 / 追溯包装误当正式证据。

**这 5 病项目当前纪律基本已内化**：机制优先七问、成本门焊最前、预登记冻结口径+第五件、BLOCKED≠FAILED、no-Holdout 物理封存。→ 印证转机制优先 + 投研线走对，不是绕远。

## 二、大类结论＝已在库/墓园，本轮不重复写（去冗余）

| 大类 | 已有权威位置 | 本轮动作 |
|---|---|---|
| Sweep/CHoCH/FVG/v4 实现线 | `SWEEP_SIGNAL_FAILURE_LESSONS_v2.md` + GRAVEYARD | 确认，不复活，不重写 |
| TSMOM 口径/第五件/WF/双引擎/扩universe | `TREND_TSMOM_LESSONS_v1.md` + GRAVEYARD | 确认，已有 |
| Carry 可行性/数据权限门 | `CARRY_KNOWLEDGE.md` + DEC-079/084/090 | 确认，已死/已禁 |
| #X2 RV / #X3 截面动量 | GRAVEYARD（2026-06-22 KILL） | 确认，已入墓园 |
| A-1/A-2/forced-flow/OFI | GRAVEYARD（休眠/KILL） | 确认，已记 |
| V4/V5 设计可复用资产 | `V4_REUSABLE_ASSETS_v1.md` | 已有 |

## 三、固化的非冗余流程门（本轮真正新增，写入下方为权威）

**门-H1（BLOCKED≠FAILED 任务状态分类）：** 网络/代理/下载/writer 失败 = **DATA-BLOCKED**，不是 alpha 失败，禁混为"机制死"；但会污染 universe/funding/basis/强平输入，须在任务状态单独标 BLOCKED/DATA-FAILED，并报 total/success/failed + 首个失败原因 + 代理状态 + 是否写入目标文件。（来源：D1/UNIVERSE_PIT/采集器 dataplane 多份；本会话"0行/风险E 误报""panel 400 假阴性"同根。）

**门-H2（scaffold/诊断/追溯 ≠ 证据）：** synthetic self-test / scaffold / 诊断 / 追溯包装只证代码可跑或事后口径，**不得包装为部分成功**；缺数据/封存/权限负向测试任一项=只能写 BLOCKED/FAILED。（来源：Carry feasibility/scaffold 多份。）

**门-H3（验证前置检查）：** 研究脚本前置加 ① 路径 denylist（防 broad rg / Holdout 误显——即便未参与计算也削弱 no-Holdout 自证）② 阈值只用 t 前数据（禁当前值进自身阈值）③ ready gate 离线自测 + manifest。（来源：PB1/DEC-070 审计/B5。）

**门-H4（工具治理登记）：** 任何新插件/Skill/MCP 进研究路径前登记：来源、版本/哈希、权限、API key 边界、撤销方式、是否可离线复现；外部 Skill 有 prompt injection/恶意脚本/数据出境/许可风险。（来源：GOV_TOOLING_EVAL/AI-NATIVE/OSS 合成；呼应本会话 grill-me/superpowers/x-reader 评估。）→ 关联 TOOLS_KNOWLEDGE。

**门-H5（工具不替裁决 / 不为工具加工具）：** 工具只沉淀判断或跑确定性检查，不替 Claude 做最终研究裁决（DEC-069）；当前瓶颈是轻治理/状态一致/验证门，不是缺重型工具——重工具须等连续失败样本证明本地机制不足（DEC-086）。

## 四、行动项（进 RESEARCH_ACTION_REGISTRY 候选，非阻塞）

| ID | 来源 | 结论 | 行动 | 状态 | 优先 |
|---|---|---|---|---|---|
| RA-H1 | 采集器多份 | Mac 侧补丁无解 | 清算/aggTrade 采集器 VM 直跑唯一线（已落地） | ✅已做 | — |
| RA-H2 | 下载多份 | 网络失败污染输入 | 下载报告强制 total/success/failed+首因+代理态（门-H1） | ⚪规范化 | P2 |
| RA-H3 | 工具调研 | 外部工具有风险 | 建插件/Skill/MCP 许可登记（门-H4） | ⚪待办 | P2 |
| RA-H4 | 治理多份 | 状态权威分散 | 状态/计划/完成事件收敛文件级单一源（部分已由 state_check+TASK_INBOX 做） | 🟡部分 | P2 |

## 五、纪律声明
未碰 Holdout、未回测、未调参、未耗计数。本摘要为 Claude 审 Codex 暂存后的权威产出；暂存原件 `HARVEST_STAGING_20260627.md` 保留为证据。大类负面知识已在各 KB/墓园，无新增机制候选。
