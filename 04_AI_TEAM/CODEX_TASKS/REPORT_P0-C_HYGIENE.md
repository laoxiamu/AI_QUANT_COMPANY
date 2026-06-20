# REPORT_P0-C_HYGIENE

**任务号：** P0-C-HYGIENE-20260621  
**执行时间：** 2026-06-21 UTC+08  
**范围：** T1 state_check 修复；T2 四份规则文件冲突裁决建议；T3 防扩张闭环。  
**未改动：** `CLAUDE.md`、`AGENTS.md`、`01_MEMORY_CORE/SYSTEM_RULES.md`、`04_AI_TEAM/AGENT_REGISTRY.md` 正文均只读，未直接修改。

## 执行前七问自查

| 问题 | 回答 |
|---|---|
| 任务在验证什么机制？ | 验证研究输入卫生：旧状态、规则冲突、假绿灯不得污染 B0-B4。 |
| 验收标准是否可量化？ | 是：退出码、路径定位、坏串命中、最新 DEC 一致性、自测、冲突清单、冻结清单。 |
| 有无更便宜等效实现？ | 有且已采用：只修小脚本 + 小测试 + 裁决建议报告，不扩展为治理系统。 |
| 是否触碰禁止项？ | 未触碰 Holdout；未改预登记；未简化成本；未读数据；未引黑箱依赖；未改四份规则正文。 |

## T1 state_check.py 修复

### 已交付

- `01_MEMORY_CORE/state_check.py`
  - 默认项目根从硬编码 Mac 绝对路径改为按脚本位置向上寻找 `CLAUDE.md` + `01_MEMORY_CORE/`。
  - 任意缺失、坏串、最新 DEC 不一致、机器可判定权威冲突均累计 `problems`，最终非零退出。
  - 新增最新 DEC 一致性：`BOOT_BRIEF` / `CURRENT_STATE` 指针必须等于 `DECISION_LOG` 实际最大 `DEC-XXX`。
  - 新增坏串库：月化30%作为验收/门槛语境、唯一已验证主线、新主线=regime-adaptive、10-20x 杠杆作为实验/Alpha语境、carry 出现在 active 主线位。
  - 新增 `--self-test`：坏串样本必须非零，干净样本必须 0。
- `01_MEMORY_CORE/test_state_check.py`
  - 覆盖坏串非零、干净样本 0、最新 DEC mismatch 非零、权威冲突非零、任意 cwd 自动定位、内置 self-test。

### 验证结果

| 命令 | 结果 |
|---|---|
| `python3 -m pytest 01_MEMORY_CORE/test_state_check.py -q` | PASS：6 passed |
| `python3 01_MEMORY_CORE/state_check.py --self-test` | PASS：self-test passed |
| `python3 01_MEMORY_CORE/state_check.py` | 返回非零：当前命中 `DECISION_LOG` 中 DEC-080 旧“月化30%目标”正向语境（L2099/L2107）；这是本任务要求的非假绿灯行为，未擅自改权威正文。 |

## T2 冲突清单

| 冲突项 | 文件A条款 | 文件B条款 | 建议生效规则 | 依据 | 是否需 Claude/Founder 拍板 |
|---|---|---|---|---|---|
| Codex commit 权限 | `AGENTS.md:23`：每任务完成 commit，message 带任务号 | `04_AI_TEAM/AGENT_REGISTRY.md:6`：Codex 直调禁止 git commit，Claude 验收后统一 | **Codex 不直接 commit；Codex 只交付代码、报告、TASK_INBOX 事件；Claude 验收后统一 commit/push。** | AGENT_REGISTRY 是 DEC-069 双审计后的 Agent 权限表；当前任务也要求先等 Claude 验收；直调 runbook 未把 commit 作为 Codex 步骤。 | 需 Claude 拍板并改 `AGENTS.md`；不建议上 Founder，除非要改变验收后推送制。 |
| §1c 写入 vs Memory Core 禁写 | `CLAUDE.md:89`：任何建议/方案/行动项当场写入 `CURRENT_STATE §1c` | `SYSTEM_RULES.md:52`：对话中的分析、推演、草稿不得写入 MEMORY_CORE | **§1c 是 CURRENT_STATE 运行看板的“对话级建议暂存区”，不等于长期事实入库；可写入但必须标注未确认，确认后才升入 §4/DECISION_LOG。** | DEC-073 已专门建立 §1c 制度；SYSTEM_RULES 原句意图是防止把草稿升级为 FACT/DECISION。 | 需 Claude 拍板澄清 `SYSTEM_RULES` 措辞；若严格遵守 SYSTEM_RULES 自身维护条款，可由 Claude 判断是否补 Founder 确认。 |
| 新对话启动协议 | `CLAUDE.md:49-60`：先读 `BOOT_BRIEF`，必要时再读 CURRENT_STATE/DECISION_LOG/PROJECT_CONTEXT | `SYSTEM_RULES.md:121-138`：先读四个文件，含已废弃 `PROJECT_OPERATING_STATE.md`，且向用户确认阶段/目标 | **生效规则用 CLAUDE.md v2.4：BOOT_BRIEF first，按需读取权威文件；不得读取废弃 `PROJECT_OPERATING_STATE.md` 作为启动必选。** | DEC-082 后 BOOT_BRIEF 已同步为启动摘要；`PROJECT_OPERATING_STATE.md` 已被 state_check 注释标为废弃路径。 | 需 Claude 拍板修 `SYSTEM_RULES` 第5节。 |
| Claude/Codex 执行边界 | `CLAUDE.md:76-78`：Claude 规划分析 + 小规模执行（≤50行脚本），Codex 复杂实现（>100行、多文件、需迭代） | `SYSTEM_RULES.md:19-21`：Claude 可直接数据下载、环境安装、运行脚本、回测、文件写入，不需 Codex；Codex 限复杂系统代码 | **按 DEC-021/CLAUDE.md 生效：Claude 可做小脚本与验收，复杂实现/多文件/大量迭代交 Codex；是否“研究回测”不是边界，复杂度和审计风险才是边界。** | CLAUDE.md 更新到 2026-06-13，SYSTEM_RULES 停在 2026-06-04，且当前项目已形成 Codex 直调验收链。 | 需 Claude 拍板修 `SYSTEM_RULES` 第1.2节。 |
| 状态权威：DB vs 文件 | `SYSTEM_RULES.md:94`：PostgreSQL 是唯一权威状态源，`_positions` 是缓存 | `AGENTS.md:20`：持仓/状态以 DB 或文件为权威，禁内存字典 | **交易/持仓/生产账户状态以 DB 为权威；项目治理、任务、决策、研究状态以权威文件为准；任何状态禁止以内存字典为最终权威。** | V4 事故根因是内存状态；当前项目治理实际依赖 DECISION_LOG/CURRENT_STATE/TASK_INBOX 文件权威。 | 需 Claude 拍板澄清 `SYSTEM_RULES` 与 `AGENTS.md`。 |

## T3 未做清单（已冻结）

以下项本任务不做，且按 DEC-082 冻结，直至“一条 edge 通过 B2”或“Founder 时间被实测为瓶颈”等解冻触发出现：

- Orchestrator / 事件库
- Strategy Governor 引擎
- 控制面
- Web / Discord
- 七维路由
- 九域记分卡
- Spec Kit 试点
- C4 全套
- ADR-业务项

## 验收自检

| 验收项 | 状态 |
|---|---|
| T1 退出码语义正确 | PASS：坏串/DEC mismatch/权威冲突测试均非零；干净样本为0。 |
| T1 路径鲁棒 | PASS：无参数运行从脚本位置定位项目根；任意 cwd 测试无 `[缺失]`。 |
| T1 坏串库更新 | PASS：所列坏串已加入，带少量纠正语境 allowlist，避免把“已纠正/移出验收”误作同类污染。 |
| T1 最新 DEC 检查 | PASS：`BOOT_BRIEF` / `CURRENT_STATE` 指针与 `DECISION_LOG` 最大 DEC 比对。 |
| T1 最小自测 | PASS：`--self-test` + pytest 覆盖。 |
| T2 冲突清单 | PASS：两项必裁 + 三项扫描补充，未改四份规则正文。 |
| T3 防扩张 | PASS：冻结未做清单已列。 |

## 备注

- 未执行 git commit：本任务核心冲突之一就是 `AGENTS.md` 要求 commit 与 `AGENT_REGISTRY.md` 禁止 Codex commit 冲突；本报告建议生效规则为“Codex 不直接 commit，Claude 验收后统一”。
- 当前 live `state_check.py` 返回非零，因为 `DECISION_LOG` 正文仍保留 DEC-080 旧“月化30%目标”正向语境。Codex 按任务禁止项未改权威文件正文，交 Claude 验收裁决。
