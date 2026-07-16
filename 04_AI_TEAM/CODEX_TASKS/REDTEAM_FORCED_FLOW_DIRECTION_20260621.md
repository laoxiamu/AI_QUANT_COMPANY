# Codex 任务：强制流/订单流研究方向独立红队（DEC-085 + B0 卡）

**类型：** 方向级机制红队（不写代码、不回测、不碰 Holdout）。纯专业异议审查。
**触发：** Founder 提示"方向定前未与 Codex 讨论"。Claude 已起草方向与 B0 卡，需 Codex 独立挑刺后再进 B1。
**你的角色：** 独立 Risk Reviewer / 机制红队。**任务是找出这个方向为什么会失败，不是确认它。** 越尖锐越好；可直接判 KILL。

## 必读（按序）
1. `01_MEMORY_CORE/DECISION_LOG.md` → DEC-085（本方向定向）、DEC-084（禁资金费）、DEC-082（拆B0-B4）、DEC-064（猎机制不猎形态）、DEC-069（验收纪律）。
2. `06_RESEARCH/PREREGISTRATIONS/FORCED_FLOW_ORDERFLOW_B0_MECHANISM_CARD.md`（被审对象）。
3. `06_RESEARCH/GRAVEYARD_INDEX.md` → 尤其 A-1 强制去杠杆回弹 FAILED 那条、Sweep 家族。
4. `06_RESEARCH/MECHANISM_SURVEY/CRYPTO_PERP_MECHANISM_SCAN_20260621.md` → #5 清算流、#9 订单流的数据/失败模式标注。
5. `06_RESEARCH/RESEARCH_PROTOCOL_v1.3_ADDENDUM.md` + `..._v1.4_A1SCREEN_ADDENDUM.md`（验收四件套+第五件+MDE+事件成本档）。

## 必答红队问题（逐条给结论，不要泛泛）
1. **A-1 换皮风险**：B0 卡 §2 声称新线≠A-1（方向不预设/数据更直接/时间尺度不同）。这三点区分**真的成立**吗？还是换个说法重测"清算后均值回归"？A-1 的失败（48h CAR 不显著、强平免费数据抽样截断）有多少会直接遗传给新线？
2. **OFI 的 MDE 死刑**：订单流失衡半衰极短、成本敏感。在分钟级、扣 0.1%/边 + 滑点后，OFI 的"合理效应上限"是否还大于 MDE（功效门，v1.4 第六）？如果大概率 MDE>效应上限，这条就该在 B0 直接 KILL 而不是 PROCEED。给你的判断 + 依据。
3. **数据门**：①清算流——币安免费 forceOrder 是抽样广播/截断，前向真实数据 still thin（A-1 旧伤）。②订单流——aggTrades 的 taker 方向标注质量、深度增量重建是否可靠到能算干净 OFI？哪个数据门是 showstopper？
4. **"形态当触发器"会不会偷偷变回看图搜索**：B0 说技术形态只作触发器、入场优化后置 B3。但实操中"触发器+方向判定"会不会又滑回 Sweep 式形态调参（风险D）？给一条能在 B1/B2 机械识别的防滑回判据。
5. **PROCEED 该不该降级为 REVISE/KILL**：综合以上，B0 卡判"PROCEED 到 B1"是否过宽？你认为正确结论是 PROCEED / REVISE（怎么改）/ KILL（理由）？
6. **有没有更高信息增益的子机制**：若 OFI 和清算流都悬，强制/激进流家族里有没有数据更干净、payer 更硬的第三个子机制值得 B1 先做？

## 交付
- 写报告 `04_AI_TEAM/CODEX_TASKS/REPORT_REDTEAM_FORCED_FLOW_20260621.md`：逐条结论 + 总裁决（ACCEPT方向 / ACCEPT-with-MODIFY / REJECT）+ 若 REJECT 给替代建议。
- 完成后按 TASK_INBOX 协议写 DONE.json（见 `04_AI_TEAM/TASK_INBOX/README.md`）。
- **边界**：不改 Claude 独占权威文件（DECISION_LOG/CURRENT_STATE/机会地图/B0卡），只产报告；不跑回测、不碰 Holdout、不耗失败计数。
