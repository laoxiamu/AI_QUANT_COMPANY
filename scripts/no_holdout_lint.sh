#!/bin/bash
# no-holdout lint v2（DEC-069）：只拦"对 Holdout 的真实读取调用"，不拦描述性提及
# 规则：同一行同时出现 HOLDOUT 与 读取函数（read_csv/open(/read_parquet/load/np.loadtxt/cat ）才算违规
# 白名单：封存写入器 a2_funding_features.py；output/ 与 __pycache__ 不扫
cd "$(git rev-parse --show-toplevel)" || exit 0
HITS=$(grep -rnE "HOLDOUT" 06_RESEARCH/CODE 04_AI_TEAM/CODEX_TASKS --include='*.py' --include='*.md' --include='*.sh' 2>/dev/null \
  | grep -v "06_RESEARCH/CODE/output/" | grep -v "__pycache__" | grep -v "a2_funding_features.py" \
  | grep -E "read_csv|read_parquet|open\(|loadtxt|\.load\(|cat .*HOLDOUT")
if [ -n "$HITS" ]; then
  echo "❌ no-holdout lint: 发现 Holdout 读取调用，提交被拒："
  echo "$HITS"
  exit 1
fi
exit 0
