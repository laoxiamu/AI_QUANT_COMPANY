#!/bin/bash
# fswatch TASK_INBOX watcher — 事件驱动派发
INBOX="/Users/yaomingyu/Documents/AI_QUANT_COMPANY/04_AI_TEAM/TASK_INBOX"
PROCESSED="$INBOX/PROCESSED"
LOG="/tmp/task_inbox_watcher.log"
FSWATCH="/opt/homebrew/bin/fswatch"
PYTHON="/usr/bin/python3"

mkdir -p "$PROCESSED"
echo "[$(date)] fswatch watcher started (v2)" >> "$LOG"

$FSWATCH -0 --event Created "$INBOX" | while IFS= read -r -d '' event; do
    if [[ "$event" == *"_DONE.json" && "$event" != *"/PROCESSED/"* ]]; then
        echo "[$(date)] Detected: $event" >> "$LOG"
        TASK_ID=$($PYTHON -c "import json; d=json.load(open('$event')); print(d.get('task_id','UNKNOWN'))" 2>/dev/null)
        NEXT=$($PYTHON -c "import json; d=json.load(open('$event')); print(d.get('next_task','NONE'))" 2>/dev/null)
        STATUS=$($PYTHON -c "import json; d=json.load(open('$event')); print(d.get('status','unknown'))" 2>/dev/null)
        echo "[$(date)] Task=$TASK_ID status=$STATUS next=$NEXT" >> "$LOG"
        mv "$event" "$PROCESSED/" 2>/dev/null
        echo "[$(date)] Moved to PROCESSED/" >> "$LOG"
    fi
done
