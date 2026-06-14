# REPORT_CARRY_SCAFFOLD

**Task:** `CARRY_SCAFFOLD`  
**Status:** completed  
**Execution scope:** code and synthetic tests only

## 异议处理

先前关于 3x 缓冲线与交易所最低维持保证金的语义异议，已由本次任务书明确
解决：

- 缓冲线以下、交易所最低线以上：`buffer_breach`，记录并同步减两腿恢复缓冲。
- 交易所最低线以下：`liquidation`，永续短腿归零并留下 spot delta 暴露。

当前无未决专业异议。

## 交付

- `06_RESEARCH/CODE/carry/`: 数据、成本、配置、触发器、引擎、组合、指标和
  门控 CLI。
- `06_RESEARCH/CODE/carry/tests/`: 仅使用临时目录和内存合成数据的测试。
- `06_RESEARCH/RESULTS/20260615_carry_scaffold_selftest.md`: 参数默认、
  测试结果、未来运行命令及范围声明。

## 验收逐条自检

- 数据加载器：实现 strict cutoff、UTC、坏行/无效行/重复行审计；未调用真实
  funding/mark 数据。
- Delta 中性引擎：实现 long spot + short perp、funding 方向、仅 00:00 UTC
  且漂移严格大于 5% 的再平衡。
- 风险：配置拒绝杠杆大于 2x；分别记录 `buffer_breach` 与 `liquidation`。
- 成本：现货与永续逐腿计 0.10% fee、0.10% slippage，事件档 0.30%，
  再平衡换手及 basis 进出场均有显式接口。
- A-1×Carry：`OI percentile <= 0.01` 后 50% 仓位、24h refractory；
  组合层输出 with/without trigger 两套净值。
- 指标：实现净 E[R]、profit factor、正年比例、几何增长、MDD、三段时间 WF、
  cluster/bootstrap 单侧 p。
- 测试：`25 passed`，覆盖任务书列出的全部合成场景及保守边界。

## 禁项自检

- 未读取 Holdout。
- 未读取 `01_MEMORY_CORE/`。
- 未修改预登记文件。
- 未运行真实 `*_FUNDING_8H.csv` / `*_MARK_1H.csv` 验收。
- 未生成真实数据验收数值、验收判决或 edge 结论。
- 未引入 MLFinPy 等不可审计依赖。

## 验证命令

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
  06_RESEARCH/CODE/carry/tests -q
```

结果：`25 passed`。

## Git 状态

已按任务号准备提交，但当前沙箱禁止写入 `.git/index.lock`，`git add` 返回
`Operation not permitted`，因此本会话无法创建 commit。交付文件保持在工作树，
未暂存或回退任何并行任务改动。
