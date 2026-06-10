# Claude Code 最佳实践：从入门到精通的完整指南

**URL:** https://mp.weixin.qq.com/s/GV8ws6Luwf7FxHA-ok8sZA

**字数:** 4223

---

Claude Code 是一个智能体编码环境。不同于等待回答问题的聊天机器人，Claude Code 可以读取你的文件、运行命令、修改代码，并自主解决问题。

核心约束：上下文窗口是关键

大多数最佳实践都基于一个约束：

Claude 的上下文窗口填充很快，性能会随着填充而下降。

上下文窗口包含你的整个对话，包括每条消息、每个文件内容和每个命令输出。当上下文窗口快满时，Claude 可能开始"忘记"早期指令或犯更多错误。

给 Claude 验证工作的方法

提供测试、截图或预期输出，让 Claude 能够自我检查。这是你能做的最有效的事情。

没有明确的成功标准，Claude 可能会产出看起来正确但实际不工作的代码。

策略对比：

策略

❌ 之前

✅ 之后

提供验证标准

"实现一个验证邮箱的函数"

"写一个 validateEmail 函数。测试用例：user@example.com

[1]

返回 true，invalid 返回 false"

UI 变更可视化验证

"让仪表盘更好看"

"粘贴截图，实现这个设计，截图对比差异并修复"

解决根本原因

"构建失败了"

"构建失败报这个错误：粘贴错误，修复并验证构建成功"

先探索，再规划，最后编码

推荐的工作流程有四个阶段：

1. 探索

— 进入计划模式，Claude 读取文件并回答问题，不做修改

2. 规划

— 让 Claude 创建详细的实现计划

3. 实现

— 切换出计划模式，让 Claude 编码并验证

4. 提交

— 让 Claude 提交代码并创建 PR

计划模式很有用，但也会增加开销。对于范围明确的小任务（如修复拼写错误、添加日志行），直接让 Claude 做就行。

在提示中提供具体上下文

指令越精确，需要的修正就越少。

策略

❌ 之前

✅ 之后

限定任务范围

"给 foo.py 加测试"

"给 foo.py 写测试，覆盖用户登出时的边界情况，避免使用 mock"

指向信息来源

"为什么 ExecutionFactory 的 API 这么奇怪？"

"查看 ExecutionFactory 的 git 历史，总结它的 API 是怎么演变的"

参考现有模式

"添加一个日历组件"

"研究主页上现有 widget 的实现模式，HotDogWidget.php 是个好例子，按照这个模式实现新的日历组件"

描述症状

"修复登录 bug"

"用户报告会话超时后登录失败，检查 src/auth/ 的认证流程，特别是 token 刷新，先写一个失败测试复现问题，再修复"

提供丰富内容的方法：

• 使用

@

引用文件

• 直接粘贴截图/图片

• 提供 URL 获取文档

• 通过管道传入数据：

cat error.log | claude

配置你的环境

编写有效的 CLAUDE.md

CLAUDE.md 是一个特殊文件，Claude 在每次对话开始时都会读取。运行

/init

自动生成初始文件。

CLAUDE.md 应该包含：

• ✅ Claude 猜不到的 Bash 命令

• ✅ 与默认值不同的代码风格规则

• ✅ 测试说明和首选测试运行器

• ✅ 仓库规范（分支命名、PR 约定）

• ✅ 项目特定的架构决策

• ✅ 开发环境的特殊要求

CLAUDE.md 不应该包含：

• ❌ Claude 通过阅读代码就能知道的内容

• ❌ Claude 已经知道的标准语言约定

• ❌ 会频繁变化的信息

• ❌ 冗长的解释或教程

配置权限

三种方式减少中断：

•

Auto 模式

：分类器自动审查命令，只阻止有风险的操作

•

权限白名单

：允许特定安全命令

•

沙箱隔离

：操作系统级别的文件和网络访问限制

使用 CLI 工具

告诉 Claude Code 使用

gh

、

aws

、

gcloud

等 CLI 工具与外部服务交互。

连接 MCP 服务器

运行

claude mcp add

连接外部工具，如 Notion、Figma 或数据库。

设置 Hooks

Hooks 在 Claude 工作流程的特定点自动运行脚本。与 CLAUDE.md 指令不同，Hooks 是确定性的，保证动作一定会执行。

创建 Skills

在

.claude/skills/

目录下创建

SKILL.md

文件，为 Claude 提供领域知识和可复用的工作流程。

安装插件

运行

/plugin

浏览市场，插件将 skills、hooks、subagents 和 MCP 服务器打包成一个可安装单元。

高效沟通

询问代码库问题

把 Claude 当作高级工程师来提问：

• 日志系统是怎么工作的？

• 如何创建新的 API 端点？

• 第 134 行的

async move { ... }

是什么意思？

让 Claude 采访你

对于大型功能，先让 Claude 采访你：

我想构建 [简要描述]。使用 AskUserQuestion 工具详细采访我。

询问技术实现、UI/UX、边界情况、关注点和权衡。

采访完成后，写一份完整的规格说明到 SPEC.md。

会话管理

及早并经常纠正方向

•

Esc

：停止 Claude 的动作，保留上下文

•

Esc + Esc

或

/rewind

：打开回退菜单，恢复之前的对话和代码状态

•

"撤销那个"

：让 Claude 回退更改

•

/clear

：在不相关任务之间重置上下文

如果你在同一会话中纠正了 Claude 两次以上，上下文已经被失败的方法污染。运行

/clear

并用更具体的提示重新开始。

积极管理上下文

• 在任务之间频繁使用

/clear

重置上下文窗口

• 使用

/compact <instructions>

自定义压缩行为

• 使用

/btw

快速提问，答案不会进入对话历史

使用 Subagents 进行调查

将研究工作委托给 subagents，它们在独立的上下文中探索，保持主对话干净：

使用 subagents 调查我们的认证系统如何处理 token 刷新，

以及是否有现有的 OAuth 工具可以复用。

使用检查点回退

每次提示都会创建一个检查点。双击

Escape

或运行

/rewind

打开回退菜单。

恢复对话

使用

claude --continue

继续最近的会话，或

claude --resume

从列表中选择。用

/rename

给会话起描述性名称。

自动化和扩展

运行非交互模式

# 一次性查询

claude -p

"解释这个项目的用途"

# 结构化输出

claude -p

"列出所有 API 端点"

--output-format json

# 流式 JSON 输出

claude -p

"分析这个日志文件"

--output-format stream-json

运行多个 Claude 会话

•

Worktrees

：在隔离的 git 检出中运行独立的 CLI 会话

•

桌面应用

：可视化管理多个本地会话

•

Web 版 Claude Code

：在 Anthropic 托管的云基础设施上运行

•

Agent 团队

：自动协调多个会话

Writer/Reviewer 模式：

会话 A (编写者)

会话 B (审查者)

"实现 API 端点的速率限制器"

"审查 @src/middleware/rateLimiter.ts 中的速率限制器实现"

"根据审查反馈修复这些问题"

跨文件分发任务

for

file

in

$(

cat

files.txt);

do

claude -p

"将

$file

从 React 迁移到 Vue。返回 OK 或 FAIL。"

\

--allowedTools

"Edit,Bash(git commit *)"

done

使用 Auto 模式自主运行

claude --permission-mode auto -p

"修复所有 lint 错误"

常见失败模式

问题

解决方案

大杂烩会话

— 从一个任务跳到另一个不相关的任务

在不相关任务之间使用

/clear

反复纠正

— Claude 做错了，纠正后还是错

两次纠正失败后，

/clear

并写更好的初始提示

过度配置的 CLAUDE.md

— 文件太长，Claude 忽略一半

无情地删减，如果 Claude 已经能正确执行就删除该指令

信任但不验证

— Claude 产出看似合理的实现但不处理边界情况

始终提供验证（测试、脚本、截图）

无限探索

— 让 Claude "调查" 但没有限定范围

窄化调查范围或使用 subagents

培养你的直觉

这些模式不是一成不变的。它们是通用的起点，但不一定在每种情况下都是最优的。

有时你应该让上下文累积，因为你在深入一个复杂问题。有时你应该跳过规划，因为任务是探索性的。有时模糊的提示正好合适，因为你想看看 Claude 如何解读问题。

注意什么有效。当 Claude 产出优秀结果时，注意你做了什么。当 Claude 遇到困难时，问为什么。

随着时间推移，你会发展出任何指南都无法捕捉的直觉。

引用链接

[1]

How Claude Code works:

https://code.claude.com/en/how-claude-code-works

[2]

Extend Claude Code:

https://code.claude.com/en/features-overview

[3]

Common workflows:

https://code.claude.com/en/common-workflows