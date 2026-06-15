# DRAFT-MASTERPLAN：起草《公司建设总图》v1（轻量，按 CTO 调整后的结构）

**定位：** 项目级顶层框架，填补"无项目级任务计划书"的缺口。**严格轻量**——只到"防错层"，不塞具体任务（实时任务仍由 `CURRENT_STATE §4` 台账管，不搞双账本）。
**依据：** `BPR_TOP_LEVEL_FRAMEWORK_REFERENCE_2026-06-15.md`（方法参考）+ 本任务的 **CTO 调整意见（优先级高于 BPR 原文）**。
**输出：** `00_PROJECT_MANAGEMENT/COMPANY_BUILD_MASTERPLAN_v1.md`（DRAFT，待 Founder D 级确认终态/阶段边界）。

## CTO 调整意见（必须体现，覆盖 BPR 原文处以此为准）
1. **价值流 = 计划连贯性工具，非组织去烟囱**。我们是 1 Founder + Claude + Codex、**无部门**。"流程所有者/Owner"是**责任帽子**，不新增组织层级。
2. **价值流当前不等权**：无在跑实盘→"信号到结算/异常到恢复/绩效到配置"为**未来阶段**，总图画全但标注"未激活"；**近期唯一活跃 = 机会到证据 + 证据到部署 + 建最小交易平台**。
3. **硬反膨胀盒**：总图只写——①公司终态 ②能力地图(9能力域) ③L1价值流(7条+起点/终点/结果/参与能力域/单一Accountable) ④能力域×价值流缺口矩阵(标"无人负责/重复建/关键依赖") ⑤分阶段(Phase 0/1/2/3)出口条件 ⑥各能力域成熟度(空白/草图/部分/成熟) ⑦实时状态去哪读(指向§4,不在总图重复)。**禁止**：ARIS/重型EA、部门岗位KPI、大爆炸再造、把规则立即系统固化、以文档完成率衡量进展。
4. **成熟度加权**：治理/知识域最成熟(少着墨)；交易平台/实时风控/监控/账务=空白或草图(总图重点标为关键缺口与依赖)；Alpha研究流程成熟但当前无活体edge(carry在可行性复核)。
5. **终态/阶段边界**：给出**你(Codex)的推荐版**，但顶部明确标注"待Founder D级确认"，不当既定。

## 同时（第二件）：重定位 OPERATING_MODEL_DESIGN_v2
- 改名/重定位为 `STRATEGY_DELIVERY_LIFECYCLE_SOP_v1`（或在原文件头部加重定位声明 + 状态 DEPRECATED-AS-COMPANY-MODEL / ACTIVE-AS-SOP）：其 R-S-E 是"机会到证据 + 证据到部署"两条价值流的**局部 SOP**；循环 E 仅覆盖"策略接入既有平台"，删除"从零建整个交易系统"的含义（系统建设归总图的平台能力域，独立于单策略）。**保留原内容，不删，只重定位 + 加 CHANGELOG。**

## 铁律：不改 DECISION_LOG/预登记/研究文件；不读 HOLDOUT；总图为 DRAFT 待 Founder D 级。完成写 `04_AI_TEAM/TASK_INBOX/DRAFT_MASTERPLAN_DONE.json`(task_id=DRAFT_MASTERPLAN,outputs,notes=终态/阶段的推荐摘要+待确认点)。可 commit。
