---
name: research-harvest
description: 定期扫描CODEX_TASKS目录中所有未处理报告，批量提取结论写入知识库。当用户说"扫描报告"、"harvest报告"、"处理积压"、"知识库更新"时触发。用于处理积压的多份报告，单份报告处理用result-intake skill。
---

# Research Harvest：积压报告批量处理

## 场景

用于处理积压的多份Codex报告（如当前项目的60+份历史积压）。单份报告验收用`result-intake` skill。

## 执行步骤

### Step 1：扫描未处理报告

```bash
ls 04_AI_TEAM/CODEX_TASKS/REPORT_*.md | sort
```

读取每份报告的**第一节（摘要/目的/背景）**，用于快速分类，不全量读取。

### Step 2：按类别分组

| 类别 | 关键词 | 写入目标 |
|---|---|---|
| Carry策略 | carry/funding/perp/delta | CARRY_KNOWLEDGE.md §四教训 |
| 系统/工程 | E系/Fix/部署/采集器 | SYSTEM_LESSONS.md（若无则创建） |
| 工具/OSS | tool/freqtrade/ccxt/vectorbt | TOOLS_KNOWLEDGE.md |
| TSMOM/Alpha | TSMOM/A-x/signal/factor | TSMOM_KNOWLEDGE.md（若无则创建） |
| 治理/审计 | audit/review/governance | RESEARCH_ACTION_REGISTRY.md |

### Step 3：逐类处理

对每类中**未在知识库中有对应条目**的报告：

1. 读取报告全文
2. 提取：核心发现、行动建议、失败原因（如有）
3. 写入对应知识库文件，格式见下

**教训写入格式（CARRY_KNOWLEDGE.md §四）：**
```markdown
### 教训C-XXX：[简短标题]
**来源：** REPORT_{ID}.md  
**核心发现：** [1-2句话]  
**对当前研究的影响：** [具体影响，不写"无"就不写]
```

**行动项写入格式（RESEARCH_ACTION_REGISTRY.md）：**
```
| RA-XXX | REPORT_{ID} | 核心结论 | 具体行动 | ❌未执行 | P2 |
```

### Step 4：生成积压处理摘要

输出格式：
```
**Harvest摘要**
扫描报告：N份
已处理（本轮）：X份
知识库新增：Y条教训，Z条行动项
主理人判断：[从这批报告里看到了什么模式/规律/Founder不会自己看到的]
仍需处理：[列出跳过的报告及原因，如"内容与已有条目重复"]
```

## 优先顺序

当积压量大时，按以下顺序处理：
1. **与当前执行主线相关**（当前=carry）的报告优先
2. 有"失败/FAILED/NOT APPROVED"标记的报告——失败教训最有价值
3. 最近6个月内的报告
4. 其余按日期倒序

## 禁止

- 禁止把"没有明确行动建议"的报告直接忽略——即使只是"不推荐做X"也是有价值的负面结论
- 禁止写通用的、非项目specific的教训（如"测试很重要"）
- 禁止在没有主理人判断的情况下完成harvest（步骤4的判断是必须的）
