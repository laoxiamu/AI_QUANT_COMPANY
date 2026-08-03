#!/bin/bash
# 每币一个独立进程，内存硬封顶
cd /root
mkdir -p /root/fl_shards
rm -f /root/fl_shards/*.json /root/fl_shards/*.conf
i=0
for f in /root/DATA/KLINES_1M_1Y/*_1m.csv.gz; do
  s=$(basename "$f" _1m.csv.gz)
  i=$((i+1))
  FL_KL=/root/DATA/KLINES_1M_1Y FL_SYMS="$s" FL_SHARD=1 \
    FL_OUT=/root/fl_shards/${s}.json \
    python3 -u funlab_backtest.py > /root/fl_shards/${s}.log 2>&1
  echo "[$i] $s done rc=$?" >> /root/fl_progress.log
done
echo ALL_SHARDS_DONE >> /root/fl_progress.log
