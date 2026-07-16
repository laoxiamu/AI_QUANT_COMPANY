# REPORT_P1PIPE_S3_UNLOCK

**任务**：P1-RES-039-PIPELINE-S3｜解锁日历拉取 + overlap 普查  
**执行时间**：2026-06-27 UTC  
**复现脚本**：`06_RESEARCH/CODE/p1pipe_s3_unlock_source_audit.py`  
**机器结果**：`06_RESEARCH/CODE/output/p1pipe_s3_unlock_source_audit.json`  
**事件输出**：`06_RESEARCH/CODE/output/p1pipe_s3_free_unlock_events.csv`  
**纪律声明**：未碰 Holdout；未回测；未调参；未用付费 API；未把文章/周报样本冒充全量事件普查。

## 结论

**Step 3 闸门不通过，任务链停在 Step 3；不得进入 Step 4 B1-KILLCARD。**

免费边界下没有拿到可复现的 post-2025 全量/准全量结构化 unlock event 表。最终可用于普查的事件数为 0：

| 项 | 结果 |
|---|---:|
| 免费结构化事件数 | 0 |
| 与价格面板 overlap episode | 0 |
| 与价格 + OI + funding overlap episode | 0 |
| episode ≥ 50，可进 Step 4 | 否 |
| episode ≥ 100 | 否 |
| episode ≥ 300，可 60/20/20 | 否 |

这不是机制结论，只是数据门结论：在“不付费、不用文章样本冒充全量、不碰 Holdout、不进 B2”的约束下，本轮没有足够事件数据支撑 B1 描述统计。

## 源审计

| 源 | 结果 | 可用性判断 |
|---|---|---|
| `https://api.llama.fi/protocols` | HTTP 200 | 只证明 api.llama.fi 可达，不是 unlock events |
| `https://api.llama.fi/emissions` | HTTP 402 | 付费墙，不能用 |
| `https://api.llama.fi/unlocks` | HTTP 404 | 非公开 endpoint |
| `https://defillama.com/unlocks` | transport/SSL 失败 | 本地直连不可稳定读取；即使页面可见，也非可审计事件表 |
| Tokenomist overview page | HTTP 200，但页面含 404/guest UI/API trial banner/文章卡片 | 有 unlock 关键词，但没有可直接采用的全量事件 JSON |
| Tokenomist AAVE unlock page | HTTP 200，但为单币 guest UI，含文章卡片/API trial banner | 不可扩成 31 symbol 全量普查 |
| Tokenomist API docs path | HTTP 404 | 当前路径不可用；此前 Phase A 已记录 API 需 key/计划边界 |

Tokenomist 页面上能看到“Build and Backtest Tokenomist API / Get Free Trial API”这类入口，并可见研究文章卡片；这不能等同于可复现事件级表。按任务要求，文章样本、周报卡片、press mention 一律不作为全量事件输入。

## Overlap 普查

`p1pipe_s3_free_unlock_events.csv` 为空（只有空文件），原因是没有发现可用的免费结构化事件表。对应 overlap 结果：

| 口径 | episode |
|---|---:|
| 价格 overlap | 0 |
| 价格 + OI + funding overlap | 0 |

规模档分布为空，不能计算 `规模/流通占比` 分档，也不能判断单调性。

## 验收自检

| 验收项 | 结果 |
|---|---|
| 免费拉 post-2025 解锁事件 | 未通过：免费结构化全量源不可用 |
| 限 universe symbol | 已准备 universe，但无事件可筛 |
| 字段尽量含 symbol/unlockDate/规模/流通占比/allocation | 无可用事件表，未伪造字段 |
| 与刷新后价格面板做 overlap | 完成，episode=0 |
| 报 ≥100 / ≥300 / 规模档 | 完成，均不达标；规模档为空 |
| 不拿文章样本冒充全量 | 达标 |
| Step 4 episode ≥50 闸门 | 不通过 |

## 停步说明

按任务硬护栏，Step 3 overlap episode < 50，**停止，不进入 Step 4**。下一步需要 Claude 回来裁决：是否购买/申请可审计 unlock event 数据，或改任务方向为“只研究 Tokenomist 免费/试用可导出的近端样本”，但后者仍需先明确数据许可证与历史覆盖。
