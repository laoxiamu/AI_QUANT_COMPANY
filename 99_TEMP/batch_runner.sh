#!/bin/bash
P=/Users/yaomingyu/Documents/AI_QUANT_COMPANY
export HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897
for T in B1 B2 B3 B4 B5; do
  echo "=== $T start $(date) ===" >> $P/99_TEMP/batch_20260612N.log
  codex exec --skip-git-repo-check -C $P --sandbox workspace-write -c model_reasoning_effort=high -c sandbox_workspace_write.network_access=true \
    "执行批次任务书 04_AI_TEAM/CODEX_TASKS/BATCH_20260612N.md 中的 $T 任务（只做 $T，其他任务忽略）。先读批次书头部铁律、AGENTS.md、该任务引用的预登记/数据。完成即写报告退出。" \
    >> $P/99_TEMP/batch_20260612N.log 2>&1 < /dev/null
  echo "=== $T end $(date) ===" >> $P/99_TEMP/batch_20260612N.log
done
echo "BATCH_DONE $(date)" >> $P/99_TEMP/batch_20260612N.log
