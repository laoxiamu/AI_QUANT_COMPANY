# 项目全盘审查调整清单 v1.0

**日期：** 2026-06-04  
**来源：** 基于外部调研结论 + 当前项目状态的全盘审查  
**性质：** 建议清单，标注为 EXPERIENCE 级，需用户确认后才能执行  

---

## A类：立即可以改的（低风险，高收益）

### A1. Python 量化环境初始化从 P2 提前到 P1
**问题：** 当前 Python 3.13.5 没有任何第三方库，连最基础的 pandas 都没装。  
**影响：** 只要开始跑回测，就会卡在这里。  
**行动：** Codex 执行一次安装命令，花10分钟，解锁后续所有研究工作。  
**安装清单：** pandas, numpy, ccxt, vectorbt, ta-lib, matplotlib, scipy, statsmodels

### A2. 确认并冻结架构草案
**问题：** AI_QUANT_COMPANY_ARCHITECTURE_v1.md 标注"草案，待确认"，但外部调研已验证其方向正确。  
**影响：** 架构不冻结，后续所有决策都缺乏依据。  
**行动：** Founder 确认后，将其写入 DECISION_LOG，状态从"草案"升级为"已确认"。

### A3. EXTERNAL_RESEARCH_REPORT 加入标准对话启动读取列表
**问题：** 外部调研报告已完成，但没有被纳入每次对话的标准读取范围。  
**影响：** 下次对话时，调研结论可能被遗忘。  
**行动：** 不需要每次读取全文，在 CURRENT_STATE 里加一行引用说明即可。已在文件中体现。

---

## B类：近期需要建立的（Phase 0A 剩余核心工作）

### B1. Research Protocol 正式建立
**问题：** D31（历史研究协议）存在但未提炼，当前没有"如何执行实验"的标准手册。  
**外部调研补充：** 需要加入走前向验证（Walk-Forward）分窗方法、Spearman IC 计算标准、手续费+滑点假设（各 0.1%）。  
**行动：** Claude 基于 D31 + 外部调研结论，起草新版 Research Protocol，Founder 确认后存入 06_RESEARCH。

### B2. Codex 首次任务执行与验证
**问题：** Codex 在本项目中从未做过任何实际任务，Layer 5（执行治理层）处于零验证状态。  
**风险：** 如果 Codex 配置有问题，越晚发现损失越大。  
**行动：** 设计一个最小任务（BTC 数据下载脚本），Claude 写任务规格书 → Codex 执行 → 验证结果。

### B3. 回测框架选型确认
**外部调研结论：** VectorBT 是 Phase 0A/0B 最优选择（M1 Mac 百万级订单70-100ms，适合假设统计验证）。  
**行动：** Founder 确认后，Codex 安装 VectorBT 并完成基础连通性测试（跑一次 BTC 数据的简单回测）。

---

## C类：文件结构调整（Phase 0B 执行，现在规划）

### C1. 目录结构重构时机
**当前状态：** 00~10 号目录，大部分为空。  
**外部调研确认：** 信息流驱动的目录结构更合理（架构草案第八章已定义）。  
**建议时机：** Phase 0B 启动前执行，届时目录大多为空，迁移成本接近零。  
**涉及变更：** 00_PROJECT_MANAGEMENT → 00_GOVERNANCE，01_MEMORY_CORE → 01_MEMORY，等（见架构草案第八章）。  
**现在不动的原因：** 等 Codex 验证后执行，可以自动化完成文件迁移。

### C2. 增加 Codex 任务模板目录
**问题：** 当前没有 Claude→Codex 标准任务模板，每次都要重写格式。  
**行动：** Phase 0B 建立 `04_AI_TEAM/CODEX_TASK_TEMPLATES/` 目录，存放标准任务规格模板。

### C3. 增加 Codex 执行报告回传模板
**外部调研发现：** 行业最佳实践要求 Codex 执行后必须有标准格式的"执行报告"回传给 Claude 审阅。  
**行动：** Phase 0B 建立执行报告模板，格式：完成内容、发现问题、需 Claude 裁决的架构问题。

---

## D类：暂不需要改动的（外部调研验证可保留）

| 项目 | 结论 | 理由 |
|------|------|------|
| CLAUDE.md 当前内容 | ✅ 保留 | 结构和质量符合行业标准，现阶段不需要大改 |
| Memory Core 四文件分层 | ✅ 保留 | 与 Context Pyramid 行业框架一致 |
| 风险容忍参数 | ✅ 保留 | 1000元-30000元分级符合小资金量化约束 |
| 腾讯云服务器（暂时不动） | ✅ 保留 | Phase 2 重建系统时再处理 |
| V4.6.2 冻结状态 | ✅ 保留 | 继续作为对照基准，不重新启动 |
| BTC 4H + 低频策略方向 | ✅ 保留 | 外部调研确认是小资金最优选择 |

---

## E类：工具配置层面的补充建议

### E1. Token 成本控制（立即可执行）
- 每次工作保持"新对话 sprint"模式（当前已在做，继续保持）
- Codex 任务明确指定工作目录范围，避免扫描全仓库
- CLAUDE.md 避免无限追加内容，保持在150行以内为宜

### E2. 数据下载方案确认
- 方案：Python + ccxt + Binance API（免费，数据从2017年起）
- 备选：CryptoDataDownload 网站直接下载CSV（更快，无需编程）
- 建议：先用 CryptoDataDownload 下载一次验证数据质量，再用 ccxt 建立自动化脚本

### E3. VectorBT 与 Backtrader 双轨方案（Phase 1 后考虑）
- Phase 0A/0B：只用 VectorBT（速度快，适合验证假设）
- Phase 1 后：视需要引入 Backtrader 做事件驱动二次验证（更接近真实交易）
- NautilusTrader：Phase 2/3 才需要考虑（机构级，当前复杂度过高）

---

## 执行优先级汇总

| 优先级 | 项目 | 执行者 | 时机 |
|--------|------|--------|------|
| P0 | A2: 架构草案冻结 | Founder 确认 | 本次对话 |
| P0 | B1: Research Protocol | Claude 起草 → Founder 确认 | 下一次对话 |
| P0 | A1: Python 环境初始化 | Codex | Codex 验证任务 |
| P0 | B2: Codex 首次任务 | Claude 写规格 + Codex 执行 | 本周 |
| P0 | B3: VectorBT 安装测试 | Codex | 随 A1 一起执行 |
| P1 | C1: 目录结构重构 | Codex | Phase 0B 启动前 |
| P1 | C2/C3: 任务模板建立 | Claude | Phase 0B |

---

*本文件为建议清单，EXPERIENCE 级，所有调整需 Founder 确认。*
