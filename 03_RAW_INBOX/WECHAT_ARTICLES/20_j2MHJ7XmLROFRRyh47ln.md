# Claude 官方 Prompt 工程完全指南：从 Claude Opus 4.8 行为特征到 Agent 系统全栈调校

**URL:** https://mp.weixin.qq.com/s/j2MHJ7XmLROFRRyh47lnyw

**字数:** 21518

---

Anthropic 官方 Prompt 工程文档完整精读。从 Claude Opus 4.8 的 11 个行为特征，到通用四原则、输出控制、工具调用、Thinking 机制、Agent 系统 12 个调校维度，再到迁移指南——一篇覆盖全部知识点。

前言

这份文档不只是"写 prompt 的技巧"。它是 Claude 最新模型的行为说明书

Anthropic 维护了一份 Claude 提示词最佳实践文档（

platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

），覆盖从

Claude Opus 4.8 到 Sonnet 4.6、Haiku 4.5

的全系模型。这不是泛泛的 prompt 鸡汤。是 API 级的模型行为说明书：effort 参数怎么选、adaptive thinking 怎么触发、tool use 什么时候该推一把、Agent 长线任务怎么管理状态，每个结论背后都有内部评测数据支撑。

我通读了两遍，按原文结构完整整理了所有知识点。文章很长。因为源文档本身就覆盖了 40 多个技术点。说白了，这不是一篇通勤读物，是让你用到时回来查的手册。

📄 全文大纲

一、Claude Opus 4.8 模型行为全解

11 个行为特征：回复长度自适应、Effort/Thinking 调校、工具调用倾向、进度更新、字面指令遵循、语气风格、子代理控制、前端默认风格、交互式 Coding token 行为、Code Review 场景、Computer Use

二、通用原则与输出控制

7 条通用原则：清晰直接、给上下文、示例、XML 标签、角色设定、长上下文、模型自认知。5 项输出控制：沟通风格、格式控制四法、LaTeX、文档创建、prefilled responses 迁移

三、工具调用：触发、并行与双向节制

建议 vs 执行界限、默认行动 prompt、保守模式 prompt、并行工具调用最大化、串行模式、旧版 overtrigger 警告

四、Thinking 与推理机制

Overthinking 问题与解法、Adaptive Thinking 机制详解、从 extended thinking 迁移指南、实用技巧 4 条

五、Agent 系统全栈调校

12 个调校维度：长线推理、Context Awareness、多 Context Window 工作流（6 条建议）、状态管理、安全边界分层、研究收集、Subagent 编排、Prompt Chaining、临时文件清理、过度工程化防范、测试硬编码、幻觉最小化

附：专项能力 + 迁移指南

视觉能力提升技巧、前端设计美学引导、Claude 4.6 迁移要点、Sonnet 4.5→4.6 迁移对照

1

Claude Opus 4.8 模型行为全解

文档第一部分专门讲 Claude Opus 4.8 的行为特征。Claude Opus 4.8 在长线 Agent 任务、知识工作、视觉和记忆任务上有突出优势，对现有 Opus 4.7 的 prompt 兼容性很好。但有几个行为变化需要主动调校。

① 回复长度自适应。

Claude Opus 4.8 会根据任务复杂度自动校准回复长度。简单查询回一句话，开放式分析可能回好几页。如果你的产品依赖固定风格或长度，需要在 prompt 里明确约束。正向示例（展示想要的简洁程度）比负面指令效果好得多。

原文

Provide concise, focused responses. Skip non-essential context, and keep examples minimal.

中文对照

提供简洁、聚焦的回复。跳过非必要上下文，示例保持最短。

② Effort 与 Thinking 调校。

Claude Opus 4.8 的

effort

参数比以往任何 Opus 版本都重要。五个级别：

max

（某些场景有收益但可能 diminishing returns 加 overthinking）、

xhigh

（coding 和 agentic 场景最佳起点）、

high

（大多数 intelligence-sensitive 场景的最低保底）、

medium

（成本敏感场景）、

low

（短任务、延迟敏感、非智力密集型）。重要提醒：Claude Opus 4.8 默认不开 thinking——必须显式设置

thinking: {type: "adaptive"}

才启用。在

max

或

xhigh

effort 下，建议 max_tokens 至少设 64k——模型和子代理需要思考空间。

如果 prompt 很复杂导致 adaptive thinking 触发过于频繁，可以加引导：

原文

Thinking adds latency and should only be used when it will meaningfully improve answer quality — typically for problems that require multi-step reasoning. When in doubt, respond directly.

中文对照

Thinking 会增加延迟，仅在能实质提升回答质量时使用——通常是需要多步推理的问题。不确定时直接回复。

反过来，如果在

medium

effort 下推理太浅，首选调高 effort，再考虑用 prompt 引导。

③ 工具调用倾向变化。

Claude Opus 4.8 倾向于先推理再调用工具，而不是立刻动手。这在大多数情况下产出更好——但如果需要更多工具使用，提高 effort（

high

或

xhigh

）能在知识工作和 agentic search/coding 场景中明显增加工具使用。也可以在 prompt 里明确告诉模型什么时候该用什么工具——比如发现模型不用你的 web search 工具时，解释清楚为什么该用、怎么用。

④ 用户可见的进度更新。

Claude Opus 4.8 在长 agent 任务中会主动、高质量地汇报进度。如果你之前加了很多脚手架代码强制模型输出中间状态（如"每 3 次工具调用总结一次进度"），可以试试删掉——Claude Opus 4.8 自己就能做好。如果更新频率或内容不符合预期，在 prompt 里描述想要什么样的更新，给示例。

⑤ 更字面的指令遵循。

Claude Opus 4.8 对 prompt 做字面理解和显式遵循——尤其在低 effort 下。它不会自动把一条指令从 A 推广到 B，也不会推断你没提的需求。这对 API 场景（结构化提取、pipeline、需要可预测行为）是好事：精准、少折腾。但如果你需要 Claude 把一条规则应用到所有场景，必须明确说范围——比如：

原文

Apply this formatting to every section, not just the first one.

中文对照

将此格式应用到所有章节，不只是第一个。

⑥ 语气和写作风格。

Claude Opus 4.8 倾向直接、有态度的文字风格，最少化"确认型"措辞（如"I hope this helps"），emoji 使用克制。如果产品需要更温暖的语气，加：

原文

Use a warm, collaborative tone. Acknowledge the user's framing before answering.

中文对照

使用温暖、协作的语气。在回答前先认可用户的提问框架。

⑦ 子代理生成控制。

Claude Opus 4.8 默认 spawn 更少子代理——但这个行为可通过 prompt 调整。给明确指引：

原文

Do not spawn a subagent for work you can complete directly in a single response. Spawn multiple subagents in the same turn when fanning out across items or reading multiple files.

中文对照

能直接在单次回复中完成的工作不要 spawn 子代理。跨条目展开或读取多个文件时，在同一轮中 spawn 多个子代理。

⑧ 设计和前端默认风格。

Claude Opus 4.8 有很强的默认设计直觉——暖奶油/米白背景（~

#F4F1EA

）、衬线标题字体（Georgia、Fraunces、Playfair）、斜体强调、赤陶/琥珀色 accent。这个风格对编辑类、酒店、作品集很合适，但对仪表盘、开发者工具、金融、医疗、企业应用会不搭。通用指令（"不要用奶油色"、"做得干净简约"）通常只会让模型切到另一个固定调色板而非产生多样性。

两种可靠解法：一是给具体替代方案——指定色板、字体、布局约束（文档给了一个完整的冷色调单色系 landing page prompt 示例，含 5 个十六进制色值、圆角规格、排版要求）；二是让模型先在构建前提出 4 个不同视觉方向让用户选，再实现被选中的方向。另外，Claude Opus 4.8 比旧模型更不需要那套"anti-AI-slob"长 prompt——它自带更强的创意判断力。简化版的前端美学引导：

原文

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white or dark backgrounds), predictable layouts and component patterns.

中文对照

绝不使用通用 AI 审美：烂大街的字体家族（Inter、Roboto、Arial、系统字体）、老套的配色方案（特别是白底或黑底上的紫色渐变）、可预测的布局和组件模式。

⑨ 交互式 Coding 产品的 token 行为。

Claude Opus 4.8 在交互式（多轮用户对话）和自主式（单轮、异步 agent）coding 场景中的 token 使用和行为不同。交互式场景下它会在每次用户回复后做更多推理，token 消耗更大但长线连贯性、指令遵循和 coding 能力更强。要兼顾效果和效率：用

xhigh

或

high

effort、加 auto mode 减少人工交互次数、在第一轮就把任务描述清楚。模糊或不完整的 prompt 分多轮给，会相对降低 token 效率和效果。

⑩ Code Review 场景。

Claude Opus 4.8 找 bug 的能力比旧模型有实质提升，内部评测中召回率和精确率都更高。但如果你的 code review harness 是为旧模型调的，可能看到召回率下降——这通常是 harness 效应而非能力退化。原因是 Claude Opus 4.8 更忠实地遵守了"只报严重问题"、"保守一点"这类指令：它同样仔细审查了代码、找到了 bug，但把低于你设定的 severity bar 的发现压住没报。精确率通常上升，但测量到的召回率可能下降。

两种 prompt 策略，效果截然不同：

❌ 模糊定性（召回率下降）

✅ 具体标准（精度 + 召回兼顾）

Only report high-severity issues. Be conservative and don't nitpick.

Report any bugs that could cause incorrect behavior, a test failure, or a misleading result; only omit nits like pure style or naming preferences.

只报严重问题。保守一点，不要吹毛求疵。

报告任何可能导致错误行为、测试失败或误导结果的 bug；只忽略纯风格或命名偏好这类问题。

效果差异：

左栏用"high-severity""conservative"等主观词，新模型会把大量中等严重度的真实 bug 压住不报（精确率↑ 但召回率↓）。右栏给出可操作的客观边界——"会引发错误行为/测试失败/误导结果"——模型能准确判断哪些该报。

⑪ Computer Use。

Claude Opus 4.8 的 computer use 能力支持最高 2576px / 3.75MP 分辨率。内部测试显示 1080p 是性能和成本的最优平衡点。成本敏感场景可降到 720p 或 1366×768。Effort 参数也可以用来调校 computer use 行为——建议自己跑测试找到最优组合。

PYTHON · Claude Opus 4.8 标准配置（xhigh effort + adaptive thinking）

import anthropic

client = anthropic.Anthropic()

response = client.messages.create(

model="claude-opus-4-8",

max_tokens=64000,  # 给 thinking 和子代理留足空间

thinking={"type": "adaptive"},

output_config={"effort": "xhigh"},

system="You are an expert software engineer.",

messages=[{

"role": "user",

"content": "Build a REST API for..."

}]

)

2

通用原则与输出控制

这部分是适用于所有 Claude 模型的基础技法，加上输出格式的完整控制手段。

清晰直接。

Claude 像一位聪明但刚入职的同事——不了解你的习惯和默认值。Golden rule：把 prompt 给一个不了解背景的同事看，他要是困惑，Claude 也会。要具体说明输出格式和约束，顺序敏感时用编号列表。

给上下文而非只给指令。

不只说"不要做什么"，而是解释为什么——Claude 能从原因推导出怎么做，这比死记规则效果好。我实际验证过：把否定式全改成正向描述加原因后，输出一致性明显提升。

❌ 效果不稳定

✅ 效果稳定

NEVER use ellipses

Your response will be read aloud by a TTS engine, so never use ellipses since it won't know how to pronounce them.

绝不使用省略号。

你的回复将被 TTS 引擎朗读，所以不要使用省略号，因为它不知道如何发音。

效果差异：

左侧只给了规则，模型不知道为什么；右侧解释了原因（TTS朗读），模型自动泛化到其他类似场景。后者输出一致性明显更高。

用示例。

3-5 个 few-shot 示例仍然是最可靠的格式/语气/结构控制手段。示例要贴近实际场景、覆盖边界情况、用

<example>

标签包裹（多个示例再套

<examples>

）。也可以让 Claude 评估你自己的示例是否足够多样，或基于初始集生成更多。

XML 标签结构化。

当 prompt 混合了指令、背景、示例、输入数据时，用

<instructions>

、

<context>

、

<input>

包裹，减少歧义。命名一致、嵌套有层级。

给 Claude 一个角色。

在 system prompt 里设角色，哪怕只有一句话也有差别。

原文

You are a helpful coding assistant specializing in Python.

中文对照

你是专注于 Python 的编程助手。

长上下文提示。

处理 20k+ token 输入时有三个关键策略：① 把长文档和数据放在 prompt 顶部，查询和指令放在末尾——测试表明查询放末尾能提升回答质量最多 30%；② 多文档场景用

<document index="n">

包裹，内含

<document_content>

和

<source>

；③ 要求 Claude 先引用原文相关段落再作答，帮它过滤文档噪音。

模型自我认知。

如果你需要 Claude 在应用中正确标识自己：

原文

The assistant is Claude, created by Anthropic. The current model is Claude Opus 4.8.

中文对照

本助手是 Claude，由 Anthropic 创建。当前模型为 Claude Opus 4.8。

API 字符串标识：

原文

The exact model string for Claude Opus 4.8 is claude-opus-4-8.

中文对照

Claude Opus 4.8 的精确模型字符串为 claude-opus-4-8。

沟通风格与长度。

新模型更直接、更接地气、更简洁。工具调用后可能跳过口头总结直接下一步。想要它汇报过程：

原文

After completing a task that involves tool use, provide a quick summary of the work you've done.

中文对照

完成涉及工具调用的任务后，简要总结你完成的工作。

控制输出格式的四条方法。

① 说想要什么，不说不要什么——正向描述比禁令更稳定。② 用 XML 标签指定输出格式——模型会认真对待结构约束。③ prompt 本身的格式会影响输出——如果你在 prompt 里没用 markdown，模型回你的 markdown 也会变少。我试过把 prompt 里的 markdown 全清掉后纯文本命中率从约七成提到九成以上。④ 需要精细控制时用详细 prompt。

❌ 禁令式（效果忽好忽坏）

✅ 正向描述（输出稳定）

Do not use markdown in your response.

Your response should be composed of smoothly flowing prose paragraphs.

不要在回复中使用 markdown。

你的回复应由流畅的散文段落组成。

效果差异：

左侧告诉模型"不要做什么"，模型可能仍以其他格式输出 markdown；右侧明确描述了目标形态，模型知道该往哪个方向走。实测命中率从约 70% 提升到 90%+。

LaTeX 输出。

新模型默认用 LaTeX 渲染数学公式。需要纯文本时加：

原文

Format your response in plain text only. Do not use LaTeX, MathJax, or any markup notation. Write all math expressions using standard text characters (e.g., '/' for division, '*' for multiplication, '^' for exponents).

中文对照

仅用纯文本格式化回复。不使用 LaTeX、MathJax 或任何标记符号。用标准文本字符书写所有数学表达式，如 '/' 表示除号、'*' 表示乘号、'^' 表示指数。

文档创建。

新模型在创建演示文稿、动画和视觉文档方面表现出色，通常第一次就能产出可直接使用的结果。

从 prefilled responses 迁移。

Claude 4.6 起不再支持末尾的 assistant turn 的 prefilled responses——请求会返回 400 错误。文档给了五种常见 prefill 场景的替代方案：① 控制输出格式 → 用 Structured Outputs 或直接要求模型按 schema 输出（新版模型指令遵循已经够强）；② 消除开场白 → system prompt 中加：

原文

Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc.

中文对照

直接回复，不用开场白。不要以 "这是……""基于……" 等短语开头。

或用 XML 标签、tool calling；③ 避免错误拒答 → 新版模型本身拒答判断已经好很多，清晰 prompt 通常够用；④ 续写 → 把续写起点放进 user message：

原文

Your previous response was interrupted and ended with '...'. Continue from where you left off.

中文对照

你之前的回复被中断，结尾为 '...'。从中断处继续。

⑤ 上下文刷新 → 把原来 prefill 的上下文提醒注入 user turn，或通过工具在 context compaction 时注入。

SYSTEM PROMPT · 结构化长文档分析（XML + 引用先行）

system = """

You are an AI physician's assistant.

<instructions>

Find quotes from the patient records

relevant to diagnosing the reported

symptoms. Place these in <quotes>

tags. Then, based on these quotes,

list diagnostic information in

<info> tags.

</instructions>

"""

中文对照：

你是 AI 医师助手。从患者记录中找出与诊断报告症状相关的引用，放入 <quotes> 标签中。然后根据这些引用，在 <info> 标签中列出诊断信息。

3

工具调用：触发、并行与双向节制

"建议"vs"执行"的界限。

新模型对措辞很敏感。同一件事，说法不同，模型的行为完全不同：

❌ 这样说 → 只给建议

✅ 这样说 → 直接执行

Can you suggest some changes to improve this function?

Change this function to improve its performance.

你能建议一些改进这个函数的方案吗？

修改这个函数以提高其性能。

效果差异：

左栏用的是 "suggest"，模型理解为"给建议即可"；右栏用的是 "Change"，模型理解为"执行变更"。一字之差，行为完全不同。

你还可以在 system prompt 层面设定模型的默认行为倾向——两套模板，按场景选用：

⚡ 主动执行模式（coding agent）

🔒 保守模式（咨询/审查场景）

By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing.

Do not jump into implementation or change files unless clearly instructed to make changes. When the user's intent is ambiguous, default to providing information and recommendations rather than taking action.

默认执行变更。意图模糊时推断最有用的行动并推进，用工具发现缺失细节。

除非明确指示，否则不直接动手。意图模糊时默认提供信息和建议。

效果差异：

左栏适合需要模型主动推进的 coding agent；右栏适合需要模型先确认再行动的咨询/审查场景。根据产品定位选择，也可按项目切换。

注意：如果你之前为了治旧模型"不够主动"而加了很强硬的工具触发措辞，新模型可能会 overtrigger。对比一下新旧两种写法：

❌ 旧版做法（新模型会 overtrigger）

✅ 新版做法（正常语气即可）

CRITICAL: You MUST use this tool when the user asks about code. If in doubt, use the tool anyway.

Use this tool when the user asks about code.

关键：当用户询问代码时你必须使用此工具。不确定时也先用上。

当用户询问代码时使用此工具。

效果差异：

左栏是为旧模型写的"加强版"指令，新模型会照单全收导致过度触发；右栏的平实措辞在新模型上已足够。核心原则：迁移到新模型后，dial back aggressive language。

并行工具调用优化。

新模型在并行工具执行上表现出色——同时发起多个搜索、并行读多个文件、甚至并行跑 bash 命令。不加 prompt 成功率已经很高，要推到接近 100%：

原文（最大化并行）

If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel. Maximize use of parallel tool calls where possible to increase speed and efficiency.

中文对照

如果你打算调用多个工具且工具调用之间没有依赖关系，将所有独立的工具调用并行执行。尽可能最大化并行工具调用以提高速度和效率。

关键补丁：如果有些调用依赖前一个调用的结果，必须串行——不要猜参数。反过来，如果希望模型放慢节奏（资源受限环境）：

原文（串行模式）

Execute operations sequentially with brief pauses between each step to ensure stability.

中文对照

顺序执行操作，每步之间短暂停顿以确保稳定性。

SYSTEM PROMPT · 默认执行 + 最大化并行（完整模板）

<default_to_action>

By default, implement changes rather than

only suggesting them. Infer the most useful

likely action and proceed.

</default_to_action>

<use_parallel_tool_calls>

If you intend to call multiple tools and

there are no dependencies, make all

independent tool calls in parallel.

Maximize parallel tool calls for speed.

Do NOT call dependent tools in parallel.

Never guess missing parameters.

</use_parallel_tool_calls>

中文对照：

默认执行变更而非仅建议，推断最有用的行动并推进。独立工具调用全部并行，最大化并行提速。有依赖关系的调用不并行，不猜测缺失参数。

4

Thinking 与推理机制

Overthinking 问题。

Opus 4.6 在高 effort 下会做大量前期探索——收集大量上下文、同时追踪多条线索。这种前期投入通常优化了最终结果，但如果你的 prompt 之前刻意让模型"更 thorough"，现在可能矫枉过正。解决：① 把 blanket 指令（"默认使用工具 X"）改成有条件的（"当工具 X 能帮你更好理解问题时用它"）；② 去掉之前为旧模型补的 over-prompting——"If in doubt, use tool"这种在新模型上会 overtrigger；③ 降低 effort 是最直接的杠杆。如果需要一个硬顶：

原文

When deciding how to approach a problem, choose an approach and commit to it. Avoid revisiting decisions unless you encounter new information that directly contradicts your reasoning.

中文对照

决定如何处理问题时，选定一个方案并坚持执行。除非遇到直接与你推理矛盾的新信息，否则不要回头重新审视已做的决定。

另外，extended thinking 的

budget_tokens

在 Opus 4.6 / Sonnet 4.6 上仍然可用但已 deprecated——建议迁移到 adaptive thinking + effort。

Adaptive Thinking 机制。

Claude 4.6 系列使用 adaptive thinking（

thinking: {type: "adaptive"}

），模型动态决定何时思考、思考多深——两个因素驱动：effort 参数 + 查询复杂度。高 effort 触发更多思考，复杂查询同理。简单查询直接回复，不用 thinking。内部评测中 adaptive thinking 效果可靠地优于 extended thinking。

使用建议：agentic 行为（多步工具调用、复杂 coding、长线 agent 循环）用 adaptive thinking。可以用 prompt 引导 thinking 行为：

原文

After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding.

中文对照

收到工具结果后，仔细反思其质量并确定最佳下一步再继续。

如果 prompt 太复杂导致 thinking 触发过于频繁——常见于大型 system prompt——加引导：

原文

Extended thinking adds latency and should only be used when it will meaningfully improve answer quality. When in doubt, respond directly.

中文对照

扩展思考会增加延迟，应仅在能实质提升回答质量时使用。不确定时直接回复。

几个实用技巧：① 通用指令好于手写步骤——"think thoroughly"通常产出比人类预先写的 step-by-step 计划更好的推理。② few-shot 示例里的

<thinking>

标签会被模型泛化到自己的 thinking 块中。③ thinking 关闭时仍可用 structured tags（

<thinking>

+

<answer>

）做手动 chain-of-thought。④ 让 Claude 自检：

原文

Before you finish, verify your answer against [test criteria].

中文对照

完成前，对照 [测试标准] 验证你的回答。

PYTHON · 从 extended thinking 迁移到 adaptive thinking

# Before (extended thinking, 旧版模型)

client.messages.create(

model="claude-sonnet-4-5-20250929",

max_tokens=64000,

thinking={"type": "enabled",

"budget_tokens": 32000},

messages=[{"role":"user","content":"..."}]

)

# After (adaptive thinking, 最新模型)

client.messages.create(

model="claude-opus-4-8",

max_tokens=64000,

thinking={"type": "adaptive"},

output_config={"effort": "high"},

messages=[{"role":"user","content":"..."}]

)

5

Agent 系统全栈调校

文档里篇幅最长的部分，覆盖 Agent 系统的 12 个调校维度。我按实战频率重新排序。

长时间推理与状态追踪。

新模型在跨 context window 的长任务上表现出色——聚焦增量进展，一次推进几步而非试图一次完成所有事。这种能力在多个 context window 或任务迭代中尤其明显。

Context Awareness。

Claude 4.6/4.5 系列有 context awareness 能力——模型能追踪自己还剩多少 context window（"token budget"）。如果你用的 agent harness 会 compaction 或允许存到外部文件，把这个信息告诉 Claude，避免它因为担心 context 耗尽而提前收工：

原文

Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely. Do not stop tasks early due to token budget concerns. Save current progress before the context window refreshes.

中文对照

你的上下文窗口在接近上限时会自动压缩，允许你无限期继续工作。不要因为 token 预算顾虑而提前停止任务。在上下文窗口刷新前保存当前进度。

Memory tool 跟 context awareness 天然配合。

多 Context Window 工作流（6 条实战建议）。

① 第一个 context window 用不同的 prompt——搭框架（写测试、建 setup 脚本），后续窗口迭代 todo-list。② 让模型先写测试（结构化格式如

tests.json

），长期迭代能力明显提升——提醒它测试不能删。③ 鼓励模型创建 QoL 工具脚本（

init.sh

启动服务器、跑测试、跑 linter），避免每次新窗口重复造轮子。④ Context window 清空时考虑全新开始而非 compaction——新模型极擅长从文件系统发现状态，有时这比保留压缩上下文效果更好。告诉它从哪里开始：

原文

Review progress.txt, tests.json, and the git logs. Manually run through a fundamental integration test before implementing new features.

中文对照

检查 progress.txt、tests.json 和 git 日志。在实现新功能前手动跑一遍基础集成测试。

⑤ 提供验证工具——长线自主任务需要不需要人工反馈的验证手段，如 Playwright MCP 或 computer use 做 UI 测试。⑥ 鼓励用完整个 output context：

原文

It's encouraged to spend your entire output context working on the task — just make sure you don't run out of context with significant uncommitted work.

中文对照

鼓励用满整个输出上下文窗口处理任务——只要确保不要在还有大量未提交工作时把上下文耗尽。

状态管理最佳实践。

结构化数据（测试结果、任务状态）用 JSON——帮 Claude 理解 schema；非结构化进度笔记用纯文本；用 git 做状态追踪——log 是天然的"做了什么的记录"和可恢复的 checkpoint。明确要求 Claude 追踪进度、聚焦增量。

自主性与安全边界。

这是文档里最务实的一段。Opus 4.6 在没有指引的情况下可能执行难以回滚的操作。按可逆性分层：① 本地可逆操作（编辑文件、跑测试）→ 鼓励直接做；② 破坏性操作（删文件/分支、drop table、rm -rf）→ 先问；③ 难以回滚（git push --force、git reset --hard、amend 已发布的 commit）→ 先问；④ 影响他人的操作（push 代码、PR 评论、发消息、改共享基础设施）→ 先问。文档给了一段可直接复用的 system prompt，建议直接放进 agent harness。

SYSTEM PROMPT · Agent 安全边界（建议直接复用）

Consider the reversibility and potential

impact of your actions. Take local,

reversible actions (editing files, running

tests). For destructive, hard-to-reverse,

or externally-visible actions, ask first.

Examples requiring confirmation:

- Destructive: deleting files/branches,

dropping tables, rm -rf

- Hard to reverse: git push --force,

git reset --hard, amending published

commits

- Visible to others: pushing code,

commenting on PRs/issues, modifying

shared infrastructure

When encountering obstacles, do not use

destructive actions as a shortcut (e.g.,

don't bypass --no-verify or discard

unfamiliar files).

中文对照：

考虑操作的可逆性和潜在影响。鼓励执行本地、可逆的操作（编辑文件、跑测试）。对于破坏性、难以回滚或对外部可见的操作，先询问确认。需要确认的操作示例：破坏性（删除文件/分支、drop table、rm -rf）、难以回滚（git push --force、git reset --hard、amend 已发布 commit）、对外部可见（push 代码、PR/issue 评论、改共享基础设施）。遇到障碍时，不要用破坏性操作走捷径（如不要 bypass --no-verify 或丢弃不熟悉的文件）。

研究与信息收集。

新模型在 agentic search 上表现出色。复杂研究任务的结构化方法：

原文

Search in a structured way. As you gather data, develop several competing hypotheses. Track your confidence levels in progress notes. Regularly self-critique your approach. Update a hypothesis tree or research notes file.

中文对照

以结构化方式搜索。在收集数据的同时发展几个竞争假设。在进度笔记中追踪置信度。定期自我批评你的方法。更新假设树或研究笔记文件。

定义成功标准、要求跨源验证。

子代理（Subagent）编排。

新模型能主动识别"这个任务该分给专门子代理并行跑"的场景。要利用这个能力：确保子代理工具在 tool definition 里定义清楚；让 Claude 自然编排，不必显式指令。但 Opus 4.6 有过度使用子代理的倾向——一个 grep 能解决的事也要 spawn。如果遇到，加引导：

原文

Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams that don't need to share state. For simple tasks, sequential operations, single-file edits, or tasks where you need to maintain context across steps, work directly rather than delegating.

中文对照

当任务可并行运行、需要隔离上下文或涉及不需要共享状态的独立工作流时使用子代理。对于简单任务、顺序操作、单文件编辑或需要跨步骤保持上下文的任务，直接操作而非委派。

Prompt Chaining。

With adaptive thinking 和 subagent orchestration，大多数多步推理模型内部就能处理。显式 prompt chaining（拆成多个 API 调用）仍有用——当你需要检查中间输出或强制特定 pipeline 结构时。最常见模式：生成草稿 → 让 Claude 按标准 review → 基于 review 改进。

减少临时文件。

新模型有时会创建临时 Python 脚本作为"草稿纸"再产出最终结果——这能提升 coding 质量。如果不想留临时文件：

原文

If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.

中文对照

如果你在迭代过程中创建了任何临时文件、脚本或辅助文件，在任务结束时清理删除它们。

避免过度工程化。

Opus 4.5/4.6 可能创建多余文件、加没必要的抽象、为不需要的灵活性预留接口。文档给了一段很实用的约束 prompt——范围上：只做被要求的事，bug fix 不需要顺手清理周边代码；文档上：不改的代码不加 docstring/注释；防御编码上：不为不可能发生的场景加 error handling；抽象上：不为一次性操作创建 helper/utility。核心原则：

原文

The right amount of complexity is the minimum needed for the current task.

中文对照

合适的复杂度是当前任务所需的最低限度。

避免为通过测试而硬编码。

Claude 有时会过度聚焦让测试通过而牺牲通用性，或创建 helper 脚本绕过标准工具。解决：

原文

Write a high-quality, general-purpose solution using standard tools. Do not create helper scripts or workarounds. Implement logic that works for all valid inputs, not just test cases. Tests verify correctness, not define the solution. If the task is unreasonable or any tests are incorrect, inform me rather than working around them.

中文对照

使用标准工具编写高质量、通用的解决方案。不要创建辅助脚本或变通方法。实现对所有有效输入都正确的逻辑，而非仅针对测试用例。测试用于验证正确性，不定义解决方案。如果任务不合理或任何测试不正确，请告知我而非绕过它们。

最小化 Agentic Coding 中的幻觉。

新模型幻觉更少、回答更准确、更基于代码实情。进一步强化：

原文

Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering. Investigate relevant files BEFORE answering questions about the codebase. Never make claims about code before investigating.

中文对照

绝不推测你没打开过的代码。如果用户提到了特定文件，你需要在回答前读取该文件。在回答关于代码库的问题之前先调查相关文件。在调查之前不对代码做任何断言。

💡 专项能力补充

视觉能力：

Opus 4.5/4.6 的图像处理和提取能力提升，多图场景改进尤为明显。一个有效技巧是给 Claude 一个 crop tool 或 skill——内部测试表明让模型能"zoom"到图片关键区域，图像评测分数可靠提升。Anthropic 提供了一个 crop tool cookbook。

前端设计：

Opus 4.5/4.6 擅长构建复杂真实 Web 应用，但无引导时可能落到"AI slop"审美。文档给了一段前端美学 system prompt——核心思路：独特字体（避免 Inter/Roboto/Arial）、有态度的配色（主导色+锐利 accent 而非均匀分布）、CSS 动画做微交互和页面加载、用渐变/几何图案/氛围效果做背景层次。Anthropic 博客有专门的前端设计 skill 指南。

⚠️ 迁移指南要点

迁移到 Claude 4.6 系列时注意：① 描述你想要的输出行为而非依赖默认值；② 用 modifier 鼓励质量和细节：

原文

Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.

中文对照

创建一个分析仪表盘。包含尽可能多的相关功能和交互。超越基础，创建一个功能完整的实现。

③ 动画和交互现在需要显式要求；④ thinking 配置从 budget_tokens 迁移到 adaptive thinking + effort；⑤ prefilled responses 不再支持，用前述替代方案；⑥ 如果之前为了治旧模型"不够主动"加了 aggressive 的 prompt，现在要调回来——新模型更主动，可能 overtrigger。

Sonnet 4.5 → Sonnet 4.6 迁移：

Sonnet 4.6 默认 effort 为

high

（Sonnet 4.5 无 effort 参数），不显式设置会多出延迟。建议大多数应用从

medium

起步，高吞吐/延迟敏感用

low

。如果不用 extended thinking，显式设

thinking: {type: "disabled"}

+ effort。最难的、最长线的问题（大规模代码迁移、复杂研究、长时间自主工作）仍用 Opus 4.8。

· · ·

总结

模型越强，Prompt 越要写"为什么"而非"做什么"

这份文档最核心的洞察，不是某个具体技巧，而是它反映的方向：

模型越强，prompt 越要从"操作手册"升级为"上下文说明书"。

旧模型需要你手把手给步骤，新模型能从原因、约束和示例推导出最佳做法。你升级的重点不是 prompt 的长度，而是它的信息密度。

如果看完这篇只记三件事：

① 给上下文而不是只给指令；② 把否定式改成正向描述，说想要什么而非不要什么；③ Agent 场景把 effort 设到 xhigh，给足 max_tokens，把安全边界分层写进 system prompt。

完整原文：

platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

。本文覆盖了全部章节——Claude Opus 4.8 11 个行为特征、7 条通用原则、5 项输出控制、2 个工具调用维度、2 层 thinking 机制、12 个 Agent 调校点、2 个专项能力、以及完整迁移指南。建议存下来，用到时回来查。

觉得有用，转发给也在调 prompt 的同事

你的 prompt 改了什么效果最明显？

关注公众号「克劳德猎手」获取更多内容 👇

📚 相关阅读

Opus 4.7 在 Claude Code 里怎么调？官方最佳实践 7 条全落地

Opus 4.7 最佳实践：Claude Code 调优官方指南

Opus 4.7 官宣：能干更难的活，可社区喊「4.6 回来了」