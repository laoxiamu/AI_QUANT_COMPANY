# Codex Skills 安装记录与项目使用建议

**日期：** 2026-06-14  
**执行人：** Codex  
**状态：** 工具层安装记录，不构成项目架构决策  
**安装位置：** `/Users/yaomingyu/.codex/skills/`

---

## 1. 安装结果

| Skill | 来源 | 状态 | 用途 |
|---|---|---|---|
| `PlanToDelivery` | `fitoe/PlanToDelivery` | 已安装 | 项目阶段编排、门禁、交付闭环、跨会话恢复 |
| `find-skills` | `vercel-labs/skills` | 已安装 | 搜索、评估、安装 open agent skills |
| `huashu-nuwa` | `alchaincyf/nuwa-skill` | 最小安装 | 蒸馏人物/主题思维方式，生成新的认知型 skill |
| `darwin-skill` | `alchaincyf/darwin-skill` | 最小安装 | 评估和优化现有 skill，含人工确认与回滚原则 |
| `tdd` | `mattpocock/skills` | 已安装 | 测试驱动开发，红绿重构 |
| `diagnose` | `mattpocock/skills` | 已安装 | 复杂 bug / 性能问题的诊断闭环 |
| `improve-codebase-architecture` | `mattpocock/skills` | 已安装 | 识别架构摩擦和可测试性改进点 |
| `to-issues` | `mattpocock/skills` | 已安装 | 把计划/PRD拆成可执行 issue |
| `obra/superpowers` full suite | `obra/superpowers` | 已安装 14 个 skill | Superpowers 工作流套件：技能路由、头脑风暴、计划执行、TDD、诊断、代码审查、并行代理、worktree、收尾验证等 |

说明：

- `PlanToDelivery` 和 `find-skills` 使用 Codex skill-installer 正常安装。
- 女娲、达尔文仓库通过完整 clone / `npx skills add` 在当前网络下卡住；已改为最小安装：下载上游 `SKILL.md` 与 `README.md`，使 Codex 能识别和触发。后续如需完整素材库，再单独补全。
- `obra/superpowers` 通过 `npx skills add obra/superpowers -g -y` 安装到 `~/.agents/skills/`，并已同步到 `~/.codex/skills/`。安装器提示 PromptScript 辅助脚本失败，但 14 个 `SKILL.md` 本体已就位；重启 Codex 后新会话可识别。

---

## 2. 项目内推荐用法

### `PlanToDelivery`

适合多步骤、多角色、跨会话的交付任务，例如未来 Discord / IM 协作控制面 PoC。当前 Phase 1 每个小实验不应强制套完整交付流程，避免放大风险 B。

### `find-skills`

适合搜索技能生态。常用命令：

```bash
npx skills find "crypto perpetual funding open interest liquidation"
npx skills find "perpetual futures funding rate"
npx skills find "crypto market microstructure order flow"
npx skills find "crypto order book futures"
npx skills find "code review"
npx skills find "discord bot"
```

不要用 `quant research` 作为主搜索词：返回结果大量偏证券/股票/传统多因子，与本项目的加密永续合约、funding、OI、强平、交易所微观结构差异很大。

搜索结果不能直接安装，需检查安装量、来源信誉、GitHub stars、许可证和是否触碰凭据/交易。

### `huashu-nuwa`

适合创建“思维角色”型 skill。候选方向：

- Quant Research Risk Reviewer
- Backtest Protocol Auditor
- Data Leakage Detector
- Codex Task Spec Writer

不用于直接生成正式决策，不蒸馏私密或版权风险内容。

### `darwin-skill`

适合评估和小范围优化我们自己创建的项目专用 skill。第三方 skill 只评估，不自动改写。

### `tdd`

适合 Codex 实现新代码模块、修复 bug、构建可测试数据处理逻辑。Claude 任务规格可要求 Codex 使用 TDD，并在报告中给出失败测试、通过测试和覆盖行为。

### `diagnose` / `systematic-debugging`

适合采集器、调度器、回测脚本、数据下载、服务器进程异常。连续两次修复失败后，应强制进入诊断流程。

### `improve-codebase-architecture`

适合 Phase 2 代码成形后审查模块边界、测试难度和 Agent 可导航性。当前阶段不为“漂亮架构”提前重构研究脚本。

### `to-issues`

适合把大型计划拆成可执行任务。当前项目没有以 GitHub issue 为权威队列，输出应适配 `04_AI_TEAM/CODEX_TASKS/` 或 `04_AI_TEAM/TASK_INBOX/`。

---

## 3. 已调研但暂不安装

| 来源 | 暂不安装原因 |
|---|---|
| Longbridge skills | 需要券商/账户/市场数据授权，且含交易相关能力；当前会扩大凭据和资金边界 |
| Binance / OKX / Blofin 官方交易所 skills | 安装量高但容易涉及 API key、账户、下单或真实交易操作；除非 Founder 明确限定“只读市场数据”，否则不自动安装 |
| 加密合约低安装量第三方 skills | 方向相关但维护质量、权限边界、实现可靠性未审计；先记录候选，不并入默认工具链 |
| 泛化 `quant-analyst` skills | 内容较模板化，可能与本项目 Research Protocol 冲突 |
| 大型 all-in-one skill 包 | 容易触发技能过载，增加上下文噪声 |
| 未知低安装量 skill | 安全和维护质量未验证 |

已执行的加密合约专项搜索：

- `crypto perpetual funding open interest liquidation`
- `perpetual futures funding rate`
- `liquidation cascade crypto`
- `crypto market microstructure order flow`
- `crypto order book futures`
- `binance futures liquidation`
- `onchain derivatives funding`

候选但未装：

- `agiprolabs/claude-trading-skills@market-microstructure` / `@custom-indicators`：研究方向较接近，但 `npx skills add` 克隆长时间无响应，已中断；如后续要装，建议先单独 clone 审计 `SKILL.md` 和权限边界。
- `aaaaqwq/claude-code-skills@tracking-crypto-derivatives`：命中 funding / OI / liquidation，但安装量低，需人工审计。
- `coinglass-official/coinglass-api-skills@coinglass-api`：数据方向可能有用，但涉及外部 API 和额度/凭据边界，需 Founder 确认只读用途。

---

## 4. 治理边界

本次安装属于个人 Codex 工具环境扩展，不自动改变项目流程。

权威仍为：

```text
DECISION_LOG → CURRENT_STATE → 公司 OS 蓝图 → Research Protocol → 任务规格/报告
```

任何 skill 输出必须经过项目既有流程吸收：

- 决策类内容：Claude 审阅，必要时 Founder 确认。
- 代码类内容：测试与验收。
- 文档类内容：不得绕过 CURRENT_STATE / DECISION_LOG 规则。
- 交易类内容：不得触发资金、下单或凭据操作。

---

## 5. 后续动作

1. 重启 Codex，使新 skill 被会话发现。
2. 若建设 Discord / IM 协作控制面，可用 `PlanToDelivery` 做 PoC 阶段门禁。
3. 若创建项目专用 skill，先用女娲生成草案，再用达尔文做小范围评估。
4. 不做自动批量 skill 优化。

【Codex继续】
