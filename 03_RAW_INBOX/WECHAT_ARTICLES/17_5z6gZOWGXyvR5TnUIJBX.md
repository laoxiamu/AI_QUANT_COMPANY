# 从"人肉闹钟"到"AI Worker"：Routine 是 Agent 的进阶（1）

**URL:** https://mp.weixin.qq.com/s/5z6gZOWGXyvR5TnUIJBXxg

**字数:** 3776

---

你有

没有过这种经历？

让 AI 处理一件事，它做到一半，来一句"如果你需要，我可以继续 xxxx"。然后你盯着屏幕，等了两秒，回复"继续"。过一会儿，它又问一句"要不要跑一下测试？"你又回复"跑"。再过一会儿，它写完草稿，问你"要不要发布？"你回复"先别发，给我看看"。

结果你变成了什么？不是 human-in-the-loop，而是 human-as-cron。每隔一会儿回一句"继续""可以""跑一下"。

模型并不懒，它有时候已经做完了 70% 的判断——知道下一步该查资料、建任务、跑测试、写 draft、或者停下来找人确认。但最后它还是把球踢回来，问一句"要不要继续"。

真正有用的人机协作，不是让人每一步都点头。人应该卡在少数真正需要判断的位置：方向选择、公开发布、资金操作、生产环境、客户承诺。其他能按规则推进的步骤，就应该自己推进。

这就引出了一个很多人还没认真想的概念：Agent Routine。

01｜Agent 的发展层次：从"怎么问"到"怎么跑"

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/aDccGUCibpAlapEMBeCoBW601pQy9ssUhibXoDUnnleL1YI1Aol9rlhS3Gz5tEb5NibGHQ3AaDBhgRWLicJjBT8ib01ZsylrNvTELicGLI8jc2h6s/640?wx_fmt=jpeg&watermark=1#imgIndex=0)

Agentic AI 这段时间的演进，其实是一层层往外扩的。

第一层：Prompt Engineering。

重点是"怎么问"。你告诉 AI 你想要什么，它给出一个结果。一次性的、对话式的，用完就散。

第二层：Context Engineering。

重点变成"模型应该看到什么"。你给它加载更多背景信息——历史记录、相关文件、知识库。它给出的结果更精准。

第三层：Agent Harness。

工具权限、文件系统、终端、浏览器、memory、skills、review gate。你给它接入工具，让它能动手干活。但本质上还是一次性的对话，只是工具更多了。

第四层：Memory / KB / Skills。

解决下次别从零开始的问题。模型记住了你的偏好、项目规则、常见失败。下次遇到类似问题，少犯错。

这些层都对，但如果你高频使用 AI，会发现还有一层没被讲清楚：

同一类工作反复发生时，它到底应该怎么被稳定处理？

这就是 Routine 的位置。

Prompt 解决启动问题。Context 解决现场信息问题。Memory 减少重复犯错。Routine 减少重复调度。

很多人把这几层混在一起，一谈 Routine 就理解成 prompt template、memory、workflow automation。其实都不是。

Routine 不是"让 AI 记住"，而是定义同类工作怎么跑——

从哪里开始、按什么顺序推进、用什么检查结果、把状态写回哪里、遇到什么情况必须停。

02｜Routine 的结构长什么样

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/aDccGUCibpAm90pfuPWCicWF9zhJ0zj6XTfxWHY0QaErfjiaibWfU3mRFia5cfiaVM2wR49IymX26SVeOJB7pBojFPdiaFMicNC3iaoqBU84NQc08W6Y/640?wx_fmt=jpeg&watermark=1#imgIndex=1)

Jason 把 Routine 拆成了 8 个部分，不是理论上的拆分，而是实际使用下来，每个部分都有明确的用途。

trigger：

什么事件触发——Telegram 收到消息、GitHub check 失败、cron 定时任务、手动触发。

route：

归到哪个账号、topic、workspace、assignee。

context：

必须加载哪些知识库、历史记录、repo 规则、客户状态。

contract：

预期产出、验收标准、边界、什么情况必须找人。

tools：

能用哪些工具，哪些动作永远不能自动做。

verification：

测试、lint、schema 检查、grep、截图、日志——能机器检查的，不要靠 AI 自己说"我确认了"。

state：

结果写回哪里——issue 评论、Google Doc、知识库、任务看板。

recovery：

检查失败怎么建修复任务，缺上下文的时候什么时候 block。

这套结构看起来偏工程，但对个人用户更有价值。因为个人和一人公司没有 PM、QA、ops、工程经理给你兜底。AI 一旦开始多线程干活，最先爆掉的不是模型能力，而是你的注意力。

Routine 不是为了把人拿掉，而是别让人做低信息量的确认。

03｜Routine 实战：Link → KB → Draft（内容研究流程）

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/aDccGUCibpAm6NhD9oIDgfjQsicCGia04b8eSsMibKD2wbQ0USU0iawNaA5AhUCb52fDwkmAUgN9I4eboo023F7rCNNIrDib3UfDjk6ZPzuGYbg5Y/640?wx_fmt=jpeg&watermark=1#imgIndex=2)

这是最常见的场景。你在聊天窗口里丢一个 X 链接、GitHub repo、论文、博客，想让 AI 帮你研究。

如果只是 Prompt，这件事是："帮我总结这个链接。"

如果加上 Context，AI 会看到原帖、thread、引用链接、图片、repo README。

如果加上 Memory / Skills，AI 会知道你的写作风格、public-safe 规则、content-lint 要跑、内部项目名不能暴露。

但这些还不等于 Routine。

Routine 是：只要固定 topic 收到 URL，系统就知道先抓 source、再标 claim、再写 KB、再生成 draft、再跑 lint、再创建 Google Doc，最后停在 review-required。

具体流程是这样的：

第一步：触发和路由。

你把链接发到固定 topic。Router 先判断这是内容研究，不是交易、工程或客户 ops。然后创建 research task，带上 source_url、目标账号、public-safe 边界和写作风格。

第二步：拿 source。

AI 的第一步不是写文章，而是拿原始素材。原帖、thread、引用链接、图片、视频、repo README，能抓多少抓多少。拿不到就标 source incomplete，不要假装完整。

第三步：写 KB。

关键 claim 要分层：source 里明确说的、你推出来的、没验证的。这个区分很重要。AI 最容易把"合理推断"打磨成"确定事实"。

第四步：生成 draft。

Writer 只基于 KB 生成角度和正文。写完跑 content-lint，再 grep 内部编辑残留和内部项目名。最后创建 Google Doc，block as review-required。

人的位置很清楚。

你不需要每一步回复"继续"。你只在两个 gate 上做判断：

source 不完整要不要继续写

draft 能不能发布

这比"帮我总结一下"慢一点，但长期看更省心。因为知识写回去了，下次写同一主题不会又从零开始。

这个 routine 的 contract 很短：

触发：固定 topic 收到 URL

验证：source 已捕获或标为不完整；claim 区分来源/推断/未验证；KB 已保存；draft 只用 KB 支持的 claim；content-lint 通过

review gate：公开草稿停在 Google Doc review；不确定的 claim 保留标记，不被磨掉

写在最后（上篇）

很多人用 AI，以为模型越强越好。其实模型能力会越来越便宜，真正稀缺的是你能不能把自己的工作拆清楚。

Prompt 是入口。Context 是现场。Memory 是经验。Harness 是工作环境。Routine 是持续工作的单元。

如果你的 agent 每做完一步都问"如果你需要，我可以继续"，那它还是聊天助手。

如果它能按 contract 自己推进、验证、写回状态，只有碰到真正的 gate 才找你，那它才开始像一个 worker。

下篇会讲两个更具体的 Routine：CI 失败处理和客户运营。以及一个判断标准——什么样的工作值得变成 Routine，什么样的不适合。