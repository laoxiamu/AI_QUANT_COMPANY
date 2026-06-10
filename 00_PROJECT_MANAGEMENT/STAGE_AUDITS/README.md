# 审计文件统一目录

**本目录是项目所有审计/审查报告的唯一归档地。** 任何 L1/L2/L3 审计、Opus 审计包、污染/缺口核查报告都放这里，不再散落到 `09_OPERATIONS/` 或 `99_TEMP/`。

> 目录名沿用历史 `STAGE_AUDITS`（原仅放阶段审计），现已扩为全部审计的统一目录。未改名是为避免重写 DECISION_LOG 中已有的历史路径引用——决策日志是历史记录，不回改。

## 命名规范

| 类型 | 文件名格式 | 触发 |
|------|-----------|------|
| L1 月度审计 | `MONTHLY_AUDIT_YYYY-MM.md` | 每月自动（DEC-022） |
| L1 深度/不定期审计 | `L1_DEEP_AUDIT_[来源]_YYYY-MM-DD.md` | 按需（如 Codex 全盘核查） |
| L2 阶段审计 | `L2_AUDIT_[阶段]_YYYY-MM-DD.md` | 阶段跨越（DEC-022） |
| L3 紧急审计 | `L3_EMERGENCY_YYYY-MM-DD.md` | 风险信号触发（DEC-022） |
| Opus 审计包 | `OPUS_PACKAGE_[范围]_YYYY-MM[-DD].md` | 每次 L1/L2 生成 |
| 专项核查 | `[主题]_AUDIT.md` / `[主题]_REVIEW.md` | 按需 |

## 待办（路径协调）

- 定时任务 `ai-quant-monthly-audit` 的 SKILL.md 仍把 L1 月报写到 `09_OPERATIONS/MONTHLY_REVIEW/`。下次自动运行会再次散落到旧目录，需更新定时任务指令指向本目录（待 Founder 确认后由 Claude 用 schedule 工具更新）。
- DEC-022 正文记录的 L1/L2/L3 输出路径为历史口径，本次统一不回改决策日志；以本 README + CLAUDE.md「审计文件归档」节为现行准则。
