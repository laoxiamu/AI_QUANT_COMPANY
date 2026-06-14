# A1-RR4：A-1 预登记 v4（路径A 关联快筛）第四轮独立盲审

**角色：** 独立 Risk Reviewer（与 thesis owner 分离），不知实验结果，只审设计。
**审查对象：** `06_RESEARCH/PREREGISTRATIONS/A1_CASCADE_REBOUND_PREREG_v4.md`
**对照：** `A1_RISK_REVIEW_v3.md` 第三轮"五项最小必改"清单。
**新语境（DEC-075 / 增补件）：** v4 已被 Founder 确认重定位为**路径A=机制前【关联】快筛，不声称机制、不耗独立计数**；功效门据 `06_RESEARCH/RESEARCH_PROTOCOL_v1.4_A1SCREEN_ADDENDUM.md` 降为报告型诊断。机制确证另走路径B(`A1_FORWARD_LIQUIDATION_PATH.md`)。
**输出：** `06_RESEARCH/PREREGISTRATIONS/A1_RISK_REVIEW_v4.md`

## 任务：逐条裁决 RR3 五项最小必改是否闭合（CLOSED/PARTIAL/NOT_CLOSED+证据§/行+仍缺）

1. **去 overclaim**：v4 是否全文把 Tier A 改"可观测条件回弹关联(探索级)"、删"机制成立"、命题仅关联层？§9/§11 是否还有残留因果或"机制"措辞？关联层定位是否自洽。
2. **依赖稳健推断一次性闭合**：v4 §4 W=144h circular moving-block 是否覆盖完整数据足迹(72h baseline+对齐lag+48h)？非等距块算法(连续UTC网格均匀起点/空块跳过/circular回绕/超额截断/等权/+1的p值/basic-bootstrap CI)是否完整可复现？§5 Spearman 改 moving-block 标签置换检验 H0:ρ=0 是否正确(解决 RR3 指出的"减均值不改秩")？
3. **功效治理**：v4 把功效降诊断并以增补件留痕——**核查增补件**：(a) 把"机制前关联快筛不耗计数→§六硬门不强制"的豁免边界是否定义清楚、是否被滥用(v4 是否确实满足豁免三条件：仅关联/不耗计数/不直接晋级)？(b) sigma_pre_h、m_bar 是否已定义？这是治理判断，请评估该豁免是否在方法学上站得住，而非简单接受。
4. **family 统一**：v4 是否全文 Holm m=4 一致(§0/§4/§7/§11)，已无 m=3 残留？
5. **WF + 真封存**：WF 三段切分(等episode数三等分+切点120h purge)是否唯一可复现？§12 sealed holdout **AES加密+密钥仅主会话持有+负向权限测试** 是否构成 RR3 要求的"执行身份确实不可读"的真权限边界(不再是仅移出workspace)？

## 第二部分：v4 新结构(W=144h块/标签置换/加密holdout/关联门重定位/增补件豁免)是否引入新缺陷或新自由度。

## 结论：APPROVED(可放行 Tier A 历史关联快筛) / NOT APPROVED(列**最小**第四轮必改)。
**特别要求：** (a) 若 APPROVED，明确放行边界(仅关联、不耗计数、不晋级)。(b) 若 NOT APPROVED，区分"真方法学阻塞" vs "可接受的探索级快筛残留"——因 v4 已自降为关联快筛(非机制确证)，审查标尺应与机制确证实验区别：不应要求关联快筛达到机制实验的全部严格度，但关联结论本身必须无偏、可复现。请按"关联快筛"的合理标尺裁决，避免无限加码。

## 铁律：禁读 HOLDOUT/`01_MEMORY_CORE/`/禁改预登记/禁提前跑事件研究。允许读 v4/v3review/增补件/路径B设计/Protocol/A-2公开假设。完成写 `04_AI_TEAM/TASK_INBOX/A1_RR4_DONE.json`(task_id=A1_RR4,status,output_file,review_conclusion,conditions_closed=x/5,notes)。
