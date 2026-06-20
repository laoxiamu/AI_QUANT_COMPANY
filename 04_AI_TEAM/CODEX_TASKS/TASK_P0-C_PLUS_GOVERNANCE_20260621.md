# 任务包 P0-C+：防断档治理（封顶·不挤占 B0·做完即停）

**任务号：** P0-C-PLUS-20260621
**Owner：** Claude 起草与验收　**执行者：** Codex
**决策来源：** DEC-083（Founder D级：Orchestrator=只读骨架；ADR-001+C4 L1+变更传播现在做）
**性质：** Founder 关切"断档/记忆缺失"的对症治理。**封顶=本一包；做完即停。严禁滚动扩展为自动派单/Strategy Governor引擎/Web/Discord/七维路由/记分卡（DEC-083 仍 DEFER）。**
**优先级约束：** 不得挤占研究主线 B0；与 B0 并行，B0 优先。

---

## T1：只读状态/事件日志骨架（SQLite，G2 只读 PoC）

**目标：** 给项目一个"任务状态有据可查、断了能恢复"的兜底，纯记录+只读展示。

**交付：**
- `04_AI_TEAM/orchestrator/event_store.py`：SQLite append-only 事件库。
  - 表 `task_events`：`event_id / task_id / actor / event_type / prev_state / next_state / payload_hash / created_at`。
  - 表 `task_state`（投影）：`task_id / status / next_actor / recovery_point / updated_at`。
  - API：`append_event()`（只写事件）、`get_task_state()`、`list_tasks()`、`render_status()`（只读文本/markdown 展示）。
- `04_AI_TEAM/orchestrator/test_event_store.py`：覆盖 append→投影一致、重复 event_id 幂等拒绝、重启后从 SQLite 恢复状态。
- 一次性回填脚本：把现有 TASK_INBOX/PROCESSED 的 *_DONE.json 导入事件库（证明可用）。

**硬禁止（DEC-083 边界）：**
- ❌ 不自动派单、不自动执行任何任务、不调用 Claude/Codex。
- ❌ 不建 Web / Discord / 任何控制面 / HTTP 服务。
- ❌ 不写任何权威文件（DECISION_LOG/CURRENT_STATE/TASK_PLAN/BOOT_BRIEF）——只读它们或独立记录。
- ❌ 不引入 Temporal/LangGraph/Celery 等重型依赖；纯标准库 sqlite3。

**验收：** 测试全过；render_status 能展示当前任务状态；重启 demo 显示状态从 SQLite 恢复；确认零自动执行路径。

---

## T2：DEC 变更传播强化（扩 state_check）

**实证动机：** 本轮 Claude 改 DEC-080 索引却漏了正文，靠 state_check 才抓到；STATE_SYNC_CHECKLIST 存在但未被严格执行。

**交付：** 扩 `01_MEMORY_CORE/state_check.py`（在现有真绿灯基础上增量）：
- 新增检查：DECISION_LOG 出现新 `DEC-XXX` 正文块时，校验该 DEC 的关联传播位是否同步——至少检 BOOT_BRIEF/CURRENT_STATE 的"最新DEC"指针（已有）+ 报告"该 DEC 是否在 CURRENT_STATE §1c 或 §4 被引用"。
- 新增 `--changelog` 模式：列出 DECISION_LOG 最大 DEC 号 vs 各权威文件引用该号的位置，缺失即非零退出。
- 保持现有 self-test 全绿；新增对应自测样本。

**禁止：** 不改 STATE_SYNC_CHECKLIST 以外的权威文件正文；只读校验。

---

## T3：ADR-001（技术架构决策留痕，一页）

**交付：** `05_ARCHITECTURE/adr/ADR-001-defer-orchestrator.md`，格式 Context/Decision/Alternatives/Consequences/Status/Related-DEC。
- 记录技术架构选择：**edge=0 阶段不建完整自动编排/控制面，维持文件式 handoff + 只读状态骨架**。
- Related DEC：DEC-082、DEC-083（业务/方向口径留在 DEC，不复制进 ADR）。
- **Codex 起草草案，Claude 验收定稿**（理由判断由 Claude 把关）。

---

## T4：C4 Level 1（当前态系统图，一页）

**交付：** `05_ARCHITECTURE/c4/L1_system_context.md`（C4-PlantUML 或 mermaid 均可）。
- 元素：Founder、Claude(Cowork)、Codex(CLI)、权威文件+Git、强平采集器(腾讯云SG)、Binance、只读状态骨架(T1)。
- 每个元素标 `CURRENT / PLANNED / DEPRECATED`，**不画未建设系统冒充现状**。
- 只画 Level 1（System Context）；不画 Container/Component（DEFER）。

---

## 完成通知与封顶自检

按协议写 `04_AI_TEAM/TASK_INBOX/P0-C-PLUS-20260621_DONE.json`。
报告 `REPORT_P0-C_PLUS.md` 末尾必须列 **「未做清单（已冻结）」**：完整 Orchestrator 自动派单 / Strategy Governor 引擎 / Web / Discord / 七维路由 / 九域记分卡 / Spec Kit 全量 —— 声明本任务不做、按 DEC-083 冻结。

**【需要 Codex】** T1-T4。
**【Claude 继续】** 验收（尤其 T1 零自动执行边界 + ADR-001 理由把关）；与此并行起草/推进 B0。
