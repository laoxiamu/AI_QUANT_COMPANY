#!/bin/bash
# 面板刷新（通道B：SG 远端跑，Mac 直连 Binance 现为 HTTP 451 geo 封锁）
# 2026-07-21 v2 重写：保留全部效果，摘除 S0-01 风险元素（set -x / StrictHostKeyChecking=no / 无校验回写）
set -uo pipefail

KEY="$HOME/.ssh/id_ed25519_aiquant"
SGIP="43.160.200.224"
SGHOST="root@${SGIP}"
KNOWN="$HOME/.ssh/known_hosts_aiquant"
R="/Users/yaomingyu/Documents/AI_QUANT_COMPANY"
W="/root/panel_work"
cd "$R" || exit 1

step(){ echo; echo "=== $* ==="; }

if ! grep -q "$SGIP" "$KNOWN" 2>/dev/null; then
  step "S0 固定 SG host key"
  ssh-keyscan -H "$SGIP" >> "$KNOWN" 2>/dev/null
fi
SSHCMD="ssh -i $KEY -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$KNOWN"
SCPOPT="-i $KEY -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$KNOWN"

step "S1 远端目录骨架"
$SSHCMD "$SGHOST" "mkdir -p $W/06_RESEARCH/CODE $W/06_RESEARCH/DATA $W/01_MEMORY_CORE $W/04_AI_TEAM/CODEX_TASKS && touch $W/CLAUDE.md"

step "S2 推送面板+脚本"
rsync -az -e "$SSHCMD" 06_RESEARCH/DATA/FUTURES_EXPANDED 06_RESEARCH/DATA/FUTURES_EXPANDED_2026 "$SGHOST:$W/06_RESEARCH/DATA/"
rsync -az -e "$SSHCMD" 06_RESEARCH/CODE/panel_refresh_2026.py "$SGHOST:$W/06_RESEARCH/CODE/"

step "S3 远端执行（SG 无 geo 限制）"
$SSHCMD "$SGHOST" "python3 -m pip install -q pandas 2>&1 | tail -1; cd $W && python3 06_RESEARCH/CODE/panel_refresh_2026.py --timeout 30 > $W/run.log 2>&1; tail -5 $W/run.log"

step "S4 回流前：远端 manifest（用于校验，防无声污染）"
$SSHCMD "$SGHOST" "cd $W/06_RESEARCH/DATA/FUTURES_EXPANDED_2026 && for f in *_4H.csv; do echo \"\$f \$(wc -l < \$f) \$(tail -1 \$f | cut -d, -f1)\"; done" > /tmp/panel_remote_manifest.txt
echo "远端 symbol 数：$(wc -l < /tmp/panel_remote_manifest.txt)"

step "S5 拉回"
rsync -az -e "$SSHCMD" "$SGHOST:$W/06_RESEARCH/DATA/FUTURES_EXPANDED_2026/" 06_RESEARCH/DATA/FUTURES_EXPANDED_2026/
rsync -az -e "$SSHCMD" "$SGHOST:$W/06_RESEARCH/CODE/output/" 06_RESEARCH/CODE/output/
rsync -az -e "$SSHCMD" "$SGHOST:$W/04_AI_TEAM/CODEX_TASKS/REPORT_PANEL_REFRESH_*" 04_AI_TEAM/CODEX_TASKS/ 2>/dev/null

step "S6 回流校验（远端 vs 本地：行数+末条时间须逐项一致）"
FAIL=0
while read -r f rows last; do
  L="06_RESEARCH/DATA/FUTURES_EXPANDED_2026/$f"
  if [ ! -f "$L" ]; then echo "⚠️缺失 $f"; FAIL=1; continue; fi
  lr=$(wc -l < "$L"); ll=$(tail -1 "$L" | cut -d, -f1)
  if [ "$lr" != "$rows" ] || [ "$ll" != "$last" ]; then echo "⚠️不一致 $f: 远端($rows,$last) vs 本地($lr,$ll)"; FAIL=1; fi
done < /tmp/panel_remote_manifest.txt
[ "$FAIL" = 0 ] && echo "✅全部一致（$(wc -l < /tmp/panel_remote_manifest.txt) symbol）" || echo "🔴校验失败：本次回流不可信，勿用于研究，人工排查后重跑"

step "S7 本地抽样确认"
for f in BTCUSDT ETHUSDT AAVEUSDT; do echo -n "$f last bar: "; tail -1 "06_RESEARCH/DATA/FUTURES_EXPANDED_2026/${f}_4H.csv" | cut -d, -f1; done
echo; echo "PANEL_SG_DONE（git 提交由 Claude 单独执行，本脚本不 commit）"
