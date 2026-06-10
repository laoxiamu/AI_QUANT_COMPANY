# AI_CAPABILITY_BASELINE.md

**版本：** 1.1  
**初始生成：** 2026-06-01  
**最后更新：** 2026-06-05（补充 Desktop Commander Mac执行能力、量化环境已安装状态、x-reader 工具）  
**审计阶段：** Phase 0A · AI能力基础设施建设  
**状态说明：** VERIFIED = 实际执行验证 | PARTIAL = 部分验证 | UNVERIFIED = 未验证 | OUTDATED = 已过期

---

## 1. Claude Cowork（主工作模式）

| 能力项 | 状态 | 备注 |
|--------|------|------|
| 自然语言理解与推理 | VERIFIED | 多次对话已验证 |
| 结构化文档输出（Markdown）| VERIFIED | 持续使用中 |
| 多轮对话上下文保持 | VERIFIED | 当前对话已验证 |
| 调用 Desktop Commander 工具 | VERIFIED | 本次审计全程依赖 |
| 调用 Web Fetch 工具 | VERIFIED | 外部调研已使用 |
| 调用 Bash 工具（沙盒） | VERIFIED | 沙盒环境，网络受限，仅限本地操作 |
| 跨对话记忆 | VERIFIED | 通过文件系统（Memory Core）实现 |
| 网络访问（web_fetch） | PARTIAL | 可访问大多数公开网站；mp.weixin.qq.com 被安全策略屏蔽 |

---

## 2. Desktop Commander（Mac 本地执行——关键能力）

> **重要说明（2026-06-05 确认）：** Desktop Commander 不只是「文件访问工具」，而是一个**完整的 Mac 本地执行环境**。`start_process` 可在用户 Mac 上执行任意 shell 命令，包括运行 Python 脚本、安装工具等。这是 Claude 直接执行小任务的主要通道，无需经过 Codex。

| 能力项 | 状态 | 备注 |
|--------|------|------|
| 本地文件读取 | VERIFIED | 全程使用 |
| 本地文件写入 | VERIFIED | 全程使用 |
| 目录列举 | VERIFIED | 已列举多层结构 |
| **在 Mac 上执行 shell 命令（start_process）** | **VERIFIED** | **可运行 Python、pip、git 等任意命令；2026-06-05 验证（安装 x-reader、执行回测测试）** |
| **Python 脚本直接执行** | **VERIFIED** | **通过 start_process 在用户 Mac 的 Python 3.13.5 环境运行** |
| 进程输出读取（read_process_output）| VERIFIED | 实时轮询长时间运行的进程 |
| 文件编辑（edit_block）| VERIFIED | 多次使用 |
| 版本 | VERIFIED | Desktop Commander v0.2.41 |
| 运行平台 | VERIFIED | macOS（arm64），zsh 默认 shell |
| 文件系统访问权限 | VERIFIED | allowedDirectories=[]，无路径限制 |

**使用规范（DEC-021）：** ≤50行、一次性的 Python 脚本 → Claude via Desktop Commander 直接执行；>100行、需要大量迭代的复杂实现 → 交给 Codex。

---

## 3. Python 量化环境（用户 Mac，2026-06-04 初始化完成）

| 能力项 | 状态 | 备注 |
|--------|------|------|
| Python3 可用 | VERIFIED | 3.13.5，`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` |
| pip3 可用 | VERIFIED | pip 25.1.1 |
| **pandas** | **VERIFIED** | **2.3.3，2026-06-04 安装** |
| **numpy** | **VERIFIED** | **2.4.6，2026-06-04 安装** |
| **vectorbt** | **VERIFIED** | **1.0.0，2026-06-04 安装；端到端回测管线已验证** |
| **ccxt** | **VERIFIED** | **4.5.56，2026-06-04 安装（Binance数据获取）** |
| **matplotlib** | **VERIFIED** | **3.10.9，2026-06-04 安装** |
| **scipy** | **VERIFIED** | **1.17.1，2026-06-04 安装** |
| **statsmodels** | **VERIFIED** | **0.14.6，2026-06-04 安装** |
| requests | VERIFIED | 系统预装 |
| SSL 证书 | VERIFIED | 2026-06-05 修复（Install Certificates.command 已执行）|
| git HTTP/1.1 | VERIFIED | `git config --global http.version HTTP/1.1` 已设置（解决 Clash Verge 兼容问题）|

---

## 4. x-reader（多平台内容抓取工具，2026-06-05 安装）

| 能力项 | 状态 | 备注 |
|--------|------|------|
| **pip 安装** | **VERIFIED** | **x-reader 0.2.0，2026-06-05 安装于用户 Mac** |
| **Playwright Chromium** | **VERIFIED** | **2026-06-05 安装，headless 模式验证通过** |
| 微信公众号抓取 | VERIFIED | Jina 失败后自动切换 Playwright headless，成功抓取全文 |
| Bilibili 内容 | PARTIAL | API 方式，理论可用，未实际测试 |
| 小红书 | PARTIAL | 需一次性登录（x-reader login xhs），未配置 |
| YouTube | PARTIAL | 需 yt-dlp，未安装 |
| 普通网页 | VERIFIED | Jina fallback，通过 web_fetch 直接调用 |
| MCP server 模式 | UNVERIFIED | mcp_server.py 存在，未配置到 Cowork |
| Obsidian vault 输出 | UNVERIFIED | 支持配置，未配置 |
| 安装路径 | VERIFIED | 通过 Desktop Commander 安装于用户 Mac 的 Python 环境 |

**使用方式：** 通过 Desktop Commander 运行 Python 脚本调用 `UniversalReader`；批量抓取已验证（20篇微信文章，约2分钟）。

---

## 5. Cowork 沙盒 Bash（受限环境）

| 能力项 | 状态 | 备注 |
|--------|------|------|
| 基础 shell 命令 | VERIFIED | echo、ls 等可用 |
| 网络访问 | PARTIAL | 代理限制，只能访问白名单域名（GitHub、pypi 可访问）|
| pip install（沙盒内） | PARTIAL | 可用但速度慢，超时风险高；优先用 Desktop Commander |
| Python 脚本执行 | PARTIAL | 沙盒内 Python，无外部网络访问，不适合量化回测 |

**注意：** 量化回测脚本应通过 Desktop Commander 在用户 Mac 上执行，而不是沙盒。

---

## 6. Node.js 环境

| 能力项 | 状态 | 备注 |
|--------|------|------|
| Node.js 可用 | VERIFIED | v22.22.0，nvm 管理 |
| npm | VERIFIED | 11.11.0 |
| openclaw | VERIFIED | openclaw@2026.4.8（全局安装，用途待 Phase 2 评估）|
| clawhub | VERIFIED | clawhub@0.6.1（用途待确认）|

---

## 7. Codex（异步任务执行）

| 能力项 | 状态 | 备注 |
|--------|------|------|
| 配置状态 | VERIFIED | 已配置 |
| 实际执行验证 | **VERIFIED** | **已完成 23 份 REPORT（0A-6 起至 P1-06），含信号检测/事件研究/策略回测/Bootstrap/单测；测试 38/38 通过** |
| 任务接收方式 | **VERIFIED** | Claude 写规格文件到项目目录，Codex 读取执行，结果写回，Claude 验收（文件式 handoff，DEC-061 已确认） |

**使用场景（DEC-021）：** >100行复杂实现、生产级系统代码、Phase 2 所有交易系统模块。

---

## 8. 数据资产

| 资产 | 状态 | 备注 |
|------|------|------|
| BTC/USDT 4H K线 | VERIFIED | 14,965条，2019-01-01 至 2025-12-31，零空值 |
| 存储路径 | VERIFIED | `/Users/yaomingyu/Documents/AI_QUANT_COMPANY/BTC_USDT_4H.csv` |
| 数据来源 | VERIFIED | data.binance.vision（月度压缩文件，无需VPN）|
| 数据截止 | VERIFIED | 2025-12-31（下一轮研究前需增量更新至最近完整月）|

---

## 9. Obsidian 协作

| 能力项 | 状态 | 备注 |
|--------|------|------|
| 项目目录作为 Vault | VERIFIED | .obsidian/ 目录存在且结构完整 |
| Obsidian Sync 已启用 | VERIFIED | 被动同步，Claude 写入文件后自动同步 |
| Claude 直接控制 Obsidian UI | 不支持 | Claude 通过文件系统间接协作 |

---

## 审计结论摘要（2026-06-05 更新）

**核心能力已就位：**
1. 文件读写链路：Claude Cowork → Desktop Commander → Mac 文件系统 ✅
2. **Mac 本地 Python 执行：** Claude → Desktop Commander → start_process → Python 3.13.5 ✅ **（新增，关键）**
3. **量化回测环境：** VectorBT 1.0.0 端到端验证通过 ✅
4. **BTC 历史数据：** 14,965条 4H K线就位 ✅
5. **多平台内容抓取：** x-reader 安装，微信批量抓取已验证 ✅

**待完成：**
- ~~Codex 首次实际任务验证（Phase 0A 任务 0A-6）~~ ✅ 已完成（2026-06-05 起，累计 23 份 REPORT）
- x-reader MCP server 配置到 Cowork
- 数据更新至最近完整月（下一轮研究前；当前截止 2025-12-31）
- 环境锁文件（requirements/lock）与数据哈希——Codex L1 标技术债，待补

*（版本注：本表 v1.1 头部仍标"Phase 0A"，实际项目已在 Phase 1；§7 Codex 状态于 2026-06-07 更正。）*
