#!/bin/bash
# 2026-07-16 L1审计R7：面板刷新改走通道B（SG服务器）——Mac直连Binance已退化为HTTP 451 geo封锁
# 用法：nohup bash panel_refresh_via_sg.sh > panel_sg.log 2>&1 &（DC fire-and-forget，VM轮询log）
set -x
KEY=~/.ssh/id_ed25519_aiquant
SGHOST=root@43.160.200.224
SSHCMD="ssh -i $KEY -o StrictHostKeyChecking=no"
R=/Users/yaomingyu/Documents/AI_QUANT_COMPANY
W=/root/panel_work
cd "$R" || exit 1

echo "=== S1 远端目录骨架（伪造ROOT标记，脚本靠CLAUDE.md+01_MEMORY_CORE定位根）==="
$SSHCMD $SGHOST "mkdir -p $W/06_RESEARCH/CODE $W/06_RESEARCH/DATA $W/01_MEMORY_CORE $W/04_AI_TEAM/CODEX_TASKS && touch $W/CLAUDE.md"

echo "=== S2 推送旧面板+现面板+脚本（~45MB）==="
rsync -az -e "$SSHCMD" 06_RESEARCH/DATA/FUTURES_EXPANDED 06_RESEARCH/DATA/FUTURES_EXPANDED_2026 $SGHOST:$W/06_RESEARCH/DATA/
rsync -az -e "$SSHCMD" 06_RESEARCH/CODE/panel_refresh_2026.py $SGHOST:$W/06_RESEARCH/CODE/

echo "=== S3 远端依赖+执行（SG直连Binance无geo问题）==="
$SSHCMD $SGHOST "python3 -m pip install -q pandas 2>&1 | tail -1; cd $W && python3 06_RESEARCH/CODE/panel_refresh_2026.py --timeout 30 > $W/run.log 2>&1; tail -5 $W/run.log"

echo "=== S4 拉回刷新后的面板+审计+报告 ==="
rsync -az -e "$SSHCMD" $SGHOST:$W/06_RESEARCH/DATA/FUTURES_EXPANDED_2026/ 06_RESEARCH/DATA/FUTURES_EXPANDED_2026/
rsync -az -e "$SSHCMD" $SGHOST:$W/06_RESEARCH/CODE/output/ 06_RESEARCH/CODE/output/
rsync -az -e "$SSHCMD" "$SGHOST:$W/04_AI_TEAM/CODEX_TASKS/REPORT_PANEL_REFRESH_*" 04_AI_TEAM/CODEX_TASKS/

echo "=== S5 本地验证 ==="
for f in BTCUSDT ETHUSDT AAVEUSDT; do echo -n "$f last bar: "; tail -1 06_RESEARCH/DATA/FUTURES_EXPANDED_2026/${f}_4H.csv | cut -d, -f1; done
echo PANEL_SG_DONE
