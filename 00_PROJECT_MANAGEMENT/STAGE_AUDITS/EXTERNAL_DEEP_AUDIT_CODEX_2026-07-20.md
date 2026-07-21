# Codex 独立第三方全方位审计报告

**委托方：** Founder  
**审计人：** Codex（按独立第三方审计人身份工作）  
**审计时点：** 2026-07-20T18:27:03Z（本机时区 Asia/Singapore 为 2026-07-21 凌晨）  
**报告文件：** `00_PROJECT_MANAGEMENT/STAGE_AUDITS/EXTERNAL_DEEP_AUDIT_CODEX_2026-07-20.md`

## 0. 审计边界与方法

本轮是只读审计；除本报告和完成信号外，不修改仓库内容，不执行交易或资金操作，不产生付费。未使用外网。`06_RESEARCH/DATA/HOLDOUT/` 内容未被查看；仅核验存在性、大小、mtime 与 SHA256，符合任务书允许的封存纪律审计范围。

只读覆盖面：
- 顶层规则、目标函数、资本架构、战略与机会地图：`CLAUDE.md`、`AGENTS.md`、`01_MEMORY_CORE/`、`00_PROJECT_MANAGEMENT/`。
- 中层架构、治理、自动化、任务流：`05_TECH_DESIGN/`、`05_ARCHITECTURE/`、`04_AI_TEAM/`、`scripts/`、git 状态。
- 底层研究、数据、代码、测试：`06_RESEARCH/`，排除 Holdout 内容读取。

关键命令证据：
- `rg --files -g '!06_RESEARCH/DATA/HOLDOUT/**' | wc -l`：1254 个非 Holdout 文件。
- `find 06_RESEARCH/CODE -name '*.py' -not -path '*/__pycache__/*' | wc -l`：114 个研究代码 Python 文件。
- `python3` AST 解析全仓 Python（排除 pycache/Holdout）：`parsed_files 118`，`syntax_errors 0`。
- `find 06_RESEARCH/DATA/HOLDOUT -maxdepth 3 -type f -print`：仅 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv`。
- `stat`：`a2_events_holdout.csv|14768|Jun 11 22:20:24 2026`。
- `shasum -a 256`：`3a2f48e6410bef25c46c9dacddd0e7453f2c7cc3d5fe01210104c79f65f683b5`。
- `bash scripts/no_holdout_lint.sh`：退出 0，无输出。

## 1. 总体结论

事实层判断：这个仓库不是“没人管”的项目。它有清晰目标函数、强研究协议、墓园纪律、任务交付链、数据缺口登记和较多单元测试；最近几轮失败也基本没有被粉饰成成功。最强资产是证伪纪律和能把失败落盘的文化。

同时，当前最大风险不在“某个策略少调一个参数”，而在权威层和运行层已经多次出现同一种失效模式：**说了/写了/进程在，不等于跑了/验了/同步了**。这会直接污染后续路线选择、自动化状态判断、Holdout 纪律证明、真实资金前的风控可信度。

严重度定义：
- S0：会破坏研究封存、资金安全、数据可信或让执行系统按错误权威行动。
- S1：会显著误导任务调度、验收口径、结论可复现性或自动化状态。
- S2：短期不致命，但会持续增加审计成本或造成二次误用。

## 2. 核心发现

### S0-01 生产/恢复脚本越过研究脚本边界，存在凭据、远端 root 数据回写和 git 破坏风险

事实：
- `06_RESEARCH/CODE/sg_recovery_20260719.sh:4` 开启 `set -x`；同文件 `:7` 使用 `StrictHostKeyChecking=no`；`:19` 用 `sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)"` 从远端回流数据；`:23` 删除 `.git/index.lock` 和 `.git/HEAD.lock`；`:24` 执行 `git add -A && git commit`。
- `06_RESEARCH/CODE/panel_refresh_via_sg.sh:4` 也开启 `set -x`；`:7` 关闭 host key 校验；`:20` 在远端 root 环境安装依赖并运行刷新脚本；`:23-25` 将远端数据、output 和报告 rsync 回本地仓库。
- `04_AI_TEAM/AGENT_REGISTRY.md:6` 明确 Codex 直调禁止 `git commit`；`AGENTS.md:23` 也要求 Codex 不直接 commit/push，由 Claude 验收后统一提交。

推断：
- 这些脚本已经不是普通研究脚本，而是带有远程生产运维、副作用回写和仓库持久化动作的半自动恢复脚本。
- `set -x` 叠加 `sshpass` 有把敏感命令形态写入日志的风险；远端 root 环境与本地仓库回写之间缺少 manifest/hash 校验，可能污染研究数据或报告；删除 git lock 可能破坏其他正在运行的 git 进程。

意见：
- 这是本轮最高优先级工程风险。研究脚本不得内置 git commit、不得删除 git lock；远程回写必须有 host key 校验、显式输入/输出 manifest、hash 校验和只读 dry-run 模式。

### S0-02 Holdout 纪律证明存在语义破口，状态文件还把破口写成“全部完好”

事实：
- `01_MEMORY_CORE/CURRENT_STATE.md:15` 写 TSMOM 引擎 L 已经经 Holdout 盲验 FAIL，TSMOM 全家族永闭，Holdout 消耗封账。
- `01_MEMORY_CORE/CURRENT_STATE.md:17` 又写“Holdout 全部封存完好；任何实验未读取”。
- `06_RESEARCH/CODE/tsmom_dual_engine.py:1215-1219` 记录过一次会话级事故：仓库级 `rg` 范围过宽，命中并显示了 `06_RESEARCH/DATA/HOLDOUT/a2_events_holdout.csv` 若干行；`:1295-1296` 写明全局 Holdout 自证 FAILED，且 lint 不覆盖本次人工 `rg` 事故。
- `scripts/no_holdout_lint.sh:2-8` 只扫描 `06_RESEARCH/CODE` 和 `04_AI_TEAM/CODEX_TASKS` 中同一行出现 `HOLDOUT` 与读函数的情况，不覆盖 `rg/sed/head/tail` 等内容显示型命令。

推断：
- TSMOM Holdout 被授权消耗与 A2 文件曾被静态搜索显示片段，是两类不同事件；前者是合规消耗，后者是会话级治理事故。当前 `CURRENT_STATE` 把二者合并写成“全部封存完好、任何实验未读取”，语义上不成立。
- 当前 lint 能发现一部分代码读取，但不能证明“会话未接触 Holdout 内容”。

意见：
- Holdout 状态应拆成至少三类：已授权消耗并封账、仍物理封存、曾发生非计算性内容暴露。`state_check` 必须检查这三个字段之间不能互相矛盾。

### S0-03 中层架构和任务主路径仍绑定已死策略，可能把后续工程资源导向错误目标

事实：
- `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md:6` 写 TSMOM regime 延续家族 Dead 且永久关闭；`:9` 写 delta 中性 carry Dead；`:7` 写 A-1 独立回弹 Dead。
- `05_TECH_DESIGN/PHASE2_SYSTEM_BLUEPRINT.md:20` 仍把 Phase 1 验证 edge 写成 “TSMOM扩展版 / A-1级联回弹 / Carry sleeve”；`:77-84` 仍列 TSMOM 和 Carry 策略模块；`:195-197` 仍列 Carry、TSMOM、A-1 上线里程碑。
- 正式架构 `05_TECH_DESIGN/02_SYSTEM_ARCHITECTURE.md:29` 和 `:41` 仍把 Layer 2 写成 TSMOM 信号、A-1 事件检测、Carry 状态管理。
- `05_TECH_DESIGN/04_MODULE_DESIGN.md:50` 仍写当前在途 D1/D2/D3；`:58` 仍把执行系统信号引擎写成 TSMOM/A-1/Carry。
- `00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md:261-263` 仍有 carry paper/shadow/真金上线任务；`:302-305` 当前关键路径仍围绕 carry 数据决策和 carry 产品化。

推断：
- 项目方向的权威顶部已经转向，但技术设计和任务下游仍保留旧路线。若新会话或 Codex 依据 `05_TECH_DESIGN` / `PROJECT_TASK_PLAN` 后段开工，会建设已判死策略的执行模块。

意见：
- Phase 2 应重写为策略无关底座：Decision Gateway、Risk Engine、账务/对账、数据契约、paper-forward adapter。策略名只能作为示例或历史，不应作为上线里程碑。

### S0-04 “旧宪法”与当前研究协议并存，验收权威会被文件名误导

事实：
- `AGENTS.md:13-15` 写当前成本与验收铁律：手续费 0.1%/边、滑点 0.1%、真实 funding；验收四件套，旧 Sharpe/MaxDD/Expectancy 门槛作废；Holdout 不得读取。
- `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md:1-10` 写明 v1.3/v1.4/v1.5 增补件优先，旧门槛全部作废，事件策略需 0.3/0.5/1.0% 滑点压力档。
- `00_PROJECT_MANAGEMENT/CONSTITUTION.md:6` 仍自称 v2.0 FROZEN；`:19` 仍写 Holdout Sharpe>1.0 为成功定义；`:245-248` 仍列 Expectancy>1.0、Sharpe>1.0、MaxDD<25%、历史触发次数等旧门槛。
- `06_RESEARCH/RESEARCH_PROTOCOL_v1.md:3` 虽声明以增补件为准，但正文 `:89-97` 仍保留 60/20/20 数据三分，`:145-157` 仍保留旧评估表。

推断：
- `CONSTITUTION.md` 这种命名和 FROZEN 状态会诱导新会话或低模型采纳旧标准。Protocol v1.2 虽有优先级声明，但旧正文仍会被检索和引用。

意见：
- 应把 `CONSTITUTION.md` 加降级横幅或改名归档；把 Research Protocol 合并成单一现行版，旧段落只能作为历史附录。

### S1-05 state-sync 制度存在，但机器检查给了错误安全感

事实：
- `01_MEMORY_CORE/STATE_SYNC_CHECKLIST.md:5-16` 要求状态变更当轮同步，并运行 `state_check.py`。
- `01_MEMORY_CORE/CURRENT_STATE.md:4` 自己记录 7/19 晚 THESIS_005 登记后 §1c 漏同步。
- `01_MEMORY_CORE/CURRENT_STATE.md:48-50` 仍写进度 2/10-20、首跑待 Founder 权限预批、P0-RES-010/011/012 本周派出；但同文件 `:21` 长段写真实进度 3/10-20，010/011/012 与 016/016b 已关闭。
- `01_MEMORY_CORE/BOOT_BRIEF.md:4` 最后更新仍是 2026-07-15；`:9` 仍写“当前恢复点（2026-07-06）”和 P0-RES-010~012 未派。
- 运行 `python3 01_MEMORY_CORE/state_check.py` 输出“无已知坏串”“无机器可判定权威冲突”“结论: 无已知滞后”，但同时阶段首命中显示 `CURRENT_STATE: Phase 1 / TASK_PLAN: Phase 0 / DECISION_LOG: Phase 0A`。
- `01_MEMORY_CORE/state_check.py:28-45` 主要靠固定坏串；`:201-260` 是当前检查主流程。

推断：
- 这不是没有状态制度，而是结构化字段太少，坏串扫描覆盖不了语义漂移。绿灯容易被误读为“权威文件一致”。

意见：
- 应把策略状态、任务状态、Holdout 状态、最新数据日期、运行层健康改成结构化字段，再由 `state_check` 做跨文件一致性校验。

### S1-06 代码内成本模型和验收门槛漂移，旧脚本结果不可与当前协议直接比较

事实：
- `06_RESEARCH/CODE/p1_01_tsmom.py:26-27` 使用 `FEE_RATE=0.0005`、`SLIPPAGE_RATE=0.001`；`:569-571` 用 `sharpe > 1.0` 和 `max_drawdown < 0.25` 判定通过。
- `06_RESEARCH/CODE/v4_strategy_backtest.py:26-28` 使用 `FEE_RATE=0.0004`、`SLIPPAGE_RATE=0.0005`、近似 funding。
- `06_RESEARCH/CODE/p0res038_phasea_free_data_audit.py:30` 写 `COST_GATES_BP = {"low": 70, "medium": 110, "cascade_high": 210}`。
- `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES038_PHASEA_20260622.md:24-25` 已指出硬纪律下应同时或优先报告 80/120/220bp。
- 较新的 `06_RESEARCH/CODE/carry/costs.py:22-24` 已使用 0.001 fee、0.001 slippage、0.003 event slippage；`06_RESEARCH/CODE/tsmom_dual_engine.py:1041-1048` 已实现新式 acceptance。

推断：
- 新旧脚本混用会造成 pass/fail 不可比，旧结果可能系统性乐观。当前代码库缺一个强制共享的成本/验收核心。

意见：
- 所有旧脚本应标 `legacy_do_not_use_for_current_acceptance`，或统一接入可审计的 `CostModel` 与 `acceptance_v1_5` 小函数；每份结果必须打印成本模型版本。

### S1-07 全量测试收集失败，测试目录结构本身不稳定

事实：
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q -p no:cacheprovider 06_RESEARCH/CODE/tests 01_MEMORY_CORE/test_state_check.py`：89 tests collected。
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q -p no:cacheprovider 06_RESEARCH/CODE 01_MEMORY_CORE/test_state_check.py`：119 tests collected 后失败。
- 失败原因：`import file mismatch`，`06_RESEARCH/CODE/test_backtest_rules.py` 与 `06_RESEARCH/CODE/tests/test_backtest_rules.py` basename 重复。
- `find 06_RESEARCH/CODE -name 'test_backtest_rules.py' -print` 返回两个路径。
- 两个文件分别见 `06_RESEARCH/CODE/test_backtest_rules.py:1-16` 与 `06_RESEARCH/CODE/tests/test_backtest_rules.py:1-13`。

推断：
- 局部 test subset 可收集，不代表全库测试入口可用。CI 或审计脚本如果指向 `06_RESEARCH/CODE` 会在收集阶段失败。

意见：
- 需要重命名根目录旧测试或调整 pytest import mode/配置；全库 collect-only 应作为最低健康门。

### S1-08 TASK_INBOX 与自动化验收权威不可靠

事实：
- `04_AI_TEAM/TASK_INBOX/README.md:16` 和 `AGENTS.md:50` 定义 status 枚举为 `completed / blocked / failed`。
- `04_AI_TEAM/TASK_INBOX/PROCESSED/P0RES015_DONE.json:4` 写的是 `"status": "FAIL"`。
- 冲突来自任务书 `04_AI_TEAM/CODEX_TASKS/TASK_P0RES015_ENGINE_L_HOLDOUT_BLIND_20260712.md:56` 要求 `status=PASS/FAIL/ERROR`。
- `04_AI_TEAM/watch_inbox.sh:15-19` 解析 JSON 后直接 `mv "$event" "$PROCESSED/"`，没有验证 `output_file` 是否存在、报告是否合格、status 是否符合协议。
- `04_AI_TEAM/TASK_INBOX/README.md:24-29` 设计上要求 Claude 读取记录、验收输出、派发下一步，再移动到 PROCESSED。
- `04_AI_TEAM/TASK_INBOX/PROCESSED/GOV-AUTO-001_DONE.json:2-5` 与 `GOV-AUTO-001_DONE_20260622.json:2-5` 是同一 task_id、同一时间、同一 output_file 的重复 DONE。

推断：
- `PROCESSED/` 只能证明文件被移动，不能证明任务已验收。枚举不一致会让自动化或统计脚本误分支。

意见：
- DONE 事件应有 schema 校验；`PROCESSED` 应改名或拆成 `SEEN` 和 `VERIFIED`，避免把“已移动”误当“已验收”。

### S1-09 git 与运行日志状态显示远端不是当前审计等价状态

事实：
- 审计中运行 `git branch -vv` 显示：`master 5a6774a [origin/master: ahead 9] ...`。
- `git status --porcelain=v1 --untracked-files=all` 显示：`M 04_AI_TEAM/CODEX_TASKS/ext_audit_20260720_run2.log`。
- 最新本地提交为 `5a6774a`，上一提交 `e78b5cb` 是 P0-GOV-013 派发；本地领先远端 9 个提交。
- `01_MEMORY_CORE/CURRENT_STATE.md:21` 又写 7/20 16:00 核查“git无积压”。

推断：
- 未见本轮 Codex 手动 commit/push；但从第三方审计视角，远端不是当前状态的等价备份，“git无积压”至少没有区分“本地已提交”与“远端已同步”。
- 运行日志在审计期间仍处修改态，说明交付审计时存在额外活跃/未收口的运行证据。

意见：
- 状态文件应分开报告：working tree clean、local commits ahead/behind、remote pushed、artifact logs archived。

### S1-10 资本原则清楚，但真钱前的可执行资本协议仍未闭合

事实：
- `CLAUDE.md:43` 与 `01_MEMORY_CORE/DECISION_LOG.md:1735-1742` 已清楚定义目标函数：找真实、可持续、可放大的 edge + 安全复利核心资本；月化 30% 不是验收条件；高杠杆不是 Alpha 来源。
- `00_PROJECT_MANAGEMENT/COMPANY_STRATEGY_PRODUCT_v1.md:45` 仍写围栏高风险子账户 “25% 本金”。
- `01_MEMORY_CORE/DECISION_LOG.md:1898-1899` 后续修订为证据等级解锁，未过 R4 不固定 25%。
- `00_PROJECT_MANAGEMENT/COMPANY_STRATEGY_PRODUCT_v1.md:104` 仍把核心 vs 围栏额度切分列为待 Founder 批。

推断：
- 原则层已经纠正了高杠杆/月化目标污染，但真钱执行层仍缺一份可执行的资本运行协议：额度、账户、触发条件、降级、补血上限、止损与回滚。

意见：
- 在任何真钱前，应另立 `CAPITAL_OPERATING_PROTOCOL.md`；旧的“25%”只能作为历史，不能作为默认额度。

### S2-11 数据资产本身有进展，但状态摘要中的数据日期漂移会误导复评时点

事实：
- 非 Holdout CSV 结构检查：`06_RESEARCH/DATA/FUTURES_EXPANDED_2026` 有 37 个 `*.csv`，所有文件末条时间 `min_last=max_last=2026-07-16 04:00:00`。
- `06_RESEARCH/DATA/LIQUIDATIONS/` 最近十日文件从 `liq_20260710.jsonl` 到 `liq_20260719.jsonl` 连续；`wc -l` 合计 298,016 行。
- `06_RESEARCH/DATA/LIQUIDATIONS/DATA_GAPS.md:7-10` 登记了 6/15 前永久起点边界和 7/19 欠费停机零数据损失终裁。
- `01_MEMORY_CORE/CURRENT_STATE.md:15` 仍写价格面板 37/37 刷新至 2026-06-22；同文件 `:20` 写 2026-07-16 已刷至 2026-07-16。

推断：
- 数据生产在推进，且缺口登记比多数个人项目更严；问题是权威摘要没有统一最新数据时间，可能影响 9/15 forced-flow 复评窗口计算。

意见：
- 数据资产应有机器生成的 `DATA_STATUS.json`，状态文件只引用它，不手写多个日期。

### S2-12 输出目录混入源码，源码/产物边界不清

事实：
- `06_RESEARCH/CODE/output/` 下存在 `.csv/.json/.png/.jpg/.html/.md`，也存在可执行 Python 文件。
- `04_AI_TEAM/CODEX_TASKS/REPORT_P0RES010_BINANCE_DELIST_EVENTS.md:13` 把 `06_RESEARCH/CODE/output/p0res010_make_delist_inventory.py` 作为生成脚本引用。

推断：
- `output/` 不再是纯结果目录。搜索、归档、lint、审计时容易把生成脚本当结果，或把结果当源码。

意见：
- 生成脚本应回到任务源码目录；`output/` 只放不可执行产物和 manifest。

### S2-13 假设登记表已失去当前性

事实：
- `00_PROJECT_MANAGEMENT/ASSUMPTION_REGISTRY.md:5-8` 要求新研究/系统决策开工前先扫假设表，证伪后更新状态。
- `ASSUMPTION_REGISTRY.md:22` 仍写 carry “部分验证（历史粗筛通过）/FEASIBILITY-LOCK进行中”。
- `ASSUMPTION_REGISTRY.md:24` 仍写 TSMOM “部分验证（Baseline）”。
- `ASSUMPTION_REGISTRY.md:63` 最后全表更新为 2026-06-20。
- 当前机会地图 `00_PROJECT_MANAGEMENT/OPPORTUNITY_MAP_STATUS.md:6` 已写 TSMOM Dead，`:9` 已写 carry Dead。

推断：
- 假设表本应防止换皮复活，但现在会把新会话引回旧假设。

意见：
- 假设登记表应纳入 `state_check`，每条假设需要 `last_decision_ref` 和 `current_status_source`。

### S2-14 成本盒是主闸之一，但当前是“知情接受滞后”，不是可观测止损

事实：
- `10_COST_TRACKING/COST_LOG_2026.md:5` 写“测不了的止损 = 没有止损”。
- 同文件 `:23-27` 仍以 871.93 元和 2026-06-11 起可观测为当前总览；`:37-42` 多项 6 月成本仍为待填。
- `00_PROJECT_MANAGEMENT/STAGE_AUDITS/L1_DEEP_AUDIT_CLAUDE_2026-07-15.md:60` 已指出成本盒仪表盲飞 34 天；`:130` 写 Founder 裁定账单补填搁置、滞后风险知情接受。

推断：
- 这不一定是违规，因为 Founder 已知情接受；但从第三方审计看，成本盒不能同时作为硬止损主闸和不可观测后台仪表。

意见：
- 若继续把 5000 元作为主闸，应至少月度记录“未知项上限估计”；否则把成本盒降级为软风险提示。

## 3. 正向控制与未发现问题

事实：
- 顶层目标函数已经从“月化 30%/高杠杆”纠偏为 edge + 核心资本复利；证据见 `CLAUDE.md:41-43` 与 `DECISION_LOG.md:1735-1742`。
- Research Protocol v1.3/v1.5 的四件套、事件滑点压力、MDE、叙事纪律和自动化边界写得足够硬；证据见 `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md:3-26`。
- TSMOM Engine L Holdout 失败没有被写成“部分成功”；机会地图和墓园均写 Dead，核心结论没有粉饰。
- A2 rolling percentile 与 A1 封存链路有测试和负权限证据；本轮未复验所有数值，但没有发现明显前视设计。
- 非 Holdout 数据资产有缺口登记，强平数据 2026-07-10 至 2026-07-19 连续。
- Python 语法层无错误；局部测试入口能收集 89 个测试，覆盖了不少前视、funding、止损、carry 引擎和 state_check 规则。

未发现的问题：
- 未发现 Codex 在本轮审计中直接 commit/push。
- 未发现本轮读取 Holdout 内容。
- 未发现把 TSMOM Holdout FAIL 改写为成功的证据。
- 已处理 DONE 的 output_file 整体存在性未见系统性缺失，但 DONE 枚举和验收状态权威仍有上述问题。

## 4. 建议优先级

1. 立即隔离并修订 `sg_recovery_20260719.sh`、`panel_refresh_via_sg.sh`：移除 `set -x`、`sshpass` 明文形态、`StrictHostKeyChecking=no`、git commit、删除 git lock；远程回写加 manifest/hash。
2. 重写 Holdout 状态模型：拆分“已授权消耗”“仍封存”“曾内容暴露”；扩展 lint 到 shell 内容显示命令和审计命令模板。
3. 给 `CONSTITUTION.md` 与旧 Research Protocol 正文加明确降级/历史横幅；单一入口只指向 v1.5。
4. 重写 Phase 2 架构和 `PROJECT_TASK_PLAN` 后段，去掉 TSMOM/A-1/Carry 作为上线目标，改为策略无关交易底座。
5. 把 `state_check` 从坏串扫描升级为结构化一致性检查：策略状态、任务状态、数据日期、Holdout 状态、git 状态。
6. 统一成本/验收核心函数，旧策略脚本全部标 legacy 或接入新函数。
7. 修复 pytest 全量收集失败；把全库 collect-only 放入最低健康门。
8. TASK_INBOX 增加 schema 校验，区分 `SEEN` 与 `VERIFIED`。
9. 为数据资产生成机器状态文件，避免权威摘要手写日期漂移。
10. 钱包/账户/围栏真钱前，另立资本运行协议，不引用旧“25%”作为默认。

## 5. 审计人最终判断

项目当前不是“方向彻底错误”，也不是“已经具备真钱运行条件”。更准确的描述是：研究纪律强于大多数早期项目，但运行纪律和权威文件一致性仍不足以承载真钱系统。最大短板是治理执行链，而不是单个 alpha 假设。

我对下一阶段的独立意见：先修运行层的证据链和权威一致性，再继续扩张自动化。否则即使找到一个前向看似有效的 edge，也会卡在“数据是否可信、状态是否同步、脚本是否越权、验收是否按现行口径”的审计泥潭里。
