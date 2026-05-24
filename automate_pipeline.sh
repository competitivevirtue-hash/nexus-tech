#!/bin/bash
# Localized background loop runner for Nexus Tech Aggregator
# Runs the aggregator_daemon.py script every 180 minutes (10800 seconds).

# Get script directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_BIN="$PARENT_DIR/venv/bin/python"

# If venv python doesn't exist, fallback to system python3
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "================================================================================"
echo "         HELIOS NEXUS TECH & GAMING AUTOMATION PIPELINE LOOP INITIALIZED"
echo "================================================================================"
echo "  * Parent Directory   : $PARENT_DIR"
echo "  * Aggregator Script  : $SCRIPT_DIR/aggregator_daemon.py"
echo "  * Interpreter Bin    : $PYTHON_BIN"
echo "  * Scheduling Interval: 180 minutes"
echo "================================================================================"

while true; do
    echo ""
    echo "[*] Ingestion Loop Triggered: $(date)"
    "$PYTHON_BIN" "$SCRIPT_DIR/aggregator_daemon.py"
    echo "[+] Pipeline execution complete. Sleeping for 180 minutes..."
    
    # Sleep 180 minutes (180 * 60 = 10800 seconds)
    sleep 10800
done
