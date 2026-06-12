#!/bin/bash
P=/Users/yaomingyu/Documents/AI_QUANT_COMPANY
export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897
sleep 8100   # 等额度恢复（~2.25h）
for i in 1 2 3 4; do
  codex exec --skip-git-repo-check -C $P --sandbox workspace-write -c model_reasoning_effort=high \
    "执行任务书 04_AI_TEAM/CODEX_TASKS/TASK_TSMOM_DUAL_ENGINE.md。先读任务书、AGENTS.md 与预登记 06_RESEARCH/HYPOTHESES/tsmom_expansion_dual_engine_v1.md。参数零调参，两引擎独立二值判定。" \
    >> $P/99_TEMP/codex_tsmom_dual.log 2>&1 < /dev/null
  [ -f "$P/06_RESEARCH/RESULTS/20260612_tsmom_dual_engine.md" ] && echo "DISPATCH_OK attempt=$i" >> $P/99_TEMP/codex_tsmom_dual.log && exit 0
  echo "attempt $i no result, retry in 30min" >> $P/99_TEMP/codex_tsmom_dual.log
  sleep 1800
done
echo "DISPATCH_FAILED_ALL" >> $P/99_TEMP/codex_tsmom_dual.log
