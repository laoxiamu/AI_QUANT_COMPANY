# 从"人肉闹钟"到"AI Worker"：Routine 是 Agent 的进阶（2）

**URL:** https://mp.weixin.qq.com/s/VsGw3wa7iLQisj5I8jUfvw

**字数:** 3512

---

上

一篇讲了 Routine 的概念和一套内容研究的实战流程。这一篇继续讲两个更具体的场景：CI 失败处理和客户运营。以及一个判断标准——什么样的工作值得变成 Routine，什么样的不适合。

04｜Routine 实战：CI 失败 → 修复 / 阻塞

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/aDccGUCibpAk1ibzbGMxJk9Ow1xcIHEqwbmSkAGZBib3icaTEJZd0GG572LLGAwp4NRTXiaXiaxoqMsmRbSN4LbIL6nEGN6Z0yTLsvXUQ5ZvCm4VM/640?wx_fmt=jpeg&watermark=1#imgIndex=0)

开发最烦的不是 CI 挂了。是 CI 挂了之后，你还要判断它是真 bug、flaky、外部服务抽风，还是 agent 刚刚改坏了什么。

如果只是 Prompt：

"帮我修这个 CI。" Agent 直接开改，很容易把 flaky test 当真 bug，把 dependency outage 改成奇怪 workaround，或者为了让测试过，把断言改松。

如果加上 Context：

Agent 看到 PR diff、失败 job log、repo 规则、最近一次相关修改。

如果加上 Memory / Skills：

Agent 知道这个 repo 的测试命令、常见 flaky、哪些断言不能改松。

但这些还不等于 Routine。Routine 是：失败触发后自动分类。flaky 就 retry 或标记；external / credential 就 block；明确代码 bug 才 patch；最后把证据、命令、结果写回 PR 或 Kanban。

具体流程：

第一步：触发。

GitHub check failed。Agent 拉 PR diff、失败 job log、repo 里的 AGENTS.md / CLAUDE.md、测试命令和最近一次相关修改。

第二步：分类。

先判断失败类型：test、lint、typecheck、build、external service、flaky。

flaky →

retry 一次或者标记 flaky，不改代码

external service / credential →

comment 说明证据，然后 block。不能让 agent 为了过 CI 去改认证逻辑

明确代码 bug →

在 worktree 里修。先跑最小相关测试，再跑 repo 定义的必要检查

第三步：修复。

如果是代码 bug，在 worktree 里 patch。跑 targeted test，跑 required lint/typecheck。

第四步：写回。

把 changed files、commands、结果、剩余风险写回 PR 或 Kanban。

第五步：review gate。

配置、auth、billing、deploy、schema migration 这些文件，一律不能自动 merge。即使测试过了，也要 review-required。

这套东西的价值不是"AI 会修 CI"。会修只是第一层。更重要的是它知道

什么时候不该修

。

一人公司尤其需要这个。因为你没有专门的 reviewer 帮你兜底。如果 agent 产 PR 的速度比你 review 的速度快，系统很快会变成一堆半可信改动。Routine 里的 block / review-required，就是为了防止"自动化越多，人越不敢合"的状态。

05｜Routine 实战：客户运营 / 预订处理

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_jpg/aDccGUCibpAkrdDUzhyn4ucjNDOvqeNdcBa2KpWiajKS2exQtABXh8rGsmTWkgGmB5MQicxVkcbqk2U7icGfobzcJjtIwoMtWeugyEZb2Oyeeyw/640?wx_fmt=jpeg&watermark=1#imgIndex=1)

第三个是客户 ops，这也是实操过程中体会最深的场景。

比如设备租赁、场地预订、课程 booking、维修安排、退款咨询。客户发来一封邮件或者表单消息，里面有日期、地址、设备型号、人数、付款状态、特殊要求。你希望 AI 帮你处理，但你不希望它乱承诺库存、乱改价格、乱答应退款。

如果只是 Prompt：

"帮我回这封客户邮件。"

如果加上 Context：

AI 看到客户消息、订单、日历、库存、付款状态。

如果加上 Memory / Skills：

AI 知道回复语气、退款规则、不能承诺未确认库存。

如果加上 Harness：

AI 只允许 draft，不允许自动发送，不允许改价格。

但 Routine 是：邮件进来后自动抽取事实、查状态、标风险、生成内部 summary 和 reply draft，遇到 refund / discount / availability 冲突就停下来找人。

具体流程：

第一步：触发。

Booking 邮件或表单进来。Router 判断它属于 customer ops。

第二步：抽取。

抽取结构化信息：客户是谁、要什么、时间窗口、地点、数量、是否付款、是否有冲突、缺什么信息。

第三步：查状态。

查日历有没有冲突、库存是否可能不足、订单状态是否存在、客户之前有没有相关沟通。查不到就标 unknown，不要补脑。

第四步：生成两样东西。

内部 ops summary：

给人看，重点是事实和风险。比如"日期缺失""库存未确认""客户要求超出标准范围""需要人工确认押金"。

Reply draft：

给客户看，但只能承诺已经被系统确认的东西。没有确认库存，就只能说"我先帮你确认 availability"，不能说"没问题"。没有确认价格，就不能自己给 discount。

第五步：review gate。

涉及 refund、damage、late fee、特殊承诺，一律 review-required。

这个 Routine 听起来不酷，但很值钱。因为一人公司的日常工作，大量时间不是花在"战略判断"，而是花在反复整理事实、查状态、写差不多的回复、提醒自己别漏掉风险点。AI 很适合接这部分，但前提是你给它边界。

没有边界，AI 客服很危险。有边界，它就是一个很好的 ops assistant。

06｜什么样的工作值得变成 Routine

Jason 给出了三个判断条件：

第一，它是不是反复出现。

同一类事情出现第三次，而且每次你都要重新解释背景，那就值得写下来。

第二，它能不能验证。

能跑测试、lint、content-lint、schema、grep、截图、日志检查，或者至少能用 checklist 验收，就适合让 agent 多做一点。

第三，它失败后能不能回流。

失败不是一句"抱歉我没做好"，而是能变成 fix task、block reason、缺失字段、待人工确认项。

反过来，高风险资金操作、法律承诺、复杂客户承诺、无法验证的开放式战略判断，不适合一开始就 routine 化。

至少不要自动执行到最后一步。

写在最后

Routine 不是自动化一切，而是固定那些反复出现的判断。

对个人 AI 用户来说，这套东西可能比"哪个模型更强"更快产生差距。因为模型能力会继续变便宜，真正稀缺的是你能不能把自己的工作拆清楚：

哪些判断可以交给 routine，哪些必须留给人

哪些结果能机器验收，哪些只能人工 review

哪些知识要写回 KB，哪些只是一次性聊天

下一阶段不是 prompt library 消失，而是 prompt library 不够了。

Prompt library 解决"这次怎么问"。Memory / skill library 解决"下次别忘什么"。Routine library 解决"每次 X 发生，系统怎么稳定处理"。

真正拉开差距的，不是谁收藏了更多 prompt，而是谁把自己的重复工作拆成了可运行的 routine。