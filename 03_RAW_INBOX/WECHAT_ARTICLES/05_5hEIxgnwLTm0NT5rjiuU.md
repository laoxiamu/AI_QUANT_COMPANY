# Claude Code 动态工作流详解

**URL:** https://mp.weixin.qq.com/s/5hEIxgnwLTm0NT5rjiuUcg

**字数:** 1551

---

之前讨论过Claude Code的SubAgent和AgentTeams工作模式。感兴趣的小伙伴可以前往阅读：

Claude Code工作模式深度拆解

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/mmbiz_png/gibJtAFvA3oku8795FDC6IdZkNVtJKic0ibvSjpYw9AJh3wLicT2xGOY9aicjEea7UGSnG5ac7ML1ticRjxGUfSaCCwVJ0Ym1q7HXnmobFiaA7qz1U/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=0)

SubAgent是从MainAgent中派生的轻量级Work进程。SubAgent执行特定的任务并汇报结果给MainAgent。SubAgent之间无法直接通信，所有Agent的结果都通过一个上下文窗口进行路由，

因此MainAgent会成为整个流程编排的瓶颈

。

AgentTeams是通过多个Agent通过共享Task列表进行协作，团队成员之间可以相互发送消息。每个AgentTeams的团队成员不建议超过5个，并且会话中断后无法继续运行，因此需要预先设计编排流程。

动态工作流是什么

动态工作流是SubAgent和AgentTeams之外的一种工作模式。动态工作流的完整编排逻辑在 JS 脚本中执行，不再完全塞进对话上下文；但第一次触发时 Claude Code 会展示编排结果，也就是运行的计划需要用户确认。

![image](https://wsrv.nl/?url=https://mmbiz.qpic.cn/sz_mmbiz_png/gibJtAFvA3ok3Wyhzuo6AntEaYude5xnzibsTmyxXibQzLj78ZcFYibIHxSjN4WnA2g9c3ibOiaP8KCBibvfTalDJAwJxVb4fZuVE5ex09rG7k3MJo/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)

对用户来说，只需要描述任务目标，Claude Code决定如何拆分任务、生成多少个SubAgent、如何验证结果以及向用户反馈哪些信息。工作流的编排逻辑直接从LLM的上下文转移到可执行代码中。

动态工作流优势

智能体规模：每个动态工作流最多可以同时运行16个子Agent、理论总量不超过1000个Agent；SubAgent 编排适合少量并行任务，数量变多后 MainAgent 容易成为上下文和调度瓶颈。

对抗性检查：Agent能够从独立的角度解决问题，Agent可以尝试反驳其他Agent的结果，功能不断迭代直到结果稳定。相比之下，SubAgent只能汇报结果，AgentTeams虽然可以协作，但是不进行对抗验证。

中断可恢复：动态工作流可以保存任务的进度。中断的任务可以从中断处继续执行；AgentTeams则会直接终止会话。

自动编排：用户只需要描述目标，Claude就会决定如何分配工作、生成多少SubAgent以及如何验证结果。

最佳实践

先从小规模任务入手，评估Token适用情况，然后再考虑推广。因为工作流消耗的Token远远高于普通会话。

启动自动模式，让Claude决定何时使用动态工作流，何时使用普通对话即可。

会话级别可以通过ultracode指令控制Claude启动 workflow模式，并进入xhigh模式。

第一次触发时要审查执行计划。定义不清的范围会不必要地扩散到多个 agent。

企业级套餐默认关闭动态工作流的功能，需要管理员启用。