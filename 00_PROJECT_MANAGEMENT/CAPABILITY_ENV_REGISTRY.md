# 能力/环境登记表

**用途：** 下"做不到X"或"环境支持Y"结论前，必须先查本表。防止重复踩同一个坑，或因不了解工具能力而做出错误的技术判断。  
**更新规则：** 每次发现新能力/限制/环境事实，当轮更新。发现表中条目已过期，直接修改并注明日期。  
**维护者：** Claude（主理人）；Codex 执行过程中发现的事实须通过任务报告回传，由 Claude 写入。

---

## 1. Codex CLI 执行环境

| 能力项 | 状态 | 详情 | 最后验证 |
|---|---|---|---|
| Codex CLI 直调 | ✅可用 | 配方见 `04_AI_TEAM/CODEX_DIRECT_CALL_RUNBOOK.md`；需 `代理env + </dev/null + workspace-write` | 2026-06-11 |
| `--sandbox workspace-write` 模式 | ✅可用 | 文件读写正常；**无 shell 网络访问**（pip install/curl 均失败） | 2026-06-11 |
| `--sandbox danger-full-access` 模式 | ✅可用 | 有完整 shell 网络权限；可 SSH、pip install、curl | 2026-06-11 |
| Codex nohup 长时间任务 | ✅可用 | 跑批首选 Codex nohup；夜间定时不可靠（两次事故） | 2026-06-13 |
| Codex 写项目外密钥/文件 | ❌不可用 | Codex 沙箱内无法写项目目录外文件（custodian 封存必须主会话人工操作） | 2026-06-15 |
| Codex TASK_INBOX 完成通知 | ✅可用 | Codex 完成后写 `04_AI_TEAM/TASK_INBOX/{ID}_DONE.json` | 2026-06-14 |
| Codex Skills（14个） | ✅已安装 | PlanToDelivery/女娲/达尔文/TDD等；需重启 Codex 后新会话识别；见 `CODEX_SKILLS_INSTALL_LOG_2026-06-14.md` | 2026-06-14 |

---

## 2. 服务器环境（腾讯云 SG 轻量）

| 能力项 | 状态 | 详情 | 最后验证 |
|---|---|---|---|
| SSH 访问 | ✅可用 | root@43.160.200.224；需经住宅代理跳板 | 2026-06-15 |
| 新加坡跳板代理 | ✅必须保持 | Clash 链式代理（本地→腾讯SG→SG住宅商家）；双跳致 VM下载/DC断联 | 2026-06-14 |
| Binance REST API（服务器端） | ✅可用 | fapi HTTP200 正常；REST 不受 IP 限制 | 2026-06-15 |
| Binance WS 旧路由（`/ws/`） | ❌不可用 | `wss://fstream.binance.com/ws/!forceOrder@arr` → 0帧；**Binance 2026-04-23路由迁移** | 2026-06-15 |
| Binance WS 新路由（`/market/ws/`） | ✅可用 | `wss://fstream.binance.com/market/ws/!forceOrder@arr` → 已收92帧 | 2026-06-15 |
| 强平采集器 | ✅运行中 | `/opt/ai_quant_liq_collector/`；修复后持续收数 | 2026-06-15 |
| 服务器下载大文件（>10MB） | ⚠️受限 | 双跳代理带宽约束；2核跳板拉不动53MB二进制；Founder选择忍受 | 2026-06-14 |

---

## 3. 本地 Mac 执行环境

| 能力项 | 状态 | 详情 | 最后验证 |
|---|---|---|---|
| Desktop Commander (DC) | ✅主通道 | Mac 执行首选；Cowork沙箱失败时回退 DC | 2026-06-11 |
| Python 3.13 量化环境 | ✅可用 | VectorBT / pytest 已装 | 2026-06-11 |
| git + GitHub 私库 | ✅可用 | `laoxiamu/AI_QUANT_COMPANY`（deploy key，验收后推送制） | 2026-06-11 |
| claude-code-vm / workspace bash | ⚠️不稳定 | VM 2.1.170 下载循环失败；mcp__workspace__bash 启动时有"Workspace still starting"；重试可用 | 2026-06-11 |

---

## 4. 数据源能力边界（Binance）

| 数据项 | 正确来源 | 关键限制 | 验证日期 |
|---|---|---|---|
| Contract K线 | `/fapi/v1/klines` 或 data.binance.vision | USD-M volume = base quantity；≠ quote asset volume；≠ mark price | 2026-06-15 |
| Mark Price K线 | `/fapi/v1/markPriceKlines` | 响应中 volume 字段为 ignore；只能当 mark price 序列 | 2026-06-15 |
| Funding 历史 | `/fapi/v1/fundingRate` | limit max 1000；需分页 | 2026-06-15 |
| OI 历史（长期） | data.binance.vision metrics 或第三方 | REST `/futures/data/openInterestHist` **只提供近1个月** | 2026-06-15 |
| 强平实时流 | `<symbol>@forceOrder` / `!forceOrder@arr` | **每symbol每1000ms只推最大/最新1笔 snapshot**；不是完整逐笔历史 | 2026-06-15 |
| 强平历史（完整） | CoinGlass / CoinAPI / Amberdata | Binance 官方无完整历史；自建采集器只能从部署时间起积累 | 2026-06-15 |
| 用户强平订单 | `/fapi/v1/forceOrders` | USER_DATA；默认7天；最多90天；不是全市场历史 | 2026-06-15 |

---

## 5. OSS 工具能力

| 工具 | 适用场景 | 不适用场景 | 详情来源 |
|---|---|---|---|
| CCXT | 统一交易所REST/WS；行情/K线/订单/账户/funding/OI | 完整强平历史；Binance特有字段（需额外params） | `STAGE_AUDITS/OSS_BUILD_VS_BUY_2026-06-15.md` |
| Freqtrade | Phase 1 回测/纸面/实盘最小闭环；dry-run/live/DB/UI | Phase 2+ 生产级高吞吐；RL训练 | 同上 |
| NautilusTrader | Phase 2+ 生产级事件驱动 | Phase 1 最快上手（学习成本高） | 同上 |
| vectorbt | 研究批量参数扫描 | 实盘执行/对账/风控闭环 | 同上 |

---

*最后全表更新：2026-06-20*
