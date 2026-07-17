# TASK P0-RES-016b：解锁源 lookahead 修复（事件类登记通道复活）

**派发：** 2026-07-17（巡检发现+Claude诊断确认） | **执行：** Codex | **验收：** Claude

## 问题（Claude 已实测诊断，勿重复）

`thesis_hf_scan.py` 的 `scan_token_unlocks()` 代码本身支持 max_days=14 向前窗，**但数据源不支持**：CryptoRank `/token-unlock` 页面 `__NEXT_DATA__.fallbackData.data` 仅 SSR 渲染"今天"的 6 条事件行 + 14 条无 date 字段的概览行（已验证 repr=None，非解析bug）。未来解锁走客户端 XHR。后果：解锁候选永远 T0 当天才浮出→只能按事后偏误拒→事件类登记通道实质关闭（7/17 巡检：DBR $10.5M/12%市值本可 T-1 评估，被迫拒）。

已试过 404 的猜测端点（勿重试）：`api.cryptorank.io/v0/token-unlock/upcoming`、`/v0/token-unlock?limit=50`、`/v0/coin-unlock/upcoming`。页面 chunk `pages/token-unlock-db0565aafda4237c.js`（40KB）未直接暴露路径——API base 可能拼装于共享 chunk。

## 目标

让 `token_unlock` 源稳定浮出 **T-14 ~ T0** 窗口内的解锁事件（字段至少：symbol/key、T0 日期、解锁金额USD、占市值%）。两条路径按序尝试：

1. **首选：找到 CryptoRank 真实 upcoming API**——下载页面引用的全部 JS chunks，grep API base 拼装逻辑（找 `api.cryptorank.io` / `api2` / fetch/axios baseURL），复原 upcoming unlocks 的 XHR 请求（含必要 headers）；在 SG 上 curl 实测返回真实未来事件后再写进代码。
2. **备选：DropsTab `/vesting` HTML 解析**（P0-RES-016 已证 HTTP 200 可达，结构较不稳）——解析 upcoming 列表，标注"结构脆弱"并写入 source_errors 降级路径。

两路都通=用1留2作fallback；都不通=诚实报告"免费结构化 upcoming 解锁不可得"，禁止硬凑。

## 交付与护栏

- 改动限 `scan_token_unlocks()` 及其辅助函数；其余三源与 legacy 输出零改动（回归对照同 P0-RES-016 方法）。
- 补测试进 `tests/test_thesis_hf_scan.py`（含"源结构变化→进 source_errors 不崩全局"用例）。
- SG 实测一次全源扫描，报告里贴 unlock 源浮出的未来事件样例（须含 ≥1 条 T+1~T+14 事件才算修复成立）。
- `REPORT_P0RES016B_UNLOCK_LOOKAHEAD_20260717.md` + `TASK_INBOX/P0RES016B_DONE.json`。
- 不碰 Holdout/不做量化实验/不花钱/不注册 thesis；网络走 SG（Mac 直连 Binance 451，CryptoRank 从 SG 走亦可）。
