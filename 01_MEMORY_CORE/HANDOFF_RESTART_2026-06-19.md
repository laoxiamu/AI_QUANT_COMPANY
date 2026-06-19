# 重启交接简报（2026-06-19）— 新对话开局优先读这一份

> 旧线程超长已弃。本简报=干净交接。读完按"新会话第一件事"执行。

## 一、当前真实状态
- **A-1 独立回弹=Dead**（历史快筛FAILED Holm p=0.32）；OI信号降级为carry风控触发候选；前向真实强平=休眠期权。
- **carry=主线**：预登记v4已APPROVED（历史可行性复核放行,不耗计数/不上线）；但**可行性复核BLOCKED**（custodian需主会话写项目外密钥,Codex沙箱做不了→需主会话做封存那步,参A-1 v5 §12 chmod-000法）。
- **采集器=已修好**（根因=Binance 2026-04-23 WS路由迁移,改`/market/ws/`,非封IP；收到92帧）。
- **TSMOM=Baseline**（定仓维度穷尽）。**A-4=Candidate排队**。
- **公司总图+PROJECT_TASK_PLAN（108任务）已建**,OPERATING_MODEL_v2已降级为策略SOP,§4退为指针。

## 二、刚做完的4棱镜独立审计核心结论（决定方向,必须折入）
1. **实盘=有条件NO-GO**：实时风控/账本/对账/对手方合规**全没建**,没有这些绝不能碰真钱（A3）。
2. **系统过度工程化**：别自建重型五层；**砍成借力的最小纸面→小额实盘闭环**——用CCXT/Freqtrade/数据商(Coinglass等),自己只写薄风控/决策门层（A2）。强平/funding/OI直接用数据商,别自建采集器。
3. **数据质量=隐藏头号风险**(contract/mark、base/quote volume、零帧都真卡过)→实盘前先建DATA_CONTRACT+校验。
4. **严谨度对齐3万在险资金**：carry不需18-24月学术级shadow,改"几月纸面+小额真钱+硬风控"。
5. **协作模型是瓶颈**：Claude额度被轮询/重读/纠错烧→**已止血**(禁codex-task-inbox-checker每15分钟+weekly-monitor)；用结构化验收包替代轮询；活跃权威文件压≤8。
6. **最没被质疑的假设**：公开数据+AI能在6月内找到可交易edge→**6月目标重定为"验证是否值得继续",设kill/pivot条件**。

## 三、根因（半个月误投,防重演）
埋头执行不质疑框架 + 流程无build-vs-buy/退步检查点 + 拿非技术Founder当唯一退步机制；超长线程+"只记执行不记假设"文件架构放大之。**修复**：build-vs-buy硬关卡、红队周期化、能力&假设登记表、短会话、实时回写计划、CTO自扛退步。

## 四、新会话第一件事 = 全项目重组（大部分派Codex,省Claude额度）
1. 归档过期/重型方案(旧蓝图、OPERATING_MODEL重型部分、历史审计)到reference,活跃权威文件压≤8。
2. 权威文件**去叙事化**(删"旧判断+纠正判断并存"污染,只留最新真值)。
3. 折入审计+OSS结论,把PROJECT_TASK_PLAN改成"借力最小闭环"新路线(非旧重型路线)。
4. 建《能力/环境登记表》《假设登记表》。
5. 跑state_check确认无滞后。

## 五、在跑Codex（会落文件,新会话harvest,别重复派）
- `AUDIT_A1_THESIS`(战略棱镜,前次4h前网络死已重派)→`STAGE_AUDITS/AUDIT_2026-06-15_A1.md`,齐4份后综合主报告。
- `RESEARCH_OSS_TOOLS`(CCXT/Freqtrade/数据商build-vs-buy)→`STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md`。
- A2/A3/A4审计已在`STAGE_AUDITS/`。carry可行性复核待主会话custodian封存后executor再跑。

## 六、待Founder D级（攒着,整理后一次给）
① 系统砍成最小借力闭环+build-vs-buy? ② carry严谨度下调? ③ 6月目标重定为"验证可行性"+kill/pivot? ④ 公司终态/阶段门(总图推荐版待确认)。

## 七、纪律（硬规矩）
每轮决策/变更**当轮**写回PROJECT_TASK_PLAN；派Codex后**必核实真在动**(别等尸体)；网络/SSH活用`codex --sandbox danger-full-access`；下"做不到X"结论前查能力登记表；短会话不堆超长线程。
