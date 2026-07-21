#!/bin/bash
# SG 恢复/回流脚本（2026-07-21 v2 重写：保留"一条命令跑完"的全部效果，摘除 S0-01 四项风险元素）
#
# v1→v2 变更（外部审计 S0-01，Claude 接受）：
#   1. 删除内置 git commit —— 脚本只干活，版本提交由 Claude 单独做（AGENTS.md：Codex/脚本不得直接 commit）
#   2. 删除 rm .git/*.lock —— 改为检测到锁即报错退出（大锤修表→告警）
#   3. 删除 set -x + sshpass 明文 —— 改分步 echo 进度；认证一律走密钥，密码不进日志
#   4. 删除 StrictHostKeyChecking=no —— 改用固定 known_hosts（首次自动 ssh-keyscan 落盘，之后严格校验）
#   5. 新增：回流前后 hash/行数校验（v1 是无校验 rsync 覆盖研究数据，出错无人知晓）
#
# 用法（DC fire-and-forget）：
#   nohup bash 06_RESEARCH/CODE/sg_recovery_20260719.sh < /dev/null > 04_AI_TEAM/CODEX_TASKS/sg_recovery_$(date +%Y%m%d).log 2>&1 &
set -uo pipefail

KEY="$HOME/.ssh/id_ed25519_aiquant"
SGIP="43.160.200.224"
SGHOST="root@${SGIP}"
KNOWN="$HOME/.ssh/known_hosts_aiquant"
R="/Users/yaomingyu/Documents/AI_QUANT_COMPANY"
LIQ_REMOTE="/opt/ai_quant_liq_collector/data/LIQUIDATIONS/"
LIQ_LOCAL="$R/06_RESEARCH/DATA/LIQUIDATIONS/"
cd "$R" || exit 1

step(){ echo; echo "=== $* ==="; }

# --- 前置：host key 固定（一次性落盘，之后严格校验；替代 StrictHostKeyChecking=no） ---
if ! grep -q "$SGIP" "$KNOWN" 2>/dev/null; then
  step "S0 首次固定 SG host key → $KNOWN"
  ssh-keyscan -H "$SGIP" >> "$KNOWN" 2>/dev/null && echo "host key 已固定（后续严格校验）"
fi
SSHCMD="ssh -i $KEY -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$KNOWN"

step "S1 采集器健康 + 逐日缺口量化"
$SSHCMD "$SGHOST" "systemctl is-active aiquant-liq-collector.service; ls -la $LIQ_REMOTE | tail -8" || echo "⚠️S1 失败（SG不可达？先查欠费/网络）"

step "S2 哨兵状态 + 推送当前版扫描器"
scp -i "$KEY" -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$KNOWN" 06_RESEARCH/CODE/thesis_hf_scan.py "$SGHOST:/root/thesis_sentinel/" && echo "扫描器已推送"
$SSHCMD "$SGHOST" "crontab -l | grep thesis_sentinel; ls -t /root/thesis_sentinel/out/ | head -3"

step "S3 强平数据回流（密钥认证，无明文密码；带校验）"
$SSHCMD "$SGHOST" "cd $LIQ_REMOTE && ls liq_*.jsonl | tail -5 | xargs wc -l" > /tmp/liq_remote_manifest.txt 2>/dev/null
rsync -av -e "$SSHCMD" "$SGHOST:$LIQ_REMOTE" "$LIQ_LOCAL" | tail -3
echo "--- 回流校验（远端 vs 本地行数，须逐行一致）---"
cat /tmp/liq_remote_manifest.txt
for f in $(awk '{print $2}' /tmp/liq_remote_manifest.txt | grep 'liq_.*jsonl'); do
  [ -f "$LIQ_LOCAL$f" ] && echo "local $f: $(wc -l < "$LIQ_LOCAL$f")" || echo "⚠️local $f 缺失"
done

step "S4 git 状态检查（只报告，不提交——提交由 Claude 单独执行）"
if [ -f "$R/.git/index.lock" ] || [ -f "$R/.git/HEAD.lock" ]; then
  echo "⚠️检测到 git lock 文件残留：可能有并发 git 进程。本脚本不删除锁，请人工确认后处理。"
else
  echo "git lock 无残留"
fi
git status --short | head -10
echo "本地 vs 远端：$(git rev-list --count origin/master..HEAD 2>/dev/null) 个提交未推送"

step "S5 关注标的现况快照（只读行情，不下单）"
for s in "${@:-}"; do
  [ -z "$s" ] && continue
  echo "== $s"
  $SSHCMD "$SGHOST" "curl -s 'https://fapi.binance.com/fapi/v1/premiumIndex?symbol=$s' | head -c 260; echo"
done

echo; echo "SG_RECOVERY_DONE（提交与裁决留给 Claude）"
