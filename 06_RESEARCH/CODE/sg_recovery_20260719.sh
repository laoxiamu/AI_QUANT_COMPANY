#!/bin/bash
# 2026-07-19 SG欠费停机恢复核查+积压修复（DC恢复后第一动作，一条命令跑完）
# 用法（DC）：nohup bash 06_RESEARCH/CODE/sg_recovery_20260719.sh < /dev/null > 04_AI_TEAM/CODEX_TASKS/sg_recovery_20260719.log 2>&1 &
set -x
KEY=~/.ssh/id_ed25519_aiquant
SGHOST=root@43.160.200.224
SSHCMD="ssh -i $KEY -o StrictHostKeyChecking=no"
R=/Users/yaomingyu/Documents/AI_QUANT_COMPANY
cd "$R" || exit 1

echo "=== S1 采集器健康+缺口量化（关键：停机窗口内哪些天的文件缺失/偏小）==="
$SSHCMD $SGHOST "systemctl is-active aiquant-liq-collector.service; ls -la /opt/ai_quant_liq_collector/data/LIQUIDATIONS/ | tail -8; for f in /opt/ai_quant_liq_collector/data/LIQUIDATIONS/liq_2026071[5-9].jsonl; do echo -n \"\$f: \"; wc -l < \"\$f\" 2>/dev/null || echo MISSING; done"

echo "=== S2 哨兵状态+推送修复版扫描器 ==="
scp -i $KEY -o StrictHostKeyChecking=no 06_RESEARCH/CODE/thesis_hf_scan.py $SGHOST:/root/thesis_sentinel/
$SSHCMD $SGHOST "crontab -l | grep thesis_sentinel; ls -t /root/thesis_sentinel/out/ | head -3; tail -2 /root/thesis_sentinel/last.log 2>/dev/null"

echo "=== S3 强平数据回流本地 ==="
sshpass -p "$(cat ~/.aiquant_sealed/sg_pass)" rsync -av -e "ssh -o StrictHostKeyChecking=no" $SGHOST:/opt/ai_quant_liq_collector/data/LIQUIDATIONS/ 06_RESEARCH/DATA/LIQUIDATIONS/ 2>/dev/null || rsync -av -e "$SSHCMD" $SGHOST:/opt/ai_quant_liq_collector/data/LIQUIDATIONS/ 06_RESEARCH/DATA/LIQUIDATIONS/
ls 06_RESEARCH/DATA/LIQUIDATIONS/ | tail -3

echo "=== S4 git积压提交 ==="
rm -f .git/index.lock .git/HEAD.lock
git add -A && git -c user.name="Claude (operating principal)" -c user.email="yaojinyu1129@gmail.com" commit -q -m "SG停机恢复: 016b验收PASS落库+缺口量化+哨兵新版扫描器+liq回流(7/19)" && git log --oneline -1

echo "=== S5 KAITO/ZRO T-1快照（若在7/20前跑到）==="
$SSHCMD $SGHOST "for s in KAITOUSDT ZROUSDT; do echo \"== \$s\"; curl -s \"https://fapi.binance.com/fapi/v1/premiumIndex?symbol=\$s\" | head -c 300; echo; curl -s \"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=\$s\" | head -c 300; echo; done"
echo SG_RECOVERY_DONE
