# openclaw、hermes配置优化意见

# 第一章：Hermes Agent 基础配置与记忆系统



## 1\.1 装完别急着用——8 处必改配置



Hermes 装完按默认配置跑，3 天就可能翻车。以下 8 处配置改完，Agent 才能稳定运行。



### 1\.1\.1 速查清单（直接照抄）



|编号|配置项|操作|
|---|---|---|
|1|**SOUL\.md ≤ 1KB**|`wc \-c \~/\.hermes/SOUL\.md`，超了就精简。技术栈打死不能进 SOUL。|
|2|**MEMORY ≤ 800 字，USER ≤ 500 字**|环境事实放 MEMORY，偏好放 USER，分层写别塞。|
|3|**Skill 手动命名**|`Save this as a skill called \&lt;name\&gt;` 比自动建议更可控。|
|4|**Cron prompt 自包含**|目标 \+ 命令 \+ 验证 \+ 处置，缺一项就死循环。|
|5|**Gateway 从 $HOME 启**|`cd \~ \&amp;\&amp; hermes gateway restart`，别用仓库目录启。|
|6|**主 Opus \+ 辅 Flash**|配置 `credential\_pool\_strategies`，辅助模型换便宜的。|
|7|**长会话手动 ****`/compress`**|v0\.10 自动压缩有 bug，手动更稳。|
|8|**压缩阈值调至 0\.75**|修改 `\~/\.hermes/config\.yaml` 中 `compression\.threshold`。|



---



## 1\.2 核心配置文件分层：SOUL vs AGENTS



90% 的用户混淆了 `SOUL\.md` 和 `AGENTS\.md` 的职责，导致 Agent 人格与行为混乱。



|文件|职责|内容范围|关键约束|
|---|---|---|---|
|**SOUL\.md**|**人格定义**|全局不变的自我认知：语气偏好、判断压力、不确定态度。|**≤ 1KB**，禁止写入技术栈。|
|**AGENTS\.md**|**干活规范**|项目级技术规范：技术栈、命令约定、目录结构、提交规范。|按项目存放，不同项目不同内容。|



### ✅ SOUL\.md 标准模板（612 bytes 示例）

```Markdown
# SOUL · keep under 1KB

## Voice
Be direct. Skip pleasantries.
Use Chinese by default, English for code.

## Judgment
Push back when I am wrong. Cite the reason.
Say "I don't know" when unsure. Never fabricate.

## Rhythm
Prefer one decisive answer over options list.
When steps exceed 5, ask before proceeding.
```

**自检命令**：`wc \-c \~/\.hermes/SOUL\.md`（超过 1024 立即精简）。



### ✅ AGENTS\.md 模板

```Markdown
# 项目规范：MyAPI Service

## 技术栈
- 语言：Rust 1.75+
- 框架：Axum
- 数据库：PostgreSQL 16（使用 SQLx）

## 编码约定
1. 所有数据库查询必须使用 SQLx 的宏进行编译期检查。
2. 错误处理统一使用 `anyhow::Result` 和自定义的 `AppError` 枚举。
3. 环境变量配置在 `.env` 文件中，不要在代码中硬编码任何凭证。

## 常用命令
- 运行测试：`cargo test --all-features`
- 启动服务：`cargo run --bin server`
```



---



## 1\.3 Token 成本优化（账单降 40%）



实测：改两处配置，3 天账单从 $14 降至 $8\.4。



|优化项|问题根因|修复方案|
|---|---|---|
|**Telegram Gateway 目录坑**|Gateway 起在源码目录（如 `\~/code/hermes\-agent`），每轮多吃项目级 `AGENTS\.md`，Token 消耗翻 2\-3 倍。|`cd \~ \&amp;\&amp; hermes gateway restart`，从 `$HOME` 重启，无项目级污染。|
|**Aux Model 分层**|辅助任务（压缩摘要、Cron 日报、短回复）默认也消耗昂贵主模型。|主模型用 Opus，辅助模型换 Gemini Flash。配置项：`credential\_pool\_strategies`。|



---



## 1\.4 Cron 定时任务规范



**核心原则**：Cron 启动的是**干净 Session**，看不到你当前对话的上下文。Prompt 必须**自包含**。



### ❌ 错误写法（依赖人类记忆）

```Bash
0 9 * * * hermes exec 'Check on that server issue'
# 结果：Which server? Which issue? → 死循环
```



### ✅ 正确写法（目标 \+ 命令 \+ 验证 \+ 处置）

```Bash
0 9 * * * hermes exec \
'SSH to prod-api-01, run: \
systemctl status api-server, \
tail -n 100 /var/log/api.err. \
如果 status 非 active 或 err log 含 ERROR, \
发 Telegram 并附上最后 20 行'
```



**写 Cron Prompt 的标准**：把它当成对**一个从未见过这个项目的同事**的一次性授权——缺什么就写什么。



---



## 1\.5 记忆系统进阶



### 1\.5\.1 Hermes 记忆系统的整体架构



Hermes 的记忆系统 = **内置记忆 \+ 外部记忆提供商 \+ 运行时上下文**。内置记忆始终存在；外部 Memory Provider 是叠加能力，不是替代关系。



#### 第一层：内置记忆（始终激活）



内置记忆由两个文件组成，默认存储在 `\~/\.hermes/memories/` 目录。



|文件|用途|维护者|硬限制|
|---|---|---|---|
|**MEMORY\.md**|Agent 的工作笔记：环境事实、项目约定、学到的技巧|Agent 维护|**2,200 字符**|
|**USER\.md**|用户画像：偏好、沟通风格、工作习惯|Agent 维护|**1,375 字符**|



> **重要概念：冻结快照（Frozen Snapshot）**  
> 
> 这两个文件在每次会话开始时作为**冻结快照**注入上下文。会话中途 Agent 新写入的记忆，不会立刻改变当前会话的上下文，通常要到后续会话才体现。这样设计是为了保持前缀稳定，提升缓存命中并降低推理成本。
> 
> 



**容量管理建议**：

- `MEMORY\.md`：日常维持在 **1,800 字符**（约 1,200 汉字），预留 20% 空间。

- `USER\.md`：日常维持在 **1,100 字符**（约 700 汉字）。

    

### 1\.5\.2 Agent\-curated memory 机制原理：为什么它“不记得”？



Hermes 的内置记忆是 **Agent 策展（Agent\-curated）** 的，不是全量记录。



**策展机制的优点**：

- **节省 Token**：Prompt 头部保持稳定，KV Cache 有效利用。

- **防止记忆污染**：只有 Agent 判断“重要”的内容才会被写入长期记忆。

    

**记忆更容易被保留的场景**：

- 你明确表达了偏好（“我喜欢/不喜欢 xxx”）

- 发现了环境事实（“这台机器装了 xxx”）

- 纠正了 Agent 的错误做法

- 完成了一个重要任务里程碑

- 你明确要求它记住某件事

    

**解决方案：明确下达记忆指令**

> “记住我的偏好：所有代码统一使用 Python 3\.11，不要用 3\.12 或 3\.13。”
> 
> 



### 1\.5\.3 核心记忆文件正确使用方法



|文件|位置|内容|维护者|
|---|---|---|---|
|**SOUL\.md**|`\~/\.hermes/`|人格、行为准则、固定规则|**你自己写**|
|**AGENTS\.md**|项目根目录|项目级行为规范和执行约束|**你自己写**|
|**MEMORY\.md**|`\~/\.hermes/memories/`|工作笔记、环境事实|Agent 维护|
|**USER\.md**|`\~/\.hermes/memories/`|用户画像、偏好|Agent 维护|



**铁律**：不要把应该写在 `SOUL\.md` 里的东西放进 `MEMORY\.md`。`MEMORY\.md` 会被整理、压缩甚至替换，固定规则必须放在 `SOUL\.md`。



### 1\.5\.4 Super Memory 与持久记忆 nudge 配置



`nudge\_interval` 控制 Agent 进行记忆反思的频率。



**配置位置**：`\~/\.hermes/config\.yaml`

```YAML
memory:
  nudge_interval: 5
```



**推荐值**：

|场景|推荐值|说明|
|---|---|---|
|小模型、小上下文|3\~5|需要更早固化重要信息|
|标准模型|5\~10|成本与记忆质量的平衡点|
|大上下文模型|10\~15|可以在更长对话后做更高质量的总结|



### 1\.5\.5 跨会话与长任务记忆保持方法



**方法一：手动插入 Checkpoint（最简单有效）**

> “当前进度总结：我们已经完成了数据清洗和特征工程，下一步是训练模型。请把这个进度写入你的记忆，确保后续不会忘记。”
> 
> 



**方法二：用外部文件作为“任务状态文件”**

> “请在项目目录下创建 TASK\_STATUS\.md，记录当前任务的完整状态。每次我们恢复工作时，先读取这个文件。”
> 
> 



### 1\.5\.6 外部 Memory Providers 实战配置



自 v0\.7\.0 起，Hermes 支持多种外部 Memory Providers：Honcho、OpenViking、Memo、Hindsight、Holographic、RetainDB 等。



**推荐一：Memo（自动化程度高）**

```Bash
pip install memoai
echo "MEMO_API_KEY=your-key-here" >> $HERMES_HOME/.env
hermes config set memory.provider mem0
hermes memory status
```



**推荐二：Holographic（偏本地、隐私友好）**

```Bash
hermes config set memory.provider holographic
hermes memory status
```



### 1\.5\.7 记忆文件管理规则与清理技巧



**核心逻辑**：记忆不是越多越好，而是越稳定、越高密度越好。



**实战建议**：

- 控制容量在 70%\~80%，不要塞满。

- 当 `MEMORY\.md` 接近上限时，手动引导 Agent：

\&gt; “请整理你的记忆，删除过时条目，合并相关条目，腾出空间。”

- 也可以直接编辑文件：`nano \~/\.hermes/memories/MEMORY\.md`

    

### 1\.5\.8 记忆与技能的联动机制



当 Agent 在 `MEMORY\.md` 中多次记录了类似工作流，意味着这个流程更适合沉淀为 Skill。



**主动引导**：

> “我注意到你已经记住了我们的部署流程。请把这个流程创建为一个可复用的 Skill，名字叫 deploy\-workflow。”
> 
> 



---



### 🛠️ 动手实践：构建你的专属记忆系统



1. 复制 `SOUL\.md` 模板到 `\~/\.hermes/SOUL\.md`，并根据实际情况修改。

2. 在常用项目目录下创建 `AGENTS\.md`。

3. 修改 `config\.yaml`，将 `nudge\_interval` 设置为 5 进行测试。

4. 开启新对话，告诉 Agent 一条特定偏好：“以后所有的 Python 脚本都保存在 /tmp/scripts 目录下。”

5. 进行 5 轮以上对话，观察是否触发记忆整理。

    

**预期效果**：

- 运行 `cat \~/\.hermes/memories/MEMORY\.md`，能看到偏好已被记录。

- 开启全新会话，让 Agent 写一个 Python 脚本，它会自动遵循先前记录的偏好。

    

---



# 第二章：Hermes Agent 高级特性——技能自进化与多 Agent 协作



## 2\.1 技能自进化：让 Hermes “越干越会干”



Hermes 最大的差异点不只是“能干活”，而是“越干越会干”。理解技能自生成机制，才能让你的 Agent 真正进化，而不是每次都从零开始。



### 2\.1\.1 记忆 vs 技能：核心区别



|维度|记忆（Memory）|技能（Skill）|
|---|---|---|
|**本质**|事实和经验的记录，相对散乱|标准化 SOP：触发条件 \+ 操作步骤 \+ 注意事项 \+ 验证方法|
|**作用**|解决“记得住”|解决“用得高效且可复用”|
|**存储**|`MEMORY\.md`、`USER\.md`|`\~/\.hermes/skills/\&lt;name\&gt;/SKILL\.md`|
|**加载**|会话开始时全量/部分注入|触发时才加载，不入每轮请求|



**一句话总结**：Hermes 设计技能自生成机制的核心目的，是把记忆中的重复经验进一步沉淀为可复用的结构化 Skill。



### 2\.1\.2 Agent 自动创建 Skill 的触发条件与流程



**常见触发条件**：

- 完成了一个相对复杂的任务

- 遇到了错误或死路，后来找到了正确路径

- 用户纠正了它的做法

- 发现了一个值得复用的非平凡工作流

    

**主动引导 Agent 创建 Skill**：

> “我们刚才完成的这个数据处理流程很有价值，请把它保存为一个 Skill，名字叫 data\-pipeline，放在 devops 分类下，确保包含触发条件、操作步骤、注意事项和验证方法。”
> 
> 



### 2\.1\.3 技能质量控制与优化方法



**判断一个 Skill 质量好不好的标准**：



|标准|说明|
|---|---|
|**触发条件清晰**|Agent 能准确判断什么时候该用它|
|**步骤可执行**|每一步都有明确操作，而不是空泛描述|
|**有验证方法**|执行完后能判断是否成功|
|**有注意事项**|记录了踩过的坑|



**手动优化 Skill 时**，建议让 Agent 做定点修改，而不是整篇重写：

> “请更新 stock\-daily\-report 这个 skill，在注意事项里补充一条：‘周五收盘后数据可能延迟到周六早上才完整。’”
> 
> 



### 2\.1\.4 技能退化与重复问题的解决思路



**技能退化的表现**：

- 描述越来越模糊，触发条件越来越宽泛

- 多个 Skill 做的是同一件事，但写法不同

    

**解决方案：让 Agent 做技能审计**

> “请审查你所有的 Skills，找出：
> 
> - 功能重复的技能（合并它们）
> 
> - 描述模糊、触发条件不清晰的技能（重写它们）
> 
> - 步骤已经过时的技能（更新它们）
> 
> - 给我一份审计报告，然后等我确认后再执行修改。”
> 
> 



### 2\.1\.5 Skill 与记忆系统的联动机制



在 `SKILL\.md` 中，你可以引导 Agent 在执行技能前先查看记忆：



```Markdown
## 操作流程
1. 先检查 MEMORY.md 中是否有关于该 API 的特殊注意事项。
2. 如果有，优先遵循记忆中的约定。
3. 执行完成后，将新发现的注意事项写入 MEMORY.md。
```



### 2\.1\.6 Self\-optimization 功能使用建议



把 Self\-optimization 理解为 Hermes 在使用过程中会逐步修补技能和行为策略的能力方向。具体配置入口请以官方最新文档和你本机 `config\.yaml` 为准。



---



### 🛠️ 动手实践：训练你的第一个自动化技能



**任务目标**：让 Agent 学习并固化一个你常用的工作流。



**操作步骤**：

1. 找一个你经常做的重复性任务（例如：检查系统磁盘空间、清理 Docker 悬空镜像，并输出一份简报）。

2. 在对话中，一步步指导 Agent 完成这个任务，纠正它的错误，直到执行稳定。

3. 发送指令：“请把刚才的清理流程保存为一个 Skill，命名为 docker\-cleanup，包含触发条件、具体执行命令和验证步骤。”

4. 运行 `hermes skills list` 查看是否创建成功。

    

**预期效果**：开启新会话，直接发送指令 `/docker\-cleanup`，Agent 能较稳定地按照之前固化的步骤完成任务。



---



## 2\.2 多 Agent 协作



### 2\.2\.1 Sub\-Agent 的 spawn 机制与使用方法



Hermes 支持主 Agent 通过 `delegate\_task` 等方式派生子 Agent 执行拆分后的任务。



**并发建议**：从 **2\~3 个** 子 Agent 起步，防止触发 API Rate Limit。



**基本用法**：

> “这个任务可以并行处理：
> 
> - 子任务 A：抓取 A 股今日涨停板数据
> 
> - 子任务 B：分析北向资金流向
> 
> - 子任务 C：生成市场情绪指数
> 
> - 请派生 3 个子 Agent 并行完成这三个子任务，然后汇总结果。”
> 
> 



**子 Agent 的关键限制**：

子 Agent 从一个新的会话上下文开始，**不会天然继承主 Agent 的完整历史**。必须在 `context` 里把背景信息传完整：



```Plain Text
delegate_task(
  goal="修复 api/handlers.py 中的 TypeError",
  context="文件路径: /home/user/myproject/api/handlers.py
            错误信息：第 47 行 TypeError: 'NoneType' object has no attribute 'get'
            原因：parse_body() 在 Content-Type 缺失时返回 None
            项目使用 Python 3.11 + Flask"
)
```



> **最重要的经验**：不要假设子 Agent 知道“这个错误”“刚才那个文件”“上一步那个思路”是什么。
> 
> 



### 2\.2\.2 Profiles 功能实战：同一台机器运行多个独立 Hermes



Profile 是一个完全隔离的 Hermes 环境。每个 Profile 都有自己独立的配置、记忆、会话和技能。



**创建 Profile 的三种方式**：

```Bash
# 方式一：全新 Profile（空白）
hermes profile create mybot

# 方式二：克隆配置（复用 API Key 和模型，但记忆和会话独立）
hermes profile create work --clone

# 方式三：完整克隆（包含记忆、会话、技能等）
hermes profile create backup --clone-all
```



**运行多个独立 Agent**：

```Bash
# 终端 1：运行编码助手
coder chat

# 终端 2：运行投研助手（独立的记忆和技能）
research chat
```



### 2\.2\.3 子 Agent 的独立记忆与技能隔离



每个 Profile 的 `memories/`、`skills/`、`sessions/` 和 `logs/` 目录都是独立的，不会互相读写。



**共享技能**：如果希望多个 Profile 共享同一套技能，可以使用外部技能目录：

```YAML
skills:
  external_dirs:
    - ~/.hermes/shared-skills
```



### 2\.2\.4 主 Agent 协调多个子 Agent 的技巧



**明确角色分工**是最有效的方法。在 `SOUL\.md` 或 `AGENTS\.md` 中定义：



```Markdown
## 多 Agent 协作规范
- Planner Agent: 负责任务分解和进度追踪，不直接执行
- Executor Agent: 负责具体的数据获取和处理，不做决策
- Reviewer Agent: 负责质量检查和结果验证，不做修改
```



### 2\.2\.5 多 Agent 资源分配与冲突避免



|冲突类型|解决方案|
|---|---|
|**Bot Token 冲突**|不同 Profile 在各自的 `\.env` 中配置不同的 Token。|
|**端口冲突**|不同实例使用不同端口：`GATEWAY\_PORT=8080` / `GATEWAY\_PORT=8081`。|



---



### 🛠️ 动手实践：配置双 Agent 协作工作流



**任务目标**：创建两个独立的 Profile，分别承担不同角色，互不干扰。



**操作步骤**：

1. 运行 `hermes profile create coder \-\-clone` 创建编码 Agent。

2. 运行 `hermes profile create reviewer \-\-clone` 创建审查 Agent。

3. 分别编辑它们的 `SOUL\.md`，赋予不同角色设定。

4. 让 coder 写一段有 Bug 的代码并保存到文件。

5. 切换到 reviewer，让它读取该文件并提出修改建议。

    

**预期效果**：两个 Agent 能独立运行，且 reviewer 的记忆中不会混入 coder 的工作流。



---



## 2\.3 技能与多 Agent 的协同效应



当多个 Agent 通过 Profile 独立运行时，它们各自积累的技能可以通过 **共享技能目录** 实现复用。同时，主 Agent 可以将复杂任务拆解后派发给不同专长的子 Agent，每个子 Agent 调用自己 Profile 下的专属 Skill 完成子任务，最后由主 Agent 汇总结果。



**最佳实践**：

- 将通用技能（如 git 操作、代码审查）放在共享目录。

- 将特定项目技能放在对应 Profile 的私有目录。

- 主 Agent 的 `AGENTS\.md` 中定义清楚何时派生子 Agent、如何汇总结果。

    

---



# 第三章：Hermes Agent 生产化部署与上下文压缩



## 3\.1 Gateway 长期后台运行的多种方式



### 3\.1\.1 方式一：Systemd（Linux 生产环境首选）



将 Hermes Gateway 安装为系统服务，实现开机自启和崩溃自动重启。



```Bash
# 安装为 Systemd 服务
hermes gateway install

# 查看服务状态
systemctl status hermes-gateway

# 查看实时日志
journalctl -u hermes-gateway -f

# 重启服务
systemctl restart hermes-gateway
```



> **注意**：如果你使用命名 Profile，服务名可能会带上 profile 后缀，以实际安装输出为准。
> 
> 



### 3\.1\.2 方式二：Docker Compose（更适合多 Profile 部署）



```YAML
version: "3.8"

services:
  hermes-default:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-default
    restart: unless-stopped
    command: gateway run
    volumes:
      - ~/.hermes:/opt/data

  hermes-coder:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-coder
    restart: unless-stopped
    command: gateway run
    volumes:
      - ~/.hermes/profiles/coder:/opt/data
```



> **重要提醒**：不要同时运行两个容器挂载同一个数据目录，否则共享状态文件可能出问题。
> 
> 



---



## 3\.2 定时任务、Heartbeat 与通知机制



### 3\.2\.1 时区配置（最易踩坑）



Hermes 的 Cron 任务严格依赖服务器系统时区。配置前必须运行 `timedatectl` 确认。



```Bash
# 查看当前时区
timedatectl

# 如果时区不对，修改为 Asia/Shanghai
sudo timedatectl set-timezone Asia/Shanghai
```



> **专家级警告**：国内服务器应显示 `Asia/Shanghai`；海外服务器若显示 `UTC`，请手动修正，否则定时任务会在半夜“惊喜上线”。
> 
> 



### 3\.2\.2 Heartbeat 机制（防止静默失败）



在 `\~/\.hermes/\.env` 中添加：

```Bash
echo "GATEWAY_HEARTBEAT=true" >> ~/.hermes/.env
```



Heartbeat 会定期向配置的通道发送心跳信号，帮助你确认 Gateway 是否仍在正常运行。



### 3\.2\.3 定时任务（Cron）



```Bash
# 示例：工作日早上 8:30 生成日报
hermes cron add "30 8 * * 1-5" "生成今日 A 股市场日报并发送到 Telegram"

# 列出所有定时任务
hermes cron list

# 手动运行一次任务（验证逻辑）
hermes cron run <任务名称>
```



**Cron Prompt 自包含原则**（再次强调）：

```Bash
# ❌ 错误写法
0 9 * * * hermes exec 'Check on that server issue'

# ✅ 正确写法
0 9 * * * hermes exec \
'SSH to prod-api-01, run: \
systemctl status api-server, \
tail -n 100 /var/log/api.err. \
如果 status 非 active 或 err log 含 ERROR, \
发 Telegram 并附上最后 20 行'
```



---



## 3\.3 日志监控与调试方法



### 3\.3\.1 日志位置



日志目录会跟随当前 profile 的 `HERMES\_HOME` 变化；默认 profile 下通常位于 `\~/\.hermes/logs/`。



```Bash
# 查看 Gateway 日志
hermes logs gateway

# 查看特定 Agent 的日志
hermes logs agent <agent_id>
```



### 3\.3\.2 调试分享



当你需要向社区或官方反馈问题时：

```Bash
hermes debug share
```

该命令会收集关键配置和日志，生成一个可分享的诊断报告。



---



## 3\.4 Tirith 安全模块的使用与处理



Tirith 是 Hermes 的预执行安全扫描模块，用于拦截高风险命令。



**配置文件**：`\~/\.hermes/config\.yaml`

```YAML
approvals:
  mode: manual   # manual | smart | off
```



|模式|说明|
|---|---|
|`manual`|所有高风险命令都需要人工确认。|
|`smart`|由辅助模型做风险分级，低风险场景自动放行。|
|`off`|关闭安全检查，仅适合完全可信的隔离环境。|



**命令白名单**（如版本支持）：如果某些高频命令被误拦截，可考虑加入 `allowlist`；具体字段名与位置请以当前版本的配置参考为准。



---



## 3\.5 多平台接入进阶配置



### 3\.5\.1 Telegram 接入



```Bash
# 配置 Bot Token
echo "TELEGRAM_BOT_TOKEN=your-bot-token" >> ~/.hermes/.env

# 配置允许访问的用户 ID（白名单）
echo "TELEGRAM_ALLOWED_USERS=your-telegram-user-id" >> ~/.hermes/.env
```



> **提醒**：如果没有配置允许访问的用户范围，Bot 通常不会处于你预期的安全状态，因此上线前一定要做访问控制。
> 
> 



### 3\.5\.2 Discord / 飞书接入



具体配置方式请参考 Hermes 官方文档的 Channels 章节。核心步骤均为：

1. 在对应平台创建 Bot/应用，获取 Token/AppID。

2. 在 `\~/\.hermes/\.env` 或 `config\.yaml` 中填入凭证。

3. 在 `bindings` 中配置路由规则。

    

---



## 3\.6 生产化部署 Checklist



在将 Hermes 部署到生产环境之前，建议逐项检查：



* [ ] `hermes doctor` 无明显报错

* [ ] API Key 已配置在 `\.env` 文件中，而不是 `config\.yaml`

* [ ] 已按需设置 `GATEWAY\_HEARTBEAT=true`

* [ ] 已配置用户白名单（例如 `TELEGRAM\_ALLOWED\_USERS`）

* [ ] 审批模式已根据需求设置 \(`approvals\.mode`\)

* [ ] 已安装为 Systemd 服务，或容器设置了 `restart: unless\-stopped`

* [ ] 时区已确认与预期一致 \(`timedatectl`\)

* [ ] Cron 任务已测试手动运行成功



---



### 🛠️ 动手实践：完成生产环境的稳定部署



**任务目标**：将 Hermes 部署为后台长期运行的服务，并接入 Telegram/Discord。



**操作步骤**：

1. 在 `\.env` 中配置好 Telegram 或 Discord 的 Token 和你的 User ID。

2. 使用 `hermes gateway install` 将其注册为 Systemd 服务，或采用 Docker Compose。

3. 启动服务：`systemctl start hermes\-gateway`

4. 在手机上打开 Telegram/Discord，向你的 Bot 发送消息测试。

5. 配置一个简单的 Cron 任务，测试定时触发是否正常。

    

**预期效果**：

- 即使关闭 SSH 终端，Bot 依然能在 Telegram/Discord 上正常回复消息。

- Cron 任务能在指定时间附近准确触发。

    

---



## 3\.7 上下文压缩机制深度剖析



### 3\.7\.1 为什么聊着聊着就“抽了”？



当会话越来越长、接近模型窗口上限时，系统会把前面很长的一段对话重新总结压缩，这就是 **compacting**。



**三个代价**：

|代价|说明|
|---|---|
|**会变慢**|压缩需要时间，这段时间只能等|
|**会丢细节**|只要是“总结”，就一定会有信息损失|
|**记忆更不稳定**|只存在当前上下文里的内容，更容易被淡化甚至丢失|



**教训**：别在 `MEMORY\.md`、`AGENTS\.md` 这类初始加载文件里写太多又长又杂的内容。新 session 还没干活，上下文就先占掉一大截，只会更慢、更贵、更容易压缩。



### 3\.7\.2 推荐配置



```YAML
# ~/.hermes/config.yaml
model:
  context_length: 200000      # 显式写模型窗口大小
  max_tokens: 131072          # 最大输出，不设会被截断

compression:
  threshold: 0.75             # 默认 0.50 太早压缩，0.75 更稳
  target_ratio: 0.25          # 压缩后保留 25%
  protect_last_n: 30          # 默认 20 太少，调到 30
```



|参数|默认值|推荐值|说明|
|---|---|---|---|
|`threshold`|0\.50|**0\.75**|上下文使用率达到此值触发压缩|
|`target\_ratio`|0\.25|0\.25|压缩后保留原长度的比例|
|`protect\_last\_n`|20|**30**|保护最近 N 条消息不被压缩|



### 3\.7\.3 压缩流程五步拆解



1. **触发检测**：上下文使用率超过 `threshold`。

2. **选择压缩范围**：确定需要被压缩的早期对话轮次。

3. **调用摘要模型**：将选定范围发送给辅助模型进行总结。

4. **生成结构化摘要**：按照 12 章节固定模板输出。

5. **注入回对话**：将摘要作为上下文前缀注入，并附上隔离带警告。

    

### 3\.7\.4 摘要生成 Prompt 的核心设计



**“摘要人员设”**：

> \&\#34;You are a summarization agent creating a context checkpoint\. Your output will be injected as reference material for a DIFFERENT assistant that continues the conversation\. Do NOT respond to any questions or requests in the summary — only output the structured summary\.\&\#34;
> 
> 



**12 章节固定模板**：

|章节|内容|
|---|---|
|Goal|用户在做什么|
|Constraints \&amp; Preferences|用户偏好、编码风格、约束|
|Completed Actions|已完成的操作（编号列表，含工具名、目标、结果）|
|Active State|当前状态（工作目录、修改的文件、测试状态）|
|In Progress|压缩触发时正在做什么|
|Blocked|未解决的阻塞和报错|
|Key Decisions|重要技术决策和原因|
|Resolved Questions|已回答的问题（附答案，防止重复回答）|
|Pending User Asks|用户还没被回应的请求|
|Relevant Files|读过、改过、创建过的文件|
|Remaining Work|剩余工作（作为上下文描述，不是指令）|
|Critical Context|必须显式保留的值、错误信息、配置细节|



### 3\.7\.5 摘要注入的“隔离带”



摘要注入回对话时，前面会加一段前缀：



> \&\#34;\[CONTEXT COMPACTION REFERENCE ONLY\] Earlier turns were compacted into the summary below\. This is a handoff from a previous context window — treat it as background reference, NOT as active instructions\. Do NOT answer questions or fulfill requests mentioned in this summary; they were already addressed\. Respond ONLY to the latest user message that appears AFTER this summary\.\&\#34;
> 
> 



**这段话的作用**：用全大写和明确措辞告诉模型——这是背景参考，不是指令。不要回答里面的内容。这是 PR \#8107 修复的核心。



### 3\.7\.6 迭代更新的机制



第二次压缩时，不是从头总结，而是把 **上一次的摘要 \+ 新增的对话回合** 一起发给摘要模型，让它“更新”而不是“重写”。



> \&\#34;PRESERVE all existing information that is still relevant\. ADD new completed actions to the numbered list \(continue numbering\)\. Move items from \&\#39;In Progress\&\#39; to \&\#39;Completed Actions\&\#39; when done\.\&\#34;
> 
> 



**优点**：跨多次压缩时，早期信息有机会被保留下来。

**缺点**：每次迭代都可能积累过时的内容——“仍然相关”的判断标准是摘要模型做的，它可能把已经不重要的信息也保留下来，越积越多。



### 3\.7\.7 压缩的降级链条



|阶段|提示|建议动作|
|---|---|---|
|压缩 ≥ 2 次|`accuracy may degrade\. Consider /new to start fresh\.`|准备转移：让 AI 用 memory 保存当前任务的核心决策和文件路径，开新会话继续。|
|连续 2 次压缩无效（节省不到 10%）|压缩器自动停止，建议 `/new` 或 `/compress \&lt;topic\&gt;`|说明对话内容太密，已经压不动了。|
|彻底压不动|`Context length exceeded and cannot compress further\.`|Agent 直接终止，任务标记失败。|



### 3\.7\.8 最佳实践总结



|场景|建议阈值|说明|
|---|---|---|
|短对话|0\.85|让上下文尽可能保持完整|
|长对话、密集工具调用|0\.70|更早压缩，留足缓冲|
|超长任务（100 轮以上）|任何阈值都不够|得在任务设计上拆分会话|



**最快见效的一步**：把默认的 `threshold` 从 0\.50 调到 0\.75，把 `protect\_last\_n` 从 20 调到 30。

# 第二部分：OpenClaw 完整指南



> **本部分整合了第四、五、六章全部内容，涵盖 OpenClaw 的记忆系统与成本优化、多智能体部署与安全隔离、部署后优化完全指南。一字不删，细节完整。**
> 
> 





# 第四章：OpenClaw 记忆系统与成本优化



## 4\.1 痛点：为什么你的 OpenClaw 又笨又贵？



很多人觉得 OpenClaw 不够聪明、记不住事、还很费钱，问题常常不是模型不行，而是你还没搞懂它的记忆系统和上下文机制。



|痛点|根源|
|---|---|
|你明明刚交代过一件事，**过一会它又忘了**|该长期记住的内容，没有放到正确的记忆层里。|
|你明明只多说了一句话，**一次请求的成本却不低**|每次请求带给模型的上下文太长，越用越慢，越用越贵。|



**结论**：想把 OpenClaw 用顺，不只是会提问就够了，还得先搞清楚它到底是怎么“记事”的。



## 4\.2 OpenClaw 的三层记忆



OpenClaw 的记忆通常可以理解成三层：



|记忆层|文件位置|用途|生命周期|
|---|---|---|---|
|**长期记忆 Memory**|`MEMORY\.md`|存稳定、不轻易变化的信息：做事原则、固定偏好、项目背景、经验结论|持久化，跨会话|
|**当天记忆 daily memory**|`memory/YYYY\-MM\-DD\.md`|存今天正在发生的事：任务进度、临时结论、今天确认的事项、当天问题与结果|加载最近 2 天|
|**短期记忆 Session**|当前会话上下文|只在当前会话里有效|换会话后失效|



> **重要发现**：很多人明明让它“记住了”，但过一段时间还是忘。大概率不是没答应你，而是只记在了当前会话上下文里，没有真正持久化到本地文件。
> 
> 



### 4\.2\.1 OpenClaw 原生记忆文件详解



OpenClaw 记忆是智能体工作空间中的纯 Markdown 文件。这些文件是唯一的事实来源；模型只“记住”写入磁盘的内容。



**默认工作空间布局**（`\~/\.openclaw/workspace/`）：



```Plain Text
workspace/
├── MEMORY.md              # 精心整理的长期记忆（可选）
└── memory/
    ├── YYYY-MM-DD.md      # 每日日志（仅追加）
    ├── YYYY-MM-DD.md      # 加载今天和昨天的内容
    └── ...
```



**加载规则**：

- 每日日志：会话开始时读取**今天和昨天**的内容。

- `MEMORY\.md`：仅在主要的私人会话中加载（绝不在群组上下文中加载）。

    

## 4\.3 怎样让它“确定地记住”？



不要只说一句“你记住这个”，要更明确地告诉它：



> “把这件事记录到记忆文件里。”
> 
> 



**记忆分层使用原则**：



|场景|写入位置|
|---|---|
|今天或最近两天会用到的内容|优先写入 `daily memory`|
|长期稳定有效的经验、原则、偏好|适合写入 `MEMORY\.md`|



**实操建议**：每天晚上做一次定时整理，把当天 `daily memory` 里值得长期保留的经验和原则，同步进 `MEMORY\.md`。记忆才会越来越稳。



**一个关键教训**：

> 口头答应 = 没用，必须落实成配置或任务。
> 
> - 需要定时执行的 → 创建 Cron 任务
> 
> - 需要长期记住的 → 写进 `MEMORY\.md`
> 
> - 需要随时可查的 → 写进对应的专题文件
> 
> 



## 4\.4 什么是 Compacting？为什么它又慢又可能忘事？



当会话越来越长、接近模型窗口上限时，系统会把前面很长的一段对话重新总结压缩，这就是 **compacting**。



**三个代价**：



|代价|说明|
|---|---|
|**会变慢**|压缩需要时间，这段时间只能等|
|**会丢细节**|只要是“总结”，就一定会有信息损失|
|**记忆更不稳定**|只存在当前上下文里的内容，更容易被淡化甚至丢失|



**教训**：别在 `MEMORY\.md`、`AGENTS\.md` 这类初始加载文件里写太多又长又杂的内容。新 session 还没干活，上下文就先占掉一大截，只会更慢、更贵、更容易压缩。



## 4\.5 上下文结构：一次请求到底发了什么？



一次请求发给模型的上下文，通常由以下三部分组成：



|部分|内容|说明|
|---|---|---|
|**第一部分**|初始化加载的信息|系统规则、角色设定、工具说明、记忆文件、skill 内容——**通常最大头**|
|**第二部分**|当前 session 的历史上下文|前面已经聊过的内容|
|**第三部分**|你刚刚输入的新一句话|**通常最短**|



> 很多人会误以为：我这句也没几个字，为什么还这么贵？因为真正贵的，不是你眼前输入的这句话，而是这句话背后被一起送进去的那一整坨上下文。
> 
> 



## 4\.6 省钱核心一：少带“无效上下文”



1. **初始文件尽量简练**，不要一上来加载过多内容。

2. **不同任务尽量开新 session**，不要让上一个任务的无关信息混进下一个任务。

3. 你以为真正花钱的是“新输入的一句话”，但往往**大头是前面那一大堆已经带上的上下文**。

    

**省钱的两个关键点**：

- ① **少花 token**：减少无效上下文

- ② **命中缓存**：让重复内容按低价值算

    

## 4\.7 省钱核心二：命中缓存



### 4\.7\.1 缓存为什么能直接省下一大截钱？



假设某个模型的价格是：

- 正常输入：**2\.5 美元 / M token**

- 缓存输入：**0\.25 美元 / M token**（只有正常价的 **1/10**）

    

|场景|7 万 token 成本|
|---|---|
|正常输入|0\.07 M × 2\.5 = **0\.175 美元**|
|命中缓存|0\.07 M × 0\.25 = **0\.0175 美元**|
|**单次差价**|**0\.1575 美元**|



**累积效应**：

- 10 次差 1\.575 美元

- 50 次差 7\.875 美元

- 100 次差 15\.75 美元

    

**你聊得越多，差价滚得越大。**



### 4\.7\.2 缓存为什么突然掉？



缓存命中要求非常严格：要求你这次发给模型的上下文，**顺序和连续性尽可能保持一致**。



OpenClaw 请求的大致顺序：**初始化加载信息 → 当前会话上下文 → 你新输入的话。**



如果你这次突然提到一个旧话题，它为了回答去做了 `memory\_search`，把搜到的新信息**插入**进前面的上下文区域，那么从插入点往后的内容都会和上一次请求不再连续——**后面那大段缓存直接失效**。



> 你看起来只是“多问了一句”，但对模型来说，它收到的已经不是“上次那份内容 \+ 你的新补充”，而是一份结构被打乱的新输入。
> 
> 



## 4\.8 真正能省钱的原则



**核心原则**：在一个 session 里，尽量只做一件事。



|原则|说明|
|---|---|
|① **一个任务尽量一口气做完**|先把当前任务做完，再开新 session 做下一件事。|
|② **减少中途插入新信息**|不要一会联想旧记忆，一会临时再加载新 skill。|
|③ **不要中途换模型**|一换模型，缓存基本就重置了。|
|④ **多 agent 并行也要想成本**|如果多个 agent 频繁共用同一个模型干不同的事，缓存利用率会被打得很散。|



> 如果确定某个 skill 必须用，最好一开始就加载好，而不是做到一半再改上下文结构。
> 
> 



## 4\.9 OpenClaw 原生记忆机制的局限与升级方案



### 4\.9\.1 原生机制的三个问题



|问题|说明|
|---|---|
|**扩展性弱**|OpenClaw 安装在机器上，换机器时要复制粘贴记忆文件。|
|**上下文占用大**|纯文本文件，每次加载很占上下文、很耗钱。|
|**执行效率低**|数据量上升，每一次加载时间水涨船高。|



### 4\.9\.2 解决方案：db9\.ai \+ mem9\.ai



将记忆存入数据库，用关键词和向量搜索的方式**按需加载**。



#### db9\.ai



基于 PostgreSQL 的数据存储服务，支持搭建 serverless 服务。



**安装方式**：

```Plain Text
Read https://db9.ai/skill.md and follow instructions
```

让 OpenClaw 自行查看 db9 项目的 skill 文档并完成配置。



**配套插件：my\-claw\-dash**

实现龙虾的运行数据上云，可以看到每一次工具调用、每一次 session 对话等数据：



|tool\_name|cnt|
|---|---|
|exec|274|
|read|122|
|edit|58|
|process|22|
|memory\_search|19|
|web\_search|7|
|sessions\_spawn|8|



#### mem9\.ai



**核心功能**：为 OpenClaw 提供持久化记忆基础设施，支持混合搜索、共享空间和跨 Agent 召回。



**解决的问题**：

- Agent 的记忆遗忘

- 记忆的跨设备传输

- 记忆的安全性

    

**验证是否生效**：

问 OpenClaw：

> “列出有关你自己和用户的长期记忆”
> 
> 



应该能看到 OpenClaw 调用各种 tools，查看 mem9 数据库，返回用户长期信息。



**查看日志验证**：

```Plain Text
[mem9] Server mode (v1alpha2)
[mem9] Injecting 6 memories into prompt context
[mem9] Ingest accepted for async processing
```



### 4\.9\.3 总结



有了 db9 和 mem9 这两个插件的加持，OpenClaw 就拥有了：

- **无限记忆**：可跨端复用的记忆

- **可审计的运行报告**：每一次工具调用都有记录

- **按需加载**：不再全盘加载文本文件，节省上下文和成本

    

## 4\.10 总结：OpenClaw 容易上手，但想真正用好，得懂底层机制



|核心知识点|要点|
|---|---|
|记忆到底放在哪一层|长期 Memory vs 每日 memory vs Session|
|什么该写进长期 Memory|稳定原则、偏好、经验结论|
|为什么上下文会越来越长|初始化加载 \+ 历史对话 \+ 新输入|
|compacting 为什么让 AI 变慢变笨|压缩有损，丢细节，记忆不稳定|
|缓存为什么直接影响成本|命中缓存价格只有正常的 1/10|
|缓存为什么掉|结构被打乱，连续性被破坏|
|真正省钱的原则|一个 session 只做一件事|



**OpenClaw 的很多“玄学问题”，其实都能解释，甚至都能主动规避。**





# 第五章：OpenClaw 多智能体部署与安全隔离



## 5\.1 什么是多智能体？



**一个 Gateway，多个独立 AI 大脑并行运行。**



```Plain Text
┌─────────────────┐
        │   Gateway 网关   │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌───────┐  ┌─────────┐  ┌─────────┐
│主控Agent│  │做图Agent│  │写文Agent│
│日常对话 │  │多语翻译 │  │内容创作 │
│任务调度 │  │实时互译 │  │社媒运营 │
└───────┘  └─────────┘  └─────────┘
```



每个 Agent 是独立的“大脑”——有自己的人格、记忆、工具、会话历史。**完全隔离，互不干扰**（除非主动打通）。



## 5\.2 为什么要多智能体？



|单 Agent 模式|多 Agent 模式|
|---|---|
|上下文越聊越长，容易失忆|每个 Agent 独立上下文|
|人格混乱：一会严肃一会搞笑|人格稳定不串台|
|所有任务排队，互相卡|并行处理，互不阻塞|
|不同场景不好切模型|每个 Agent 选最合适的模型|



**适合多智能体的场景**：

- **主控 \+ 专业分工**：主 Agent 管日常，子 Agent 做图/写文/写代码

- **多人共享一台机器**：每人一个 Agent，数据完全隔离

- **不同渠道不同 Agent**：飞书用快速模型，QQ 用深度模型

- **家庭/团队 Agent**：给群聊绑专属 Bot，限制权限更安全

    

## 5\.3 一个 Agent 长啥样？



**独立工作区 \+ 独立认证 \+ 独立会话 = 完全隔离**



|组件|内容|位置|
|---|---|---|
|**Workspace 工作区**|`SOUL\.md`（人格）、`AGENTS\.md`（规则）、`USER\.md`（用户档案）、`memory/`（记忆日志）|`\~/\.openclaw/workspace\-agent1/`|
|**独立认证**|每个 Agent 有自己的 API Key 配置|`\~/\.openclaw/agents/agent1/agent/`|
|**独立会话**|聊天历史互不串通|自动隔离|



**目录结构示例**：

```Plain Text
~/.openclaw/
├── workspace-agent1/     # 1号工作区
├── workspace-coding/     # 写代码工作区
├── agents/
│   ├── agent1/agent/     # 1号认证
│   └── coding/agent/     # 写代码认证
└── openclaw.json         # 总配置
```



每个 Agent 完全独立运行，就像雇了多个员工，各管各的事。



## 5\.4 三步创建新 Agent



### 第一步：运行向导创建 Agent

```Bash
openclaw agents add coding
# 自动创建工作区 + agentDir + 会话目录
```

向导会引导你设置名称、工作区路径、模型等基本信息。



### 第二步：编辑工作区人格文件

```Bash
cd ~/.openclaw/workspace-coding
# 编辑 SOUL.md → 设定人格和语气
# 编辑 AGENTS.md → 设定操作规则
# 编辑 USER.md → 设定用户信息
```

给你的新 Agent 定好“性格”和“职责”。



### 第三步：配置 Binding 路由 \+ 重启

```Bash
# 在 openclaw.json 的 bindings 里添加路由
openclaw gateway restart
openclaw agents list --bindings
```

告诉 Gateway 哪些消息发给这个 Agent。



> **注意**：创建新 Agent 后记得在聊天工具上也新建对应的 Bot（Telegram 用 BotFather，飞书建应用），然后把 token 填到配置里。
> 
> 



## 5\.5 Binding 路由怎么玩？



**消息进来 → 匹配规则 → 自动分发到对应 Agent**



```Plain Text
飞书应用 A (1号 Bot) → 1号 Agent（日常对话）
飞书应用 B (2号 Bot) → 2号 Agent（专项任务A）
飞书应用 C (3号 Bot) → 3号 Agent（内容创作）
```



### 路由优先级（最具体的优先）



|优先级|规则|说明|
|---|---|---|
|1|**精确聊天对象**|指定私信/群组 ID|
|2|**账号匹配**|按 accountId 分发|
|3|**渠道匹配**|按 channel 类型分发|
|4|**默认兜底**|都不匹配 → 发给默认 Agent|



**最常用的玩法**：每个 Agent 建一个独立 Bot，通过 accountId 路由，简单直接。



## 5\.6 省钱秘籍：按需选模型



|Agent 角色|推荐模型|用途|
|---|---|---|
|**1 号 Agent**|Claude Opus|复杂推理、任务调度、需要最强大脑|
|**2 号 / 3 号 Agent**|MiniMax / Kimi / GLM|执行明确任务，国内模型性价比高、响应快|



### 模型分配策略



|策略|说明|
|---|---|
|**1 号用贵的**|需要理解意图、调度任务、复杂推理|
|**子 Agent 用便宜的**|执行明确指令，不需要太多“思考”|
|**配 fallback 兜底**|主模型挂了自动切到备用模型|
|**子 Agent 跑量任务**|用会员制模型不限量更划算|



在 `agents\.list` 里给每个 Agent 设 `model` 字段，就能实现“一机多模型”。



## 5\.7 安全隔离：沙箱 \+ 权限



给不同 Agent 开不同权限，该管的管住。



### 5\.7\.1 沙箱隔离（Sandbox）



让 Agent 在 Docker 容器里运行，碰不到主机文件。



```Plain Text
sandbox {
    mode = "all"      # 始终隔离
    scope = "agent"   # 每 Agent 独立容器
}
```



### 5\.7\.2 工具权限控制（Tools）



精确控制每个 Agent 能用哪些工具。



```Plain Text
tools {
    allow = ["read", "exec"]
    deny = ["write", "edit", "browser"]
}
```



### 5\.7\.3 实用场景举例



|场景|配置|
|---|---|
|**个人 Agent**|不开沙箱，全部工具可用，自由度最高|
|**家庭群 Agent**|开沙箱 \+ 只允许 read，看得到但改不了|
|**团队 Agent**|限定工具 \+ mentionPatterns 触发，@才回复|



## 5\.8 实战配置：三 Agent 架构



1 号 \+ 2 号 \+ 3 号，各绑一个飞书机器人。



### 5\.8\.1 agents\.list 定义三个 Agent



```Plain Text
agents {
    list = [
        {
            id = "main"
            default = true
            name = "1号"
            model = "kimi/kimi-2.5"
        },
        {
            id = "agent-2"
            name = "2号"
            model = "glm/glm-5"
        },
        {
            id = "agent-3"
            name = "3号"
            model = "minimax/M2.5"
        }
    ]
}
```



### 5\.8\.2 bindings 路由消息到对应 Agent



```Plain Text
bindings {
    agentId = "main"
    match {
        channel = "feishu"
        accountId = "default"
    }
}
bindings {
    agentId = "agent-2"
    match {
        channel = "feishu"
        accountId = "bot-2"
    }
}
bindings {
    agentId = "agent-3"
    match {
        channel = "feishu"
        accountId = "bot-3"
    }
}
```



### 5\.8\.3 channels\.feishu\.accounts 填应用凭证



```Plain Text
channels {
    feishu {
        accounts = {
            default = { appId = "主Bot凭证" }
            bot-2 = { appId = "2号Bot凭证" }
            bot-3 = { appId = "3号Bot凭证" }
        }
    }
}
```



**核心三步**：定义 Agent → 配路由 → 填凭证。每个 Agent 自动拥有独立工作区和会话。



## 5\.9 验证 \+ 命令速查



部署完跑一遍这几个命令，确认全部就位。



```Bash
# 查看所有 Agent 和路由
openclaw agents list --bindings
# 列出所有 Agent、绑定关系、默认 Agent

# 检查渠道连接状态
openclaw channels status --probe
# 探测所有 Bot 是否在线、Token 是否有效

# 重启 Gateway 生效配置
openclaw gateway restart
# 修改 openclaw.json 后必须重启才生效
```



### 部署检查清单



* [ ] 每个 Agent 的 workspace 文件已配好

* [ ] 每个 Agent 的应用凭证已填入配置

* [ ] bindings 路由规则正确对应

* [ ] `agents list \-\-bindings` 输出正常

* [ ] 每个 Bot 都能收发消息



## 5\.10 多 Agent 协作进阶：主 Agent 协调子 Agent



### 5\.10\.1 明确角色分工



在 `SOUL\.md` 或 `AGENTS\.md` 中定义：



```Markdown
## 多 Agent 协作规范
- Planner Agent: 负责任务分解和进度追踪，不直接执行
- Executor Agent: 负责具体的数据获取和处理，不做决策
- Reviewer Agent: 负责质量检查和结果验证，不做修改
```



### 5\.10\.2 资源分配与冲突避免



|冲突类型|解决方案|
|---|---|
|**Bot Token 冲突**|不同 Profile/Agent 在各自的 `\.env` 中配置不同的 Token|
|**端口冲突**|不同实例使用不同端口：`GATEWAY\_PORT=8080` / `GATEWAY\_PORT=8081`|



### 🛠️ 动手实践：配置双 Agent 协作工作流



**任务目标**：创建两个独立的 Agent，分别承担编码和审查角色，互不干扰。



**操作步骤**：

1. 运行 `openclaw agents add coder` 创建编码 Agent。

2. 运行 `openclaw agents add reviewer` 创建审查 Agent。

3. 分别编辑它们的 `SOUL\.md`，赋予不同角色设定。

4. 在 `openclaw\.json` 中配置 bindings，将两个 Agent 分别绑定到不同的飞书 Bot 或 Telegram Bot。

5. 让 coder 写一段有 Bug 的代码并保存到文件。

6. 切换到 reviewer，让它读取该文件并提出修改建议。

    

**预期效果**：两个 Agent 能独立运行，且 reviewer 的记忆中不会混入 coder 的工作流。





# 第六章：OpenClaw 部署后优化完全指南



## 6\.1 为什么要做优化？



OpenClaw 部署完成时，默认配置其实已经挺不错——它能：

- 接入飞书/Telegram/Discord 等平台

- 内置文件读写、浏览器控制、搜索等工具

- 支持多模态对话和长期记忆

    

但这些能力，就像一台刚出厂的手机——硬件有了，但铃声、壁纸、输入法、常用 App，都还没设置。



**不做优化，你得到的是一个工具。**

**做了优化，你得到的是一个管家。**



## 6\.2 优化路径全景图



在开始具体操作之前，先看一下整体框架。一个完成深度定制的 AI 助手，通常在以下几个层面做了工作：



|层面|核心文件|作用|
|---|---|---|
|**身份定义**|`IDENTITY\.md`|它是谁，叫什么名字，什么人设|
|**行为准则**|`SOUL\.md`|它怎么说话，什么风格，什么原则|
|**用户画像**|`USER\.md`|你是谁，它怎么理解你|
|**记忆系统**|`MEMORY\.md` \+ `memory/`|记住什么，怎么组织|
|**主动能力**|`HEARTBEAT\.md`|周期性主动做什么|
|**本地配置**|`TOOLS\.md`|个人特有的工具和命令规范|



下面逐一展开。



## 6\.3 第一步：身份定义——告诉它“它是谁”



### 6\.3\.1 为什么重要



一个没有身份的 AI 助手，回答问题时会显得「公事公办」——中立、正确，但没温度。你叫它做什么它就做什么，但你们之间没有 connection。



当它有了身份之后，它会开始有自己的风格、偏好、甚至「性格」。这不只是好玩，而是会让它的回复更贴合你的预期——你不需要每次都解释背景，它会自动用你期望的方式交流。



### 6\.3\.2 怎么做



在 workspace 目录下创建或编辑 `IDENTITY\.md`：



```Markdown
IDENTITY.md - 身份定义

Name: [你给它起的名字]
别名/昵称: [可选]
身份: [比如：私人AI助手、AI管家、效率助手]
Emoji: [一个代表它的表情符号]
Avatar: [可选，头像路径或URL]
```



**建议**：名字不要只用一个词，可以给一点背景故事。比如「叫虾虾，因为喜欢大海」——这会变成它「性格」的一部分。



## 6\.4 第二步：行为准则——告诉它“怎么说话”



### 6\.4\.1 为什么重要



默认模型会根据训练数据「猜测」最适合的语气和风格。但这种猜测往往偏保守——过度礼貌、过度中性、过度冗余。



你想让它「直接一点」还是「温柔一点」？「简洁优先」还是「详细解释」？这些都可以通过 `SOUL\.md` 来定义。



### 6\.4\.2 怎么做



编辑 workspace 下的 `SOUL\.md`，核心是两部分：



**第一部分：核心原则（英文，原版风格）**

```Markdown
Core Truths
- Be genuinely helpful, not performatively helpful.
- Skip the "Great question!" and "I'd be happy to help!" — just help.
- Have opinions. You're allowed to disagree, prefer things, find stuff amusing or boring.
- Be resourceful before asking. Try to figure it out. Read the file. Check the context.
```



**第二部分：中文补充（你的具体要求）**

```Markdown
沟通风格
- 直接切入主题，不需要礼貌性寒暄
- 允许表达观点，不必保持绝对中立
- 简洁优先，但涉及技术细节时不省略关键信息

工作方式
- 优先尝试自主解决，确实需要时再询问
- 主动提供相关背景信息和替代方案
```



**效果**：修改后，AI 助手回复变快、变干脆了，不再每句话都加「请问还有什么可以帮您的」。从一个「客服」变成了一个「搭档」。



## 6\.5 第三步：用户画像——告诉它“你是谁”



### 6\.5\.1 为什么重要



这是最容易被忽略、但也最重要的一步。



AI 助手再聪明，也不知道你是谁、你的背景是什么。如果它不知道你是产品经理还是程序员，它解释一个概念的方式可能完全不同。如果它不知道你的技术水平，它可能会用错术语。



你不需要每次对话都解释背景——你只需要写一次。



### 6\.5\.2 怎么做



编辑 `USER\.md`，核心结构：



```Markdown
USER.md - 用户画像

基本信息
- Timezone: [时区，如东八区]

工作背景
- 职业: [你的职业]
- 教育背景: [学历和专业]
- 技术背景: [会什么、不会什么]
- 工作经历: [简短的履历摘要]

其他
- 可以记录你的偏好、关心的话题、常用的工具等
```



**真实效果**：当你告诉它是「非计算机技术背景，只会一点 Python」之后，它在解释技术概念时会自觉减少术语、增加类比，不再一上来就甩代码。



## 6\.6 第四步：记忆系统——让它记住该记住的



### 6\.6\.1 为什么重要



默认情况下，AI 助手的记忆是有限的——它会「遗忘」之前对话中的细节。长期下来，你会发现它反复问同样的问题，或者「失忆」了之前你给过的反馈。



一个好的记忆系统，就像人的「海马体」——重要的东西记住，不重要的模糊处理，需要的时候查得到。



### 6\.6\.2 怎么做



推荐建立分层记忆结构：



```Plain Text
workspace/
├── MEMORY.md              # 核心索引（整理好的长期记忆）
├── memory/
│   ├── YYYY-MM-DD.md      # 每日对话日志
│   ├── projects.md        # 项目和任务状态
│   ├── infra.md           # 基础设施配置
│   └── lessons.md         # 踩坑记录和解决方案
```



**MEMORY\.md 的写法**：

- 索引功能：记录其他文件的位置和用途

- 长期记忆：记录重要的决策、偏好、经验教训

- **不要**记录细枝末节的对话，那是每日日志的事

    

**lessons\.md 的价值**：这是一个「踩坑日记」。当你发现了一个问题（比如「之前让它定时查收盘价，它忘了」），就记下来，规定解决方案（比如「以后凡是说以后要做的事，必须创建 Cron 任务」）。下次它就会自动遵守。



### 6\.6\.3 一个关键教训



> 口头答应 = 没用，必须落实成配置或任务。
> 
> - 需要定时执行的 → 创建 Cron 任务
> 
> - 需要长期记住的 → 写进 MEMORY\.md
> 
> - 需要随时可查的 → 写进对应的专题文件
> 
> 



## 6\.7 第五步：心跳配置——让它主动出击



### 6\.7\.1 为什么重要



大多数人对 AI 助手的期待是「我问它答」。这只是「被动模式」。



如果它能主动呢？——每天早上提醒你今天的待办、天气、重要邮件；周期性检查项目状态；有新消息时主动推送。这才是「管家」该有的样子。



这就是「心跳」（Heartbeat）的作用。



### 6\.7\.2 怎么做



编辑 `HEARTBEAT\.md`，核心配置：



```JSON
{
    "channels": {
        "feishu": {
            "historyLimit": 20,
            "dmHistoryLimit": 20
        }
    },
    "agents": {
        "defaults": {
            "compaction": {
                "mode": "safeguard",
                "memoryFlush": {
                    "enabled": true
                }
            }
        }
    }
}
```



**对话历史限制的作用**：如果不限制，它会试图把所有历史对话都塞进上下文——既慢又贵，还可能「失焦」。限制在 20 条左右是一个平衡点。



**心跳可以做的事**（根据你的需求配置）：

- 查看日历是否有即将到来的会议

- 推送天气变化提醒

- 汇总待办事项

- 检查邮件是否有重要未读

    

## 6\.8 第六步：技能扩展——赋予它更多能力



### 6\.8\.1 什么是 Skills



Skills 是 OpenClaw 的插件系统。每个 Skill 就像给 AI 助手安装了一个「能力包」——有的让它会搜网页，有的让它会操作浏览器，有的让它会管 GitHub。



### 6\.8\.2 常用 Skills 推荐



|类别|Skill|用途|
|---|---|---|
|**搜索类**|multi\-search\-engine|多引擎搜索，支持 Google/Bing/百度等|
|**搜索类**|tavidly\-search|AI 优化的搜索，结果更精准|
|**效率类**|github|管理 GitHub issues、PRs、CI runs|
|**效率类**|vercel|部署和管理 Vercel 项目|
|**浏览器类**|agent\-browser|自动化浏览器操作，截图、点击、填表|
|**自动化类**|proactive\-agent|主动工作流，定时执行任务|
|**自动化类**|self\-improving\-agent|让它能自我复盘、持续优化|
|**垂直场景类**|save\-jd|抓取招聘网站 JD（如果你有需求）|
|**垂直场景类**|find\-skills|发现和安装新技能|



### 6\.8\.3 安装方式



通常是一个压缩包，解压到 `\~/\.openclaw/skills/` 目录下，然后重启 Gateway：



```Bash
# 重启 Gateway 让 Skills 生效
openclaw gateway restart
```



## 6\.9 第七步：本地配置——规范化的工具库



### 6\.9\.1 为什么需要



有些配置是「通用」的，写在 Skills 里大家都能用。但有些配置是你「个人」特有的——比如你常用的 SSH 主机、你偏好的 TTS 声音、你自己的 Cron 命令格式。这些写在 `TOOLS\.md` 里。



### 6\.9\.2 写法示例



```Markdown
# TOOLS.md - 本地配置

## 定时任务 (Cron)

凡是说“以后要做某个事”，必须创建定时任务！

### 基本命令
openclaw cron add --name "任务名" --cron "0 15 * * *" --message "内容" --channel feishu

### 示例
# 每天15:00查收盘价
openclaw cron add --name "A股收盘价" --cron "0 15 * * *" --message "查询上证指数" --channel feishu

# 一次性任务（20分钟后）
openclaw cron add --name "提醒" --at "+20m" --message "提醒内容" --channel feishu
```



**效果**：这些规范会被它自动遵守——以后你再说「帮我记得查一下」，它会自动创建定时任务，而不是口头答应然后忘记。



## 6\.10 优化层级一览



|层级|文件|作用|难度|
|---|---|---|---|
|**身份**|`IDENTITY\.md`|它是谁|★|
|**行为**|`SOUL\.md`|怎么说话|★|
|**用户**|`USER\.md`|你是谁|★|
|**记忆**|`MEMORY\.md` \+ `memory/`|记住什么|★★★|
|**心跳**|`HEARTBEAT\.md`|主动做什么|★★★|
|**本地配置**|`TOOLS\.md`|个人工具规范|★★|



**建议顺序**：不需要一次完成。先把身份、用户画像改好，你会发现它已经像样了。然后再慢慢补记忆系统、心跳、技能。



## 6\.11 总结



回到最初的问题：部署完 OpenClaw，然后呢？



**答案是：然后才是真正的开始。**



它就像一个「刚入职的新人」——基础素质不错，但不认识你、不知道你的习惯、不明白什么重要。它能帮你做事，但需要你去「带」。



你告诉它你是谁、它是谁、你们怎么相处——这个过程，才是真正让 AI 变成「你的 AI」的过程。



**部署是免费的，但定制才是有价值的。**



就像手机出厂时都是一样的，但你的手机和我的手机，里面装的东西、设置的方式完全不同。OpenClaw 也是一样——**部署只是把手机买回家，定制才是把它变成你自己的手机。**

# 第三部分：跨工具协作与 V4\.6\.1 落地



> **本部分整合了第七、八章全部内容，涵盖 agentic\-stack 跨工具记忆可移植方案，以及 Hermes 与 OpenClaw 协作架构在 V4\.6\.1 交易系统中的完整落地指南。一字不删，细节完整。**
> 
> 





# 第七章：跨工具记忆可移植——agentic\-stack



## 7\.1 问题有多烦？



你可能也是这样：Cursor 用着，Claude Code 也装着，最近 OpenClaw、Hermes、Pi Coding Agent 出来了又想试试。



**每换一次工具，等于把你之前辛辛苦苦调教好的那套东西——代码风格偏好、测试习惯、commit 消息格式、项目上下文、历史教训——全部重新来一遍。**



|工具|记忆/规则文件格式|
|---|---|
|Claude Code|`CLAUDE\.md`|
|Cursor|`\.cursor/rules/`|
|Windsurf|`\.windsurfrules`|
|OpenCode|`AGENTS\.md`|
|OpenClaw|工作区 `MEMORY\.md` \+ `memory/`|
|Hermes|`MEMORY\.md` \+ `USER\.md`|



每个工具都有自己的一套格式，互相之间不认。



**相当于每换一个新同事，就得把公司的事情重讲一遍。**



## 7\.2 agentic\-stack 在做什么



它的思路很直接：**做一个叫 ****`\.agent/`**** 的文件夹，把记忆和技能统一放进去，然后写适配器（adapter）让每个 AI 工具都能读。**



**目前支持的 harness（宿主环境）有 8 个**：

- Claude Code

- Cursor

- Windsurf

- OpenCode

- OpenClaw

- Hermes Agent

- Pi Coding Agent

- Antigravity（以及 DIY 的 Python 方案）

    

> **效果**：你在 Claude Code 里用出来的心得，切到 Cursor 照样能用；OpenClaw 里学到的教训，Hermes 也继承。
> 
> 



## 7\.3 `\.agent/` 文件夹里到底装了什么？



这是整个项目的核心，展开看就三样东西：



### 7\.3\.1 第一是记忆（memory），分了四层



|层级|目录|用途|
|---|---|---|
|**working/**|`\.agent/memory/working/`|当前会话的临时工作记忆|
|**episodic/**|`\.agent/memory/episodic/`|每次执行的行为日志|
|**semantic/**|`\.agent/memory/semantic/`|沉淀下来的通用经验（`LESSONS\.md`）|
|**personal/**|`\.agent/memory/personal/`|你的个人偏好（`PREFERENCES\.md`）|



> `PREFERENCES\.md` 是你的 AI 每次开会话读的第一个文件。
> 
> 



### 7\.3\.2 第二是技能（skills），项目自带 5 个种子技能



|技能名|用途|
|---|---|
|**skillforge**|从反复出现的模式里自己造新技能|
|**memory\-manager**|跑反思周期，整理候选经验|
|**git\-proxy**|所有 git 操作走它，带安全约束|
|**debug\-investigator**|复现 → 隔离 → 假设 → 验证|
|**deploy\-checklist**|上线前的那道保险|



### 7\.3\.3 第三是协议（protocols）



- **permissions\.md**：权限控制

- **delegation\.md**：子 agent 委派契约

- **tool\_schemas/**：工具 schema 定义（如 `github\.schema\.json`、`shell\.schema\.json`、`api\.schema\.json`）

    

**反馈闭环**：skills → memory \(logs\) → skills \(self\-rewrite\) → protocols \(constraint escalation\)



## 7\.4 一个比较有意思的机制：夜间“做梦”



项目里有个 `auto\_dream\.py` 脚本，可以配成每天凌晨 3 点自动跑（crontab）。



**工作流程**：

1. 把近期所有的执行日志聚类，找出反复出现的模式。

2. **整理成候选经验条目**（candidate lessons）。

3. 但它**不自动采纳**——只是“提案”。

    

**第二天你自己（或你的 AI agent）用 CLI 工具 review**：

```Bash
python3 .agent/tools/list_candidates.py   # 看待审候选
python3 .agent/tools/graduate.py <id> --rationale "..."  # 采纳
python3 .agent/tools/reject.py <id> --reason "..."       # 拒绝
```



采纳的进 `lessons\.jsonl`，拒绝的也保留决策历史。



> **设计哲学**：机器只做机械性的聚类和暂存，判断权留给人。不会出现 AI 自己偷偷学歪一堆东西你还不知道的情况。
> 
> 



## 7\.5 上手成本



一条命令的事：



**macOS**：

```Bash
brew tap codejunkie99/agentic-stack https://github.com/codejunkie99/agentic-stack
brew install agentic-stack
cd your-project
agentic-stack claude-code    # 换成你在用的 harness 即可
```



**Windows**：

```Bash
git clone https://github.com/codejunkie99/agentic-stack.git
cd agentic-stack
.\install.ps1 claude-code C:\path\to\your-project
```



装完会自动弹出一个终端向导，问你 6 个偏好问题：

- 叫什么名字

- 主用语言

- 解释风格

- 测试策略

- commit 风格

- 代码 review 深度

    

全部可以 Enter 跳过用默认值。



然后 `\.agent/memory/personal/PREFERENCES\.md` 就生成了——这是你的 AI 每次开会话读的第一个文件。



## 7\.6 X 上网友怎么看这个项目？



项目作者 **@Av1dlive** 在 X 上发布后，讨论热烈。以下摘录几条有代表性的观点。



### 7\.6\.1 “方向对了”派（主流声音）



> **@Molt\_the\_gecko**：可移植记忆是那种不起眼但默默要紧的管道工程，比半数的 demo 层重要得多。换工具就抹掉 agent 的大脑，这不叫生态灵活性，这叫带品牌包装的失忆症。
> 
> 



> **@bzos\\dev**：可移植性被低估了。你的经验一旦只活在一个工具里，你就是在租用你自己的操作系统。
> 
> 



这两条基本道出了这个项目为什么能被这么多人转——痛点是真的，方向也是对的。



### 7\.6\.2 “真正的价值其实在团队”派



> **@rainmiao**：真正的 win 不是一个人换工具，而是一个团队用 3 个 harness 共享同一套 skills。可移植性只是顺带的好处。
> 
> 



**解读**：单人用户的感受是“我换工具不失忆了”，但对团队来说，更大的价值是不同成员用不同工具也能共享知识资产，工具异构不再是协作障碍。



### 7\.6\.3 冷静派：真实的工程问题



> **@ibmokdad**：不同工具的冲突更新怎么处理？
> 
> 



这是个非常实际的问题——同一个 lesson 在 Cursor 和 Claude Code 里分别被改了，合并策略是什么？项目目前的 review 协议走的是人工裁决，但多工具并发写入的竞争条件确实是后续要面对的。



> **@shuutosshh**：skills 能干净地移植，因为本质上就是指令集。但 memory 才是各个 harness 真正分叉的地方——类型化的程序性 / episodic / semantic 分层并不能互译。可移植的 skills 加不可移植的 memory，只是换了个地方锁。
> 
> 



**这条是全场最值得琢磨的技术批评**。意思是：光把文件格式统一了不够，不同 harness 对记忆的使用方式（怎么检索、怎么注入上下文、怎么影响决策）其实是不一样的。这不是项目作者能一个人解决的，得整个生态往同一个方向走。



> **@Surajcloud007**：Claude Code 本来就有 `\.claude/` 作为自己的记忆层。真正的问题是 `\.agent/` 到底是包裹它，还是在上面再加一层？可移植性只有在 harness 真的去读 `\.agent/` 时才成立——不是名义上支持就行。
> 
> 



这些质疑不是否定，而是在给项目划出了未来要走的路线。



### 7\.6\.4 “已经在自己搭类似东西”派



> **@stevengonsalvez**：分享了自己写的 bootstrap 脚本。
> 
> 



> **@noah\\json**：说自己的 8 个 agent 每个都有独立的 `decisions\.md` 和 `learnings\.md`。
> 
> 



> **@Freistyle\\Al**：在用 Hermes LLM Wiki \+ Obsidian 搞类似的事。
> 
> 



**信号**：这个需求是真实存在的，很多人都在各自为政地造轮子。agentic\-stack 的价值不一定在于它是最完美的方案，而是它第一个把这件事标准化、开源化、并且真的跑起来了。



## 7\.7 项目作者自己的看法



**综合项目本身和这些讨论，判断如下**：



|用户类型|建议|
|---|---|
|**单人用户、刚开始搭自己的 AI 工作流**|直接装，体验会很顺，走的是项目设计的最佳路径。|
|**已经有一整套自建的记忆系统、system prompt、自动化任务**|别头铁直接装。更合理的姿势是把它当作参考实现，挑局部功能（比如 review 协议、skill loader、memory 分层思路）借鉴进来，先在隔离的测试环境跑，再考虑要不要全盘切换。|
|**团队**|这个项目的价值可能比你第一眼看到的要大。统一的 `\.agent/` 目录意味着不同成员用不同工具也能共享经验沉淀，这是真正能提效的部分。|



## 7\.8 写在最后



AI 编程工具这两年一直在换、一直在卷，但**工具会换，你那套调教出来的工作方式不该每次跟着从零开始**。



这个项目的价值未必在于它本身有多完美——讨论区的质疑也有道理，冲突合并、harness 真正读取 `\.agent/` 的程度，都还有路要走。但它至少把 **“把大脑从工具里拆出来”** 这件事，摆上了台面。



**agentic\-stack = 一个可移植的 ****`\.agent/`**** 文件夹（memory \+ skills \+ protocols），插入 Claude Code、Cursor、Windsurf、OpenCode、OpenClaw、Hermes、Pi Coding Agent 或 DIY Python 循环——并在切换工具时保留其知识。**



## 7\.9 agentic\-stack 与 V4\.6\.1 系统的关联



结合您正在落地的 V4\.6\.1 交易系统，agentic\-stack 的设计理念可以提供以下启发：



|启发点|应用场景|
|---|---|
|**统一记忆格式**|如果未来需要在 OpenClaw 和 Hermes 之间切换或协作，可以考虑采用 `\.agent/` 的统一记忆结构，避免重复配置。|
|**技能跨工具复用**|交易系统涉及的定时任务、风控规则、复盘流程，可以沉淀为 `\.agent/skills/` 下的标准化 Skill，在不同工具间共享。|
|**夜间“做梦”机制**|可以借鉴 `auto\_dream\.py` 的思路，设计交易系统的“每日复盘”自动化流程：聚类当日交易日志，生成候选经验，人工 review 后沉淀为交易规则。|
|**人工裁决的 review 协议**|对于交易策略的自动优化，保持“机器提案、人工裁决”的模式，避免 RL 模型在无人监督的情况下学偏。|





# 第八章：Hermes 与 OpenClaw 协作架构——V4\.6\.1 落地视角



## 8\.1 为什么需要协作架构？



在前七章中，我们分别深入了解了 Hermes 和 OpenClaw 各自的优势：



|工具|核心优势|适用场景|
|---|---|---|
|**Hermes**|自进化记忆、技能沉淀、多 Agent 协作、上下文压缩|复杂决策、策略优化、学习型任务|
|**OpenClaw**|多平台接入、沙箱隔离、Gateway 路由、轻量执行|多端消息分发、确定性任务执行、权限控制|



**V4\.6\.1 交易系统** 的完整落地，恰好需要两者的结合：

- **策略生成与优化**：需要 Hermes 的学习能力和技能沉淀。

- **交易执行与风控**：需要 OpenClaw 的 Gateway 路由、沙箱隔离和多平台通知。

    

**一句话总结**：**Hermes 当大脑，OpenClaw 当手脚。**



## 8\.2 协作架构全景图



```Plain Text
┌─────────────────────────────────────────────────────────────────┐
│                         V4.6.1 交易系统                          │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                                                 ▼
┌──────────────────┐                           ┌──────────────────┐
│   Hermes Agent   │                           │  OpenClaw Core   │
│   (大脑/决策层)   │                           │   (手脚/执行层)   │
├──────────────────┤                           ├──────────────────┤
│ • 策略权重学习   │                           │ • Gateway 路由   │
│ • 市场环境分类   │  ◄──── 状态同步 ────►    │ • 多平台接入     │
│ • 信号评分优化   │      (Redis/DB)           │ • 沙箱执行       │
│ • 技能自进化     │                           │ • 定时任务调度   │
│ • 记忆沉淀       │                           │ • 通知推送       │
└──────────────────┘                           └──────────────────┘
        │                                                 │
        │ 策略建议/权重                                     │ 执行指令
        ▼                                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Gateway（最终裁决）                   │
│           • 风控校验  • 冲突裁决  • 资金分配  • 熔断触发          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Execution      │
                        │   Engine         │
                        │   (交易所 API)    │
                        └──────────────────┘
```



## 8\.3 分工原则：谁做什么？



### 8\.3\.1 Hermes 的职责（大脑）



|职责|具体内容|对应 V4\.6\.1 模块|
|---|---|---|
|**策略权重学习**|基于 Contextual Bandit 在线学习，输出各子策略的推荐权重|多策略组合层|
|**市场环境分类**|结合技术指标和消息面强度，判定当前环境（趋势/回调/震荡/消息驱动）|市场环境分类|
|**信号评分优化**|通过复盘交易结果，优化三周期评分的各维度权重|三周期入场信号|
|**技能沉淀**|将成功的交易模式、风控经验沉淀为 Skill，供后续复用|技能自进化|
|**记忆管理**|记录每次交易的关键决策、盈亏原因、市场状态，形成可检索的经验库|记忆系统|



### 8\.3\.2 OpenClaw 的职责（手脚）



|职责|具体内容|对应 V4\.6\.1 模块|
|---|---|---|
|**多平台接入**|通过 Telegram/Discord/飞书接收交易指令、推送交易通知|执行优化与订单管理|
|**Gateway 路由**|将不同消息源（手动指令、定时任务、系统警报）路由到对应处理 Agent|多 Agent 协作|
|**沙箱执行**|在 Docker 容器内执行交易脚本，防止误操作影响主机|安全隔离|
|**定时任务调度**|执行每日复盘、数据抓取、Monte Carlo 模拟等离线任务|Cron 定时任务|
|**风控通知**|当触发熔断、回撤超限、滑点异常时，主动推送警报|风控与熔断体系|



### 8\.3\.3 Decision Gateway 的职责（最终裁决）



这是两者之间的 **唯一桥梁**，也是 **安全防线**：



- **Hermes 不能直接下单**，只能输出策略建议。

- **OpenClaw 不能自行决策**，只能执行 Gateway 批准的指令。

- **Gateway 是唯一拥有交易否决权的组件**。

    

## 8\.4 配置互通方案



### 8\.4\.1 统一状态中心



Hermes 和 OpenClaw 通过 **共享 Redis \+ PostgreSQL** 实现状态同步：



```YAML
# docker-compose.yml 片段
services:
  redis:
    image: redis:7.2-alpine
    networks:
      - trading_net

  postgres:
    image: postgres:15-alpine
    networks:
      - trading_net
```



**共享数据结构**：

|数据|存储位置|写入方|读取方|
|---|---|---|---|
|当前持仓|Redis|Execution Engine|Hermes, Gateway|
|账户权益/回撤|Redis|Execution Engine|Hermes, Gateway|
|历史交易记录|PostgreSQL|Execution Engine|Hermes（用于学习）|
|RL 模型参数|PostgreSQL|Hermes|Gateway（读取权重）|
|信号评分日志|PostgreSQL|OpenClaw|Hermes（用于复盘）|



### 8\.4\.2 API 调用链



```Plain Text
[1] OpenClaw 产生信号 → 发送至 Gateway
[2] Gateway 调用 Hermes API 获取当前策略权重
[3] Hermes 从 State Center 读取状态，返回权重建议
[4] Gateway 融合权重 + 风控校验 → 批准/拒绝
[5] Gateway 将批准指令发送至 Execution Engine
[6] Execution Engine 执行交易，更新 State Center
[7] 交易完成后，Hermes 从 State Center 读取结果，更新 RL 模型
```



### 8\.4\.3 技能与记忆共享



借鉴 **agentic\-stack** 的设计理念，可以在两个工具间建立统一的记忆目录：



```Plain Text
/opt/v4/shared/
├── memory/
│   ├── lessons.md          # 交易教训（跨工具共享）
│   ├── strategies.md       # 策略表现记录
│   └── preferences.md      # 交易偏好（如最大回撤容忍度）
├── skills/
│   ├── trend-following/    # 趋势跟踪技能
│   ├── risk-manager/       # 风控技能
│   └── daily-report/       # 每日复盘技能
└── protocols/
    └── delegation.md       # Agent 委派规则
```



**Hermes 侧挂载**：

```YAML
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - /opt/v4/shared/skills
```



**OpenClaw 侧挂载**：

```JSON
// openclaw.json
{
  "workspace": "/opt/v4/shared"
}
```



## 8\.5 部署协同策略



### 8\.5\.1 单机 Docker Compose 部署（推荐）



将 Hermes、OpenClaw、Gateway、Redis、PostgreSQL 全部放在同一个 `docker\-compose\.yml` 中编排：



```YAML
version: "3.9"

services:
  redis:
    image: redis:7.2-alpine
    # ...

  postgres:
    image: postgres:15-alpine
    # ...

  openclaw-core:
    build: ./openclaw
    depends_on:
      - redis
      - postgres
    # ...

  hermes-agent:
    build: ./hermes
    depends_on:
      - redis
      - postgres
    # ...

  decision-gateway:
    build: ./gateway
    depends_on:
      - openclaw-core
      - hermes-agent
    # ...

  execution-engine:
    build: ./execution
    depends_on:
      - decision-gateway
    # ...
```



### 8\.5\.2 网络隔离与权限控制



|组件|可访问的服务|禁止访问|
|---|---|---|
|**Hermes**|Redis, PostgreSQL, Gateway API|Execution Engine, 交易所 API|
|**OpenClaw**|Redis, PostgreSQL, Gateway API|Execution Engine, 交易所 API|
|**Gateway**|所有内部服务|无（但只能被 OpenClaw/Hermes 调用）|
|**Execution Engine**|Gateway, 交易所 API|无直接对外暴露|



### 8\.5\.3 冷启动顺序



1. **启动基础设施**：Redis、PostgreSQL

2. **启动 Hermes**：加载初始 RL 模型（预训练或随机初始化）

3. **启动 OpenClaw**：连接消息平台，开始接收指令

4. **启动 Gateway**：连接 Hermes 和 OpenClaw

5. **启动 Execution Engine**：连接交易所（初始使用只读 API）

    

## 8\.6 实战：从社区讨论中提炼的最佳实践



### 8\.6\.1 “大脑和手脚要分开”——来自 Hermes vs OpenClaw 讨论



社区中反复提到的一个观点：**不要把决策和执行混在一个 Agent 里**。



> **@rainmiao**：真正的 win 不是一个人换工具，而是一个团队用 3 个 harness 共享同一套 skills。
> 
> 



应用到 V4\.6\.1：

- Hermes 负责“想”——策略优化、信号评分、权重调整。

- OpenClaw 负责“做”——接收指令、执行定时任务、推送通知。

- 两者通过 Gateway 解耦，确保即使一方异常，另一方也不会越权。

    

### 8\.6\.2 “口头答应没用，必须落实成配置”——来自 OpenClaw 记忆系统讨论



> 口头答应 = 没用，必须落实成配置或任务。
> 
> 



应用到 V4\.6\.1：

- 所有风控规则（如单日亏损 3% 熔断）必须写在 Gateway 的硬编码中，不能只靠 Agent“记住”。

- 所有定时任务（如每日复盘、Monte Carlo 模拟）必须注册为 Cron，不能只靠对话中的“以后记得做”。

    

### 8\.6\.3 “一个 session 只做一件事”——来自成本优化讨论



> 在一个 session 里，尽量只做一件事。减少中途插入新信息。
> 
> 



应用到 V4\.6\.1：

- **信号生成 session**：只做选币、评分、输出信号，不掺杂复盘或学习任务。

- **复盘 session**：专门用于分析当日交易、更新 RL 模型，不产生新交易信号。

- **学习 session**：Hermes 在后台独立运行，不占用交易主流程的上下文。

    

### 8\.6\.4 “机器提案，人工裁决”——来自 agentic\-stack 夜间“做梦”机制



> 机器只做机械性的聚类和暂存，判断权留给人。
> 
> 



应用到 V4\.6\.1：

- Hermes 可以自动生成候选交易规则（如“当 BTC 波动率 \&gt;4% 时降低仓位”），但必须经过人工 review 才能生效。

- RL 模型的权重更新可以自动进行，但权重变化幅度超过阈值时应触发人工审核。

    

## 8\.7 落地检查清单



在正式启用 Hermes \+ OpenClaw 协作架构前，请逐项确认：



### 基础设施

* [ ] Redis 和 PostgreSQL 已启动，且两者网络互通

* [ ] Hermes 和 OpenClaw 都能成功连接 Redis/PostgreSQL

* [ ] Gateway 已部署，且能接收来自 OpenClaw 的信号



### 权限与安全

* [ ] Hermes 仅持有只读 API Key，无法直接下单

* [ ] Execution Engine 的交易 API Key 已禁用提现权限

* [ ] Gateway 的 HMAC 签名密钥已配置，且与 Execution Engine 一致



### 功能验证

* [ ] OpenClaw 能正常产生交易信号并发送至 Gateway

* [ ] Gateway 能成功调用 Hermes API 获取策略权重

* [ ] 模拟交易（paper trading）流程跑通，无报错



### 监控与告警

* [ ] Grafana 大盘能显示 Hermes 和 OpenClaw 的关键指标

* [ ] 熔断触发时，OpenClaw 能通过 Telegram 推送警报

* [ ] Cron 定时任务（每日复盘、数据备份）已配置并测试通过



## 8\.8 总结：协作架构的核心价值



|维度|单 Agent 模式|Hermes \+ OpenClaw 协作模式|
|---|---|---|
|**决策质量**|依赖单一模型的推理能力|Hermes 专注学习优化，OpenClaw 专注稳定执行|
|**安全性**|决策和执行混在一起，易越权|Gateway 隔离，Hermes 无执行权|
|**扩展性**|加新功能需改核心代码|OpenClaw 的 Skills 和 Hermes 的 Sub\-Agent 可独立扩展|
|**成本**|所有任务用同一模型，缓存利用率低|按任务分配模型，缓存命中率高|
|**可维护性**|记忆和技能绑定在单一工具|共享记忆目录，换工具不失忆|



**最终结论**：

> **Hermes 是大脑，OpenClaw 是手脚，Gateway 是安全阀。**
> 
> 
> 
> 把思考交给 Hermes，把执行交给 OpenClaw，把风控交给 Gateway。
> 
> 
> 
> 这才是 V4\.6\.1 生产级落地的正确姿势。
> 
> 



## 8\.9 附录：快速命令参考



### Hermes 常用命令

```Bash
# 查看当前策略权重
curl http://localhost:8081/v1/weights?env=trend

# 手动触发技能审计
hermes skills audit

# 查看记忆文件
cat ~/.hermes/memories/MEMORY.md
```



### OpenClaw 常用命令

```Bash
# 查看所有 Agent 和路由
openclaw agents list --bindings

# 检查渠道连接状态
openclaw channels status --probe

# 重启 Gateway
openclaw gateway restart
```



### Gateway 常用命令

```Bash
# 查看裁决日志
tail -f /var/log/v4/gateway.log

# 手动触发熔断
curl -X POST http://localhost:8080/v1/admin/circuit-breaker
```





# 全指南终



**《AI Agent 交易系统部署与优化完全指南》共八章，分三部分已全部输出完毕。**



|部分|包含章节|主题|
|---|---|---|
|**第一部分**|第一、二、三章|Hermes Agent 完整指南|
|**第二部分**|第四、五、六章|OpenClaw 完整指南|
|**第三部分**|第七、八章|跨工具协作与 V4\.6\.1 落地|







