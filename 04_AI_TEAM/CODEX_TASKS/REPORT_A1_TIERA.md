**[专业异议] A1_TIERA 当前为 BLOCKED，不得运行事件后收益计算。**

# REPORT_A1_TIERA

生成时间（UTC）：2026-06-14T04:01:11Z

## 阻塞原因

v5 §12 要求 sealed 密钥由 Codex 执行身份不可读的独立 principal 持有，
且 RR5 明确要求封存和正式执行身份负向权限测试完成前不得计算事件后收益。

当前 Codex 沙箱只能写项目目录和 `/tmp`：

- `~/.aiquant_sealed/a1/a1_key.bin` 不存在；
- 当前身份对 `$HOME` 的写权限测试为非零退出；
- 若改由当前进程生成或暂存密钥，会破坏“执行身份不可读”的冻结权限边界；
- 不允许通过 UI、环境变量、命令行参数或项目文件绕过该边界。
- `git add` 也因无法创建 `.git/index.lock` 被拒绝，当前身份不能完成提交。

因此真实 custodian 阶段未运行，executor 也未运行。当前没有 Tier A
PASS/FAILED 科学判决，不能以数据缺失或权限阻塞改写为 FAILED。

## 已完成

- 审计 v5、Protocol 增补件、RR5、既有 A-1/A-2 特征代码和原始数据 schema。
- 确认既有 A-1 特征使用 `sum_open_interest`，不符合 v5 的名义 OI
  `sum_open_interest_value`，最终实现已按 v5 独立重建。
- 新增 `06_RESEARCH/CODE/a1_tiera_core.py`：
  - 严格事件前 365 天 midrank；
  - 180 个有效日和 720 个有效样本谓词；
  - 纯方向触发、24h refractory、deterministic 每五条封存；
  - circular moving-block bootstrap、Spearman 配对 bootstrap、Holm m=4；
  - WF midpoint purge、功效诊断、AES-256-GCM 小函数。
- 新增 `06_RESEARCH/CODE/a1_tiera_custodian.py`：
  - 只读取 cutoff 前 OI/MARK/funding；
  - 生成 pooled episodes、切分、加密和 manifest；
  - sealed 明文不落盘，脚本结束前释放引用；
  - 不包含任何事件后收益计算。
- 新增 `06_RESEARCH/CODE/a1_tiera_permtest.py`：
  - 实际执行 manifest 读取命令；
  - 子进程尝试打开密钥，只有密钥不可访问才记录 PASS；
  - 密钥可读时拒绝解密并判权限边界失败。
- 新增 `06_RESEARCH/CODE/a1_tiera_executor.py`：
  - 负向权限测试和 work SHA 未通过时拒绝运行；
  - 事件数据只加载 `work_episodes.csv`；
  - 市场 CSV 流式读取并在 cutoff 前停止；
  - 实现 CAR、family、WF、成本、功效、报告和完成事件。
- 新增 `06_RESEARCH/CODE/tests/test_a1_tiera.py`。
- 定向验证：`17 passed in 1.69s`。
- 已确认未创建 `06_RESEARCH/DATA/A1_WORK/work_episodes.csv`、
  `sealed_holdout.enc` 或 Tier A 判决报告，未计算真实事件后收益。

## 剩余步骤

1. 由可写 `.git` 的主会话只提交本报告列出的 A1_TIERA 文件，排除现有
   `A1_TIERA_EXEC.md`、运行日志和无关文件。
2. 由独立 custodian principal 在代码提交后运行：
   `python3 06_RESEARCH/CODE/a1_tiera_custodian.py`。
3. 配置密钥目录 ACL/身份边界，确保正式 executor 无法打开密钥。
4. 由正式 executor 身份运行：
   `python3 06_RESEARCH/CODE/a1_tiera_permtest.py`，且日志 `overall=PASS`。
5. 恢复 Codex 执行：
   `python3 06_RESEARCH/CODE/a1_tiera_executor.py`。
6. 复核判决报告、结果 JSON、TASK_INBOX 事件和 git diff 后提交结果。

## 恢复前提

- A1_TIERA 代码和本阻塞报告已提交，工作树中无同文件未提交漂移；
- `work_episodes.csv`、`sealed_holdout.enc` 和 manifest 已由独立 custodian
  一次性生成；
- `~/.aiquant_sealed/a1/a1_key.bin` 对 executor 实际不可打开；
- `A1_HOLDOUT_PERMTEST.log` 明确记录 manifest 退出码 0、解密探针非零退出、
  原因证据和 `overall=PASS`。
