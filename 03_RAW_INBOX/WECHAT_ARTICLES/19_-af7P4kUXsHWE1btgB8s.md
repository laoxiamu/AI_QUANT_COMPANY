# 老码农的Vibe Coding：超能力七阶段Superpowers工作流完整图谱

**URL:** https://mp.weixin.qq.com/s/-af7P4kUXsHWE1btgB8shw

**字数:** 17910

---

PART 01

12.1 从「喊麦指挥」到「甩手掌柜」

你有没有过这种体验？

你：帮我实现这个功能...

AI：好的

你：不对，应该这样做...

AI：明白了

你：等等，这个bug还没修...

AI：我看看...

你：测试跑了吗？

AI：还没...

你：...

这就是「喊麦指挥」模式

——你需要一直盯着AI的工作，不停地给出指令，确认进度，就像一个监工。

问题是：

你很累

：要时刻关注AI在做什么

AI效率低

：每次都要等你的反馈才能继续

容易出错

：你可能会漏掉某些检查

有没有一种方式，让AI自动工作，你只需要验收结果？

这就是

Superpowers

要解决的问题。

///

PART 02

12.2 Superpowers是什么？

12.2.1 核心理念

Superpowers = 让AI自动触发工作流，无需人工喊麦

它不是一个具体的AI工具，而是一套

基于Skill的软件开发方法论

。

传统模式：

你 → AI → 你 → AI → 你 → AI → ... （你来我往，累死）

Superpowers模式：

你 → AI（自动工作流）→ 你（验收结果）→ 完成（爽死）

本质区别

：

维度

传统模式

Superpowers

你的角色

监工/指挥官

验收者

AI的行为

等待指令

自动执行

触发方式

人工喊麦

事件自动触发

工作流

碎片化

连续自动化

你的参与度

高（累）

低（爽）

12.2.2 什么是「Agentless」？

「Agentless」不是没有Agent，而是你不需要「喊」Agent工作。

传统Agent

：你告诉Agent做什么，什么时候做（你喊它才动）

Agentless

：AI根据上下文自动触发下一个工作流步骤（它自己知道该做什么）

Agent模式：

你：/subagent code-reviewer "审查代码"

你：/subagent tdd-guide "修复Bug"

你：/subagent architect "设计架构"

你：/subagent ...

（你在喊，Agent在动）

Agentless模式：

你：开始开发这个功能

（AI自动按顺序执行：brainstorming → plan → implement → review → test）

你：最后验收

（你在看，AI自己动）

12.2.3 Superpowers的来源

Superpowers最初由@obra开发，是一个开源的AI编程方法论项目：

GitHub

：obra/superpowers（开源）

支持平台

：Claude Code、OpenAI Codex、OpenCode、Cursor

安装方式

：一行命令即可安装

///

PART 03

12.3 七阶段完整链路

Superpowers定义了七阶段的自动化工作流：

┌─────────────────────────────────────────────────────────────┐

│                                                             │

│  1. brainstorming ──→ 2. worktree ──→ 3. writing-plans     │

│         ↓                   ↓                ↓              │

│     需求澄清            隔离工作区        任务拆解          │

│                                                             │

│  4. subagent-driven-development / executing-plans           │

│         ↓                                                  │

│     并行执行 + 两阶段审查                                   │

│                                                             │

│  5. test-driven-development ──→ 6. requesting-code-review  │

│         ↓                               ↓                   │

│     RED-GREEN-REFACTOR            按严重性报告              │

│                                                             │

│  7. finishing-a-development-branch                         │

│         ↓                                                  │

│     验证测试，提供合并/丢弃选项                             │

│                                                             │

└─────────────────────────────────────────────────────────────┘

每个阶段都是自动触发的，你只需要在关键节点确认。

///

PART 04

12.4 阶段详解

12.4.1 阶段1：brainstorming —— Socratic追问，需求澄清

目标

：在动手之前，彻底理解需求

问题场景

：

你：帮我实现一个用户登录功能

AI：（直接开始写代码）

...

AI：完成了

你：等等，登录方式是用户名还是手机号？

AI：啊，您没说明...

结果

：返工，浪费时间。

Brainstorming阶段的做法

：

你：帮我实现一个用户登录功能

AI（Brainstorming模式）：

"在开始之前，我需要澄清几个问题：

1. 登录方式

- 用户名+密码？

- 手机号+验证码？

- 邮箱+密码？

- SSO单点登录？

2. 认证方式

- JWT Token？

- Session？

- OAuth 2.0？

3. 安全要求

- 是否需要多因素认证？

- 密码强度要求？

- 登录失败锁定？

4. 用户体验

- "记住我"功能？

- 第三方登录（Google/GitHub）？

请确认以上需求，我会据此设计最佳实现方案。"

Socratic追问的核心

：

不是一口气问完所有问题，而是

基于你的回答继续追问

，直到完全理解需求。

你：用手机号登录

AI：好的，手机号登录。

追问1：验证码是短信还是邮件？

你：短信

AI：明白。

追问2：验证码有效期多久？（5分钟？10分钟？）

...

Brainstorming的Skill

：通常使用

brainstorming

Skill，定义追问策略和需求澄清流程。

12.4.2 阶段2：using-git-worktrees —— 隔离工作区，建立干净测试基线

目标

：在隔离的环境中工作，不污染主分支

问题场景

：

你：在main分支上开发新功能

AI：好的，开始写代码...

你：等等，要测试一下

AI：测试通过

你：看看main分支状态

AI：... 有20个未提交的修改，包括新功能和临时测试代码

结果

：混乱的分支，测试代码污染主分支。

Worktree阶段的做法

：

AI（自动执行）：

1. 创建新的git worktree

$ git worktree add /workspace/feature-login

2. 在新worktree中建立测试基线

$ cd /workspace/feature-login

$ git checkout -b feature/login

3. 运行现有测试，确认基线干净

$ npm test

✅ 所有测试通过

现在开始可以安心开发，不会影响main分支。

Git Worktree的好处

：

好处

说明

隔离开发

新功能在独立目录，不影响主代码

并行工作

可以同时在多个分支工作

干净基线

每个worktree都有独立的测试状态

快速切换

无需stash/unstash，切换即可

易于清理

完成即可删除worktree，不留痕迹

OpenCode中的Worktree集成

：

# 手动创建worktree

/opencode worktree create feature/login

# 列出所有worktree

/opencode worktree list

# 切换worktree

/opencode worktree switch feature/login

# 删除worktree

/opencode worktree remove feature/login

12.4.3 阶段3：writing-plans —— 拆解为2-5分钟可执行任务

目标

：把大任务拆成小任务，每个任务2-5分钟可完成

问题场景

：

你：帮我实现整个用户系统

AI：好的（开始埋头写代码）

...

2小时后

AI：完成了

你：等等，登录和注册是一起写的吗？

AI：是啊

你：不对，应该先写注册，再写登录，再写找回密码

AI：... 那要重写

结果

：架构混乱，返工。

Writing Plans阶段的做法

：

AI（自动规划）：

根据需求，创建了以下实施计划：

## 用户登录功能实施计划

### 阶段A：基础设施

- [ ] Task 1: 创建用户数据模型（2min）

- [ ] Task 2: 配置数据库连接（3min）

### 阶段B：用户注册

- [ ] Task 3: 实现注册API接口（4min）

- [ ] Task 4: 添加输入验证（2min）

- [ ] Task 5: 密码加密存储（3min）

### 阶段C：用户登录

- [ ] Task 6: 实现登录API接口（4min）

- [ ] Task 7: JWT Token生成（3min）

- [ ] Task 8: 登录中间件（2min）

### 阶段D：测试

- [ ] Task 9: 单元测试-注册（3min）

- [ ] Task 10: 单元测试-登录（3min）

- [ ] Task 11: 集成测试（5min）

每个任务都有：

- 具体要修改的文件

- 预期的结果

- 验收步骤

好任务的标准

：

标准

说明

示例

时间可控

2-5分钟完成

✅ "添加密码加密" / ❌ "完成整个登录系统"

结果明确

完成后有什么可验证的结果

✅ "用户表增加password_hash字段" / ❌ "改进用户体验"

可验收

有明确的验收步骤

✅ "运行test/login.spec.ts通过" / ❌ "确保正常工作"

独立

不依赖其他任务的结果

✅ "添加注册API" / ❌ "修复登录发现的问题"

12.4.4 阶段4：subagent-driven-development / executing-plans —— 并行执行+两阶段审查

目标

：并行执行任务，保证质量和效率

执行模式

：

┌──────────────────────────────────────────────────────────────┐

│  主Agent（规划+协调）                                        │

│       ↓                                                     │

│  并行分配给多个子Agent                                       │

│       ↓                                                     │

│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │

│  │Task 1  │  │Task 2  │  │Task 3  │  │Task 4  │        │

│  │Agent A │  │Agent B │  │Agent C │  │Agent D │        │

│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │

│       ↓             ↓             ↓             ↓            │

│  两阶段审查       两阶段审查     两阶段审查     两阶段审查    │

│  ①规范合规       ①规范合规      ①规范合规      ①规范合规    │

│  ②代码质量       ②代码质量      ②代码质量      ②代码质量    │

│       ↓             ↓             ↓             ↓            │

│  主Agent汇总 → 迭代修复 → 最终交付                       │

└──────────────────────────────────────────────────────────────┘

两阶段审查机制

：

第一阶段：规范合规性审查

检查清单：

□ 是否符合SKILL.md中定义的项目规范？

□ 是否遵循团队的编码风格？

□ 是否有硬编码的敏感信息？

□ 是否有未处理的错误边界？

第二阶段：代码质量审查

检查清单：

□ 代码逻辑是否正确？

□ 是否有潜在的bug？

□ 是否有性能问题？

□ 测试覆盖是否充分？

为什么是两阶段？

阶段

关注点

审查速度

失败影响

第一阶段

规范合规

快（模板检查）

低（可快速修复）

第二阶段

代码质量

慢（深度分析）

高（需要重构）

先快速过滤规范问题，再深度分析质量问题，效率最高。

12.4.5 阶段5：test-driven-development —— RED-GREEN-REFACTOR

目标

：用TDD方式保证代码质量

RED-GREEN-REFACTOR三步曲

：

┌────────────────────────────────────────────────────────────┐

│                                                            │

│   RED（红）                                               │

│   写一个失败的测试                                         │

│   你：「这个函数应该返回X」                                 │

│   AI：写测试，测试失败（因为函数还不存在）                   │

│   状态：❌ 测试失败                                        │

│                                                            │

│   GREEN（绿）                                             │

│   写最少的代码让测试通过                                    │

│   AI：写最简单的实现                                       │

│   状态：✅ 测试通过                                        │

│                                                            │

│   REFACTOR（重构）                                         │

│   重构代码，让它更好                                       │

│   AI：改善代码结构，提高可读性                              │

│   状态：✅ 测试仍然通过                                    │

│                                                            │

└────────────────────────────────────────────────────────────┘

为什么TDD重要？

没有TDD

有TDD

写完代码再测试

先写测试再写代码

测试可能遗漏

强制覆盖

后期发现bug

实时发现bug

代码难以重构

重构有信心

测试覆盖率低

测试覆盖率有保证

Superpowers中的TDD集成

：

# OpenCode中的TDD流程

/opencode tdd init     # 初始化TDD环境

/opencode tdd red      # 进入RED阶段

/opencode tdd green    # 进入GREEN阶段

/opencode tdd refactor # 进入REFACTOR阶段

/opencode tdd next     # 下一个任务继续TDD

12.4.6 阶段6：requesting-code-review —— 按严重性报告，关键问题阻塞

目标

：代码审查，按严重性分类问题

传统代码审查的问题

：

AI：审查完成，发现了以下问题：

- 缩进不一致

- 变量命名不够清晰

- SQL注入漏洞

- 忘记处理空值

- 逻辑错误

- ...

你：这么多问题，哪个最严重？

AI：都重要

你：...

结果

：没有重点，不知道从哪里开始修复。

按严重性报告

：

AI（代码审查报告）：

## 代码审查报告

### 🔴 阻塞问题（必须修复才能合并）

1. SQL注入漏洞 - src/auth/login.ts:45

- 直接拼接SQL参数

- 必须使用参数化查询

### 🟠 严重问题（应该修复）

2. 密码明文传输 - src/auth/api.ts:23

- 未使用HTTPS

- 敏感数据暴露风险

### 🟡 建议问题（可以后续修复）

3. 缺少错误处理 - src/utils/helper.ts:12

4. 日志记录不完整 - src/api/user.ts:8

5. 命名不规范 - src/auth/token.ts:34

### ✅ 通过项

- 代码结构清晰

- 逻辑正确

- 测试覆盖充分

---

⚠️ 阻塞问题必须修复后才能合并

严重性等级

：

等级

标签

说明

行为

P0

🔴 阻塞

必须修复

阻塞合并

P1

🟠 严重

应该修复

建议修复

P2

🟡 建议

可以后续

记录在案

P3

⚪ 低优

可忽略

可选改进

12.4.7 阶段7：finishing-a-development-branch —— 验证测试，提供合并/丢弃选项

目标

：完成开发，提供明确的下一步行动

工作流程

：

┌────────────────────────────────────────────────────────────┐

│                                                            │

│  AI自动执行：                                               │

│  1. 运行完整测试套件                                       │

│  2. 生成测试覆盖率报告                                      │

│  3. 列出所有变更                                           │

│  4. 检查是否满足合并条件                                    │

│                                                            │

│  输出结果：                                                 │

│                                                            │

│  ## 分支完成：feature/login                                │

│                                                            │

│  测试结果：✅ 全部通过（156个测试）                         │

│  覆盖率：✅ 85%                                            │

│  变更：+523行 / -89行                                      │

│                                                            │

│  ## 请选择下一步操作：                                       │

│                                                            │

│  [1] 合并到main分支                                        │

│  [2] 创建PR请求审查                                         │

│  [3] 丢弃此分支                                             │

│  [4] 继续开发                                               │

│                                                            │

└────────────────────────────────────────────────────────────┘

选项说明

：

选项

场景

合并到main

功能完成，测试通过，准备发布

创建PR

需要人工审查

丢弃分支

决定不做了，或另起新分支

继续开发

还有更多功能要做

///

PART 05

12.5 每阶段的Skill加载

12.5.1 Skill触发机制

Superpowers的每个阶段都有对应的Skill：

阶段

对应Skill

触发时机

brainstorming

brainstorming

用户描述需求时

using-git-worktrees

using-git-worktrees

开始实现前

writing-plans

writing-plans

需求澄清后

executing-plans

subagent-driven-development

计划创建后

test-driven-development

test-driven-development

开发过程中

requesting-code-review

requesting-code-review

代码完成后

finishing-a-development-branch

finishing-a-development-branch

审查通过后

12.5.2 Skill自动加载原理

用户输入：「帮我实现用户登录」

↓

检测到开发任务

↓

自动加载 brainstorming Skill

↓

执行Socratic追问

↓

需求澄清完成

↓

自动切换到下一个Skill

↓

...（自动流转）

你不需要手动告诉AI「现在用TDD」

，AI根据当前阶段自动加载对应的Skill。

///

PART 06

12.6 OpenCode中安装Superpowers

12.6.1 一键安装

在OpenCode中执行：

Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md

OpenCode会自动：

下载Superpowers配置

安装所有必需的Skill

配置Hook规则

验证安装完整性

12.6.2 验证安装

# 查看已安装的Superpowers Skill

/opencode skills list | grep superpower

# 预期输出：

# - superpower-brainstorming

# - superpower-git-worktrees

# - superpower-writing-plans

# - superpower-tdd

# - superpower-code-review

# - superpower-finish-branch

# 查看Hook配置

/opencode hooks list | grep superpower

# 预期输出：

# - superpower:pre-tool-use

# - superpower:post-tool-use

# - superpower:session-end

12.6.3 跨平台支持

Superpowers支持多个AI编程平台：

平台

安装命令

Claude Code

/plugin install superpowers@claude-plugins-official

OpenAI Codex CLI

/plugins

搜索 superpowers

OpenCode

Fetch URL（见上文）

Cursor

/add-plugin superpowers

///

PART 07

12.7 为什么这是「Agentless」的？

12.7.1 Agent vs Agentless的区别

维度

Agent模式

Agentless模式

触发方式

人工委托

事件自动触发

人工介入

每个步骤都需要

只在关键节点

工作流

碎片化

连续自动化

你的角色

指挥官

验收者

12.7.2 Superpowers的Agentless实现

传统Agent：

你：/subagent "tdd-guide" "帮我实现这个功能"

AI：好的（执行）

你：/subagent "code-reviewer" "审查代码"

AI：好的（执行）

你：/subagent "architect" "设计架构"

AI：好的（执行）

（你在喊，AI才动）

Superpowers（Agentless）：

你：开始实现这个功能

AI：brainstorming（自动开始需求澄清）

↓

需求澄清完成

↓（自动触发）

AI：using-git-worktrees（自动创建隔离环境）

↓

环境就绪

↓（自动触发）

AI：writing-plans（自动拆解任务）

↓

计划完成

↓（自动触发）

AI：subagent-driven-development（自动并行执行）

↓

开发完成

↓（自动触发）

...（后续阶段自动流转）

（AI自己知道下一步该做什么）

12.7.3 你什么时候需要介入？

虽然大部分流程是自动的，但你需要在这些节点做决策：

1. Brainstorming阶段

AI追问需求时 → 你需要回答

2. Plan审查时

AI生成计划后 → 你确认/修改计划

3. 阻塞问题时

代码审查发现P0问题 → 你决定如何处理

4. 分支完成时

AI提供合并选项 → 你选择下一步操作

5. 验收时

所有工作完成后 → 你最终验收

///

PART 08

12.8 与传统敏捷开发的对比

12.8.1 流程对比

维度

传统敏捷

Superpowers

迭代周期

2-4周（Sprint）

分钟级（每个任务）

反馈循环

Sprint Review

实时自动化

测试

Sprint结束统一测试

每个任务TDD

代码审查

PR时人工审查

自动化+关键节点人工

部署

Sprint结束部署

随时可部署

人工介入

每个环节都需要

只有关键节点

12.8.2 效率对比（假设场景）

场景：实现一个包含5个功能的用户系统

传统敏捷流程

：

Day 1：Sprint计划会议（4小时）

Day 1-10：开发（10天，每天8小时 = 80小时）

Day 5：发现需求理解错误，返工（16小时）

Day 10：开发完成

Day 11：测试（1天）

Day 12：代码审查（发现一堆问题）

Day 13-14：修复问题（2天）

Day 15：部署

总耗时：15天 = 大量人工投入

Superpowers流程

：

你：帮我实现这个用户系统

AI（Brainstorming）：追问需求（30分钟，你回答）

AI（Worktree）：创建隔离环境（5分钟）

AI（Plans）：生成任务计划（15分钟，你确认）

AI（并行开发）：实现5个功能（每功能15分钟 = 75分钟）

AI（TDD）：每个功能测试通过（自动）

AI（Review）：审查代码（自动，按严重性报告）

你：看审查报告，确认P0问题已修复

AI（Finish）：提供合并选项

总耗时：约2小时（你的介入：30分钟回答 + 15分钟确认）

效率提升：75%+人工时间节省

///

PART 09

12.9 实战：体验Superpowers完整流程

12.9.1 启动Superpowers

你：帮我实现一个博客评论功能

AI：

┌─────────────────────────────────────────────────────────────┐

│  🚀 Superpowers 已激活                                      │

│                                                             │

│  阶段 1/7：Brainstorming                                    │

│  正在澄清需求...                                            │

└─────────────────────────────────────────────────────────────┘

AI："在开始之前，我需要确认几个问题：

1. 评论的层级结构？

- 一级评论（直接评论文章）？

- 二级评论（回复其他评论）？

- 多级嵌套？

2. 评论的内容限制？

- 字数限制？

- 支持Markdown？

- 支持@提及？

请回答以上问题，我会据此设计最佳实现方案。"

12.9.2 需求澄清

你：

- 一级和二级评论

- 字数限制500字

- 支持Markdown

- 需要审核机制

AI：

"明白了，需求已记录：

✅ 一级评论

✅ 二级评论（回复）

✅ 500字限制

✅ Markdown支持

✅ 评论审核机制

进入下一阶段..."

12.9.3 创建工作区

AI：

┌─────────────────────────────────────────────────────────────┐

│  阶段 2/7：Using Git Worktrees                              │

│  正在创建隔离工作区...                                       │

└─────────────────────────────────────────────────────────────┘

$ git worktree add /workspace/feature-blog-comment

$ git checkout -b feature/blog-comment

$ npm test

✅ 基线测试通过（23个测试）

工作区已就绪，可以安全开发。

12.9.4 生成计划

AI：

┌─────────────────────────────────────────────────────────────┐

│  阶段 3/7：Writing Plans                                    │

│  正在拆解任务...                                            │

└─────────────────────────────────────────────────────────────┘

## 博客评论功能实施计划

### 阶段A：数据模型

- [ ] Task 1: 创建评论表（2min）

- [ ] Task 2: 创建评论回复表（2min）

### 阶段B：API开发

- [ ] Task 3: POST /comments（创建评论）（4min）

- [ ] Task 4: GET /comments/:articleId（获取评论）（3min）

- [ ] Task 5: POST /comments/:id/reply（回复评论）（4min）

### 阶段C：内容处理

- [ ] Task 6: Markdown渲染（3min）

- [ ] Task 7: 字数限制验证（2min）

### 阶段D：审核机制

- [ ] Task 8: 审核状态字段（2min）

- [ ] Task 9: 管理员审核API（3min）

### 阶段E：测试

- [ ] Task 10: 单元测试套件（10min）

共10个任务，预计总耗时：35分钟

[1] 确认计划，开始执行

[2] 修改计划

[3] 取消

12.9.5 执行开发

你：确认计划，开始执行

AI：

┌─────────────────────────────────────────────────────────────┐

│  阶段 4/7：Subagent-Driven Development                     │

│  正在并行执行任务...                                        │

│                                                             │

│  Task 1 → Agent-A                                          │

│  Task 2 → Agent-B                                          │

│  Task 3 → Agent-C                                          │

│  Task 4 → Agent-D                                          │

│  ...                                                       │

└─────────────────────────────────────────────────────────────┘

[并行执行中...]

✅ Task 1 完成（数据模型）

✅ Task 2 完成（回复表）

✅ Task 3 完成（评论API）

...

所有任务完成，进入下一阶段...

12.9.6 代码审查

AI：

┌─────────────────────────────────────────────────────────────┐

│  阶段 6/7：Code Review                                     │

│  正在审查代码...                                            │

└─────────────────────────────────────────────────────────────┘

## 代码审查报告

### 🔴 阻塞问题

1. XSS漏洞 - src/comments/api.ts:56

- 用户输入未转义直接渲染

- 必须使用DOMPurify净化

### 🟠 严重问题

无

### 🟡 建议问题

1. 缺少评论数缓存 - src/comments/service.ts:12

2. 日志记录不完整 - src/comments/api.ts:8

✅ 通过项：代码结构、逻辑正确、测试覆盖85%

⚠️ 请修复阻塞问题后继续

12.9.7 完成分支

你：修复XSS漏洞

AI：✅ XSS漏洞已修复

✅ 重新审查通过

AI：

┌─────────────────────────────────────────────────────────────┐

│  阶段 7/7：Finishing Development Branch                    │

└─────────────────────────────────────────────────────────────┘

## 分支完成：feature/blog-comment

测试结果：✅ 全部通过（89个测试）

覆盖率：✅ 87%

变更：+892行 / -124行

## 请选择下一步操作：

[1] 合并到main分支

[2] 创建PR请求审查

[3] 丢弃此分支

[4] 继续开发

你：1

AI：✅ 已合并到main分支

📦 部署就绪

///

PART 10

12.10 本章小结

核心要点

Superpowers核心理念

：让AI自动触发工作流，无需人工喊麦

七阶段完整链路

：

brainstorming → Socratic追问，需求澄清

using-git-worktrees → 隔离工作区

writing-plans → 2-5分钟可执行任务拆解

subagent-driven-development → 并行执行+两阶段审查

test-driven-development → RED-GREEN-REFACTOR

requesting-code-review → 按严重性报告

finishing-a-development-branch → 验证+合并选项

Agentless的本质

：AI根据上下文自动触发下一个工作流步骤

Skill自动加载

：每个阶段对应特定的Skill，自动加载和切换

安装方式

：

Fetch and follow instructions from URL

效率提升

：75%+人工时间节省，从15天到2小时

实践建议

✅ 安装Superpowers后，先在小项目上体验完整流程

✅ 熟悉7个阶段的自动流转

✅ 学会在关键节点做决策（确认计划、修复P0、选择合并）

✅ 理解Skill触发机制，知道什么时候该介入

❌ 不要期望100%自动化，关键节点仍需要你决策

❌ 不要跳过Brainstorming阶段，需求澄清最重要

❌ 不要忽略TDD，质量是开发出来的不是测出来的

下一步

Superpowers让你从「喊麦指挥」变成「甩手掌柜」，但每个阶段用对模型才能真正省钱。

下一章：

Token经济学——月薪3000怎么用出30000的AI

，教你如何选择对的模型、对的时机，省下70%的AI成本。

老码农的Vibe Coding：

老码农的Vibe Coding：我让AI替我写代码，三小时完成了一天的活

老码农的Vibe Coding：手写代码 → Copilot → Vibe Coding

老码农的Vibe Coding：Plan vs Build 先想好再动手的智慧

Vibe Coding必备：

《Prompt模板库》同样的AI，为什么别人用出10倍效率？

Vibe Coding必备！这份OpenCode速查手册，3分钟掌握核心技能

THANKS FOR READING

🦐 龙虾 · OpenClaw 技术分享