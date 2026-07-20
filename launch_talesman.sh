#!/bin/bash

# Talesman launch script
# Location: /home/n01d/Talesman/launch_talesman.sh

BOT_DIR="/home/n01d/Talesman"
LOGFILE="$BOT_DIR/talesman.log"

cd "$BOT_DIR" || exit 1

echo "Starting Talesman..."
echo "Logging to $LOGFILE"

# Export API keys if needed
export GEMINI_API_KEY="${GEMINI_API_KEY:-YOUR_API_KEY_HERE}"
export TALESMAN_PASS="${TALESMAN_PASS:-YOUR_NICKSERV_PASSWORD}"

# Loop forever — auto‑restart on crash
while true; do
    echo "[$(date)] Talesman starting..." >> "$LOGFILE"
    python3 main.py >> "$LOGFILE" 2>&1
    echo "[$(date)] Talesman crashed. Restarting in 5 seconds..." >> "$LOGFILE"
    sleep 5
done

